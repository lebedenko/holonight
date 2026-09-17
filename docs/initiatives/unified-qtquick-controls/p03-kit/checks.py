"""Helper, collector, syntax and compositor configuration readiness."""

from common import isolated, kit, root, run
from pathlib import Path
import ast

run(
    "ai-workspace-helper",
    isolated + ["python3", Path(__file__).parent / "ai-palette-check.py", kit],
)
run("collector-tests", ["python3", root / "tests/test_guided_app.py"])
run("terminal-syntax", ["sh", "-n", kit / "terminal.sh"])
run(
    "sway-config",
    isolated
    + [
        "env",
        "WLR_BACKENDS=headless",
        "WLR_RENDERER=pixman",
        "WLR_LIBINPUT_NO_DEVICES=1",
        "sway",
        "--validate",
        "--config",
        kit / "sway.conf",
    ],
)
for path in list(kit.rglob("*.py")) + list(Path(__file__).parent.glob("*.py")):
    ast.parse(path.read_text())
run("installer-check", ["bash", root / "scripts/install.sh", "--check"])
run("licensing", ["reuse", "--no-multiprocessing", "lint"])

run("documentation", ["python3", Path(__file__).parent / "check-docs.py"])
