#!/usr/bin/env python3
"""Start a user-operated UQC compositor from a real tux VT login."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def output(*command):
    return subprocess.check_output(command, text=True).strip()


def main():
    kit = Path(__file__).resolve().parent
    if len(sys.argv) != 2 or sys.argv[1] not in ("hyprland", "sway"):
        raise SystemExit("Usage: python3 guided-session.py hyprland|sway")
    if os.getuid() != 1001 or output("id", "-un") != "tux":
        raise SystemExit("STOP: use the real tux VT login, never sudo/su/SSH.")
    if os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY"):
        raise SystemExit("STOP: start from a fresh VT login, outside a compositor.")
    obj = output("busctl", "--system", "call", "org.freedesktop.login1",
                 "/org/freedesktop/login1", "org.freedesktop.login1.Manager",
                 "GetSessionByPID", "u", str(os.getpid())).split('"')[1]
    sid = output("busctl", "--system", "get-property", "org.freedesktop.login1",
                 obj, "org.freedesktop.login1.Session", "Id").split('"')[1]
    identity = output("loginctl", "show-session", sid, "-p", "User", "-p", "Active",
                      "-p", "Remote", "-p", "Type", "-p", "Seat", "-p", "TTY")
    fields = dict(line.split("=", 1) for line in identity.splitlines())
    if any(fields.get(k) != v for k, v in
           {"User": "1001", "Active": "yes", "Remote": "no", "Type": "tty"}.items()):
        raise SystemExit("STOP: expected an active local tux VT login.\n" + identity)
    prefix = kit / "prefix"
    if not (kit / "READY").is_file():
        raise SystemExit("STOP: this kit has not completed preparation.")
    inventory = (kit / "PROVIDER.txt").read_text().splitlines()
    for package in ("qt6-base", "qt6-declarative", "hyprpolkitagent"):
        if output("pacman", "-Q", package) not in inventory:
            raise SystemExit("STOP: installed " + package + " changed; rebuild/review this kit.")
    runs = Path.home() / "uqc-guided-evidence"
    runs.mkdir(mode=0o700, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix=sys.argv[1] + "-", dir=runs))
    (run / "identity.txt").write_text(identity + "\nId=" + sid + "\n")
    env = os.environ.copy()
    for key in ("QT_QUICK_CONTROLS_STYLE", "QT_QUICK_CONTROLS_CONF",
                "QT_QUICK_CONTROLS_FALLBACK_STYLE", "QML2_IMPORT_PATH",
                "QT_QUICK_BACKEND", "QT_SCALE_FACTOR", "DBUS_SESSION_BUS_ADDRESS"):
        env.pop(key, None)
    for key in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME",
                "XDG_CONFIG_DIRS"):
        path = run / key.lower()
        path.mkdir(mode=0o700)
        env[key] = str(path)
    config = Path(env["XDG_CONFIG_HOME"]) / "holonight-ai/config.json"
    config.parent.mkdir()
    config.write_text(json.dumps({
        "provider_instances": {"schema_version": 1, "instances": [
            {"id": name, "type": name, "name": name, "enabled": False, "settings": {}}
            for name in ("ollama", "openai", "anthropic", "google")], "tombstones": []},
        "utility": {"chat_title_generation_enabled": False}}))
    env.update(UQC_KIT=str(kit), UQC_PREFIX=str(prefix), UQC_SESSION_RUN=str(run),
               HOLONIGHT_APPEARANCE_FILE=str(run / "appearance.toml"),
               XDG_CURRENT_DESKTOP="Hyprland" if sys.argv[1] == "hyprland" else "sway",
               XDG_SESSION_ID=sid, PATH=f"{prefix}/bin:/usr/bin:/bin",
               XDG_DATA_DIRS=f"{prefix}/share:/usr/local/share:/usr/share",
               QML_IMPORT_PATH=f"{prefix}/lib/qt6/qml",
               QT_PLUGIN_PATH=f"{prefix}/lib/qt6/plugins", LD_LIBRARY_PATH=f"{prefix}/lib",
               QT_QPA_PLATFORM="wayland", QT_QPA_PLATFORMTHEME="holonight",
               QML_IMPORT_TRACE="1", QT_DEBUG_PLUGINS="1", QT_FORCE_STDERR_LOGGING="1",
               QT_LOGGING_RULES="*.debug=true;*.info=true")
    (run / "versions.txt").write_text(output("pacman", "-Q", "haruna", "neochat", "tokodon",
                                              "hyprpolkitagent", "qt6-base", "qt6-declarative",
                                              "hyprland", "sway") + "\n")
    compositor = "Hyprland" if sys.argv[1] == "hyprland" else "sway"
    command = ["dbus-run-session", "--", compositor, "--config", str(kit / (sys.argv[1] + ".conf"))]
    (run / "command.json").write_text(json.dumps(command) + "\n")
    print("Session evidence:", run, flush=True)
    # Discovery is inherited when this new bus starts; the normal desktop is untouched.
    with (run / "compositor.log").open("w") as log:
        return subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
