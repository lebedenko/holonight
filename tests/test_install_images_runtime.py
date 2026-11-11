"""Stage an explicitly prepared native Images build through the real ownership functions.

Run with HOLONIGHT_IMAGES_INSTALL_BUILD pointing at the opt-in provider build.
Optionally set HOLONIGHT_IMAGES_INSTALL_CONSUMER and HOLONIGHT_IMAGES_INSTALL_FIXTURES
to run an existing native installed consumer against the upgraded runtime.
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
        # Model a previous generation with an additional owned dependency.
        obsolete = helper.parent / 'retired-dependency.so'
        obsolete.write_bytes(b'old runtime dependency')
        obsolete.chmod(0o644)
        state = fixture.target / 'var/lib/holonight/source-install/manifest.tsv'
        with state.open('a') as stream:
            stream.write('\t'.join(['holonight-images', ownership.FIXTURE_REVISION, 'f', '644',
                                     hashlib.sha256(obsolete.read_bytes()).hexdigest(),
                                     '/' + str(obsolete.relative_to(fixture.target))]) + '\n')
        for _ in range(2):
            result = fixture.run_functions('collision_check; copy_stage')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(obsolete.exists())
        consumer = os.environ.get('HOLONIGHT_IMAGES_INSTALL_CONSUMER')
        if consumer:
            result = subprocess.run([consumer, str(helper.parents[2]),
                                     os.environ['HOLONIGHT_IMAGES_INSTALL_FIXTURES']],
                                    capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        modified = fixture.target / 'usr/libexec/holonight-images/runtime/manifest.json'
        modified.write_bytes(b'user-modified runtime manifest')
        result = subprocess.run(['bash', str(ownership.ROOT / 'scripts/uninstall.sh'), '--yes', '--root', str(fixture.target)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(modified.read_bytes(), b'user-modified runtime manifest')
        self.assertFalse(helper.exists())
        for name in runtime_files - {'usr/libexec/holonight-images/runtime/manifest.json'}:
            self.assertFalse((fixture.target / name).exists(), name)


class RuntimeUpgrade(unittest.TestCase):
    base = 'usr/libexec/holonight-images/runtime'

    def setUp(self):
        self.fixture = ownership.ViewerOwnership()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.runtime = self.fixture.stage / self.base
        self.installed = self.fixture.target / self.base
        self.state = self.fixture.target / 'var/lib/holonight/source-install/manifest.tsv'
        self.bundle({'old/dependency.so': b'old dependency', 'keep.so': b'generation one'})
        self.deploy()
        self.bundle({'keep.so': b'generation two'})

    def bundle(self, files, verifier_exit=0):
        if self.runtime.exists():
            shutil.rmtree(self.runtime)
        files = dict(files)
        files['usr/libexec/holonight-images-helper'] = (
            '#!/bin/sh\nexit ' + str(verifier_exit) + '\n').encode()
        for name, data in files.items():
            path = self.runtime / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if name.endswith('holonight-images-helper'):
                path.chmod(0o755)
        module_paths = self.fixture.build / 'module-paths/holonight-images'
        module_paths.write_text(''.join('/' + str(p.relative_to(self.fixture.stage)) + '\n'
                                        for p in self.runtime.rglob('*') if p.is_file()))
        result = self.fixture.run_functions('make_manifest')
        self.assertEqual(result.returncode, 0, result.stderr)

    def deploy(self):
        result = self.fixture.run_functions('collision_check; copy_stage')
        self.assertEqual(result.returncode, 0, result.stderr)

    def assert_blocked(self, commands='ADOPT_EXISTING=1; collision_check; copy_stage'):
        manifest = self.state.read_bytes()
        keep = (self.installed / 'keep.so').read_bytes()
        result = self.fixture.run_functions(commands)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('resolve it manually', result.stderr)
        self.assertEqual(self.state.read_bytes(), manifest)
        self.assertEqual((self.installed / 'keep.so').read_bytes(), keep)
        self.assertTrue((self.installed / 'old/dependency.so').exists())

    def test_upgrade_removes_obsolete_files_and_empty_directories_and_repeats(self):
        unrelated = self.fixture.target / 'unrelated'
        unrelated.write_bytes(b'preserve')
        for _ in range(2):
            self.deploy()
            self.assertFalse((self.installed / 'old').exists())
            self.assertEqual({str(p.relative_to(self.installed)) for p in self.installed.rglob('*')},
                             {str(p.relative_to(self.runtime)) for p in self.runtime.rglob('*')})
        self.assertEqual(unrelated.read_bytes(), b'preserve')

    def test_modified_obsolete_hash_or_mode_blocks(self):
        path = self.installed / 'old/dependency.so'
        path.write_bytes(b'modified')
        self.assert_blocked()
        path.write_bytes(b'old dependency')
        path.chmod(0o600)
        self.assert_blocked()

    def test_unowned_and_forgotten_files_block(self):
        path = self.installed / 'old/unowned.so'
        path.write_bytes(b'unowned')
        self.assert_blocked()
        path.unlink()
        self.state.write_text(''.join(line + '\n' for line in self.state.read_text().splitlines()
                                      if not line.endswith('/old/dependency.so')))
        self.assert_blocked()

    def test_unowned_empty_directory_and_all_conflicts_are_reported(self):
        (self.installed / 'empty-unowned').mkdir()
        (self.installed / 'second-conflict').write_bytes(b'unowned')
        result = self.fixture.run_functions('collision_check; copy_stage')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('empty-unowned', result.stderr)
        self.assertIn('second-conflict', result.stderr)
        self.assertTrue((self.installed / 'old/dependency.so').exists())

    def test_unowned_current_file_cannot_be_adopted(self):
        self.state.write_text(''.join(line + '\n' for line in self.state.read_text().splitlines()
                                      if not line.endswith('/keep.so')))
        self.assert_blocked()

    def test_unexpected_symlink_and_incompatible_type_block(self):
        link = self.installed / 'unexpected'
        link.symlink_to(self.fixture.root)
        self.assert_blocked()
        link.unlink()
        keep = self.installed / 'keep.so'
        keep.unlink()
        keep.mkdir()
        previous = self.state.read_bytes()
        result = self.fixture.run_functions('collision_check; copy_stage')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.state.read_bytes(), previous)
        self.assertTrue(keep.is_dir())

    def test_symlinked_parent_blocks_without_touching_external_tree(self):
        parent = self.installed.parent
        outside = self.fixture.root / 'external'
        parent.rename(outside)
        parent.symlink_to(outside, target_is_directory=True)
        self.assert_blocked()

    def test_recheck_blocks_new_conflict_before_any_copy(self):
        self.assert_blocked('collision_check; touch "$TARGET_ROOT/' + self.base + '/new-conflict"; copy_stage')

    def test_final_verification_failure_preserves_ownership_and_reports_failure(self):
        previous = self.state.read_bytes()
        self.bundle({'keep.so': b'generation two'}, verifier_exit=77)
        result = self.fixture.run_functions('collision_check; copy_stage; note "Installed HoloNight"')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('deployed Images runtime verification failed', result.stderr)
        self.assertNotIn('Installed HoloNight', result.stdout)
        self.assertEqual(self.state.read_bytes(), previous)


if __name__ == '__main__':
    unittest.main()
