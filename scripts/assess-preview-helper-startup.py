#!/usr/bin/env python3
"""Offline operation decision review of the retained helper-startup diagnostic."""
import argparse
from collections import defaultdict
import importlib.util
import math
from pathlib import Path
import shutil
import statistics
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('review_evidence', Path(__file__).with_name('helper-startup-review-evidence.py'))
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)
a = h.module('review_span_analysis', 'analyze-preview-helper-startup.py')


def clip(parts, start, stop):
    return a.union((max(start, l), min(stop, r)) for l, r in parts)


def stats(values):
    values = sorted(values)
    return dict(count=len(values), minimum=values[0], median=statistics.median(values),
                p95=values[math.ceil(.95 * len(values)) - 1], maximum=values[-1])


def origin(account, endpoint):
    delivery = endpoint['delivery']
    rows = [row for row in account['lifecycle']['accounting'] if row['sample'] == endpoint['observation'] - 1]
    h.require(len(rows) == 1, 'missing/ambiguous observation')
    matches = [e for e in rows[0]['boundaries']['startup_origin'] if all(
        e[k] == delivery[k] for k in ('pid', 'service', 'observation'))]
    h.require(len(matches) == 1 and matches[0]['ns'] < delivery['ns'], 'missing/ambiguous startup origin')
    return matches[0]


def selected(window, endpoint):
    e, d = window['begin'], endpoint['delivery']
    return all(e[k] == d[k] for k in ('pid', 'service', 'observation', 'worker', 'preparation'))


def scheduler_parts(span, parts, capture, normalized):
    bound = a.scheduler_span(span, capture, (normalized[0], []))
    h.require(bound['available'], 'required scheduler coverage unavailable: ' + bound.get('reason', 'unknown'))
    totals = dict.fromkeys(('running', 'runnable', 'non_runnable'), 0)
    for l, r in parts:
        for row in bound['intervals']:
            left, right = max(l, row['start_ns']), min(r, row['stop_ns'])
            if left < right:
                h.require(row['state'] in totals, 'scheduler unknown state')
                totals[row['state']] += right - left
    h.require(sum(totals.values()) == a.duration(parts), 'scheduler gap')
    return totals


def endpoint_review(account, endpoint, capture=None, normalized=None):
    start, stop = origin(account, endpoint)['ns'], endpoint['delivery']['ns']
    result = {k: endpoint[k] for k in ('variant', 'arm', 'block', 'warmup', 'endpoint', 'invocation_index', 'observation', 'harness_latency_ns')}
    result.update(start_ns=start, stop_ns=stop, latency_ns=stop-start, origin=origin(account, endpoint),
                  delivery=endpoint['delivery'], groups={}, preparations=[])
    if endpoint['arm'] == 'baseline':
        result['supplemental'] = 'unavailable: baseline has no supplemental substeps'
        return result
    if capture is not None:
        h.require(capture.get('export_complete') is True and not capture.get('diagnostics') and
                  not any(e['kind'] == 'loss' for e in capture['events']), 'scheduler loss/incomplete export')
        result['scheduler_global_issues'] = normalized[1]
    buckets = defaultdict(lambda: defaultdict(list))
    for window in account['windows']:
        e = window['begin']
        kind = window['lifecycle_binding']['classification']
        same_observation = all(e[k] == endpoint['delivery'][k] for k in ('pid', 'service', 'observation'))
        if kind == 'demand' and same_observation:
            h.require(selected(window, endpoint), 'demand/endpoint identity mismatch')
        group = 'selected_demand' if kind == 'demand' and selected(window, endpoint) else kind
        if kind == 'demand' and group != 'selected_demand':
            continue
        if kind == 'standby' and not same_observation:
            continue
        if not clip([(e['ns'], window['end']['ns'])], start, stop):
            continue
        if window['end']['outcome'] != 'returned':
            group = 'exceptional_' + group
        result['preparations'].append(dict(group=group, identity={k: e[k] for k in h.IDENTITY},
            root_span=window['root_span'], outcome=window['end']['outcome']))
        root = next(s for s in account['spans'] if s['pid'] == e['pid'] and s['span'] == window['root_span'])
        spans = [root, *window['spans']]
        for span in spans:
            children = [s for s in spans if s['pid'] == span['pid'] and s['parent'] == span['span']]
            inclusive = clip([(span['start'], span['stop'])], start, stop)
            exclusive = clip(a.subtract(span['start'], span['stop'], [(s['start'], s['stop']) for s in children]), start, stop)
            name = span['operation'] + ('.residual' if children else '')
            buckets[group][name].append((span, inclusive, exclusive))
    h.require('selected_demand' in buckets, 'selected demand preparation missing')
    for group, names in sorted(buckets.items()):
        operations = {}
        covered = []
        for name, spans in sorted(names.items()):
            parts = a.union(p for _, _, exclusive in spans for p in exclusive)
            inclusive = a.union(p for _, inc, _ in spans for p in inc)
            covered.extend(parts)
            metric = dict(intervals=parts, union_ns=a.duration(parts), inclusive_union_ns=a.duration(inclusive),
                          inclusive_sum_ns=sum(a.duration(inc) for _, inc, _ in spans))
            if capture is not None and not group.startswith('exceptional_'):
                # Scheduler time is task-time; cross-thread overlap is not elapsed startup cost.
                totals = dict.fromkeys(('running', 'runnable', 'non_runnable'), 0)
                for span, _, exclusive in spans:
                    if exclusive:
                        for state, ns in scheduler_parts(span, exclusive, capture, normalized).items():
                            totals[state] += ns
                metric['scheduler_task_ns'] = totals
            operations[name] = metric
        uncovered = a.subtract(start, stop, covered)
        result['groups'][group] = dict(operations=operations, uncovered_intervals=uncovered,
                                      uncovered_ns=a.duration(uncovered))
    return result


def selections(rows):
    values = sorted(r['latency_ns'] for r in rows)
    median = statistics.median(values)
    distance = min(abs(v-median) for v in values)
    cutoff = values[-min(5, len(values))]
    return {'slowest': [r for r in rows if r['latency_ns'] >= cutoff],
            'nearest_median': [r for r in rows if abs(r['latency_ns']-median) == distance]}


def summaries(rows):
    cells = defaultdict(list)
    for row in rows:
        if row['warmup']:
            continue
        key = (row['variant'], row['arm'], row['endpoint'])
        for block in ('pooled', row['block']):
            cells[(*key, block, 'all')].append(row)
    for key in sorted({(r['variant'], r['arm'], r['endpoint']) for r in rows if not r['warmup'] and r['arm'] != 'baseline'}):
        population = [r for r in rows if not r['warmup'] and (r['variant'], r['arm'], r['endpoint']) == key]
        for selection, chosen in selections(population).items():
            cells[(*key, 'pooled', selection)] = chosen
    output = []
    for (variant, arm, endpoint, block, selection), members in sorted(cells.items(), key=lambda item: str(item[0])):
        cell = dict(variant=variant, arm=arm, endpoint=endpoint, block=block, selection=selection,
                    members=[[r['invocation_index'], r['observation']] for r in members],
                    latency_ns=stats([r['latency_ns'] for r in members]),
                    harness_latency_ns=stats([r['harness_latency_ns'] for r in members]), groups={})
        for group in sorted({g for r in members for g in r['groups']}):
            names = sorted({n for r in members for n in r['groups'].get(group, {}).get('operations', {})})
            operations = {}
            for name in names:
                metrics = [r['groups'].get(group, {}).get('operations', {}).get(name, {}) for r in members]
                operations[name] = {field: stats([m.get(field, 0) for m in metrics]) for field in
                                    ('union_ns', 'inclusive_union_ns', 'inclusive_sum_ns')}
                if arm == 'captured' and not group.startswith('exceptional_'):
                    operations[name]['scheduler_task_ns'] = {state: stats([m.get('scheduler_task_ns', {}).get(state, 0) for m in metrics])
                        for state in ('running', 'runnable', 'non_runnable')}
            ranking = sorted(names, key=lambda n: (-operations[n]['union_ns']['median'], n))
            top = operations[ranking[0]]['union_ns']['median'] if ranking else 0
            winners = [n for n in ranking if operations[n]['union_ns']['median'] == top]
            uncovered = stats([r['groups'].get(group, {}).get('uncovered_ns', r['latency_ns']) for r in members])
            cell['groups'][group] = dict(operations=operations, ranking=ranking, winners=winners, uncovered_ns=uncovered)
        output.append(cell)
    return output


def decision(summary):
    votes = []
    for cell in summary:
        if cell['variant'] != 'C' or cell['arm'] == 'baseline':
            continue
        group = cell['groups'].get('selected_demand', {})
        winners = group.get('winners', [])
        candidate = winners[0] if len(winners) == 1 else None
        reason = None
        if candidate is None:
            reason = 'tied or missing operation ranking'
        elif candidate.endswith('.residual'):
            reason = 'dominant parent-exclusive residual'
        elif group['uncovered_ns']['median'] >= group['operations'][candidate]['union_ns']['median']:
            reason = 'dominant uncovered startup time'
        votes.append(dict(arm=cell['arm'], endpoint=cell['endpoint'], block=cell['block'], selection=cell['selection'],
                          winners=winners, candidate=candidate, rejection=reason))
    priorities = {v['candidate'] for v in votes}
    agreed = len(votes) == 32 and len(priorities) == 1 and None not in priorities and not any(v['rejection'] for v in votes)
    return dict(decision='Investigate ' + next(iter(priorities)) if agreed else 'Evidence insufficient',
                operation=next(iter(priorities)) if agreed else None, votes=votes,
                limitation='Investigation only; no optimization benefit established. Qualification remains failed at 78/80.')


def review(output):
    roots = [h.ROOT / 'build' / name for name in h.NAMES]
    h.fresh(output, roots)
    result = dict(status='blocked', decision='Evidence insufficient')
    before, files = {}, {}
    try:
        (output / 'tools').mkdir()
        for path in sorted({Path(__file__), Path(__file__).with_name('verify-preview-helper-startup-review.py'),
                            h.ROOT / 'tests/test_preview_helper_startup_review.py', *h.tool_paths(h, a)}):
            files[str(path)] = h.digest(path)
            shutil.copy2(path, output / 'tools' / path.name)
        roots, before, consumed = h.bind_inputs()
        files.update(consumed)
        h.write(output / 'inputs.json', dict(inventories=before, files=files))
        accounts = h.accounts(roots)
        rows, registry = [], []
        for index, account in enumerate(accounts):
            capture, normalized = None, None
            if account['population']['arm'] == 'captured':
                capture = h.read(roots[2] / f'recording-{index:03}/scheduler.json')
                normalized = a.s.scheduler(capture, capture['clock'])
            registry.extend(dict(invocation_index=index, warmup=account['population']['warmup'],
                                 variant=account['variant'], arm=account['population']['arm'],
                                 identity={k: w['begin'][k] for k in h.IDENTITY},
                                 classification=w['lifecycle_binding']['classification'], outcome=w['end']['outcome'],
                                 start_ns=w['begin']['ns'], stop_ns=w['end']['ns']) for w in account['windows'])
            rows.extend(endpoint_review(account, e, capture, normalized) for e in account['endpoints'])
        h.write(output / 'endpoints.json', [r for r in rows if not r['warmup']])
        h.write(output / 'warmups.json', [r for r in rows if r['warmup']])
        h.write(output / 'preparations.json', registry)
        summary = summaries(rows)
        h.write(output / 'distributions.json', summary)
        # Signed descriptive block-median arm comparisons; no correction or quantile subtraction.
        effects = []
        for variant in ('A', 'C'):
            for endpoint in ('pixels', 'metadata'):
                for left, right in (('baseline', 'instrumented'), ('instrumented', 'captured')):
                    differences, harness_differences = [], []
                    for block in range(5):
                        cell = {c['arm']: c['latency_ns']['median'] for c in summary if
                                (c['variant'], c['endpoint'], c['block'], c['selection']) == (variant, endpoint, block, 'all')}
                        diff = cell[right] - cell[left]
                        differences.append(diff)
                        harness = {c['arm']: c['harness_latency_ns']['median'] for c in summary if
                                   (c['variant'], c['endpoint'], c['block'], c['selection']) == (variant, endpoint, block, 'all')}
                        harness_differences.append(harness[right] - harness[left])
                        effects.append(dict(variant=variant, endpoint=endpoint, left=left, right=right, block=block,
                                            signed_ns=diff, harness_signed_ns=harness_differences[-1]))
                    effects.append(dict(variant=variant, endpoint=endpoint, left=left, right=right, block='block_medians', signed_ns=statistics.median(differences), harness_signed_ns=statistics.median(harness_differences)))
        h.write(output / 'effects.json', effects)
        chosen = decision(summary)
        h.write(output / 'decision.json', chosen)
        result.update(status='complete', decision=chosen['decision'], measured_observations=150, endpoints=300, warmup_observations=6)
    except (ValueError, KeyError, TypeError, OSError, IndexError, StopIteration) as error:
        result['failure'] = str(error)
    finally:
        try:
            passed = h.recheck(before, files)
        except (OSError, ValueError):
            passed = False
        if not passed:
            result.update(status='blocked', failure='input/tool drift', decision='Evidence insufficient')
        h.write(output / 'integrity.json', dict(passed=passed, inventories=before, files=files))
        h.write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('# Offline helper-startup decision review\n\n' +
            result['status'] + ': ' + result['decision'] + '\n\n' + result.get('failure', '') +
            '\n\nNo optimization selected. Qualification remains failed at 78/80.\n')
        h.write(output / 'seal.json', h.inventory(output))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    value = review(args.output.absolute())
    print(h.json.dumps(value, indent=2))
    sys.exit(value['status'] != 'complete')
