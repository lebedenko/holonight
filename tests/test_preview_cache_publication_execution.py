"""Synthetic execution boundary checks; all process creation is forbidden."""
import importlib.util
from pathlib import Path
import sys
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
DIRECTORY = Path(__file__).resolve().parents[1] / 'tooling/preview-cache-publication'
sys.path.insert(0, str(DIRECTORY))
import evidence as e
import run


class ExecutionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.guard = patch('subprocess.Popen', side_effect=AssertionError('process execution forbidden'))
        self.guard.start()
        self.addCleanup(self.guard.stop)

    def events(self):
        identity = dict(invocation='i', service='s', request='r', worker='w', preparation='p',
            transaction='1', source='source', generation='1', width=256, height=256,
            original_decode=True, tier=256, outcome=0)
        return [dict(identity, event=name, ns=str(ns)) for name, ns in
            [('eligible', 1), ('enqueue', 2), ('store_entry', 3), ('accepted', 4),
             ('adequate', 5), ('store_return', 6), ('final', 7)]]

    def parse(self, rows):
        return e.parse_events('\n'.join('CACHE_PUBLICATION ' + e.h.json.dumps(r) for r in rows))

    def test_decimal_nanoseconds_remain_exact(self):
        rows = self.events()
        for row in rows:
            row['ns'] = str(int(row['ns']) + 10**19)
        self.assertEqual(self.parse(rows)[0]['ns'], 10**19 + 1)

    def test_duplicate_event_rejected(self):
        rows = self.events()
        with self.assertRaises(ValueError):
            self.parse(rows + [rows[0]])

    def test_cross_transaction_join_rejected(self):
        rows = self.events()
        rows[-1]['transaction'] = '2'
        with self.assertRaises(ValueError):
            self.parse(rows)

    def test_boundary_equality_is_not_support(self):
        for boundary in ('store_entry', 'store_return'):
            rows = self.events()
            stamp = next(r['ns'] for r in rows if r['event'] == boundary)
            for row in rows:
                if row['event'] in ('accepted', 'adequate'):
                    row['ns'] = stamp
            self.assertFalse(e.historical.observation(self.parse(rows)))

    def test_non_decimal_and_numeric_timestamps_rejected(self):
        for stamp in (1, '1.0', '-1', '١', ''):
            rows = self.events()
            rows[0]['ns'] = stamp
            with self.assertRaises(ValueError):
                self.parse(rows)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate event field'):
            e.parse_events('CACHE_PUBLICATION {"ns":"1","ns":"2"}')

    def test_incomplete_schedule_cannot_claim_overlap(self):
        self.assertEqual(e.historical.outcome([]), 'Evidence insufficient')

    def test_command_passes_and_records_invocation_and_private_directories(self):
        environment = dict(HOLONIGHT_CACHE_INVOCATION='unique-id', TMPDIR='/private/source',
                           XDG_CACHE_HOME='/private/cache')
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, environment):
            def completed(argv, **kwargs):
                for key, value in environment.items():
                    self.assertEqual(kwargs['env'][key], value)
                return subprocess.CompletedProcess(argv, 0)
            with patch.object(subprocess, 'run', side_effect=completed):
                run.command(['synthetic-command'], Path(directory), 'native')
            record = e.h.read(Path(directory) / 'native-command.json')
            for key, value in environment.items():
                self.assertEqual(record['environment'][key], value)

    def test_output_collision_is_rejected_without_modification(self):
        with tempfile.TemporaryDirectory(dir=e.ROOT / 'build') as directory:
            output = Path(directory)
            sentinel = output / 'retained'
            sentinel.write_text('preserve')
            with self.assertRaisesRegex(ValueError, 'collision'):
                e.h.fresh(output, [])
            self.assertEqual(sentinel.read_text(), 'preserve')

    def test_output_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=e.ROOT / 'build') as directory:
            output = Path(directory) / 'escape'
            output.symlink_to('/tmp', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'destination must be'):
                e.h.fresh(output / 'child', [])


if __name__ == '__main__':
    unittest.main()
