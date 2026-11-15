#!/usr/bin/env python3
"""Independent stdlib-only raw validation replay; imports no audit or reporter."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys


def read(path):
    return json.loads(path.read_text())


def check(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def seal(root):
    expected = read(root / 'seal.json')
    actual = {}
    for path in root.rglob('*'):
        check(not path.is_symlink(), 'symlink in evidence')
        if path.is_file() and path != root / 'seal.json':
            actual[str(path.relative_to(root))] = digest(path)
    check(actual == expected, 'seal mismatch: ' + str(root))


def paired(target):
    stacks = defaultdict(list)
    seen = set()
    result = []
    previous = defaultdict(lambda: -1)
    for path in (target.with_suffix('.stderr'), target.with_suffix('.stdout')):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if not line.startswith('VALIDATION '):
                continue
            def unique(pairs):
                value = {}
                for key, item in pairs:
                    check(key not in value, 'duplicate JSON key')
                    value[key] = item
                return value
            event = json.loads(line[11:], object_pairs_hook=unique)
            check(event['version'] == 1 and type(event['ns']) is int, 'invalid raw record')
            key = event['pid'], event['tid']
            check(event['ns'] >= previous[key], 'misordered raw thread')
            previous[key] = event['ns']
            stack = stacks[key]
            citation = dict(event, file=str(path), line=number, text=line)
            if event['edge'] == 'begin':
                identity = event['pid'], event['span']
                check(identity not in seen, 'duplicate span')
                seen.add(identity)
                check(event['parent'] == (stack[-1]['span'] if stack else 0), 'raw nesting mismatch')
                check(event['outcome'] == 'unavailable', 'invalid entry outcome')
                stack.append(citation)
            else:
                check(event['edge'] == 'end' and stack, 'unpaired raw end')
                begin = stack.pop()
                check(all(begin[k] == event[k] for k in event if k not in ('ns', 'edge', 'outcome')),
                      'raw boundary identity mismatch')
                check(event['ns'] > begin['ns'] and event['outcome'] == 'returned', 'invalid duration/outcome')
                result.append(dict(begin=begin, end=citation))
    check(not any(stacks.values()), 'missing raw end')
    return result


def raw_work(target, mapping):
    spans = paired(target)
    roots = [s for s in spans if s['begin']['parent'] == 0]
    output = []
    consumed = set()
    for root in roots:
        begin = root['begin']
        check(begin['operation'] == 'generation' and begin['validation'] == begin['span'], 'unexplained root')
        owned = {begin['span']}
        selected = []
        # Parent closure, never timestamp proximity.
        pending = [s for s in spans if s['begin']['pid'] == begin['pid']]
        while True:
            children = [s for s in pending if s['begin']['span'] in owned or s['begin']['parent'] in owned]
            if not children:
                break
            selected.extend(children)
            for span in children:
                owned.add(span['begin']['span'])
                pending.remove(span)
        runtime = [s for s in selected if s['begin']['operation'] == 'runtime']
        check(len(runtime) == 1, 'missing/duplicate runtime')
        file_spans = [s for s in selected if s['begin']['operation'] == 'file']
        check(sorted(s['begin']['ordinal'] for s in file_spans) == list(range(len(mapping))), 'ordinal coverage mismatch')
        files = []
        for file in file_spans:
            ordinal = file['begin']['ordinal']
            check(file['begin']['parent'] == runtime[0]['begin']['span'], 'file/runtime ownership mismatch')
            hashes = [s for s in selected if s['begin']['operation'] == 'read_hash' and
                      s['begin']['parent'] == file['begin']['span']]
            check(len(hashes) == 1 and hashes[0]['begin']['ordinal'] == ordinal, 'missing/duplicate read_hash')
            span = hashes[0]
            ns = span['end']['ns']-span['begin']['ns']
            record = mapping[ordinal]
            files.append(dict(**record, successful_passes=1, inferred_bytes=record['size'], read_hash_ns=ns,
                              bytes_per_second=record['size']*1e9/ns, citations=[span['begin'], span['end']]))
        files.sort(key=lambda f: f['ordinal'])
        ns = sum(f['read_hash_ns'] for f in files)
        duration = root['end']['ns']-begin['ns']
        check(ns <= duration, 'read/hash overlap')
        consumed.update((s['begin']['pid'], s['begin']['span']) for s in selected)
        output.append(dict(root=dict(pid=begin['pid'], service=begin['service'], span=begin['span']),
                           observation=begin['observation'], validation_ns=duration, read_hash_ns=ns,
                           residual_validation_ns=duration-ns, inferred_bytes=sum(f['size'] for f in files),
                           bytes_per_second=sum(f['size'] for f in files)*1e9/ns, files=files))
    check(consumed == {(s['begin']['pid'], s['begin']['span']) for s in spans}, 'unaccounted raw span')
    return output


def dist(values):
    values = sorted(values)
    if not values:
        return dict(count=0)
    return dict(count=len(values), minimum=values[0], median=statistics.median(values),
                p95=values[math.ceil(len(values)*.95)-1], maximum=values[-1])


def verify(output):
    seal(output)
    check(read(output / 'assessment.json')['status'] == 'complete', 'audit blocked')
    inputs = read(output / 'inputs.json')
    for name, expected in inputs['identities'].items():
        path = Path(name)
        check(digest(path) == expected, 'consumed identity drift')
        if path.name == 'seal.json':
            seal(path.parent)
    execution, report = Path(inputs['execution']), Path(inputs['report'])
    registration = read(execution / 'preregistration.json')
    package = Path(registration['package'])
    frozen = read(package / 'inputs.json')
    manifest = Path(frozen['built']) / 'validation/C/runtime/manifest.json'
    mapping = [dict(ordinal=i, **{k: row[k] for k in ('path', 'size', 'sha256')})
               for i, row in enumerate(read(manifest)['files'])]
    check(mapping == inputs['mapping'] == frozen['mapping'], 'manifest mismatch')
    assessment = read(execution / 'assessment.json')
    check(assessment['status'] == 'complete' and len(assessment['invocations']) == 10, 'execution incomplete')
    accounting = read(output / 'accounting.json')
    replayed = []
    for index, entry in enumerate(assessment['invocations']):
        invocation = entry['entry']['invocation']
        check(entry['status'] == 'passed' and entry['entry'] == registration['commands'][index], 'invocation mismatch')
        target = execution / 'observations' / f'{index:03}.json'
        check(str(target) == entry['entry']['argv'][-1], 'target mismatch')
        rows = raw_work(target, mapping)
        for row in rows:
            population = 'setup' if row['observation'] is None else ('warmup' if invocation['warmup'] else 'measured')
            candidates = [r for r in accounting if r['invocation'] == index and r['root'] == row['root']]
            check(len(candidates) == 1, 'missing/duplicate accounted root')
            saved = candidates[0]
            for key, value in row.items():
                check(saved[key] == value, 'independent accounting mismatch: ' + key)
            check(saved['population'] == population and saved['arm'] == invocation['arm'] and
                  saved['block'] == invocation['block'], 'population drift')
            life = saved['lifecycle']
            for key in ('binding', 'construction'):
                span = life[key]
                for edge in ('begin', 'end'):
                    event = span[edge]
                    # v3 historical lifecycle paths name the harness JSON; the
                    # actual TRACE records live in stderr.
                    path = Path(event['file']).with_suffix('.stderr')
                    text = path.read_text().splitlines()[event['line']-1]
                    check(text.startswith('TRACE '), 'lifecycle citation absent')
                    raw = json.loads(text[6:])
                    check(all(raw.get(k) == value for k, value in event.items() if k not in ('file', 'line')),
                          'lifecycle citation drift')
                check(span['begin']['pid'] == row['root']['pid'] and span['begin']['service'] == row['root']['service'],
                      'lifecycle ownership mismatch')
            binding = life['binding']
            check(binding['phase'] == 'generation_validation' and
                  binding['begin']['tid'] == row['files'][0]['citations'][0]['tid'] and
                  binding['begin']['observation'] == (row['observation'] or 0), 'root lifecycle binding drift')
            check(life['classification'] == ('setup construction' if population == 'setup' else 'observation construction'),
                  'classification drift')
            replayed.append(saved)
    check(len(replayed) == len(accounting) and sum(r['population'] == 'measured' for r in replayed) == 40 and
          sum(r['population'] == 'warmup' for r in replayed) == 2, 'replay population mismatch')
    summaries = read(output / 'distributions.json')
    expected_cells = {(r['population'], arm, block) for r in replayed
                      for arm in ('all', r['arm']) for block in ('pooled', r['block'])
                      if block is not None}
    actual_cells = [(s['population'], s['arm'], s['block']) for s in summaries]
    check(len(actual_cells) == len(expected_cells) and set(actual_cells) == expected_cells,
          'distribution coverage mismatch')
    for summary in summaries:
        rows = [r for r in replayed if r['population'] == summary['population'] and
                (summary['arm'] == 'all' or r['arm'] == summary['arm']) and
                (summary['block'] == 'pooled' or r['block'] == summary['block'])]
        for key, value in summary['timings'].items():
            check(dist([r[key] for r in rows]) == value, 'timing distribution mismatch')
        files = [f for r in rows for f in r['files']]
        check(sorted(cell['ordinal'] for cell in summary['files']) == list(range(len(mapping))),
              'file distribution coverage mismatch')
        check(set(summary['timings']) == {'validation_ns', 'read_hash_ns', 'residual_validation_ns',
                                         'inferred_bytes', 'bytes_per_second'}, 'missing timing distribution')
        for cell in [summary['pooled'], *summary['files']]:
            fs = [f for f in files if 'ordinal' not in cell or f['ordinal'] == cell['ordinal']]
            ns = sum(f['read_hash_ns'] for f in fs)
            size = sum(f['size'] for f in fs)
            expected = dict(successful_passes=len(fs), inferred_bytes=size, read_hash_ns=ns,
                            bytes_per_second=size*1e9/ns,
                            duration_distribution=dist([f['read_hash_ns'] for f in fs]),
                            throughput_distribution=dist([f['bytes_per_second'] for f in fs]))
            check(all(cell[k] == value for k, value in expected.items()), 'pooled/file accounting mismatch')
    check(read(output / 'tails.json') == read(report / 'tails.json'), 'tail membership drift')
    for arm, fields in read(output / 'tails.json').items():
        rows = [r for r in read(report / 'observations.json') if r['arm'] == arm]
        for field, selected in fields.items():
            cutoff = sorted(r[field] for r in rows)[math.ceil(.95*len(rows))-1]
            check({(r['invocation'], r['observation']) for r in selected} ==
                  {(r['invocation'], r['observation']) for r in rows if r[field] >= cutoff}, 'p95 ties lost')
    source_base = Path(frozen['package']) / 'validation/C'
    inventory = read(source_base / 'source-inventory.json')['source']
    for source in read(output / 'source-citations.json'):
        path = Path(source['file'])
        relative = str(path.relative_to(source_base / 'source'))
        check(source['sha256'] == inventory[relative] == digest(path), 'source digest mismatch')
        lines = path.read_text().splitlines()
        check(all(lines[e['line']-1] == e['text'] for e in source['excerpts']), 'source citation mismatch')
    services = {(r['invocation'], r['root']['pid'], r['root']['service']) for r in replayed}
    check(len(services) == len(replayed), 'repeated lifetime needs generation evidence')
    lifetimes = read(output / 'lifetimes.json')
    check(len(lifetimes) == len(services) and
          {(r['invocation'], r['pid'], r['service']) for r in lifetimes} == services, 'lifetime count drift')
    for row in lifetimes:
        matches = [r for r in replayed if (r['invocation'], r['root']['pid'], r['root']['service']) ==
                   (row['invocation'], row['pid'], row['service'])]
        check(len(matches) == row['validations'] == 1 and row['within_lifetime_repeated_bytes'] == 0 and
              row['inferred_bytes'] == matches[0]['inferred_bytes'], 'lifetime accounting drift')
    check(read(output / 'proposal.json')['kind'] == 'native SHA-256 throughput diagnostic', 'unsupported proposal')
    seal(output)
    for name, expected in inputs['identities'].items():
        check(digest(Path(name)) == expected, 'consumed identity changed during verification')
    return dict(status='passed', audit_seal=digest(output / 'seal.json'), validations=len(replayed),
                measured_observations=40, warmups=2, imports_audit_or_reporter=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check(not args.output.resolve().is_relative_to(args.audit.resolve()), 'verification must be outside seal')
    check(not args.output.exists(), 'destination collision')
    try:
        result = verify(args.audit.absolute())
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        result = dict(status='failed', failure=str(error))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(result)
    sys.exit(result['status'] != 'passed')
