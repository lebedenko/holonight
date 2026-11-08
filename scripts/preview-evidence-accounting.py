#!/usr/bin/env python3
"""Diagnostic-only accounting. Parent and helper clocks are never combined."""
import json

PHASES = ('capture', 'runtime_validation', 'launcher_readiness', 'request_transfer',
          'response_receipt_validation', 'acknowledgement_exit', 'cleanup')


def telemetry(text):
    records, errors = [], []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith('HN_DIAG '):
            continue
        try:
            row = json.loads(line[8:])
            if not isinstance(row, dict) or not isinstance(row.get('event'), str):
                raise ValueError('not a telemetry record')
            records.append(row)
        except (ValueError, TypeError) as error:
            errors.append({'line': number, 'error': str(error)})
    trailers = [r for r in records if r['event'] == 'flush']
    pending = 0
    mismatches = []
    for row in records:
        if row['event'] == 'flush':
            if row.get('records') != pending:
                mismatches.append({'claimed': row.get('records'), 'observed': pending})
            pending = 0
        else:
            pending += 1
    return records, {'malformed': errors, 'missing_flush': not trailers or pending != 0,
                     'record_count_mismatches': mismatches,
                     'dropped': sum(r.get('dropped', 0) for r in trailers)}


def interval(row):
    try:
        start, end = int(row['begin_ns']), int(row['end_ns'])
        return (start, end) if 0 <= start <= end else None
    except (KeyError, ValueError, TypeError):
        return None


def union_duration(intervals):
    end, total = -1, 0
    for start, finish in sorted(intervals):
        total += max(0, finish - max(start, end))
        end = max(end, finish)
    return total


def account(text):
    rows, diagnostics = telemetry(text)
    grouped = {}
    for row in rows:
        if row.get('operation'):
            grouped.setdefault((row.get('pid'), row['operation']), []).append(row)
    operations = []
    for (pid, identifier), records in grouped.items():
        phases = {}
        for phase in PHASES:
            observations = [interval(r) for r in records if r['event'] == phase]
            phases[phase] = {'intervals_ns': observations,
                             'missing': not observations or any(v is None for v in observations)}
        spans = [interval(r) for r in records if r['event'] == 'provider_call']
        outer = spans[0] if len(spans) == 1 else None
        known = [span for phase in phases.values() for span in phase['intervals_ns'] if span is not None]
        if outer and all(outer[0] <= a <= b <= outer[1] for a, b in known):
            unexplained = outer[1] - outer[0] - union_duration(known)
        else:
            unexplained = None
        helpers = []
        for row in records:
            if row['event'] == 'helper_telemetry':
                helper_rows, helper_errors = telemetry(row.get('stderr', ''))
                helpers.append({'records': helper_rows, 'diagnostics': helper_errors,
                                'truncated': row.get('truncated', True)})
        operations.append({'pid': pid, 'operation': identifier,
                           'consumers': sorted({r.get('consumer', '') for r in records}),
                           'phases': phases, 'parent_unexplained_ns': unexplained,
                           'helper_timelines': helpers, 'helper_telemetry_missing': not helpers,
                           'results': [r for r in records if r['event'] == 'provider_result']})
    consumers = []
    consumer_groups = {}
    for row in rows:
        if row.get('consumer'):
            consumer_groups.setdefault((row.get('pid'), row['consumer']), []).append(row)
    for (pid, identifier), records in consumer_groups.items():
        dispatch = [r for r in records if r['event'] == 'consumer_dispatch']
        entry = [r for r in records if r['event'] == 'worker_entry']
        workers = [interval(r) for r in records if r['event'] == 'worker_execution']
        calls = [interval(r) for r in records if r['event'] == 'provider_call']
        span = workers[0] if len(workers) == 1 else None
        complete_calls = [value for value in calls if value is not None]
        unexplained = None
        if span and len(calls) == len(complete_calls) and all(span[0] <= a <= b <= span[1] for a, b in complete_calls):
            unexplained = span[1] - span[0] - union_duration(complete_calls)
        try:
            queue = int(entry[0]['ns']) - int(dispatch[0]['ns']) if len(entry) == len(dispatch) == 1 else None
        except (KeyError, ValueError, TypeError):
            queue = None
        consumers.append({'pid': pid, 'consumer': identifier, 'dispatch_to_worker_ns': queue,
                          'worker_interval_ns': span, 'worker_outside_provider_ns': unexplained,
                          'provider_calls': len(calls),
                          'publications': sum(r['event'] == 'result_publication' for r in records),
                          'delivered': sum(r['event'] == 'consumer_delivery' for r in records),
                          'final_deliveries': sum(r['event'] == 'consumer_delivery' and r.get('final', False) for r in records)})
    return {'qualifying_latency': False, 'operations': operations, 'consumers': consumers, 'diagnostics': diagnostics,
            'counts': {event: sum(r['event'] == event for r in rows) for event in sorted({r['event'] for r in rows})},
            'cleanup_failures': sum(r['event'] == 'cleanup_result' and not r.get('verified', False) for r in rows),
            'records': rows}


def preserve_attempt(output, attempt, raw_text, log_text, returncode):
    """Flush an attempt even when the harness died or left a truncated final row."""
    samples, errors = [], []
    for number, line in enumerate(raw_text.splitlines(), 1):
        try:
            samples.append(json.loads(line))
        except ValueError as error:
            errors.append({'line': number, 'error': str(error)})
    diagnostics = account(log_text)
    cleanup_failure = returncode == 20 or diagnostics['cleanup_failures'] > 0 or any(
        r.get('sample', {}).get('cleanup_failure') or r.get('setup', {}).get('cleanup_failure') for r in samples)
    result = {'attempt': attempt, 'harness_exit': returncode, 'samples': samples,
              'incomplete': bool(errors) or not samples or returncode != 0,
              'parse_errors': errors, 'diagnostics': diagnostics, 'cleanup_failure': cleanup_failure}
    with output.open('a') as stream:
        stream.write(json.dumps(result) + '\n')
        stream.flush()
    return result
