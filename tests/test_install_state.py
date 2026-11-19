"""Deployment and retry contracts in disposable roots; no host mutation."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from install_catalog import select
from install_state import RUNTIME, STATE, inventory, manifest_text, parse_manifest, read_manifest, snapshot

SPEC = importlib.util.spec_from_file_location('installer', SCRIPTS / 'source-install.py')
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class Deployment(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'target'
        self.state = self.root / STATE
        self.state.mkdir(parents=True)
        self.payload = Path(self.temporary.name) / 'prepared'
        path = self.payload / 'holonight-viewer/usr/bin/hn-viewer'
        path.parent.mkdir(parents=True)
        path.write_text('new viewer')
        self.incoming = inventory(self.payload / 'holonight-viewer', 'holonight-viewer', '1' * 40)

    def transaction(self):
        return installer.new_transaction(self.root, self.state, ['holonight-viewer'], self.incoming,
                                         False, False, self.payload)

    def execute(self, transaction):
        # Package database identity is an external boundary; fixture contains inert bytes.
        with patch.object(installer, 'validate_prepared'):
            (self.payload / 'prepared.json').write_text('{}')
            installer.execute(self.root, self.state, transaction)

    def modified_payload(self, name='/usr/bin/hn-viewer', owner='holonight-viewer',
                         old_mode=0o755, staged_mode=0o751):
        staged = self.payload / 'holonight-viewer' / name.lstrip('/')
        staged.parent.mkdir(parents=True, exist_ok=True)
        live = self.root / name.lstrip('/')
        live.parent.mkdir(parents=True, exist_ok=True)
        live.write_text('previous executable')
        live.chmod(old_mode)
        (self.state / 'manifest.tsv').write_text(
            manifest_text({name: [owner, '0' * 40, *snapshot(live), name]}))
        live.write_text('local executable')
        live.chmod(0o644)
        staged.write_text('staged executable')
        staged.chmod(staged_mode)
        self.incoming = inventory(self.payload / 'holonight-viewer', 'holonight-viewer', '1' * 40)
        return live

    def saved_record(self, owner, rows):
        record = {'root': str(self.root), 'selection': [owner], 'host': hashlib.sha256(b'').hexdigest(),
                  'components': {owner: {'revision': '1' * 40, 'inventory': rows, 'dirty': False}},
                  'adopt': False, 'protected_images': False, 'maintenance': False}
        (self.payload / 'prepared.json').write_text(json.dumps(record))
        return record

    def test_repairs_modified_executable_without_live_execute_bits(self):
        live = self.modified_payload()
        previous = snapshot(live)
        with patch.object(installer, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')) as run:
            transaction = self.transaction()
            run.assert_called_once()
            self.assertEqual(run.call_args.args, ('pacman', '--root', self.root, '-Qql'))
        action = next(action for action in transaction['actions'] if action['path'] == '/usr/bin/hn-viewer')
        self.assertTrue(action['executable_repair'])
        self.assertEqual(action['previous'], previous)
        self.execute(transaction)
        self.assertEqual(live.read_text(), 'staged executable')
        self.assertEqual(live.stat().st_mode & 0o777, 0o751)
        self.assertEqual(read_manifest(self.state / 'manifest.tsv'), self.incoming)
        self.assertEqual(list(self.state.glob('adoption-backup-*')), [])

    def test_executable_repair_requires_readable_unclaimed_inventory(self):
        live = self.modified_payload()
        cases = (
            (subprocess.CompletedProcess([], 0, f'{live}\n', ''), 'package-owned collision'),
            (subprocess.CompletedProcess([], 0, '', 'error: could not open package files'), 'cannot read pacman'),
            (subprocess.CalledProcessError(1, ['pacman'], stderr='database unavailable'), 'cannot read pacman'),
        )
        for result, message in cases:
            with self.subTest(message=message), patch.object(installer, 'run') as run:
                if isinstance(result, Exception):
                    run.side_effect = result
                else:
                    run.return_value = result
                with self.assertRaisesRegex(ValueError, message):
                    self.transaction()
                run.assert_called_once()
                self.assertFalse((self.state / 'transaction.json').exists())
                self.assertEqual(live.read_text(), 'local executable')

    def test_ineligible_modified_paths_keep_collision_protection(self):
        cases = (
            ('/usr/bin/hn-viewer', 'holonight-files', 0o755, 0o751),
            ('/usr/bin/hn-viewer', 'holonight-viewer', 0o644, 0o751),
            ('/usr/bin/hn-viewer', 'holonight-viewer', 0o755, 0o644),
            ('/usr/lib/hn-viewer.so', 'holonight-viewer', 0o755, 0o751),
            (RUNTIME + '/usr/bin/hn-viewer', 'holonight-viewer', 0o755, 0o751),
        )
        for name, owner, old_mode, staged_mode in cases:
            with self.subTest(name=name, owner=owner, modes=(old_mode, staged_mode)):
                live = self.modified_payload(name, owner, old_mode, staged_mode)
                with patch.object(installer, 'run') as run, self.assertRaisesRegex(ValueError, 'modified|unselected'):
                    installer.new_transaction(self.root, self.state, ['holonight-viewer', owner],
                                              {name: self.incoming[name]}, False, False, self.payload)
                run.assert_not_called()
                self.assertEqual(live.read_text(), 'local executable')

    def test_modified_executable_symlink_and_unsafe_ancestor_are_rejected(self):
        live = self.modified_payload()
        live.unlink()
        outside = Path(self.temporary.name) / 'outside'
        outside.mkdir()
        external = outside / live.name
        external.write_text('external executable')
        live.symlink_to(external)
        with self.assertRaisesRegex(ValueError, 'preserve modified path'):
            self.transaction()
        live.unlink()
        live.parent.rmdir()
        live.parent.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'unsafe installation parent|occupied'):
            self.transaction()
        self.assertEqual(external.read_text(), 'external executable')

    def test_obsolete_cleanup_and_uninstall_preserve_modified_executable(self):
        live = self.modified_payload()
        old = read_manifest(self.state / 'manifest.tsv')
        upgrade = installer.new_transaction(self.root, self.state, ['holonight-viewer'], {}, False, False)
        self.assertEqual(upgrade['actions'], [])
        self.assertEqual(upgrade['manifest'], old)
        removal = installer.new_transaction(self.root, self.state, ['holonight-viewer'], {}, True, False)
        self.execute(removal)
        self.assertEqual(live.read_text(), 'local executable')
        self.assertEqual(read_manifest(self.state / 'manifest.tsv'), old)

    def test_repair_resume_rechecks_ownership_preserves_edits_and_does_not_recopy(self):
        live = self.modified_payload()
        record = self.saved_record('holonight-viewer', self.incoming)
        args = argparse.Namespace(root=self.root, prepared=self.payload)
        save = installer.save_transaction

        def interrupt(state, transaction):
            if live.read_text() == 'staged executable':
                raise InterruptedError('after atomic replacement')
            save(state, transaction)

        with patch.object(installer, 'host_identity', return_value=record['host']), \
                patch.object(installer, 'run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, '', '')
            with patch.object(installer, 'save_transaction', side_effect=interrupt), \
                    self.assertRaises(InterruptedError):
                installer.deploy(args)
            run.assert_called_once()
            timestamp = live.stat().st_mtime_ns
            run.return_value.stdout = str(live) + '\n'
            with self.assertRaisesRegex(ValueError, 'package-owned collision'):
                installer.deploy(args)
            self.assertEqual(live.stat().st_mtime_ns, timestamp)
            run.return_value.stdout = ''
            live.write_text('further local edit')
            with self.assertRaisesRegex(ValueError, 'transaction conflict'):
                installer.deploy(args)
            self.assertEqual(live.read_text(), 'further local edit')
            live.write_text('staged executable')
            inode = live.stat().st_ino
            with patch.object(installer, 'atomic', wraps=installer.atomic) as atomic:
                installer.deploy(args)
            self.assertFalse(any(call.args[0] == live for call in atomic.call_args_list))
            self.assertEqual(live.stat().st_ino, inode)
            self.assertEqual(run.call_count, 4)
        self.assertIsNone(installer.pending(self.state))

    def test_public_installer_deploys_saved_package_helper_repair(self):
        owner = 'holonight-pkg-manager'
        name = '/usr/libexec/holonight-package-helper'
        live = self.modified_payload(name, owner)
        (self.payload / 'holonight-viewer/usr/bin/hn-viewer').unlink()
        (self.payload / 'holonight-viewer/usr/bin').rmdir()
        (self.payload / 'holonight-viewer').rename(self.payload / owner)
        rows = inventory(self.payload / owner, owner, '1' * 40)
        self.saved_record(owner, rows)
        fixture = Path(self.temporary.name)
        scripts = fixture / 'scripts'
        scripts.mkdir()
        for filename in ('install.sh', 'source-install.py', 'install_state.py', 'install_catalog.py'):
            shutil.copy2(SCRIPTS / filename, scripts)
        work = fixture / '.source-install'
        work.mkdir()
        (work / 'prepared.path').write_text(str(self.payload))
        pacman = fixture / 'pacman'
        pacman.write_text('#!/bin/sh\ncase "$*" in\n'
                          '  "-Q"|"--root $TARGET -Qql") exit 0;;\n'
                          '  *) exit 1;;\nesac\n')
        pacman.chmod(0o755)
        result = subprocess.run([scripts / 'install.sh', '--resume', '--yes', '--root', self.root],
                                env={**os.environ, 'PATH': f'{fixture}:{os.environ["PATH"]}', 'TARGET': str(self.root)},
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'Replaced modified executable: {live}', result.stdout)
        self.assertIn(f'Verified installed {owner}', result.stdout)
        self.assertEqual(live.read_text(), 'staged executable')
        self.assertEqual(live.stat().st_mode & 0o777, 0o751)
        self.assertEqual(read_manifest(self.state / 'manifest.tsv')[name], rows[name])
        self.assertEqual(list(self.state.glob('adoption-backup-*')), [])

    def test_resume_after_replacement_does_not_recopy_and_preserves_conflict(self):
        transaction = self.transaction()
        original = installer.save_transaction
        def interrupt(state, record):
            if (self.root / 'usr/bin/hn-viewer').exists() and not record.get('published'):
                raise InterruptedError('after payload replacement')
            original(state, record)
        with patch.object(installer, 'save_transaction', side_effect=interrupt):
            with self.assertRaises(InterruptedError):
                self.execute(transaction)
        transaction = installer.pending(self.state)
        binary = self.root / 'usr/bin/hn-viewer'
        timestamp = binary.stat().st_mtime_ns
        self.execute(transaction)
        self.assertEqual(binary.stat().st_mtime_ns, timestamp)
        self.assertEqual(read_manifest(self.state / 'manifest.tsv'), self.incoming)
        transaction['status'] = 'pending'
        binary.write_text('administrator edit')
        with self.assertRaisesRegex(ValueError, 'changed|conflict'):
            self.execute(transaction)
        self.assertEqual(binary.read_text(), 'administrator edit')

    def test_scoped_install_and_repeated_uninstall_preserve_other_ownership(self):
        other = ['holonight-files', '2' * 40, 'f', '644', '0' * 64, '/usr/bin/hn-files']
        (self.state / 'manifest.tsv').write_text(manifest_text({other[5]: other}))
        self.execute(self.transaction())
        self.assertEqual(read_manifest(self.state / 'manifest.tsv')[other[5]], other)
        binary = self.root / 'usr/bin/hn-viewer'
        binary.write_text('local edit')
        for _ in range(2):
            transaction = installer.new_transaction(self.root, self.state, ['holonight-viewer'], {}, True, False)
            installer.execute(self.root, self.state, transaction)
            rows = read_manifest(self.state / 'manifest.tsv')
            self.assertEqual(rows[other[5]], other)
            self.assertEqual(rows['/usr/bin/hn-viewer'], self.incoming['/usr/bin/hn-viewer'])
            self.assertEqual(binary.read_text(), 'local edit')

    def test_malformed_manifest_and_symlink_parent_rejected_before_mutation(self):
        line = 'holonight-viewer\tr\tf\t644\t' + '0' * 64 + '\t'
        for path in ('/usr/../outside', '//usr/bin/a', '/usr/./a', '/var/lib/holonight/source-install/a'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                parse_manifest(line + path + '\n')
        with self.assertRaises(ValueError):
            parse_manifest(manifest_text(self.incoming) * 2)
        outside = Path(self.temporary.name) / 'outside'
        outside.mkdir()
        (self.root / 'usr').symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'parent|occupied'):
            self.transaction()
        self.assertEqual(list(outside.iterdir()), [])

    def test_adoption_backs_up_every_original_before_replacement(self):
        second = self.payload / 'holonight-viewer/usr/bin/second'
        second.write_text('new second')
        incoming = inventory(self.payload / 'holonight-viewer', 'holonight-viewer', '1' * 40)
        for name in ('hn-viewer', 'second'):
            path = self.root / 'usr/bin' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('old ' + name)
        with patch.object(installer, 'package_collision', return_value=False):
            transaction = installer.new_transaction(self.root, self.state, ['holonight-viewer'], incoming,
                                                     False, True, self.payload)
        atomic = installer.atomic
        def fail_backup(path, *args, **kwargs):
            if 'adoption-backup-' in str(path) and path.name == 'second':
                raise OSError('backup failure')
            atomic(path, *args, **kwargs)
        with patch.object(installer, 'atomic', side_effect=fail_backup):
            with self.assertRaisesRegex(OSError, 'backup failure'):
                self.execute(transaction)
        for name in ('hn-viewer', 'second'):
            self.assertEqual((self.root / 'usr/bin' / name).read_text(), 'old ' + name)
        self.execute(transaction)
        backups = list(self.state.glob('adoption-backup-*/usr/bin/*'))
        self.assertEqual({path.name: path.read_text() for path in backups},
                         {'hn-viewer': 'old hn-viewer', 'second': 'old second'})

    def test_resume_after_manifest_publication_skips_completed_payloads(self):
        transaction = self.transaction()
        original = installer.save_transaction
        def interrupt(state, record):
            if record.get('published'):
                raise InterruptedError('after manifest publication')
            original(state, record)
        with patch.object(installer, 'save_transaction', side_effect=interrupt):
            with self.assertRaises(InterruptedError):
                self.execute(transaction)
        published = read_manifest(self.state / 'manifest.tsv')
        self.assertEqual(published, self.incoming)
        binary = self.root / 'usr/bin/hn-viewer'
        timestamp = binary.stat().st_mtime_ns
        self.execute(installer.pending(self.state))
        self.assertEqual(binary.stat().st_mtime_ns, timestamp)
        self.assertIsNone(installer.pending(self.state))

    def test_persistent_directory_lock_excludes_another_process(self):
        from install_state import lock
        child = ('import os,fcntl,sys; fd=os.open(sys.argv[1],os.O_RDONLY|os.O_DIRECTORY); '
                 '\ntry: fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)'
                 '\nexcept BlockingIOError: sys.exit(0)'
                 '\nsys.exit(1)')
        with lock(self.state):
            result = subprocess.run([sys.executable, '-c', child, str(self.state)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_selection_expands_only_installed_dependents_and_removal_checks_edges(self):
        installed = {'holonight-images', 'holonight-thumbnails', 'holonight-file-browser', 'holonight-viewer'}
        self.assertEqual(set(select(['holonight-images'], installed)), installed)
        self.assertEqual(select(['holonight-viewer'], installed), ['holonight-viewer'])
        with self.assertRaisesRegex(ValueError, 'dependents'):
            select(['holonight-images'], installed, removing=True)
        self.assertEqual(set(select(list(installed), installed, removing=True)), installed)


@unittest.skipUnless(installer.shutil.which('cmake') and installer.shutil.which('ninja') and installer.shutil.which('c++'),
                     'native CMake/Ninja toolchain required')
class NativePreparation(unittest.TestCase):
    def test_incremental_build_saved_payload_and_stale_host_rejection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'holonight-viewer'
            source.mkdir()
            (source / 'CMakeLists.txt').write_text(
                'cmake_minimum_required(VERSION 3.20)\nproject(Fixture LANGUAGES CXX)\n'
                'add_executable(fixture main.cpp)\ninstall(TARGETS fixture DESTINATION bin)\n')
            (source / 'main.cpp').write_text('int main(){return 0;}\n')
            for command in (['git', 'init', '-q', source], ['git', '-C', source, 'add', '.'],
                            ['git', '-C', source, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                             'commit', '-qm', 'fixture']):
                subprocess.run(list(map(str, command)), check=True, capture_output=True)
            work = root / '.source-install'
            work.mkdir()
            args = argparse.Namespace(components=['holonight-viewer'], root=root / 'target',
                                      protected_images_runtime=False, adopt_existing=False,
                                      maintenance_migrate_images_runtime=False)
            logs = []
            real_run = installer.run
            def capture(*command, **kwargs):
                result = real_run(*command, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                logs.append(result.stdout)
                return result
            with patch.object(installer, 'ROOT', root), patch.object(installer, 'WORK', work), \
                    patch.object(installer, 'host_identity', return_value='fixture-host'), \
                    patch.object(installer, 'run', side_effect=capture):
                first, first_record = installer.prepare(['holonight-viewer'], args)
                binary = next((work / 'caches').glob('*/build/holonight-viewer/fixture'))
                before = binary.stat().st_mtime_ns
                second, _ = installer.prepare(['holonight-viewer'], args)
                self.assertEqual(binary.stat().st_mtime_ns, before)
                self.assertIn('ninja: no work to do.', '\n'.join(logs))
                self.assertNotEqual(first, second)
                (source / 'main.cpp').write_text('int main(){return 7;}\n')
                installer.validate_prepared(first, first_record)
                third, third_record = installer.prepare(['holonight-viewer'], args)
                self.assertTrue(third_record['components']['holonight-viewer']['dirty'])
                self.assertNotEqual(first_record['components']['holonight-viewer']['identity'],
                                    third_record['components']['holonight-viewer']['identity'])
                self.assertNotEqual((first / 'holonight-viewer/usr/bin/fixture').read_bytes(),
                                    (third / 'holonight-viewer/usr/bin/fixture').read_bytes())
                with patch.object(installer, 'host_identity', return_value='changed-host'):
                    with self.assertRaisesRegex(ValueError, 'prepare again'):
                        installer.validate_prepared(first, first_record)


if __name__ == '__main__':
    unittest.main()
