#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicitly synchronize the versioned bundle, or check drift without writing."""
import argparse
import json
from pathlib import Path
import shutil
import sys

FILES = ['VERSION', 'workflow.py', 'compilation.py', 'qml_policy.py', 'clang-format',
         'clang-tidy-qt', 'clang-tidy-cpp', 'clang-tidy-tests', 'clangd', 'README.md']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--module', type=Path, action='append')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    modules = args.module or sorted(p for p in root.iterdir() if (p / '.git').exists())
    drift = []
    for module in modules:
        for name in FILES:
            source, target = root / 'tooling' / name, module / 'tooling' / name
            if not target.exists() or source.read_bytes() != target.read_bytes():
                drift.append(str(target.relative_to(root)) if target.is_relative_to(root) else str(target))
                if not args.check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
        config_path = module / 'tooling/module.json'
        if config_path.exists():
            config = json.loads(config_path.read_text())
            if 'cpp' in config.get('languages', []):
                instantiated = {'clang-format': module / '.clang-format', 'clangd': module / '.clangd',
                                ('clang-tidy-cpp' if module.name == 'holonightd' else 'clang-tidy-qt'): module / '.clang-tidy'}
                if (module / 'tests').is_dir() and module.name != 'holonight-icons':
                    instantiated['clang-tidy-tests'] = module / 'tests/.clang-tidy'
                for name, target in instantiated.items():
                    source = root / 'tooling' / name
                    if not target.exists() or source.read_bytes() != target.read_bytes():
                        drift.append(str(target))
                        if not args.check:
                            shutil.copyfile(source, target)
    for path in drift:
        print(('DRIFT ' if args.check else 'SYNC ') + path)
    return int(args.check and bool(drift))

if __name__ == '__main__':
    sys.exit(main())
