#!/usr/bin/env python3
"""Launch one manual dropdown check in the prepared test session."""
import argparse
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("application", choices=("settings", "greeter"))
    parser.add_argument("--style", choices=("default", "Fusion"), default="default")
    parser.add_argument("--scale", choices=("1", "1.25"), default="1.25")
    args = parser.parse_args()
    kit = Path(__file__).resolve().parent
    if os.environ.get("UQC_KIT") != str(kit) or not (kit / "READY").is_file():
        parser.error("run this kit's guided-session.py from a fresh tux VT login first")
    print("Settings: Appearance font dropdowns. Greeter demo: session dropdown.\n"
          "Select a middle or last row, close and reopen with mouse, then keyboard.\n"
          "Check selected row visibility/highlight, hover/scroll, first/last selection,\n"
          "outside dismissal and Escape. Record each result and exact selector.\n"
          "Close the application when finished; retain its printed evidence path.", flush=True)
    return subprocess.call(["python3", str(kit / "guided-app.py"), args.application,
                            "--style", args.style, "--scale", args.scale])


if __name__ == "__main__":
    raise SystemExit(main())
