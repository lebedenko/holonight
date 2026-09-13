"""Evidence indexing and runtime attribution regressions; no live authentication."""
import sys
sys.dont_write_bytecode = True

import importlib.util
import json
import os
import signal
import subprocess
import time
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

DOCS = Path(__file__).resolve().parents[1] / 'docs/initiatives/unified-qtquick-controls'


def load_helper():
    modules = {}
    for name, functions in {'session_identity': ('identity', 'output'),
                            'registration': ('registration_reply',),
                            'bounded_challenge': ('run_challenge',)}.items():
        module = types.ModuleType(name)
        for function in functions:
            setattr(module, function, lambda *args: None)
        modules[name] = module
    spec = importlib.util.spec_from_file_location('authentication_test', DOCS / 'authentication-test.py')
    helper = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(helper)
    return helper


helper = load_helper()


class AuthenticationEvidence(unittest.TestCase):
    def test_index_selects_latest_matching_run_in_current_session_and_kit(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            first, _ = helper.new_run(base, '42', 'polkit', 'Holonight', '1.25')
            second, _ = helper.new_run(base, '42', 'polkit', 'Fusion', '1.25')
            third, _ = helper.new_run(base, '42', 'polkit', 'Holonight', '1.25')
            helper.new_run(base, '43', 'polkit', 'Holonight', '1.25')
            for run in (first, second, third):
                (run / 'session-id').write_text('42')
            self.assertEqual(helper.latest_run(base, '42', 'Holonight', '1.25'), third)
            self.assertEqual(helper.latest_run(base, '42', 'Fusion', '1.25'), second)
            self.assertEqual(len((base / 'session-42.jsonl').read_text().splitlines()), 3)
            with patch.object(helper, 'KIT', Path('/tmp/different-kit')):
                with self.assertRaisesRegex(SystemExit, 'start the matching'):
                    helper.latest_run(base, '42', 'Holonight', '1.25')
            (third / 'session-id').write_text('99')
            with self.assertRaisesRegex(SystemExit, 'session mismatch'):
                helper.latest_run(base, '42', 'Holonight', '1.25')

    def test_runtime_requires_actual_style_scale_and_all_staged_modules(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            metadata = dict(pid=123, style='Fusion', scale='1.25')
            paths = [str(helper.KIT / 'prefix/lib' / name) for name in
                     ('libholonight_config.so', 'libholonight_core_qml.so', 'libholonight_controls_qml.so')]
            paths.append('/usr/lib/libqtquickcontrols2fusionstyleplugin.so')
            valid = ('phase=selection configured= "Fusion"\nphase=window devicePixelRatio= 1.25\n' +
                     '\n'.join('123: calling init: ' + path for path in paths))
            for text, expected in ((valid, True),
                                   (valid.replace('1.25', '1'), False),
                                   (valid.replace('"Fusion"', '"Holonight"'), False),
                                   (valid.replace(paths[0], '/usr/lib/libholonight_config.so'), False),
                                   (valid.replace(paths[1], '/usr/lib/unrelated.so'), False)):
                (run / 'process.log').write_text(text)
                helper.runtime_evidence(run, metadata)
                self.assertEqual(json.loads((run / 'runtime.json').read_text())['verified'], expected)

    def test_missing_ready_and_modified_packages_are_refused(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(helper, 'KIT', Path(directory)):
            with self.assertRaisesRegex(SystemExit, 'not READY'):
                helper.compatible()
            (helper.KIT / 'READY').write_text('ready')
            (helper.KIT / 'PROVIDER.txt').write_text('qt6-base original-version\n')
            with patch.object(helper, 'output', return_value='qt6-base changed-version'):
                with self.assertRaisesRegex(SystemExit, 'package changed'):
                    helper.compatible()

    def test_modified_kit_file_is_refused(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(helper, 'KIT', Path(directory)):
            (helper.KIT / 'READY').write_text('ready')
            (helper.KIT / 'PROVIDER.txt').write_text('fixture-version\n')
            (helper.KIT / 'payload').write_text('modified')
            (helper.KIT / 'SHA256SUMS').write_text('0' * 64 + '  payload\n')
            with patch.object(helper, 'output', return_value='fixture-version'):
                with self.assertRaisesRegex(SystemExit, 'checksum mismatch'):
                    helper.compatible()


class AuthenticationSupervisor(unittest.TestCase):
    def test_interrupt_records_agent_exit_and_preserves_stdout_diagnostics(self):
        with tempfile.TemporaryDirectory(prefix='uqc-auth-supervisor-') as directory:
            kit = Path(directory)
            (kit / 'prefix/libexec').mkdir(parents=True)
            executable = kit / 'prefix/libexec/holonight-polkit-agent'
            executable.write_text('#!/usr/bin/python3\nimport signal, sys, time\n'
                                  'signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))\n'
                                  'print("synthetic-agent-stdout", flush=True)\n'
                                  'while True: time.sleep(0.05)\n')
            executable.chmod(0o755)
            run = kit / 'evidence'
            run.mkdir()
            driver = kit / 'driver.py'
            driver.write_text(
                'import sys\nfrom pathlib import Path\n'
                'sys.path.insert(0, ' + repr(str(Path(__file__).resolve().parent)) + ')\n'
                'from test_authentication_kit import load_helper\n'
                'helper = load_helper()\n'
                'helper.KIT = Path(' + repr(str(kit)) + ')\n'
                'helper.verify_registration = lambda *args: None\n'
                'metadata = dict(kind="polkit", session="fixture", style="Holonight", scale="1.25")\n'
                'helper.launch(Path(' + repr(str(run)) + '), metadata, {})\n')
            with (kit / 'driver.log').open('w') as log:
                process = subprocess.Popen([sys.executable, str(driver)], stdout=log, stderr=log,
                                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
                try:
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        path = run / 'process.log'
                        if path.exists() and 'synthetic-agent-stdout' in path.read_text():
                            break
                        self.assertIsNone(process.poll())
                        time.sleep(0.01)
                    else:
                        self.fail('synthetic agent did not start')
                    process.send_signal(signal.SIGINT)
                    self.assertEqual(process.wait(timeout=7), 0)
                    metadata = json.loads((run / 'process.json').read_text())
                    self.assertEqual(metadata['outcome'], 'interrupted')
                    self.assertEqual(metadata['cleanup'], 'terminated')
                    self.assertEqual(metadata['exit_status'], 0)
                    self.assertTrue((run / 'runtime.json').is_file())
                    self.assertIn('synthetic-agent-stdout', (run / 'process.log').read_text())
                finally:
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()
