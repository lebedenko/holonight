#!/usr/bin/env python3
"""Offline acceptance-runner regressions."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('gate', Path(__file__).with_name('check-isolated-previews.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateTests(unittest.TestCase):
    def test_missing_arguments_rejected(self):
        result = subprocess.run([sys.executable, str(Path(gate.__file__))], capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_failed_and_timed_out_commands_retain_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            with self.assertRaises(RuntimeError):
                gate.run([sys.executable, '-c', 'raise SystemExit(9)'], {}, output, 'failed')
            self.assertEqual(json.loads((output / 'failed.json').read_text())['returncode'], 9)
            with patch.object(gate.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['probe'], 1)):
                with self.assertRaises(subprocess.TimeoutExpired):
                    gate.run(['probe'], {}, output, 'timeout', 1)
            self.assertIn('error', json.loads((output / 'timeout.json').read_text()))
            self.assertFalse((output / 'complete.json').exists())

    def test_user_manager_failure_stops_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix = root / 'prefix'
            runtime = prefix / 'runtime'
            runtime.mkdir(parents=True)
            (runtime / 'manifest.json').write_text('{}')
            test_runtime = root / 'test-runtime'
            test_runtime.mkdir()
            (test_runtime / 'manifest.json').write_text('{}')
            package = prefix / 'lib/cmake/HolonightFileBrowser/HolonightFileBrowserConfig.cmake'
            package.parent.mkdir(parents=True)
            package.touch()
            (root / 'sample.png').touch()
            executable = root / 'executable'
            executable.touch()
            args = ['gate']
            for name, value in dict(prefix=prefix, runtime=runtime, test_runtime=test_runtime, files=executable,
                                    files_tests=executable, unknown_tests=executable, portal=executable,
                                    provider=executable, fixtures=root, output=root / 'evidence').items():
                args += ['--' + name.replace('_', '-'), str(value)]
            with patch.object(sys, 'argv', args), patch.object(gate, 'run', side_effect=RuntimeError('no manager')) as run:
                with self.assertRaisesRegex(RuntimeError, 'no manager'):
                    gate.main()
            self.assertEqual(run.call_count, 1)
            self.assertTrue(prefix.exists())
            self.assertFalse((root / 'evidence/complete.json').exists())

    def test_relocation_failure_restores_original_prefix(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix = root / 'prefix'
            runtime = prefix / 'runtime'
            runtime.mkdir(parents=True)
            (runtime / 'manifest.json').write_text('{}')
            test_runtime = root / 'test-runtime'
            test_runtime.mkdir()
            (test_runtime / 'manifest.json').write_text('{}')
            package = prefix / 'lib/cmake/HolonightFileBrowser/HolonightFileBrowserConfig.cmake'
            package.parent.mkdir(parents=True)
            package.touch()
            (root / 'sample.png').touch()
            executable = root / 'executable'
            executable.touch()
            args = ['gate']
            for name, value in dict(prefix=prefix, runtime=runtime, test_runtime=test_runtime, files=executable,
                                    files_tests=executable, unknown_tests=executable, portal=executable,
                                    provider=executable, fixtures=root, output=root / 'evidence').items():
                args += ['--' + name.replace('_', '-'), str(value)]

            def fail_relocated(command, env, output, name, timeout=600):
                if name == 'relocated-provider':
                    self.assertFalse(prefix.exists())
                    self.assertTrue((root / 'evidence/relocated-prefix/runtime/manifest.json').exists())
                    raise RuntimeError('relocation failure')

            with patch.object(sys, 'argv', args), patch.object(gate, 'run', side_effect=fail_relocated):
                with self.assertRaisesRegex(RuntimeError, 'relocation failure'):
                    gate.main()
            self.assertTrue((runtime / 'manifest.json').is_file())
            self.assertFalse(prefix.with_name('prefix.acceptance-hidden').exists())
            self.assertFalse((root / 'evidence/complete.json').exists())


if __name__ == '__main__':
    unittest.main()
