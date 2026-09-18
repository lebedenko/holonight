"""Populate diagnostics and isolated launch helpers after the complete fresh build."""

from common import docs, kit, mask, prefix, root, run, work
from pathlib import Path
import subprocess
import shutil
import json

audit = root / "holonight-qt/docs/sdd/unified-qtquick-controls/audit"
flags = subprocess.check_output(
    ["pkg-config", "--cflags", "--libs", "Qt6Quick", "Qt6Qml"], text=True
).split()
run(
    "render-observer-build",
    [
        "g++",
        "-std=c++23",
        "-shared",
        "-fPIC",
        audit / "render-diagnostics.cpp",
        "-o",
        prefix / "lib/render-diagnostics.so",
        *flags,
    ],
)
if json.loads((kit / "profile.json").read_text())["profile"] not in ("settings-scale1", "ai-scale1"):
    shutil.copy2(work / "build/qt/tests/palette-diagnostics.so", prefix / "lib/palette-diagnostics.so")
    shutil.copy2(audit / "palette-diagnostics.cpp", kit)
    shutil.copy2(docs / "palette-test.py", kit)
    shutil.copy2(Path(__file__).parent / "ai-palette.py", kit)
shutil.copy2(audit / "render-diagnostics.cpp", kit)
for name in ("rendering-test.py", "verify-rendering-kit.py"):
    shutil.copy2(docs / name, kit)
# The existing profile/bus collector is retained. Add disposable HOME and mask
# host providers around the new compositor only; no host session is manipulated.
shutil.copytree(work / "host-plugins", kit / "host-plugins", dirs_exist_ok=True)
manual_mask = [
    part.replace(str(work / "host-plugins"), str(kit / "host-plugins")) for part in mask
]
# A real-seat compositor needs GPU, input and VT devices. Keep the synthetic
# /dev for offscreen checks only; normal user/logind permissions still apply.
device_index = manual_mask.index("--dev")
manual_mask[device_index : device_index + 2] = ["--dev-bind", "/dev", "/dev"]
session = (docs / "guided-session.py").read_text()
session = session.replace(
    'for key in ("XDG_CONFIG_HOME",', 'for key in ("HOME", "XDG_CONFIG_HOME",'
)
session = session.replace(
    'command = ["dbus-run-session",',
    "command = " + repr(manual_mask) + ' + ["--", "dbus-run-session",',
)
(kit / "guided-session.py").write_text(session)
recipes = kit / "preparation"
recipes.mkdir(exist_ok=True)
for path in Path(__file__).parent.glob("*.py"):
    shutil.copy2(path, recipes / path.name)
