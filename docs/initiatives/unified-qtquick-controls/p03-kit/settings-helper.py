"""Exercise the actual guided helper offscreen, without seat or focus automation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

kit = Path(sys.argv[1]).resolve()
work = Path.cwd() / ".cache" / kit.name
prefix = kit / "prefix"
surface = "ai" if json.loads((kit / "profile.json").read_text())["profile"] == "ai-scale1" else "settings"
executable = "holonight-chat" if surface == "ai" else "holonight-settings"
spec = importlib.util.spec_from_file_location("collector", kit / "guided-app.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
for style in ("default", "Fusion"):
    session = work / (surface + "-helper-" + style)
    session.mkdir()
    env = dict(os.environ, UQC_SESSION_RUN=str(session), UQC_KIT=str(kit),
               UQC_PREFIX=str(prefix), WAYLAND_DISPLAY="offscreen-test-only",
               QT_QPA_PLATFORM="offscreen", QT_QUICK_BACKEND="software",
               QT_QPA_PLATFORMTHEME="holonight", QML_IMPORT_TRACE="1",
               HOLONIGHT_APPEARANCE_FILE=str(session / "appearance.toml"))
    for name in ("HOME", "XDG_CONFIG_HOME", "XDG_CONFIG_DIRS", "XDG_DATA_HOME",
                 "XDG_DATA_DIRS", "XDG_CACHE_HOME", "XDG_STATE_HOME"):
        path = session / name.lower()
        path.mkdir()
        env[name] = str(path)
    if surface == "ai":
        seed = session / "xdg_config_home/holonight-ai/config.json"
        seed.parent.mkdir()
        seed.write_text(json.dumps({
            "provider_instances": {"schema_version": 1, "instances": [
                {"id": name, "type": name, "name": name, "enabled": False, "settings": {}}
                for name in ("ollama", "openai", "anthropic", "google")], "tombstones": []},
            "utility": {"chat_title_generation_enabled": False}}))
    # Exercise selector clearing even in a contaminated parent environment.
    env.update(QT_QUICK_CONTROLS_STYLE="Basic", QT_QUICK_CONTROLS_CONF="/absent.conf",
               QT_QUICK_CONTROLS_FALLBACK_STYLE="Basic")
    wrapper = "import os,runpy; os.getuid=lambda:1001; runpy.run_path(" + repr(str(kit / "guided-app.py")) + ",run_name='__main__')"
    child_pid = None
    with (session / "helper.log").open("w") as log:
        helper = subprocess.Popen([sys.executable, "-c", wrapper, surface, "--style", style,
                                   "--scale", "1", "--render-diagnostics", *(["--index", "batch6"] if surface == "ai" else [])], env=env,
                                  stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                records = list(session.glob(surface + "-*/pid-*.json"))
                if records:
                    record = records[0]
                    run = record.parent
                    data = json.loads(record.read_text())
                    child_pid = data["pid"]
                    if (run / "isolation.json").exists() and json.loads((run / "isolation.json").read_text())["status"] == "verified":
                        break
                assert helper.poll() is None, (session / "helper.log").read_text()
                time.sleep(.1)
            else:
                raise AssertionError("No verified runtime collection")
            assert data["executable"] == str(prefix / "bin" / executable)
            actual = data["environment"]
            assert actual["QT_QUICK_CONTROLS_STYLE"] == (None if style == "default" else style)
            assert actual["QT_QUICK_CONTROLS_CONF"] is None
            raw_env = dict(x.split("=", 1) for x in Path(f"/proc/{child_pid}/environ").read_text().split("\0") if "=" in x)
            assert "QT_QUICK_CONTROLS_FALLBACK_STYLE" not in raw_env
            assert raw_env["HOME"] == env["HOME"]
            assert raw_env["DBUS_SESSION_BUS_ADDRESS"] == env["DBUS_SESSION_BUS_ADDRESS"]
            if surface == "ai":
                config_home = Path(raw_env["XDG_CONFIG_HOME"])
                assert config_home == run / "xdg_config_home"
                config = json.loads((config_home / "holonight-ai/config.json").read_text())
                assert config["provider_instances"]["instances"]
                assert all(not row["enabled"] for row in config["provider_instances"]["instances"])
                assert config["utility"]["chat_title_generation_enabled"] is False
                assert raw_env["HOLONIGHT_APPEARANCE_FILE"] == str(run / "appearance.toml")
            assert actual["LD_PRELOAD"] == str(prefix / "lib/render-diagnostics.so")
            text = (run / "launch.log").read_text()
            measured = collector.render_observations(text)["actual_window_dpr"]
            assert measured and set(measured.values()) == {1}
            records = [json.loads(line.split("HN_RENDER ", 1)[1]) for line in text.splitlines() if "HN_RENDER " in line]
            origins = sorted({row["origin"] for row in records if row.get("origin")})
            assert origins, "No control origins"
            assert any("Holonight" in origin for origin in origins)
            os.kill(child_pid, signal.SIGTERM)
            helper.wait(timeout=10)
            assert helper.returncode == 241, "Guided helper must propagate SIGTERM outcome"
            assert (run / "exit.txt").read_text().strip() == "-15"
            if surface == "ai":
                finished = json.loads((session / "batch6-index.jsonl").read_text().splitlines()[-1])
                assert finished["status"] == "finished" and finished["process_exit"] == -15
                assert finished["outcome"] == "signal"
            (session / "result.json").write_text(json.dumps(dict(style=style, evidence=str(run),
                measured_dpr=measured, origins=origins, selector=actual["QT_QUICK_CONTROLS_STYLE"],
                executable=data["executable"], isolation="verified", exit=-15,
                outcome="bounded automated SIGTERM; normal closure remains human",
                log_sha256=hashlib.sha256((run / "launch.log").read_bytes()).hexdigest()), indent=2) + "\n")
        finally:
            if child_pid and Path(f"/proc/{child_pid}").exists():
                os.kill(child_pid, signal.SIGTERM)
            if helper.poll() is None:
                helper.terminate()
                helper.wait(timeout=5)
    print("PASS actual guided helper", surface, style)
