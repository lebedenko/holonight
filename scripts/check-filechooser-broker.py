#!/usr/bin/env python3
"""Check staged FileChooser activation and cancellation through an isolated real broker."""

import argparse
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import time
from xml.sax.saxutils import escape


BACKEND = "org.freedesktop.impl.portal.desktop.holonight_filechooser"
DESKTOP = "org.freedesktop.portal.Desktop"
PATH = "/org/freedesktop/portal/desktop"


def session(root):
    from gi.repository import Gio, GLib

    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def call(name, path, interface, method, args=None):
        return bus.call_sync(name, path, interface, method, args, None,
                             Gio.DBusCallFlags.NONE, 5000, None)

    def backend_request_exists(handle):
        try:
            xml = call(BACKEND, handle, "org.freedesktop.DBus.Introspectable", "Introspect").unpack()[0]
            return "org.freedesktop.impl.portal.Request" in xml
        except GLib.Error:
            return False

    def wait_for(condition, message):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if condition():
                return
            time.sleep(0.05)
        raise RuntimeError(message)

    log = root / "broker.log"
    with log.open("w") as output:
        broker = subprocess.Popen(["/usr/lib/xdg-desktop-portal", "--verbose"],
                                  stdout=output, stderr=subprocess.STDOUT)
        try:
            wait_for(lambda: call("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
                                  "NameHasOwner", GLib.Variant("(s)", (DESKTOP,))).unpack()[0],
                     "Real broker did not acquire its bus name")
            for index, (method, extra) in enumerate((
                    ("OpenFile", {}),
                    ("OpenFile", {"directory": GLib.Variant("b", True)}),
                    ("OpenFile", {"multiple": GLib.Variant("b", True)}),
                    ("SaveFile", {"current_name": GLib.Variant("s", "out.txt")}),
                    ("SaveFiles", {"files": GLib.Variant("aay", [list(b"out.txt\0")])}))):
                options = {"handle_token": GLib.Variant("s", f"check{index}"),
                           "current_folder": GLib.Variant("ay", list(os.fsencode(root) + b"\0")), **extra}
                handle = call(DESKTOP, PATH, "org.freedesktop.portal.FileChooser", method,
                              GLib.Variant("(ssa{sv})", ("", "Isolated broker check", options))).unpack()[0]
                wait_for(lambda: backend_request_exists(handle), f"{method} did not reach the staged backend")
                call(DESKTOP, handle, "org.freedesktop.portal.Request", "Close")
                wait_for(lambda: not backend_request_exists(handle), f"{method} cancellation left a backend request")
                print(f"{method} case {index}: staged backend activation, dispatch and cancellation PASS", flush=True)
        finally:
            try:
                pid = call("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus",
                           "GetConnectionUnixProcessID", GLib.Variant("(s)", (BACKEND,))).unpack()[0]
                if Path(f"/proc/{pid}/exe").resolve() == Path(os.environ["PORTAL_CHECK_EXECUTABLE"]):
                    os.kill(pid, signal.SIGTERM)
            except (GLib.Error, ProcessLookupError):
                pass
            broker.terminate()
            broker.wait(timeout=5)
    print("Unsandboxed cancellation checks only; successful selections and document grants require manual acceptance.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-build", type=Path)
    parser.add_argument("--shell-stage", type=Path, help="Staged Shell prefix, e.g. /tmp/stage/usr")
    parser.add_argument("--imports", help="Colon-separated installed provider QML paths")
    parser.add_argument("--libraries", help="Colon-separated installed provider library paths")
    parser.add_argument("--session", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.session:
        session(args.session)
        return
    if not args.backend_build or not args.shell_stage or not args.imports or not args.libraries:
        parser.error("--backend-build, --shell-stage, --imports and --libraries are required")
    with tempfile.TemporaryDirectory(prefix="filechooser-broker-") as directory:
        root = Path(directory)
        stage = root / "stage"
        subprocess.run(["cmake", "--install", str(args.backend_build.resolve())],
                       env={**os.environ, "DESTDIR": str(stage)}, check=True, capture_output=True)
        service = next(stage.rglob("org.freedesktop.impl.portal.desktop.holonight_filechooser.service"))
        executable = stage / shlex.split(next(line[5:] for line in service.read_text().splitlines()
                                             if line.startswith("Exec=")))[0].lstrip("/")
        if not executable.is_file():
            raise RuntimeError("Staged backend executable missing")
        service.write_text("\n".join(f"Exec={shlex.quote(str(executable))}" if line.startswith("Exec=") else line
                                     for line in service.read_text().splitlines()) + "\n")
        env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_QUICK_BACKEND": "software",
               "QML_IMPORT_PATH": args.imports, "LD_LIBRARY_PATH": args.libraries, "XDG_CURRENT_DESKTOP": "HoloNight",
               "QT_QPA_PLATFORMTHEME": "", "PORTAL_CHECK_EXECUTABLE": str(executable),
               "GSETTINGS_SCHEMA_DIR": "/usr/share/glib-2.0/schemas",
               "DBUS_SYSTEM_BUS_ADDRESS": f"unix:path={root}/no-system-bus",
               "XDG_DESKTOP_PORTAL_DIR": str(next(stage.rglob("holonight-filechooser.portal")).parent)}
        for name in ("HOME", "XDG_CONFIG_HOME", "XDG_CONFIG_DIRS", "XDG_DATA_HOME", "XDG_DATA_DIRS",
                     "XDG_CACHE_HOME", "XDG_RUNTIME_DIR", "XDG_STATE_HOME"):
            path = root / name
            path.mkdir(mode=0o700)
            env[name] = str(path)
        config = Path(env["XDG_CONFIG_HOME"]) / "xdg-desktop-portal"
        config.mkdir()
        routing = args.shell_stage / "share/xdg-desktop-portal/holonight-portals.conf"
        (config / routing.name).write_bytes(routing.read_bytes())
        # The broker override also changes its configuration search directory.
        (Path(env["XDG_DESKTOP_PORTAL_DIR"]) / routing.name).write_bytes(routing.read_bytes())
        bus_config = root / "bus.conf"
        bus_config.write_text(f'''<busconfig><type>session</type><listen>unix:tmpdir={escape(str(root))}</listen>
<auth>EXTERNAL</auth><servicedir>{escape(str(service.parent))}</servicedir>
<policy context="default"><allow own="*"/><allow send_destination="*"/><allow receive_sender="*"/></policy>
</busconfig>''')
        result = subprocess.run(["dbus-run-session", f"--config-file={bus_config}", "--", sys.executable,
                                 str(Path(__file__).resolve()), "--session", str(root)], env=env, timeout=90)
        print((root / "broker.log").read_text() if (root / "broker.log").exists() else "Broker log unavailable")
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
