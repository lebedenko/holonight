#!/usr/bin/env python3
"""Explain review 03's retained startup remainder without executing workloads."""
import argparse
from collections import defaultdict
import importlib.util
import math
from pathlib import Path
import shutil
import statistics
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('remainder_boundary', Path(__file__).with_name('helper-startup-remainder-evidence.py'))
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h


def source_probes(probes, root, name):
    return [p for p in probes if p['file'].startswith(str(root) + '/') and '"' + name + '"' in p['text']]

a = h.module('remainder_intervals', 'analyze-preview-helper-startup.py')
v3 = h.module('remainder_v3', 'analyze-preview-startup.py')
EXCLUDED = ('transaction_wrapper', 'retirement_call')
COARSE = ('pre_decode', 'decode_exchange', 'post_decode')


def union(parts):
    return a.union(parts)


def intersect(left, right):
    return union((max(l, x), min(r, y)) for l, r in left for x, y in right)


def duration(parts):
    return sum(r-l for l, r in parts)


def stats(values):
    values = sorted(values)
    if not values:
        return None
    return dict(count=len(values), minimum=values[0], median=statistics.median(values),
                p95=values[math.ceil(.95*len(values))-1], maximum=values[-1])


def partition(remainder, phases):
    output = []
    for left, right in remainder:
        points = sorted({left, right, *(max(left, min(right, p)) for s in phases for p in (s['start'], s['stop']))})
        for start, stop in zip(points, points[1:]):
            names = sorted({s['name'] for s in phases if s['start'] <= start and stop <= s['stop']})
            output.append(dict(start_ns=start, stop_ns=stop, phases=names, duration_ns=stop-start))
    return output


def endpoint(account, e, previous, probes):
    d = e['delivery']
    rows = [r for r in account['lifecycle']['accounting'] if r['sample'] == e['observation']-1]
    h.require(len(rows) == 1, 'ambiguous observation')
    row = rows[0]
    origins = [x for x in row['boundaries']['startup_origin'] if all(x[k] == d[k] for k in ('pid', 'service', 'observation'))]
    h.require(len(origins) == 1, 'origin identity mismatch')
    start, stop = origins[0]['ns'], d['ns']
    h.require((start, stop) == (previous['start_ns'], previous['stop_ns']) and origins[0] == previous['origin'] and
              d == previous['delivery'], 'review window mismatch')
    roots = []
    discrepancies = []
    for w in account['windows']:
        if w['lifecycle_binding']['classification'] != 'demand':
            continue
        if all(w['begin'][k] == d[k] for k in ('pid', 'service', 'observation')):
            h.require(all(w['begin'][k] == d[k] for k in ('worker', 'preparation')), 'selected preparation mismatch')
            roots.append((w['begin']['ns'], w['end']['ns']))
            discrepancies.append(w['lifecycle_binding'])
    if e['arm'] == 'baseline':
        remainder = [[start, stop]]
    else:
        h.require(roots, 'missing selected preparation')
        remainder = a.subtract(start, stop, roots)
        h.require(remainder == previous['groups']['selected_demand']['uncovered_intervals'] and
                  duration(remainder) == previous['groups']['selected_demand']['uncovered_ns'], 'review remainder mismatch')
    phases, context = [], []
    for s in row['timeline']:
        x, y = s['begin'], s['end']
        h.require(all(x[k] == y[k] for k in ('pid', 'tid', 'service', 'observation', 'job', 'worker', 'preparation', 'role')),
                  'v3 boundary identity mismatch')
        h.require(all(x[k] == d[k] for k in ('pid', 'service', 'observation')), 'v3 ownership mismatch')
        # The observation's recorded dispatch/selection lifecycle owns precursor
        # demand IDs too; service-control has explicit zero worker/job identities.
        eligible = s['role'] in ('demand', 'service_control') and s['phase'] in v3.PHASES and s['phase'] != 'helper_prepare'
        if eligible and s['role'] == 'demand':
            identities = {tuple(d[k] or 0 for k in ('job', 'worker', 'preparation'))}
            identities.update(tuple(t['begin'][k] for k in ('job', 'worker', 'preparation')) for t in row['timeline']
                              if t['phase'] == 'demand_dispatch' and t['role'] == 'demand')
            h.require(tuple(x[k] for k in ('job', 'worker', 'preparation')) in identities, 'v3 demand lineage mismatch')
        if eligible and s['role'] == 'service_control':
            h.require(all(x[k] == 0 for k in ('job', 'worker', 'preparation')), 'service-control identity mismatch')
        item = dict(s, name='v3:' + s['phase'], ownership=s['role'])
        (phases if eligible else context).append(item)
    for s in e['operations']:
        x, y = s['begin'], s['end']
        keys = ('pid', 'tid', 'service', 'observation', 'job', 'worker', 'preparation', 'transaction', 'publication', 'session', 'generation', 'span', 'endpoint')
        h.require(all(x[k] == y[k] for k in keys), 'v4 boundary identity mismatch')
        h.require(all(x[k] == d[k] for k in ('pid', 'service', 'observation', 'job', 'worker', 'preparation', 'transaction')), 'v4 transaction identity mismatch')
        if x['publication'] is not None:
            h.require(any(t['begin']['publication'] == x['publication'] and t['begin']['endpoint'] == x['endpoint']
                          for t in e['operations'] if t['operation'] == 'callback_execution'), 'publication identity mismatch')
        item = dict(s, name='v4:' + s['operation'], ownership='transaction/publication')
        (context if s['operation'] in EXCLUDED else phases).append(item)
    mode = 'baseline' if e['arm'] == 'baseline' else 'instrumented'
    for s in phases:
        name = s.get('phase', s.get('operation'))
        s['source_citations'] = source_probes(probes, h.ROOT / 'build' / h.NAMES[0] / mode / e['variant'], name)
        h.require(s['source_citations'], 'missing source binding: ' + name)
    decode = [s for s in phases if s['name'] == 'v3:decode_exchange_including_transport' and
              s['role'] == 'demand' and all(s['begin'][k] == (d[k] or 0) for k in ('job', 'worker', 'preparation'))]
    h.require(len(decode) == 1, 'missing/ambiguous decode boundary')
    bounds = (start, decode[0]['start'], decode[0]['stop'], stop)
    h.require(list(bounds) == sorted(bounds), 'invalid decode ordering')
    segments = partition(remainder, phases)
    explained = sum(s['duration_ns'] for s in segments if s['phases'])
    unmeasured = sum(s['duration_ns'] for s in segments if not s['phases'])
    h.require(explained + unmeasured == duration(remainder), 'remainder reconciliation failed')
    result = {k: previous[k] for k in ('variant', 'arm', 'endpoint', 'block', 'warmup', 'invocation_index', 'observation', 'latency_ns')}
    result.update(origin=origins[0], delivery=d, remainder_intervals=remainder, remainder_ns=duration(remainder),
                  helper_partition_available=e['arm'] != 'baseline', explained_ns=explained, unmeasured_ns=unmeasured,
                  segments=segments, phases=phases, context=context, helper_boundary_discrepancies=discrepancies,
                  phase_absence=row['phase_absence'], decode_boundary=decode[0],
                  inclusive={s['name']: duration(intersect(remainder, [(t['start'], t['stop']) for t in phases if t['name'] == s['name']])) for s in phases},
                  coarse={n: dict(intervals=intersect(remainder, [(l, r)]), remainder_ns=duration(intersect(remainder, [(l, r)])),
                                  explained_ns=sum(duration(intersect([(s['start_ns'], s['stop_ns'])], [(l, r)])) for s in segments if s['phases']),
                                  unmeasured_ns=sum(duration(intersect([(s['start_ns'], s['stop_ns'])], [(l, r)])) for s in segments if not s['phases']))
                          for n, l, r in zip(COARSE, bounds, bounds[1:])})
    return result


def summaries(rows, old):
    result = []
    for cell in old:
        members = [r for r in rows if not r['warmup'] and (r['variant'], r['arm'], r['endpoint']) ==
                   (cell['variant'], cell['arm'], cell['endpoint']) and [r['invocation_index'], r['observation']] in cell['members']]
        h.require(len(members) == len(cell['members']), 'selection inventory mismatch')
        groups = sorted({' + '.join(s['phases']) if s['phases'] else 'unmeasured' for r in members for s in r['segments']})
        metrics = {}
        for name in groups:
            values = [sum(s['duration_ns'] for s in r['segments'] if (' + '.join(s['phases']) if s['phases'] else 'unmeasured') == name) for r in members]
            metrics[name] = dict(duration_ns=stats(values), share=stats([v/r['remainder_ns'] for v, r in zip(values, members) if r['remainder_ns']]))
        ranking = sorted(groups, key=lambda n: (-metrics[n]['duration_ns']['median'], n))
        winners = [n for n in ranking if metrics[n]['duration_ns']['median'] == metrics[ranking[0]]['duration_ns']['median']]
        result.append(dict({k: cell[k] for k in ('variant', 'arm', 'endpoint', 'block', 'selection', 'members')},
                           metrics=metrics, ranking=ranking, winners=winners,
                           totals={k: stats([r[k] for r in members]) for k in ('remainder_ns', 'explained_ns', 'unmeasured_ns')},
                           shares={k: stats([r[k]/r['remainder_ns'] for r in members if r['remainder_ns']]) for k in ('explained_ns', 'unmeasured_ns')},
                           phase_availability={n: dict((status, sum(r['phase_absence'].get(n, 'unavailable') == status for r in members)) for status in sorted({r['phase_absence'].get(n, 'unavailable') for r in members})) for n in v3.PHASES},
                           inclusive={n: stats([r['inclusive'].get(n, 0) for r in members]) for n in sorted({n for r in members for n in r['inclusive']})},
                           coarse={n: {k: stats([r['coarse'][n][k] for r in members]) for k in ('remainder_ns', 'explained_ns', 'unmeasured_ns')} for n in COARSE}))
    return result


def decision(cells):
    votes = [dict({k: c[k] for k in ('arm', 'endpoint', 'block', 'selection')}, winners=c['winners'])
             for c in cells if c['variant'] == 'C' and c['arm'] != 'baseline']
    choices = {v['winners'][0] for v in votes if len(v['winners']) == 1}
    agreed = len(votes) == 32 and all(len(v['winners']) == 1 for v in votes) and len(choices) == 1 and 'unmeasured' not in choices
    choice = next(iter(choices)) if agreed else None
    return dict(decision='Investigate ' + choice if choice else 'Evidence insufficient', active_phase_set=choice, votes=votes,
                missing_information=('For runtime_validation nested in generation_validation, the smallest missing distinction is identity-bound elapsed coverage of per-file open/read/SHA-256 verification versus manifest parsing, attribute checks and final inventory traversal in verifyRuntime (frozen verification.cpp). File reads and hashing are combined by hash.addData(&file); the retained scope cannot separate their cost or waiting. No substep duration or scheduler state is inferred.' if choice == 'v3:generation_validation + v3:runtime_validation' else 'Identity-bound sub-boundaries separating the calls inside the agreed scopes, with shared-clock causal handoffs.') if choice else
                'Resolve the conflicting phase sets listed in votes; separate validation traversal/read/hash work, decode transport/processing, and unnamed boundary gaps with identity-bound causal observations.',
                limitation='Temporal coverage is not causation. No scheduler state is inferred outside verified helper coverage. No experiment prepared. Historical qualification remains failed at 78/80.')


def report(output):
    h.fresh(output, [b.REVIEW, *(h.ROOT / 'build' / n for n in h.NAMES)])
    before, files = {}, {}
    result = dict(status='blocked', decision='Evidence insufficient')
    try:
        (output / 'tools').mkdir()
        for path in sorted({Path(__file__).resolve(), Path(__file__).with_name('verify-preview-helper-remainder.py'),
                            h.ROOT / 'tests/test_preview_helper_remainder.py', *h.tool_paths(b, a, v3)}):
            files[str(path)] = h.digest(path)
            shutil.copy2(path, output / 'tools' / path.name)
        roots, before, consumed, accounts, probes = b.bind()
        files.update(consumed)
        for name in consumed:
            path = Path(name)
            if path.parent in (h.ROOT / 'scripts', h.ROOT / 'tests'):
                shutil.copy2(path, output / 'tools' / path.name)
        old = h.read(b.REVIEW / 'endpoints.json') + h.read(b.REVIEW / 'warmups.json')
        lookup = {(r['invocation_index'], r['observation'], r['endpoint']): r for r in old}
        rows = [endpoint(account, e, lookup[e['invocation_index'], e['observation'], e['endpoint']], probes)
                for account in accounts for e in account['endpoints']]
        h.require(len(rows) == 312 and sum(not r['warmup'] for r in rows) == 300, 'endpoint population mismatch')
        for name, values in (('endpoints', [r for r in rows if not r['warmup']]), ('warmups', [r for r in rows if r['warmup']])):
            h.write(output / (name + '.json'), values)
        cells = summaries(rows, h.read(b.REVIEW / 'distributions.json'))
        chosen = decision(cells)
        h.write(output / 'distributions.json', cells)
        h.write(output / 'decision.json', chosen)
        h.write(output / 'effects.json', h.read(b.REVIEW / 'effects.json'))
        result.update(status='complete', decision=chosen['decision'], measured_observations=150, endpoints=300, warmup_observations=6, warmup_endpoints=12)
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration) as error:
        result['failure'] = str(error)
    finally:
        try:
            passed = h.recheck(before, files)
        except (OSError, ValueError):
            passed = False
        if not passed:
            result.update(status='blocked', decision='Evidence insufficient', failure='input/tool drift')
        h.write(output / 'integrity.json', dict(passed=passed, inventories=before, files=files))
        h.write(output / 'assessment.json', result)
        lines = ['# Retained helper-uncovered startup remainder', '', result['status'] + ': ' + result['decision'], '',
                 result.get('failure', ''), 'All durations are ns. Active sets describe temporal coverage, not causation. Inclusive unions are non-additive. Baseline uses the full window. Warm-ups are separate.', '',
                 'Historical review 03 remains Evidence insufficient; qualification remains failed at 78/80.', '']
        if result['status'] == 'complete':
            lines += ['| Arm | Endpoint | Block | Selection | Winners | Remainder median | Explained median | Unmeasured median |', '|---|---|---|---|---|---:|---:|---:|']
            for c in cells:
                if c['variant'] == 'C' and c['arm'] != 'baseline':
                    lines.append('| ' + ' | '.join(str(x) for x in (c['arm'], c['endpoint'], c['block'], c['selection'], ', '.join(c['winners']), *(c['totals'][n]['median'] for n in ('remainder_ns', 'explained_ns', 'unmeasured_ns')))) + ' |')
            lines += ['', chosen['missing_information'], '', chosen['limitation'], '',
                      'See [endpoints](endpoints.json), [warm-ups](warmups.json), [distributions](distributions.json), [decision](decision.json), and [signed arm comparisons](effects.json). Medians are descriptive and must not be added to reconstruct a median endpoint.']
        (output / 'REPORT.md').write_text('\n'.join(lines) + '\n')
        h.write(output / 'seal.json', h.inventory(output))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    value = report(args.output.absolute())
    print(h.json.dumps(value, indent=2))
    sys.exit(value['status'] != 'complete')
