"""Focused checks first, then full suites for the changed package environment."""
from common import ctest, docs, isolated, kit, prefix, root, run, work
from pathlib import Path
import ast
import sys

ctest("provider-controls-policy", "qt", "runtime_composites|qml_.*policy|startup_|package_install_test")
ctest("settings-controls-policy", "settings", "settings_controls_|qml_import_policy|settings_startup_")
for mode in ("default", "environment", "command-line", "configuration"):
    run("settings-installed-" + mode, isolated + [
        "python3", root / "holonight-settings/tests/check_settings_startup.py",
        prefix / "bin/holonight-settings", prefix / "lib/qt6/qml", mode,
        "--forbid-qml-root", work / "build"])
ctest("provider-full", "qt", ".")
ctest("settings-full", "settings", ".")
run("settings-helper", isolated + ["python3", Path(__file__).with_name("settings-helper.py"), kit])
run("collector-tests", ["python3", root / "tests/test_guided_app.py"])
run("profile-tests", ["python3", root / "tests/test_settings_kit.py"])
run("terminal-syntax", ["sh", "-n", kit / "terminal.sh"])
run("sway-config", isolated + ["env", "WLR_BACKENDS=headless", "WLR_RENDERER=pixman",
    "WLR_LIBINPUT_NO_DEVICES=1", "sway", "--validate", "--config", kit / "sway.conf"])
import runpy
runpy.run_path(str(Path(__file__).with_name("device-check.py")))
for path in kit.rglob("*.py"):
    ast.parse(path.read_text())
run("licensing", ["reuse", "--no-multiprocessing", "lint"])
run("documentation", ["python3", Path(__file__).with_name("check-docs.py")])
