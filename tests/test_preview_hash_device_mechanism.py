import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


r = module('mechanism_runner', 'run-preview-hash-device-mechanism.py')
v = module('mechanism_checker', 'verify-preview-hash-device-mechanism.py')


def fixture(counting=False):
    mapping = [dict(ordinal=0, path='empty', size=0, sha256='empty'),
               dict(ordinal=1, path='partial', size=1025, sha256='partial')]
    reg = dict(mapping=mapping, schedule=r.schedule(), count_schedule=r.count_schedule())
    raw = [dict(type='identity', pid=123, counting=counting, maps='')]
    for sweep in reg['count_schedule' if counting else 'schedule']:
        for f in mapping:
            row = dict(sweep, type='file', ordinal=f['ordinal'], bytes=f['size'], sha256=f['sha256'],
                       init_ns=1, update_ns=10 + 2*v.CASES.index(sweep['case']), final_ns=1)
            if counting:
                case = row['case']
                chunk = 65536 if '64k' in case else 1024
                n = (f['size'] + chunk - 1)//chunk
                row.update(read_calls=None if case.startswith('device') else 0 if case.startswith('memory') else n+1,
                           update_calls=None if case.startswith('device') else n, histogram=[])
                if not case.startswith('memory'):
                    bins = {}
                    remaining = f['size']
                    while remaining:
                        count = min(chunk, remaining)
                        bins[count] = bins.get(count, 0)+1
                        remaining -= count
                    bins[0] = 1
                    row['histogram'] = [dict(requested=chunk, returned=k, calls=c) for k, c in bins.items()]
            raw.append(row)
        raw.append(dict(type='sweep_end', index=sweep['index'], elapsed_ns=1000))
    return reg, raw


class MechanismTests(unittest.TestCase):
    def replay(self, reg, raw, counting=False):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'raw'
            p.write_text(''.join(json.dumps(x)+'\n' for x in raw))
            return v.replay(p, reg, counting)

    def test_balanced_schedule_and_separate_counting(self):
        self.assertEqual(r.schedule(), v.expected_schedule())
        self.assertEqual(r.count_schedule(), v.expected_schedule(True))
        self.assertEqual(len(r.schedule()), 200)
        self.assertEqual(sum(x['warmup'] for x in r.schedule()), 8)
        for b in range(8):
            group = [s for s in r.schedule() if s['block'] == b]
            self.assertEqual(len(group), 24)
            self.assertEqual(group[0]['case'], v.CASES[b])
            self.assertEqual([s['sweep'] for s in group[:3]], [0, 1, 2])
            for c in v.CASES:
                self.assertEqual(sum(x['case'] == c for x in group), 3)
        self.assertEqual(192*60, 11520)
        self.assertEqual(192*87215960, 16745464320)

    def test_signed_reconciliation_and_warmup_exclusion(self):
        reg, raw = fixture()
        _, rows = self.replay(reg, raw)
        result = r.report(rows)
        self.assertEqual(result, v.summaries(rows))
        first = result['contrasts'][0]
        self.assertEqual(first['difference_sum_ns'], -24)
        self.assertEqual(first['mean_difference_ns'], -8)
        self.assertEqual(sum(c['difference_sum_ns'] for c in first['contributions']), -24)
        for row in rows:
            if row['warmup']: row['update_ns'] = 1000000
        self.assertEqual(result, v.summaries(rows))

    def test_histograms_and_empty_files(self):
        reg, raw = fixture(True)
        _, rows = self.replay(reg, raw, True)
        self.assertEqual(len(rows), 16)
        self.assertEqual(sum(row['bytes'] for row in rows), 8*1025)
        self.assertEqual(r.report_counts(rows), v.count_summary(rows))
        for key, value in [('calls', 0), ('requested', -1), ('returned', -1), ('calls', 2)]:
            altered = copy.deepcopy(raw)
            altered[2]['histogram'][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.replay(reg, altered, True)

    def test_rejects_coverage_digest_schedule_and_extra_rows(self):
        reg, raw = fixture()
        for key, value in [('ordinal', 1), ('sha256', 'bad'), ('bytes', 1), ('index', 99), ('update_ns', 0)]:
            altered = copy.deepcopy(raw)
            altered[1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): self.replay(reg, altered)
        for altered in (raw[:-1], raw+[raw[-1]], raw[:1]+raw[2:]):
            with self.assertRaises(ValueError): self.replay(reg, altered)
        with self.assertRaises(ValueError): self.replay(reg, fixture(True)[1])

    def test_rejects_duplicate_json_and_malformed_raw(self):
        with self.assertRaises(ValueError): v.decode('{"a":1,"a":2}')
        with self.assertRaises(ValueError): v.decode('{')

    def test_collisions_and_sealed_partial_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'out'
            out.mkdir()
            with self.assertRaises(ValueError): r.run(Path(tmp)/'audit', Path(tmp)/'verification', out)
            out = Path(tmp)/'failed'
            result = r.run(Path(tmp)/'missing-audit', Path(tmp)/'missing-check', out)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(len(result['unexecuted_schedule']), 200)
            self.assertEqual(len(result['unexecuted_count_schedule']), 8)
            self.assertTrue(result['cleanup'])
            v.seal(out)
            (out/'schedule.json').write_text('[]')
            with self.assertRaises(ValueError): v.seal(out)

    def test_timeout_cleanup_retains_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with self.assertRaises(ValueError):
                r.execute([sys.executable, '-c', 'import time; time.sleep(60)'], out, 'timeout', .05)
            record = v.read(out/'timeout.json')
            self.assertTrue(record['cleanup'])
            self.assertTrue(record['timed_out'])

    def test_resealed_signed_tampering_rejected(self):
        reg, raw = fixture()
        _, rows = self.replay(reg, raw)
        saved = r.report(rows)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            saved['contrasts'][0]['contributions'][0]['difference_sum_ns'] += 1
            r.write(out/'summary.json', saved)
            r.seal(out)
            v.seal(out)
            self.assertNotEqual(v.summaries(rows), v.read(out/'summary.json'))

    def test_exact_audit_pin_rejects_resealed_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = Path(tmp)/'preview-hash-device-path-20261116-15'
            audit.mkdir()
            r.write(audit/'assessment.json', dict(status='complete', source_status='exact', new_measurements=False))
            r.seal(audit)
            verification = Path(tmp)/'verification.json'
            r.write(verification, dict(status='passed', source_status='exact', audit_seal=v.digest(audit/'seal.json')))
            with self.assertRaisesRegex(ValueError, 'wrong exact-source audit'):
                v.provenance(audit, verification)

    def test_malformed_process_output_is_cleaned_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with self.assertRaises(ValueError):
                r.execute([sys.executable, '-c', 'print("malformed", flush=True)'], out, 'bad', 2, True)
            self.assertTrue(v.read(out/'bad.json')['cleanup'])



if __name__ == '__main__':
    unittest.main()
