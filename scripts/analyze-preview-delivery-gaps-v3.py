#!/usr/bin/env python3
"""Offline delivery-gap audit of retained v3 traces and frozen source."""
import argparse
from collections import Counter, defaultdict
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('startup_v3', ROOT / 'scripts/analyze-preview-startup-v3.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
a = v.a
IDENTITY = ('pid', 'service', 'observation', 'job', 'worker', 'request')


def compatible(left, right):
    return all(left[k] == right[k] for k in IDENTITY)


def interval(row, endpoint, boundary):
    deliveries = [e for e in row['deliveries'] if e['phase'] == endpoint]
    if len(deliveries) != 1:
        return dict(unavailable='missing_or_ambiguous_delivery')
    delivery = deliveries[0]
    decodes = [s for s in row['timeline'] if s['phase'] == 'decode_exchange_including_transport'
               and s['role'] == 'demand' and compatible(s['begin'], delivery)]
    if len(decodes) != 1:
        return dict(unavailable='missing_decode' if not decodes else 'ambiguous_decode')
    decode = decodes[0]
    if decode['stop'] > delivery['ns']:
        return dict(unavailable='decode_ends_after_delivery')
    selected = decode
    if boundary == 'cleanup':
        cleanup = [s for s in row['timeline'] if s['phase'] == 'cleanup' and s['role'] == 'demand'
                   and compatible(s['begin'], decode['begin'])
                   and decode['stop'] <= s['start'] <= s['stop'] <= delivery['ns']]
        if len(cleanup) != 1:
            return dict(unavailable='absent_cleanup' if not cleanup else 'ambiguous_cleanup')
        selected = cleanup[0]
    start, end = selected['stop'], delivery['ns']
    spans = [dict(s, clipped_start=max(start, s['start']), clipped_stop=min(end, s['stop']))
             for s in row['timeline'] if s['start'] < end and s['stop'] > start]
    covered = [(s['clipped_start'], s['clipped_stop']) for s in spans
               if s['phase'] in a.PHASES and s['role'] in ('demand', 'service_control')]
    gaps = a.gaps(start, end, covered)
    return dict(start_ns=start, end_ns=end, elapsed_ms=(end-start)/1e6,
                boundary=selected['end'], delivery=delivery, covered_intervals_ns=a.union(covered),
                covered_union_ms=a.duration(covered), uncovered_intervals_ns=gaps,
                uncovered_ms=a.duration(gaps), intervening_spans=spans,
                intervening_markers=[e for e in row.get('markers', []) if start <= e['ns'] <= end])


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
        item = dict(mode=mode, variant=variant, fixture=fixture, endpoint=endpoint, block=block,
                    observations=len(values), harness_latency_context_ms=a.distribution([
                        r['latencies']['first_ms' if endpoint == 'pixels' else 'final_ms'] for r in values]))
        if mode == 'T':
            item['intervals'] = {}
            for boundary in ('decode', 'cleanup'):
                windows = [r['intervals'][endpoint][boundary] for r in values]
                present = [w for w in windows if 'unavailable' not in w]
                item['intervals'][boundary] = dict(present=len(present), unavailable_reasons=dict(Counter(
                    w['unavailable'] for w in windows if 'unavailable' in w)), **{
                    k: a.distribution([w[k] for w in present]) for k in ('elapsed_ms', 'covered_union_ms', 'uncovered_ms')})
        result.append(item)
    return result


def examples(rows):
    result = []
    for tail in v.select_tails(rows):
        variant, endpoint = tail['variant'], tail['endpoint']
        values = [r for r in rows if r['mode'] == 'T' and not r['warmup']
                  and r['variant'] == variant and r['fixture'] == '3200x2400.png']
        key = 'first_ms' if endpoint == 'pixels' else 'final_ms'
        median = a.distribution([r['latencies'][key] for r in values])
        near = sorted(values, key=lambda r: (abs(r['latencies'][key]-median['median']), r['block'], r['sample']))[:5] if values else []
        result.append(dict(variant=variant, endpoint=endpoint, tails=tail['observations'], median_near=near))
    return result


# Each file is retained independently per variant; no cross-variant equivalence is assumed.
SOURCE_FILES = {
    'runtime': 'source/holonight-images/src/isolated/runtime.cpp',
    'client': 'source/holonight-images/src/isolated/client.cpp',
    'cleanup': 'source/holonight-images/src/isolated/cleanup.cpp',
    'protocol': 'source/holonight-images/src/isolated/protocol.cpp',
    'preview': 'source/holonight-file-browser/src/preview/preview_service.cpp',
    'thumbnail': 'source/holonight-file-browser/src/preview/thumbnail_service.cpp',
    'store': 'source/holonight-thumbnails/src/cache.cpp',
    'harness': 'harness-source/reuse.cpp',
}


def source_map(root, prep, seal, read):
    result = []
    for variant in 'ABCD':
        files = {}
        for operation, name in SOURCE_FILES.items():
            category, relative = name.split('/', 1)
            path = root / (variant + 'T') / name
            content = read(path, prep['pairs'][variant + 'T'][category][relative])
            # Full function context is retained, with exact line numbers and hashes.
            files[operation] = dict(file=str(path), sha256=a.digest(path), first_line=1,
                                    last_line=len(content.splitlines()), text=content)
        trace_path = root / 'trace.h'
        trace_text = read(trace_path, seal['trace.h'])
        files['trace'] = dict(file=str(trace_path), sha256=a.digest(trace_path), first_line=1,
                              last_line=len(trace_text.splitlines()), text=trace_text)
        operations = []
        definitions = [
            ('exchange', 'runtime', 'StandbyTrace::Scope trace(command.operation', 'demand worker',
             'Decode operation selects decode_exchange_including_transport; RAII scope includes response parsing/checks and return.'),
            ('response_processing', 'protocol', 'Reply parseReply(', 'demand worker',
             'Called inside exchange; validates response and constructs decoded result before exchange end.'),
            ('transaction_completion', 'runtime', 'auto reply = exchange(', 'demand worker',
             'A/B acknowledge helper, wait for exit and cleanup before return; C/D session success validates completion acknowledgement before return.'),
            ('transaction_return', 'client', 'IsolatedClient::sourceTransaction(', 'demand worker',
             'One-shot wrapper calls run; reusable wrapper calls run with persistent execution when ready.'),
            ('raster_storage_branch', 'preview', 'ThumbnailService::storeRaster(', 'demand worker',
             'Requires decodedSource, tier, successful outcome and unchangedSource; cancellation checks surround publication.'),
            ('raster_storage_delegate', 'thumbnail', 'void storeRaster(', 'calling demand worker',
             'Synchronous cacheRequest and HolonightThumbnails::store call.'),
            ('storage_implementation', 'store', 'bool store(', 'calling demand worker',
             'Conditional request/size/directory checks, tagging, QSaveFile open/permissions, PNG save, commit; cancellation/error exits.'),
            ('pixel_publication', 'preview', 'result.final = false;', 'demand worker',
             'Publishes non-final image before EXIF formatting and conditional memory-cache insertion.'),
            ('metadata_preparation', 'preview', 'result.image = {};', 'demand worker',
             'PNG/JPEG EXIF formatting; cache insertion requires successful outcome, unchangedSource and no cancellation; final result returned.'),
            ('queued_handoff', 'preview', 'const auto publish = [this]', 'worker to service QObject thread',
             'Qt::QueuedConnection captures result and trace context; callback calls applyResult; worker may continue concurrently.'),
            ('apply_result', 'preview', 'void PreviewService::applyResult(', 'service QObject thread',
             'Rejects cancelled/stale/timed-out results, applies image/facts/busy state, then notifyChanged emits changed.'),
            ('harness_capture', 'harness', 'const auto connection = QObject::connect', 'application callback thread',
             'changed callback captures elapsed latency before separate pixels and metadata trace probes; endpoint predicates differ.'),
        ]
        for operation, name, anchor, thread, ordering in definitions:
            f = files[name]
            matches = [i for i, line in enumerate(f['text'].splitlines(), 1) if anchor in line]
            if operation in ('pixel_publication', 'metadata_preparation'):
                raster_end = next(i for i, line in enumerate(f['text'].splitlines(), 1) if 'PreviewResult decodeSvg(' in line)
                storage_line = next(i for i, line in enumerate(f['text'].splitlines(), 1) if 'ThumbnailService::storeRaster(' in line)
                matches = [i for i in matches if storage_line < i < raster_end]
            if len(matches) != 1:
                raise ValueError(f'ambiguous source operation: {variant} {operation}')
            start = max(1, matches[0]-3)
            # Context ranges preserve branch conditions and downstream calls; full text remains available.
            stop = min(f['last_line'], matches[0] + (90 if operation in ('exchange', 'transaction_completion', 'apply_result', 'storage_implementation') else 40))
            operations.append(dict(operation=operation, file=f['file'], sha256=f['sha256'],
                                   first_line=start, last_line=stop, thread=thread,
                                   static_order_and_conditions=ordering,
                                   observed_execution='Not established for conditional operations by source alone'))
        result.append(dict(variant=variant, files=files, operations=operations))
    return result


def analyze(root, prior, output):
    root, prior, output = (p.resolve() for p in (root, prior, output))
    if ROOT / 'build' not in output.parents or any(p == output or p in output.parents or output in p.parents for p in (root, prior)):
        raise ValueError('fresh output must be under ignored build/ and disjoint from both inputs')
    if '/build/' not in (ROOT / '.gitignore').read_text().splitlines():
        raise ValueError('build/ must be ignored')
    output.mkdir()
    before, issues, rows, inventory, sources, selected, summary = {}, [], [], [], [], [], []
    counts = {}

    def read(path, expected=None):
        path = path.resolve()
        digest = a.digest(path)
        before[str(path)] = digest
        if expected is not None and digest != expected:
            raise ValueError('integrity mismatch: ' + str(path))
        return path.read_text()

    def load(path, expected=None):
        return json.loads(read(path, expected))

    try:
        for name in ('analyze-preview-delivery-gaps-v3.py', 'analyze-preview-startup-v3.py',
                     'measure-preview-tracing-overhead.py', 'run-preview-startup-smoke.py', 'analyze-preview-startup.py'):
            read(ROOT / 'scripts' / name)
        integrity = load(prior / 'input-integrity.json')
        if not integrity['unchanged'] or integrity['before'] != integrity['after']:
            raise ValueError('prior integrity was not unchanged')
        for name, expected in integrity['before'].items():
            read(Path(name), expected)
        if load(prior / 'assessment.json')['status'] != 'complete':
            raise ValueError('prior analysis is blocked')
        # Reparse raw inputs using unchanged historical validation, then reconcile all outputs.
        if v.analyze(root, output / 'revalidated-startup'):
            raise ValueError('historical parser/lifecycle validation failed')
        for name in ('inventory', 'accounting', 'setup-activity', 'phase-summary', 'attribution-issues', 'tails', 'assessment'):
            old = load(prior / (name + '.json'))
            new = load(output / 'revalidated-startup' / (name + '.json'))
            if old != new:
                raise ValueError('prior reconciliation differs: ' + name)
        rows = load(prior / 'accounting.json')
        inventory = load(prior / 'inventory.json')
        counts = load(prior / 'assessment.json')['counts']
        if len(rows) != 2424:
            raise ValueError('observation count differs')
        seal = load(root / 'seal.json')
        prep = load(root / 'preparation.json', seal['preparation.json'])
        sources = source_map(root, prep, seal, read)
        for row in rows:
            if row['mode'] == 'T':
                row['intervals'] = {e: {b: interval(row, e, b) for b in ('decode', 'cleanup')}
                                    for e in ('pixels', 'metadata')}
        selected, summary = examples(rows), summarize(rows)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        issues.append(dict(reason=str(error)))
    after = {}
    for name in before:
        try:
            after[name] = a.digest(Path(name))
        except OSError:
            after[name] = None
    if before != after:
        issues.append(dict(reason='consumed inputs changed during analysis'))
    status = 'blocked' if issues else 'complete'
    for name, data in [('inventory', inventory), ('intervals', rows), ('summary', summary),
                       ('source-path-map', sources), ('selected-examples', selected), ('issues', issues),
                       ('input-integrity', dict(before=before, after=after, unchanged=before == after)),
                       ('assessment', dict(status=status, counts=counts, issues=issues))]:
        a.write_json(output / (name + '.json'), data)
    report(root, output, status, sources, selected, summary, issues)
    return int(bool(issues))


def report(root, output, status, sources, selected, summary, issues):
    def link(e):
        return f"[{Path(e['file']).name}:{e['line']}]({os.path.relpath(e['file'], output)}#L{e['line']})"

    lines = ['# Retained startup delivery gaps', '', f'Status: {status}.', '',
             'Decode exchange includes response transport, parseReply, final checks and scope exit. Its end is not helper decode completion. The intervals below end at separate pixel and metadata harness probes, after latency capture.', '',
             'Coverage is the intersecting historical phase union; inclusive durations are not additive. Broad envelopes and standby work appear as context only. All gaps remain unnamed elapsed time. Warm-ups, setup and post-delivery work are excluded from measured summaries. U is separate harness-latency context.', '',
             f'[Overhead assessment]({os.path.relpath(root / "FINAL-ASSESSMENT.md", output)}): the host-activity limitation applies. No overhead is subtracted, no thresholds introduced. C’s failed qualification and D’s failed pilot remain unchanged.', '',
             '[Inventory](inventory.json), [intervals](intervals.json), [pooled/block summaries](summary.json), [source map](source-path-map.json), [examples](selected-examples.json), [issues](issues.json), [integrity](input-integrity.json).', '']
    for source in sources:
        lines += [f"## {source['variant']} source path", '']
        for name, f in source['files'].items():
            # Emit exact source excerpts around all relevant operations, independently per variant.
            tokens = {'runtime': ('decode_exchange', 'parseReply', 'completion', 'cleanup(', 'return result'),
                      'trace': ('struct Scope', '~Scope', 'CLOCK_MONOTONIC'),
                      'cleanup': ('CleanupReport cleanup', 'void finishCleanup'),
                      'client': ('sourceTransaction', 'run<DecodeResult>', 'completionAcknowledged'),
                      'protocol': ('Reply parseReply',),
                      'preview': ('storeRaster', 'publish(result)', 'ExifReader::format', 'cache.insert', 'applyResult(', 'notifyChanged()', 'Qt::QueuedConnection'),
                      'thumbnail': ('void storeRaster', 'HolonightThumbnails::store'),
                      'store': ('bool store(', 'tagged.save', 'file.commit', 'ensureDirectory'),
                      'harness': ('clock.start', 'QObject::connect', 'const auto latency', 'StandbyTrace::event("pixels"', 'StandbyTrace::event("metadata"')}[name]
            hits = [i for i, line in enumerate(f['text'].splitlines(), 1) if any(t in line for t in tokens)]
            lines += [f"{name}: SHA-256 `{f['sha256']}`. " + ', '.join(link(dict(file=f['file'], line=i)) for i in hits) + '.', '']
        for op in source['operations']:
            lines += [f"{op['operation']}: {link(dict(file=op['file'], line=op['first_line']))}–{link(dict(file=op['file'], line=op['last_line']))}; thread: {op['thread']}. {op['static_order_and_conditions']}", '']
        lines += ['Successful-path source order: exchange response parsing → transaction completion (one-shot acknowledgement, exit and verified cleanup for A/B; reusable completion acknowledgement for C/D) → result checks → conditional storeRaster → enqueue pixel result → EXIF formatting for PNG/JPEG → conditional memory-cache insertion → return final result → enqueue final result. Worker-side publication enqueues callbacks; application of pixels can overlap subsequent worker metadata work. Each queued callback runs applyResult on the service thread, validates generation/cancellation, updates state and emits changed; the harness callback captures latency before its delivery probe.', '',
                  'storeRaster delegates synchronously to HolonightThumbnails::store: request and size checks, directory preparation, image tagging, QSaveFile open/permissions, PNG serialization and commit, with cancellation/error exits. This branch requires decodedSource, a tier, successful raster outcome and unchangedSource; the source alone proves neither branch execution nor its duration in a sample. Cache insertion also checks cancellation, outcome and unchangedSource. Existing exchange/cleanup probes do not isolate these operations or the queue handoff.', '']
    lines += ['## Pooled measured T intervals', '', '| Variant | Fixture | Endpoint | Boundary | Present | Elapsed median/p95 ms | Unnamed median/p95 ms | Unavailable |', '|---|---|---|---|---:|---:|---:|---|']
    for g in summary:
        if g['mode'] != 'T' or g['block'] != 'pooled':
            continue
        for b, w in g['intervals'].items():
            def fmt(key):
                d = w[key]
                return f"{d['median']:.6f}/{d['p95']:.6f}" if d else 'unavailable'
            lines.append(f"| {g['variant']} | {g['fixture']} | {g['endpoint']} | {b} | {w['present']} | {fmt('elapsed_ms')} | {fmt('uncovered_ms')} | {w['unavailable_reasons']} |")
    for cell in selected:
        for kind in ('tails', 'median_near'):
            lines += ['', f"## {cell['variant']} {cell['endpoint']} {kind}", '', 'Median-near examples are descriptive comparisons, not matched controls.', '']
            for r in cell[kind]:
                lines += [f"### Invocation {r['index']}, block {r['block']}, sample {r['sample']}", '']
                for b, w in r['intervals'][cell['endpoint']].items():
                    if 'unavailable' in w:
                        lines += [f"{b}: {w['unavailable']}.", '']
                        continue
                    lines += [f"{b}: {w['elapsed_ms']:.6f} ms; covered {w['covered_union_ms']:.6f} ms; unnamed {w['uncovered_ms']:.6f} ms. Boundary {link(w['boundary'])} → delivery {link(w['delivery'])}. Gaps (absolute ns): `{w['uncovered_intervals_ns']}`.", '', '| Span/marker | Role | Clipped ns | Raw evidence |', '|---|---|---|---|']
                    for s in w['intervening_spans']:
                        lines.append(f"| {s['phase']} | {s['role']} | {s['clipped_start']}–{s['clipped_stop']} | {link(s['begin'])}, {link(s['end'])} |")
                    for e in w['intervening_markers']:
                        lines.append(f"| {e['phase']} | {e['role']} | {e['ns']} | {link(e)} |")
                    lines.append('')
    lines += ['', 'Boundary availability: B has multiple compatible demand cleanup spans in the selected interval, so its cleanup boundary is ambiguous. C/D have no applicable demand cleanup before delivery, consistent with reusable completion; absence does not imply zero time. Decode-end intervals remain separate from both cases.', '', '## Minimum missing boundaries', '',
              'Retained evidence does not resolve attribution. Add these boundaries in this order to distinguish the remaining explanations; this audit implements none:', '',
              '1. Transaction completion acknowledgement and transaction return, distinguishing one-shot helper exit/cleanup from reusable-session completion; distinguish effective retirement from subsequent retirement calls with an operation/reason identity (B has repeated cleanup spans). Retain the existing exchange boundary.',
              '2. storeRaster branch decision (including skip reason), entry and return, with nested PNG serialization and commit boundaries; metadata formatting and memory-cache insertion entry/return and skip reasons.',
              '3. Pixel and final-result enqueue, callback entry, applyResult entry/return and changed emission, linked to each harness latency capture/probe. Separate queue residence from worker work and callback execution.',
              'All records need monotonic timestamps, pid/tid, invocation, observation, service lifetime, request/generation, job, worker/session/transaction, endpoint and publication sequence. Propagate the publication identity across the worker-to-service queued handoff and signal-to-harness callback; record actual executing thread independently of propagated context. Include branch outcome and cancellation/staleness rejection. These wall-clock boundaries still cannot establish CPU or scheduler attribution.', '']
    if issues:
        lines += ['Blocked issues: `' + json.dumps(issues) + '`. Partial evidence is preserved.', '']
    (output / 'ASSESSMENT.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('retained_package', type=Path)
    parser.add_argument('startup_analysis', type=Path)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    sys.exit(analyze(args.retained_package, args.startup_analysis, args.output_directory))
