import os
import pathlib
import subprocess
import sys
import time
import json
import shutil

root = pathlib.Path.cwd()
kit = pathlib.Path(sys.argv[1]).resolve()
work = root / ".cache" / kit.name
prefix = kit / "prefix"
assert not (kit / "READY").exists()
os.environ["LD_LIBRARY_PATH"] = str(prefix / "lib")
patchelf = os.environ.get("HOLONIGHT_PATCHELF_EXECUTABLE") or shutil.which("patchelf")
assert patchelf, "Set HOLONIGHT_PATCHELF_EXECUTABLE to the existing patchelf executable"
modules = [
    ("config", "holonight-config", ["-DBUILD_TESTING=ON"]),
    ("system-services", "holonight-system-services", ["-DBUILD_TESTS=ON"]),
    ("shell-config", "holonight-shell/libs/holonight-shell-config", []),
    (
        "qt",
        "holonight-qt",
        [
            "-DBUILD_TESTS=ON",
            "-DBUILD_DEMO=ON",
            "-DBUILD_CONTROLS_GALLERY=ON",
            f"-DHOLONIGHT_PATCHELF_EXECUTABLE={patchelf}",
        ],
    ),
    (
        "appearance-adapters",
        "holonight-appearance-adapters",
        [
            "-DBUILD_TESTING=ON",
            f"-DHOLONIGHT_QT_DIR={prefix}",
            f"-DHOLONIGHT_CONFIG_DIR={prefix}",
        ],
    ),
    ("shell", "holonight-shell", ["-DBUILD_TESTS=ON"]),
    ("settings", "holonight-settings", ["-DBUILD_TESTS=ON"]),
    ("ai", "holonight-ai", ["-DBUILD_TESTS=ON"]),
    ("pkg-manager", "holonight-pkg-manager", ["-DBUILD_TESTS=ON"]),
    ("greeter", "holonight-greeter", ["-DBUILD_TESTING=ON"]),
]

if json.loads((kit / "profile.json").read_text())["profile"] == "observer-repair":
    modules = [
        ("config", "holonight-config", ["-DBUILD_TESTING=OFF"]),
        (
            "qt",
            "holonight-qt",
            [
                "-DBUILD_TESTS=ON",
                "-DBUILD_DEMO=OFF",
                "-DBUILD_CONTROLS_GALLERY=OFF",
                f"-DHOLONIGHT_PATCHELF_EXECUTABLE={patchelf}",
            ],
        ),
        ("ai", "holonight-ai", ["-DBUILD_TESTS=OFF"]),
    ]


if json.loads((kit / "profile.json").read_text())["profile"] == "settings-scale1":
    modules = [m for m in modules if m[0] in ("config", "system-services", "shell-config", "qt", "settings")]


def run(name, cmd):
    print(name, flush=True)
    start = time.monotonic()
    with (work / "logs" / f"{name}.log").open("w") as f:
        f.write("$ " + " ".join(map(str, cmd)) + "\n")
        f.flush()
        r = subprocess.run(list(map(str, cmd)), stdout=f, stderr=subprocess.STDOUT)
    with (work / "results.jsonl").open("a") as f:
        f.write(
            json.dumps(
                dict(
                    name=name,
                    command=list(map(str, cmd)),
                    code=r.returncode,
                    seconds=round(time.monotonic() - start, 2),
                )
            )
            + "\n"
        )
    if r.returncode:
        print("FAILED " + name, flush=True)
        sys.exit(r.returncode)


start = sys.argv[2] if len(sys.argv) > 2 else modules[0][0]
for name, source, opts in modules[
    next(i for i, m in enumerate(modules) if m[0] == start) :
]:
    build = work / "build" / name
    run(
        name + "-configure",
        [
            "cmake",
            "-S",
            root / source,
            "-B",
            build,
            "-G",
            "Ninja",
            "-DCMAKE_BUILD_TYPE=Debug",
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            f"-DCMAKE_PREFIX_PATH={prefix}",
            "-DCMAKE_INSTALL_LIBDIR=lib",
            "-DTIDY_JOBS=4",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
        ]
        + opts,
    )
    run(name + "-build", ["cmake", "--build", build, "-j", "6"])
    run(name + "-install", ["cmake", "--install", build])
