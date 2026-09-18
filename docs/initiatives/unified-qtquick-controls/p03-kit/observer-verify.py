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

# Inspect device identities through the exact launcher namespace without opening
# devices or starting/focusing a compositor. Normal seat access remains manual.
tree = ast.parse((kit / "guided-session.py").read_text())
commands = [
    node
    for node in ast.walk(tree)
    if isinstance(node, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "command" for t in node.targets)
]
command = next(node.value for node in commands if isinstance(node.value, ast.BinOp))
mask = ast.literal_eval(command.left)
assert "--dev-bind" in mask and "--unshare-net" in mask
assert "--dev" not in mask
probe = "import os, pathlib, json, socket; print(json.dumps({'devices': {str(p): [p.stat().st_dev, p.stat().st_rdev] for base in ['/dev/dri', '/dev/input'] for p in pathlib.Path(base).glob('*')}, 'net': socket.if_nameindex()}))"
run(
    "real-seat-device-bindings",
    [
        sys.executable,
        "-c",
        "\n".join(
            [
                "import json, subprocess",
                "probe = " + repr(probe),
                "host = json.loads(subprocess.check_output(['python3', '-c', probe], text=True))",
                "isolated = json.loads(subprocess.check_output("
                + repr(mask + ["--", "python3", "-c", probe])
                + ", text=True))",
                "assert host['devices'] and host['devices'] == isolated['devices']",
                "assert [name for _, name in isolated['net']] == ['lo']",
                "print(json.dumps(isolated, indent=2))",
            ]
        ),
    ],
)
