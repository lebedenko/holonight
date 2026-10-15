# SPDX-License-Identifier: GPL-3.0-or-later
"""Native tests isolate host services while preserving writable build trees."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ecosystem', ROOT / 'scripts/build-ecosystem.py')
ecosystem = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ecosystem)


@unittest.skipUnless(all(shutil.which(tool) for tool in ('dbus-run-session', 'dbus-send', 'ctest')),
                     'private bus tools unavailable')
class BusIsolation(unittest.TestCase):
    def test_integration_bus_excludes_host_service_activation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            services = root / 'data/dbus-1/services'
            services.mkdir(parents=True)
            name = 'org.holonight.TestActivation'
            (services / f'{name}.service').write_text(
                f'[D-BUS Service]\nName={name}\nExec=/usr/bin/false\n')
            env = dict(os.environ, XDG_DATA_HOME=str(root / 'data'),
                       DBUS_SESSION_BUS_ADDRESS=f'unix:path={root}/nonexistent-parent-bus')
            query = ['dbus-send', '--session', '--print-reply', '--dest=org.freedesktop.DBus',
                     '/org/freedesktop/DBus', 'org.freedesktop.DBus.ListActivatableNames']
            ordinary = subprocess.check_output(['dbus-run-session', '--', *query], env=env, text=True)
            self.assertIn(name, ordinary, 'fixture must be visible to ordinary session activation')
            probe = root / 'probe.py'
            probe.write_text('import subprocess\n'
                             f'names = subprocess.check_output({query!r}, text=True)\n'
                             f'assert {name!r} not in names, names\n')
            (root / 'CTestTestfile.cmake').write_text(
                f'add_test(no-host-activation "/usr/bin/python3" "{probe}")\n')
            ecosystem.run_tests(root / 'holonight-ai', root, env)


@unittest.skipIf(os.environ.get('UQC_ISOLATED') == '1', 'requires native host isolation')
@unittest.skipUnless(all(shutil.which(tool) for tool in ('bwrap', 'ctest', 'dbus-daemon')),
                     'native isolation tools unavailable')
class NativeIsolation(unittest.TestCase):
    def test_external_ctest_build_is_writable_but_sibling_prefix_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            umbrella = Path(tmp) / 'umbrella'
            scripts = umbrella / 'shell/scripts'
            scripts.mkdir(parents=True)
            runner = scripts / 'run-isolated-test.py'
            shutil.copy2(ROOT / 'holonight-shell/scripts/run-isolated-test.py', runner)
            build = umbrella / 'build/integration/shell build'
            build.mkdir(parents=True)
            prefix = umbrella / 'build/integration/prefix'
            prefix.mkdir()
            sentinel = prefix / 'installed-file'
            sentinel.write_text('preserved')
            probe = build / 'probe.py'
            probe.write_text('import errno\nfrom pathlib import Path\n'
                             f'Path({str(build / "test-result")!r}).write_text("passed")\n'
                             'try:\n'
                             f'    Path({str(sentinel)!r}).write_text("changed")\n'
                             'except OSError as error:\n'
                             '    assert error.errno == errno.EROFS, error\n'
                             'else:\n'
                             '    raise AssertionError("sibling prefix was writable")\n')
            # CTest discovery, like GoogleTest PRE_TEST discovery, writes before running tests.
            (build / 'CTestTestfile.cmake').write_text(
                f'file(WRITE "{build}/discovery.json" "{{}}")\n'
                f'add_test(write-results "/usr/bin/python3" "{probe}")\n')
            result = subprocess.run(['python3', str(runner), '--hide-host', '--build-dir', str(build),
                                     'ctest', '--test-dir', str(build), '--output-on-failure',
                                     '--no-tests=error'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((build / 'discovery.json').read_text(), '{}')
            self.assertEqual((build / 'test-result').read_text(), 'passed')
            self.assertTrue((build / 'Testing/Temporary/LastTest.log').is_file())
            self.assertEqual(sentinel.read_text(), 'preserved')


if __name__ == '__main__':
    unittest.main()
