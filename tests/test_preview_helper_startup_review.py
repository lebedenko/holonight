import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


r = module('assessment_test', 'assess-preview-helper-startup.py')
v = module('independent_assessment_test', 'verify-preview-helper-startup-review.py')


def span(number, operation, start, stop, parent=None, preparation=4, worker=3):
    e = dict(pid=10, tid=11, service=1, observation=1, job=2, worker=worker, preparation=preparation,
             invocation='test', host='host', boot='boot', clock='CLOCK_MONOTONIC', ns=start)
    return dict(pid=10, span=number, operation=operation, parent=parent, start=start, stop=stop,
                begin=e, end=dict(e, ns=stop, outcome='returned'))


def fixture(preparation=4):
    root = span(1, 'preparation', 10, 90, preparation=preparation)
    parent = span(2, 'session_readiness', 20, 80, 1, preparation)
    leaf = span(3, 'session_readiness_payload_receive', 30, 70, 2, preparation)
    window = dict(begin=root['begin'], end=root['end'], root_span=1, spans=[parent, leaf],
                  lifecycle_binding=dict(classification='demand'))
    origin = dict(pid=10, service=1, observation=1, ns=0)
    delivery = dict(pid=10, service=1, observation=1, worker=3, preparation=preparation, ns=100)
    endpoint = dict(variant='C', arm='instrumented', block=0, warmup=False, endpoint='pixels',
                    invocation_index=0, observation=1, harness_latency_ns=100, delivery=delivery)
    account = dict(spans=[root, parent, leaf], windows=[window], original_samples=[dict(first_ms=.0001)],
                   lifecycle=dict(accounting=[dict(sample=0, boundaries=dict(startup_origin=[origin]))]))
    return account, endpoint


def capture_for(account):
    identity = [dict(invocation='test', pid=10, tid=11, ns=n) for n in (10, 90, 20, 80, 30, 70)]
    task = dict(key=[10, 11, 0], start_ns=0, stop_ns=110, initial='running', cpu=0, identity_evidence=identity)
    return dict(version=2, clock=dict(name='CLOCK_MONOTONIC', provenance=dict(host='host', boot_id='boot')),
                start_ns=0, stop_ns=110, tasks=[task], events=[], export_complete=True, diagnostics=[])


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.guards = [patch('subprocess.run', side_effect=AssertionError('process execution disabled')),
                       patch('subprocess.Popen', side_effect=AssertionError('process execution disabled')),
                       patch('os.system', side_effect=AssertionError('process execution disabled'))]
        for guard in self.guards:
            guard.start()
            self.addCleanup(guard.stop)

    def test_nested_spans_are_disjoint_and_clipped(self):
        account, endpoint = fixture()
        endpoint['delivery']['ns'] = 60
        result = r.endpoint_review(account, endpoint)
        group = result['groups']['selected_demand']
        self.assertEqual({k: m['union_ns'] for k, m in group['operations'].items()},
                         {'preparation.residual': 10, 'session_readiness.residual': 10,
                          'session_readiness_payload_receive': 30})
        self.assertEqual(group['uncovered_ns'], 10)
        self.assertEqual(group['operations']['session_readiness.residual']['inclusive_union_ns'], 40)
        v.check_endpoint(account, endpoint, result, None, None)
        result['groups']['selected_demand']['operations']['session_readiness.residual']['union_ns'] += 1
        with self.assertRaisesRegex(ValueError, 'interval/scheduler'):
            v.check_endpoint(account, endpoint, result, None, None)

    def test_unavailable_A_preparation_id_is_identity_not_proximity(self):
        account, endpoint = fixture(None)
        endpoint['variant'] = 'A'
        result = r.endpoint_review(account, endpoint)
        self.assertIsNone(result['preparations'][0]['identity']['preparation'])
        endpoint['delivery']['worker'] = 99
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            r.endpoint_review(account, endpoint)

    def test_missing_or_ambiguous_origin_rejected(self):
        account, endpoint = fixture()
        origin = account['lifecycle']['accounting'][0]['boundaries']['startup_origin'][0]
        origin['service'] = 100
        with self.assertRaisesRegex(ValueError, 'startup origin'):
            r.endpoint_review(account, endpoint)
        origin['service'] = 1
        account['lifecycle']['accounting'][0]['boundaries']['startup_origin'].append(origin.copy())
        with self.assertRaisesRegex(ValueError, 'startup origin'):
            r.endpoint_review(account, endpoint)

    def test_multiple_preparations_setup_standby_and_exception_are_separate(self):
        account, endpoint = fixture()
        original = copy.deepcopy(account['windows'][0])
        for offset, kind, exceptional in ((10, 'setup', True), (20, 'standby', False), (30, 'demand', False)):
            window = copy.deepcopy(original)
            window['root_span'] += offset
            for s in window['spans']:
                s['span'] += offset
                s['parent'] += offset
            for e in (window['begin'], window['end']):
                if kind != 'demand':
                    e['worker'] = offset
                    e['preparation'] = offset
            window['lifecycle_binding']['classification'] = kind
            window['end']['outcome'] = 'exception' if exceptional else 'returned'
            root = span(1+offset, 'preparation', 10, 90, preparation=window['begin']['preparation'], worker=window['begin']['worker'])
            root['begin'] = window['begin']
            root['end'] = window['end']
            account['spans'].extend([root, *window['spans']])
            account['windows'].append(window)
        result = r.endpoint_review(account, endpoint)
        self.assertEqual(len(result['preparations']), 4)
        self.assertEqual(set(result['groups']), {'selected_demand', 'standby', 'exceptional_setup'})
        self.assertEqual(result['groups']['selected_demand']['operations']['session_readiness_payload_receive']['union_ns'], 40)
        self.assertEqual(result['groups']['selected_demand']['operations']['session_readiness_payload_receive']['inclusive_sum_ns'], 80)

    def test_baseline_keeps_latency_without_substeps(self):
        account, endpoint = fixture()
        endpoint['arm'] = 'baseline'
        result = r.endpoint_review(account, endpoint)
        self.assertEqual(result['latency_ns'], 100)
        self.assertEqual(result['groups'], {})
        v.check_endpoint(account, endpoint, result, None, None)

    def test_scheduler_intersects_exact_same_exclusive_intervals(self):
        account, endpoint = fixture()
        endpoint['arm'] = 'captured'
        capture = capture_for(account)
        normalized = r.a.s.scheduler(capture, capture['clock'])
        result = r.endpoint_review(account, endpoint, capture, normalized)
        metric = result['groups']['selected_demand']['operations']['session_readiness_payload_receive']
        self.assertEqual(metric['scheduler_task_ns'], dict(running=40, runnable=0, non_runnable=0))
        v.check_endpoint(account, endpoint, result, capture, normalized[0])

    def test_unrelated_scheduler_warnings_retained(self):
        account, endpoint = fixture()
        endpoint['arm'] = 'captured'
        capture = capture_for(account)
        timelines, _ = r.a.s.scheduler(capture, capture['clock'])
        result = r.endpoint_review(account, endpoint, capture, (timelines, ['unrelated startup warning']))
        self.assertEqual(result['scheduler_global_issues'], ['unrelated startup warning'])

    def test_scheduler_gaps_unknown_loss_and_incomplete_export_rejected(self):
        for failure in ('gap', 'unknown', 'loss', 'export', 'identity', 'lifetime'):
            with self.subTest(failure=failure):
                account, endpoint = fixture()
                endpoint['arm'] = 'captured'
                capture = capture_for(account)
                timelines, issues = r.a.s.scheduler(capture, capture['clock'])
                if failure == 'gap':
                    timelines[(10, 11, 0)][0]['stop_ns'] = 40
                elif failure == 'unknown':
                    timelines[(10, 11, 0)][0]['state'] = 'unknown'
                elif failure == 'loss':
                    capture['events'].append(dict(kind='loss'))
                elif failure == 'export':
                    capture['export_complete'] = False
                elif failure == 'identity':
                    capture['tasks'][0]['identity_evidence'][0]['invocation'] = 'other'
                else:
                    capture['tasks'].append(copy.deepcopy(capture['tasks'][0]))
                with self.assertRaises(ValueError):
                    r.endpoint_review(account, endpoint, capture, (timelines, issues))

    def test_slowest_cutoff_ties_and_all_nearest_median(self):
        rows = [dict(latency_ns=n, observation=i) for i, n in enumerate([1, 2, 3, 4, 4, 4, 8, 9])]
        selected = r.selections(rows)
        self.assertEqual([r['latency_ns'] for r in selected['slowest']], [4, 4, 4, 8, 9])
        self.assertEqual(len(selected['nearest_median']), 3)
        rows = [dict(latency_ns=n) for n in [1, 2, 2, 2, 2, 2, 3]]
        self.assertEqual(len(r.selections(rows)['slowest']), 6)
        self.assertEqual([r['latency_ns'] for r in r.selections([dict(latency_ns=n) for n in [1, 2, 4, 5]])['nearest_median']], [2, 4])

    def decision_summary(self):
        cells = []
        for arm in ('instrumented', 'captured'):
            for endpoint in ('pixels', 'metadata'):
                for block, selection in [(b, 'all') for b in ('pooled', *range(5))] + [('pooled', s) for s in ('slowest', 'nearest_median')]:
                    cells.append(dict(variant='C', arm=arm, endpoint=endpoint, block=block, selection=selection,
                        groups=dict(selected_demand=dict(winners=['wait_for_started'], uncovered_ns=dict(median=10),
                        operations=dict(wait_for_started=dict(union_ns=dict(median=30)))))))
        return cells

    def test_unanimity_required_across_all_32_views(self):
        cells = self.decision_summary()
        result = r.decision(cells)
        self.assertEqual(result['decision'], 'Investigate wait_for_started')
        v.check_decision(cells, result)
        for mutation in ('disagreement', 'tie', 'uncovered', 'residual', 'missing'):
            changed = copy.deepcopy(cells)
            group = changed[0]['groups']['selected_demand']
            if mutation == 'disagreement':
                group['winners'] = ['process_start']
                group['operations']['process_start'] = dict(union_ns=dict(median=30))
            elif mutation == 'tie':
                group['winners'].append('process_start')
            elif mutation == 'uncovered':
                group['uncovered_ns']['median'] = 30
            elif mutation == 'residual':
                group['winners'] = ['preparation.residual']
                group['operations']['preparation.residual'] = dict(union_ns=dict(median=40))
            else:
                changed.pop()
            decision = r.decision(changed)
            self.assertEqual(decision['decision'], 'Evidence insufficient')
            v.check_decision(changed, decision)

    def test_independent_union_difference_handles_overlap_and_clipping(self):
        self.assertEqual(v.intervals([(-5, 8), (3, 12), (15, 25)], (0, 20), [(4, 6), (10, 17)]), [[0, 4], [6, 10], [17, 20]])

    def test_summary_distributions_selections_and_tampering(self):
        account, endpoint = fixture()
        base = r.endpoint_review(account, endpoint)
        rows = []
        for variant in ('A', 'C'):
            for arm in ('baseline', 'instrumented', 'captured'):
                for endpoint_name in ('pixels', 'metadata'):
                    for block in range(5):
                        for observation in range(2):
                            row = copy.deepcopy(base)
                            row.update(variant=variant, arm=arm, endpoint=endpoint_name, block=block,
                                       invocation_index=block, observation=observation, latency_ns=100+block)
                            if arm == 'baseline':
                                row['groups'] = {}
                            rows.append(row)
        summary = r.summaries(rows)
        v.check_summaries(rows, summary)
        changed = copy.deepcopy(summary)
        changed[0]['latency_ns']['median'] += 1
        with self.assertRaisesRegex(ValueError, 'distribution'):
            v.check_summaries(rows, changed)
        changed = copy.deepcopy(summary)
        cell = next(c for c in changed if c['selection'] == 'slowest')
        cell['members'].pop()
        with self.assertRaisesRegex(ValueError, 'selection/cutoff'):
            v.check_summaries(rows, changed)

    def test_seal_rejects_drift_and_inventory_additions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'raw').write_text('original')
            r.h.write(root / 'seal.json', r.h.inventory(root))
            r.h.sealed(root)
            (root / 'extra').write_text('untracked')
            with self.assertRaisesRegex(ValueError, 'seal/inventory'):
                r.h.sealed(root)

    def test_destination_collision_preserves_existing_files(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp:
            output = Path(tmp)
            (output / 'keep').write_text('original')
            with self.assertRaisesRegex(ValueError, 'collision'):
                r.review(output)
            self.assertEqual((output / 'keep').read_text(), 'original')

    def test_destination_overlap_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'overlaps'):
                r.h.fresh(root / 'new', [root])
            self.assertFalse((root / 'new').exists())

    def test_input_drift_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'evidence').write_text('before')
            before = {str(root): r.h.inventory(root)}
            self.assertTrue(r.h.recheck(before, {}))
            (root / 'evidence').write_text('after')
            self.assertFalse(r.h.recheck(before, {}))

    def test_blocked_results_are_sealed_and_partial_evidence_preserved(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'build') as tmp:
            output = Path(tmp) / 'review'
            with patch.object(r.h, 'bind_inputs', side_effect=ValueError('synthetic missing evidence')):
                result = r.review(output)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(result['failure'], 'synthetic missing evidence')
            self.assertTrue((output / 'tools/assess-preview-helper-startup.py').exists())
            r.h.sealed(output)
            self.assertEqual(v.verify(output)['outcome'], 'blocked')


if __name__ == '__main__':
    unittest.main()
