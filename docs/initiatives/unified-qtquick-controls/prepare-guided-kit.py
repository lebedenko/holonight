#!/usr/bin/env python3
"""Populate a newly configured UQC kit; verification must precede its READY marker."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kit", type=Path)
    args = parser.parse_args()
    kit = args.kit.resolve()
    docs = Path(__file__).resolve().parent
    root = docs.parents[2]
    if kit.parent != Path("/tmp") or not re.fullmatch(r"holonight-uqc201-[A-Za-z0-9_-]+", kit.name):
        parser.error("use a fresh /tmp/holonight-uqc201-* directory")
    if (kit / "READY").exists():
        parser.error("do not change a kit already released for manual checks")
    if (kit / "guided-session.py").exists():
        parser.error("helpers already exist; preserve this kit and use a fresh directory")
    kit.mkdir(mode=0o755, exist_ok=True)
    kit.chmod(0o755)
    source = root / "holonight-qt/docs/sdd/unified-qtquick-controls/audit"
    for name in ("auth-test.py", "registration.py", "terminal.sh"):
        shutil.copy2(source / "auth-test" / name, kit / name)
    shutil.copy2(source / "launch.py", kit / "launch.py")
    for name in ("guided-session.py", "guided-app.py", "GUIDED.md", "MANUAL.md", "AUTHENTICATION.md"):
        shutil.copy2(docs / name, kit / name)
    (kit / "README.md").write_text(
        "# UQC-201 temporary kit\n\n"
        "Use GUIDED.md, starting with batch 1 after preparation creates READY.\n"
        "This kit's path is " + str(kit) + ". Substitute it for any recorded run path.\n")
    owned = kit / "owned-auth"
    owned.mkdir()
    for name in ("auth-test.py", "registration.py"):
        shutil.copy2(kit / name, owned / name)
    subprocess.run(["patch", "--batch", "--fuzz=0", "-p0", "-i", str(docs / "owned-auth.patch")],
                   cwd=owned, check=True)
    terminal = f"/bin/sh {kit}/terminal.sh"
    (kit / "hyprland.conf").write_text(
        f"monitor = , preferred, auto, 1\nexec-once = {terminal}\n"
        f"bind = SUPER, Return, exec, {terminal}\n"
        "bind = SUPER SHIFT, E, exit,\nbind = SUPER, Q, killactive,\n"
        "input {\n    kb_layout = us\n}\ngeneral {\n    gaps_in = 5\n    gaps_out = 10\n}\n")
    (kit / "sway.conf").write_text(
        f"set $mod Mod4\noutput * scale 1\nexec {terminal}\n"
        f"bindsym $mod+Return exec {terminal}\n"
        "bindsym $mod+Shift+e exit\nbindsym $mod+q kill\n")
    inventory = []
    for command in (["git", "rev-parse", "HEAD"], ["git", "submodule", "status"],
                    ["pacman", "-Q", "haruna", "neochat", "tokodon", "hyprpolkitagent",
                     "qt6-base", "qt6-declarative", "hyprland", "sway", "cmake", "gcc"]):
        inventory.append(subprocess.check_output(command, cwd=root, text=True))
    (kit / "PROVIDER.txt").write_text("Configured prefix: " + str(kit / "prefix") + "\n" + "\n".join(inventory))
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                    "-i", "testsrc2=size=640x360:rate=24", "-t", "5", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", str(kit / "sample.mp4")], check=True)
    print("Prepared helpers only; validate the configured installation before creating READY:", kit)


if __name__ == "__main__":
    main()
