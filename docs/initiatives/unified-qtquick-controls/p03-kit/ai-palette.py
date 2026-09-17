"""Change only a live isolated AI acceptance profile's appearance."""

import argparse
import json
import os
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("scheme", choices=("dark", "light"))
args = parser.parse_args()
kit = Path(__file__).resolve().parent
session = Path(os.environ["UQC_SESSION_RUN"]).resolve()
runs = sorted(session.glob("ai-*"), key=lambda p: p.stat().st_mtime_ns)
assert runs, "Launch the AI run first"
run = runs[-1]
assert run.parent == session and not (run / "exit.txt").exists(), (
    "Latest AI run is not active"
)
records = list(run.glob("pid-*.json"))
assert len(records) == 1, "Wait for process evidence collection"
record = json.loads(records[0].read_text())
assert (
    Path("/proc", str(record["pid"]), "exe").resolve()
    == kit / "prefix/bin/holonight-chat"
)
env = record["environment"]
assert env["HOLONIGHT_APPEARANCE_FILE"] == str(run / "appearance.toml"), (
    "Expected isolated per-run appearance"
)
assert env["HOLONIGHT_PALETTE_DIAGNOSTICS"] == "1"
config = json.loads((run / "xdg_config_home/holonight-ai/config.json").read_text())
instances = config["provider_instances"]["instances"]
assert config["provider_instances"]["schema_version"] == 1
assert {p["type"] for p in instances} == {"ollama", "openai", "anthropic", "google"}
assert all(p["enabled"] is False for p in instances), (
    "All providers must be explicitly disabled"
)
assert config["utility"]["chat_title_generation_enabled"] is False
path = run / "appearance.toml"
temporary = run / "appearance.toml.next"
temporary.write_bytes((kit / f"appearance-{args.scheme}.toml").read_bytes())
temporary.replace(path)
with (run / "palette-transitions.jsonl").open("a") as out:
    out.write(
        json.dumps(
            dict(time_ms=time.time_ns() // 1000000, scheme="holonight-" + args.scheme)
        )
        + "\n"
    )
print(run, "->", args.scheme)
