"""Bounded UQC-224 installed-observer verification; no consumer suites."""

from common import ctest, isolated, kit, prefix, root, run, work
import ast
import sys

ctest("provider-window-core", "qt", "holonight_window_palette_|core_isolation")
ctest("provider-observer-policy", "qt", "palette_diagnostics_|qml_.*policy")
audit = root / "holonight-qt/docs/sdd/unified-qtquick-controls/audit"
run(
    "diagnostic-configure",
    ["cmake", "-S", audit, "-B", work / "diagnostic-build", "-G", "Ninja"],
)
run(
    "diagnostic-build",
    [
        "cmake",
        "--build",
        work / "diagnostic-build",
        "--target",
        "uqc-palette-transition",
        "-j",
        "4",
    ],
)
run(
    "observer-collect",
    isolated
    + [
        "python3",
        audit / "palette-stability.py",
        "collect",
        "--output",
        work / "matrix",
        "--prefix",
        prefix,
        "--executable",
        work / "diagnostic-build/uqc-palette-transition",
        "--observer",
        prefix / "lib/palette-diagnostics.so",
    ],
)
run(
    "observer-assert",
    ["python3", audit / "palette-stability.py", "assert", "--output", work / "matrix"],
)
run(
    "observer-installed-regression",
    isolated
    + [
        "env",
        "QT_QPA_PLATFORM=offscreen",
        "QT_QUICK_CONTROLS_STYLE=Fusion",
        "UQC_IMPORT_PATH=" + str(prefix / "lib/qt6/qml"),
        "LD_PRELOAD=" + str(prefix / "lib/palette-diagnostics.so"),
        "HOLONIGHT_PALETTE_DIAGNOSTICS=1",
        work / "build/qt/tests/holonight_palette_diagnostics_check",
    ],
)

import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("device-check.py")))
