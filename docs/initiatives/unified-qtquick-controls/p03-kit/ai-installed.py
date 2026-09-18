"""Verify all installed selectors and reject source/build QML discovery."""
from pathlib import Path
import subprocess
import sys

root = Path.cwd()
kit = Path(sys.argv[1]).resolve()
work = root / ".cache" / kit.name
logs = work / "logs/ai-installed"
subprocess.run([
    "python3", root / "holonight-ai/scripts/check-runtime-launches.py",
    kit / "prefix/bin/holonight-chat", kit / "prefix",
    "--forbid-path", work / "build", "--logs", logs,
], check=True)
for mode in ("default", "environment", "command-line", "external-config"):
    for suffix in ("log", "maps"):
        evidence = (logs / f"{mode}.{suffix}").read_text()
        for repo in ("holonight-ai", "holonight-qt"):
            assert str(root / repo) not in evidence, (mode, suffix, repo)
print("PASS all installed selectors; source and build roots forbidden")
