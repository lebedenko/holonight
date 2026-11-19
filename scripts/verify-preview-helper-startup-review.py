#!/usr/bin/env python3
"""Independent offline decision arithmetic; never imports the assessment program."""
import argparse
from collections import defaultdict
import importlib.util
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('independent_review_evidence', Path(__file__).with_name('helper-startup-review-evidence.py'))
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)


def intervals(parts, bounds, excluded=()):
    """Independent endpoint sweep for union, clipping and set difference."""
    left, right = bounds
    points = sorted({left, right, *(max(left, min(right, p)) for part in [*parts, *excluded] for p in part)})
    output = []
    for start, stop in zip(points, points[1:]):
        if any(a <= start and stop <= b for a, b in parts) and not any(a <= start and stop <= b for a, b in excluded):
            if output and output[-1][1] == start:
                output[-1][1] = stop
            else:
                output.append([start, stop])
    return output


def length(parts):
    return sum(b-a for a, b in parts)


def distribution(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle-1] + ordered[middle]) / 2
    return dict(count=len(ordered), minimum=ordered[0], median=median,
                p95=ordered[math.ceil(len(ordered)*.95)-1], maximum=ordered[-1])


def scheduler_totals(span, parts, capture, timelines):
    e = span['begin']
    clock = capture['clock']
    h.require(capture['export_complete'] and not capture.get('diagnostics') and
              not any(row['kind'] == 'loss' for row in capture['events']), 'loss/incomplete scheduler export')
    h.require((e['clock'], e['host'], e['boot']) == (clock['name'], clock['provenance']['host'], clock['provenance']['boot_id']), 'scheduler provenance mismatch')
    tasks = [t for t in capture['tasks'] if t['key'][:2] == [e['pid'], e['tid']] and
             t['start_ns'] <= span['start'] and span['stop'] <= t['stop_ns']]
    h.require(len(tasks) == 1, 'ambiguous scheduler lifetime')
    task = tasks[0]
    for ns in (span['start'], span['stop']):
        h.require(any((r.get('invocation'), r.get('pid'), r.get('tid'), r.get('ns')) ==
                      (e['invocation'], e['pid'], e['tid'], ns) for r in task['identity_evidence']), 'scheduler identity mismatch')
    totals = dict.fromkeys(('running', 'runnable', 'non_runnable'), 0)
    for left, right in parts:
        cursor = left
        for row in timelines[tuple(task['key'])]:
            start, stop = max(left, row['start_ns']), min(right, row['stop_ns'])
            if start < stop:
                h.require(start == cursor and row['state'] in totals, 'scheduler gap/unknown state')
                totals[row['state']] += stop-start
                cursor = stop
        h.require(cursor == right, 'incomplete scheduler coverage')
    return totals


def check_endpoint(account, endpoint, saved, capture, timelines):
    delivered = endpoint['delivery']
    origins = [e for row in account['lifecycle']['accounting'] if row['sample'] == endpoint['observation']-1
               for e in row['boundaries']['startup_origin'] if all(e[k] == delivered[k] for k in ('pid', 'service', 'observation'))]
    h.require(len(origins) == 1, 'origin identity mismatch')
    start, stop = origins[0]['ns'], delivered['ns']
    h.require(start < stop and saved['start_ns'] == start and saved['stop_ns'] == stop and
              saved['latency_ns'] == stop-start and saved['origin'] == origins[0] and saved['delivery'] == delivered, 'startup window mismatch')
    for k in ('variant', 'arm', 'block', 'warmup', 'endpoint', 'invocation_index', 'observation', 'harness_latency_ns'):
        h.require(saved[k] == endpoint[k], 'endpoint context mismatch')
    sample = account['original_samples'][endpoint['observation']-1]
    h.require(endpoint['harness_latency_ns'] == sample['first_ms' if endpoint['endpoint'] == 'pixels' else 'final_ms']*1e6, 'harness latency mismatch')
    if endpoint['arm'] == 'baseline':
        h.require(not saved['groups'] and not saved['preparations'] and saved['supplemental'].startswith('unavailable'), 'baseline supplemental data')
        return
    expected = defaultdict(lambda: defaultdict(list))
    preparations = []
    all_spans = {(s['pid'], s['span']): s for s in account['spans']}
    for window in account['windows']:
        e = window['begin']
        kind = window['lifecycle_binding']['classification']
        same = all(e[k] == delivered[k] for k in ('pid', 'service', 'observation'))
        selected = all(e[k] == delivered[k] for k in ('pid', 'service', 'observation', 'worker', 'preparation'))
        if kind == 'demand':
            h.require(not same or selected, 'selected demand identity mismatch')
            if not selected:
                continue
            group = 'selected_demand'
        elif kind == 'standby':
            if not same:
                continue
            group = kind
        else:
            group = kind
        root = all_spans[e['pid'], window['root_span']]
        if max(start, root['start']) >= min(stop, root['stop']):
            continue
        if window['end']['outcome'] != 'returned':
            group = 'exceptional_' + group
        preparations.append(dict(group=group, identity={k: e[k] for k in h.IDENTITY}, root_span=window['root_span'], outcome=window['end']['outcome']))
        descendants = []
        for span in account['spans']:
            node = span
            seen = set()
            while node['parent'] is not None:
                key = (node['pid'], node['span'])
                h.require(key not in seen, 'cyclic span parent')
                seen.add(key)
                node = all_spans[node['pid'], node['parent']]
            if node is root:
                descendants.append(span)
        h.require([s for s in descendants if s is not root] == window['spans'], 'preparation span inventory mismatch')
        for span in descendants:
            children = [s for s in descendants if s['parent'] == span['span']]
            name = span['operation'] + ('.residual' if children else '')
            inside = intervals([(span['start'], span['stop'])], (start, stop))
            exclusive = intervals([(span['start'], span['stop'])], (start, stop), [(s['start'], s['stop']) for s in children])
            expected[group][name].append((span, inside, exclusive))
    h.require(saved['preparations'] == preparations and set(saved['groups']) == set(expected) and 'selected_demand' in expected, 'preparation accounting mismatch')
    for group, names in expected.items():
        actual = saved['groups'][group]
        h.require(set(actual['operations']) == set(names), 'operation inventory mismatch')
        coverage = []
        for name, spans in names.items():
            exclusive = intervals([p for _, _, ex in spans for p in ex], (start, stop))
            inclusive = intervals([p for _, inc, _ in spans for p in inc], (start, stop))
            metric = dict(intervals=exclusive, union_ns=length(exclusive), inclusive_union_ns=length(inclusive),
                          inclusive_sum_ns=sum(length(inc) for _, inc, _ in spans))
            if capture is not None and not group.startswith('exceptional_'):
                totals = dict.fromkeys(('running', 'runnable', 'non_runnable'), 0)
                for span, _, ex in spans:
                    if ex:
                        for state, ns in scheduler_totals(span, ex, capture, timelines).items():
                            totals[state] += ns
                metric['scheduler_task_ns'] = totals
            h.require(actual['operations'][name] == metric, 'operation interval/scheduler mismatch')
            coverage += exclusive
        uncovered = intervals([(start, stop)], (start, stop), coverage)
        h.require(actual['uncovered_intervals'] == uncovered and actual['uncovered_ns'] == length(uncovered), 'uncovered interval mismatch')


def check_summaries(rows, summary):
    expected_cells = {}
    keys = {(r['variant'], r['arm'], r['endpoint']) for r in rows}
    for key in keys:
        population = [r for r in rows if (r['variant'], r['arm'], r['endpoint']) == key]
        for block in ('pooled', *range(5)):
            expected_cells[(*key, block, 'all')] = [r for r in population if block == 'pooled' or r['block'] == block]
        if key[1] != 'baseline':
            latencies = sorted(r['latency_ns'] for r in population)
            median = statistics.median(latencies)
            closest = min(abs(ns-median) for ns in latencies)
            expected_cells[(*key, 'pooled', 'slowest')] = [r for r in population if r['latency_ns'] >= latencies[-5]]
            expected_cells[(*key, 'pooled', 'nearest_median')] = [r for r in population if abs(r['latency_ns']-median) == closest]
    h.require(len(summary) == len(expected_cells), 'summary inventory mismatch')
    seen = set()
    for cell in summary:
        key = tuple(cell[k] for k in ('variant', 'arm', 'endpoint', 'block', 'selection'))
        h.require(key not in seen and key in expected_cells, 'duplicate/foreign summary cell')
        seen.add(key)
        members = expected_cells[key]
        h.require(cell['members'] == [[r['invocation_index'], r['observation']] for r in members], 'selection/cutoff tie mismatch')
        for field in ('latency_ns', 'harness_latency_ns'):
            h.require(cell[field] == distribution([r[field] for r in members]), 'latency distribution mismatch')
        groups = {g for r in members for g in r['groups']}
        h.require(set(cell['groups']) == groups, 'summary group mismatch')
        for group in groups:
            saved = cell['groups'][group]
            names = {n for r in members for n in r['groups'].get(group, {}).get('operations', {})}
            h.require(set(saved['operations']) == names, 'summary operation mismatch')
            for name in names:
                values = [r['groups'].get(group, {}).get('operations', {}).get(name, {}) for r in members]
                expected = {field: distribution([v.get(field, 0) for v in values]) for field in ('union_ns', 'inclusive_union_ns', 'inclusive_sum_ns')}
                if cell['arm'] == 'captured' and not group.startswith('exceptional_'):
                    expected['scheduler_task_ns'] = {state: distribution([v.get('scheduler_task_ns', {}).get(state, 0) for v in values])
                                                     for state in ('running', 'runnable', 'non_runnable')}
                h.require(saved['operations'][name] == expected, 'operation distribution mismatch')
            ranking = sorted(names, key=lambda n: (-saved['operations'][n]['union_ns']['median'], n))
            winners = [n for n in ranking if saved['operations'][n]['union_ns']['median'] == saved['operations'][ranking[0]]['union_ns']['median']]
            h.require(saved['ranking'] == ranking and saved['winners'] == winners, 'ranking mismatch')
            h.require(saved['uncovered_ns'] == distribution([r['groups'].get(group, {}).get('uncovered_ns', r['latency_ns']) for r in members]), 'uncovered distribution mismatch')


def check_decision(summary, result):
    votes = []
    for cell in summary:
        if cell['variant'] == 'C' and cell['arm'] in ('captured', 'instrumented'):
            group = cell['groups'].get('selected_demand', {})
            winners = group.get('winners', [])
            candidate = winners[0] if len(winners) == 1 else None
            rejection = None
            if candidate is None:
                rejection = 'tied or missing operation ranking'
            elif candidate.endswith('.residual'):
                rejection = 'dominant parent-exclusive residual'
            elif group['uncovered_ns']['median'] >= group['operations'][candidate]['union_ns']['median']:
                rejection = 'dominant uncovered startup time'
            votes.append(dict(arm=cell['arm'], endpoint=cell['endpoint'], block=cell['block'], selection=cell['selection'], winners=winners, candidate=candidate, rejection=rejection))
    choices = {v['candidate'] for v in votes}
    agreed = len(votes) == 32 and len(choices) == 1 and None not in choices and all(v['rejection'] is None for v in votes)
    operation = choices.pop() if agreed else None
    h.require(result['votes'] == votes and result['operation'] == operation and result['decision'] ==
              ('Investigate ' + operation if agreed else 'Evidence insufficient'), 'decision mismatch')


def verify(output):
    h.sealed(output)
    integrity = h.read(output / 'integrity.json')
    h.require(integrity['passed'] and h.recheck(integrity['inventories'], integrity['files']), 'input/tool drift')
    for name, expected in integrity['files'].items():
        if Path(name).parent == h.ROOT / 'scripts' or Path(name).parent == h.ROOT / 'tests':
            h.require(h.digest(output / 'tools' / Path(name).name) == expected, 'tool snapshot drift')
    assessment = h.read(output / 'assessment.json')
    if assessment['status'] == 'blocked':
        h.require(assessment.get('failure') and assessment['decision'] == 'Evidence insufficient', 'blocked review lacks failure')
        return dict(status='passed', outcome='blocked', evidence_seal=h.digest(output / 'seal.json'))
    roots, before, files = h.bind_inputs()
    h.require(before == integrity['inventories'] and all(integrity['files'].get(k) == v for k, v in files.items()), 'input set mismatch')
    accounts = h.accounts(roots)
    measured, warmups = h.read(output / 'endpoints.json'), h.read(output / 'warmups.json')
    h.require(len(measured) == 300 and len(warmups) == 12, 'endpoint populations mismatch')
    saved_rows = {(r['invocation_index'], r['observation'], r['endpoint']): r for r in [*measured, *warmups]}
    h.require(len(saved_rows) == 312 and all(not r['warmup'] for r in measured) and all(r['warmup'] for r in warmups), 'duplicate endpoint/warmup leakage')
    for population, count in ((measured, 150), (warmups, 6)):
        observations = defaultdict(set)
        for row in population:
            observations[row['invocation_index'], row['observation']].add(row['endpoint'])
        h.require(len(observations) == count and all(kinds == {'pixels', 'metadata'} for kinds in observations.values()), 'observation/endpoint reconciliation mismatch')
    scheduler = h.module('independent_scheduler_reconstruction', 'analyze-preview-delivery-scheduler.py')
    required_tools = {Path(__file__), Path(__file__).with_name('assess-preview-helper-startup.py'),
                      h.ROOT / 'tests/test_preview_helper_startup_review.py', *h.tool_paths(h, scheduler)}
    h.require(all(integrity['files'].get(str(path)) == h.digest(path) for path in required_tools), 'missing consumed tool binding')
    registry = []
    for index, account in enumerate(accounts):
        capture, timelines = None, None
        if account['population']['arm'] == 'captured':
            capture = h.read(roots[2] / f'recording-{index:03}/scheduler.json')
            timelines, issues = scheduler.scheduler(capture, capture['clock'])
        for e in account['endpoints']:
            saved = saved_rows[index, e['observation'], e['endpoint']]
            check_endpoint(account, e, saved, capture, timelines)
            if capture is not None:
                h.require(saved['scheduler_global_issues'] == issues, 'global scheduler warning loss')
        registry.extend(dict(invocation_index=index, warmup=account['population']['warmup'], variant=account['variant'],
                             arm=account['population']['arm'], identity={k: w['begin'][k] for k in h.IDENTITY},
                             classification=w['lifecycle_binding']['classification'], outcome=w['end']['outcome'],
                             start_ns=w['begin']['ns'], stop_ns=w['end']['ns']) for w in account['windows'])
    h.require(registry == h.read(output / 'preparations.json'), 'preparation inventory mismatch')
    summary = h.read(output / 'distributions.json')
    check_summaries(measured, summary)
    effects = h.read(output / 'effects.json')
    expected_effects = []
    for variant in ('A', 'C'):
        for endpoint in ('pixels', 'metadata'):
            for left, right in (('baseline', 'instrumented'), ('instrumented', 'captured')):
                values, harness_values = [], []
                for block in range(5):
                    means = {c['arm']: c['latency_ns']['median'] for c in summary if
                             (c['variant'], c['endpoint'], c['block'], c['selection']) == (variant, endpoint, block, 'all')}
                    values.append(means[right]-means[left])
                    harness = {c['arm']: c['harness_latency_ns']['median'] for c in summary if
                               (c['variant'], c['endpoint'], c['block'], c['selection']) == (variant, endpoint, block, 'all')}
                    harness_values.append(harness[right]-harness[left])
                    expected_effects.append(dict(variant=variant, endpoint=endpoint, left=left, right=right, block=block,
                                                 signed_ns=values[-1], harness_signed_ns=harness_values[-1]))
                expected_effects.append(dict(variant=variant, endpoint=endpoint, left=left, right=right, block='block_medians', signed_ns=statistics.median(values), harness_signed_ns=statistics.median(harness_values)))
    h.require(effects == expected_effects, 'signed block median comparison mismatch')
    historical_effects = h.read(roots[3] / 'effects.json')
    h.require(len(effects) == len(historical_effects) and all(
        effect['harness_signed_ns'] == original['signed_block_median_difference_ns'] and
        all(effect[k] == original[k] for k in ('variant', 'endpoint', 'left', 'right', 'block'))
        for effect, original in zip(effects, historical_effects)), 'historical signed comparison drift')
    chosen = h.read(output / 'decision.json')
    check_decision(summary, chosen)
    h.require(assessment['decision'] == chosen['decision'] and (assessment['measured_observations'], assessment['endpoints'], assessment['warmup_observations']) == (150, 300, 6), 'assessment counts/decision mismatch')
    h.require(h.recheck(before, integrity['files']), 'input drift during verification')
    return dict(status='passed', outcome='complete', decision=chosen['decision'], measured_observations=150,
                endpoints=300, warmup_observations=6, evidence_seal=h.digest(output / 'seal.json'),
                imports_assessor=False, verifier_sha256=h.digest(Path(__file__)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    try:
        print(h.json.dumps(verify(args.evidence.absolute()), indent=2))
    except (ValueError, KeyError, OSError, TypeError, IndexError) as error:
        print(h.json.dumps(dict(status='blocked', failure=str(error)), indent=2))
        sys.exit(1)
