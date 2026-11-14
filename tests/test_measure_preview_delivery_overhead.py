"""Deterministic checks for the fixed delivery overhead experiment."""
import copy
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

m = load('measure_delivery_overhead', 'scripts/measure-preview-delivery-overhead.py')
f = load('historical_overhead_tests', 'tests/test_preview_tracing_overhead.py')


class MeasurementTests(unittest.TestCase):
    def rows(self):
        return [dict(invocation=r, samples=[f.sample(10000, 20000) if r['warmup'] else f.sample(10, 20) if r['mode'] == 'v3' else f.sample(5, 10)] * r['observations']) for r in m.prep.schedule()]

    def test_schedule_and_negative_distributions(self):
        rows = self.rows()
        self.assertEqual(len(rows), 264)
        self.assertEqual(sum(len(r['samples']) for r in rows), 2424)
        report = m.statistics_report(rows)
        self.assertEqual(len(report), 24)
        self.assertEqual(report[0]['statistics']['median'], dict(v3=10, v4=5, delta_ms=-5, delta_percent=-50))
        self.assertTrue(all(len(c['blocks']) == 10 for c in report))
        for bad in (rows[:-1], rows + rows[:1], rows[::-1]):
            with self.assertRaises(ValueError):
                m.statistics_report(bad)
        rows[8]['samples'] = []
        with self.assertRaises(ValueError):
            m.statistics_report(rows)

    def test_nearest_rank_and_zero(self):
        self.assertEqual(m.old.comparison(list(range(1, 101)), [0] * 100)['p95']['delta_ms'], -95)
        self.assertIsNone(m.old.comparison([0], [1])['median']['delta_percent'])

    def test_integrity_and_missing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            (output / 'raw').write_text('original')
            m.seal(output)
            m.check_output(output)
            (output / 'raw').write_text('changed')
            with self.assertRaises(ValueError):
                m.check_output(output)
            with self.assertRaises((OSError, ValueError)):
                m.verify(output)

    def test_timeout_preserves_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'sample.json'
            result = m.gate.smoke.execute([sys.executable, '-c', 'import time;print("partial",flush=True);time.sleep(60)'], target, os.environ, {}, timeout=.1)
            self.assertTrue(result['timeout'])
            self.assertFalse(result['cleanup_verified'])
            self.assertIn('partial', target.with_suffix('.stdout').read_text())
            with self.assertRaises(ValueError):
                m.validate(target, m.prep.schedule()[0], result, os.getuid())

    def test_v4_count_required(self):
        for count in (1, 10):
            with self.assertRaises(ValueError):
                m.v4_gate(dict(issues=[], events=[dict(operation='endpoint_pixels')], spans=[]), 'A', count)

    def test_fixture_count_for_warmup_and_measured_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures = root / 'fixtures'
            fixtures.mkdir()
            (fixtures / 'image.png').write_bytes(b'fixture')
            target = root / 'sample.json'
            work = root / 'sample.json.work-private'
            work.mkdir()
            (work / 'cache').mkdir()
            with patch.object(m.old, 'FIXTURE_ROOT', fixtures):
                for count in (1, 10):
                    for i in range(count * 8 + 8):
                        (work / f'{i}.png').write_bytes(b'fixture')
                    row = dict(fixture='image.png', observations=count)
                    m.validate_work(target, row, os.getuid())
                    (work / '0.png').write_bytes(b'tampered')
                    with self.assertRaises(ValueError):
                        m.validate_work(target, row, os.getuid())
                    (work / '0.png').write_bytes(b'fixture')
                    with self.assertRaises(ValueError):
                        m.validate_work(target, row, os.getuid() + 1)
                (work / '0.png').unlink()
                with self.assertRaises(ValueError):
                    m.validate_work(target, row, os.getuid())

    def test_first_failure_and_integrity_drift_stop_launches(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            commands = [dict(invocation=r, argv=['synthetic', str(output / f'{i}.json')]) for i, r in enumerate(m.prep.schedule()[:2])]
            for integrity_failure in (False, True):
                result = dict(invocations=[])
                def integrity():
                    if integrity_failure:
                        raise ValueError('integrity drift')
                with patch.object(m.gate, 'scope_snapshot', return_value=dict(isolated=True)), \
                     patch.object(m.gate.smoke, 'execute', return_value=dict(exit=7, timeout=False, cleanup_verified=True)) as execute, \
                     patch.object(m, 'validate', side_effect=ValueError('failed evidence')):
                    with self.assertRaises(ValueError):
                        m.run_commands(commands, output, result, 1000, {}, {}, integrity)
                    self.assertEqual(execute.call_count, 0 if integrity_failure else 1)

    def test_supplemental_mode_contamination(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'sample.json'
            row = m.prep.schedule()[0]
            m.write(target, dict(scenario='startup', fixture=str(m.old.FIXTURE_ROOT / row['fixture']), samples=[f.sample()]))
            target.with_suffix('.stderr').write_text('DELIVERY {}')
            target.with_suffix('.stdout').write_text('')
            with patch.object(m.old, 'validate_trace', return_value=dict(issues=[])):
                with self.assertRaisesRegex(ValueError, 'contamination'):
                    m.validate(target, row, dict(exit=0, timeout=False, cleanup_verified=True), os.getuid())

    def test_generalized_v4_gate_accepts_one_and_ten(self):
        fixture = load('generalized_delivery_fixture', 'tests/test_preview_delivery_smoke.py')
        for variant in 'ABCD':
            historical, values = fixture.combined(variant)
            template = fixture.s.trace_validation(fixture.trace(historical, values), [{}, {}, {}], '/raw', variant)
            for count in (1, 10):
                report = dict(issues=[], events=[], spans=[], handoffs=[])
                for observation in range(1, count + 1):
                    for group in ('events', 'spans', 'handoffs'):
                        for original in template[group]:
                            context = original.get('begin', original.get('identity', original))
                            if context.get('observation') != 1:
                                continue
                            def remap(value):
                                if isinstance(value, list):
                                    return [remap(v) for v in value]
                                if isinstance(value, dict):
                                    return {k: observation if k == 'observation' and v is not None else v + observation * 10000 if k == 'publication' and v is not None else remap(v) for k, v in value.items()}
                                return value
                            report[group].append(remap(copy.deepcopy(original)))
                m.v4_gate(report, variant, count)
                report['events'] = [e for e in report['events'] if e['operation'] != 'endpoint_metadata']
                with self.assertRaises(ValueError):
                    m.v4_gate(report, variant, count)

    def test_incomplete_report_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            execution = root / 'build/execution'
            execution.mkdir()
            m.write(execution / 'assessment.json', dict(status='blocked', failure='fixture provenance mismatch', invocations=[]))
            m.seal(execution)
            before = m.inventory(execution)
            with patch.object(m, 'ROOT', root), patch.object(m, 'verify'):
                self.assertEqual(m.report(root / 'prepared', execution, root / 'build/report'), 1)
            self.assertEqual(m.inventory(execution), before)
            report = m.read(root / 'build/report/assessment.json')
            self.assertEqual(report['unexecuted'], 264)
            self.assertFalse(report['statistics_available'])


if __name__ == '__main__':
    unittest.main()
