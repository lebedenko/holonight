import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


r = module('assessor', 'assess-preview-hash-value.py')
v = module('checker', 'verify-preview-hash-value.py')


def fixture():
    mapping = [dict(ordinal=0, size=0, path='empty', sha256='empty'),
               dict(ordinal=1, size=1, path='one', sha256='one')]
    schedule, rows = [], [dict(type='identity', pid=123, counting=False)]
    for block in [None, *range(8)]:
        for case in ('device_buffered', 'stream_64k_buffered'):
            for sweep in range(1 if block is None else 3):
                s = dict(index=len(schedule), case=case, block=block, warmup=block is None, sweep=sweep)
                schedule.append(s)
                for f in mapping:
                    # Empty-file contribution is negative; nonempty is positive.
                    ns = (10 if f['ordinal'] == 0 else 40) if case == 'device_buffered' else 20
                    rows.append(dict(s, type='file', ordinal=f['ordinal'], bytes=f['size'], sha256=f['sha256'], update_ns=ns))
    return mapping, schedule, rows


class HashValueTests(unittest.TestCase):
    def save_mechanism(self, root, mapping, schedule, rows):
        r.write(root / 'preregistration.json', dict(mapping=mapping, schedule=schedule))
        r.write(root / 'native.json', dict(pid=123))
        (root / 'native.stdout').write_text(''.join(json.dumps(x)+'\n' for x in rows))

    def test_direct_signed_arithmetic_includes_empty_and_excludes_warmups(self):
        mapping, schedule, rows = fixture()
        blocks = r.arithmetic(rows, mapping)
        self.assertEqual([c['difference_sum_ns'] for c in blocks[0]['contributions']], [-30, 60])
        self.assertEqual(blocks[0]['mean_difference_ns'], 10)
        self.assertEqual(blocks[0]['duration_ratio'], 1.25)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.save_mechanism(root, mapping, schedule, rows)
            self.assertEqual(blocks, v.comparison(root, mapping))
        for row in rows[1:]:
            if row['warmup']:
                row['update_ns'] = 999999999
        self.assertEqual(blocks, r.arithmetic(rows, mapping))

    def test_missing_duplicate_ordinals_and_process_identity(self):
        mapping, schedule, rows = fixture()
        for altered in (rows[:-1], rows + [rows[-1]], copy.deepcopy(rows)):
            if len(altered) == len(rows):
                altered[1]['ordinal'] = 1
            with self.subTest(length=len(altered)), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.save_mechanism(root, mapping, schedule, altered)
                with self.assertRaises(ValueError):
                    v.comparison(root, mapping)
        rows[0]['pid'] = 456
        with tempfile.TemporaryDirectory() as tmp:
            self.save_mechanism(Path(tmp), mapping, schedule, rows)
            with self.assertRaisesRegex(ValueError, 'process mismatch'):
                v.comparison(Path(tmp), mapping)

    def test_threshold_below_equal_above_and_mixed_directions(self):
        for ns, expected in [(4_999_999, (8, 0, 0)), (5_000_000, (0, 8, 0)), (5_000_001, (0, 0, 8))]:
            blocks = [dict(mean_difference_ns=ns, difference_sum_ns=ns*3) for _ in range(8)]
            decision = r.recommendation(blocks)
            self.assertEqual(decision, v.decision(blocks))
            self.assertEqual(tuple(decision[k] for k in ('below_threshold', 'equal_threshold', 'above_threshold')), expected)
            self.assertEqual(decision['recommendation'].startswith('defer'), ns < 5_000_000)
            self.assertFalse(decision['future_5ms_savings_ruled_out'])
        blocks[0] = dict(mean_difference_ns=-1, difference_sum_ns=-3)
        self.assertEqual(r.recommendation(blocks)['direction'], 'mixed; inconclusive')

    def test_collision_overlap_and_sealed_partial_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paths = [base / str(i) for i in range(4)]
            with self.assertRaisesRegex(ValueError, 'collision'):
                r.run(*paths, base)
            with self.assertRaisesRegex(ValueError, 'overlap'):
                r.run(*paths, paths[0] / 'child')
            out = base / 'failed'
            result = r.run(*paths, out)
            self.assertEqual(result['status'], 'blocked')
            self.assertIsNone(result['recommendation'])
            self.assertFalse((out / 'decision.json').exists())
            v.seal(out)
            with self.assertRaisesRegex(ValueError, 'blocked'):
                v.verify(out)

    def test_provenance_drift_and_verification_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            roots, verifications = [], []
            for name, expected, vh, key in v.PINS:
                root = base / name
                root.mkdir()
                r.write(root / 'assessment.json', dict(status='complete'))
                r.seal(root)
                verification = base / (name + '.json')
                r.write(verification, dict(status='passed', **{key: expected}))
                roots.append(root)
                verifications.append(verification)
            with self.assertRaisesRegex(ValueError, 'identity drift'):
                v.bindings(roots[0], verifications[0], roots[1], verifications[1])

    def test_resealed_arithmetic_tampering(self):
        mapping, schedule, rows = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.save_mechanism(root, mapping, schedule, rows)
            blocks = r.arithmetic(rows, mapping)
            blocks[0]['contributions'][0]['difference_sum_ns'] += 1
            r.write(root / 'arithmetic.json', blocks)
            r.seal(root)
            v.seal(root)
            self.assertNotEqual(v.comparison(root, mapping), v.read(root / 'arithmetic.json'))

    def test_population_separation_and_join_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            execution, report = work / 'execution', work / 'report'
            execution.mkdir()
            report.mkdir()
            commands, rows, observed, lifetimes = [], [], [], []
            for i in range(52):
                population = 'measured' if i < 40 else 'warmup' if i < 42 else 'setup'
                arm = 'profiled' if i % 2 else 'unprofiled'
                commands.append(dict(invocation=dict(warmup=population == 'warmup', arm=arm, block=None)))
                row = dict(invocation=i, observation=None if population == 'setup' else 1,
                           root=dict(pid=123, service=i, span=i), population=population, arm=arm, block=None,
                           validation_ns=10 if population == 'measured' else 999, read_hash_ns=5)
                if population != 'setup': row['endpoints_ns'] = dict(pixels=20, metadata=30)
                rows.append(row)
                lifetimes.append(dict(invocation=i, pid=123, service=i, validations=1, within_lifetime_repeated_bytes=0))
                if population == 'measured':
                    observed.append(dict(invocation=i, observation=1, arm=arm, block=None, validation_ns=10, pixel_ns=20, metadata_ns=30))
            r.write(work / 'inputs.json', dict(execution=str(execution), report=str(report)))
            r.write(execution / 'preregistration.json', dict(commands=commands))
            r.write(work / 'accounting.json', rows)
            r.write(work / 'lifetimes.json', lifetimes)
            r.write(work / 'source-citations.json', [])
            r.write(report / 'observations.json', observed)
            context = v.context(work)
            self.assertEqual(len(context['distributions']), 6)
            self.assertEqual(context['distributions'][0]['timings']['validation_ns']['median'], 10)
            self.assertEqual(context['distributions'][-1]['endpoints_ns']['pixels'], dict(count=0))
            observed[0]['invocation'] = 999
            (report / 'observations.json').write_text(json.dumps(observed))
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                v.context(work)


if __name__ == '__main__':
    unittest.main()
