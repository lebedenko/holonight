#!/usr/bin/env python3
"""Summarize diagnostic evidence without merging it into qualifying A/B latency."""
import argparse
import hashlib
import importlib.util
from collections import Counter, defaultdict
import json
from pathlib import Path
import statistics


def distribution(values, expected):
    values = [v for v in values if v is not None]
    return {'observations': len(values), 'missing': expected - len(values),
            'median': statistics.median(values) if values else None,
            'maximum': max(values) if values else None}


def mixed_fixture_batch(row):
    names = ['160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg']
    operations = row.get('sample', row.get('setup', {})).get('operations', [])
    return (row.get('scheduler_threads') == 2 and row.get('box_pixels') == 256
            and row.get('fixture_cycle') == names and len(operations) == 16
            and [r.get('source_fixture') for r in operations] == names * 4)


def summarize(root):
    provenance = json.loads((root / 'provenance.json').read_text())
    attempts = [json.loads(line) for line in (root / 'attempts.jsonl').read_text().splitlines()] if (root / 'attempts.jsonl').exists() else []
    spec = importlib.util.spec_from_file_location('accounting', Path(__file__).with_name('preview-evidence-accounting.py'))
    accounting = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(accounting)
    phases = defaultdict(list)
    consumer_phases = defaultdict(list)
    kind_counts = Counter()
    kind_phases = defaultdict(lambda: defaultdict(list))
    consumer_count = 0
    counters = Counter()
    scheduler = defaultdict(list)
    samples = []
    operation_results = []
    resources = []
    settled = []
    helper_phases = defaultdict(list, {'helper_provider_execution': [], 'helper_reply_serialization': []})
    missing_helper = 0
    operation_count = 0
    pre_ack = []
    for attempt in attempts:
        samples.extend(attempt['samples'])
        command = provenance['commands'][attempt['attempt']]
        log = Path(command[-1]).with_suffix('.log')
        diagnostics = accounting.account(log.read_text()) if log.exists() else attempt['diagnostics']
        for consumer in diagnostics.get('consumers', []):
            consumer_count += 1
            for key in ('dispatch_to_worker_ns', 'worker_outside_provider_ns'):
                consumer_phases[key].append(consumer[key]/1e6 if consumer[key] is not None else None)
        counters.update(diagnostics['counts'])
        operation_count += len(diagnostics['operations'])
        for operation in diagnostics['operations']:
            kind = next((r.get('kind', 'unknown') for r in diagnostics['records']
                         if r.get('operation') == operation['operation'] and r['event'] == 'provider_begin'), 'unknown')
            kind_counts[kind] += 1
            operation_results.extend(operation['results'])
            phases['parent_unexplained'].append(
                operation['parent_unexplained_ns'] / 1e6 if operation['parent_unexplained_ns'] is not None else None)
            for name, observations in operation['phases'].items():
                intervals = observations['intervals_ns']
                duration = sum((b-a)/1e6 for a, b in intervals) if intervals and all(intervals) else None
                phases[name].append(duration)
                kind_phases[kind][name].append(duration)
            found = set()
            for timeline in operation['helper_timelines']:
                for row in timeline['records']:
                    if row['event'] in ('helper_provider_execution', 'helper_reply_serialization'):
                        try:
                            helper_phases[row['event']].append((int(row['end_ns'])-int(row['begin_ns']))/1e6)
                            found.add(row['event'])
                        except (KeyError, ValueError):
                            pass
            missing_helper += len(found) != 2
        for row in diagnostics['records']:
            if row['event'].startswith('post_drain_'):
                settled.append(row)
            if row['event'] == 'pre_ack_resources':
                pre_ack.append(row)
        if provenance['kind'] == 'scheduler':
            command = provenance['commands'][attempt['attempt']]
            label = Path(command[0]).parents[1].name
            scheduler[label + '-' + command[3]].extend(attempt['samples'])
    for file in root.glob('*.resources.jsonl'):
        rows = [json.loads(line) for line in file.read_text().splitlines()]
        resources.append({'file': file.name, 'ticks': len(rows),
                          **{key: distribution([row.get(key) for row in rows], len(rows)) for key in
                             ('parent_rss_bytes', 'concurrent_scope_bytes', 'concurrent_parent_plus_scope_bytes')},
                          'maximum_observed_interval_ms': max(((b['monotonic_ns'] - a['monotonic_ns'])/1e6
                                                               for a, b in zip(rows, rows[1:])), default=None)})
    grid = {}
    for name, rows in scheduler.items():
        timed = [row.get('sample', {}) for row in rows]
        grid[name] = {'attempts': len(rows), 'missing_attempts': 100 - len(rows),
                      'mixed_fixture_batches': sum(mixed_fixture_batch(row) for row in rows),
                      'excluded_workload_batches': sum(not mixed_fixture_batch(row) for row in rows),
                      'failures': sum(not row.get('success', False) for row in timed),
                      'setup_failures': sum(bool(row.get('setup')) and not row['setup'].get('success') for row in rows),
                      'wall_ms': distribution([row.get('wall_ms') for row in timed], len(rows)),
                      'counts': {key: sum(row.get(key, 0) for row in timed) for key in
                                 ('issued', 'started', 'cancelled_before_start', 'cancelled_after_start', 'delivered', 'finished')},
                      'missing_counts': {key: sum(key not in row for row in timed) for key in
                                         ('issued', 'started', 'cancelled_before_start', 'cancelled_after_start', 'delivered')},
                      'undrained': sum(not row.get('drained', False) for row in timed)}
    for label in provenance.get('variants', ['A', 'B']):
        for workload in ('cold', 'warm', 'cancel'):
            if provenance['kind'] == 'scheduler':
                grid.setdefault(label + '-' + workload, {'attempts': 0, 'missing_attempts': 100})
    expected = 600 if provenance['kind'] == 'scheduler' else (280 if provenance['kind'] == 'diagnostic' else 84)
    failed = sum(not r.get('sample', r).get('success', False) or
                 (bool(r.get('setup')) and not r['setup'].get('success', False)) for r in samples)
    exclusion = json.loads((root / 'EXCLUSION.json').read_text()) if (root / 'EXCLUSION.json').exists() else None
    excluded = len(samples) if exclusion else (sum(not mixed_fixture_batch(r) for r in samples) if grid else 0)
    completed = sum(bool(r.get('sample')) for r in samples) if grid else len(samples)
    requested = sum(int(c[4]) for c in provenance['commands'])
    attempted = len(samples)
    unreported = sum(a['incomplete'] and len(a['samples']) < int(provenance['commands'][a['attempt']][4]) for a in attempts)
    return {'variants': provenance.get('variants', ['A', 'B'] if grid else ['D']),
            'denominators': {'planned': expected, 'attempted': attempted, 'completed': completed,
                             'failed': failed, 'excluded': excluded, 'missing': expected - len(samples),
                             'missing_measurements': expected - completed, 'requested_sample_slots': requested, 'attempts_with_unreported_slots': unreported},
            'kind': provenance['kind'], 'qualifying_latency': False, 'stopped': provenance['stopped'],
            'attempted_invocations': len(attempts), 'harness_exits': dict(Counter(str(a['harness_exit']) for a in attempts)),
            'incomplete_invocations': sum(a['incomplete'] for a in attempts),
            'exclusion': exclusion,
            'sample_observations': len(samples), 'missing_samples': expected - len(samples),
            'service_failures': sum(not r.get('success', False) for r in samples) if not grid else None,
            'service_setup_failures': sum(not r.get('setup_success', False) for r in samples) if not grid else None,
            'analysis_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'accounting_sha256': hashlib.sha256(Path(__file__).with_name('preview-evidence-accounting.py').read_bytes()).hexdigest(),
            'consumer_jobs': consumer_count, 'consumer_phases_ms': {k: distribution(v, consumer_count) for k, v in consumer_phases.items()},
            'operation_kinds': dict(kind_counts),
            'phases_by_operation_kind_ms': {kind: {name: distribution(values, kind_counts[kind]) for name, values in fields.items()} for kind, fields in kind_phases.items()},
            'provider_operations': operation_count, 'provider_results': len(operation_results),
            'provider_results_missing': operation_count - len(operation_results),
            'provider_runtime_statuses': dict(Counter(str(r['runtime']) for r in operation_results)),
            'counters': dict(counters), 'parent_phases_ms': {k: distribution(v, operation_count) for k, v in phases.items()},
            'helper_phases_ms': {k: distribution(v, operation_count) for k, v in helper_phases.items()},
            'missing_helper_timelines': missing_helper,
            'telemetry_errors': [a['diagnostics']['diagnostics'] for a in attempts
                                 if a['diagnostics']['diagnostics']['malformed'] or a['diagnostics']['diagnostics']['dropped'] or a['diagnostics']['diagnostics'].get('record_count_mismatches')
                                 or (provenance['kind'] != 'scheduler' and a['diagnostics']['diagnostics']['missing_flush'])],
            'pre_ack_resources': pre_ack,
            'individual_scope_memory_peak_bytes': distribution([int(r['memory_peak']) if r.get('memory_peak', '').strip().isdigit() else None for r in pre_ack], operation_count),
            'scope_cpu_usage_usec': distribution([next((int(line.split()[1]) for line in r.get('cpu_stat', '').splitlines() if line.startswith('usage_usec ') and line.split()[1].isdigit()), None) for r in pre_ack], operation_count),
            'missing_pre_ack_resources': operation_count - len(pre_ack),
            'pre_ack_cpu_unavailable': sum(not r.get('cpu_stat') for r in pre_ack),
            'pre_ack_memory_unavailable': sum(not r.get('memory_peak') for r in pre_ack),
            'settled_observations': settled, 'resource_passes': resources, 'scheduler': grid}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    report = summarize(args.run)
    (args.run / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Diagnostic evidence (not qualifying A/B latency)', '',
             f'Variants: {", ".join(report["variants"])}.',
             f'Denominators: {json.dumps(report["denominators"], sort_keys=True)}.',
             f'Kind: {report["kind"]}; samples: {report["sample_observations"]}; missing: {report["missing_samples"]}.',
             f'Stop reason: {report["stopped"] or "none"}. Harness exits: {report["harness_exits"]}.', '',
             'Durations below are nested observations. Do not add parent and helper phases.', '',
             '| Timeline / phase | Observed | Missing | Median ms | Maximum ms |',
             '| --- | ---: | ---: | ---: | ---: |']
    for timeline in ('parent_phases_ms', 'helper_phases_ms'):
        for phase, values in report[timeline].items():
            lines.append(f'| {timeline}/{phase} | {values["observations"]} | {values["missing"]} | '
                         f'{values["median"]} | {values["maximum"]} |')
    if report['exclusion']:
        lines += ['', '**Excluded workload:** ' + report['exclusion']['reason']]
    if report['scheduler']:
        lines += ['', '| Control | Attempts | Mixed-fixture batches | Failures | Issued | Started | Cancelled before / after entry | Delivered |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for name, result in report['scheduler'].items():
            counts = result.get('counts', {})
            lines.append(f'| {name} | {result["attempts"]} | {result.get("mixed_fixture_batches", 0)} | '
                         f'{result.get("failures", "missing")} | {counts.get("issued", "missing")} | '
                         f'{counts.get("started", "missing")} | {counts.get("cancelled_before_start", "missing")} / '
                         f'{counts.get("cancelled_after_start", "missing")} | {counts.get("delivered", "missing")} |')
    lines += ['', 'Provider execution includes all helper provider work; it is not a codec-only duration.',
              'Sampled concurrent resource peaks are reported per pass in summary.json. Individual cgroup memory.peak',
              'observations remain separate and are never summed. Missing reads remain explicit.',
              'One-second post-drain snapshots are observations, not proof of leak freedom.',
              'Scheduler results concern response delivery, not rendered QML frames.', '']
    (args.run / 'report.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
