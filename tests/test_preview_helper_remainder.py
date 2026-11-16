import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


r = module('remainder_tests', 'report-preview-helper-remainder.py')
v = module('remainder_verifier_tests', 'verify-preview-helper-remainder.py')


def fixture(preparation=4):
    identity = dict(pid=10, tid=11, service=1, observation=1, job=2, worker=3, preparation=preparation)
    delivery = dict(identity, ns=100, transaction=5, publication=8)
    origin = dict(pid=10, service=1, observation=1, ns=0)
    def phase(name, start, stop, role='demand'):
        begin = dict(identity, phase=name, ns=start, role=role)
        if preparation is None:
            begin['preparation'] = 0
        return dict(phase=name, role=role, start=start, stop=stop, begin=begin, end=dict(begin, ns=stop))
    decode = phase('decode_exchange_including_transport', 40, 70)
    capture = phase('source_capture', -2, 20)
    setup = phase('runtime_validation', 1, 9, 'setup')
    standby = phase('runtime_validation', 1, 99, 'standby')
    envelope = phase('construction_outer', 0, 100, 'service_control')
    begin = dict(identity, ns=10)
    window = dict(begin=begin, end=dict(begin, ns=30), lifecycle_binding=dict(classification='demand', supplemental_after_legacy_ns=2))
    row = dict(sample=0, boundaries=dict(startup_origin=[origin]), timeline=[capture, setup, standby, envelope, decode], phase_absence={})
    account = dict(lifecycle=dict(accounting=[row]), windows=[window])
    e = dict(delivery=delivery, observation=1, arm='instrumented', variant='C', operations=[])
    previous = dict(start_ns=0, stop_ns=100, origin=origin, delivery=delivery,
                    groups=dict(selected_demand=dict(uncovered_intervals=[[0, 10], [30, 100]], uncovered_ns=80)),
                    variant='C', arm='instrumented', endpoint='pixels', block=0, warmup=False, invocation_index=0, observation=1, latency_ns=100)
    root = r.h.ROOT / 'build' / r.h.NAMES[0] / 'instrumented' / 'C'
    probes = [dict(file=str(root / 'source/test.cpp'), text='"' + name + '"') for name in ('source_capture', 'decode_exchange_including_transport')]
    return account, e, previous, probes


class RemainderTests(unittest.TestCase):
    def setUp(self):
        for name in ('subprocess.run', 'subprocess.Popen', 'os.system'):
            guard = patch(name, side_effect=AssertionError('process execution disabled'))
            guard.start()
            self.addCleanup(guard.stop)

    def test_nested_concurrent_clipped_disjoint_sets(self):
        spans = [dict(name='outer', start=-5, stop=15), dict(name='inner', start=2, stop=5), dict(name='concurrent', start=4, stop=20)]
        result = r.partition([[0, 10], [12, 22]], spans)
        self.assertEqual(sum(x['duration_ns'] for x in result), 20)
        self.assertIn(dict(start_ns=4, stop_ns=5, phases=['concurrent', 'inner', 'outer'], duration_ns=1), result)
        self.assertEqual(result[-1]['phases'], [])

    def test_independent_intersection(self):
        for parts, spans in (([[0, 10], [15, 20]], [[5, 18]]), ([], [[0, 1]]), ([[0, 1]], [[2, 3]])):
            self.assertEqual(r.intersect(parts, spans), v.intersection(parts, spans))

    def test_ties_disagreement_and_unmeasured_reject(self):
        cells = [dict(variant='C', arm='instrumented' if i < 16 else 'captured', endpoint='pixels' if i % 2 else 'metadata',
                      block=i % 5, selection='all', winners=['v3:runtime_validation']) for i in range(32)]
        accepted = r.decision(cells)
        v.check_decision(cells, accepted)
        self.assertEqual(accepted['active_phase_set'], 'v3:runtime_validation')
        for winners in (['v3:other'], ['unmeasured'], ['v3:runtime_validation', 'v3:other'], []):
            cells[0]['winners'] = winners
            result = r.decision(cells)
            self.assertEqual(result['decision'], 'Evidence insufficient')
            v.check_decision(cells, result)

    def test_empty_distribution_is_unavailable_not_zero(self):
        self.assertIsNone(r.stats([]))
        self.assertIsNone(v.distribution([]))
        self.assertEqual(r.stats([0])['median'], 0)

    def test_identity_bound_reconciliation_and_context(self):
        account, e, previous, probes = fixture()
        result = r.endpoint(account, e, previous, probes)
        self.assertEqual((result['remainder_ns'], result['explained_ns'], result['unmeasured_ns']), (80, 40, 40))
        self.assertEqual(result['inclusive']['v3:source_capture'], 10)
        self.assertEqual(len(result['context']), 3)
        self.assertEqual(result['helper_boundary_discrepancies'][0]['supplemental_after_legacy_ns'], 2)
        v.check_endpoint(account, e, previous, result, probes)
        result['explained_ns'] += 1
        with self.assertRaisesRegex(ValueError, 'arithmetic'):
            v.check_endpoint(account, e, previous, result, probes)

    def test_unavailable_preparation_is_preserved(self):
        account, e, previous, probes = fixture(None)
        result = r.endpoint(account, e, previous, probes)
        self.assertIsNone(result['delivery']['preparation'])
        self.assertEqual(result['decode_boundary']['begin']['preparation'], 0)
        v.check_endpoint(account, e, previous, result, probes)

    def test_foreign_worker_origin_and_boundaries_block(self):
        import copy
        for mutation in ('origin', 'preparation', 'boundary', 'decode', 'ambiguous_decode'):
            account, e, previous, probes = fixture()
            if mutation == 'origin':
                account['lifecycle']['accounting'][0]['boundaries']['startup_origin'][0]['service'] = 99
            elif mutation == 'preparation':
                account['windows'][0]['begin']['worker'] = 99
            elif mutation == 'boundary':
                account['lifecycle']['accounting'][0]['timeline'][0]['end']['worker'] = 99
            elif mutation == 'decode':
                account['lifecycle']['accounting'][0]['timeline'].pop()
            else:
                account['lifecycle']['accounting'][0]['timeline'].append(copy.deepcopy(account['lifecycle']['accounting'][0]['timeline'][-1]))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                r.endpoint(account, e, previous, probes)

    def test_review_remainder_tampering_blocks(self):
        account, e, previous, probes = fixture()
        previous['groups']['selected_demand']['uncovered_intervals'][0][1] += 1
        with self.assertRaisesRegex(ValueError, 'review remainder'):
            r.endpoint(account, e, previous, probes)

    def test_v4_envelopes_excluded_and_transaction_checked(self):
        account, e, previous, probes = fixture()
        identity = dict(e['delivery'], session=None, generation=None, span=6, endpoint='unavailable', publication=None)
        for operation in ('transaction_wrapper', 'retirement_call'):
            e['operations'].append(dict(operation=operation, start=0, stop=100, begin=dict(identity, ns=0), end=dict(identity, ns=100)))
        result = r.endpoint(account, e, previous, probes)
        self.assertEqual(result['explained_ns'], 40)
        self.assertEqual(len(result['context']), 5)
        v.check_endpoint(account, e, previous, result, probes)
        for edge in ('begin', 'end'):
            e['operations'][0][edge]['transaction'] = 999
        with self.assertRaisesRegex(ValueError, 'transaction identity'):
            r.endpoint(account, e, previous, probes)

    def test_input_drift_is_sealed_and_verification_rejects_it(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as directory:
            output = Path(directory) / 'result'
            with patch.object(r.b, 'bind', side_effect=ValueError('synthetic')), patch.object(r.h, 'recheck', return_value=False):
                result = r.report(output)
            self.assertEqual(result['failure'], 'input/tool drift')
            r.h.sealed(output)
            with self.assertRaisesRegex(ValueError, 'drift'):
                v.verify(output)

    def test_baseline_has_full_window_context(self):
        account, e, previous, probes = fixture()
        e['arm'] = previous['arm'] = 'baseline'
        for p in probes:
            p['file'] = p['file'].replace('/instrumented/', '/baseline/')
        result = r.endpoint(account, e, previous, probes)
        self.assertFalse(result['helper_partition_available'])
        self.assertEqual(result['remainder_ns'], 100)
        self.assertEqual(result['explained_ns'], 50)
        v.check_endpoint(account, e, previous, result, probes)

    def test_demand_lineage_rejects_foreign_worker_on_both_edges(self):
        account, e, previous, probes = fixture()
        for edge in ('begin', 'end'):
            account['lifecycle']['accounting'][0]['timeline'][0][edge]['worker'] = 999
        with self.assertRaisesRegex(ValueError, 'lineage'):
            r.endpoint(account, e, previous, probes)

    def test_selection_cutoff_and_nearest_median_ties(self):
        import copy
        account, e, previous, probes = fixture()
        base = r.endpoint(account, e, previous, probes)
        rows = []
        for i, latency in enumerate((1, 2, 3, 4, 4, 4)):
            row = copy.deepcopy(base)
            row.update(observation=i+1, latency_ns=latency)
            rows.append(row)
        accepted = []
        for selection, indices in (('all', range(6)), ('slowest', range(1, 6)), ('nearest_median', range(2, 6))):
            accepted.append(dict(variant='C', arm='instrumented', endpoint='pixels', block='pooled', selection=selection,
                                 members=[[0, i+1] for i in indices]))
        cells = r.summaries(rows, accepted)
        v.check_summaries(rows, cells, accepted)
        self.assertEqual(len(cells[2]['members']), 4)
        cells[1]['members'].pop()
        with self.assertRaisesRegex(ValueError, 'selection'):
            v.check_summaries(rows, cells, accepted)

    def test_zero_remainder_share_is_unavailable(self):
        account, e, previous, probes = fixture()
        row = r.endpoint(account, e, previous, probes)
        row.update(remainder_ns=0, explained_ns=0, unmeasured_ns=0, segments=[])
        accepted = [dict(variant='C', arm='instrumented', endpoint='pixels', block='pooled', selection='all', members=[[0, 1]])]
        cells = r.summaries([row], accepted)
        self.assertIsNone(cells[0]['shares']['explained_ns'])
        v.check_summaries([row], cells, accepted)

    def test_destination_must_be_disjoint(self):
        with self.assertRaisesRegex(ValueError, 'overlaps'):
            r.h.fresh(r.b.REVIEW / 'new-child', [r.b.REVIEW])

    def test_collision_and_sealed_failure(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as directory:
            output = Path(directory) / 'result'
            with patch.object(r.b, 'bind', side_effect=ValueError('synthetic binding failure')):
                result = r.report(output)
            self.assertEqual(result['status'], 'blocked')
            self.assertIn('synthetic', result['failure'])
            self.assertEqual(v.verify(output)['outcome'], 'blocked')
            with self.assertRaisesRegex(ValueError, 'collision'):
                r.report(output)
            (output / 'REPORT.md').write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'seal'):
                v.verify(output)


if __name__ == '__main__':
    unittest.main()
