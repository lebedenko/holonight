#!/usr/bin/env python3
"""Verify actual Settings lifecycle and candidate runtime mappings in private displays."""
import argparse
import sys
sys.dont_write_bytecode = True

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time


def stop(process):
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        raise RuntimeError("test process did not terminate promptly")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kit", type=Path)
    parser.add_argument("--settings-acceptance", type=Path, required=True)
    parser.add_argument("--logs", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("UQC_ISOLATED") != "1":
        parser.error("run inside the private-bus/host-masked test wrapper")
    kit = args.kit.resolve()
    prefix = kit / "prefix"
    args.logs.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("guided_app", kit / "guided-app.py")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    with tempfile.TemporaryDirectory(prefix="uqc-input-runtime-") as directory:
        workspace = Path(directory)
        for style in ("Holonight", "Fusion"):
            for scale in ("1", "1.25"):
                case = workspace / (style + "-" + scale)
                case.mkdir()
                for part in ("config", "cache", "data", "runtime", "empty-path"):
                    (case / part).mkdir(mode=0o700)
                env = os.environ.copy()
                for key in ("QT_QUICK_CONTROLS_CONF", "QT_QUICK_CONTROLS_FALLBACK_STYLE", "QML2_IMPORT_PATH",
                            "WAYLAND_DISPLAY", "SWAYSOCK", "HYPRLAND_INSTANCE_SIGNATURE", "DISPLAY"):
                    env.pop(key, None)
                env.update(QT_QPA_PLATFORM="offscreen", QT_QUICK_BACKEND="software", QT_QPA_PLATFORMTHEME="",
                           QT_STYLE_OVERRIDE="", QT_QUICK_CONTROLS_STYLE=style, QT_SCALE_FACTOR=scale,
                           QT_LOGGING_RULES="*.debug=false;qt.quick.viewport.debug=true", QT_FORCE_STDERR_LOGGING="1",
                           QML_IMPORT_PATH=str(prefix / "lib/qt6/qml"), QT_PLUGIN_PATH=str(prefix / "lib/qt6/plugins"),
                           LD_LIBRARY_PATH=str(prefix / "lib"), HOLONIGHT_APPEARANCE_FILE=str(case / "appearance.toml"),
                           XDG_CONFIG_HOME=str(case / "config"), XDG_CONFIG_DIRS=str(case / "config"),
                           XDG_CACHE_HOME=str(case / "cache"), XDG_DATA_HOME=str(case / "data"),
                           XDG_DATA_DIRS=str(case / "data"), XDG_RUNTIME_DIR=str(case / "runtime"),
                           PULSE_SERVER="unix:" + str(case / "unavailable-audio"))
                tag = style + "-" + scale
                # This harness enters both Appearance and Weather, exercises the
                # real edit models and returns self-mappings. Empty PATH prevents
                # any native appearance adapter execution while saving test data.
                accepted = subprocess.run([str(args.settings_acceptance.resolve())],
                                          env=dict(env, PATH=str(case / "empty-path")),
                                          capture_output=True, text=True, timeout=30)
                output = accepted.stdout + accepted.stderr
                (args.logs / ("settings-lifecycle-" + tag + ".log")).write_text(output)
                assert accepted.returncode == 0 and "ACCEPTANCE_OK" in output, "Settings lifecycle failed: " + tag
                assert "PAGE appearance" in output and "PAGE weather" in output
                assert not re.search(r"Binding loop|ReferenceError|TypeError|Cannot assign|Unable to assign", output), tag
                maps = output.split("MAPS_BEGIN\n")[1].split("MAPS_END")[0].splitlines()
                result = helper.assess_isolation({"environment": env}, maps, prefix)
                (args.logs / ("settings-lifecycle-" + tag + ".json")).write_text(json.dumps(result, indent=2))
                assert result["status"] == "verified", result

                compositor = None
                compositor_log = None
                try:
                    for app in ("settings", "greeter", "shell"):
                        destination = args.logs / (app + "-" + tag)
                        destination.mkdir(exist_ok=True)
                        child_env = env.copy()
                        command = [str(prefix / "bin" / ("holonight-" + app))]
                        if app == "greeter":
                            command += ["--demo", "--state", str(case / "greeter-state.json")]
                        if app == "shell":
                            config = case / "sway.conf"
                            config.write_text("output HEADLESS-1 mode 1280x720\n")
                            compositor_log = (destination / "sway.log").open("w")
                            compositor = subprocess.Popen(["sway", "--unsupported-gpu", "--config", str(config)],
                                env=dict(env, WLR_BACKENDS="headless", WLR_RENDERER="pixman", WLR_LIBINPUT_NO_DEVICES="1"),
                                stdout=compositor_log, stderr=subprocess.STDOUT)
                            deadline = time.monotonic() + 10
                            sockets = []
                            while time.monotonic() < deadline:
                                assert compositor.poll() is None, "headless Sway exited"
                                sockets = [p for p in (case / "runtime").glob("wayland-*") if p.is_socket()]
                                if sockets:
                                    break
                                time.sleep(0.05)
                            assert len(sockets) == 1, "missing private Wayland socket"
                            child_env.update(QT_QPA_PLATFORM="wayland", WAYLAND_DISPLAY=sockets[0].name,
                                             SWAYSOCK=str(next((case / "runtime").glob("sway-ipc.*.sock"))),
                                             XDG_CURRENT_DESKTOP="sway")
                            command += ["--debug", "--no-log-file"]
                        with (destination / "launch.log").open("w") as log:
                            child = subprocess.Popen(command, env=child_env, stdout=log, stderr=subprocess.STDOUT)
                            try:
                                deadline = time.monotonic() + 3
                                while time.monotonic() < deadline:
                                    assert child.poll() is None, "premature exit: " + app + " " + tag
                                    time.sleep(0.05)
                                assert helper.collect(child.pid, destination, prefix), "incomplete isolation: " + app + " " + tag
                            finally:
                                stop(child)
                            (destination / "exit.json").write_text(json.dumps(dict(
                                code=child.returncode, reason="terminated after bounded runtime inspection")))
                        diagnostics = (destination / "launch.log").read_text()
                        assert not re.search(r"Binding loop|ReferenceError|TypeError|Cannot assign|Unable to assign", diagnostics), app + tag
                finally:
                    if compositor is not None:
                        stop(compositor)
                    if compositor_log is not None:
                        compositor_log.close()
                print("PASS lifecycle and runtime isolation", tag, flush=True)


if __name__ == "__main__":
    main()
