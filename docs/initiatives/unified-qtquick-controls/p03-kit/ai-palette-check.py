from pathlib import Path
import os
import subprocess
import time
import json
import importlib.util
import hashlib
import sys

root = Path.cwd()
kit = Path(sys.argv[1]).resolve()
work = root / ".cache" / kit.name
prefix = kit / "prefix"
spec = importlib.util.spec_from_file_location("collector", kit / "guided-app.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
for style in ("default", "Fusion"):
    session = work / ("ai-palette-" + style)
    run = session / "ai-check"
    run.mkdir(parents=True)
    env = dict(
        os.environ,
        UQC_SESSION_RUN=str(session),
        QT_QPA_PLATFORM="offscreen",
        QT_QUICK_BACKEND="software",
        QT_QPA_PLATFORMTHEME="holonight",
        QT_SCALE_FACTOR="1.25",
        QML_IMPORT_PATH=str(prefix / "lib/qt6/qml"),
        QT_PLUGIN_PATH=str(prefix / "lib/qt6/plugins"),
        LD_LIBRARY_PATH=str(prefix / "lib"),
        LD_PRELOAD=str(prefix / "lib/palette-diagnostics.so"),
        HOLONIGHT_PALETTE_DIAGNOSTICS="1",
        HOLONIGHT_APPEARANCE_FILE=str(run / "appearance.toml"),
    )
    for k in (
        "QT_QUICK_CONTROLS_STYLE",
        "QT_QUICK_CONTROLS_CONF",
        "QT_QUICK_CONTROLS_FALLBACK_STYLE",
        "HOLONIGHT_RENDER_DIAGNOSTICS",
        "HOLONIGHT_SESSION_DIAGNOSTICS",
    ):
        env.pop(k, None)
    if style != "default":
        env["QT_QUICK_CONTROLS_STYLE"] = style
    for k in (
        "HOME",
        "XDG_CONFIG_HOME",
        "XDG_CONFIG_DIRS",
        "XDG_CACHE_HOME",
        "XDG_DATA_HOME",
        "XDG_STATE_HOME",
    ):
        p = run / k.lower()
        p.mkdir()
        env[k] = str(p)
    config = run / "xdg_config_home/holonight-ai/config.json"
    config.parent.mkdir()
    config.write_text(
        json.dumps(
            {
                "provider_instances": {
                    "schema_version": 1,
                    "instances": [
                        {
                            "id": n,
                            "type": n,
                            "name": n,
                            "enabled": False,
                            "settings": {},
                        }
                        for n in ("ollama", "openai", "anthropic", "google")
                    ],
                    "tombstones": [],
                },
                "utility": {"chat_title_generation_enabled": False},
            }
        )
    )
    with (run / "launch.log").open("w") as log:
        child = subprocess.Popen(
            [str(prefix / "bin/holonight-chat")],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            time.sleep(2)
            assert child.poll() is None
            assert collector.collect(child.pid, run, prefix)
            helper_env = dict(os.environ, UQC_SESSION_RUN=str(session))
            # Refusals must leave appearance and transition evidence untouched.
            valid = config.read_text()
            record_path = next(run.glob("pid-*.json"))
            valid_record = record_path.read_text()

            def refuse(label):
                before = {p.name: p.read_bytes() for p in run.glob("appearance*")}
                transitions = run / "palette-transitions.jsonl"
                previous = transitions.read_bytes() if transitions.exists() else None
                result = subprocess.run(
                    ["python3", str(kit / "ai-palette.py"), "light"],
                    env=helper_env,
                    capture_output=True,
                    text=True,
                )
                assert result.returncode != 0, label
                assert before == {
                    p.name: p.read_bytes() for p in run.glob("appearance*")
                }
                assert previous == (
                    transitions.read_bytes() if transitions.exists() else None
                )
                (run / (label + "-refusal.txt")).write_text(result.stderr)

            for label in (
                "enabled-provider",
                "title-generation",
                "missing-provider",
                "invalid-json",
            ):
                data = json.loads(valid)
                if label == "enabled-provider":
                    data["provider_instances"]["instances"][0]["enabled"] = True
                if label == "title-generation":
                    data["utility"]["chat_title_generation_enabled"] = True
                if label == "missing-provider":
                    data["provider_instances"]["instances"].pop()
                config.write_text("{" if label == "invalid-json" else json.dumps(data))
                refuse(label)
            config.write_text(valid)
            data = json.loads(valid_record)
            data["environment"]["HOLONIGHT_APPEARANCE_FILE"] = "/tmp/not-this-profile"
            record_path.write_text(json.dumps(data))
            refuse("wrong-profile")
            record_path.write_text(valid_record)
            snapshots = []
            for scheme in ("dark", "light", "dark"):
                subprocess.run(
                    ["python3", str(kit / "ai-palette.py"), scheme],
                    env=helper_env,
                    check=True,
                )
                time.sleep(1)
                entries = [
                    json.loads(line.split("HN_PALETTE ", 1)[1])
                    for line in (run / "launch.log").read_text().splitlines()
                    if "HN_PALETTE " in line
                ]
                snapshots.append(
                    [
                        r["color"]
                        for r in entries
                        if "WorkspaceWindow" in r.get("id", "") and "color" in r
                    ][-1]
                )
            assert snapshots[0] != snapshots[1] and snapshots[2] == snapshots[0], (
                "workspace color round trip not observed"
            )
        finally:
            child.terminate()
            child.wait(timeout=5)
    (run / "exit.txt").write_text(str(child.returncode) + "\n")
    refusal = subprocess.run(
        ["python3", str(kit / "ai-palette.py"), "light"],
        env=helper_env,
        capture_output=True,
        text=True,
    )
    assert refusal.returncode != 0
    (run / "closed-run-refusal.txt").write_text(refusal.stderr)
    text = (run / "launch.log").read_text()
    observations = collector.palette_observations(text)
    assert observations["palette_samples"] > 0
    assert observations["palette_window_dpr"] and set(
        observations["palette_window_dpr"].values()
    ) == {1.25}
    assert observations["palette_origins"]
    records = [
        json.loads(line.split("HN_PALETTE ", 1)[1])
        for line in text.splitlines()
        if "HN_PALETTE " in line
    ]
    colors = {
        json.dumps(r.get("palette"), sort_keys=True) for r in records if "palette" in r
    }
    # Scene colors prove the programmatic round trip; native/global palette scope remains a manual distinction.
    result = dict(
        style=style,
        exit=child.returncode,
        reason="bounded termination after palette transitions",
        closed_run_refused=True,
        workspace_color_round_trip=snapshots,
        log_sha256=hashlib.sha256((run / "launch.log").read_bytes()).hexdigest(),
        **observations,
    )
    (run / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS AI palette helper", style, flush=True)
