#!/usr/bin/env python3
"""Exercise actual helper refusals without launching a compositor or authentication."""
import os
from pathlib import Path
import subprocess
import sys

kit = Path(sys.argv[1]).resolve()
docs = Path(__file__).resolve().parents[1] / 'docs/initiatives/unified-qtquick-controls'
assert os.getuid() != 1001, 'run preparation as the development user'
commands = [(['python3', str(kit / 'authentication-test.py'), 'polkit'], 'run as tux'),
            (['python3', str(kit / 'guided-session.py'), 'hyprland'], 'real tux VT login')]
if len(sys.argv) == 3:
    commands += [(['python3', str(docs / 'prepare-authentication-kit.py'), '--resume', str(kit)], 'preserve released'),
                 (['python3', str(docs / 'restore-authentication-kit.py'), sys.argv[2]], 'preserving existing')]
for command, expected in commands:
    result = subprocess.run(command, capture_output=True, text=True, timeout=15,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert result.returncode != 0 and expected in result.stderr, result.stdout + result.stderr
    print('PASS:', expected)
