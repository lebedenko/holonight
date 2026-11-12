"""Offline delivery-boundary, selection and integrity regressions."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gaps', ROOT / 'scripts/analyze-preview-delivery-gaps-v3.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class DeliveryGapTests(unittest.TestCase):
    def row(self):
        def event(ns, phase, line):
            return dict(ns=ns, phase=phase, file='/raw.stderr', line=line, pid=1, service=2,
                        observation=3, job=4, worker=5, request='diagnostic', tid=6, role='demand')

        def span(start, stop, phase, line):
            return dict(start=start, stop=stop, phase=phase, role='demand',
                        begin=event(start, phase, line), end=event(stop, phase, line+1))

        return dict(mode='T', variant='A', fixture='3200x2400.png', warmup=False, block=0, sample=0,
                    latencies=dict(first_ms=10, final_ms=12), deliveries=[event(20, 'pixels', 10), event(25, 'metadata', 11)],
                    timeline=[span(1, 5, 'decode_exchange_including_transport', 1), span(8, 12, 'cleanup', 3),
                              span(9, 10, 'runtime_validation', 5), span(18, 30, 'source_capture', 7)],
                    markers=[event(17, 'test_marker', 9)])

    def test_endpoints_clipping_nested_union_and_raw_references(self):
        row = self.row()
        p = g.interval(row, 'pixels', 'decode')
        m = g.interval(row, 'metadata', 'decode')
        self.assertEqual(p['elapsed_ms'], 15/1e6)
        self.assertEqual(m['elapsed_ms'], 20/1e6)
        self.assertEqual(p['covered_intervals_ns'], [[8, 12], [18, 20]])
        self.assertEqual(p['uncovered_intervals_ns'], [[5, 8], [12, 18]])
        self.assertAlmostEqual(p['covered_union_ms'] + p['uncovered_ms'], p['elapsed_ms'])
        self.assertEqual(p['intervening_spans'][-1]['clipped_stop'], 20)
        self.assertEqual(p['boundary']['line'], 2)
        self.assertEqual(p['delivery']['line'], 10)
        self.assertEqual(p['intervening_markers'][0]['file'], '/raw.stderr')

    def test_cleanup_requires_unique_intervening_identity(self):
        row = self.row()
        self.assertEqual(g.interval(row, 'pixels', 'cleanup')['elapsed_ms'], 8/1e6)
        cleanup = row['timeline'][1]
        cleanup['role'] = 'shutdown'
        self.assertEqual(g.interval(row, 'pixels', 'cleanup')['unavailable'], 'absent_cleanup')
        cleanup['role'] = 'demand'
        cleanup['stop'] = 22
        self.assertEqual(g.interval(row, 'pixels', 'cleanup')['unavailable'], 'absent_cleanup')
        self.assertEqual(g.interval(row, 'metadata', 'cleanup')['start_ns'], 22)
        cleanup['stop'] = 12
        row['timeline'].append(copy.deepcopy(cleanup))
        self.assertEqual(g.interval(row, 'pixels', 'cleanup')['unavailable'], 'ambiguous_cleanup')

    def test_decode_ambiguity_never_chooses_nearest(self):
        row = self.row()
        second = copy.deepcopy(row['timeline'][0])
        second['stop'] = 19
        row['timeline'].append(second)
        self.assertEqual(g.interval(row, 'pixels', 'decode')['unavailable'], 'ambiguous_decode')
        for field in g.IDENTITY:
            other = copy.deepcopy(row)
            other['timeline'][-1]['begin'][field] = 'foreign'
            self.assertEqual(g.interval(other, 'pixels', 'decode')['start_ns'], 5)
        row['timeline'] = []
        self.assertEqual(g.interval(row, 'pixels', 'decode')['unavailable'], 'missing_decode')

    def test_setup_standby_shutdown_and_post_delivery_not_coverage(self):
        row = self.row()
        for s in row['timeline'][1:]:
            s['role'] = 'standby'
        row['timeline'].append(dict(row['timeline'][0], start=21, stop=30, phase='cleanup'))
        w = g.interval(row, 'pixels', 'decode')
        self.assertEqual(w['covered_union_ms'], 0)
        self.assertEqual(w['uncovered_intervals_ns'], [[5, 20]])
        self.assertTrue(all(s['clipped_stop'] <= 20 for s in w['intervening_spans']))

    def test_summary_excludes_warmups_and_separates_u(self):
        r = self.row()
        r['intervals'] = {e: {b: g.interval(r, e, b) for b in ('decode', 'cleanup')} for e in ('pixels', 'metadata')}
        values = [r, dict(r, warmup=True), dict(r, mode='U')]
        summary = g.summarize(values)
        self.assertTrue(all(s['observations'] == 1 for s in summary))
        self.assertTrue(all('intervals' not in s for s in summary if s['mode'] == 'U'))

    def test_examples_median_near_and_tails_deterministic(self):
        r = self.row()
        values = [dict(r, block=b, sample=s, latencies=dict(first_ms=b, final_ms=3-b)) for b in range(4) for s in range(2)]
        selected = g.examples(list(reversed(values)) + [dict(r, warmup=True), dict(r, mode='U')])
        self.assertEqual([(x['block'], x['sample']) for x in selected[0]['median_near']], [(1, 0), (1, 1), (2, 0), (2, 1), (0, 0)])
        self.assertEqual(selected[0]['tails'][0]['block'], 3)
        self.assertEqual(selected[1]['tails'][0]['block'], 0)

    def test_invalid_destinations_and_hash_failure_preserve_partial_outputs(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as directory:
            base = Path(directory)
            root, prior = base / 'input', base / 'prior'
            root.mkdir()
            prior.mkdir()
            for out in (root / 'out', prior / 'out', base, ROOT / 'outside-build-test'):
                with self.assertRaises(ValueError):
                    g.analyze(root, prior, out)
            evidence = root / 'evidence'
            evidence.write_text('retained')
            (prior / 'input-integrity.json').write_text(json.dumps(dict(unchanged=True,
                before={str(evidence): 'wrong'}, after={str(evidence): 'wrong'})))
            out = base / 'output'
            self.assertEqual(g.analyze(root, prior, out), 1)
            self.assertEqual(json.loads((out / 'assessment.json').read_text())['status'], 'blocked')
            self.assertIn('integrity mismatch', (out / 'issues.json').read_text())
            self.assertTrue((out / 'intervals.json').exists())
            self.assertTrue(json.loads((out / 'input-integrity.json').read_text())['unchanged'])
            with self.assertRaises(FileExistsError):
                g.analyze(root, prior, out)


if __name__ == '__main__':
    unittest.main()
