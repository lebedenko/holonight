"""Offline accounting regressions; no measured programs are executed."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('startup', Path(__file__).resolve().parents[1] / 'scripts/analyze-preview-startup.py')
a = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a)


def event(ns, phase, edge='begin', tid=1, obj='service', slot=-1, request='changing'):
    return dict(ns=ns, phase=phase, edge=edge, pid=1, tid=tid, object=obj, slot=slot, request=request)


def parse(events):
    return a.parse_trace('\n'.join('TRACE ' + json.dumps(e) for e in events), 'test.log')


class StartupAnalysisTests(unittest.TestCase):
    def test_interval_union_and_uncovered_gaps(self):
        self.assertEqual(a.union([(1, 10), (2, 3), (8, 12), (15, 16)]), [[1, 12], [15, 16]])
        self.assertEqual(a.gaps(0, 20, [(1, 10), (2, 3), (8, 12), (15, 16)]), [[0, 1], [12, 15], [16, 20]])

    def test_nested_matching_interleaved_threads_and_changed_labels(self):
        events = [event(1, 'p'), event(2, 'p'), event(3, 'p', tid=2),
                  event(4, 'p', 'end', request='new'), event(5, 'p', 'end', tid=2), event(6, 'p', 'end')]
        _, spans, issues = parse(events)
        self.assertEqual([(s['start'], s['stop']) for s in spans], [(1, 6), (2, 4), (3, 5)])
        self.assertEqual(issues, [])

    def test_malformed_truncated_and_unmatched_remain_visible(self):
        _, _, issues = a.parse_trace('TRACE {\nTRACE ' + json.dumps(event(1, 'p')) + '\nTRACE ' + json.dumps(event(2, 'q', 'end')), 'bad.log')
        self.assertEqual({i['kind'] for i in issues}, {'malformed', 'unmatched_begin', 'unmatched_end'})
        self.assertTrue(all(i['line'] for i in issues))

    def fixture(self, missing=False):
        events = [event(0, 'service_construction'), event(1, 'service_construction', 'end'),
                  event(10, 'service_construction'), event(11, 'service_construction', 'end'),
                  event(12, 'pool_prepare', tid=2, obj='pool', slot=0), event(13, 'pool_prepare', 'end', tid=2, obj='pool', slot=0),
                  event(14, 'pool_worker_prepare', tid=3, obj='pool', slot=0),
                  event(15, 'helper_prepare', tid=3, obj='helper'), event(16, 'helper_prepare', 'end', tid=3, obj='helper'),
                  event(17, 'pool_worker_prepare', 'end', tid=3, obj='pool', slot=0),
                  event(18, 'pool_job', tid=3, obj='pool', slot=0),
                  event(19, 'source_capture', tid=3), event(20, 'source_capture', 'end', tid=3),
                  event(21, 'inspect_exchange_including_transport', tid=3),
                  event(21, 'transaction_dispatch', tid=3, obj='pool', slot=0),
                  event(22, 'transaction_dispatch', 'end', tid=3, obj='pool', slot=0),
                  event(22, 'pool_worker_prepare', tid=4, obj='pool', slot=1),
                  event(23, 'helper_prepare', tid=4, obj='standby'), event(24, 'helper_prepare', 'end', tid=4, obj='standby'),
                  event(25, 'pool_worker_prepare', 'end', tid=4, obj='pool', slot=1),
                  event(26, 'inspect_exchange_including_transport', 'end', tid=3),
                  event(27, 'pool_job', 'end', tid=3, obj='pool', slot=0),
                  event(28, 'cleanup', tid=8, obj='previous'), event(29, 'cleanup', 'end', tid=8, obj='previous'),
                  event(30, 'pixels', 'point')]
        if not missing:
            events.append(event(31, 'metadata', 'point'))
        return parse(events)

    def test_demand_standby_pointer_reuse_and_previous_cleanup(self):
        events, spans, _ = self.fixture()
        rows, issues, unassigned = a.account(events, spans, [{'first_ms': 1, 'final_ms': 2}], 'test.log')
        row = rows[0]
        self.assertEqual(issues, [])
        self.assertEqual(row['status'], 'associated')
        self.assertEqual(row['phases']['helper_prepare']['count'], 1)
        self.assertIsNone(row['phases']['cleanup'])
        self.assertEqual(row['standby_overlap_ms'], 3 / 1e6)
        self.assertTrue(any(s['role'] == 'standby' for s in row['timeline']))
        self.assertTrue(row['unknown'])
        self.assertEqual(len(unassigned), 1)  # setup constructor
        self.assertEqual(rows, a.account(events, spans, [{'first_ms': 1, 'final_ms': 2}], 'test.log')[0])

    def test_missing_delivery_and_count_mismatch_do_not_join_by_label(self):
        events, spans, _ = self.fixture(missing=True)
        rows, issues, _ = a.account(events, spans, [{}, {}], 'test.log')
        self.assertTrue(issues)
        self.assertTrue(all(r['status'] == 'unknown' and r['unknown'] for r in rows))

    def test_partial_delivery_preserves_other_sample_and_pixel_accounting(self):
        events, spans, _ = self.fixture(missing=True)
        rows, issues, _ = a.account(events, spans, [{}], 'test.log')
        self.assertEqual(rows[0]['status'], 'partial')
        self.assertEqual(rows[0]['delivery_counts'], {'pixels': 1, 'metadata': 0})
        self.assertTrue(rows[0]['phases']['source_capture'])
        self.assertTrue(issues)

    def test_duplicate_pixels_are_reported_with_metadata_accounting(self):
        events, _, _ = self.fixture()
        events.append(dict(events[-2], ns=30, line=999))
        events, spans, _ = parse([{k: e[k] for k in a.FIELDS} for e in events])
        rows, issues, _ = a.account(events, spans, [{}], 'test.log')
        self.assertEqual(rows[0]['status'], 'partial')
        self.assertEqual(rows[0]['delivery_counts']['pixels'], 2)
        self.assertTrue(any(i['kind'] == 'service_delivery_count' for i in issues))

    def test_preparation_without_dispatch_remains_unknown(self):
        events, _, _ = self.fixture()
        events, spans, _ = parse([{k: e[k] for k in a.FIELDS} for e in events if e['phase'] != 'transaction_dispatch'])
        rows, _, _ = a.account(events, spans, [{}], 'test.log')
        self.assertFalse(any(s['role'] == 'standby' for s in rows[0]['timeline']))
        self.assertIsNone(rows[0]['standby_overlap_ms'])

    def test_explicit_identity_handles_overlapping_reused_addresses_and_delayed_work(self):
        raw = []
        def add(ns, phase, edge, service, observation, role='demand', job=1, worker=1):
            raw.append(dict(event(ns, phase, edge, obj='reused'), version=2, service=service,
                            observation=observation, job=job + service * 10, worker=worker, role=role))
        add(0, 'service_construction', 'begin', 1, 1)
        add(1, 'service_construction', 'end', 1, 1)
        add(1, 'demand_dispatch', 'point', 1, 1)
        add(2, 'helper_prepare', 'begin', 1, 1)
        add(3, 'service_construction', 'begin', 2, 2)
        add(4, 'service_construction', 'end', 2, 2)
        add(5, 'pool_worker_prepare', 'begin', 2, 2, 'standby', 2, 2)
        add(5, 'helper_prepare', 'begin', 2, 2, 'standby', 2, 2)
        add(6, 'helper_prepare', 'end', 1, 1)
        add(7, 'helper_prepare', 'end', 2, 2, 'standby', 2, 2)
        add(7, 'pool_worker_prepare', 'end', 2, 2, 'standby', 2, 2)
        for service, observation, ns in ((1, 1, 8), (2, 2, 10)):
            add(ns, 'pixels', 'point', service, observation)
            add(ns + 1, 'metadata', 'point', service, observation)
        events, spans, issues = parse(raw)
        self.assertEqual(issues, [])
        rows, _, _ = a.account(events, spans, [{}, {}], 'test.log')
        self.assertEqual([r['status'] for r in rows], ['associated', 'associated'])
        self.assertEqual(rows[0]['phases']['helper_prepare']['count'], 1)
        self.assertIsNone(rows[1]['phases']['helper_prepare'])
        self.assertEqual(rows[0]['identity_limitations'], ['version 2 lacks preparation linkage'])
        self.assertTrue(all(s['begin']['service'] == 1 for s in rows[0]['timeline']))

    def test_v2_spans_do_not_pair_across_job_identities(self):
        raw = [dict(event(1, 'cleanup'), version=2, service=1, observation=1, job=1, worker=1, role='shutdown'),
               dict(event(2, 'cleanup', 'end'), version=2, service=1, observation=1, job=2, worker=1, role='shutdown')]
        _, spans, issues = parse(raw)
        self.assertEqual(spans, [])
        self.assertEqual(len(issues), 2)

    def test_controller_work_after_delivery_is_recovered_without_claiming_standby(self):
        events, _, _ = self.fixture()
        raw = [{k: e[k] for k in a.FIELDS} for e in events]
        raw += [event(32, 'pool_prepare', tid=2, obj='pool', slot=1),
                event(33, 'generation_acquisition', tid=2, obj='owner'),
                event(34, 'generation_acquisition', 'end', tid=2, obj='owner'),
                event(35, 'pool_prepare', 'end', tid=2, obj='pool', slot=1)]
        events, spans, _ = parse(raw)
        rows, _, _ = a.account(events, spans, [{}], 'test.log')
        late = [s for s in rows[0]['timeline'] if s['start'] >= 32]
        self.assertEqual({s['role'] for s in late}, {'service_control'})
        self.assertTrue(all(s['after_delivery'] for s in late))
        self.assertIsNone(rows[0]['phases']['generation_acquisition'])

    def test_multiple_preparations_are_not_collapsed(self):
        events, _, _ = self.fixture()
        raw = [{k: e[k] for k in a.FIELDS} for e in events]
        raw += [event(12, 'pool_worker_prepare', tid=3, obj='pool', slot=0),
                event(13, 'pool_worker_prepare', 'end', tid=3, obj='pool', slot=0)]
        events, spans, _ = parse(raw)
        rows, _, _ = a.account(events, spans, [{}], 'test.log')
        preps = [s for s in rows[0]['timeline'] if s['phase'] == 'pool_worker_prepare' and s['role'] == 'demand']
        self.assertEqual(len(preps), 2)

    def test_refuses_overwrite_or_output_inside_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                a.analyze(root, root / 'new', {})
            with self.assertRaises(FileExistsError):
                a.analyze(root / 'input', root, {})

    def test_identical_inputs_produce_identical_accounting_and_keep_warmups_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'evidence'
            root.mkdir()
            (root / 'trace.h').write_text('// synthetic')
            (root / 'result.json').write_text(json.dumps({'overlap': {k: {'overlapping_requests': 0} for k in 'CD'}}))
            events, _, _ = self.fixture()
            raw = '\n'.join('TRACE ' + json.dumps({k: e[k] for k in a.FIELDS}) for e in events)
            for mode in ('diagnostic', 'pilot'):
                folder = root / (mode + '-observations')
                folder.mkdir()
                for label in 'ABCD':
                    for tag in ('warmup', 'block-00'):
                        path = folder / f'{tag}-{label}-3200x2400.png.json'
                        path.write_text(json.dumps({'samples': [{'first_ms': 1, 'final_ms': 2}]}))
                        path.with_suffix('.log').write_text(raw if mode == 'diagnostic' else '')
            for name in ('one', 'two'):
                a.analyze(root, base / name, {'synthetic': True})
            self.assertEqual((base / 'one/accounting.json').read_bytes(), (base / 'two/accounting.json').read_bytes())
            summary = json.loads((base / 'one/summary.json').read_text())
            self.assertTrue(all(g['observations'] == 1 for g in summary['groups']))
            accounting = json.loads((base / 'one/accounting.json').read_text())
            self.assertEqual(sum(r['warmup'] for r in accounting), 8)
            manifest = json.loads((base / 'one/input-manifest.json').read_text())
            self.assertTrue(manifest['unchanged'])

    def v3(self):
        raw = []
        def add(ns, phase, edge='point', job=0, worker=0, prep=0, role='service_control'):
            raw.append(dict(event(ns, phase, edge), version=3, service=1, observation=1,
                            job=job, worker=worker, preparation=prep, role=role))
        add(0, 'startup_origin')
        add(1, 'construction_outer', 'begin')
        add(2, 'service_construction', 'begin')
        add(3, 'service_construction', 'end')
        add(4, 'construction_outer', 'end')
        add(4, 'construction_complete')
        add(5, 'preparation_schedule', worker=2, prep=3)
        add(6, 'pool_worker_prepare', 'begin', worker=2, prep=3, role='demand')
        add(7, 'helper_prepare', 'begin', worker=2, prep=3, role='demand')
        add(8, 'helper_prepare', 'end', worker=2, prep=3, role='demand')
        add(9, 'pool_worker_prepare', 'end', worker=2, prep=3, role='demand')
        add(10, 'preparation_ready', worker=2, prep=3)
        add(11, 'demand_dispatch', job=4, worker=5, role='demand')
        add(12, 'selected_worker', job=4, worker=2, prep=3, role='demand')
        add(13, 'pool_job', 'begin', job=4, worker=2, prep=3, role='demand')
        add(14, 'decode_exchange_including_transport', 'begin', job=4, worker=2, prep=3, role='demand')
        add(17, 'decode_exchange_including_transport', 'end', job=4, worker=2, prep=3, role='demand')
        add(18, 'pool_job', 'end', job=4, worker=2, prep=3, role='demand')
        add(15, 'pixels', job=4, worker=2, prep=3, role='demand')
        add(16, 'metadata', job=4, worker=2, prep=3, role='demand')
        return raw

    def test_v3_pre_demand_preparation_and_clipped_delivery_window(self):
        events, spans, errors = parse(self.v3())
        rows, issues, _ = a.account(events, spans, [{}], 'test.log', 'C')
        self.assertEqual(errors + issues, [])
        self.assertEqual(rows[0]['status'], 'associated')
        self.assertEqual(rows[0]['phases']['decode_exchange_including_transport']['union_ms'], 2 / 1e6)
        self.assertEqual(rows[0]['phases']['helper_prepare']['count'], 1)
        self.assertEqual(rows[0]['phase_absence']['generation_validation'], 'missing_or_ambiguous')

    def test_v3_invalid_claims_cannot_succeed(self):
        cases = (
            ('metadata', 'job', 0), ('metadata', 'job', 99),
            ('metadata', 'observation', 2), ('metadata', 'service', 0),
            ('metadata', 'ns', 14), ('selected_worker', 'preparation', 99),
            ('pool_job', 'worker', 0), ('preparation_ready', 'preparation', 0),
            ('helper_prepare', 'role', 'invented'), ('construction_complete', 'ns', 20),
        )
        for phase, key, value in cases:
            with self.subTest(phase=phase, key=key):
                raw = self.v3()
                for e in raw:
                    if e['phase'] == phase:
                        e[key] = value
                events, spans, errors = parse(raw)
                rows, issues, _ = a.account(events, spans, [{}], 'test.log', 'C')
                self.assertTrue(errors + issues)
                self.assertNotEqual(rows[0]['status'], 'associated')

    def test_v3_missing_duplicate_and_unpaired_records_are_partial(self):
        for phase in ('pixels', 'metadata', 'selected_worker', 'preparation_ready', 'preparation_schedule', 'construction_outer'):
            raw = [e for e in self.v3() if e['phase'] != phase]
            events, spans, errors = parse(raw)
            rows, issues, _ = a.account(events, spans, [{}], 'test.log', 'C')
            self.assertTrue(errors + issues)
            self.assertNotEqual(rows[0]['status'], 'associated')
        raw = self.v3()
        raw.append(dict(raw[-1]))
        events, spans, _ = parse(raw)
        rows, issues, _ = a.account(events, spans, [{}], 'test.log', 'C')
        self.assertTrue(issues)
        self.assertEqual(rows[0]['status'], 'partial')

    def test_absent_distribution_is_not_zero(self):
        self.assertIsNone(a.distribution([]))
        self.assertEqual(a.distribution(list(range(100)))['p95'], 94)


if __name__ == '__main__':
    unittest.main()
