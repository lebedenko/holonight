"""Independent blocked-record acceptance tests, with subprocess execution forbidden."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
DIRECTORY = Path(__file__).resolve().parents[1] / 'tooling/preview-cache-publication'
sys.path.insert(0, str(DIRECTORY))
import evidence as e
spec = importlib.util.spec_from_file_location('publication_offline_execution', DIRECTORY / 'offline/verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class BlockedVerificationTests(unittest.TestCase):
    def setUp(self):
        self.guard = patch.object(subprocess, 'Popen', side_effect=AssertionError('process execution forbidden'))
        self.guard.start()
        self.addCleanup(self.guard.stop)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name) / 'record'
        self.root.mkdir()
        self.binding = dict(path=str(e.PACKAGE), seal=e.SEAL, independent_sha256='synthetic')
        binding = patch.object(e, 'package', return_value=self.binding)
        binding.start()
        self.addCleanup(binding.stop)
        (self.root / 'tools').mkdir()
        tools = e.tools()
        for path in tools:
            shutil.copyfile(path, self.root / 'tools' / Path(path).name)
        for name, value in [('tools', tools), ('package', self.binding),
                ('protocol', e.historical.protocol()), ('integrity', dict(unchanged=True)),
                ('assessment', dict(status='blocked', decision='Evidence insufficient', attempted=0,
                    unexecuted=e.historical.protocol()['schedule'], staging='not attempted',
                    native_correctness='unvalidated', failure='missing compiler'))]:
            e.h.write(self.root / (name + '.json'), value)
        e.h.write(self.root / 'compiler-command.json', dict(argv=['c++', '--version'],
            cwd=str(e.ROOT), timeout_seconds=600, environment=dict(QT_QPA_PLATFORM='offscreen',
                CMAKE_BUILD_PARALLEL_LEVEL='4')))
        e.h.write(self.root / 'compiler-result.json', dict(start_ns=1, stop_ns=2,
            exit=127, failure='missing compiler'))
        (self.root / 'compiler.stdout').write_text('')
        (self.root / 'compiler.stderr').write_text('compiler unavailable\n')
        self.seal()

    def seal(self):
        inventory = e.h.inventory(self.root)
        inventory.pop('seal.json', None)
        e.h.write(self.root / 'seal.json', inventory)

    def test_blocked_record_remains_insufficient(self):
        result = v.verify(self.root)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['decision'], 'Evidence insufficient')
        self.assertEqual(result['observations'], 0)

    def test_resealed_unexpected_member_is_rejected(self):
        (self.root / 'unexpected').write_text('extra')
        self.seal()
        with self.assertRaisesRegex(ValueError, 'artifact membership'):
            v.verify(self.root)

    def test_raw_log_drift_is_rejected(self):
        (self.root / 'compiler.stderr').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'seal/inventory'):
            v.verify(self.root)

    def test_resealed_wrong_command_is_rejected(self):
        path = self.root / 'compiler-command.json'
        value = e.h.read(path)
        value['argv'] = ['true']
        e.h.write(path, value)
        self.seal()
        with self.assertRaisesRegex(ValueError, 'identity command'):
            v.verify(self.root)

    def test_skipped_prerequisites_cannot_be_claimed_passing(self):
        path = self.root / 'assessment.json'
        value = e.h.read(path)
        value['native_correctness'] = 'passed'
        e.h.write(path, value)
        self.seal()
        with self.assertRaisesRegex(ValueError, 'prerequisite accounting'):
            v.verify(self.root)

    def test_incomplete_unexecuted_schedule_is_rejected(self):
        path = self.root / 'assessment.json'
        value = e.h.read(path)
        value['unexecuted'].pop()
        e.h.write(path, value)
        self.seal()
        with self.assertRaisesRegex(ValueError, 'schedule'):
            v.verify(self.root)

    def test_missing_result_is_rejected_even_after_resealing(self):
        (self.root / 'compiler-result.json').unlink()
        self.seal()
        with self.assertRaisesRegex(ValueError, 'unpaired process'):
            v.verify(self.root)


if __name__ == '__main__':
    unittest.main()
