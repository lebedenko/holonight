# SPDX-License-Identifier: GPL-3.0-or-later
"""Deployment identity regressions with disposable files and mocked systemd."""
import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from install_state import inventory
SPEC = importlib.util.spec_from_file_location('verified_installer', SCRIPTS / 'source-install.py')
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class Verification(unittest.TestCase):
    def test_replaced_file_is_detected_even_after_actions_completed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / 'usr/libexec/holonight-package-helper'
            executable.parent.mkdir(parents=True)
            executable.write_text('new helper')
            transaction = {'removing': False, 'selection': ['holonight-pkg-manager'],
                           'manifest': inventory(root, 'holonight-pkg-manager', 'revision')}
            with redirect_stdout(io.StringIO()) as report:
                installer.verify_deployment(root, transaction)
            self.assertIn('Verified installed holonight-pkg-manager: revision', report.getvalue())
            executable.write_text('stale helper')
            with self.assertRaisesRegex(ValueError, 'deployment verification failed'):
                installer.verify_deployment(root, transaction)

    def test_wrong_activation_path_is_rejected(self):
        with patch.object(installer, 'output', return_value='{ path=/usr/local/bin/old-helper ; }'):
            with self.assertRaisesRegex(ValueError, 'does not activate'):
                installer.report_package_helper(Path('/'), ['holonight-pkg-manager'], False)

    def test_inactive_service_is_not_started(self):
        with patch.object(installer, 'output', side_effect=[
                '{ path=/usr/libexec/holonight-package-helper ; }', '0']) as command:
            with redirect_stdout(io.StringIO()) as report:
                installer.report_package_helper(Path('/'), ['holonight-pkg-manager'], False)
            self.assertIn('Verified activation', report.getvalue())
            self.assertTrue(all(call.args[1] == 'show' for call in command.call_args_list))

    def test_old_running_inode_is_reported_without_restart(self):
        from types import SimpleNamespace
        with patch.object(installer, 'output', side_effect=[
                '{ path=/usr/libexec/holonight-package-helper ; }', '123']), \
                patch.object(Path, 'stat', side_effect=[
                    SimpleNamespace(st_dev=1, st_ino=1), SimpleNamespace(st_dev=1, st_ino=2)]):
            with redirect_stdout(io.StringIO()) as report:
                installer.report_package_helper(Path('/'), ['holonight-pkg-manager'], False)
            self.assertIn('previous executable', report.getvalue())

    def test_staged_root_never_queries_host_systemd(self):
        with patch.object(installer, 'output') as command:
            installer.report_package_helper(Path('/fixture'), ['holonight-pkg-manager'], False)
            command.assert_not_called()


if __name__ == '__main__':
    unittest.main()
