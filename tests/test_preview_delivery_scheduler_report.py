import copy
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot_report', ROOT/'scripts/report-preview-delivery-scheduler.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name in ('subprocess.Popen', 'subprocess.run', 'subprocess.call', 'subprocess.check_call',
                     'subprocess.check_output', 'os.system', 'os.popen', 'os.posix_spawn',
                     'os.posix_spawnp', 'os.fork', 'os.execv', 'os.execve', 'os.spawnv', 'os.spawnve'):
            self.stack.enter_context(patch(name, side_effect=AssertionError('process launch forbidden')))

    def accounting(self, dual=True):
        e = dict(pid=10, tid=11, service=1, observation=1, job=2, worker=3,
                 preparation=None, generation=4, session=5, transaction=6,
                 publication=7, endpoint='final_result', ns=40)
        endpoints = [dict(endpoint='metadata', record=dict(e, operation='endpoint_metadata'))]
        if dual:
            endpoints.append(dict(endpoint='pixels', record=dict(e, operation='endpoint_pixels')))
        invoke = dict(operation='enqueue_call', begin=dict(e, ns=10, tid=12),
                      end=dict(e, ns=20, tid=12), start=10, stop=20)
        callback = dict(operation='callback_execution', begin=dict(e, ns=30),
                        end=dict(e, ns=50), start=30, stop=50)
        return dict(issues=[], assessment_available=True, spans=[invoke, callback],
                    windows=[dict(delivery=x['record'], endpoint=x['endpoint']) for x in endpoints],
                    handoffs=[dict(identity=e, endpoints=endpoints)])

    def test_dual_endpoint_predicates_use_identity_not_publication_label(self):
        rows = a.publication_rows(self.accounting(), 'one')
        self.assertEqual(len(rows), 1)
        self.assertEqual({e['endpoint'] for e in rows[0]['endpoints']}, {'pixels', 'metadata'})
        self.assertEqual(len(a.observations(rows, 1)), 1)
        rows[0]['observation_key'] = ('one', 1)
        summary = a.summaries(dict(pilot=rows))
        self.assertEqual([s['count'] for s in summary], [1, 1, 1])
        self.assertEqual(summary[-1]['endpoint_count'], 2)

    def test_publication_ids_are_invocation_local(self):
        one = a.publication_rows(self.accounting(), 'one')[0]
        two = a.publication_rows(self.accounting(), 'two')[0]
        for r in (one, two): r['observation_key'] = (r['invocation'], 1)
        summary = a.summaries(dict(pilot=[one, two]))
        self.assertEqual(summary[-1]['count'], 2)
        self.assertEqual(summary[-1]['observations'], 2)

    def test_distinct_overlapping_publications_remain_separate(self):
        report = self.accounting(False)
        other = self.accounting(False)
        # Same boundaries, separate publication and observation, no proximity join.
        def change(v):
            if isinstance(v, dict):
                if 'publication' in v: v.update(publication=8, observation=2)
                for x in v.values(): change(x)
            elif isinstance(v, list):
                for x in v: change(x)
        change(other)
        for key in ('spans', 'windows', 'handoffs'): report[key].extend(other[key])
        rows = a.publication_rows(report, 'one')
        self.assertEqual([r['identity']['publication'] for r in rows], [7, 8])
        self.assertEqual([r['invoke_return_to_callback_ns'] for r in rows], [10, 10])

    def test_duplicate_publications_endpoints_and_context_conflicts_block(self):
        for problem in ('handoff', 'window', 'context', 'span'):
            with self.subTest(problem=problem):
                report = self.accounting()
                if problem == 'handoff': report['handoffs'] *= 2
                if problem == 'window': report['windows'].append(copy.deepcopy(report['windows'][0]))
                if problem == 'context': report['windows'][0]['delivery']['session'] = 99
                if problem == 'span': report['spans'].append(copy.deepcopy(report['spans'][0]))
                with self.assertRaises(ValueError): a.publication_rows(report, 'one')

    def test_signed_callback_before_return_is_preserved(self):
        report = self.accounting()
        report['spans'][0].update(stop=45, end=dict(report['spans'][0]['end'], ns=45))
        row = a.publication_rows(report, 'one')[0]
        self.assertEqual(row['invoke_return_to_callback_ns'], -15)

    def scheduler_row(self):
        totals = dict(running=3, runnable=2, non_runnable=5, unknown=0)
        thread = dict(tid=12, complete=True, totals=totals,
                      intervals=[dict(start_ns=20, stop_ns=30)],
                      parts=dict(return_to_dispatch=dict(totals=dict(running=0, runnable=2, non_runnable=5, unknown=0)),
                                 dispatch_to_callback=dict(totals=dict(running=3, runnable=0, non_runnable=0, unknown=0))))
        return dict(identity=dict(tid=12), callback_entry=dict(tid=11),
                    invoke_return_to_callback_ns=10, invoke_return_to_dispatch_ns=7,
                    dispatch_to_callback_ns=3,
                    thread_accounting=[thread, dict(copy.deepcopy(thread), tid=11)])

    def test_both_threads_and_dispatch_splits_reconcile_without_summing_views(self):
        row = self.scheduler_row()
        a.reconcile(row)
        self.assertEqual([t['roles'] for t in row['thread_accounting']], [['publisher'], ['receiver']])
        self.assertEqual(sum(sum(t['totals'].values()) for t in row['thread_accounting']), 20)
        self.assertEqual(row['invoke_return_to_callback_ns'], 10)
        for problem in ('totals', 'parts', 'intervals', 'complete', 'thread', 'signed'):
            broken = copy.deepcopy(row)
            t = broken['thread_accounting'][0]
            if problem == 'totals': t['totals']['unknown'] = 1
            if problem == 'parts': t['parts']['dispatch_to_callback']['totals']['running'] = 4
            if problem == 'intervals': t['intervals'][0]['stop_ns'] = 29
            if problem == 'complete': t['complete'] = False
            if problem == 'thread': broken['thread_accounting'].pop()
            if problem == 'signed': broken['invoke_return_to_dispatch_ns'] = 8
            with self.subTest(problem=problem), self.assertRaises(ValueError): a.reconcile(broken)

    def test_ten_sample_nearest_rank_p95_and_all_tied_maxima(self):
        rows = []
        for i in range(1, 11):
            row = a.publication_rows(self.accounting(), 'one')[0]
            row.update(observation=i, observation_key=('one', i), invoke_return_to_callback_ns=min(i, 9))
            rows.append(row)
        summary = a.summaries(dict(pilot=rows))
        for s in summary:
            self.assertEqual((s['count'], s['minimum_ns'], s['median_ns'], s['p95_ns'], s['maximum_ns']), (10, 1, 5.5, 9, 9))
        self.assertEqual([(s['endpoint'], s['publication']['observation']) for s in a.selections(rows)],
                         [('pixels', 9), ('pixels', 10), ('metadata', 9), ('metadata', 10)])

    def test_negative_scheduler_window_is_empty_and_signed_boundaries_remain(self):
        row = self.scheduler_row()
        row.update(invoke_return_to_callback_ns=-3, invoke_return_to_dispatch_ns=-5, dispatch_to_callback_ns=2)
        for t in row['thread_accounting']:
            t.update(totals=dict.fromkeys(t['totals'], 0), intervals=[], parts={})
        a.reconcile(row)
        self.assertEqual(row['invoke_return_to_callback_ns'], -3)

    def failure_inputs(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT/'build')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        inputs = []
        for name in ('execution', 'normalized', 'analysis', 'historical'):
            path = root/name; path.mkdir()
            a.write(path/'assessment.json', dict(status='complete'))
            a.write(path/'integrity.json', dict(before={}, final_checks={}))
            a.o.seal(path)
            inputs.append(path)
        return inputs, root/'output'

    def test_bad_input_seal_produces_sealed_blocked_report(self):
        inputs, output = self.failure_inputs()
        (inputs[0]/'drift').write_text('tampered')
        result = a.report(*inputs, output)
        self.assertEqual(result['status'], 'blocked')
        self.assertIn('integrity drift', result['failure'])
        self.assertIn('No partial results', (output/'REPORT.md').read_text())
        a.o.check_output(output)

    def test_input_drift_preserves_first_error_and_seals_failure(self):
        inputs, output = self.failure_inputs()
        original = a.o.check_output
        def verify(path):
            original(path)
            if path == inputs[1]:
                (inputs[0]/'drift').write_text('changed during validation')
                raise ValueError('original validation failure')
        with patch.object(a.o, 'check_output', side_effect=verify):
            result = a.report(*inputs, output)
        self.assertEqual(result['failure'], 'original validation failure')
        self.assertEqual(result['integrity_failure'], 'input drift')
        self.assertFalse(a.read(output/'integrity.json')['passed'])
        a.o.check_output(output)

    def test_destination_reuse_and_overlap_are_rejected_before_writing(self):
        inputs, output = self.failure_inputs()
        output.mkdir()
        with self.assertRaises(ValueError): a.report(*inputs, output)
        self.assertEqual(list(output.iterdir()), [])
        with self.assertRaises(ValueError): a.report(*inputs, inputs[0]/'nested')

    def test_raw_citation_mismatch_blocks(self):
        inputs, _ = self.failure_inputs()
        path = inputs[0]/'raw'; path.write_text('original\n')
        ref = dict(file=str(path), line=1, text='original')
        self.assertEqual(a.raw_citations([ref])[0]['sha256'], a.o.digest(path))
        ref['text'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'text mismatch'): a.raw_citations(ref)


if __name__ == '__main__':
    unittest.main()
