"""Stage an explicitly prepared native Images build through the real ownership functions.

Run with HOLONIGHT_IMAGES_INSTALL_BUILD pointing at the opt-in provider build.
No host installation or services are modified.
"""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_install_ownership as ownership


class IsolatedImagesOwnership(unittest.TestCase):
    def test_normal_staging_prepares_runtime_before_installing_dependents(self):
        fixture = ownership.ViewerOwnership()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        log = fixture.root / 'stage-commands'
        for module in ('holonight-images', 'holonight-thumbnails'):
            (fixture.build / 'build' / module).mkdir(parents=True)
        for tool in ('cmake', 'python3'):
            command = fixture.commands / tool
            command.write_text('#!/bin/sh\nprintf "%s\\n" "' + tool + ' $*" >> "' + str(log) + '"\n')
            command.chmod(0o755)
        result = fixture.run_functions('configure_and_stage holonight-images; configure_and_stage holonight-thumbnails')
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = log.read_text().splitlines()
        self.assertIn('-DHOLONIGHT_IMAGES_ISOLATED=ON', commands[0])
        self.assertIn('--build', commands[1])
        self.assertIn('prepare-isolated-runtime.py --helper', commands[2])
        self.assertIn('--plugins /usr/lib/qt6/plugins', commands[2])
        self.assertIn('-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE=', commands[3])
        self.assertIn('--install', commands[4])
        self.assertIn('-DHOLONIGHT_THUMBNAILS_ISOLATED=ON', commands[5])
        self.assertIn('-DCMAKE_INSTALL_PREFIX=/usr', commands[0])

    @unittest.skipUnless(os.environ.get('HOLONIGHT_IMAGES_INSTALL_BUILD'), 'explicit native Images build required')
    def test_real_staging_inventory_collision_and_conservative_uninstall(self):
        fixture = ownership.ViewerOwnership()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        # Use a fresh stage, preserving the common installer fixture's unrelated payload.
        build = Path(os.environ['HOLONIGHT_IMAGES_INSTALL_BUILD']).resolve()
        env = dict(os.environ, DESTDIR=str(fixture.stage))
        subprocess.run(['cmake', '--install', str(build), '--prefix', '/usr'], env=env,
                       check=True, capture_output=True)
        installed = (build / 'install_manifest.txt').read_text().splitlines()
        self.assertTrue(any('/runtime/manifest.json' in path for path in installed))
        runtime = fixture.stage / 'usr/libexec/holonight-images/runtime'
        runtime_files = {str(p.relative_to(fixture.stage)) for p in runtime.rglob('*') if p.is_file()}
        self.assertTrue(runtime_files <= {p.lstrip('/') for p in installed})
        # CMake's manifest, not directory differences, assigns every artifact its owner.
        module_build = fixture.build / 'build/holonight-images'
        module_build.mkdir(parents=True)
        (module_build / 'install_manifest.txt').write_text('\n'.join(installed) + '\n')
        fixture.module = 'holonight-images'
        manifest = fixture.make_manifest()
        entries = {row[5]: row for line in manifest.splitlines() if (row := line.split('\t'))}
        for name in runtime_files:
            self.assertEqual(entries['/' + name][0], 'holonight-images')
            self.assertEqual(entries['/' + name][4], hashlib.sha256((fixture.stage / name).read_bytes()).hexdigest())
        helper = fixture.target / 'usr/libexec/holonight-images/runtime/usr/libexec/holonight-images-helper'
        helper.parent.mkdir(parents=True)
        helper.write_bytes(b'unowned collision')
        collision = fixture.run_functions('collision_check')
        self.assertNotEqual(collision.returncode, 0)
        self.assertEqual(helper.read_bytes(), b'unowned collision')
        helper.unlink()  # Test-owned collision fixture only.
        result = fixture.run_functions('collision_check; copy_stage')
        self.assertEqual(result.returncode, 0, result.stderr)
        modified = fixture.target / 'usr/libexec/holonight-images/runtime/manifest.json'
        modified.write_bytes(b'user-modified runtime manifest')
        result = subprocess.run(['bash', str(ownership.ROOT / 'scripts/uninstall.sh'), '--yes', '--root', str(fixture.target)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(modified.read_bytes(), b'user-modified runtime manifest')
        self.assertFalse(helper.exists())
        for name in runtime_files - {'usr/libexec/holonight-images/runtime/manifest.json'}:
            self.assertFalse((fixture.target / name).exists(), name)


if __name__ == '__main__':
    unittest.main()
