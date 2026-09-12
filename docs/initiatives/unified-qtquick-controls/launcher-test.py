#!/usr/bin/env python3
"""Run the isolated shell or request its launcher from the test-session terminal."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "toggle"))
    parser.add_argument("--style", choices=("default", "Fusion"), default="default")
    parser.add_argument("--scale", choices=("1", "1.25"), default="1.25")
    args = parser.parse_args()
    kit = Path(__file__).resolve().parent
    if os.environ.get("UQC_KIT") != str(kit) or not (kit / "READY").is_file():
        parser.error("start this kit's guided-session.py from a fresh tux VT login first")
    if args.action == "run":
        print("In a second test terminal, run launcher-test.py toggle. Leave the pointer\n"
              "over another result while using Up/Down and Enter; compare browse/search,\n"
              "filtering and reopen. Move within the same row, then click immediately.\n"
              "Use Ctrl+C here when finished; retain the printed evidence directory.", flush=True)
        # Keep one supervising process so Ctrl+C cannot kill the evidence helper
        # before it records the shell's termination.
        os.execv(sys.executable, [sys.executable, str(kit / "guided-app.py"), "shell",
                                 "--style", args.style, "--scale", args.scale])
    env = dict(os.environ, LD_LIBRARY_PATH=str(kit / "prefix/lib"))
    return subprocess.call([str(kit / "prefix/bin/holonight-shell"), "--toggle-launcher"], env=env)


if __name__ == "__main__":
    raise SystemExit(main())
