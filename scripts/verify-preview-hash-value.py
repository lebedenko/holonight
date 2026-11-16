#!/usr/bin/env python3
"""Independent stdlib-only replay of the offline buffered hashing assessment."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

THRESHOLD_NS = 5_000_000
PINS = (
    ('preview-hash-device-mechanism-20261116-01', '5c526f8fe12cf0d3e87c88b0d90d4dc197c14dd5416cbb6c421aa339724d2cf8',
     'd0d397ef5790af7f755b336116b2a866d398bacd04a364d4f6838d2fc5ace76d', 'evidence_seal'),
    ('preview-verification-work-20261115-04', '6c2a6671b1d36a7adbd8ce18b51d3b45b06e43ed5a7776f2d144da220676d407',
     'e5a0db9daf3f9148ba2154fdee0b98214c2d3011bfb2f6e251133d6e685e4b5c', 'audit_seal'))


def check(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            check(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def seal(root):
    actual = {}
    for path in root.rglob('*'):
        check(not path.is_symlink(), 'symlink in evidence')
        if path.is_file() and path != root / 'seal.json':
            actual[str(path.relative_to(root))] = digest(path)
    check(actual == read(root / 'seal.json'), 'seal mismatch: ' + str(root))


def bindings(mechanism, mechanism_verification, work, work_verification):
    identities = {}
    checked = set()

    def identity(path, expected):
        path = Path(path)
        check(digest(path) == expected, 'consumed identity drift: ' + str(path))
        check(str(path) not in identities or identities[str(path)] == expected, 'identity conflict')
        identities[str(path)] = expected
        if path.name == 'seal.json' and path.parent not in checked:
            checked.add(path.parent)
            seal(path.parent)
            inputs = path.parent / 'inputs.json'
            if inputs.exists():
                data = read(inputs)
                for name, value in data.get('identities', {}).items():
                    identity(Path(name), value)
                for name, value in data.get('seals', {}).items():
                    identity(Path(name) / 'seal.json', value)

    for root, verification, pin in zip((mechanism, work), (mechanism_verification, work_verification), PINS):
        name, expected, verification_hash, key = pin
        check(root.name == name, 'wrong retained input')
        identity(root / 'seal.json', expected)
        identity(verification, verification_hash)
        record = read(verification)
        check(record['status'] == 'passed' and record[key] == expected, 'verification binding mismatch')
        check(read(root / 'assessment.json')['status'] == 'complete', 'input incomplete')
    m, w = read(mechanism / 'inputs.json'), read(work / 'inputs.json')
    check(m['mapping'] == w['mapping'], 'payload mapping mismatch')
    mapping = m['mapping']
    check([r['ordinal'] for r in mapping] == list(range(60)) and
          sum(r['size'] for r in mapping) == 87215960, 'frozen population mismatch')
    runtime = Path(m['runtime'])
    manifest = runtime / 'manifest.json'
    identity(manifest, digest(manifest))
    check(mapping == [dict(ordinal=i, **{k: r[k] for k in ('path', 'size', 'sha256')})
                      for i, r in enumerate(read(manifest)['files'])], 'manifest mapping mismatch')
    for row in mapping:
        path = runtime / row['path']
        check(path.resolve().is_relative_to(runtime.resolve()) and path.stat().st_size == row['size'], 'payload size/path drift')
        identity(path, row['sha256'])
    for dep in m['dependencies'].values():
        identity(Path(dep['host']), dep['host_sha256'])
        identity(Path(dep['payload']), dep['payload_sha256'])
    for label in ('native', 'counting'):
        for name, expected in read(mechanism / (label + '-mapped-identities.json')).items():
            identity(Path(name), expected)
    for name, expected in read(mechanism / 'tool-identities.json').items():
        identity(Path(name), expected)
    return dict(mechanism=str(mechanism), mechanism_verification=str(mechanism_verification),
                work=str(work), work_verification=str(work_verification), mapping=mapping, identities=identities)


def comparison(mechanism, mapping):
    reg = read(mechanism / 'preregistration.json')
    check(reg['mapping'] == mapping, 'registration mapping mismatch')
    raw = [json.loads(line) for line in (mechanism / 'native.stdout').read_text().splitlines()]
    check(raw[0]['type'] == 'identity' and raw[0]['counting'] is False, 'timing identity mismatch')
    check(raw[0]['pid'] == read(mechanism / 'native.json')['pid'], 'process mismatch')
    expected = [(s, f) for s in reg['schedule'] for f in mapping]
    files = [r for r in raw if r['type'] == 'file']
    check(len(files) == len(expected), 'missing/duplicate timing rows')
    for row, (sweep, file) in zip(files, expected):
        check(all(row[k] == v for k, v in sweep.items()) and
              (row['ordinal'], row['bytes'], row['sha256']) == (file['ordinal'], file['size'], file['sha256']),
              'timing ordinal/schedule mismatch')
        check(type(row['update_ns']) is int and row['update_ns'] > 0, 'invalid timer')
    result = []
    for block in range(8):
        contributions = []
        for file in mapping:
            totals = []
            for case in ('device_buffered', 'stream_64k_buffered'):
                selected = [r for r in files if not r['warmup'] and r['block'] == block and
                            r['case'] == case and r['ordinal'] == file['ordinal']]
                check(sorted(r['sweep'] for r in selected) == [0, 1, 2], 'missing/duplicate ordinals')
                totals.append(sum(r['update_ns'] for r in selected))
            a, b = totals
            contributions.append(dict(ordinal=file['ordinal'], size=file['size'], left_sum_ns=a,
                                      right_sum_ns=b, difference_sum_ns=a-b))
        a = sum(r['left_sum_ns'] for r in contributions)
        b = sum(r['right_sum_ns'] for r in contributions)
        result.append(dict(block=block, left_sum_ns=a, right_sum_ns=b, left_mean_ns=a/3,
                           right_mean_ns=b/3, difference_sum_ns=a-b, mean_difference_ns=(a-b)/3,
                           duration_ratio=a/b, contributions=contributions))
    return result


def decision(blocks):
    differences = [r['difference_sum_ns'] for r in blocks]
    check(len(differences) == 8, 'block coverage')
    positive = sum(d > 0 for d in differences)
    negative = sum(d < 0 for d in differences)
    below = sum(d < 3*THRESHOLD_NS for d in differences)
    equal = sum(d == 3*THRESHOLD_NS for d in differences)
    return dict(threshold_ns=THRESHOLD_NS, positive_blocks=positive, negative_blocks=negative,
                zero_blocks=8-positive-negative, direction='mixed; inconclusive' if positive and negative else
                'all positive' if positive == 8 else 'all negative' if negative == 8 else 'includes zero; inconclusive',
                below_threshold=below, equal_threshold=equal, above_threshold=8-below-equal,
                recommendation='defer a private A/B experiment on current evidence' if below == 8 else
                'threshold reached in retained blocks; candidate experiment requires its own plan',
                future_5ms_savings_ruled_out=False)


def dist(values):
    values = sorted(values)
    if not values:
        return dict(count=0)
    return dict(count=len(values), minimum=values[0], median=statistics.median(values),
                p95=values[math.ceil(.95*len(values))-1], maximum=values[-1])


def context(work):
    inputs = read(work / 'inputs.json')
    rows = read(work / 'accounting.json')
    report = read(Path(inputs['report']) / 'observations.json')
    execution = Path(inputs['execution'])
    invocations = read(execution / 'preregistration.json')['commands']
    seen = set()
    observations = []
    for row in rows:
        key = (row['invocation'], row['root']['pid'], row['root']['service'])
        check(key not in seen, 'duplicate service lifetime')
        seen.add(key)
        invocation = invocations[row['invocation']]['invocation']
        population = 'setup' if row['observation'] is None else 'warmup' if invocation['warmup'] else 'measured'
        check((population, invocation['arm'], invocation['block']) ==
              (row['population'], row['arm'], row['block']), 'population mismatch')
        if population == 'measured':
            matches = [r for r in report if (r['invocation'], r['observation']) ==
                       (row['invocation'], row['observation'])]
            check(len(matches) == 1, 'observation identity mismatch')
            r = matches[0]
            check((r['arm'], r['block'], r['validation_ns'], r['pixel_ns'], r['metadata_ns']) ==
                  (row['arm'], row['block'], row['validation_ns'], row['endpoints_ns']['pixels'],
                   row['endpoints_ns']['metadata']), 'endpoint identity mismatch')
        observations.append(dict(execution=str(execution), **{k: row[k] for k in
                            ('invocation', 'observation', 'root', 'population', 'arm', 'block',
                             'validation_ns', 'read_hash_ns')}, endpoints_ns=row.get('endpoints_ns')))
    check(len(rows) == 52 and sum(r['population'] == 'measured' for r in rows) == 40 and
          sum(r['population'] == 'warmup' for r in rows) == 2, 'work population mismatch')
    lifetimes = read(work / 'lifetimes.json')
    check(len(lifetimes) == len(seen) and {(r['invocation'], r['pid'], r['service']) for r in lifetimes} == seen and
          all(r['validations'] == 1 and r['within_lifetime_repeated_bytes'] == 0 for r in lifetimes), 'lifetime drift')
    for citation in read(work / 'source-citations.json'):
        path = Path(citation['file'])
        check(digest(path) == citation['sha256'], 'source identity drift')
        lines = path.read_text().splitlines()
        check(all(lines[e['line']-1] == e['text'] for e in citation['excerpts']), 'source citation drift')
    cells = []
    for population in ('measured', 'warmup', 'setup'):
        for arm in ('unprofiled', 'profiled'):
            group = [r for r in rows if (r['population'], r['arm']) == (population, arm)]
            if group:
                cells.append(dict(population=population, arm=arm, timings={
                    k: dist([r[k] for r in group]) for k in ('validation_ns', 'read_hash_ns')},
                    endpoints_ns={k: dist([r['endpoints_ns'][k] for r in group if 'endpoints_ns' in r])
                                  for k in ('pixels', 'metadata')}))
    return dict(observations=observations, distributions=cells, service_lifetimes=len(seen),
                redundant_validation_demonstrated=False)


def verify(output):
    seal(output)
    check(read(output / 'assessment.json')['status'] == 'complete', 'assessment blocked')
    reg = read(output / 'protocol.json')
    check(reg == dict(threshold_ns=THRESHOLD_NS, comparison='device buffered minus stream 64K buffered',
                      classification='new post hoc comparison', new_measurements=False), 'protocol drift')
    inputs = read(output / 'inputs.json')
    paths = [Path(inputs[k]) for k in ('mechanism', 'mechanism_verification', 'work', 'work_verification')]
    check(bindings(*paths) == inputs, 'input binding drift')
    blocks = comparison(paths[0], inputs['mapping'])
    check(blocks == read(output / 'arithmetic.json'), 'arithmetic mismatch')
    selected = decision(blocks)
    check(selected == read(output / 'decision.json'), 'decision mismatch')
    assessment = read(output / 'assessment.json')
    check(assessment == dict(status='complete', recommendation=selected['recommendation'], new_measurements=False),
          'assessment recommendation mismatch')
    text = (output / 'report.md').read_text()
    check(selected['recommendation'] + '.' in text, 'report recommendation mismatch')
    for b in blocks:
        line = (f"| {b['block']} | {b['left_mean_ns']/1e6:.6f} | {b['right_mean_ns']/1e6:.6f} | "
                f"{b['mean_difference_ns']/1e6:+.6f} | {b['duration_ratio']:.8f} |")
        check(text.splitlines().count(line) == 1, 'report arithmetic mismatch')
    for name in ('source-citations.json', 'lifetimes.json'):
        check(read(output / name) == read(paths[2] / name), 'retained context copy mismatch')
    check(context(paths[2]) == read(output / 'context.json'), 'context mismatch')
    tools = read(output / 'tool-identities.json')
    check({Path(p).name for p in tools} == {'assess-preview-hash-value.py', 'verify-preview-hash-value.py',
                                           'test_preview_hash_value.py'} and len(tools) == 3, 'tool coverage mismatch')
    for name, expected in tools.items():
        check(digest(Path(name)) == expected and digest(output / 'source' / Path(name).name) == expected, 'tool snapshot drift')
    for name, expected in inputs['identities'].items():
        check(digest(Path(name)) == expected, 'consumed identity changed during verification')
    seal(output)
    return dict(status='passed', assessment_seal=digest(output / 'seal.json'), blocks=8,
                imports_assessor_or_reporter=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assessment', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check(not args.output.exists() and not args.output.resolve().is_relative_to(args.assessment.resolve()), 'destination collision/overlap')
    try:
        result = verify(args.assessment.resolve())
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        result = dict(status='failed', failure=str(error))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(result)
    sys.exit(result['status'] != 'passed')
