#!/usr/bin/env python3
"""Offline retained startup trace accounting; never executes the measured program."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys

PHASES = ('service_construction', 'runtime_validation', 'generation_validation',
          'generation_acquisition', 'source_capture', 'helper_prepare',
          'inspect_exchange_including_transport', 'decode_exchange_including_transport', 'cleanup')
IDENTITIES = {'version': int, 'service': int, 'observation': int, 'job': int, 'worker': int, 'role': str}
FIELDS = {'ns': int, 'pid': int, 'tid': int, 'request': str, 'object': str,
          'slot': int, 'phase': str, 'edge': str}


def distribution(values):
    values = sorted(values)
    return {'count': len(values), 'median': statistics.median(values),
            'p95': values[math.ceil(len(values) * .95) - 1]} if values else None


def union(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return merged


def duration(intervals):
    return sum(b - a for a, b in union(intervals)) / 1e6


def gaps(start, end, intervals):
    cursor, result = start, []
    for a, b in union((max(start, a), min(end, b)) for a, b in intervals if a < end and b > start):
        if a > cursor:
            result.append([cursor, a])
        cursor = max(cursor, b)
    if cursor < end:
        result.append([cursor, end])
    return result


def parse_trace(text, source):
    events, spans, issues, stacks = [], [], [], defaultdict(list)
    for line, raw in enumerate(text.splitlines(), 1):
        if 'TRACE' not in raw:
            continue
        ref = {'file': source, 'line': line}
        try:
            if not raw.startswith('TRACE '):
                raise ValueError('noncanonical prefix')
            event = json.loads(raw[6:])
            schema = FIELDS if 'version' not in event else dict(FIELDS, **IDENTITIES)
            if event.get('version') == 3:
                schema['preparation'] = int
            if set(event) != set(schema) or any(type(event[k]) is not t for k, t in schema.items()):
                raise ValueError('invalid fields/types')
            if event.get('version', 2) not in (2, 3):
                raise ValueError('unsupported trace version')
            if event['ns'] < 0 or event['edge'] not in ('begin', 'end', 'point'):
                raise ValueError('invalid timestamp/edge')
        except (ValueError, TypeError) as error:
            issues.append(dict(ref, kind='malformed', raw=raw, reason=str(error)))
            continue
        event = dict(event, **ref)
        events.append(event)
    events.sort(key=lambda e: (e['ns'], e['line']))
    for event in events:
        key = tuple(event[k] for k in ('pid', 'tid', 'object', 'slot', 'phase')) + tuple(event.get(k) for k in IDENTITIES if k != 'role') + (event.get('preparation'), event.get('role'))
        if event['edge'] == 'begin':
            stacks[key].append(event)
        elif event['edge'] == 'end':
            if not stacks[key]:
                issues.append(dict(event, kind='unmatched_end'))
            else:
                begin = stacks[key].pop()
                spans.append({'begin': begin, 'end': event, 'phase': event['phase'],
                              'start': begin['ns'], 'stop': event['ns']})
    for stack in stacks.values():
        issues.extend(dict(e, kind='unmatched_begin') for e in stack)
    return events, sorted(spans, key=lambda s: (s['start'], s['begin']['line'])), issues


def contains(outer, inner):
    return outer['start'] <= inner['start'] <= inner['stop'] <= outer['stop']


def identity_issues(events, source):
    """Validate claims without inventing missing identities from addresses or time."""
    issues = []
    services, preparations, jobs = {}, {}, {}
    worker_phases = {'pool_job', 'pool_worker_prepare', 'helper_prepare', 'helper_ready',
                     'source_capture', 'inspect_exchange_including_transport',
                     'decode_exchange_including_transport', 'selected_worker', 'preparation_ready'}
    for e in events:
        if not e.get('version'):
            continue
        reasons = []
        if e['pid'] <= 0 or e['tid'] <= 0 or e['service'] <= 0 or e['observation'] < 0:
            reasons.append('invalid process/service/observation')
        key = e['pid'], e['service']
        observation = services.setdefault(key, e['observation'])
        if observation != e['observation']:
            reasons.append('inconsistent service observation')
        if any(e[k] < 0 for k in ('job', 'worker')) or e.get('preparation', 0) < 0:
            reasons.append('negative identity')
        if e['role'] not in ('setup', 'demand', 'standby', 'service_control', 'shutdown'):
            reasons.append('unsupported role')
        if e['phase'] in worker_phases and not e['worker']:
            reasons.append('missing worker')
        if e['phase'] in ('pool_job', 'selected_worker', 'pixels', 'metadata', 'demand_dispatch') and not e['job']:
            reasons.append('missing demand job')
        if e['role'] == 'demand' and e['phase'] in worker_phases and not e['job'] and not (e.get('version') == 3 and e.get('preparation')):
            reasons.append('unsupported demand role')
        if e['phase'] in ('pool_job', 'source_capture', 'helper_prepare', 'helper_ready',
                          'inspect_exchange_including_transport', 'decode_exchange_including_transport') and e['role'] == 'service_control':
            reasons.append('unsupported worker role')
        if e['role'] == 'standby' and e['phase'] in ('pool_job', 'pixels', 'metadata'):
            reasons.append('unsupported standby role')
        if e['job']:
            job_key = e['pid'], e['job']
            owner = jobs.setdefault(job_key, (e['service'], e['observation']))
            if owner != (e['service'], e['observation']):
                reasons.append('inconsistent demand job')
        if e.get('version') == 3:
            prep = e['preparation']
            if e['phase'] in ('pool_worker_prepare', 'preparation_ready') and not prep:
                reasons.append('missing preparation')
            if prep:
                owner = preparations.setdefault((e['pid'], prep), (e['service'], e['worker']))
                if owner != (e['service'], e['worker']) or not e['worker']:
                    reasons.append('inconsistent preparation worker')
        for reason in reasons:
            issues.append({'kind': 'identity_claim', 'file': source, 'line': e['line'], 'reason': reason})
    for e in events:
        if e.get('version') != 3 or e['phase'] not in ('pool_worker_prepare', 'preparation_ready'):
            continue
        same = [p for p in events if p.get('version') == 3 and
                (p['pid'], p['service'], p['worker'], p['preparation']) ==
                (e['pid'], e['service'], e['worker'], e['preparation'])]
        scheduled = [p for p in same if p['phase'] == 'preparation_schedule' and p['edge'] == 'point']
        execution = [p for p in same if p['phase'] == 'pool_worker_prepare']
        valid = len(scheduled) == 1 and scheduled[0]['ns'] <= e['ns']
        if e['phase'] == 'preparation_ready':
            starts = [p for p in execution if p['edge'] == 'begin']
            ends = [p for p in execution if p['edge'] == 'end']
            valid = valid and len(starts) == len(ends) == 1 and starts[0]['ns'] <= ends[0]['ns'] <= e['ns']
        if not valid:
            issues.append({'kind': 'identity_claim', 'file': source, 'line': e['line'],
                           'reason': 'unsupported preparation lifecycle'})
    return issues


def account(events, spans, samples, source, variant=None):
    constructions = [s for s in spans if s['phase'] == 'service_construction']
    deliveries = [e for e in events if e['phase'] == 'metadata' and e['edge'] == 'point']
    issues, rows, used = identity_issues(events, source), [], set()
    invalid_lines = {i['line'] for i in issues}
    pixels = [e for e in events if e['phase'] == 'pixels' and e['edge'] == 'point']
    if len(pixels) != len(samples):
        issues.append({'kind': 'pixel_count_mismatch', 'file': source, 'samples': len(samples), 'pixels': len(pixels)})
    if len(deliveries) != len(samples):
        issues.append({'kind': 'observation_count_mismatch', 'file': source,
                       'samples': len(samples), 'metadata_points': len(deliveries)})
    explicit = any(e.get('version') in (2, 3) for e in events)
    # Harness constructs one unmeasured setup service, then one per startup sample.
    if not explicit and len(constructions) != len(samples) + 1:
        issues.append({'kind': 'construction_count_mismatch', 'file': source})
    for index, sample in enumerate(samples):
        row = {'sample': index, 'observation_file': source.replace('.log', '.json'),
               'json_pointer': f'/samples/{index}', 'latencies': {k: sample.get(k) for k in ('first_ms', 'final_ms')},
               'status': 'unknown', 'phases': {}, 'timeline': [], 'unknown': []}
        rows.append(row)
        matches = [s for s in constructions if s['begin'].get('observation') == index + 1 and s['begin'].get('service', 0) > 0 and s['begin']['line'] not in invalid_lines] if explicit else []
        if (explicit and len(matches) != 1) or (not explicit and len(constructions) != len(samples) + 1):
            row['unknown'].append('cannot join samples to service lifetimes')
            issues.append({'kind': 'lifetime_join_failure', 'file': source, 'sample': index})
            continue
        construction = matches[0] if explicit else constructions[index + 1]
        start = construction['start']
        row['boundaries'] = {phase: [e for e in events if e.get('service') == construction['begin'].get('service') and e['phase'] == phase] for phase in ('startup_origin', 'construction_outer', 'construction_complete')} if explicit else {}
        origins = row['boundaries'].get('startup_origin', [])
        if len(origins) == 1:
            start = origins[0]['ns']
        limit = constructions[index + 2]['start'] if not explicit and index + 2 < len(constructions) else float('inf')
        begin = construction['begin']
        def owned(e):
            if explicit:
                return (e.get('service') == begin['service'] and e['pid'] == begin['pid']
                        and e.get('observation') == begin['observation'])
            return start <= e['ns'] < limit and e['pid'] == begin['pid'] and e['object'] == begin['object']
        points = [e for e in events if owned(e) and e['phase'] in ('pixels', 'metadata') and e['edge'] == 'point']
        matched = {p: [e for e in points if e['phase'] == p] for p in ('pixels', 'metadata')}
        row['delivery_counts'] = {p: len(v) for p, v in matched.items()}
        for phase, values in matched.items():
            if len(values) != 1:
                issues.append({'kind': 'service_delivery_count', 'file': source, 'sample': index, 'phase': phase, 'actual': len(values)})
        ends = matched['metadata'] if len(matched['metadata']) == 1 else matched['pixels']
        if len(ends) != 1:
            row['unknown'].append('no unique delivery endpoint; construction retained')
            row['timeline'] = [dict(construction, role='demand', after_delivery=False)]
            continue
        end = ends[0]
        row['identity_limitations'] = (['version 2 lacks preparation linkage'] if begin.get('version') == 2 else []) if begin.get('version') else ['historical trace lacks service, observation, job and worker identities']
        row['deliveries'] = points
        row['status'] = 'associated' if all(len(v) == 1 for v in matched.values()) else 'partial'
        window = [s for s in spans if s['begin']['pid'] == begin['pid'] and
                  ((s['begin'].get('service') == begin['service']) if begin.get('service') else start <= s['start'] < limit)]
        jobs = [s for s in window if s['phase'] == 'pool_job' and s['stop'] <= end['ns']]
        captures = [s for s in window if s['phase'] == 'source_capture' and s['stop'] <= end['ns']]
        worker_threads = {s['begin']['tid'] for s in captures}
        job = jobs[0] if len(jobs) == 1 else None
        pool = job['begin']['object'] if job else None
        preparations = [s for s in window if s['phase'] == 'pool_worker_prepare' and pool == s['begin']['object']]
        demand_preps = [s for s in preparations if s['begin']['slot'] == job['begin']['slot'] and s['stop'] <= job['start']] if job else []
        owner_threads = {s['begin']['tid'] for s in window if s['phase'] == 'pool_prepare' and s['begin']['object'] == pool}
        shutdowns = [s for s in window if s['phase'] == 'pool_shutdown' and s['begin']['object'] == pool]
        dispatches = [s for s in window if s['phase'] == 'transaction_dispatch' and s['begin']['object'] == pool]
        standby_preps = [p for p in preparations if job and p['begin']['slot'] != job['begin']['slot']
                         and any(d['start'] <= p['start'] for d in dispatches)]
        for s in window:
            b = s['begin']
            role = 'unknown'
            if s is construction:
                role = 'demand'
            elif job and s is job:
                role = 'demand'
            elif any(contains(p, s) and p['begin']['tid'] == b['tid'] for p in preparations):
                parents = [p for p in preparations if contains(p, s) and p['begin']['tid'] == b['tid']]
                roles = {'demand' if p in demand_preps else 'standby' if p in standby_preps else 'unknown' for p in parents}
                role = next(iter(roles)) if len(roles) == 1 else 'unknown'
            elif job and contains(job, s) and b['tid'] == job['begin']['tid']:
                role = 'demand'
            elif b['tid'] in owner_threads and s['phase'] in ('generation_validation', 'generation_acquisition', 'runtime_validation', 'pool_prepare'):
                role = 'service_control'
            elif not job and len(worker_threads) == 1 and b['tid'] in worker_threads and s['stop'] <= end['ns']:
                role = 'demand'
            elif s in shutdowns or any(contains(p, s) for p in shutdowns):
                role = 'shutdown'
            if b.get('version') in (2, 3) and b.get('service') == begin.get('service'):
                role = b['role'] if b['role'] in ('demand', 'standby', 'service_control', 'shutdown', 'setup') else 'unknown'
                if s['phase'] in ('pool_job', 'pool_worker_prepare', 'source_capture', 'helper_prepare', 'inspect_exchange_including_transport', 'decode_exchange_including_transport') and (not b.get('worker') or (not b.get('job') and not (b.get('version') == 3 and b.get('preparation')))):
                    role = 'unknown'
            if explicit and role in ('demand', 'standby') and s['phase'] in (
                    'pool_worker_prepare', 'helper_prepare', 'source_capture',
                    'inspect_exchange_including_transport', 'decode_exchange_including_transport'):
                prep_support = [p for p in window if p['phase'] == 'pool_worker_prepare' and
                                p['begin'].get('worker') == b.get('worker') and
                                (b.get('version') != 3 or p['begin'].get('preparation') == b.get('preparation')) and
                                contains(p, s)]
                job_support = [e for e in events if owned(e) and e['phase'] in ('demand_dispatch', 'pool_job') and
                               e.get('job') == b.get('job') and b.get('job')]
                if not prep_support and (role == 'standby' or not job_support):
                    role = 'unknown'
            if b.get('version') == 3 and role == 'demand' and b.get('preparation') and not b.get('job'):
                consumers = [e for e in events if owned(e) and e['phase'] == 'selected_worker' and
                             e.get('preparation') == b['preparation'] and e.get('worker') == b['worker']]
                if len(consumers) != 1:
                    role = 'unknown'
            if b.get('version') == 3 and role == 'standby':
                sponsors = [e for e in events if owned(e) and e['phase'] == 'transaction_dispatch' and
                            e.get('job') == b.get('job') and b.get('job')]
                if not sponsors:
                    role = 'unknown'
            if explicit and (b['line'] in invalid_lines or s['end']['line'] in invalid_lines):
                role = 'unknown'
            entry = dict(s, role=role, after_delivery=s['start'] >= end['ns'])
            row['timeline'].append(entry)
            used.add(s['begin']['line'])
            if role in ('unknown', 'shutdown_unresolved'):
                row['unknown'].append({'line': b['line'], 'phase': s['phase'], 'reason': role})
        for phase in PHASES:
            selected = [s for s in row['timeline'] if s['phase'] == phase and s['role'] in ('demand', 'service_control') and not s['after_delivery']]
            row.setdefault('phase_absence', {})[phase] = 'absent_by_design' if phase.startswith('generation_') and variant == 'A' else 'missing_or_ambiguous' if not selected else 'observed'
            row['phases'][phase] = {'count': len(selected), 'union_ms': duration((max(start, s['start']), min(end['ns'], s['stop'])) for s in selected if s['start'] < end['ns'] and s['stop'] > start)} if selected else None
        # pool_job is an envelope, not additional observed work.
        intervals = [(max(start, s['start']), min(s['stop'], end['ns'])) for s in row['timeline']
                     if s['phase'] in PHASES and s['role'] in ('demand', 'service_control') and s['start'] < end['ns'] and s['stop'] > start]
        row['observable_window_ms'] = (end['ns'] - start) / 1e6
        row['covered_union_ms'] = duration(intervals)
        row['uncovered_intervals_ns'] = gaps(start, end['ns'], intervals)
        exchanges = [s for s in row['timeline'] if 'exchange_including_transport' in s['phase'] and s['role'] == 'demand']
        intersections = [(max(x['start'], p['start']), min(x['stop'], p['stop'])) for x in exchanges for p in preparations
                         if p in standby_preps and max(x['start'], p['start']) < min(x['stop'], p['stop'])]
        if explicit:
            exchanges = [s for s in row['timeline'] if 'exchange_including_transport' in s['phase'] and s['role'] == 'demand']
            standby = [s for s in row['timeline'] if s['phase'] == 'pool_worker_prepare' and s['role'] == 'standby']
            intersections = [(max(x['start'], p['start']), min(x['stop'], p['stop'])) for x in exchanges for p in standby if max(x['start'], p['start']) < min(x['stop'], p['stop'])]
        unresolved = any(s['role'] == 'unknown' and s['phase'] in
                         ('pool_worker_prepare', 'pool_job', 'inspect_exchange_including_transport',
                          'decode_exchange_including_transport') for s in row['timeline'])
        row['standby_overlap_ms'] = duration((max(start, a), min(end['ns'], b)) for a, b in intersections
                                             if a < end['ns'] and b > start) if (job or explicit) and not unresolved else None
        row_errors = []
        if len(matched['pixels']) == len(matched['metadata']) == 1:
            if not start <= matched['pixels'][0]['ns'] <= matched['metadata'][0]['ns']:
                row_errors.append('invalid delivery ordering')
        if explicit:
            owned_events = [e for e in events if owned(e)]
            row_errors.extend(i['reason'] for i in issues if i.get('line') in {e['line'] for e in owned_events})
            paired = {s[edge]['line'] for s in window for edge in ('begin', 'end')}
            if any(e['edge'] != 'point' and e['line'] not in paired for e in owned_events):
                row_errors.append('incomplete lifetime spans')
            if any(s['role'] == 'unknown' for s in row['timeline']):
                row_errors.append('unsupported span attribution')
            demand_jobs = {e['job'] for e in owned_events if e['phase'] in ('demand_dispatch', 'pool_job', 'selected_worker', 'pixels', 'metadata')}
            if len(demand_jobs) != 1 or 0 in demand_jobs:
                row_errors.append('discontinuous demand job')
            if begin.get('version') == 3:
                outer = [s for s in window if s['phase'] == 'construction_outer']
                complete = row['boundaries']['construction_complete']
                if not (len(origins) == len(outer) == len(complete) == 1 and
                        origins[0]['ns'] <= outer[0]['start'] <= construction['start'] <=
                        construction['stop'] <= outer[0]['stop'] <= complete[0]['ns'] <= end['ns']):
                    row_errors.append('invalid startup boundaries')
                selected = [e for e in owned_events if e['phase'] == 'selected_worker']
                for execution in [s for s in window if s['phase'] == 'pool_job']:
                    b = execution['begin']
                    links = [e for e in selected if e['job'] == b['job'] and e['worker'] == b['worker'] and
                             e['preparation'] == b['preparation'] and e['ns'] <= execution['start']]
                    ready = [e for e in owned_events if e['phase'] == 'preparation_ready' and
                             e['preparation'] == b['preparation'] and e['worker'] == b['worker'] and e['ns'] <= execution['start']]
                    if len(links) != 1 or (b['preparation'] and len(ready) != 1):
                        row_errors.append('unsupported selected worker preparation')
        if variant in ('C', 'D') and not job:
            row['standby_overlap_ms'] = None
        if row_errors:
            row['status'] = 'partial'
            row['unknown'].extend(sorted(set(row_errors)))
            row['standby_overlap_ms'] = None
            issues.extend({'kind': 'observation_contract', 'file': source, 'sample': index, 'reason': reason}
                          for reason in sorted(set(row_errors)))
    unassigned = [s for s in spans if s['begin']['line'] not in used]
    for span in unassigned:
        span['cause'] = 'setup_activity' if len(constructions) > 1 and span['start'] < constructions[1]['start'] and span['stop'] <= constructions[1]['start'] else 'genuine_ambiguity'
    return rows, issues, unassigned


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')


def analyze(root, output, invocation):
    root, output = root.resolve(), output.resolve()
    if output == root or root in output.parents:
        raise ValueError('output must be outside retained experiment')
    output.mkdir()  # Exclusive: never overwrite evidence or an earlier analysis.
    inputs = set(root.glob('*.json')) | set(root.glob('*.py')) | {root / 'trace.h'}
    for base in [root / 'diagnostic', root / 'pilot']:
        inputs.update(base.glob('*/source-inventory.json'))
        inputs.update(base.glob('*/binary-inventory.json'))
        inputs.update(base.glob('*/harness-source/*'))
        inputs.update(base.glob('*/source/**/src/isolated/*.cpp'))
        inputs.update(base.glob('*/source/**/src/preview/*.cpp'))
    for mode in ('diagnostic', 'pilot'):
        inputs.update((root / (mode + '-observations')).glob('*'))
    inputs = sorted(p for p in inputs if p.is_file())
    before = {str(p): digest(p) for p in inputs}
    before[str(Path(__file__).resolve())] = digest(Path(__file__).resolve())
    write_json(output / 'invocation.json', invocation)
    all_rows, issues, inventories, unassigned, trace_records = [], [], [], [], []
    for mode in ('diagnostic', 'pilot'):
        for path in sorted((root / (mode + '-observations')).glob('*.json')):
            match = re.fullmatch(r'(warmup|block-\d+)-([ABCD])-(.+)\.json', path.name)
            if not match:
                issues.append({'kind': 'unexpected_observation_file', 'file': str(path)})
                continue
            tag, label, fixture = match.groups()
            samples = json.loads(path.read_text())['samples']
            inventories.append({'mode': mode, 'tag': tag, 'variant': label, 'fixture': fixture, 'count': len(samples), 'file': str(path)})
            expected = 1 if tag == 'warmup' else 10
            if len(samples) != expected:
                issues.append({'kind': 'observation_count_mismatch', 'file': str(path), 'expected': expected, 'actual': len(samples)})
            if mode == 'diagnostic':
                log = path.with_suffix('.log')
                events, spans, errors = parse_trace(log.read_text(), str(log))
                trace_records.extend(events)
                rows, errors2, remaining = account(events, spans, samples, str(log), label)
                issues.extend(errors + errors2)
                unassigned.extend(remaining)
            else:
                rows = [{'sample': i, 'latencies': {k: s.get(k) for k in ('first_ms', 'final_ms')}, 'status': 'uninstrumented'} for i, s in enumerate(samples)]
            for row in rows:
                row.update(mode=mode, tag=tag, variant=label, fixture=fixture, warmup=tag == 'warmup')
            all_rows.extend(rows)
    measured = [r for r in all_rows if not r['warmup']]
    summary = []
    for mode in ('diagnostic', 'pilot'):
        for label in 'ABCD':
            for fixture in sorted({r['fixture'] for r in measured}):
                rows = [r for r in measured if (r['mode'], r['variant'], r['fixture']) == (mode, label, fixture)]
                summary.append({'mode': mode, 'variant': label, 'fixture': fixture, 'observations': len(rows),
                                'latencies': {k: distribution([r['latencies'][k] for r in rows if r['latencies'][k] is not None]) for k in ('first_ms', 'final_ms')},
                                'phases': {p: {'present': sum(bool(r.get('phases', {}).get(p)) for r in rows),
                                               'absent_by_design': sum(r.get('phase_absence', {}).get(p) == 'absent_by_design' for r in rows),
                                               'missing_or_unknown': sum(not r.get('phases', {}).get(p) and r.get('phase_absence', {}).get(p) != 'absent_by_design' for r in rows),
                                               'distribution': distribution([r['phases'][p]['union_ms'] for r in rows if r.get('phases', {}).get(p)])} for p in PHASES} if mode == 'diagnostic' else None})
    retained = json.loads((root / 'result.json').read_text())
    overlap = {}
    for label in 'CD':
        rows = [r for r in measured if r['mode'] == 'diagnostic' and r['variant'] == label]
        actual = sum((r.get('standby_overlap_ms') or 0) > 0 for r in rows)
        expected = 400 if label == 'C' else 0
        if retained['overlap'][label]['overlapping_requests'] != expected:
            issues.append({'kind': 'retained_overlap_contract', 'variant': label})
        overlap[label] = {'observations': len(rows), 'resolved': sum(r.get('standby_overlap_ms') is not None for r in rows), 'actual': actual, 'retained': expected}
        if actual != expected or overlap[label]['resolved'] != 400:
            issues.append({'kind': 'overlap_analysis_failure', 'variant': label, **overlap[label]})
    for mode in ('diagnostic', 'pilot'):
        if sum(r['mode'] == mode for r in measured) != 1600:
            issues.append({'kind': 'corpus_count_failure', 'mode': mode})
    for mode in ('diagnostic', 'pilot'):
        if sum(r['mode'] == mode and r['warmup'] for r in all_rows) != 16:
            issues.append({'kind': 'warmup_count_failure', 'mode': mode})
    causes = defaultdict(list)
    for span in unassigned:
        causes[span['cause']].append(span['begin'])
    for row in all_rows:
        for span in row.get('timeline', []):
            if span['role'] in ('shutdown', 'service_control'):
                causes['recoverable_service_activity'].append(span['begin'])
            elif span['role'] == 'unknown':
                causes['genuine_ambiguity'].append(span['begin'])
    causes['missing_instrumentation'] = [dict(file=r['observation_file'], sample=r['sample'], reason=reason) for r in all_rows for reason in r.get('identity_limitations', [])]
    causes['missing_instrumentation'] += [{'file': i['file'], 'kind': i['kind']} for i in issues if 'delivery' in i['kind']]
    write_json(output / 'attribution-audit.json', {k: {'count': len(v), 'examples': v[:8]} for k, v in sorted(causes.items())})
    write_json(output / 'trace-records.json', trace_records)
    write_json(output / 'accounting.json', all_rows)
    write_json(output / 'inventory.json', inventories)
    write_json(output / 'issues.json', {'issues': issues, 'unassigned_spans': unassigned})
    write_json(output / 'summary.json', {'groups': summary, 'overlap': overlap})
    report(output, root, measured, summary, overlap, issues, unassigned)
    after = {p: digest(Path(p)) for p in before}
    write_json(output / 'input-manifest.json', {'before': before, 'after': after, 'unchanged': before == after})
    if before != after:
        raise RuntimeError('consumed inputs changed during analysis')
    return issues


def report(output, root, rows, summary, overlap, issues, unassigned):
    lines = ['# Retained startup bottleneck assessment', '',
             f'Conclusion: {len(issues)} analysis failures; attribution remains incomplete. Qualification remains failed and D’s failed pilot is unchanged. Prepared tracing does not authorize execution.', '',
             '## Coverage and method', '',
             f'Measured diagnostic observations: {sum(r["mode"] == "diagnostic" for r in rows)}. Separate pilot observations: {sum(r["mode"] == "pilot" for r in rows)}. Warm-ups are inventoried separately in inventory.json and accounting.json.',
             f'Parser/correlation failures: {len(issues)}; unassigned spans (including setup): {len(unassigned)}. Unsupported per-observation associations: {sum(len(r.get("unknown", [])) for r in rows)}. Every unsupported record is retained in accounting.json or issues.json.', '',
             'Spans match by process/thread/object/slot/phase with LIFO nesting; request labels are retained but never used as identity. Chronological construction and matching deliveries establish sample windows. Pool jobs establish worker/slot context; preparation containment distinguishes demand and standby. Synchronous pool shutdown containment recovers shutdown and enclosed cleanup; activity outside supported contexts remains unknown, including previous-service activity. No address alone establishes ownership.', '',
             'Durations use interval unions. Nested validation remains inclusive within helper preparation; these are overlapping measurements, never additive components. Uncovered intervals are unnamed elapsed time. Median uses the sample median; p95 uses nearest rank ceil(n*0.95), matching the retained harness tooling. Missing phases are null, never zero; generation validation/acquisition in A are separately marked absent by design.', '',
             'Constructor tracing omits member initialization. There is no exact startup-origin marker. The observable construction-to-metadata window excludes earlier startup work and is not a complete critical path. JSON latency is never subtracted from a trace timestamp to infer origin. Inspect/decode exchanges include transport. A validates inside helper preparation; B/C/D validate/acquire generations before demand helper preparation, so helper preparation boundaries are not equivalent across those variants. Cleanup can follow delivery and is annotated separately.', '',
             'Pilot samples are uninstrumented and cannot be joined to diagnostic samples. The retained pilot failed the required large-PNG improvement gate; instrumented timings establish neither qualification nor causation.', '',
             '## Distributions (ms)', '', '| Mode | Variant | Fixture | n | Pixels median / p95 | Metadata median / p95 |', '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for group in summary:
        a, b = (group['latencies'][k] for k in ('first_ms', 'final_ms'))
        lines.append(f'| {group["mode"]} | {group["variant"]} | {group["fixture"]} | {group["observations"]} | {a["median"]:.3f} / {a["p95"]:.3f} | {b["median"]:.3f} / {b["p95"]:.3f} |')
    lines += ['', 'The observable large-PNG phases include substantial validation, demand helper preparation and decode exchange spans. Their relative boundaries differ: A helper preparation contains runtime validation, while protected B/C/D generation validation contains runtime validation separately. C/D remove no validation requirement. The overlap cross-check must reproduce retained counts before supporting a statement about removal of concurrent standby preparation; discrepancies remain analysis failures. The separate failed pilot supplies no evidence of a startup improvement. Missing startup-origin and lifecycle linkage markers prevent complete attribution of the tails.', '', '## Diagnostic phase coverage and timings', '', '| Variant | Fixture | Phase | Present | Absent by design | Missing/unknown | Median / p95 ms |', '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for group in summary:
        if group['mode'] != 'diagnostic':
            continue
        for phase, value in group['phases'].items():
            d = value['distribution']
            timing = f'{d["median"]:.3f} / {d["p95"]:.3f}' if d else 'unavailable'
            lines.append(f'| {group["variant"]} | {group["fixture"]} | {phase} | {value["present"]} | {value["absent_by_design"]} | {value["missing_or_unknown"]} | {timing} |')
    lines += ['', '## Overlap cross-check', '', '```json', json.dumps(overlap, indent=2), '```', '',
              'Any discrepancy is an analysis failure; retained results are never adjusted.', '', '## Large-PNG tail observations', '',
              'Five slowest per variant and event, ties ordered by block/sample. Offsets below use the first traced constructor instruction, not startup origin. Each timeline lists phase, role and start/end milliseconds. Inclusive overlaps are visible; independent phase quantiles are never added or differenced for attribution.']
    for label in 'ABCD':
        candidates = [r for r in rows if r['mode'] == 'diagnostic' and r['variant'] == label and r['fixture'] == '3200x2400.png']
        for metric in ('first_ms', 'final_ms'):
            lines += ['', f'### {label}: {metric}', '']
            for r in sorted(candidates, key=lambda r: (-r['latencies'][metric], r['tag'], r['sample']))[:5]:
                timeline = r['timeline']
                if not r.get('covered_union_ms'):
                    continue
                origin = next(s['start'] for s in timeline if s['phase'] == 'service_construction')
                file = Path(r['observation_file'])
                link = os.path.relpath(file, output)
                lines += [f'- [{r["tag"]} sample {r["sample"]}]({link}) {r["latencies"][metric]:.3f} ms; covered union {r["covered_union_ms"]:.3f} ms; observable window {r["observable_window_ms"]:.3f} ms; unknown spans {len(r["unknown"])}.', '', '```text']
                for s in timeline:
                    ref = s['begin']
                    lines.append(f'{(s["start"]-origin)/1e6:9.3f}..{(s["stop"]-origin)/1e6:9.3f} {s["phase"]} [{s["role"]}]' + (' after delivery' if s['after_delivery'] else '') + f' line {ref["line"]}..{s["end"]["line"]}')
                for gap in r['uncovered_intervals_ns']:
                    lines.append(f'{(gap[0]-origin)/1e6:9.3f}..{(gap[1]-origin)/1e6:9.3f} uncovered elapsed interval')
                for p in r.get('deliveries', []):
                    lines.append(f'{(p["ns"]-origin)/1e6:9.3f} {p["phase"]} line {p["line"]}')
                lines += ['```', '', f'[Original trace]({os.path.relpath(file.with_suffix(".log"), output)})', '']
    lines += ['## Required markers before another experiment', '',
              'Add a monotonic startup-origin marker before construction, a unique service generation propagated to every worker/control event, explicit demand/job and standby identifiers, and shutdown begin/end linked to that generation. Trace member initialization or mark its boundaries. Mark validation completion, demand dispatch, readiness, delivery and cleanup with the same generation/job identity. These markers would distinguish unobserved pre-constructor work, delivery gaps and previous-service cleanup. Their absence prevents complete tail attribution; this report recommends no scheduling experiment.', '',
              '[Machine-readable accounting](accounting.json), [phase summaries](summary.json), [unsupported records](issues.json), [all trace points including readiness](trace-records.json), [input hashes](input-manifest.json), [exact invocation](invocation.json).', '']
    audit = json.loads((output / 'attribution-audit.json').read_text())
    lines += ['## Attribution audit', '']
    for cause, value in audit.items():
        lines += [f'- {cause}: {value["count"]} spans/records.']
        for ref in value['examples'][:3]:
            lines += [f'  - [{Path(ref["file"]).name}:{ref.get("line", "?")}]({os.path.relpath(ref["file"], output)})']
    lines += ['', 'The saved harness destroys each startup service before constructing the next; pool shutdown waits for both worker threads. This permits recovery of pool shutdown cleanup by containment and controller validation/acquisition on its established owner thread, including activity after delivery. Such control work is not relabeled standby. Audit counts include diagnostic warm-ups; missing-instrumentation counts are observations lacking identities, while activity counts are spans.', '', f'[Saved harness]({os.path.relpath(root / "diagnostic/C/harness-source/reuse.cpp", output)}), [C lifecycle]({os.path.relpath(root / "diagnostic/C/source/holonight-file-browser/src/preview/session_pool.cpp", output)}), [D lifecycle]({os.path.relpath(root / "diagnostic/D/source/holonight-file-browser/src/preview/session_pool.cpp", output)}), [A lifecycle]({os.path.relpath(root / "diagnostic/A/source/holonight-file-browser/src/preview/preview_service.cpp", output)}), [B lifecycle]({os.path.relpath(root / "diagnostic/B/source/holonight-file-browser/src/preview/preview_service.cpp", output)}).', '', 'Historical identities remain unavailable. Unobserved generation phases in A are absent by design; other absent spans remain missing or ambiguous. Setup activity is reported separately. Shutdown ownership requires the same pool and synchronous shutdown containment.', '']
    (output / 'ASSESSMENT.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    issues = analyze(args.experiment, args.output, {'argv': sys.argv, 'cwd': str(Path.cwd())})
    print(json.dumps({'output': str(args.output), 'analysis_failures': len(issues)}))
    return bool(issues)


if __name__ == '__main__':
    sys.exit(main())
