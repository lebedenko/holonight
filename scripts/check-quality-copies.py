#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check every declared submodule's standalone analysis helpers for drift."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
paths = subprocess.check_output(['git', 'config', '--file', str(root / '.gitmodules'),
                                 '--get-regexp', r'^submodule\..*\.path$'], text=True)
for line in paths.splitlines():
    component = line.split(maxsplit=1)[1]
    for name in ('quality.py', 'test-quality.py'):
        target = root / component / 'scripts' / name
        if not target.exists() or target.read_bytes() != (root / 'scripts' / name).read_bytes():
            raise SystemExit(f'Quality helper drift: {target}')
print('Quality helper copies match all declared submodules')
