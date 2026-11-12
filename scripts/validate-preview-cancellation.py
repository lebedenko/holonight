#!/usr/bin/env python3
"""Cancellation-specific ledger joins; deliberately does not use startup account()."""
import importlib.util
import json
from collections import defaultdict, deque
from pathlib import Path

spec = importlib.util.spec_from_file_location('startup_analysis', Path(__file__).with_name('analyze-preview-startup.py'))
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)
parse_trace = analysis.parse_trace
identity_issues = analysis.identity_issues
SCENARIOS = ('preparation', 'active', 'cleanup', 'destruction')


def validate(text, ledger, barriers, harness, process, scenario, source='trace'):
    events, spans, issues = parse_trace(text, source)
    issues += identity_issues(events, source)

    def need(condition, kind):
        if not condition:
            issues.append({'kind': kind})

    need(scenario in SCENARIOS, 'unknown_scenario')
    need(process.get('exit') == 0 and not process.get('timeout'), 'process_failure')
    need(bool(harness) and harness.get('success') is True and harness.get('scenario') == scenario and
         harness.get('services') == 1 and not harness.get('barrier_timeout') and not harness.get('cleanup_failure'), 'harness_failure')
    need(bool(events) and all(e.get('version') == 3 for e in events), 'requires_v3')
    constructions = [s for s in spans if s['phase'] == 'service_construction']
    destructions = [s for s in spans if s['phase'] == 'service_destruction']
    need(len(constructions) == len(destructions) == 1, 'single_balanced_lifetime')
    keys = {(s['begin']['pid'], s['begin'].get('service')) for s in constructions}
    need(len(keys) == 1 and all((e['pid'], e.get('service')) in keys for e in events), 'foreign_service')
    if len(constructions) == len(destructions) == 1:
        birth, death = constructions[0], destructions[0]
        need(birth['stop'] <= death['start'] <= death['stop'] and
             death['begin']['role'] == death['end']['role'] == 'shutdown', 'destruction_completion')
        need(all(birth['start'] <= s['start'] <= s['stop'] <= death['stop'] for s in spans if s['phase'] in ('pool_job', 'pool_worker_prepare', 'worker_cleanup', 'cleanup')), 'activity_outside_lifetime')
        need(all(s['begin']['role'] == s['end']['role'] == 'shutdown' and
                 birth['stop'] <= s['start'] <= s['stop'] <= death['stop']
                 for s in spans if s['phase'] == 'service_shutdown'), 'invalid_optional_shutdown')
    rows = sorted(ledger + barriers, key=lambda r: r.get('order', -1))
    required_fields = {'event', 'order', 'ns', 'pid', 'tid', 'version', 'service', 'observation', 'job', 'worker', 'preparation', 'role', 'selection'}
    need(bool(rows) and all(required_fields <= r.keys() for r in rows), 'diagnostic_schema')
    if not rows or not all(required_fields <= r.keys() for r in rows):
        return {'issues': issues, 'events': events, 'spans': spans, 'requests': []}
    need([r['order'] for r in rows] == list(range(1, len(rows)+1)) and
         all(a['ns'] <= b['ns'] for a, b in zip(rows, rows[1:])), 'diagnostic_order')
    need(all((r['pid'], r['service']) in keys and r['version'] == 3 for r in rows), 'foreign_diagnostic_service')

    def records(name, job=None):
        return [r for r in rows if r['event'] == name and (job is None or r['job'] == job)]

    submissions = records('submit')
    need(len(submissions) == 2 and len({r['job'] for r in submissions}) == 2 and
         all(r['job'] > 0 and r['selection'] > 0 and r.get('path') for r in submissions), 'two_explicit_requests')
    jobs = {r['job'] for r in submissions}
    need(all(not e['job'] or e['job'] in jobs for e in events) and
         all(not r['job'] or r['job'] in jobs for r in rows), 'foreign_job')
    need(not records('barrier_timeout'), 'barrier_timeout')
    gates = ['preparation'] if scenario == 'preparation' else ['active']
    if scenario == 'cleanup':
        gates.append('retirement')
    for gate in gates:
        hits, releases, resumes = (records(gate + suffix) for suffix in ('_reached', '_release', '_resumed'))
        need(len(hits) == len(releases) == len(resumes) == 1 and
             hits[0]['order'] < releases[0]['order'] < resumes[0]['order'], 'barrier_acknowledgement:' + gate)
    need(bool(records('retirement_complete')) and all(r.get('verified') is True for r in records('retirement_complete')) and
         all(r.get('cleanup_ok') is True for r in records('terminal') + records('preparation_terminal')),
         'unverified_cleanup')
    for retirement in records('retirement_complete'):
        need(any(s['phase'] == 'cleanup' and s['begin']['worker'] == retirement['worker'] and
                 s['begin']['preparation'] == retirement['preparation'] and
                 s['start'] <= retirement['ns'] <= s['stop'] for s in spans), 'cleanup_trace_join')
    request_rows = []
    for index, submit in enumerate(submissions):
        job = submit['job']
        selected = [e for e in events if e['phase'] == 'selected_worker' and e['job'] == job]
        executed = [s for s in spans if s['phase'] == 'pool_job' and s['begin']['job'] == job]
        dispatch = [s for s in spans if s['phase'] == 'demand_dispatch' and s['begin']['job'] == job]
        need(len(dispatch) == 1, 'dispatch_join')
        need(len(selected) == len(executed) <= 1, 'execution_selection_join')
        for selection in selected:
            prep = selection['preparation']
            matching = [e for e in events if (e['pid'], e['service'], e['worker'], e['preparation']) ==
                        (selection['pid'], selection['service'], selection['worker'], prep)]
            ready = [e for e in matching if e['phase'] == 'preparation_ready']
            need(prep > 0 and len(ready) == 1 and ready[0]['ns'] <= selection['ns'] and
                 any(s['begin']['worker'] == selection['worker'] and s['begin']['preparation'] == prep and
                     selection['ns'] <= s['start'] for s in executed), 'selected_preparation_linkage')
        # Join the observed handoffs without assigning a synthetic delivery identity.
        publications, attempts = defaultdict(deque), defaultdict(deque)
        delivery_keys = ('pid', 'service', 'observation', 'job', 'worker', 'preparation',
                         'selection', 'pixels', 'final', 'success')
        delivery_rows = [r for r in rows if r['job'] == job and
                         r['event'] in ('publication', 'application_attempt', 'accepted')]
        for r in delivery_rows:
            need(r['selection'] == submit['selection'], 'selection_join')
            valid = all(type(r.get(field)) is bool for field in ('pixels', 'final', 'success'))
            need(valid, 'delivery_schema')
            if not valid:
                continue
            key = tuple(r[field] for field in delivery_keys)
            if r['event'] == 'publication':
                publications[key].append(r)
            elif r['event'] == 'application_attempt':
                matched = bool(publications[key])
                need(matched, 'publication_attempt_join')
                if matched:
                    publication = publications[key].popleft()
                    need(publication['order'] < r['order'], 'publication_attempt_order')
                    attempts[key].append(r)
            else:
                matched = bool(attempts[key])
                need(matched, 'attempt_acceptance_join')
                if matched:
                    attempt = attempts[key].popleft()
                    need(attempt['order'] < r['order'] and attempt.get('current_selection') == r['selection'],
                         'accepted_selection_order')
                need(any(e['worker'] == r['worker'] and e['preparation'] == r['preparation']
                         for e in selected), 'accepted_worker_join')
                if len(destructions) == 1:
                    need(r['ns'] < destructions[0]['start'], 'acceptance_during_destruction')
        accepted = records('accepted', job)
        pixels = [r for r in accepted if r.get('pixels')]
        successful_pixels = [r for r in pixels if r.get('success') is True]
        final = [r for r in accepted if r.get('final') and r.get('success') is True]
        recovery = index == 1 and scenario != 'destruction'
        if recovery:
            need(len(executed) == 1 and bool(successful_pixels) and len(final) == 1 and
                 successful_pixels[0]['order'] < final[0]['order'] and harness.get('correct_pixels') is True and
                 harness.get('correct_metadata') is True, 'replacement_delivery')
            need(bool(records('terminal', job)), 'replacement_terminal')
        else:
            need(not pixels and not final, 'stale_accepted_delivery')
            if index == 0 and scenario != 'preparation':
                need(len(executed) == 1, 'primary_execution_required')
            if scenario == 'destruction' and index == 1:
                need(not executed and len(records('pending_destroyed', job)) == 1 and
                     records('pending_destroyed', job)[0].get('cancelled') is True, 'pending_destruction_terminal')
            elif index == 0 and scenario != 'preparation':
                # During shutdown completeJob callbacks can be suppressed by the pool's lifetime guard.
                need(bool(records('terminal', job)) or scenario == 'destruction', 'primary_terminal')
        request_rows.append({'submission': submit, 'selected': selected, 'execution': executed,
                             'accepted': accepted, 'outcome': 'recovery' if recovery else 'cancelled'})
    if len(submissions) == 2:
        primary, replacement = submissions
        pending = records('pending', primary['job'] if scenario == 'preparation' else replacement['job'])
        if scenario in ('preparation', 'cleanup', 'destruction'):
            need(len(pending) == 1, 'pending_acknowledgement')
        if scenario == 'preparation':
            cancelled = records('preparation_cancel_observed')
            ack = records('preparation_cancel_set')
            need(len(cancelled) == len(ack) == 1 and cancelled[0].get('cancelled') is True and
                 ack[0].get('cancelled') is True and ack[0]['preparation'] == cancelled[0]['preparation'] and
                 ack[0]['order'] < cancelled[0]['order'], 'preparation_cancel_acknowledgement')
            if cancelled:
                prep = cancelled[0]['preparation']
                owned = [e for e in events if e['preparation'] == prep]
                need(prep > 0 and len([s for s in spans if s['phase'] == 'pool_worker_prepare' and s['begin']['preparation'] == prep]) == 1 and
                     not any(e['phase'] in ('preparation_ready', 'selected_worker', 'helper_ready') for e in owned) and
                     not [r for r in records('gate_open') if r['preparation'] == prep], 'cancelled_preparation_lifecycle')
                retirements = [r for r in records('retirement_complete') if r['preparation'] == prep and r.get('launched')]
                terminals = [r for r in records('preparation_terminal') if r['preparation'] == prep]
                need(bool(retirements) and bool(terminals) and terminals[-1]['order'] < replacement['order'], 'preparation_cleanup_before_recovery')
        elif scenario == 'destruction':
            need(len(records('destructor_cancel')) == 1 and records('destructor_cancel')[0].get('cancelled') is True and
                 records('active_release') and records('destructor_cancel')[0]['order'] < records('active_release')[0]['order'], 'destructor_cancellation_acknowledgement')
        else:
            need(len(records('cancel')) == 1 and records('cancel')[0].get('cancelled') is True, 'active_cancel_acknowledgement')
            retirements = [r for r in records('retirement_complete', primary['job']) if r.get('launched') and
                           r['role'] == 'demand' and any(r['worker'] == e['worker'] and
                           r['preparation'] == e['preparation'] for e in request_rows[0]['selected'])]
            need(bool(retirements), 'primary_verified_retirement')
            if scenario == 'cleanup':
                entry = records('retirement_reached')
                release = records('retirement_release')
                need(bool(entry) and bool(release) and bool(pending) and
                     entry[0]['order'] < replacement['order'] <= pending[0]['order'] < release[0]['order'], 'replacement_during_cleanup')
            if retirements:
                need(all(s['start'] >= retirements[-1]['ns'] for s in spans if
                         s['phase'] == 'pool_job' and s['begin']['job'] == replacement['job']), 'replacement_before_retirement')
    return {'issues': issues, 'events': events, 'spans': spans, 'requests': request_rows,
            'standby': [e for e in events if e['role'] == 'standby'],
            'shutdown': [e for e in events if e['role'] == 'shutdown'],
            'lifecycles': {'construction': constructions, 'destruction': destructions,
                           'shutdown': [s for s in spans if s['phase'] == 'service_shutdown']}}


def load_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def validate_files(target, process, scenario):
    try:
        harness = json.loads(target.read_text())
        ledger = load_rows(Path(str(target) + '.ledger.jsonl'))
        barriers = load_rows(Path(str(target) + '.barriers.jsonl'))
    except (OSError, ValueError) as error:
        return {'issues': [{'kind': 'missing_or_invalid_json', 'reason': str(error)}]}
    return validate(target.with_suffix('.stderr').read_text() + '\n' + target.with_suffix('.stdout').read_text(),
                    ledger, barriers, harness, process, scenario, str(target))
