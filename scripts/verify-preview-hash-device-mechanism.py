#!/usr/bin/env python3
"""Independent standard-library-only replay of the native SHA-256 diagnostic."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

CASES = ('device_buffered', 'device_unbuffered', 'stream_1k_buffered', 'stream_1k_unbuffered',
         'stream_64k_buffered', 'stream_64k_unbuffered', 'memory_1k', 'memory_64k')
CONTRASTS = ((2, 4), (3, 5), (0, 1), (2, 3), (4, 5), (0, 2), (1, 3), (6, 7))
AUDIT_SEAL = '076c7e460049f5627a91d55455b1abc0edaa358cb0aa23f7e546772d51bf5ef1'



def check(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return decode(path.read_text())


def decode(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            check(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def seal(root):
    actual = {}
    for path in root.rglob('*'):
        check(not path.is_symlink(), 'symlink in evidence: ' + str(path))
        if path.is_file() and path != root / 'seal.json':
            actual[str(path.relative_to(root))] = digest(path)
    check(actual == read(root / 'seal.json'), 'seal mismatch: ' + str(root))


def build_id(path):
    notes = subprocess.check_output(['readelf', '-n', str(path)], text=True, timeout=30)
    ids = re.findall(r'Build ID: ([0-9a-f]+)', notes)
    check(len(ids) == 1, 'missing/ambiguous build ID: ' + str(path))
    return ids[0]


def payload_provenance(audit, verification):
    seal(audit)
    record = read(verification)
    check(record['status'] == 'passed' and record['audit_seal'] == digest(audit / 'seal.json') and
          record['measured_observations'] == 40 and record['warmups'] == 2 and record['validations'] == 52,
          'independent audit binding mismatch')
    check(read(audit / 'assessment.json')['status'] == 'complete', 'audit incomplete')
    inputs = read(audit / 'inputs.json')
    identities = {str(audit / 'seal.json'): digest(audit / 'seal.json'), str(verification): digest(verification)}
    for name, expected in inputs['identities'].items():
        path = Path(name)
        check(digest(path) == expected, 'provenance identity drift: ' + name)
        if path.name == 'seal.json':
            seal(path.parent)
        identities[name] = expected
    execution = Path(inputs['execution'])
    registration = read(execution / 'preregistration.json')
    package = Path(registration['package'])
    check(digest(package / 'seal.json') == registration['package_seal'], 'execution package binding drift')
    frozen = read(package / 'inputs.json')
    for name, expected in frozen['seals'].items():
        check(digest(Path(name) / 'seal.json') == expected, 'frozen seal binding drift')
        seal(Path(name))
        identities[str(Path(name) / 'seal.json')] = expected
    runtime = Path(frozen['built']) / 'validation/C/runtime'
    manifest = runtime / 'manifest.json'
    mapping = [dict(ordinal=i, **{k: row[k] for k in ('path', 'size', 'sha256')})
               for i, row in enumerate(read(manifest)['files'])]
    check(mapping == inputs['mapping'] == frozen['mapping'], 'manifest mapping drift')
    check(len(mapping) == 60 and sum(r['size'] for r in mapping) == 87215960, 'wrong frozen population')
    for row in mapping:
        path = runtime / row['path']
        check(path.resolve().is_relative_to(runtime.resolve()), 'payload path escape')
        check(path.stat().st_size == row['size'] and digest(path) == row['sha256'], 'payload drift')
    dependencies = frozen['dependencies']
    check(set(dependencies) == {'libQt6Core.so.6', 'libcrypto.so.4', 'libc.so.6'}, 'dependency coverage drift')
    for name, dep in dependencies.items():
        host = Path('/usr/lib') / name
        payload = runtime / 'usr/lib' / name
        check(digest(host) == dep['host_sha256'] == dep['payload_sha256'] == digest(payload), 'host dependency drift: ' + name)
        check(build_id(host) == dep['host_build_id'] == dep['build_id'] == build_id(payload), 'dependency build ID drift')
        identities[str(host.resolve())] = digest(host)
    identities[str(manifest)] = digest(manifest)
    return dict(audit=str(audit), verification=str(verification), runtime=str(runtime), mapping=mapping,
                dependencies=dependencies, identities=identities)



def provenance(audit, verification):
    seal(audit)
    check(audit.name == 'preview-hash-device-path-20261116-15' and
          digest(audit / 'seal.json') == AUDIT_SEAL, 'wrong exact-source audit')
    passed = read(verification)
    check(passed['status'] == 'passed' and passed['source_status'] == 'exact' and
          passed['audit_seal'] == AUDIT_SEAL, 'exact-source verification mismatch')
    check(read(audit / 'assessment.json') == dict(status='complete', source_status='exact', new_measurements=False),
          'exact-source assessment mismatch')
    bindings = read(audit / 'inputs.json')
    throughput = Path(bindings['evidence'])
    seal(throughput)
    prior = read(Path(bindings['verification']))
    check(prior['status'] == 'passed' and prior['evidence_seal'] == digest(throughput / 'seal.json'),
          'throughput verification mismatch')
    for name, expected in bindings['identities'].items():
        check(digest(Path(name)) == expected, 'audit input drift: ' + name)
        if Path(name).name == 'seal.json': seal(Path(name).parent)
    consumed = read(throughput / 'inputs.json')
    result = payload_provenance(Path(consumed['audit']), Path(consumed['verification']))
    check(result == consumed, 'throughput provenance drift')
    result = dict(result, audit=str(audit), verification=str(verification))
    result['identities'] = dict(result['identities'], **bindings['identities'])
    result['identities'].update({str(audit / 'seal.json'): AUDIT_SEAL, str(verification): digest(verification)})
    return result


def expected_schedule(counting=False):
    if counting:
        return [dict(index=i, case=c, block=None, warmup=False, sweep=0) for i, c in enumerate(CASES)]
    result = [dict(case=c, block=None, warmup=True, sweep=0) for c in CASES]
    for block in range(8):
        for c in CASES[block:] + CASES[:block]:
            result.extend(dict(case=c, block=block, warmup=False, sweep=s) for s in range(3))
    return [dict(index=i, **r) for i, r in enumerate(result)]


def histogram(row):
    size, case = row['bytes'], row['case']
    device, memory = case.startswith('device'), case.startswith('memory')
    chunk = 65536 if '64k' in case else 1024
    updates = (size + chunk - 1) // chunk
    check(row['update_calls'] == (None if device else updates), 'update count mismatch')
    check(row['read_calls'] == (None if device else 0 if memory else updates + 1), 'read count mismatch')
    pairs = set()
    total = calls = 0
    for h in row['histogram']:
        request, returned, n = (h[k] for k in ('requested', 'returned', 'calls'))
        check(all(type(x) is int for x in (request, returned, n)) and request >= 0 and
              0 <= returned <= request and n > 0, 'invalid histogram bin')
        check((request, returned) not in pairs, 'duplicate histogram bin')
        pairs.add((request, returned))
        total += returned*n
        calls += n
    check(total == (0 if memory else size), 'histogram bytes mismatch')
    check((not row['histogram']) if memory else calls > 0, 'histogram coverage mismatch')
    if case.endswith('unbuffered'):
        check(all(h['requested'] in (0, chunk) for h in row['histogram']), 'unbuffered request mismatch')
        check(sum(h['calls'] for h in row['histogram'] if h['requested'] > 0) == updates + 1, 'unbuffered call count mismatch')


def replay(path, registration, counting=False):
    records = [decode(line) for line in path.read_text().splitlines()]
    check(records and records[0]['type'] == 'identity', 'missing identity')
    identity = records.pop(0)
    check(type(identity['pid']) is int and identity['pid'] > 0 and identity['counting'] is counting,
          'invalid process identity')
    schedule = expected_schedule(counting)
    check(registration['count_schedule' if counting else 'schedule'] == schedule, 'schedule drift')
    rows = []
    pos = 0
    for sweep in schedule:
        selected = []
        for f in registration['mapping']:
            check(pos < len(records), 'missing file row')
            r = records[pos]
            pos += 1
            check(r['type'] == 'file' and all(r[k] == x for k, x in sweep.items()), 'schedule mismatch')
            check((r['ordinal'], r['bytes'], r['sha256']) == (f['ordinal'], f['size'], f['sha256']),
                  'digest/ordinal/bytes mismatch')
            check(all(type(r[k]) is int and r[k] > 0 for k in ('init_ns', 'update_ns', 'final_ns')), 'invalid duration')
            if counting: histogram(r)
            else: check(not any(k in r for k in ('histogram', 'read_calls', 'update_calls')), 'timing instrumented')
            selected.append(r)
        check(pos < len(records), 'missing sweep end')
        end = records[pos]
        pos += 1
        check(end['type'] == 'sweep_end' and end['index'] == sweep['index'] and
              type(end['elapsed_ns']) is int and 0 < end['elapsed_ns'] <= 30000000000 and
              sum(r[k] for r in selected for k in ('init_ns', 'update_ns', 'final_ns')) <= end['elapsed_ns'],
              'sweep bound mismatch')
        rows.extend(selected)
    check(pos == len(records), 'extra output')
    return identity, rows


def summaries(rows):
    cells = []
    for c in CASES:
        group = [r for r in rows if r['case'] == c and not r['warmup']]
        ns = sum(r['update_ns'] for r in group)
        size = sum(r['bytes'] for r in group)
        cells.append(dict(case=c, bytes=size, update_ns=ns, bytes_per_second=size*1e9/ns))
    contrasts = []
    for block in range(8):
        by_case = {}
        for r in rows:
            if r['block'] == block and not r['warmup']:
                by_case.setdefault(r['case'], {}).setdefault(r['ordinal'], []).append(r['update_ns'])
        for ai, bi in CONTRASTS:
            a, b = CASES[ai], CASES[bi]
            contributions = []
            for ordinal in sorted(by_case[a]):
                left, right = sum(by_case[a][ordinal]), sum(by_case[b][ordinal])
                check(len(by_case[a][ordinal]) == len(by_case[b][ordinal]) == 3, 'contrast coverage')
                contributions.append(dict(ordinal=ordinal, left_sum_ns=left, right_sum_ns=right,
                                          difference_sum_ns=left-right))
            left = sum(c['left_sum_ns'] for c in contributions)
            right = sum(c['right_sum_ns'] for c in contributions)
            contrasts.append(dict(block=block, left=a, right=b, left_sum_ns=left, right_sum_ns=right,
                                  difference_sum_ns=left-right, mean_difference_ns=(left-right)/3,
                                  duration_ratio=left/right, contributions=contributions))
    return dict(cells=cells, contrasts=contrasts)


def count_summary(rows):
    result = []
    for case in CASES:
        group = [r for r in rows if r['case'] == case]
        bins = {}
        for row in group:
            for h in row['histogram']:
                pair = h['requested'], h['returned']
                bins[pair] = bins.get(pair, 0) + h['calls']
        result.append(dict(case=case, files=len(group), bytes=sum(r['bytes'] for r in group),
                           read_calls=None if case.startswith('device') else sum(r['read_calls'] for r in group),
                           update_calls=None if case.startswith('device') else sum(r['update_calls'] for r in group),
                           readData_calls=sum(bins.values()),
                           histogram=[dict(requested=p[0], returned=p[1], calls=n) for p, n in sorted(bins.items())]))
    return result


def verify(evidence):
    seal(evidence)
    assessment = read(evidence / 'assessment.json')
    check(assessment['status'] == 'complete' and assessment['cleanup'] and
          assessment['unexecuted_schedule'] == [] and assessment['unexecuted_count_schedule'] == [], 'execution blocked')
    reg = read(evidence / 'preregistration.json')
    check(reg['schedule'] == read(evidence / 'schedule.json') == expected_schedule() and
          reg['count_schedule'] == expected_schedule(True), 'schedule drift')
    for k, value in dict(configuration_timeout_seconds=300, compilation_timeout_seconds=300,
                         exclusions=['file open', 'memory load', 'digest comparison', 'JSON output'], retained_payload_cap=134217728, process_timeout_seconds=180, sweep_timeout_seconds=30,
                         termination_grace_seconds=5, retries=0, threads=1, primary_timer='update_ns',
                         no_cache_drops=True, no_cpu_pinning=True, no_governor_changes=True).items():
        check(reg[k] == value, 'protocol drift: ' + k)
    current = provenance(Path(reg['audit']), Path(reg['verification']))
    check(current == read(evidence / 'inputs.json') and reg['mapping'] == current['mapping'] and
          reg['runtime'] == current['runtime'], 'consumed-input drift')
    identities = []
    for label, counting in (('native', False), ('counting', True)):
        identity, rows = replay(evidence / (label + '.stdout'), reg, counting)
        identities.append(identity)
        process = read(evidence / (label + '.json'))
        check(identity['pid'] == process['pid'], 'process identity mismatch')
        if not counting:
            check(summaries(rows) == read(evidence / 'summary.json'), 'summary mismatch')
            check(len(rows) == 12000 and sum(r['bytes'] for r in rows if not r['warmup']) == 16745464320,
                  'measured population mismatch')
        else:
            check(count_summary(rows) == read(evidence / 'counts.json'), 'count summary mismatch')
        mapped = {line.split()[-1] for line in identity['maps'].splitlines()
                  if len(line.split()) >= 6 and line.split()[-1].startswith('/')}
        check({p: digest(Path(p)) for p in mapped if Path(p).is_file()} ==
              read(evidence / (label + '-mapped-identities.json')), 'mapping drift')
        for dep in current['dependencies'].values():
            check(str(Path(dep['host']).resolve()) in mapped, 'dependency mapping mismatch')
    check(identities[0]['pid'] != identities[1]['pid'], 'counting process not separate')
    for label, bound in (('configure', 300), ('compile', 300), ('correctness', 30), ('native', 180), ('counting', 180)):
        process = read(evidence / (label + '.json'))
        check(process['cleanup'] and not process['timed_out'] and process['returncode'] == 0 and
              process['elapsed_seconds'] <= bound+10, 'process failed: ' + label)
    binary = evidence / 'native/preview-hash-device-mechanism'
    saved = read(evidence / 'native-identity.json')
    linkage = subprocess.check_output(['ldd', str(binary)], text=True, timeout=30)
    check(re.sub(r' \(0x[0-9a-f]+\)', '', linkage) == re.sub(r' \(0x[0-9a-f]+\)', '', saved['linkage']), 'linkage drift')
    check(digest(binary) == saved['sha256'] and build_id(binary) == saved['build_id'], 'binary identity drift')
    check('CMAKE_BUILD_TYPE:STRING=Release' in (evidence / 'native/CMakeCache.txt').read_text(), 'not Release')
    commands = read(evidence / 'native/compile_commands.json')
    check(len(commands) == 1 and '-DNDEBUG' in commands[0]['command'], 'compile flags drift')
    for p, expected in read(evidence / 'tool-identities.json').items():
        check(digest(Path(p)) == expected, 'source/tool drift')
        snapshot = evidence / 'source' / Path(p).name
        if snapshot.exists(): check(digest(snapshot) == expected, 'snapshot drift')
    seal(evidence)
    return dict(status='passed', evidence_seal=digest(evidence / 'seal.json'), measured_sweeps=192,
                measured_rows=11520, measured_bytes=16745464320, warmup_sweeps=8, counting_sweeps=8,
                imports_runner_or_reporter=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check(not args.output.exists() and not args.output.resolve().is_relative_to(args.evidence.resolve()), 'destination collision')
    try:
        result = verify(args.evidence.resolve())
    except (ValueError, OSError, KeyError, TypeError, IndexError, subprocess.SubprocessError) as error:
        result = dict(status='failed', failure=str(error))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(result)
    sys.exit(result['status'] != 'passed')
