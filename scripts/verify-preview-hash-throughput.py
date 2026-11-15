#!/usr/bin/env python3
"""Independent standard-library-only replay of the native SHA-256 diagnostic."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import sys

CASES = ('qt_device', 'qt_file', 'evp_file', 'qt_memory', 'evp_memory')


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


def provenance(audit, verification):
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


def expected_schedule():
    result = [dict(case=case, block=None, warmup=True, sweep=0) for case in CASES]
    for block in range(5):
        for case in CASES[block:] + CASES[:block]:
            result.extend(dict(case=case, block=block, warmup=False, sweep=sweep) for sweep in range(5))
    return [dict(index=i, **row) for i, row in enumerate(result)]


def dist(values):
    values = sorted(values)
    return dict(count=len(values), minimum=values[0], median=statistics.median(values),
                p95=values[math.ceil(.95 * len(values))-1], maximum=values[-1])


def replay(path, registration):
    records = [decode(line) for line in path.read_text().splitlines()]
    check(records and records[0]['type'] == 'identity', 'missing process identity')
    identity = records.pop(0)
    check(type(identity['pid']) is int and identity['pid'] > 0 and bool(identity['provider']), 'invalid process identity')
    schedule = expected_schedule()
    check(registration['schedule'] == schedule, 'schedule drift')
    rows = []
    position = 0
    for sweep in schedule:
        for file in registration['mapping']:
            check(position < len(records), 'missing file row')
            row = records[position]
            position += 1
            check(row['type'] == 'file' and all(row[k] == v for k, v in sweep.items()), 'file schedule mismatch')
            check(row['ordinal'] == file['ordinal'] and row['bytes'] == file['size'] and row['sha256'] == file['sha256'], 'file/digest mismatch')
            check(all(type(row[k]) is int and row[k] > 0 for k in ('init_ns', 'update_ns', 'final_ns')), 'nonpositive/noninteger duration')
            rows.append(row)
        check(position < len(records), 'missing sweep completion')
        end = records[position]
        position += 1
        selected = rows[-len(registration['mapping']):]
        check(end['type'] == 'sweep_end' and end['index'] == sweep['index'] and
              type(end['elapsed_ns']) is int and 0 < end['elapsed_ns'] <= 30000000000 and
              sum(r[k] for r in selected for k in ('init_ns', 'update_ns', 'final_ns')) <= end['elapsed_ns'], 'invalid sweep bound')
    check(position == len(records), 'extra/duplicate output')
    return identity, rows


def summaries(rows):
    cells = []
    for warmup in (True, False):
        for block in ([None] if warmup else ['pooled', *range(5)]):
            for case in CASES:
                selected = [r for r in rows if r['warmup'] == warmup and r['case'] == case and
                            (block == 'pooled' or r['block'] == block)]
                size = sum(r['bytes'] for r in selected)
                ns = sum(r['update_ns'] for r in selected)
                sweeps = [sum(r['update_ns'] for r in selected if r['index'] == i) for i in sorted({r['index'] for r in selected})]
                cells.append(dict(warmup=warmup, block=block, case=case, files=len(selected), bytes=size,
                                  update_ns=ns, bytes_per_second=size*1e9/ns,
                                  durations={k: dist([r[k] for r in selected]) for k in ('init_ns', 'update_ns', 'final_ns')},
                                  sweep_update_ns=dist(sweeps),
                                  file_bytes_per_second=dist([r['bytes']*1e9/r['update_ns'] for r in selected]),
                                  sweep_bytes_per_second=dist([sum(r['bytes'] for r in selected if r['index'] == i)*1e9/
                                      sum(r['update_ns'] for r in selected if r['index'] == i)
                                      for i in sorted({r['index'] for r in selected})])))
    ratios = []
    for block in range(5):
        rates = {c['case']: c['bytes_per_second'] for c in cells if not c['warmup'] and c['block'] == block}
        for left, right in (('qt_device', 'qt_file'), ('qt_file', 'evp_file'), ('qt_memory', 'evp_memory')):
            ratios.append(dict(block=block, numerator=left, denominator=right, ratio=rates[left]/rates[right]))
    return dict(cells=cells, ratios=ratios)


def check_accounting(rows, saved):
    check(summaries(rows) == saved, 'accounting/distribution/ratio mismatch')


def verify_early_failure(evidence, assessment):
    """Verify a pre-sweep failure without presenting any performance result."""
    check(assessment['stage'] == 'measurement' and assessment['cleanup'] is True,
          'unsupported partial-evidence gate')
    inputs = read(evidence / 'inputs.json')
    check(provenance(Path(inputs['audit']), Path(inputs['verification'])) == inputs,
          'partial evidence provenance drift')
    reg = read(evidence / 'preregistration.json')
    check(reg['schedule'] == read(evidence / 'schedule.json') == expected_schedule() ==
          assessment['unexecuted_schedule'], 'partial schedule mismatch')
    check(reg['mapping'] == inputs['mapping'] and reg['runtime'] == inputs['runtime'],
          'partial registration payload drift')
    check((evidence / 'native.stdout').read_bytes() == b'', 'partial evidence contains unexplained rows')
    process = read(evidence / 'native.json')
    check(process['returncode'] != 0 and process['cleanup'] and not process['timed_out'],
          'partial process failure/cleanup mismatch')
    for label in ('configure', 'compile', 'correctness'):
        saved = read(evidence / (label + '.json'))
        check(saved['returncode'] == 0 and saved['cleanup'] and not saved['timed_out'],
              'partial prerequisite failure: ' + label)
    native = read(evidence / 'native-identity.json')
    binary = evidence / 'native/preview-hash-throughput'
    check(digest(binary) == native['sha256'] and build_id(binary) == native['build_id'], 'partial native identity drift')
    for path, expected in read(evidence / 'tool-identities.json').items():
        snapshot = evidence / 'source' / Path(path).name
        check(digest(snapshot if snapshot.exists() else Path(path)) == expected, 'partial source/tool identity drift')
    seal(evidence)
    return dict(status='blocked', integrity_status='passed', experiment_status='blocked',
                evidence_seal=digest(evidence / 'seal.json'), measured_sweeps=0, warmup_sweeps=0,
                unexecuted_sweeps=130, cleanup=True, performance_interpretation=False,
                failure=assessment['failure'], imports_runner_or_reporter=False)


def verify(evidence):
    seal(evidence)
    assessment = read(evidence / 'assessment.json')
    if assessment['status'] == 'blocked':
        return verify_early_failure(evidence, assessment)
    check(assessment['status'] == 'complete' and assessment['cleanup'] is True and assessment['returncode'] == 0 and
          assessment['unexecuted_schedule'] == [], 'execution blocked/incomplete')
    reg = read(evidence / 'preregistration.json')
    for key, value in dict(chunk_bytes=65536, retained_payload_cap=134217728, process_timeout_seconds=180,
                           sweep_timeout_seconds=30, termination_grace_seconds=5, configuration_timeout_seconds=300,
                           compilation_timeout_seconds=300, retries=0, threads=1, primary_timer='update_ns',
                           exclusions=['file open', 'memory load', 'digest comparison', 'JSON output'],
                           no_cache_drops=True, no_cpu_pinning=True, no_governor_changes=True).items():
        check(reg[key] == value, 'protocol drift: ' + key)
    check(read(evidence / 'schedule.json') == expected_schedule(), 'persisted schedule drift')
    for label, bound in (('configure', 300), ('compile', 300), ('correctness', 30), ('native', 180)):
        process = read(evidence / (label + '.json'))
        check(process['cleanup'] and not process['timed_out'] and process['returncode'] == 0 and
              process['elapsed_seconds'] <= bound + 5, 'process bound/cleanup failed: ' + label)
    cache = (evidence / 'native/CMakeCache.txt').read_text()
    check('CMAKE_BUILD_TYPE:STRING=Release' in cache, 'non-Release build')
    commands = read(evidence / 'native/compile_commands.json')
    check(len(commands) == 1 and '-DNDEBUG' in commands[0]['command'], 'missing release compile flags')
    current = provenance(Path(reg['audit']), Path(reg['verification']))
    check(current == read(evidence / 'inputs.json'), 'consumed provenance drift')
    check(reg['mapping'] == current['mapping'] and reg['runtime'] == current['runtime'], 'registration payload drift')
    identity, rows = replay(evidence / 'native.stdout', reg)
    check_accounting(rows, read(evidence / 'summary.json'))
    saved = read(evidence / 'native-identity.json')
    binary = evidence / 'native/preview-hash-throughput'
    check(digest(binary) == saved['sha256'] and build_id(binary) == saved['build_id'], 'native binary drift')
    mapped = {line.split()[-1] for line in identity['maps'].splitlines() if len(line.split()) >= 6 and line.split()[-1].startswith('/')}
    for name, dep in current['dependencies'].items():
        check(str(Path(dep['host']).resolve()) in mapped, 'required host dependency not mapped: ' + name)
    expected_maps = {p: digest(Path(p)) for p in mapped if Path(p).is_file()}
    check(expected_maps == read(evidence / 'mapped-identities.json'), 'mapped library identity drift')
    check(not any('libcrypto' in p and p != str(Path(current['dependencies']['libcrypto.so.4']['host']).resolve()) for p in mapped), 'unexpected crypto mapping')
    check(identity['pid'] == assessment['pid'], 'process identity mismatch')
    for path, expected in read(evidence / 'tool-identities.json').items():
        check(digest(Path(path)) == expected, 'source/tool drift')
    check(read(evidence / 'correctness.json')['returncode'] == 0, 'native correctness failed')
    seal(evidence)
    return dict(status='passed', evidence_seal=digest(evidence / 'seal.json'), measured_sweeps=125,
                warmup_sweeps=5, measured_rows=7500, warmup_rows=300,
                measured_bytes=sum(r['bytes'] for r in rows if not r['warmup']), imports_runner_or_reporter=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check(not args.output.exists() and not args.output.resolve().is_relative_to(args.evidence.resolve()), 'destination collision or output inside evidence')
    try:
        result = verify(args.evidence.resolve())
    except (ValueError, OSError, KeyError, TypeError, IndexError, subprocess.SubprocessError) as error:
        result = dict(status='failed', failure=str(error))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(result)
    sys.exit(result['status'] != 'passed')
