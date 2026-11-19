#!/usr/bin/env python3
"""Independent remainder sweep and decision verification; never imports its reporter."""
import argparse
from collections import defaultdict
import importlib.util
import math
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('independent_remainder_boundary', Path(__file__).with_name('helper-startup-remainder-evidence.py'))
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h


def source_probes(probes, root, name):
    return [p for p in probes if p['file'].startswith(str(root) + '/') and '"' + name + '"' in p['text']]

old = h.module('independent_original_review', 'verify-preview-helper-startup-review.py')
v3 = h.module('independent_remainder_allowlist', 'analyze-preview-startup.py')


def measure(parts):
    return sum(y-x for x, y in parts)


def intersection(parts, spans):
    points = sorted({p for pair in [*parts, *spans] for p in pair})
    return old.intervals([(x, y) for x, y in zip(points, points[1:]) if
                          any(a <= x < y <= z for a, z in parts) and any(a <= x < y <= z for a, z in spans)],
                         (points[0], points[-1])) if points else []


def distribution(values):
    return old.distribution(values) if values else None


def check_endpoint(account, e, previous, saved, probes):
    d = e['delivery']
    row, = [r for r in account['lifecycle']['accounting'] if r['sample'] == e['observation']-1]
    origin, = [x for x in row['boundaries']['startup_origin'] if all(x[k] == d[k] for k in ('pid', 'service', 'observation'))]
    start, stop = origin['ns'], d['ns']
    h.require(start < stop and (previous['origin'], previous['delivery'], previous['start_ns'], previous['stop_ns']) ==
              (origin, d, start, stop), 'review startup window mismatch')
    preparations, discrepancies = [], []
    for window in account['windows']:
        identity = window['begin']
        if window['lifecycle_binding']['classification'] == 'demand' and all(identity[k] == d[k] for k in ('pid', 'service', 'observation')):
            h.require(all(identity[k] == d[k] for k in ('worker', 'preparation')), 'preparation identity mismatch')
            preparations.append((identity['ns'], window['end']['ns']))
            discrepancies.append(window['lifecycle_binding'])
    remainder = old.intervals([(start, stop)], (start, stop), preparations if e['arm'] != 'baseline' else [])
    if e['arm'] != 'baseline':
        h.require(preparations and remainder == previous['groups']['selected_demand']['uncovered_intervals'] and
                  measure(remainder) == previous['groups']['selected_demand']['uncovered_ns'], 'review uncovered mismatch')
    expected, context = [], []
    for span in row['timeline']:
        x, y = span['begin'], span['end']
        h.require(all(x[k] == y[k] for k in ('pid', 'tid', 'service', 'observation', 'job', 'worker', 'preparation', 'role')) and
                  all(x[k] == d[k] for k in ('pid', 'service', 'observation')), 'v3 identity mismatch')
        item = dict(span, name='v3:' + span['phase'], ownership=span['role'])
        if span['phase'] in set(v3.PHASES)-{'helper_prepare'} and span['role'] in {'demand', 'service_control'}:
            if span['role'] == 'demand':
                allowed = [tuple(d[k] or 0 for k in ('job', 'worker', 'preparation'))]
                allowed += [tuple(t['begin'][k] for k in ('job', 'worker', 'preparation')) for t in row['timeline']
                            if t['phase'] == 'demand_dispatch' and t['role'] == 'demand']
                h.require(tuple(x[k] for k in ('job', 'worker', 'preparation')) in allowed, 'v3 demand lineage mismatch')
            else:
                h.require((x['job'], x['worker'], x['preparation']) == (0, 0, 0), 'service-control ownership mismatch')
            expected.append(item)
        else:
            context.append(item)
    for span in e['operations']:
        x, y = span['begin'], span['end']
        identity = ('pid', 'tid', 'service', 'observation', 'job', 'worker', 'preparation', 'transaction', 'publication', 'session', 'generation', 'span', 'endpoint')
        h.require(all(x[k] == y[k] for k in identity) and all(x[k] == d[k] for k in
                  ('pid', 'service', 'observation', 'job', 'worker', 'preparation', 'transaction')), 'v4 identity mismatch')
        if x['publication'] is not None:
            h.require((x['publication'], x['endpoint']) in {(s['begin']['publication'], s['begin']['endpoint']) for s in e['operations']
                      if s['operation'] == 'callback_execution'}, 'publication mismatch')
        item = dict(span, name='v4:' + span['operation'], ownership='transaction/publication')
        (context if span['operation'] in {'transaction_wrapper', 'retirement_call'} else expected).append(item)
    source_root = h.ROOT / 'build' / h.NAMES[0] / ('baseline' if e['arm'] == 'baseline' else 'instrumented') / e['variant']
    for item in expected:
        name = item['phase'] if 'phase' in item else item['operation']
        item['source_citations'] = source_probes(probes, source_root, name)
        h.require(item['source_citations'], 'missing source probe')
    decode, = [s for s in expected if s['name'] == 'v3:decode_exchange_including_transport' and s['role'] == 'demand' and
               all(s['begin'][k] == (d[k] or 0) for k in ('job', 'worker', 'preparation'))]
    h.require(start <= decode['start'] <= decode['stop'] <= stop, 'decode ordering mismatch')
    segments = []
    for left, right in remainder:
        points = {left, right}
        for span in expected:
            points.update(p for p in (span['start'], span['stop']) if left < p < right)
        points = sorted(points)
        for x, y in zip(points, points[1:]):
            active = sorted({s['name'] for s in expected if s['start'] <= x and s['stop'] >= y})
            segments.append(dict(start_ns=x, stop_ns=y, duration_ns=y-x, phases=active))
    explained = sum(s['duration_ns'] for s in segments if s['phases'])
    unmeasured = sum(s['duration_ns'] for s in segments if not s['phases'])
    h.require(explained + unmeasured == measure(remainder), 'reconciliation failed')
    coarse = {}
    for name, pair in zip(('pre_decode', 'decode_exchange', 'post_decode'), ((start, decode['start']), (decode['start'], decode['stop']), (decode['stop'], stop))):
        parts = intersection(remainder, [pair])
        coarse[name] = dict(intervals=parts, remainder_ns=measure(parts), explained_ns=sum(
            measure(intersection([(s['start_ns'], s['stop_ns'])], [pair])) for s in segments if s['phases']), unmeasured_ns=sum(
            measure(intersection([(s['start_ns'], s['stop_ns'])], [pair])) for s in segments if not s['phases']))
    inclusive = {name: measure(intersection(remainder, [(s['start'], s['stop']) for s in expected if s['name'] == name])) for name in {s['name'] for s in expected}}
    result = {k: previous[k] for k in ('variant', 'arm', 'endpoint', 'block', 'warmup', 'invocation_index', 'observation', 'latency_ns')}
    result.update(origin=origin, delivery=d, remainder_intervals=remainder, remainder_ns=measure(remainder),
                  helper_partition_available=e['arm'] != 'baseline', explained_ns=explained, unmeasured_ns=unmeasured,
                  segments=segments, phases=expected, context=context, helper_boundary_discrepancies=discrepancies,
                  phase_absence=row['phase_absence'], decode_boundary=decode, inclusive=inclusive, coarse=coarse)
    h.require(saved == result, 'endpoint arithmetic/context mismatch')


def check_summaries(rows, cells, previous):
    # Recompute selection membership directly from endpoint latencies; separately
    # require exact agreement with the accepted review's membership and order.
    h.require(len(cells) == len(previous), 'summary inventory mismatch')
    for c, accepted in zip(cells, previous):
        keys = ('variant', 'arm', 'endpoint', 'block', 'selection', 'members')
        h.require(all(c[k] == accepted[k] for k in keys), 'review selection mismatch')
        population = [r for r in rows if (r['variant'], r['arm'], r['endpoint']) == (c['variant'], c['arm'], c['endpoint'])]
        values = sorted(r['latency_ns'] for r in population)
        median = statistics.median(values)
        distance = min(abs(v-median) for v in values)
        if c['selection'] == 'slowest':
            members = [r for r in population if r['latency_ns'] >= values[-5]]
        elif c['selection'] == 'nearest_median':
            members = [r for r in population if abs(r['latency_ns']-median) == distance]
        else:
            members = [r for r in population if c['block'] == 'pooled' or r['block'] == c['block']]
        h.require(c['members'] == [[r['invocation_index'], r['observation']] for r in members], 'selection ties mismatch')
        groups = {(' + '.join(s['phases']) or 'unmeasured') for r in members for s in r['segments']}
        metrics = {}
        for group in groups:
            values = [sum(s['duration_ns'] for s in r['segments'] if (' + '.join(s['phases']) or 'unmeasured') == group) for r in members]
            metrics[group] = dict(duration_ns=distribution(values), share=distribution([v/r['remainder_ns'] for v, r in zip(values, members) if r['remainder_ns']]))
        ranking = sorted(groups, key=lambda n: (-metrics[n]['duration_ns']['median'], n))
        winners = [n for n in ranking if metrics[n]['duration_ns']['median'] == metrics[ranking[0]]['duration_ns']['median']]
        h.require((c['metrics'], c['ranking'], c['winners']) == (metrics, ranking, winners), 'distribution/ranking mismatch')
        h.require(c['totals'] == {k: distribution([r[k] for r in members]) for k in ('remainder_ns', 'explained_ns', 'unmeasured_ns')}, 'total distribution mismatch')
        h.require(c['shares'] == {k: distribution([r[k]/r['remainder_ns'] for r in members if r['remainder_ns']]) for k in ('explained_ns', 'unmeasured_ns')}, 'share distribution mismatch')
        availability = {}
        for name in v3.PHASES:
            counts = defaultdict(int)
            for r in members:
                counts[r['phase_absence'].get(name, 'unavailable')] += 1
            availability[name] = dict(counts)
        h.require(c['phase_availability'] == availability, 'phase availability mismatch')
        h.require(c['inclusive'] == {n: distribution([r['inclusive'].get(n, 0) for r in members]) for n in {n for r in members for n in r['inclusive']}}, 'inclusive distribution mismatch')
        h.require(c['coarse'] == {n: {k: distribution([r['coarse'][n][k] for r in members]) for k in ('remainder_ns', 'explained_ns', 'unmeasured_ns')} for n in ('pre_decode', 'decode_exchange', 'post_decode')}, 'coarse distribution mismatch')


def check_decision(cells, decision):
    votes = []
    for c in cells:
        if c['variant'] == 'C' and c['arm'] in ('instrumented', 'captured'):
            votes.append({k: c[k] for k in ('arm', 'endpoint', 'block', 'selection', 'winners')})
    choices = [v['winners'][0] if len(v['winners']) == 1 else None for v in votes]
    agreed = len(choices) == 32 and len(set(choices)) == 1 and choices[0] not in (None, 'unmeasured')
    choice = choices[0] if agreed else None
    h.require(decision['votes'] == votes and decision['active_phase_set'] == choice and decision['decision'] ==
              ('Investigate ' + choice if choice else 'Evidence insufficient') and decision['missing_information'], 'decision mismatch')


def verify(output):
    h.sealed(output)
    integrity = h.read(output / 'integrity.json')
    h.require(integrity['passed'] and h.recheck(integrity['inventories'], integrity['files']), 'input/tool drift')
    for name, digest in integrity['files'].items():
        if Path(name).parent in (h.ROOT / 'scripts', h.ROOT / 'tests'):
            h.require(h.digest(output / 'tools' / Path(name).name) == digest, 'snapshot mismatch')
    result = h.read(output / 'assessment.json')
    if result['status'] == 'blocked':
        h.require(result.get('failure') and result['decision'] == 'Evidence insufficient', 'invalid blocked result')
        return dict(status='passed', outcome='blocked', evidence_seal=h.digest(output / 'seal.json'))
    roots, before, files, accounts, probes = b.bind()
    h.require(old.verify(b.REVIEW)['outcome'] == 'complete', 'independent review replay failed')
    h.require(before == integrity['inventories'] and all(integrity['files'].get(k) == v for k, v in files.items()), 'consumed binding mismatch')
    required = {Path(__file__).resolve(), Path(__file__).with_name('report-preview-helper-remainder.py'),
                h.ROOT / 'tests/test_preview_helper_remainder.py', *h.tool_paths(b, v3)}
    h.require(all(integrity['files'].get(str(p)) == h.digest(p) for p in required), 'missing tool binding')
    measured, warmups = h.read(output / 'endpoints.json'), h.read(output / 'warmups.json')
    h.require(len(measured) == 300 and len(warmups) == 12 and all(not r['warmup'] for r in measured) and all(r['warmup'] for r in warmups), 'population mismatch')
    rows = measured + warmups
    lookup = {(r['invocation_index'], r['observation'], r['endpoint']): r for r in rows}
    h.require(len(lookup) == 312, 'duplicate endpoint')
    for population, count in ((measured, 150), (warmups, 6)):
        observations = defaultdict(set)
        for r in population:
            observations[r['invocation_index'], r['observation']].add(r['endpoint'])
        h.require(len(observations) == count and all(s == {'pixels', 'metadata'} for s in observations.values()), 'observation mismatch')
    accepted = {(r['invocation_index'], r['observation'], r['endpoint']): r for r in
                h.read(b.REVIEW / 'endpoints.json') + h.read(b.REVIEW / 'warmups.json')}
    for account in accounts:
        for e in account['endpoints']:
            key = e['invocation_index'], e['observation'], e['endpoint']
            check_endpoint(account, e, accepted[key], lookup[key], probes)
    cells = h.read(output / 'distributions.json')
    check_summaries(measured, cells, h.read(b.REVIEW / 'distributions.json'))
    check_decision(cells, h.read(output / 'decision.json'))
    h.require(h.read(output / 'effects.json') == h.read(b.REVIEW / 'effects.json'), 'signed comparison drift')
    h.require(result == dict(status='complete', decision=h.read(output / 'decision.json')['decision'], measured_observations=150,
                             endpoints=300, warmup_observations=6, warmup_endpoints=12), 'assessment mismatch')
    h.require(h.recheck(before, integrity['files']), 'verification input drift')
    return dict(status='passed', outcome='complete', decision=result['decision'], measured_observations=150, endpoints=300,
                warmup_observations=6, warmup_endpoints=12, evidence_seal=h.digest(output / 'seal.json'),
                imports_reporter=False, verifier_sha256=h.digest(Path(__file__)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    try:
        print(h.json.dumps(verify(args.evidence.absolute()), indent=2))
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print(h.json.dumps(dict(status='blocked', failure=str(error)), indent=2))
        sys.exit(1)
