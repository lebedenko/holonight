#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise real installer/uninstaller generation delegation in protected /run roots."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
sys.path.insert(0, str(ROOT / 'scripts'))
from install_state import inventory, manifest_text
import test_install_ownership as ownership
spec = importlib.util.spec_from_file_location('generations', ROOT / 'scripts/manage-images-generations.py')
generations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generations)


def exercise(bundle):
    if os.geteuid() != 0:
        raise ValueError('requires root and protected /run fixture ancestors')
    tempfile.tempdir = '/run'
    fixture = ownership.ViewerOwnership()
    fixture.setUp()
    try:
        fixture.root.chmod(0o755)
        staged = fixture.stage / 'usr/libexec/holonight-images/runtime'
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(bundle, staged)
        (fixture.build / 'module-paths/holonight-images').write_text(''.join(
            '/' + str(path.relative_to(fixture.stage)) + '\n' for path in staged.rglob('*') if path.is_file()))
        runtime = fixture.target / 'usr/libexec/holonight-images/runtime'
        state = fixture.target / 'var/lib/holonight/source-install/manifest.tsv'

        prepared_counter = 0
        def install(accepted=True):
            nonlocal prepared_counter
            prepared_counter += 1
            prepared = fixture.root / f'prepared-{prepared_counter}'
            images = prepared / 'holonight-images' / 'usr/libexec/holonight-images/runtime'
            images.parent.mkdir(parents=True)
            shutil.copytree(staged, images)
            viewer = prepared / 'holonight-viewer/usr/bin/hn-viewer'
            viewer.parent.mkdir(parents=True)
            viewer.write_bytes(b'inert viewer fixture')
            components = {}
            for name in ('holonight-images', 'holonight-viewer'):
                components[name] = {'revision': 'fixture', 'options': [],
                                    'inventory': inventory(prepared / name, name, 'fixture')}
            import hashlib
            host = hashlib.sha256(subprocess.check_output(['pacman', '-Q'], text=True).strip().encode()).hexdigest()
            (prepared / 'prepared.json').write_text(json.dumps({
                'selection': ['holonight-images', 'holonight-viewer'], 'host': host,
                'components': components, 'root': str(fixture.target),
                'protected_images': True, 'adopt': False, 'maintenance': False}))
            result = subprocess.run(['python3', str(ROOT / 'scripts/source-install.py'), 'deploy',
                                     '--root', str(fixture.target), '--prepared', str(prepared)],
                                    capture_output=True, text=True, timeout=60)
            if (result.returncode == 0) != accepted:
                raise AssertionError(result.stdout + result.stderr)
            return result

        def runtime_records():
            return '\n'.join(line for line in state.read_text().splitlines()
                              if '/usr/libexec/holonight-images/runtime' in line)

        def uninstall():
            return subprocess.run(['bash', str(ROOT / 'scripts/uninstall.sh'), '--yes', '--root', str(fixture.target)],
                                  capture_output=True, text=True, timeout=30)

        install()
        first = (runtime / 'current').read_text().strip()
        assert '/runtime/generations/' in state.read_text()
        assert '/runtime/usr/libexec/holonight-images-helper' not in state.read_text()
        manifest = staged / 'manifest.json'
        data = json.loads(manifest.read_text())
        manifest.write_text(json.dumps(data, separators=(',', ':')) + '\n')
        install()
        second = (runtime / 'current').read_text().strip()
        assert first != second
        assert len(list((runtime / 'generations').iterdir())) == 2
        manifest.write_text(json.dumps(data, indent=3) + '\n')
        with generations.lease(runtime / 'generations' / first):
            before = state.read_bytes()
            install(False)
            assert state.read_bytes() == before
            assert (runtime / 'current').read_text().strip() == second
            assert len(list((runtime / 'generations').iterdir())) == 2
        install()
        third = (runtime / 'current').read_text().strip()
        assert third not in (first, second)
        assert not (runtime / 'generations' / first).exists()
        for name in (second, third):
            assert '/runtime/generations/' + name + '/manifest.json' in state.read_text()
        # Generic uninstall must never touch a managed tree when it is modified,
        # unowned or busy, and must preserve the corresponding ownership rows.
        injected = runtime / 'generations' / third / 'unowned'
        injected.write_bytes(b'preserve unowned fixture')
        before = runtime_records()
        result = uninstall()
        assert result.returncode == 0, result.stderr
        assert injected.exists() and runtime_records() == before
        assert not (fixture.target / 'usr/bin/hn-viewer').exists()
        assert '/usr/bin/hn-viewer' not in state.read_text()
        injected.unlink()
        payload = runtime / 'generations' / third / 'manifest.json'
        original = payload.read_bytes()
        payload.write_bytes(original + b' ')
        result = uninstall()
        assert result.returncode == 0, result.stderr
        assert payload.read_bytes() == original + b' '
        assert runtime_records() == before
        payload.write_bytes(original)
        with generations.lease(runtime / 'generations' / third):
            result = uninstall()
            assert result.returncode == 0, result.stderr
            assert (runtime / 'current').exists() and runtime_records() == before
            assert len(list((runtime / 'generations').iterdir())) == 2
        result = uninstall()
        assert result.returncode == 0, result.stderr
        assert not (runtime / 'current').exists()
        assert not list((runtime / 'generations').iterdir())
        assert json.loads((runtime / 'ownership.json').read_text()) == []
        assert state.exists() and '/runtime/ownership.json' in state.read_text()
        assert not (runtime / '.lock').exists()
        result = uninstall()
        assert result.returncode == 0, result.stderr
        assert '/runtime/ownership.json' in state.read_text()
        print('managed installer: generation ownership, upgrades, busy cap, excluded generic loops and conservative repeated uninstall passed')
    finally:
        fixture.doCleanups()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    args = parser.parse_args()
    exercise(args.bundle.resolve(strict=True))
