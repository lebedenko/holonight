#!/usr/bin/env python3
"""Offline supplemental v4 accounting; original v3 parsing remains unchanged."""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('delivery_history', ROOT / 'scripts/analyze-preview-delivery-gaps-v3.py')
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)
a = history.a
IDENTITIES = ('service', 'observation', 'job', 'worker', 'preparation', 'generation', 'session', 'transaction', 'publication')
FIELDS = {'version', 'ns', 'pid', 'tid', *IDENTITIES, 'endpoint', 'operation', 'edge', 'span', 'outcome'}
CATEGORIES = {
    'transaction': ('transaction_wrapper', 'oneshot_ack', 'helper_exit', 'reusable_completion_ack', 'retirement_call', 'effective_cleanup'),
    'storage': ('store_raster', 'store_raster_delegate', 'thumbnail_store', 'png_serialization', 'storage_commit'),
    'metadata': ('metadata_format', 'memory_insert'),
    'delivery': ('enqueue_call', 'callback_execution', 'apply_result', 'changed_emission', 'harness_execution'),
}


def identity(event):
    return tuple(event[k] for k in ('pid', *IDENTITIES, 'endpoint'))


def analyze(text, source, variant, samples=None):
    events, issues, unavailable = [], [], []
    for line, raw in enumerate(text.splitlines(), 1):
        if 'DELIVERY' not in raw:
            continue
        ref = dict(file=source, line=line)
        try:
            if not raw.startswith('DELIVERY '):
                raise ValueError('noncanonical prefix')
            def unique(pairs):
                value = {}
                for k, v in pairs:
                    if k in value:
                        raise ValueError('duplicate JSON key')
                    value[k] = v
                return value
            e = json.loads(raw[9:], object_pairs_hook=unique)
            if set(e) != FIELDS or e['version'] != 4 or type(e['version']) is not int:
                raise ValueError('invalid schema/version')
            if any(type(e[k]) is not int or e[k] < (0 if k == 'ns' else 1) for k in ('ns', 'pid', 'tid')):
                raise ValueError('invalid clock/process/thread')
            if any(e[k] is not None and (type(e[k]) is not int or e[k] < 1) for k in (*IDENTITIES, 'span')):
                raise ValueError('unknown identity must be null; known identity must be positive integer')
            if any(type(e[k]) is not str or not e[k] for k in ('endpoint', 'operation', 'edge', 'outcome')):
                raise ValueError('invalid string field')
            if e['endpoint'] not in ('unavailable', 'pixel_result', 'final_result'):
                raise ValueError('invalid endpoint')
            if e['edge'] not in ('begin', 'end', 'point') or (e['edge'] != 'point' and e['span'] is None) or (e['edge'] == 'point' and e['span'] is not None):
                raise ValueError('invalid edge/span')
            events.append(dict(e, **ref))
        except (ValueError, TypeError, KeyError) as error:
            issues.append(dict(ref, reason=str(error), raw=raw))
    if not events:
        unavailable.append(dict(reason='no_supplemental_records'))
    jobs = defaultdict(set)
    for e in events:
        if e['job'] is not None and e['generation'] is not None:
            jobs[e['pid'], e['service'], e['job']].add(e['generation'])
        if e['operation'].startswith('endpoint_') and (e['publication'] is None or any(e[k] is None for k in ('service', 'observation', 'job', 'worker', 'generation'))):
            unavailable.append(dict(reason='endpoint_identity_unavailable', record=e))
    for key, generations in jobs.items():
        if len(generations) > 1:
            issues.append(dict(reason='job_crosses_generations', job=key, generations=sorted(generations)))
    # Group by explicit process/span identity. Do not sort timestamps to repair ordering.
    groups = defaultdict(list)
    for e in events:
        if e['edge'] != 'point':
            groups[e['pid'], e['span']].append(e)
    spans = []
    for key, values in groups.items():
        begin = [e for e in values if e['edge'] == 'begin']
        end = [e for e in values if e['edge'] == 'end']
        if len(begin) > 1 or len(end) > 1:
            issues.append(dict(reason='ambiguous_span', records=values))
            continue
        if not begin or not end:
            unavailable.append(dict(reason='missing_span_boundary', records=values))
            continue
        b, e = begin[0], end[0]
        if identity(b) != identity(e) or (b['tid'], b['operation']) != (e['tid'], e['operation']):
            issues.append(dict(reason='incompatible_span_identity', records=values))
        elif b['ns'] > e['ns']:
            issues.append(dict(reason='impossible_span_order', records=values))
        else:
            spans.append(dict(operation=b['operation'], start=b['ns'], stop=e['ns'], inclusive_ns=e['ns']-b['ns'], begin=b, end=e))
    publications = defaultdict(list)
    for e in events:
        if e['publication'] is not None:
            publications[e['pid'], e['publication']].append(e)
    handoffs = []
    for key, values in publications.items():
        if len({identity(e) for e in values}) != 1:
            issues.append(dict(reason='incompatible_publication_identity', records=values))
            continue
        owned = [s for s in spans if (s['begin']['pid'], s['begin']['publication']) == key]
        def select(op):
            found = [s for s in owned if s['operation'] == op]
            if len(found) > 1:
                issues.append(dict(reason='ambiguous_publication_operation', operation=op, records=found))
            return found[0] if len(found) == 1 else None
        enqueue, callback, applied, changed = (select(op) for op in ('enqueue_call', 'callback_execution', 'apply_result', 'changed_emission'))
        row = dict(pid=key[0], publication=key[1], identity=values[0], endpoints=[])
        if enqueue:
            row['enqueue_call_ns'] = enqueue['inclusive_ns']
        if callback:
            row['callback_execution_ns'] = callback['inclusive_ns']
        if not enqueue or not callback:
            row['unavailable'] = 'missing_enqueue_or_callback'
        elif callback['start'] < enqueue['start']:
            issues.append(dict(reason='callback_before_enqueue', records=[enqueue, callback]))
        else:
            row['enqueue_to_callback_elapsed_ns'] = callback['start']-enqueue['start']
        # A callback may execute before the enqueue call returns on another thread.
        if callback and applied and (callback['begin']['tid'] != applied['begin']['tid'] or not callback['start'] <= applied['start'] <= applied['stop'] <= callback['stop']):
            issues.append(dict(reason='apply_outside_callback', records=[callback, applied]))
        decisions = [e for e in values if e['operation'] == 'result_decision']
        if len(decisions) != 1:
            row['decision_unavailable'] = 'missing_or_ambiguous_decision'
            if len(decisions) > 1:
                issues.append(dict(reason='ambiguous_result_decision', records=decisions))
        else:
            decision = decisions[0]
            if decision['outcome'] not in ('accepted', 'stale', 'cancelled', 'timed_out'):
                issues.append(dict(reason='invalid_result_decision', records=decisions))
            if applied and not applied['start'] <= decision['ns'] <= applied['stop']:
                issues.append(dict(reason='decision_outside_apply', records=decisions))
            if decision['outcome'] != 'accepted' and changed:
                issues.append(dict(reason='rejected_result_emitted_changed', records=[changed, decision]))
        if changed and (not applied or changed['begin']['tid'] != applied['begin']['tid'] or not applied['start'] <= changed['start'] <= changed['stop'] <= applied['stop']):
            issues.append(dict(reason='changed_outside_apply', records=[changed]))
        for endpoint in ('pixels', 'metadata'):
            endpoints = [e for e in values if e['operation'] == 'endpoint_' + endpoint]
            captures = [e for e in values if e['operation'] == 'latency_capture']
            entries = [e for e in values if e['operation'] == 'harness_entry']
            for e in endpoints:
                if not changed or len(captures) != 1 or len(entries) != 1 or not (changed['begin']['tid'] == e['tid'] == entries[0]['tid'] == captures[0]['tid'] and changed['start'] <= entries[0]['ns'] <= captures[0]['ns'] <= e['ns'] <= changed['stop']):
                    issues.append(dict(reason='invalid_endpoint_attribution', records=[e, *captures, *entries]))
            if len(endpoints) > 1:
                issues.append(dict(reason='ambiguous_endpoint', records=endpoints))
            row['endpoints'].extend(dict(endpoint=endpoint, record=e) for e in endpoints)
        handoffs.append(row)
    # Cleanup only counts explicit effective work, never historical retirement envelopes.
    cleanups = defaultdict(list)
    for s in spans:
        if s['operation'] == 'effective_cleanup':
            if s['end']['outcome'] not in ('verified', 'unverified', 'exception'):
                issues.append(dict(reason='invalid_cleanup_outcome', records=[s]))
            if s['begin']['session'] is not None:
                cleanups[s['begin']['pid'], s['begin']['session']].append(s)
        if s['operation'] == 'retirement_call' and s['end']['outcome'] not in ('already_retired', 'effective_retirement', 'exception'):
            issues.append(dict(reason='invalid_retirement_outcome', records=[s]))
    for values in cleanups.values():
        if len(values) > 1:
            issues.append(dict(reason='multiple_effective_cleanups', records=values))
    if variant != 'A':
        for call in (s for s in spans if s['operation'] == 'retirement_call'):
            nested = [s for s in spans if s['operation'] == 'effective_cleanup' and
                      identity(s['begin']) == identity(call['begin']) and
                      call['start'] <= s['start'] <= s['stop'] <= call['stop']]
            absent = [e for e in events if e['operation'] == 'effective_cleanup' and e['edge'] == 'point' and
                      e['outcome'] == 'not_launched' and identity(e) == identity(call['begin']) and
                      call['start'] <= e['ns'] <= call['stop']]
            if call['end']['outcome'] == 'already_retired' and (nested or absent):
                issues.append(dict(reason='noop_retirement_performed_cleanup', records=[call, *nested, *absent]))
            if call['end']['outcome'] == 'effective_retirement':
                if len(nested) + len(absent) > 1:
                    issues.append(dict(reason='ambiguous_retirement_cleanup', records=[call, *nested, *absent]))
                elif not nested and not absent:
                    unavailable.append(dict(reason='missing_effective_retirement_outcome', record=call))
    v3_events, v3_spans, v3_issues = a.parse_trace(text, source)
    historical = dict(events=v3_events, spans=v3_spans, issues=v3_issues, validation='parser_only; harness samples unavailable')
    if samples is not None:
        historical = history.v.overhead.validate_trace(text, samples, source, variant)
        historical['validation'] = 'historical_lifecycle_accounting'
    issues.extend(historical['issues'])
    # Supplemental endpoint evidence must agree with explicitly matching v3 identities.
    for e in events:
        if not e['operation'].startswith('endpoint_'):
            continue
        endpoint = e['operation'][9:]
        matching = [v for v in v3_events if v['phase'] == endpoint and v['edge'] == 'point' and
                    all((v.get(k) or None) == e[k] for k in ('pid', 'service', 'observation', 'job', 'worker', 'preparation'))]
        if v3_events and len(matching) != 1:
            issues.append(dict(reason='missing_or_ambiguous_v3_endpoint', records=[e, *matching]))
    windows = []
    for row in handoffs:
        for endpoint in row['endpoints']:
            e = endpoint['record']
            if any(e[k] is None for k in ('service', 'observation', 'job', 'worker', 'generation')):
                windows.append(dict(endpoint=endpoint['endpoint'], publication=row['publication'], unavailable='endpoint_identity_unavailable'))
                continue
            decodes = [s for s in v3_spans if s['phase'] == 'decode_exchange_including_transport' and all((s['begin'].get(k) or None) == e[k] for k in ('pid', 'service', 'observation', 'job', 'worker', 'preparation'))]
            window = dict(endpoint=endpoint['endpoint'], publication=row['publication'])
            if len(decodes) != 1:
                window['unavailable'] = 'missing_or_ambiguous_decode'
            elif decodes[0]['stop'] > e['ns']:
                issues.append(dict(reason='endpoint_before_decode_end', records=[e, decodes[0]]))
            else:
                start, stop = decodes[0]['stop'], e['ns']
                eligible = [s for s in spans if all(s['begin'][k] == e[k] for k in ('pid', 'service', 'observation', 'job', 'worker', 'generation'))]
                clipped = [(max(start, s['start']), min(stop, s['stop'])) for s in eligible if s['start'] < stop and s['stop'] > start]
                window.update(start_ns=start, stop_ns=stop, union_ns=round(a.duration(clipped)*1e6), clipped_union_ns=a.union(clipped),
                              categories={category: a.union([(max(start, s['start']), min(stop, s['stop'])) for s in eligible if s['operation'] in ops and s['start'] < stop and s['stop'] > start]) for category, ops in CATEGORIES.items()}, boundary=decodes[0]['end'], delivery=e)
            windows.append(window)
    report = dict(status='blocked' if issues else 'complete', variant=variant, events=events, spans=spans,
                  handoffs=handoffs, windows=windows, historical=historical, issues=issues, unavailable=unavailable,
                  categories={category: dict(spans=[s for s in spans if s['operation'] in ops], union_ns=a.union([(s['start'], s['stop']) for s in spans if s['operation'] in ops])) for category, ops in CATEGORIES.items()},
                  cleanup_availability='observed' if cleanups else 'unavailable',
                  limitations='Inclusive durations are not additive. Enqueue-to-callback is elapsed time, not pure queue residence. Missing boundaries are unavailable. No diagnostic overhead estimate.')
    if issues:
        report['assessment_available'] = False
    else:
        report['assessment_available'] = True
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--variant', choices=list('ABCD'), required=True)
    parser.add_argument('--samples', type=Path, help='Original harness JSON; enable full historical lifecycle validation')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        report = analyze(args.trace.read_text(), str(args.trace.resolve()), args.variant,
                         json.loads(args.samples.read_text())['samples'] if args.samples else None)
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return int(report['status'] == 'blocked')


if __name__ == '__main__':
    sys.exit(main())
