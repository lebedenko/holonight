#!/usr/bin/env python3
"""Build a fresh dropdown/input verification kit; retain commands across reboots."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", type=Path, help="resume an unreleased kit after a preparation failure")
    args = parser.parse_args()
    docs = Path(__file__).resolve().parent
    root = docs.parents[2]
    kit = args.resume.resolve() if args.resume else Path(tempfile.mkdtemp(prefix="holonight-uqc206-", dir="/tmp"))
    if kit.parent != Path("/tmp") or not kit.name.startswith("holonight-uqc206-"):
        parser.error("expected /tmp/holonight-uqc206-* directory")
    if (kit / "READY").exists():
        parser.error("preserve released kits; prepare a fresh one")
    kit.mkdir(exist_ok=True)
    kit.chmod(0o755)
    work = root / ".cache" / kit.name
    work.mkdir(exist_ok=True)
    (work / "logs").mkdir(exist_ok=True)
    prefix = kit / "prefix"
    (root / ".cache/uqc206-kit").write_text(str(kit) + "\n")
    shutil.copy2(__file__, work / "prepare-dropdown-kit.py")

    def run(name, command, env=None):
        print(name, flush=True)
        with (work / "logs" / (name + ".log")).open("a") as log:
            result = subprocess.run(list(map(str, command)), cwd=root, env=env,
                                    stdout=log, stderr=subprocess.STDOUT)
        with (work / "results.jsonl").open("a") as log:
            log.write(json.dumps(dict(name=name, command=list(map(str, command)), code=result.returncode)) + "\n")
        if result.returncode:
            raise SystemExit(f"{name} failed; see {work}/logs/{name}.log; resume with --resume {kit}")

    old = root / ".cache/uqc201-guided-qht3_tjs/build"
    for name, source in (("config", root / "holonight-config"),
                         ("system-services", root / "holonight-system-services"),
                         ("shell-config", root / "holonight-shell/libs/holonight-shell-config")):
        build = old / name
        run(name + "-configure", ["cmake", "-S", source, "-B", build,
                                 f"-DCMAKE_INSTALL_PREFIX={prefix}", f"-DCMAKE_PREFIX_PATH={prefix}",
                                 f"-DHoloNightConfig_DIR={prefix}/lib/cmake/HoloNightConfig"])
        run(name + "-build", ["cmake", "--build", build, "-j", "4"])
        run(name + "-install", ["cmake", "--install", build])
    run("qt-build", ["cmake", "--build", root / "holonight-qt/build", "-j", "4"])
    run("qt-install", ["cmake", "--install", root / "holonight-qt/build", "--prefix", prefix])
    for name in ("settings", "greeter"):
        build = work / "build" / name
        run(name + "-configure", ["cmake", "-S", root / ("holonight-" + name), "-B", build,
                                 "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Debug",
                                 "-DBUILD_TESTS=" + ("ON" if name == "settings" else "OFF"),
                                 "-DBUILD_TESTING=OFF", "-DCMAKE_INSTALL_LIBDIR=lib",
                                 f"-DCMAKE_PREFIX_PATH={prefix}", f"-DCMAKE_INSTALL_PREFIX={prefix}"])
        targets = ["--target", "holonight-settings", "settings_controls_acceptance"] if name == "settings" else []
        run(name + "-build", ["cmake", "--build", build, "-j", "4", *targets])
        run(name + "-install", ["cmake", "--install", build])
    run("shell-install", ["cmake", "--install", root / "holonight-shell/build", "--prefix", prefix])

    # Keep the established real-VT/private-bus/disposable-profile session contract.
    for name in ("guided-session.py", "guided-app.py", "dropdown-test.py", "launcher-test.py", "verify-input-kit.py"):
        shutil.copy2(docs / name, kit / name)
    shutil.copy2(root / "holonight-qt/docs/sdd/unified-qtquick-controls/audit/auth-test/terminal.sh", kit)
    terminal = f"/bin/sh {kit}/terminal.sh"
    (kit / "sway.conf").write_text(
        f"set $mod Mod4\noutput * scale 1\nexec {terminal}\n"
        f"bindsym $mod+Return exec {terminal}\n"
        "bindsym $mod+Shift+e exit\nbindsym $mod+q kill\n")
    (kit / "hyprland.conf").write_text(
        f"monitor = , preferred, auto, 1\nexec-once = {terminal}\n"
        f"bind = SUPER, Return, exec, {terminal}\n"
        "bind = SUPER SHIFT, E, exit,\nbind = SUPER, Q, killactive,\n")
    inventory = subprocess.check_output(["pacman", "-Q", "qt6-base", "qt6-declarative",
                                         "hyprpolkitagent", "sway", "hyprland"], text=True)
    (kit / "PROVIDER.txt").write_text("Focused verification candidate from recorded revisions; not ecosystem integration.\n" + inventory)
    revisions = {}
    for name in ("holonight-config", "holonight-system-services", "holonight-shell", "holonight-qt",
                 "holonight-settings", "holonight-greeter"):
        revisions[name] = subprocess.check_output(["git", "-C", str(root / name), "rev-parse", "HEAD"], text=True).strip()
    (kit / "revisions.json").write_text(json.dumps(revisions, indent=2) + "\n")
    (kit / "provider.patch").write_bytes(subprocess.check_output(
        ["git", "-C", str(root / "holonight-qt"), "diff", "HEAD", "--", "qml"]))

    mask = ["bwrap", "--die-with-parent", "--bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
            "--tmpfs", "/usr/lib/qt6/qml/Holonight"]
    for path in Path("/usr/lib").glob("*holonight*.so*"):
        if path.is_file() and not path.is_symlink():
            mask += ["--ro-bind", "/dev/null", str(path)]
    env = dict(os.environ, LD_LIBRARY_PATH=str(prefix / "lib"))
    for style in ("Holonight", "Fusion"):
        for scale in ("1", "1.25"):
            run(f"dropdown-{style}-{scale}", mask + ["--", "env", "QT_QPA_PLATFORM=offscreen",
                "QT_QPA_PLATFORMTHEME=", "QT_QUICK_BACKEND=software", "QT_QUICK_CONTROLS_CONF=",
                "QT_LOGGING_RULES=qt.quick.viewport.debug=true",
                f"QT_QUICK_CONTROLS_STYLE={style}", f"QT_SCALE_FACTOR={scale}",
                f"UQC_IMPORT_PATH={prefix}/lib/qt6/qml",
                root / "holonight-qt/build/tests/holonight_runtime_composite_tests",
                "--gtest_filter=InputInteraction*.*:Controls/DropdownInteraction.*"], env)
    isolated = mask + ["--setenv", "UQC_ISOLATED", "1", "--", "python3",
                       root / "holonight-shell/scripts/run-isolated-test.py"]
    for mode in ("default", "environment", "command-line", "configuration"):
        run("settings-" + mode, isolated + ["python3", root / "holonight-settings/tests/check_settings_startup.py",
            prefix / "bin/holonight-settings", prefix / "lib/qt6/qml", mode, "--forbid-qml-root", root], env)
    run("greeter-launches", mask + ["--", "python3", root / "holonight-greeter/scripts/check-runtime-launches.py",
        prefix / "bin/holonight-greeter", prefix, "--forbid-path", root, "--logs", work / "logs/greeter-launches"], env)
    run("runtime-isolation", isolated + ["python3", kit / "verify-input-kit.py", kit,
        "--settings-acceptance", work / "build/settings/apps/settings/settings_controls_acceptance",
        "--logs", work / "logs/runtime"], env)
    run("evidence-regressions", ["python3", root / "tests/test_guided_app.py"])
    for source, installed in (("qml/ComboBox.qml", "Holonight/ComboBox.qml"),
                              ("qml/controls/HnIconComboBox.qml", "Holonight/Controls/HnIconComboBox.qml")):
        assert (root / "holonight-qt" / source).read_bytes() == (prefix / "lib/qt6/qml" / installed).read_bytes()
    for path in kit.glob("*.py"):
        ast.parse(path.read_text())
    run("terminal-syntax", ["sh", "-n", kit / "terminal.sh"])
    run("launcher-help", ["python3", kit / "dropdown-test.py", "--help"])
    (kit / "README.md").write_text((docs / "INPUT.md").read_text().replace("__KIT__", str(kit)))
    checksums = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(kit)}"
                 for path in sorted(kit.rglob("*")) if path.is_file()]
    (kit / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
    (kit / "READY").write_text("Verified dropdown/input candidate; see revisions.json, SHA256SUMS and retained runtime evidence.\n")
    archive = work / (kit.name + ".tar.gz")
    with tarfile.open(archive, "w:gz") as saved:
        saved.add(kit, arcname=kit.name)
    print(f"READY: {kit}\nPersistent archive: {archive}", flush=True)


if __name__ == "__main__":
    main()
