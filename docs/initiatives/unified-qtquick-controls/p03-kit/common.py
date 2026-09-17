"""Shared paths, isolation and recorded command execution for the P03 kit."""

import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import time

root = Path.cwd()
kit = Path(sys.argv[1]).resolve()
work = root / ".cache" / kit.name
prefix = kit / "prefix"
docs = root / "docs/initiatives/unified-qtquick-controls"
assert kit.parent == Path("/tmp") and kit.name.startswith("holonight-uqc201-p03-")
assert not (kit / "READY").exists(), "Released kits are immutable"
os.environ["LD_LIBRARY_PATH"] = str(prefix / "lib")
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
mask = [
    "bwrap",
    "--die-with-parent",
    "--unshare-net",
    "--bind",
    "/",
    "/",
    "--dev",
    "/dev",
    "--proc",
    "/proc",
]
for path in [
    Path("/usr/lib/qt6/qml/Holonight"),
    Path("/usr/local/lib/qt6/qml/Holonight"),
]:
    if path.exists():
        mask += ["--tmpfs", str(path)]
for base in ("/usr/lib", "/usr/local/lib"):
    for pattern in ("*holonight*.so*", "*HoloNight*.so*"):
        for path in Path(base).glob(pattern):
            if path.is_file() and not path.is_symlink():
                mask += ["--ro-bind", "/dev/null", str(path)]
# Hide plugin entries rather than replacing them with unreadable files: Qt scans
# plugin metadata even when another theme is selected.
for base in ("/usr/lib/qt6/plugins", "/usr/local/lib/qt6/plugins"):
    for category in ("platformthemes", "styles"):
        original = Path(base) / category
        if not original.exists():
            continue
        mirror = work / "host-plugins" / base.strip("/").replace("/", "-") / category
        mirror.mkdir(parents=True, exist_ok=True)
        for path in original.iterdir():
            if path.is_file() and "holonight" not in path.name.lower():
                target = mirror / path.name
                if not target.exists():
                    shutil.copy2(path, target)
        mask += ["--ro-bind", str(mirror), str(original)]
isolated = mask + [
    "--setenv",
    "UQC_ISOLATED",
    "1",
    "--",
    "python3",
    str(root / "holonight-shell/scripts/run-isolated-test.py"),
]


def run(name, command, expected=0):
    if len(sys.argv) > 2 and name not in sys.argv[2:]:
        return
    command = list(map(str, command))
    print(name, flush=True)
    start = time.monotonic()
    log_path = work / "logs" / (name + ".log")
    if log_path.exists():
        attempt = len(list(log_path.parent.glob(name + ".attempt-*.log"))) + 1
        log_path.rename(log_path.with_name(name + ".attempt-" + str(attempt) + ".log"))
    with log_path.open("w") as log:
        log.write("$ " + " ".join(command) + "\n")
        log.flush()
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    with (work / "focused-results.jsonl").open("a") as log:
        log.write(
            json.dumps(
                dict(
                    name=name,
                    command=command,
                    code=result.returncode,
                    expected=expected,
                    environment={
                        key: os.environ.get(key)
                        for key in (
                            "QT_QUICK_CONTROLS_STYLE",
                            "QT_SCALE_FACTOR",
                            "LD_LIBRARY_PATH",
                        )
                    },
                    seconds=round(time.monotonic() - start, 2),
                )
            )
            + "\n"
        )
    assert result.returncode == expected, name


def ctest(name, component, regex):
    run(
        name,
        isolated
        + [
            "ctest",
            "--test-dir",
            work / "build" / component,
            "-R",
            regex,
            "--output-on-failure",
            "--no-tests=error",
            "-j",
            "1",
        ],
    )
