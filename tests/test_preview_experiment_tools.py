"""Evidence accounting must not hide failed requests or missing observations."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import zlib


ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


measure = module('measure-preview-experiments')
baselines = module('preview-experiment-baselines')


class EvidenceAccounting(unittest.TestCase):
    def test_failed_requests_remain_in_denominator(self):
        records = [dict(success=True, setup_success=True, harness_timeout=False,
                        superseded_selections=20, first_ms=2, final_ms=4, wall_ms=5),
                   dict(success=False, setup_success=False, harness_timeout=True,
                        superseded_selections=20, first_ms=-1, final_ms=-1, wall_ms=10000,
                        error='deadline exceeded')]
        result = measure.summary(records)
        self.assertEqual(result['samples'], 2)
        self.assertEqual(result['failures'], 1)
        self.assertEqual(result['setup_failures'], 1)
        self.assertEqual(result['harness_timeouts'], 1)
        self.assertEqual(result['first_ms']['missing'], 1)
        self.assertEqual(result['final_ms']['observations'], 1)
        self.assertEqual(result['wall_ms']['maximum'], 10000)
        self.assertEqual(result['superseded_selections'], 40)
        self.assertEqual(result['reported_errors'], {'deadline exceeded': 1})

    def test_all_missing_pixels_have_no_latency_statistic(self):
        result = measure.summary([dict(success=False, setup_success=True, harness_timeout=False,
                                       superseded_selections=0, first_ms=-1, final_ms=8, wall_ms=9)])
        self.assertIsNone(result['first_ms']['median'])
        self.assertIsNone(result['first_ms']['p95'])
        self.assertIsNone(result['first_ms']['maximum'])
        self.assertEqual(result['final_ms']['median'], 8)

    def test_idle_pane_completion_without_upgraded_pixels_is_invalid(self):
        result = measure.summary([dict(success=True, setup_success=True, harness_timeout=False,
                                       superseded_selections=0, first_ms=-1, final_ms=.002, wall_ms=.003)])
        self.assertEqual(result['invalid_success_observations'], 1)
        self.assertEqual(result['first_ms']['missing'], 1)
        self.assertIsNone(result['first_ms']['median'])

    def test_p95_uses_nearest_rank_and_preserves_maximum(self):
        records = [dict(success=True, setup_success=True, harness_timeout=False,
                        superseded_selections=0, first_ms=i, final_ms=i, wall_ms=i) for i in range(1, 101)]
        result = measure.summary(records)
        self.assertEqual(result['first_ms']['median'], 50.5)
        self.assertEqual(result['first_ms']['p95'], 95)
        self.assertEqual(result['first_ms']['maximum'], 100)

    def test_inventory_detects_bytes_modes_and_symlink_replacement(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'artifact'
            path.write_bytes(b'one')
            before = baselines.inventory(root)
            path.write_bytes(b'two')
            self.assertNotEqual(before, baselines.inventory(root))
            before = baselines.inventory(root)
            path.chmod(0o700)
            self.assertNotEqual(before, baselines.inventory(root))
            before = baselines.inventory(root)
            path.unlink()
            path.symlink_to('missing')
            self.assertNotEqual(before, baselines.inventory(root))

    def test_fixture_is_valid_deterministic_rgb_png(self):
        data = measure.png(3, 2)
        self.assertEqual(data, measure.png(3, 2))
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        offset = 8
        chunks = {}
        while offset < len(data):
            length = struct.unpack('>I', data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            payload = data[offset + 8:offset + 8 + length]
            crc = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
            self.assertEqual(crc, zlib.crc32(kind + payload))
            chunks[kind] = payload
            offset += 12 + length
        self.assertEqual(struct.unpack('>IIBBBBB', chunks[b'IHDR']), (3, 2, 8, 2, 0, 0, 0))
        self.assertEqual(zlib.decompress(chunks[b'IDAT']), (b'\0' + b'\xff\0\0' * 3) * 2)
        self.assertNotEqual(measure.png(3, 2), measure.png(3, 2, True))


accounting = module('preview-evidence-accounting')


class DiagnosticAccounting(unittest.TestCase):
    def test_missing_and_truncated_records_are_not_zero_durations(self):
        report = accounting.account('HN_DIAG {"event":"provider_begin","pid":7,"operation":"1"}\nHN_DIAG {')
        self.assertEqual(len(report['diagnostics']['malformed']), 1)
        self.assertTrue(report['diagnostics']['missing_flush'])
        operation = report['operations'][0]
        self.assertIsNone(operation['parent_unexplained_ns'])
        self.assertTrue(operation['phases']['capture']['missing'])
        self.assertTrue(operation['helper_telemetry_missing'])

    def test_nested_phases_use_interval_union_and_keep_helper_separate(self):
        import json
        rows = [dict(event='provider_call', begin_ns='10', end_ns='110'),
                dict(event='capture', begin_ns='20', end_ns='50'),
                dict(event='runtime_validation', begin_ns='30', end_ns='60'),
                dict(event='helper_telemetry', stderr='HN_DIAG {"event":"helper_provider_execution",'
                     '"begin_ns":"100000","end_ns":"900000"}', truncated=False)]
        report = accounting.account('\n'.join('HN_DIAG ' + json.dumps(dict(r, pid=7, operation='1', consumer='c'))
                                               for r in rows))
        self.assertEqual(report['operations'][0]['parent_unexplained_ns'], 60)
        self.assertEqual(report['operations'][0]['consumers'], ['c'])
        self.assertEqual(len(report['operations'][0]['helper_timelines']), 1)

    def test_same_operation_id_in_different_processes_does_not_merge(self):
        report = accounting.account('HN_DIAG {"event":"provider_begin","pid":1,"operation":"1"}\n'
                                    'HN_DIAG {"event":"provider_begin","pid":2,"operation":"1"}')
        self.assertEqual(len(report['operations']), 2)

    def test_failed_exit_preserves_partial_rows_and_cleanup_stop(self):
        import json
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'attempts.jsonl'
            result = accounting.preserve_attempt(output, 0, '{"sample":{"cleanup_failure":true}}\n{', '', 20)
            self.assertTrue(result['cleanup_failure'])
            self.assertTrue(result['incomplete'])
            self.assertEqual(len(result['samples']), 1)
            self.assertEqual(json.loads(output.read_text()), result)

    def test_runner_stops_after_cleanup_failure_without_next_invocation(self):
        import json
        import subprocess
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'provenance.json').write_text('{}')
            fixtures = root / 'fixtures'
            fixtures.mkdir()
            for name in ('160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg'):
                (fixtures / name).write_bytes(b'fixture')
            binary = root / 'A/harness/preview-grid-control'
            binary.parent.mkdir(parents=True)
            binary.write_text('#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\n'
                              'Path(sys.argv[5]).write_text(\'{"sample":{"cleanup_failure":true}}\\n\')\n'
                              'raise SystemExit(20)\n')
            binary.chmod(0o755)
            completed = subprocess.run(['python3', str(ROOT / 'scripts/run-preview-evidence.py'),
                                        str(root), str(fixtures), '--kind', 'scheduler'],
                                       capture_output=True, text=True)
            self.assertEqual(completed.returncode, 20, completed.stderr)
            output = next(root.glob('scheduler-run-*'))
            provenance = json.loads((output / 'provenance.json').read_text())
            self.assertEqual(len(provenance['commands']), 1)
            self.assertEqual(provenance['completed_invocations'], 1)
            self.assertEqual(len((output / 'attempts.jsonl').read_text().splitlines()), 1)

    def test_overflow_and_silently_missing_records_remain_explicit(self):
        rows, diagnostic = accounting.telemetry('HN_DIAG {"event":"capture"}\n'
                                                'HN_DIAG {"event":"flush","records":2,"dropped":3}')
        self.assertEqual(diagnostic['dropped'], 3)
        self.assertEqual(diagnostic['record_count_mismatches'], [{'claimed': 2, 'observed': 1}])

    def test_missing_proc_observation_does_not_become_zero_memory(self):
        runner = module('run-preview-evidence')
        with tempfile.TemporaryDirectory() as temporary:
            observed = runner.observe(123, Path(temporary))
        self.assertFalse(observed['discovery_complete'])
        self.assertIsNone(observed['parent_rss_bytes'])
        self.assertIsNone(observed['concurrent_scope_bytes'])

    def test_homogeneous_batches_do_not_qualify_as_mixed_fixture_control(self):
        reporter = module('report-preview-evidence')
        names = ['160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg']
        row = {'fixture_cycle': names,
               'sample': {'operations': [{'source_fixture': name} for name in names * 4]}}
        self.assertTrue(reporter.mixed_fixture_batch(row))
        row['sample']['operations'][1]['source_fixture'] = names[0]
        self.assertFalse(reporter.mixed_fixture_batch(row))
        self.assertFalse(reporter.mixed_fixture_batch({'fixture': names[0], 'sample': {}}))


if __name__ == '__main__':
    unittest.main()
