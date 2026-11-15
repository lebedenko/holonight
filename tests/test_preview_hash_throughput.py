import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


r = module('hash_runner_test', 'run-preview-hash-throughput.py')
v = module('hash_checker_test', 'verify-preview-hash-throughput.py')


def fixture():
    mapping = [dict(ordinal=0, path='empty', size=0, sha256='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
               dict(ordinal=1, path='abc', size=3, sha256='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')]
    reg = dict(mapping=mapping, schedule=r.schedule())
    rows = [dict(type='identity', pid=123, provider='default', maps='')]
    for sweep in reg['schedule']:
        for file in mapping:
            rows.append(dict(sweep, type='file', ordinal=file['ordinal'], bytes=file['size'], sha256=file['sha256'],
                             init_ns=1, update_ns=10 if file['size'] else 100, final_ns=1))
        rows.append(dict(type='sweep_end', index=sweep['index'], elapsed_ns=200))
    return reg, rows


class HashThroughputTests(unittest.TestCase):
    def replay(self, reg, rows):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'raw'
            path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
            return v.replay(path, reg)

    def test_fixed_rotation_and_population(self):
        schedule = r.schedule()
        self.assertEqual(len(schedule), 130)
        self.assertEqual(sum(s['warmup'] for s in schedule), 5)
        for block in range(5):
            group = [s for s in schedule if s['block'] == block]
            self.assertEqual(group[0]['case'], v.CASES[block])
            self.assertEqual([s['sweep'] for s in group[:5]], list(range(5)))
            for case in v.CASES:
                self.assertEqual(sum(s['case'] == case for s in group), 5)

    def test_zero_bytes_warmup_exclusion_and_pooled_arithmetic(self):
        reg, raw = fixture()
        _, rows = self.replay(reg, raw)
        summary = v.summaries(rows)
        self.assertEqual(r.report(rows), summary)
        pooled = next(c for c in summary['cells'] if c['block'] == 'pooled')
        self.assertEqual((pooled['files'], pooled['bytes'], pooled['update_ns']), (50, 75, 2750))
        self.assertEqual(pooled['bytes_per_second'], 75*1e9/2750)
        warmup = next(c for c in summary['cells'] if c['warmup'])
        self.assertEqual(warmup['files'], 2)
        self.assertEqual(warmup['bytes'], 3)

    def test_nearest_rank_p95_ties(self):
        self.assertEqual(v.dist([1]*18 + [7, 7]), dict(count=20, minimum=1, median=1.0, p95=7, maximum=7))

    def test_rejects_missing_duplicate_reordered_wrong_digest_and_bad_timing(self):
        reg, raw = fixture()
        variants = [raw[:-1], raw + [raw[-1]], raw[:1] + raw[2:], raw[:2] + [raw[1]] + raw[2:]]
        for key, value in (('sha256', 'wrong'), ('bytes', 1), ('ordinal', 5), ('update_ns', 0),
                           ('init_ns', -1), ('final_ns', 1.5), ('index', 3), ('case', 'evp_memory')):
            changed = copy.deepcopy(raw)
            changed[1][key] = value
            variants.append(changed)
        changed = copy.deepcopy(raw)
        changed[3]['elapsed_ns'] = 30000000001
        variants.append(changed)
        for rows in variants:
            with self.subTest(rows=len(rows)), self.assertRaises((ValueError, KeyError)):
                self.replay(reg, rows)

    def test_malformed_json_rejected(self):
        reg, _ = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'raw'
            path.write_text('{bad}\n')
            with self.assertRaises(ValueError):
                v.replay(path, reg)

    def test_schedule_tampering_rejected(self):
        reg, rows = fixture()
        reg['schedule'][5]['case'] = 'evp_file'
        with self.assertRaises(ValueError):
            self.replay(reg, rows)

    def test_collision_preserves_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / 'marker'
            marker.write_text('keep')
            with self.assertRaises(ValueError):
                r.run(root / 'audit', root / 'verification', root)
            self.assertEqual(marker.read_text(), 'keep')

    def test_timeout_kills_and_reaps_ignoring_termination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = 'import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)'
            with self.assertRaises(ValueError):
                r.execute([sys.executable, '-c', code], root, 'timeout', .2)
            saved = v.read(root / 'timeout.json')
            self.assertTrue(saved['timed_out'])
            self.assertTrue(saved['cleanup'])
            self.assertEqual(saved['returncode'], -9)
            with self.assertRaises(ProcessLookupError):
                os.kill(saved['pid'], 0)

    def test_failure_seals_partial_evidence_with_complete_unexecuted_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = r.run(root / 'missing-audit', root / 'missing-verification', root / 'output')
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(len(result['unexecuted_schedule']), 130)
            v.seal(root / 'output')
            with self.assertRaises(ValueError):
                v.verify(root / 'output')

    def test_provenance_binding_and_seal_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit = root / 'audit'
            audit.mkdir()
            r.write(audit / 'assessment.json', dict(status='complete'))
            r.seal(audit)
            verification = root / 'verification.json'
            r.write(verification, dict(status='passed', audit_seal='wrong', measured_observations=40, warmups=2, validations=52))
            with self.assertRaisesRegex(ValueError, 'binding'):
                v.provenance(audit, verification)
            (audit / 'assessment.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'seal mismatch'):
                v.provenance(audit, verification)

    def test_accounting_tampering_after_reseal_rejected(self):
        reg, raw = fixture()
        _, rows = self.replay(reg, raw)
        summary = r.report(rows)
        summary['cells'][0]['bytes'] += 1
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            r.write(root / 'summary.json', summary)
            r.seal(root)
            v.seal(root)
            with self.assertRaisesRegex(ValueError, 'accounting'):
                v.check_accounting(rows, v.read(root / 'summary.json'))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            v.decode('{"bytes": 0, "bytes": 1}')


if __name__ == '__main__':
    unittest.main()
