# SPDX-License-Identifier: GPL-3.0-or-later
"""Acceptance must include current source edits and stop on failed quality gates."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('container_launcher', ROOT / 'scripts/ci/container.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class Acceptance(unittest.TestCase):
    def test_snapshot_includes_edits_and_new_files_but_excludes_builds_and_deleted_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / 'source', Path(tmp) / 'snapshot'
            source.mkdir()
            subprocess.run(['git', 'init', '-q', str(source)], check=True)
            (source / '.gitignore').write_text('build/\ntracked-ignored.cpp\n')
            (source / 'tracked.cpp').write_text('before')
            (source / 'deleted.cpp').write_text('removed')
            (source / 'tracked-ignored.cpp').write_text('tracked despite ignore rule')
            subprocess.run(['git', '-C', str(source), 'add', '--force', 'tracked-ignored.cpp'], check=True)
            subprocess.run(['git', '-C', str(source), 'add', '.'], check=True)
            (source / 'tracked.cpp').write_text('after')
            (source / 'new.cpp').write_text('new')
            (source / 'deleted.cpp').unlink()
            (source / 'build').mkdir()
            (source / 'build/host-binary').write_text('must not be copied')
            launcher.snapshot(source, target)
            self.assertEqual((target / 'tracked.cpp').read_text(), 'after')
            self.assertEqual((target / 'new.cpp').read_text(), 'new')
            self.assertFalse((target / 'deleted.cpp').exists())
            self.assertFalse((target / 'build').exists())
            self.assertTrue((target / '.git').is_dir())
            inventory = subprocess.check_output(['git', '-C', str(target), 'ls-files'], text=True)
            self.assertIn('tracked-ignored.cpp', inventory.splitlines())

    def test_pinned_umbrella_snapshot_excludes_unpublished_provider_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'umbrella'
            child = source / 'provider'
            child.mkdir(parents=True)
            def git(repository, *args):
                subprocess.run(['git', '-C', str(repository), '-c', 'user.name=Fixture',
                                '-c', 'user.email=fixture@example.invalid', *args],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            git(child, 'init', '-q')
            (child / 'api.txt').write_text('published')
            git(child, 'add', '.')
            git(child, 'commit', '-qm', 'fixture')
            git(source, 'init', '-q')
            (source / '.gitmodules').write_text('[submodule "provider"]\npath = provider\nurl = unused\n')
            git(source, 'add', '.')
            git(source, 'commit', '-qm', 'pin provider')
            (child / 'api.txt').write_text('unpublished edit')
            (child / 'new.txt').write_text('new source')
            pinned, current = Path(tmp) / 'pinned', Path(tmp) / 'current'
            launcher.snapshot(source, pinned, pinned_submodules=True)
            launcher.snapshot(source, current)
            self.assertEqual((pinned / 'provider/api.txt').read_text(), 'published')
            self.assertFalse((pinned / 'provider/new.txt').exists())
            self.assertEqual((current / 'provider/api.txt').read_text(), 'unpublished edit')
            self.assertTrue((current / 'provider/new.txt').exists())

    def test_failed_test_format_tidy_or_license_stops_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('task', 'reuse'):
                command = root / name
                command.write_text('#!/bin/sh\nprintf "%s\\n" "$1" >> "$LOG"\n'
                                   '[ "$1" != "$FAIL" ] || exit 37\n')
                command.chmod(0o755)
            log = root / 'calls'
            stages = ['test', 'format-check', 'tidy', 'lint']
            for stage in stages:
                with self.subTest(stage=stage):
                    log.unlink(missing_ok=True)
                    result = subprocess.run(['bash', str(ROOT / 'holonight-config/scripts/ci/check.sh')],
                                            env=dict(os.environ, PATH=f'{root}:/usr/bin', FAIL=stage, LOG=str(log)))
                    self.assertEqual(result.returncode, 37)
                    self.assertEqual(log.read_text().splitlines(), stages[:stages.index(stage) + 1])

    def test_standalone_repositories_use_the_same_immutable_image(self):
        expected = (ROOT / 'scripts/ci/image.txt').read_text().strip()
        self.assertRegex(expected, r'@sha256:[0-9a-f]{64}$')
        # Only declared components belong to umbrella acceptance. Other local
        # checkouts may have a Taskfile without adopting this CI environment.
        declared = subprocess.check_output(
            ['git', 'config', '--file', str(ROOT / '.gitmodules'),
             '--get-regexp', r'^submodule\..*\.path$'], text=True)
        repositories = [line.split(None, 1)[1] for line in declared.splitlines()]
        self.assertTrue(repositories)
        for repository in repositories:
            with self.subTest(repository=repository):
                self.assertEqual((ROOT / repository / 'scripts/ci/image.txt').read_text().strip(), expected)


if __name__ == '__main__':
    unittest.main()
