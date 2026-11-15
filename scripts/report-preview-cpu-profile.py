#!/usr/bin/env python3
"""Offline, non-additive stack views and exclusive userspace self attribution."""
import argparse
from collections import Counter, defaultdict
import importlib.util
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


validation = module('cpu_validation_report', 'report-preview-validation.py')
require, read, write, o = validation.require, validation.read, validation.write, validation.o
CATEGORIES = ('hashing/dispatch', 'Qt I/O/buffering', 'userspace copying', 'demonstrated probe logging', 'other/unresolved')
HEADER = re.compile(r'^\s*(.*?)\s+(\d+)/(\d+)\s+(\d+)\.(\d+):\s+(\d+)\s+cpu-clock:u:\s+(.*)$')
FRAME = re.compile(r'^\s*([0-9a-f]+)\s+(.+?)\s+\((.*)\)\s*$')


def parse(text):
    samples, tasks = [], []
    current = None
    for number, line in enumerate(text.splitlines(), 1):
        require(not any(token in line for token in ('PERF_RECORD_LOST', 'PERF_RECORD_THROTTLE', 'PERF_RECORD_AUX')),
                'capture loss/throttling')
        if 'PERF_RECORD_' in line:
            tasks.append(dict(line=number, text=line))
            current = None
            continue
        match = HEADER.match(line)
        if match:
            comm, pid, tid, seconds, fraction, period, tail = match.groups()
            require(len(fraction) <= 9 and int(period) > 0, 'invalid sample timestamp/period')
            current = dict(pid=int(pid), tid=int(tid), ns=int(seconds)*10**9 + int(fraction.ljust(9, '0')),
                           period=int(period), line=number, frames=[], header_frame=tail, comm=comm.strip())
            samples.append(current)
        elif current and line.strip():
            frame = FRAME.match(line)
            require(frame is not None, 'malformed stack frame at line ' + str(number))
            address, symbol, dso = frame.groups()
            current['frames'].append(dict(ip=address, symbol=symbol, dso=dso, line=number))
        elif not line.strip():
            current = None
        elif line.strip() and not line.startswith('#'):
            raise ValueError('unparsed perf export line ' + str(number) + ': ' + line[:120])
    for sample in samples:
        if not sample['frames']:
            frame = FRAME.match(sample['header_frame'])
            if frame:
                address, symbol, dso = frame.groups()
                sample['frames'] = [dict(ip=address, symbol=symbol, dso=dso, line=sample['line'])]
        sample['truncated'] = not sample['frames'] or len(sample['frames']) >= 127
    return dict(samples=samples, tasks=tasks)


def distribution(values):
    values = sorted(values)
    return dict(count=len(values), minimum=values[0], median=statistics.median(values),
                p95=values[math.ceil(.95*len(values))-1], maximum=values[-1]) if values else dict(count=0)


def symbol_index(symbols, run=subprocess.check_output):
    result = {}
    for name, identity in symbols.items():
        text = run(['nm', '-S', '-n', '-C', '--defined-only', identity['path']], text=True)
        names = defaultdict(list)
        for line in text.splitlines():
            match = re.match(r'^[0-9a-f]+\s+([0-9a-f]+)\s+[tTwW]\s+(.+)$', line)
            if match:
                size, symbol = match.groups()
                if int(size, 16):
                    names[symbol].append(int(size, 16))
        result[name] = dict(names)
    return result


def resolved(frame, index):
    """Accept only explicit sized symbol ranges; never nearest exported names."""
    match = re.match(r'^(.*?)(?:\+0x([0-9a-f]+))?$', frame['symbol'])
    name, offset = match.groups()
    offset = int(offset or '0', 16)
    dso = Path(frame['dso']).name
    library = next((lib for lib in index if dso == lib or dso.startswith(lib.split('.so')[0] + '.so.')), None)
    sizes = index.get(library, {}).get(name, [])
    return name if sizes and all(offset < size for size in sizes) else None


def classify(frames, index):
    names = [resolved(frame, index) for frame in frames]
    leaf = names[0] if names else None
    if leaf is None:
        return CATEGORIES[-1]
    if re.search(r'(sha256|sha2_|SHA256|SHA2_|EVP_(?:Digest|MD)|QCryptographicHash::|ossl_.*(?:sha256|digest))', leaf):
        return CATEGORIES[0]
    if re.search(r'^(?:__)?(?:memcpy|memmove|mempcpy|bcopy)', leaf):
        return CATEGORIES[2]
    if re.search(r'^(QFile|QFileDevice|QIODevice|QRingBuffer|QFSFileEngine|QAbstractFileEngine|QFileSystemEngine)::', leaf):
        return CATEGORIES[1]
    # Generic formatting/write routines are logging only with an explicit probe
    # frame, whose sized range must also have been independently resolved.
    if any(name and name.startswith(('ValidationTrace::', 'DeliveryTrace::', 'StandbyTrace::')) for name in names):
        return CATEGORIES[3]
    return CATEGORIES[-1]


def attribute(samples, windows, index):
    """Half-open monotonic spans, local pid/tid identities, no nearest matching."""
    rows = []
    for window in windows:
        selected = [s for s in samples if (s['pid'], s['tid']) == (window['pid'], window['tid']) and
                    window['start'] <= s['ns'] < window['stop']]
        counts = Counter({key: 0 for key in CATEGORIES})
        periods = Counter({key: 0 for key in CATEGORIES})
        inclusive = Counter()
        unresolved = truncated = 0
        for sample in selected:
            category = classify(sample['frames'], index)
            counts[category] += 1; periods[category] += sample['period']
            unresolved += sum(resolved(f, index) is None for f in sample['frames'])
            truncated += sample['truncated']
            # Inclusive symbols are a separate non-additive presence count.
            inclusive.update(set(resolved(f, index) or ('unresolved:' + f['ip'] + ':' + f['dso']) for f in sample['frames']))
        total = len(selected); period = sum(periods.values())
        rows.append(dict(window=window, sample_count=total, recorded_period=period,
                         counts=dict(counts), periods=dict(periods), unresolved_frames=unresolved,
                         truncated_stacks=truncated, inclusive=dict(inclusive),
                         count_shares={k: counts[k]/total for k in CATEGORIES} if total else None,
                         period_shares={k: periods[k]/period for k in CATEGORIES} if period else None,
                         sample_lines=[s['line'] for s in selected]))
    return rows


def windows(observations, setup):
    result = []
    for row in observations:
        part = row['validation']
        for file in part['files']:
            for span in file['operations']:
                if span['operation'] == 'read_hash':
                    result.append(dict(pid=span['begin']['pid'], tid=span['begin']['tid'],
                        observation=row['observation'], service=span['begin']['service'],
                        start=span['start'], stop=span['stop'], ordinal=file['ordinal'], path=file['path'], setup=False))
    for group in setup:
        for file in group['validation']['files']:
            for span in file['operations']:
                if span['operation'] == 'read_hash':
                    result.append(dict(pid=span['begin']['pid'], tid=span['begin']['tid'], observation=None,
                        service=group['service'], start=span['start'], stop=span['stop'],
                        ordinal=file['ordinal'], path=file['path'], setup=True))
    for i, left in enumerate(result):
        for right in result[i+1:]:
            require((left['pid'], left['tid']) != (right['pid'], right['tid']) or
                    max(left['start'], right['start']) >= min(left['stop'], right['stop']), 'overlapping sample ownership')
    return result


def account(target, text, observations, index=None):
    capture = parse(text)
    require(capture['samples'] and capture['tasks'], 'missing samples/task identity records')
    setup = read(target.with_suffix('.validation-setup.json'))
    if index is None:
        execution = target.parents[1]
        package = Path(read(execution / 'preregistration.json')['package'])
        cache = execution / 'symbol-index.json'
        if cache.exists():
            index = read(cache)
        else:
            index = symbol_index(read(package / 'symbols.json'))
            # Include unstripped probe-owning binaries and providers explicitly.
            sources = {str(path): dict(path=str(path)) for path in [
                validation.r.v.ROOT / 'build/preview-validation-20261115-04-built/validation/C/reuse-harness/preview-benchmark',
                *list((validation.r.v.ROOT / 'build/preview-validation-20261115-04-built/validation/C/prefix/lib').glob('*.so'))]}
            extra = symbol_index(sources)
            for name, names in extra.items(): index[Path(name).name] = names
            write(cache, index)
    rows = attribute(capture['samples'], windows(observations, setup), index)
    value = dict(capture=capture, files=rows,
                 outside_read_hash_samples=len(capture['samples']) - sum(r['sample_count'] for r in rows))
    write(target.with_suffix('.cpu.json'), value)
    return value


def rehearsal(target, text):
    capture = parse(text)
    markers = [json.loads(line) for line in target.with_suffix('.stdout').read_text().splitlines()]
    begins = {(m['pid'], m['tid']): m['start_ns'] for m in markers if 'start_ns' in m}
    ends = {(m['pid'], m['tid']): m['stop_ns'] for m in markers if 'stop_ns' in m}
    require(begins.keys() == ends.keys() and len(begins) == 3, 'synthetic thread/descendant identity mismatch')
    gate = read(target.parent / (target.stem + '-recording') / 'gate.json')
    require(any(pid == tid == gate['pid'] for pid, tid in begins), 'gate exec changed PID')
    for key, start in begins.items():
        samples = [s for s in capture['samples'] if (s['pid'], s['tid']) == key and start <= s['ns'] < ends[key]]
        require(samples and any(len(s['frames']) > 1 for s in samples), 'inheritance/timestamp/stack rehearsal failed')
    write(target.with_suffix('.verified.json'), dict(passed=True, identities=[list(key) for key in begins],
          samples=len(capture['samples']), tasks=capture['tasks']))


def aggregate(files):
    counts = {k: sum(f['counts'][k] for f in files) for k in CATEGORIES}
    periods = {k: sum(f['periods'][k] for f in files) for k in CATEGORIES}
    n, period = sum(counts.values()), sum(periods.values())
    return dict(sample_count=n, recorded_period=period, counts=counts, periods=periods,
                count_shares={k: counts[k]/n for k in CATEGORIES} if n else None,
                period_shares={k: periods[k]/period for k in CATEGORIES} if period else None,
                unresolved_frames=sum(f['unresolved_frames'] for f in files),
                truncated_stacks=sum(f['truncated_stacks'] for f in files))


def tails(rows, field):
    if not rows: return []
    values = sorted(r[field] for r in rows)
    cutoff = values[max(0, math.ceil(.95*len(values))-1)]
    return [dict(invocation=r['invocation'], observation=r['observation'], value=r[field],
                 sampled=r.get('sampled')) for r in rows if r[field] >= cutoff]


def report(execution, output):
    o.fresh(output, execution)
    result = dict(status='blocked')
    try:
        o.check_output(execution)
        assessment = read(execution / 'assessment.json')
        require(assessment['status'] == 'complete', 'experiment stopped: ' + assessment.get('failure', 'unknown'))
        rows, setup, warmups = [], [], []
        for entry in assessment['invocations']:
            invocation = entry['entry']['invocation']; target = Path(entry['entry']['argv'][-1])
            observations = read(target.with_suffix('.cpu-observations.json'))
            capture = read(target.with_suffix('.cpu.json')) if invocation['arm'] == 'profiled' else None
            for observation in observations:
                row = dict(invocation=entry['index'], observation=observation['observation'],
                           arm=invocation['arm'], block=invocation['block'],
                           validation_ns=observation['validation']['duration_ns'],
                           pixel_ns=observation['endpoints']['pixels']['harness_latency_ns'],
                           metadata_ns=observation['endpoints']['metadata']['harness_latency_ns'])
                if capture:
                    files = [f for f in capture['files'] if not f['window']['setup'] and
                             f['window']['observation'] == observation['observation']]
                    row.update(sampled=aggregate(files), files=files)
                (warmups if invocation['warmup'] else rows).append(row)
            if capture:
                setup.append(dict(invocation=entry['index'], files=[f for f in capture['files'] if f['window']['setup']]))
        require(len(rows) == 40 and len(warmups) == 2, 'report count mismatch')
        summaries = []
        for arm in ('unprofiled', 'profiled'):
            for block in [None, *range(4)]:
                selected = [row for row in rows if row['arm'] == arm and (block is None or row['block'] == block)]
                summary = dict(arm=arm, block='pooled' if block is None else block,
                               timings={k: distribution([r[k] for r in selected]) for k in
                                        ('validation_ns', 'pixel_ns', 'metadata_ns')})
                if arm == 'profiled':
                    summary['samples'] = {k: distribution([r['sampled'][k] for r in selected]) for k in
                        ('sample_count', 'recorded_period', 'unresolved_frames', 'truncated_stacks')}
                    summary['category_count_shares'] = {k: distribution([r['sampled']['count_shares'][k] for r in selected
                        if r['sampled']['count_shares'] is not None]) for k in CATEGORIES}
                    summary['category_period_shares'] = {k: distribution([r['sampled']['period_shares'][k] for r in selected
                        if r['sampled']['period_shares'] is not None]) for k in CATEGORIES}
                    summary['files'] = {name: {k: distribution([f['count_shares'][k] for r in selected for f in r['files']
                        if f['window']['path'] == name and f['count_shares'] is not None]) for k in CATEGORIES}
                        for name in sorted({f['window']['path'] for r in selected for f in r['files']})}
                summaries.append(summary)
        selections = {arm: {field: tails([r for r in rows if r['arm'] == arm], field) for field in
                      ('validation_ns', 'pixel_ns', 'metadata_ns')} for arm in ('unprofiled', 'profiled')}
        write(output / 'observations.json', rows); write(output / 'warmups.json', warmups)
        write(output / 'setup.json', setup); write(output / 'summary.json', summaries)
        write(output / 'tails.json', selections)
        result.update(status='complete', observations=40, warmups=2)
        # Recommendation is deliberately left for evidence-backed interpretation.
        lines = ['# Sampled C userspace execution', '',
                 'All shares concern sampled userspace execution. Kernel cost and exact elapsed-time decomposition remain unresolved.', '',
                 'Self categories are exclusive. Inclusive stack presence is separate and non-additive. Zero-sample windows remain unavailable.', '',
                 'Unprofiled to profiled harness differences are instrumentation effects; no overhead is subtracted and no gain or significance is inferred.', '',
                 '| Arm | Block | Validation median ms | Pixel median ms | Metadata median ms |',
                 '|---|---|---:|---:|---:|']
        for s in summaries:
            lines.append('| ' + ' | '.join([s['arm'], str(s['block']), *[f"{s['timings'][k]['median']/1e6:.3f}" for k in
                ('validation_ns', 'pixel_ns', 'metadata_ns')]]) + ' |')
        lines += ['', 'See summary.json for count/minimum/median/nearest-rank p95/maximum, per-observation count and period shares, and frozen file-ordinal views.',
                  'See tails.json for retained p95-cutoff observations including all ties. Sparse per-file sampling limits interpretation.', '']
        (output / 'REPORT.md').write_text('\n'.join(lines))
    except validation.r.ERRORS as error:
        result['failure'] = str(error)
    finally:
        write(output / 'assessment.json', result); o.seal(output)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execution', type=Path, required=True); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = report(args.execution.absolute(), args.output.absolute())
    print(result); sys.exit(result['status'] != 'complete')
