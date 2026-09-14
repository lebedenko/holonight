#!/usr/bin/env python3
"""Index one human-operated scale-1 Batch 4 run from a fresh isolated profile."""
import argparse
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('application', choices=('neochat', 'tokodon', 'haruna'))
    parser.add_argument('--style', choices=('Holonight', 'Fusion'), required=True)
    parser.add_argument('--diagnostics', action='store_true')
    args = parser.parse_args()
    kit = Path(__file__).resolve().parent
    if os.getuid() != 1001 or os.environ.get('UQC_KIT') != str(kit) or not (kit / 'READY').is_file():
        parser.error("use this kit's guided-session.py from a fresh tux VT login first")
    os.execv(sys.executable, [sys.executable, str(kit / 'guided-app.py'), args.application,
                             '--style', args.style, '--scale', '1', '--index', 'batch4',
                             *(['--palette-diagnostics'] if args.diagnostics else [])])


if __name__ == '__main__':
    main()
