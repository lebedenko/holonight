#!/usr/bin/env python3
"""Launch an acceptance surface or collect selected evidence from its actual PID."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import time


KEYS = ("QT_QUICK_CONTROLS_STYLE", "QT_QUICK_CONTROLS_CONF", "QT_QPA_PLATFORMTHEME",
        "QML_IMPORT_PATH", "QT_PLUGIN_PATH", "LD_LIBRARY_PATH", "QT_SCALE_FACTOR",
        "XDG_SESSION_ID", "XDG_DATA_DIRS")


def assess_isolation(evidence, mappings, prefix):
    """Require runtime evidence, not just configured discovery paths."""
    prefix = prefix.resolve()
    problems = []
    if evidence["environment"].get("LD_LIBRARY_PATH") != str(prefix / "lib"):
        problems.append("staged LD_LIBRARY_PATH missing or different")
    libraries = set()
    for line in mappings:
        fields = line.split(None, 5)
        if len(fields) != 6:
            continue
        path = Path(fields[5])
        if ".so" not in path.name:
            continue
        if "holonight" in path.name.lower() or "/Holonight/" in str(path):
            libraries.add(str(path))
            if not path.is_absolute() or not path.resolve().is_relative_to(prefix):
                problems.append("host/outside-prefix HoloNight mapping: " + str(path))
    required = {"libholonight_config.so", "libholonight_core_qml.so"}
    if evidence["environment"].get("QT_QUICK_CONTROLS_STYLE") != "Fusion":
        required.add("libholonight_qml.so")
    names = {Path(path).name for path in libraries}
    for name in sorted(required):
        if not any(candidate == name or candidate.startswith(name + ".") for candidate in names):
            problems.append("missing runtime mapping: " + name)
    return dict(status="verified" if not problems else "incomplete", prefix=str(prefix),
                libraries=sorted(libraries), problems=problems)


def collect(pid, destination, prefix):
    proc = Path("/proc") / str(pid)
    environment = dict(item.split("=", 1) for item in
                       (proc / "environ").read_bytes().decode().split("\0") if "=" in item)
    evidence = dict(pid=pid, executable=str((proc / "exe").resolve(strict=True)),
                    date=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    environment={key: environment.get(key) for key in KEYS})
    (destination / f"pid-{pid}.json").write_text(json.dumps(evidence, indent=2) + "\n")
    lines = (proc / "maps").read_text().splitlines()
    (destination / f"pid-{pid}.maps").write_text("\n".join(
        line for line in lines if "holonight" in line.lower() or "libQt6" in line) + "\n")
    isolation = assess_isolation(evidence, lines, prefix)
    (destination / "isolation.json").write_text(json.dumps(isolation, indent=2) + "\n")
    print("Runtime isolation:", isolation["status"], flush=True)
    return isolation["status"] == "verified"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("surface", choices=("haruna", "neochat", "tokodon", "settings",
                                            "ai", "packages", "shell", "greeter", "collect"))
    parser.add_argument("--style", choices=("default", "Holonight", "Fusion"), default="default")
    parser.add_argument("--scale", choices=("1", "1.25"), default="1")
    parser.add_argument("--pid", type=int)
    args = parser.parse_args()
    if os.getuid() != 1001 or not os.environ.get("UQC_SESSION_RUN") or not os.environ.get("WAYLAND_DISPLAY"):
        parser.error("run in the prepared tux compositor terminal")
    run = Path(os.environ["UQC_SESSION_RUN"])
    evidence = run / (args.surface + "-" + str(time.time_ns()))
    evidence.mkdir(mode=0o700)
    print("Evidence:", evidence, flush=True)
    (evidence / "isolation.json").write_text(json.dumps(dict(
        status="incomplete", problems=["runtime evidence not yet collected"])) + "\n")
    if args.surface == "collect":
        if not args.pid:
            parser.error("collect requires --pid")
        return 0 if collect(args.pid, evidence, Path(os.environ["UQC_PREFIX"])) else 2
    prefix = Path(os.environ["UQC_PREFIX"])
    binaries = {"settings": "holonight-settings", "ai": "holonight-chat",
                "packages": "holonight-packages", "shell": "holonight-shell", "greeter": "holonight-greeter"}
    owned = args.surface in binaries
    binary = prefix / "bin" / binaries[args.surface] if owned else Path("/usr/bin") / args.surface
    command = [str(binary)]
    if args.surface == "shell":
        command += ["--debug", "--no-log-file"]
    if args.surface == "greeter":
        command += ["--demo", "--config", str(run / "demo-greeter.toml"), "--state", str(run / "demo-state.json")]
    env = os.environ.copy()
    for key in ("QT_QUICK_CONTROLS_STYLE", "QT_QUICK_CONTROLS_CONF", "QT_QUICK_CONTROLS_FALLBACK_STYLE"):
        env.pop(key, None)
    style = args.style if args.style != "default" else (None if owned else "Holonight")
    if style:
        env["QT_QUICK_CONTROLS_STYLE"] = style
    env["QT_SCALE_FACTOR"] = args.scale
    # A compositor or launcher may strip LD_LIBRARY_PATH from the session.
    # Re-establish it for each child and validate what the process actually loads.
    env["LD_LIBRARY_PATH"] = str(prefix / "lib")
    env["QML_IMPORT_PATH"] = str(prefix / "lib/qt6/qml")
    env["QT_PLUGIN_PATH"] = str(prefix / "lib/qt6/plugins")
    isolated = False
    (evidence / "command.json").write_text(json.dumps(command) + "\n")
    with (evidence / "launch.log").open("w") as log:
        child = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        print("PID:", child.pid, flush=True)
        try:
            time.sleep(3)
            if child.poll() is None:
                try:
                    isolated = collect(child.pid, evidence, prefix)
                except OSError as error:
                    (evidence / "collection-error.txt").write_text(str(error) + "\n")
                    print("PID collection unavailable; retain launch log:", error, flush=True)
            code = child.wait()
        except KeyboardInterrupt:
            child.terminate()
            try:
                code = child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                code = child.wait()
    (evidence / "exit.txt").write_text(str(code) + "\n")
    print("Exit:", code, flush=True)
    return code if code else (0 if isolated else 2)


if __name__ == "__main__":
    raise SystemExit(main())
