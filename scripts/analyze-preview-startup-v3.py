#!/usr/bin/env python3
"""Read-only adapter for the retained, preregistered v3 overhead corpus."""
import argparse
from collections import Counter, defaultdict
import json
import math
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
# Importing this module defines offline helpers only; never call its execution paths.
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('overhead', ROOT / 'scripts/measure-preview-tracing-overhead.py')
overhead = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overhead)
a = overhead.smoke.analysis


def semantic(value):
    """Retained validation used the JSON path as source; raw line numbers agree."""
    if isinstance(value, dict):
        return {k: semantic(v) for k, v in value.items() if k not in ('file', 'observation_file')}
    if isinstance(value, list):
        return [semantic(v) for v in value]
    return value


def window(row, endpoint):
    start = row['boundaries']['startup_origin'][0]['ns']
    end = next(e['ns'] for e in row['deliveries'] if e['phase'] == endpoint)
    def clip(spans):
        return [(max(start, s['start']), min(end, s['stop'])) for s in spans
                if s['start'] < end and s['stop'] > start]
    eligible = [s for s in row['timeline'] if s['role'] in ('demand', 'service_control')]
    phases = {}
    for phase in (*a.PHASES, 'construction_outer'):
        spans = [s for s in eligible if s['phase'] == phase]
        intervals = clip(spans)
        phases[phase] = dict(presence=len(intervals), union_ms=a.duration(intervals),
                             availability='observed' if intervals else row['phase_absence'].get(phase, 'missing_or_ambiguous'))
    covered = clip([s for s in eligible if s['phase'] in a.PHASES])
    standby = [s for s in row['timeline'] if s['phase'] == 'pool_worker_prepare' and s['role'] == 'standby']
    exchanges = [s for s in row['timeline'] if s['role'] == 'demand' and s['phase'].endswith('exchange_including_transport')]
    overlaps = [(max(start, p['start'], x['start']), min(end, p['stop'], x['stop']))
                for p in standby for x in exchanges
                if max(start, p['start'], x['start']) < min(end, p['stop'], x['stop'])]
    return dict(origin_ns=start, endpoint_ns=end, elapsed_ms=(end-start)/1e6, phases=phases,
                covered_union_ms=a.duration(covered), uncovered_intervals_ns=a.gaps(start, end, covered),
                uncovered_ms=a.duration(a.gaps(start, end, covered)), standby_overlap_ms=a.duration(overlaps))


def summarize(rows):
    groups = defaultdict(list)
    for r in rows:
        if r['warmup']:
            continue
        for endpoint in ('pixels', 'metadata'):
            for block in ('pooled', r['block']):
                groups[r['mode'], r['variant'], r['fixture'], endpoint, block].append(r)
    result = []
    for (mode, variant, fixture, endpoint, block), values in groups.items():
        latency = 'first_ms' if endpoint == 'pixels' else 'final_ms'
        item = dict(mode=mode, variant=variant, fixture=fixture, endpoint=endpoint, block=block,
                    observations=len(values), harness_ms=a.distribution([r['latencies'][latency] for r in values]))
        if mode == 'T':
            windows = [r['windows'][endpoint] for r in values]
            item.update({k: a.distribution([w[k] for w in windows]) for k in
                         ('elapsed_ms', 'covered_union_ms', 'uncovered_ms', 'standby_overlap_ms')})
            item['overlapping_observations'] = sum(w['standby_overlap_ms'] > 0 for w in windows)
            item['phases'] = {p: dict(present_observations=sum(w['phases'][p]['presence'] > 0 for w in windows),
                                      duration_ms=a.distribution([w['phases'][p]['union_ms'] for w in windows if w['phases'][p]['presence']]))
                              for p in windows[0]['phases']}
        result.append(item)
    return result


def select_tails(rows):
    return [dict(variant=v, endpoint=e, observations=sorted(
        [r for r in rows if r['mode'] == 'T' and not r['warmup'] and r['variant'] == v and r['fixture'] == '3200x2400.png'],
        key=lambda r: (-r['latencies']['first_ms' if e == 'pixels' else 'final_ms'], r['block'], r['sample']))[:5])
        for v in 'ABCD' for e in ('pixels', 'metadata')]


def check_counts(inventory, lifetimes):
    counts = Counter()
    for r in inventory:
        counts[r['mode'] + ('_warmup' if r['warmup'] else '_measured')] += r['count']
    expected = dict(T_measured=1200, U_measured=1200, T_warmup=12, U_warmup=12)
    if len(inventory) != 264 or dict(counts) != expected or lifetimes != 1344:
        raise ValueError(f'corpus counts disagree: {dict(counts)}, invocations={len(inventory)}, lifetimes={lifetimes}')
    return dict(counts, invocations=len(inventory), traced_service_lifetimes=lifetimes, setup_services=132)


def analyze(root, output):
    root, output = root.resolve(), output.resolve()
    if root == output or root in output.parents or ROOT / 'build' not in output.parents:
        raise ValueError('fresh output must be under build/ and outside retained package')
    # Confirm the repository ignores the artifact destination without invoking Git.
    if '/build/' not in (ROOT / '.gitignore').read_text().splitlines() and 'build/' not in (ROOT / '.gitignore').read_text().splitlines():
        raise ValueError('build/ must be ignored')
    output.mkdir()
    before, rows, inventory, issues, setup = {str(Path(__file__).resolve()): a.digest(Path(__file__))}, [], [], [], []
    lifetimes = 0
    def read(path, expected=None):
        path = path.resolve()
        if root not in path.parents:
            raise ValueError('input escapes retained package: ' + str(path))
        before[str(path)] = a.digest(path)
        if expected is not None and before[str(path)] != expected:
            raise ValueError('integrity mismatch: ' + str(path))
        return path.read_text()
    def load(path, expected=None):
        return json.loads(read(path, expected))
    try:
        hashes = load(root / 'final-evidence-hashes.json')
        seal = load(root / 'seal.json')
        prep = load(root / 'preparation.json', seal['preparation.json'])
        for name, expected in prep['tools'].items():
            path = Path(name)
            before[str(path)] = a.digest(path)
            if before[str(path)] != expected:
                raise ValueError('recorded tool identity changed: ' + name)
        marker = load(root / 'execution-started.json')
        prereg = load(root / 'execution/preregistration.json', marker['preregistration_sha256'])
        def evidence(path):
            return load(path, hashes[str(path.relative_to(root / 'execution'))])
        for command in prereg['commands']:
            inv = command['invocation']
            path = Path(command['argv'][-1])
            if path.parent != root / 'execution/observations':
                raise ValueError('unexpected observation destination')
            inventory.append(dict(inv, file=str(path)))
            try:
                data = evidence(path)
                samples = data['samples']
                if len(samples) != inv['count']:
                    raise ValueError('sample count mismatch')
                streams = {ext: read(path.with_suffix(ext), hashes[str(path.with_suffix(ext).relative_to(root / 'execution'))]) for ext in ('.stderr', '.stdout')}
                retained = evidence(path.with_suffix('.validation.json'))
                if 'TRACE' in streams['.stdout']:
                    raise ValueError('TRACE on stdout')
                if inv['mode'] == 'T':
                    trace = overhead.validate_trace(streams['.stderr'], samples, str(path.with_suffix('.stderr')), inv['variant'])
                    if semantic(trace) != semantic(retained):
                        raise ValueError('retained semantic validation differs')
                    issues.extend(trace['issues'])
                    lifetimes += trace['service_lifetimes']
                    observed = trace['accounting']
                    setup.extend(dict(invocation=inv, span=s) for s in trace['unassigned'])
                else:
                    if 'TRACE' in streams['.stderr'] or retained.get('issues'):
                        raise ValueError('unexpected U trace or validation issues')
                    observed = [dict(sample=i, latencies={k: s[k] for k in ('first_ms', 'final_ms')}) for i, s in enumerate(samples)]
                for r in observed:
                    r.update(inv)
                    r['observation_file'] = str(path)
                    if any(type(x) not in (int, float) or not math.isfinite(x) or x < 0 for x in r['latencies'].values()):
                        raise ValueError('invalid harness latency')
                    if inv['mode'] == 'T':
                        r['windows'] = {e: window(r, e) for e in ('pixels', 'metadata')}
                        origin = r['windows']['pixels']['origin_ns']
                        r['markers'] = [dict(e, relative_ms=(e['ns']-origin)/1e6) for e in
                                        trace_events(streams['.stderr'], str(path.with_suffix('.stderr')), r)]
                        r['relative_timeline'] = [dict(s, start_ms=(s['start']-origin)/1e6, stop_ms=(s['stop']-origin)/1e6) for s in r['timeline']]
                    rows.append(r)
            except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
                issues.append(dict(invocation=inv, reason=str(error)))
        counts = check_counts(inventory, lifetimes)
        if [r for r in inventory if {k: r[k] for k in overhead.schedule()[0]} not in overhead.schedule()]:
            raise ValueError('preregistration identities differ from fixed schedule')
        if len({r['index'] for r in inventory}) != 264:
            raise ValueError('duplicate invocation identity')
    except (OSError, ValueError, KeyError, TypeError) as error:
        issues.append(dict(reason=str(error)))
        counts = {}
    after = {}
    for name in before:
        try:
            after[name] = a.digest(Path(name))
        except OSError as error:
            after[name] = None
            issues.append(dict(reason=str(error), file=name))
    if before != after:
        issues.append(dict(reason='inputs changed during analysis'))
    summary = summarize(rows)
    tails = select_tails(rows)
    for name, value in [('inventory', inventory), ('accounting', rows), ('setup-activity', setup), ('phase-summary', summary),
                        ('attribution-issues', issues), ('tails', tails), ('input-integrity', dict(before=before, after=after, unchanged=before == after,
                         adapter_sha256=a.digest(Path(__file__)), argv=sys.argv))]:
        a.write_json(output / (name + '.json'), value)
    status = 'blocked' if issues else 'complete'
    a.write_json(output / 'assessment.json', dict(status=status, counts=counts, issues=len(issues)))
    report(root, output, status, counts, summary, tails)
    return 1 if issues else 0


def trace_events(text, source, row):
    events, _, _ = a.parse_trace(text, source)
    identity = row['timeline'][0]['begin']
    return [e for e in events if (e['pid'], e['service']) == (identity['pid'], identity['service']) and e['edge'] == 'point']


def report(root, output, status, counts, summary, tails):
    def link(path):
        return os.path.relpath(path, output)
    lines = ['# Retained v3 startup assessment', '', status, '', f'Corpus accounting: `{json.dumps(counts, sort_keys=True)}`.', '',
             'Instrumented wall-clock intervals describe observed work, not CPU cost or a complete causal critical path. Startup origin precedes harness timer start; delivery probes follow latency capture. Harness latencies are reported separately. No origin is inferred from latency.', '',
             'Coverage retains the historical phase set. Full construction (`construction_outer`) and constructor body (`service_construction`) are separate. Broad job, dispatch and lifecycle envelopes do not contribute to coverage. Inclusive phase durations are not additive. Uncovered intervals remain unnamed elapsed time; missing or ambiguous phases remain unavailable. A generation phases are absent by design.', '',
             f'[Completed overhead report]({link(root / "FINAL-ASSESSMENT.md")}) includes the host-activity limitation: a read-only audit ran during small-PNG invocations 59–70. No estimated overhead is subtracted. Phase quantiles and T/U differences do not establish causality. C’s failed qualification and D’s failed pilot remain unchanged.', '',
             '[Inventory](inventory.json), [accounting](accounting.json), [phase and block summaries](phase-summary.json), [setup activity](setup-activity.json), [issues](attribution-issues.json), [tails](tails.json), [input integrity](input-integrity.json). Warm-ups and setup are excluded from measured summaries. Accounting retains service-control activity and post-delivery cleanup separately by role and timestamp; U supplies latency context only.', '',
             '| Variant | Fixture | Endpoint | Window median/p95 ms | Covered median ms | Uncovered median/p95 ms | Standby overlap count |', '|---|---|---|---:|---:|---:|---:|']
    for g in summary:
        if g['mode'] != 'T' or g['block'] != 'pooled':
            continue
        w, u = g['elapsed_ms'], g['uncovered_ms']
        lines.append(f"| {g['variant']} | {g['fixture']} | {g['endpoint']} | {w['median']:.3f}/{w['p95']:.3f} | {g['covered_union_ms']['median']:.3f} | {u['median']:.3f}/{u['p95']:.3f} | {g['overlapping_observations']} |")
    lines += ['', '## Large-PNG observations', '']
    for tail in tails:
        selected = tail['observations']
        if not selected:
            continue
        slowest = selected[0]
        w = slowest['windows'][tail['endpoint']]
        lines += [f"{tail['variant']} {tail['endpoint']}: selected blocks {', '.join(str(r['block']) for r in selected)}. The slowest window is {w['elapsed_ms']:.3f} ms, with {w['covered_union_ms']:.3f} ms covered and {w['uncovered_ms']:.3f} ms unnamed. Its longest uncovered interval is {max((b-a)/1e6 for a, b in w['uncovered_intervals_ns']):.3f} ms. The detailed timelines below and [tail records](tails.json) retain the evidence.", '']
    for tail in tails:
        lines += ['', f"## Large-PNG {tail['variant']} {tail['endpoint']} tails", '']
        for r in tail['observations']:
            w = r['windows'][tail['endpoint']]
            key = 'first_ms' if tail['endpoint'] == 'pixels' else 'final_ms'
            lines += [f"### Block {r['block']}, sample {r['sample']}", '', f"Harness {r['latencies'][key]:.3f} ms; origin-to-probe {w['elapsed_ms']:.3f} ms; covered {w['covered_union_ms']:.3f} ms; unnamed elapsed {w['uncovered_ms']:.3f} ms; standby overlap {w['standby_overlap_ms']:.3f} ms.", '',
                      'Gaps relative to origin (ms): `' + json.dumps([[(x-w['origin_ns'])/1e6 for x in gap] for gap in w['uncovered_intervals_ns']]) + '`.', '',
                      '| Span/marker | Role | Origin-relative ms | Raw evidence |', '|---|---|---:|---|']
            for s in r['relative_timeline']:
                b, e = s['begin'], s['end']
                lines.append(f"| {s['phase']} | {s['role']} | {s['start_ms']:.6f}–{s['stop_ms']:.6f} | [begin]({link(Path(b['file']))}#L{b['line']}), [end]({link(Path(e['file']))}#L{e['line']}) |")
            for e in r['markers']:
                lines.append(f"| {e['phase']} | {e['role']} | {e['relative_ms']:.6f} | [line {e['line']}]({link(Path(e['file']))}#L{e['line']}) |")
    lines += ['', 'The large-PNG tails retain every observed interval and boundary above. Time inside exchanges includes transport; gaps and time within broad envelopes cannot be attributed further from these traces. Observed concurrency does not identify the cause of delay. No thresholds, qualification changes or further experiment are proposed.', '']
    (output / 'ASSESSMENT.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_package', type=Path)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    return analyze(args.input_package, args.output_directory)


if __name__ == '__main__':
    sys.exit(main())
