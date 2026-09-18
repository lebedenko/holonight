"""Focused readiness: native controls, staged diagnosis and kit startup contracts."""

from common import ctest, isolated, prefix, root, run, work, kit
import os
import json
import runpy
from pathlib import Path

if json.loads((kit / "profile.json").read_text())["profile"] == "observer-repair":
    runpy.run_path(
        str(Path(__file__).with_name("observer-verify.py")), run_name="__main__"
    )
    raise SystemExit(0)

ctest("provider-window-core", "qt", "holonight_window_palette_|core_isolation")
ctest(
    "provider-palette-policy",
    "qt",
    "palette|runtime_composites|core_isolation|qml_.*policy",
)
ctest("provider-package", "qt", "package_install_test")
for scale in ("1", "1.25"):
    os.environ["QT_SCALE_FACTOR"] = scale
    ctest("ai-controls-" + scale, "ai", "^runtime_controls_|qml_import_policy")
    ctest(
        "settings-controls-" + scale,
        "settings",
        "^settings_controls_|qml_import_policy",
    )
    for style in ("Holonight", "Fusion"):
        os.environ["QT_QUICK_CONTROLS_STYLE"] = style
        ctest(
            "ai-qml-" + style + "-" + scale,
            "ai",
            "Qml|CanonicalQmlModules|BottomAnchoredListView|MarkdownBlock",
        )
    os.environ.pop("QT_QUICK_CONTROLS_STYLE", None)
os.environ.pop("QT_SCALE_FACTOR", None)
ctest("shell-launch-policy", "shell", "^uqc_launch$|^uqc_policy|^uqc_runtime_")
ctest("settings-startup", "settings", "^settings_startup_")
ctest("provider-startup", "qt", "startup_")
for name, exe in [
    ("ai", "holonight-chat"),
    ("pkg-manager", "holonight-packages"),
    ("greeter", "holonight-greeter"),
]:
    checker = root / ("holonight-" + name) / "scripts/check-runtime-launches.py"
    for kind, binary in [
        ("build", work / "build" / name / exe),
        ("installed", prefix / "bin" / exe),
    ]:
        cmd = isolated + [
            "python3",
            checker,
            binary,
            prefix,
            "--logs",
            work / "logs" / (name + "-" + kind),
        ]
        if kind == "installed":
            cmd += ["--forbid-path", work / "build"]
        run(name + "-" + kind, cmd)
for mode in ("default", "environment", "command-line", "configuration"):
    run(
        "settings-installed-" + mode,
        isolated
        + [
            "python3",
            root / "holonight-settings/tests/check_settings_startup.py",
            prefix / "bin/holonight-settings",
            prefix / "lib/qt6/qml",
            mode,
            "--forbid-qml-root",
            work / "build",
        ],
    )
    for exe in ("holonight_demo", "holonight_controls_gallery"):
        run(
            exe + "-installed-" + mode,
            isolated
            + [
                "python3",
                root / "holonight-qt/tests/check_example_startup.py",
                prefix / "bin" / exe,
                prefix / "lib/qt6/qml",
                mode,
            ],
        )
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
matrix = ["python3", audit / "palette-transition.py"]
run(
    "diagnostic-collect",
    isolated
    + matrix
    + [
        "collect",
        "--output",
        work / "matrix",
        "--prefix",
        prefix,
        "--executable",
        work / "diagnostic-build/uqc-palette-transition",
    ],
)
for name, scope, window, expected in [
    ("shared", "p03", "HnApplicationWindow", 0),
    ("positive", "positive", "all", 0),
    ("plain-boundary", "p03", "Window", 1),
    ("external-boundary", "external", "native", 1),
]:
    run(
        "diagnostic-" + name,
        matrix
        + ["assert", "--scope", scope, "--window", window, "--output", work / "matrix"],
        expected,
    )
