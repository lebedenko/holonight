#!/usr/bin/env python3
"""Launch an acceptance surface or collect selected evidence from its actual PID."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import threading


KEYS = ("QT_QUICK_CONTROLS_STYLE", "QT_QUICK_CONTROLS_CONF", "QT_QPA_PLATFORMTHEME",
        "QML_IMPORT_PATH", "QT_PLUGIN_PATH", "LD_LIBRARY_PATH", "QT_SCALE_FACTOR",
        "XDG_SESSION_ID", "XDG_DATA_DIRS", "HOLONIGHT_RENDER_DIAGNOSTICS", "HOLONIGHT_PALETTE_DIAGNOSTICS", "HOLONIGHT_SESSION_DIAGNOSTICS",
        "XDG_CONFIG_HOME", "HOLONIGHT_APPEARANCE_FILE", "LD_PRELOAD", "QT_LOGGING_RULES")


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
    required = {"libholonight_config.so"}
    foreign_fusion = (evidence.get("executable") in ("/usr/bin/haruna", "/usr/bin/neochat", "/usr/bin/tokodon")
                      and evidence["environment"].get("QT_QUICK_CONTROLS_STYLE") == "Fusion")
    if not foreign_fusion:
        required.add("libholonight_core_qml.so")
    elif not any("libqtquickcontrols2fusionstyleplugin.so" in line for line in mappings):
        problems.append("missing runtime Fusion style plugin")
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
        line for line in lines if "holonight" in line.lower() or "libQt6" in line
        or "/QtQuick/Controls/" in line) + "\n")
    isolation = assess_isolation(evidence, lines, prefix)
    (destination / "isolation.json").write_text(json.dumps(isolation, indent=2) + "\n")
    print("Runtime isolation:", isolation["status"], flush=True)
    return isolation["status"] == "verified"


def render_observations(text):
    """Keep actual window measurements separate from requested scale."""
    windows = {}
    space_events = 0
    for line in text.splitlines():
        if 'HN_RENDER ' not in line:
            continue
        try:
            record = json.loads(line.split('HN_RENDER ', 1)[1])
        except (ValueError, TypeError):
            continue
        if not isinstance(record, dict):
            continue
        if 'activeFocusItem' in record and isinstance(record.get('id'), str) and isinstance(record.get('dpr'), (int, float)):
            windows[record['id']] = record['dpr']
        if str(record.get('phase', '')).startswith('space-'):
            space_events += 1
    return dict(actual_window_dpr=windows or None, space_observations=space_events)


def palette_observations(text):
    windows, origins = {}, set()
    events = samples = 0
    for line in text.splitlines():
        if 'HN_PALETTE ' not in line:
            continue
        try:
            record = json.loads(line.split('HN_PALETTE ', 1)[1])
        except (ValueError, TypeError):
            continue
        if not isinstance(record, dict):
            continue
        samples += 1
        events += int('event' in record)
        if isinstance(record.get('dpr'), (int, float)) and isinstance(record.get('id'), str):
            windows[record['id']] = record['dpr']
        if record.get('origin'):
            origins.add(record['origin'])
    return dict(palette_samples=samples, palette_events=events,
                palette_window_dpr=windows or None, palette_origins=sorted(origins))


def session_observations(text):
    windows = {}
    counts = {}
    for line in text.splitlines():
        if "HN_SESSION " not in line:
            continue
        try:
            state = json.loads(line.split("HN_SESSION ", 1)[1])
        except ValueError:
            continue
        if not isinstance(state, dict):
            continue
        kind = state.get("kind")
        if not isinstance(kind, str):
            continue
        counts[kind] = counts.get(kind, 0) + 1
        if kind == "window" and isinstance(state.get("id"), str) and isinstance(state.get("dpr"), (int, float)):
            windows[state["id"]] = state["dpr"]
    return dict(session_samples=counts, session_window_dpr=windows or None)


def sample_session(evidence, stop):
    """Persist selected ownership metadata only, never compositor window titles."""
    previous = None
    with (evidence / "session.jsonl").open("w") as output:
        while not stop.is_set():
            state = {}
            commands = [("session", ["loginctl", "show-session", os.environ.get("XDG_SESSION_ID", ""),
                                     "-p", "Active", "-p", "State", "-p", "VTNr"])]
            if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
                commands.append(("compositor", ["hyprctl", "activewindow", "-j"]))
            for name, command in commands:
                try:
                    result = subprocess.run(command, capture_output=True, text=True, timeout=2)
                    if result.returncode:
                        state[name] = {"exit": result.returncode}
                    elif name == "compositor":
                        window = json.loads(result.stdout)
                        state[name] = {key: window.get(key) for key in ("address", "pid", "mapped")}
                    else:
                        state[name] = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
                except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                    state[name] = {"error": type(error).__name__}
            if state != previous:
                previous = state
                output.write(json.dumps(dict(state, time_ms=time.time_ns() // 1000000)) + "\n")
                output.flush()
            stop.wait(.25)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("surface", choices=("haruna", "neochat", "tokodon", "settings",
                                            "ai", "packages", "shell", "greeter", "collect"))
    parser.add_argument("--style", choices=("default", "Holonight", "Fusion"), default="default")
    parser.add_argument("--scale", choices=("1", "1.25"), default="1")
    parser.add_argument("--pid", type=int)
    parser.add_argument("--index", choices=("batch3", "batch4", "batch6"))
    parser.add_argument("--render-diagnostics", action="store_true")
    parser.add_argument("--caret-diagnostics", action="store_true")
    parser.add_argument("--palette-diagnostics", action="store_true")
    parser.add_argument("--session-diagnostics", action="store_true")
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
    for key in ("QT_QUICK_CONTROLS_STYLE", "QT_QUICK_CONTROLS_CONF", "QT_QUICK_CONTROLS_FALLBACK_STYLE",
                "HOLONIGHT_RENDER_DIAGNOSTICS", "HOLONIGHT_PALETTE_DIAGNOSTICS", "HOLONIGHT_SESSION_DIAGNOSTICS", "HOLONIGHT_SESSION_GEOMETRY", "WAYLAND_DEBUG", "LD_PRELOAD", "GREETER_CARET_DIR"):
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
    if args.index in ("batch4", "batch6"):
        # Identical empty initial state for each comparison; keep each run's writes.
        for key in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME", "XDG_CONFIG_DIRS"):
            path = evidence / key.lower()
            path.mkdir(mode=0o700)
            env[key] = str(path)
        env["HOLONIGHT_APPEARANCE_FILE"] = str(evidence / "appearance.toml")
        env["QT_LOGGING_RULES"] = "*.debug=false;*.info=true;qt.quick.dialogs=true"
        env["QML_IMPORT_TRACE"] = "0"
        env["QT_DEBUG_PLUGINS"] = "0"
    if args.index == "batch6" and args.surface == "ai":
        seed = run / "xdg_config_home/holonight-ai/config.json"
        target = Path(env["XDG_CONFIG_HOME"]) / "holonight-ai/config.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(seed.read_bytes())
    if args.session_diagnostics:
        observer = prefix / "lib/session-diagnostics.so"
        if args.index != "batch6" or args.surface not in ("shell", "ai") or not observer.is_file():
            parser.error("session diagnostics requires the Batch 6 shell/AI kit")
        if args.render_diagnostics or args.palette_diagnostics:
            parser.error("choose one observer")
        env["LD_PRELOAD"] = str(observer)
        env["HOLONIGHT_SESSION_DIAGNOSTICS"] = "1"
        if args.surface == "shell":
            env["HOLONIGHT_SESSION_GEOMETRY"] = "1"
    if args.render_diagnostics or args.caret_diagnostics:
        observer = prefix / "lib/render-diagnostics.so"
        if not observer.is_file():
            parser.error("this kit has no rendering observer")
        env["HOLONIGHT_RENDER_DIAGNOSTICS"] = "1"
        env["LD_PRELOAD"] = str(observer)
    if args.palette_diagnostics:
        observer = prefix / "lib/palette-diagnostics.so"
        if not observer.is_file() or args.render_diagnostics:
            parser.error("palette diagnostics requires its observer and cannot be combined with render diagnostics")
        env["HOLONIGHT_PALETTE_DIAGNOSTICS"] = "1"
        env["LD_PRELOAD"] = str(observer)
    if args.caret_diagnostics:
        observer = prefix / "lib/caret-diagnostics.so"
        if args.surface != "greeter" or not observer.is_file() or args.palette_diagnostics or args.session_diagnostics:
            parser.error("caret diagnostics requires the G07 greeter kit and no other observer mode")
        env["LD_PRELOAD"] += ":" + str(observer)
        env["GREETER_CARET_DIR"] = str(evidence / "caret")
        env["QT_LOGGING_RULES"] = "*.debug=false;*.info=true;qt.qml.import.debug=true"
    isolated = False
    (evidence / "command.json").write_text(json.dumps(command) + "\n")
    def index(status, code=None):
        if not args.index:
            return
        record = dict(status=status, run=str(evidence), application=args.surface,
                      style=style, requested_scale=args.scale, kit=os.environ.get("UQC_KIT"),
                      process_exit=code, render_diagnostics=args.render_diagnostics or args.caret_diagnostics,
                      caret_diagnostics=args.caret_diagnostics,
                      qt_logging_rules=env.get("QT_LOGGING_RULES"), palette_diagnostics=args.palette_diagnostics,
                      initial_profile="isolated" if args.index == "batch6" else ("empty" if args.index == "batch4" else "session"),
                      session_diagnostics=args.session_diagnostics,
                      outcome=outcome if status == "finished" else None)
        if status == "finished":
            record["log_sha256"] = hashlib.sha256((evidence / "launch.log").read_bytes()).hexdigest()
            record.update(render_observations((evidence / "launch.log").read_text(errors="replace")))
            if args.index == "batch6":
                record.update(session_observations((evidence / "launch.log").read_text(errors="replace")))
                record["session_sha256"] = hashlib.sha256((evidence / "session.jsonl").read_bytes()).hexdigest()
            record.update(palette_observations((evidence / "launch.log").read_text(errors="replace")))
        with (run / (args.index + "-index.jsonl")).open("a") as output:
            output.write(json.dumps(record) + "\n")
    outcome = None
    index("running")
    with (evidence / "launch.log").open("w") as log:
        child = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        print("PID:", child.pid, flush=True)
        sampling_stop = threading.Event()
        sampler = None
        if args.index == "batch6":
            sampler = threading.Thread(target=sample_session, args=(evidence, sampling_stop), daemon=True)
            sampler.start()
        try:
            time.sleep(3)
            if child.poll() is None:
                try:
                    isolated = collect(child.pid, evidence, prefix)
                except OSError as error:
                    (evidence / "collection-error.txt").write_text(str(error) + "\n")
                    print("PID collection unavailable; retain launch log:", error, flush=True)
            code = child.wait()
            outcome = "normal" if code >= 0 else "signal"
        except KeyboardInterrupt:
            outcome = "interrupted"
            child.terminate()
            try:
                code = child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                outcome = "forced cleanup"
                child.kill()
                code = child.wait()
        finally:
            sampling_stop.set()
            if sampler:
                sampler.join(timeout=6)
    (evidence / "exit.txt").write_text(str(code) + "\n")
    index("finished", code)
    print("Exit:", code, flush=True)
    return code if code else (0 if isolated else 2)


if __name__ == "__main__":
    raise SystemExit(main())
