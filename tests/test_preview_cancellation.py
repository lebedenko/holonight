"""Synthetic cancellation evidence; never invokes native helpers or retained workloads."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


v = load('cancel_validate', 'validate-preview-cancellation.py')
r = load('cancel_run', 'run-preview-cancellation.py')
p = load('cancel_prepare', 'prepare-preview-cancellation.py')
b = load('cancel_build', 'build-preview-cancellation.py')


class Evidence:
    def __init__(self, scenario):
        self.clock = 0
        self.events, self.ledger, self.barriers = [], [], []
        self.context = dict(version=3, pid=1, tid=1, service=1, observation=1, job=0, worker=0, preparation=0, role='service_control')
        self.scenario = scenario
        self.trace('service_construction', 'begin')
        self.trace('service_construction', 'end')
        self.submit(10, 100)
        self.context.update(job=0, worker=20, preparation=30, role='demand')
        self.trace('preparation_schedule')
        self.trace('pool_worker_prepare', 'begin')
        if scenario == 'preparation':
            self.diag('preparation_reached', barrier=True)
            self.context.update(job=10, worker=0, preparation=0)
            self.diag('pending')
            self.diag('cancel', cancelled=True)
            self.context.update(job=0, worker=20, preparation=30)
            self.diag('preparation_cancel_set', cancelled=True)
            self.diag('preparation_release', barrier=True)
            self.diag('preparation_resumed', barrier=True)
            self.diag('preparation_cancel_observed', cancelled=True)
            self.retire()
            self.trace('pool_worker_prepare', 'end')
            self.diag('preparation_terminal', cleanup_ok=True)
        else:
            self.trace('pool_worker_prepare', 'end')
            self.trace('preparation_ready')
            self.context.update(job=10)
            self.trace('selected_worker')
            self.trace('pool_job', 'begin')
            self.diag('active_reached', barrier=True)
            if scenario in ('active', 'cleanup'):
                self.diag('cancel', cancelled=True)
                self.diag('active_release', barrier=True)
                self.diag('active_resumed', barrier=True)
            if scenario == 'cleanup':
                self.diag('retirement_reached', barrier=True)
                self.submit(11, 101)
                self.diag('pending')
                self.context.update(job=10, worker=20, preparation=30)
                self.diag('retirement_release', barrier=True)
                self.diag('retirement_resumed', barrier=True)
            elif scenario == 'destruction':
                self.submit(11, 101)
                self.diag('pending')
                self.context.update(job=0, worker=0, preparation=0, role='shutdown')
                self.trace('service_destruction', 'begin')
                self.diag('destructor_cancel', cancelled=True)
                self.diag('active_release', barrier=True)
                self.context.update(job=10, worker=20, preparation=30, role='demand')
                self.diag('active_resumed', barrier=True)
            self.context.update(job=10, worker=20, preparation=30)
            self.retire()
            self.trace('pool_job', 'end')
            if scenario != 'destruction':
                self.diag('terminal', cancelled=True, cleanup_ok=True)
        if scenario != 'destruction':
            if scenario != 'cleanup':
                self.submit(11, 101)
            self.context.update(job=0, worker=21, preparation=31, role='demand')
            self.trace('preparation_schedule')
            self.trace('pool_worker_prepare', 'begin')
            self.trace('pool_worker_prepare', 'end')
            self.trace('preparation_ready')
            self.context.update(job=11)
            self.trace('selected_worker')
            self.trace('pool_job', 'begin')
            self.delivery(pixels=True, final=False)
            self.delivery(pixels=False, final=True)
            self.trace('pool_job', 'end')
            self.diag('terminal', cancelled=False, cleanup_ok=True)
            self.context.update(job=0, worker=0, preparation=0, role='shutdown')
            self.trace('service_destruction', 'begin')
        else:
            self.context.update(job=11, worker=0, preparation=0)
            self.diag('pending_destroyed', cancelled=True)
        self.context.update(job=0, worker=0, preparation=0, role='shutdown')
        self.trace('service_destruction', 'end')
        self.harness = dict(scenario=scenario, success=True, services=1, correct_pixels=True, correct_metadata=True)
        self.process = dict(exit=0, timeout=False)

    def trace(self, phase, edge='point'):
        self.clock += 10
        self.events.append(dict(self.context, ns=self.clock, request='diagnostic', object='0x1', slot=-1, phase=phase, edge=edge))

    def diag(self, event, selection=0, barrier=False, **fields):
        self.clock += 10
        row = dict(self.context, ns=self.clock, order=len(self.ledger)+len(self.barriers)+1, event=event, selection=selection, **fields)
        (self.barriers if barrier else self.ledger).append(row)

    def delivery(self, pixels, final):
        fields = dict(selection=101, pixels=pixels, final=final, success=True)
        self.diag('publication', **fields)
        self.diag('application_attempt', current_selection=101, **fields)
        self.diag('accepted', **fields)

    def submit(self, job, selection):
        self.context.update(job=job, worker=0, preparation=0, role='demand')
        self.trace('demand_dispatch', 'begin')
        self.diag('submit', selection=selection, path=f'/private/{selection}.png')
        self.trace('demand_dispatch', 'end')

    def retire(self):
        self.trace('cleanup', 'begin')
        self.diag('retirement_complete', verified=True, launched=True)
        self.trace('cleanup', 'end')

    def validate(self, suffix=''):
        text = '\n'.join('TRACE '+json.dumps(e) for e in self.events)+suffix
        return v.validate(text, self.ledger, self.barriers, self.harness, self.process, self.scenario)


class LedgerTests(unittest.TestCase):
    def test_four_valid_scenarios(self):
        for scenario in v.SCENARIOS:
            with self.subTest(scenario=scenario):
                self.assertEqual(Evidence(scenario).validate()['issues'], [])

    def test_supervisor_release_identity_and_order(self):
        for defect in ('zero_service', 'foreign_service', 'early_release'):
            with self.subTest(defect=defect):
                e = Evidence('destruction')
                release = next(row for row in e.barriers if row['event'] == 'active_release')
                if defect == 'early_release':
                    release['ns'] = next(row['ns'] for row in e.ledger if row['event'] == 'destructor_cancel') - 1
                else:
                    release['service'] = 0 if defect == 'zero_service' else 999
                self.reorder(e)
                self.assertTrue(e.validate()['issues'])

    def test_missing_acknowledgements(self):
        for scenario, missing in [('preparation', 'preparation_cancel_set'), ('active', 'active_release'),
                                  ('cleanup', 'pending'), ('destruction', 'destructor_cancel')]:
            with self.subTest(scenario=scenario):
                e = Evidence(scenario)
                e.ledger = [row for row in e.ledger if row['event'] != missing]
                e.barriers = [row for row in e.barriers if row['event'] != missing]
                self.assertTrue(e.validate()['issues'])

    def test_malformed_unpaired_and_missing_destruction(self):
        e = Evidence('active')
        self.assertTrue(e.validate('\nTRACE {')['issues'])
        for phase in ('pool_job', 'service_destruction', 'pool_worker_prepare', 'cleanup'):
            e = Evidence('active')
            e.events = [r for r in e.events if not(r['phase'] == phase and r['edge'] == 'end')]
            self.assertTrue(e.validate()['issues'])

    def test_preparation_linkage_and_foreign_attribution(self):
        for field, phase in [('preparation', 'selected_worker'), ('job', 'pool_job'), ('service', 'cleanup')]:
            e = Evidence('active')
            for event in e.events:
                if event['phase'] == phase:
                    event[field] = 999
            self.assertTrue(e.validate()['issues'])

    def test_stale_accepted_delivery_and_early_replacement(self):
        e = Evidence('cleanup')
        row = next(r for r in e.ledger if r['event'] == 'accepted')
        row.update(job=10, selection=100)
        self.assertTrue(e.validate()['issues'])
        e = Evidence('cleanup')
        retirement = next(r for r in e.ledger if r['event'] == 'retirement_complete')
        retirement['ns'] = next(t['ns']+1 for t in e.events if t['phase'] == 'pool_job' and t['edge'] == 'begin' and t['job'] == 11)
        self.assertIn('replacement_before_retirement', [i['kind'] for i in e.validate()['issues']])

    def test_nonzero_timeout_and_missing_json(self):
        for process in (dict(exit=7, timeout=False), dict(exit=0, timeout=True)):
            e = Evidence('active'); e.process = process
            self.assertTrue(e.validate()['issues'])
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(v.validate_files(Path(directory)/'missing.json', dict(exit=0), 'active')['issues'])

    def test_rejected_stale_attempt_is_permitted(self):
        e = Evidence('active')
        # A cancelled request may still have a queued callback that is rejected.
        first = next(i for i, row in enumerate(e.ledger) if row['event'] == 'publication')
        publication = dict(e.ledger[first], job=10, selection=100, worker=20, preparation=30)
        attempt = dict(e.ledger[first+1], job=10, selection=100, worker=20, preparation=30)
        e.ledger[first:first] = [publication, attempt]
        self.reorder(e)
        self.assertEqual(e.validate()['issues'], [])

    @staticmethod
    def reorder(e):
        rows = sorted(e.ledger + e.barriers, key=lambda row: row['ns'])
        for number, row in enumerate(rows, 1):
            row['order'] = number
        e.ledger.sort(key=lambda row: row['order'])
        e.barriers.sort(key=lambda row: row['order'])

    def test_metadata_only_final_requires_prior_successful_pixels(self):
        e = Evidence('active')
        final = next(row for row in e.ledger if row['event'] == 'accepted' and row['final'])
        self.assertFalse(final['pixels'])
        self.assertEqual(e.validate()['issues'], [])
        for failure in ('failed_final', 'missing_pixels', 'reversed', 'failed_pixels'):
            with self.subTest(failure=failure):
                e = Evidence('active')
                deliveries = [row for row in e.ledger if row['event'] in ('publication', 'application_attempt', 'accepted')]
                if failure == 'missing_pixels':
                    e.ledger = [row for row in e.ledger if row not in deliveries or row['final']]
                elif failure in ('failed_final', 'failed_pixels'):
                    for row in deliveries:
                        if row['final'] == (failure == 'failed_final'):
                            row['success'] = False
                else:
                    for row in deliveries:
                        row['ns'] += -40 if row['final'] else 40
                self.reorder(e)
                self.assertTrue(e.validate()['issues'])

    def test_delivery_requires_matching_publication_attempt_and_acceptance(self):
        for defect in ('missing_publication', 'missing_attempt', 'foreign_service', 'foreign_job',
                       'foreign_selection', 'foreign_worker', 'foreign_preparation', 'stale_selection', 'mismatched_payload'):
            with self.subTest(defect=defect):
                e = Evidence('active')
                row = next(row for row in e.ledger if row['event'] == 'application_attempt')
                if defect == 'missing_publication':
                    e.ledger.remove(next(row for row in e.ledger if row['event'] == 'publication'))
                elif defect == 'missing_attempt':
                    e.ledger.remove(row)
                elif defect.startswith('foreign_'):
                    row[defect.removeprefix('foreign_')] = 999
                elif defect == 'stale_selection':
                    row['current_selection'] = 999
                else:
                    row['final'] = True
                self.reorder(e)
                self.assertTrue(e.validate()['issues'])

    def test_standby_retirement_does_not_delay_replacement(self):
        e = Evidence('active')
        death = next(t for t in e.events if t['phase'] == 'service_destruction' and t['edge'] == 'begin')
        source = next(row for row in e.ledger if row['event'] == 'retirement_complete')
        retirement = dict(source, ns=death['ns']+1, worker=22, preparation=32, role='standby')
        e.ledger.append(retirement)
        context = dict(next(t for t in e.events if t['phase'] == 'cleanup'), worker=22, preparation=32, role='standby')
        e.events.extend([dict(context, ns=death['ns'], edge='begin'), dict(context, ns=death['ns']+2, edge='end')])
        self.reorder(e)
        self.assertEqual(e.validate()['issues'], [])

    def test_cancelled_preparation_cannot_claim_readiness(self):
        e = Evidence('preparation')
        event = next(t for t in e.events if t['phase'] == 'pool_worker_prepare' and t['edge'] == 'end')
        e.events.append(dict(event, phase='preparation_ready', edge='point'))
        self.assertTrue(e.validate()['issues'])


class RunnerTests(unittest.TestCase):
    def test_stops_before_next_invocation(self):
        calls = []
        def invoke(command, *args):
            calls.append(command)
            return dict(issues=[{'kind': 'failure'}], exit=1, timeout=False, scopes_isolated=True)
        result = {'invocations': []}
        with patch.object(r, 'invocation', invoke), self.assertRaises(RuntimeError):
            r.run_matrix([['one'], ['two']], ['active', 'active'], result, {}, {}, 1000)
        self.assertEqual(calls, [['one']])
        self.assertEqual(result['first_failing_command'], ['one'])

    def test_residual_scopes_fail_even_with_valid_observations(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'case.json'
            with patch.object(r.smoke, 'scope_snapshot', side_effect=[{'isolated': True}, {'isolated': False}]), \
                 patch.object(r.smoke, 'execute', return_value=dict(exit=0, timeout=False)), \
                 patch.object(r.validator, 'validate_files', return_value={'issues': []}):
                row = r.invocation(['harness', str(target)], 'active', {}, {}, 1000)
            self.assertFalse(row['scopes_isolated'])
            self.assertEqual(row['issues'], [{'kind': 'residual_scopes'}])

    def test_timeout_preserves_partial_stream_and_marks_cleanup_unverified(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'timeout.json'
            result = r.smoke.execute([sys.executable, '-c', 'import time; print("partial",flush=True); time.sleep(30)'], target, os.environ, {}, timeout=.1)
            self.assertTrue(result['timeout'])
            self.assertFalse(result['cleanup_verified'])
            self.assertIn('partial', target.with_suffix('.stdout').read_text())

    def test_changed_input_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'input'; path.write_text('original')
            expected = {'input': r.smoke.digest(path)}
            path.write_text('changed')
            with self.assertRaises(ValueError):
                r.smoke.verify_hashes(path.parent, expected)

    def test_exclusive_destination_and_marker_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with self.assertRaises(ValueError):
                p.prepare(path/'retained', path/'fixtures', path)
            (path/'execution-started.json').write_text('{}')
            with patch.object(r.os, 'geteuid', return_value=0), self.assertRaises(FileExistsError):
                r.run(type('Args', (), dict(package=path, uid=1000))())

    def test_build_and_seal_reject_marker_or_changed_prepared_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            (package/'trace.h').write_text('frozen')
            manifest = dict(tool_inputs={}, private_inputs={'trace.h': r.smoke.digest(package/'trace.h')})
            (package/'trace.h').write_text('changed')
            with self.assertRaises(ValueError):
                b.verify_inputs(package, manifest)
            (package/'execution-started.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'execution already started'):
                b.seal(package, manifest)

    def test_missing_or_duplicate_overlay_anchor_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'source.cpp'
            for text in ('missing', 'anchor anchor'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    p.replace(path, 'anchor', 'probe')
                self.assertEqual(path.read_text(), text)


if __name__ == '__main__':
    unittest.main()
