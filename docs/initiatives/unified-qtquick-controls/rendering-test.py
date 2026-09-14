#!/usr/bin/env python3
"""Index one human-operated Batch 3 run using the established session collector."""
import argparse
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('application', choices=('haruna', 'ai', 'settings', 'neochat', 'tokodon'))
    parser.add_argument('--style', choices=('Holonight', 'Fusion'), required=True)
    parser.add_argument('--scale', choices=('1', '1.25'), required=True)
    args = parser.parse_args()
    kit = Path(__file__).resolve().parent
    if os.getuid() != 1001 or os.environ.get('UQC_KIT') != str(kit) or not (kit / 'READY').is_file():
        parser.error('use this kit\'s guided-session.py in a fresh tux VT login first')
    os.execv(sys.executable, [sys.executable, str(kit / 'guided-app.py'), args.application,
                             '--style', args.style, '--scale', args.scale, '--index', 'batch3'])



if __name__ == '__main__':
    raise SystemExit(main())
