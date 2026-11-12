"""Offline endpoint, corpus and evidence regressions."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('v3', ROOT / 'scripts/analyze-preview-startup-v3.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
spec = importlib.util.spec_from_file_location('historical_tests', ROOT / 'tests/test_preview_startup_analysis.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


class V3AnalysisTests(unittest.TestCase):
    def row(self, variant='C'):
        raw = h.StartupAnalysisTests().v3()
        events, spans, errors = v.a.parse_trace('noise\n' + '\n'.join('TRACE ' + json.dumps(e) for e in raw), '/raw.stderr')
        rows, issues, _ = v.a.account(events, spans, [{'first_ms': 1, 'final_ms': 2}], '/raw.stderr', variant)
        self.assertEqual(errors + issues, [])
        row = rows[0]
        row.update(mode='T', variant=variant, fixture='3200x2400.png', block=0, warmup=False)
        row['windows'] = {e: v.window(row, e) for e in ('pixels', 'metadata')}
        return row

    def test_separate_endpoints_clipping_envelopes_and_gaps(self):
        r = self.row()
        p, m = r['windows']['pixels'], r['windows']['metadata']
        self.assertEqual(p['elapsed_ms'], 15/1e6)
        self.assertEqual(m['elapsed_ms'], 16/1e6)
        self.assertEqual(p['phases']['decode_exchange_including_transport']['union_ms'], 1/1e6)
        self.assertEqual(m['phases']['decode_exchange_including_transport']['union_ms'], 2/1e6)
        self.assertEqual(m['phases']['construction_outer']['union_ms'], 3/1e6)
        self.assertEqual(m['covered_union_ms'], 4/1e6)  # body + helper + clipped exchange
        self.assertEqual(m['uncovered_intervals_ns'], [[0, 2], [3, 7], [8, 14]])
        self.assertEqual(v.a.union([(1, 9), (2, 4), (8, 10)]), [[1, 10]])

    def test_absent_by_design_and_raw_lines(self):
        r = self.row('A')
        self.assertEqual(r['windows']['pixels']['phases']['generation_validation']['availability'], 'absent_by_design')
        self.assertEqual(r['windows']['pixels']['phases']['source_capture']['availability'], 'missing_or_ambiguous')
        self.assertEqual(r['timeline'][0]['begin']['file'], '/raw.stderr')
        self.assertEqual(r['timeline'][0]['begin']['line'], 3)
        changed = json.loads(json.dumps(r))
        changed['timeline'][0]['begin']['file'] = 'retained.json'
        self.assertEqual(v.semantic(r), v.semantic(changed))
        changed['timeline'][0]['begin']['line'] += 1
        self.assertNotEqual(v.semantic(r), v.semantic(changed))

    def test_identity_attributed_overlap(self):
        r = self.row()
        s = dict(r['timeline'][0], phase='pool_worker_prepare', role='standby', start=14, stop=16)
        r['timeline'].append(s)
        self.assertEqual(v.window(r, 'pixels')['standby_overlap_ms'], 1/1e6)
        s['role'] = 'unknown'
        self.assertEqual(v.window(r, 'pixels')['standby_overlap_ms'], 0)

    def test_warmups_and_u_have_no_phase_estimates_and_tails_tie_break(self):
        r = self.row()
        warmup = dict(r, warmup=True, block=None)
        u = dict(r, mode='U')
        groups = v.summarize([r, warmup, u])
        self.assertTrue(all(g['observations'] == 1 for g in groups))
        self.assertTrue(all('phases' not in g for g in groups if g['mode'] == 'U'))
        candidates = [dict(r, block=b, sample=s) for b in (2, 1, 0) for s in (1, 0)]
        selected = v.select_tails(candidates + [warmup, u])[4]['observations']
        self.assertEqual([(x['block'], x['sample']) for x in selected], [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)])

    def test_complete_counts_and_setup_exclusion(self):
        inventory = v.overhead.schedule()
        counts = v.check_counts(inventory, 1344)
        self.assertEqual(counts['setup_services'], 132)
        self.assertEqual(counts['T_measured'], 1200)
        for inv, services in ((inventory[:-1], 1344), (inventory, 1343)):
            with self.assertRaises(ValueError):
                v.check_counts(inv, services)

    def test_invalid_destination_and_integrity_failure_preserve_evidence(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as directory:
            base = Path(directory)
            root = base / 'input'
            root.mkdir()
            with self.assertRaises(ValueError):
                v.analyze(root, root / 'output')
            (root / 'final-evidence-hashes.json').write_text('{}')
            (root / 'seal.json').write_text(json.dumps({'preparation.json': 'incorrect'}))
            (root / 'preparation.json').write_text('{}')
            out = base / 'output'
            self.assertEqual(v.analyze(root, out), 1)
            self.assertEqual(json.loads((out / 'assessment.json').read_text())['status'], 'blocked')
            self.assertIn('integrity mismatch', (out / 'attribution-issues.json').read_text())
            self.assertTrue(json.loads((out / 'input-integrity.json').read_text())['unchanged'])
            with self.assertRaises(FileExistsError):
                v.analyze(root, out)


if __name__ == '__main__':
    unittest.main()
