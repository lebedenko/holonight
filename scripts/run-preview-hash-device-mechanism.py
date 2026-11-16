#!/usr/bin/env python3
"""Build and run the preregistered, bounded host-native SHA-256 diagnostic."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hash_evidence_checks', ROOT / 'scripts/verify-preview-hash-device-mechanism.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def seal(root):
    write(root / 'seal.json', {str(p.relative_to(root)): v.digest(p) for p in sorted(root.rglob('*')) if p.is_file()})


def schedule():
    cases = list(v.CASES)
    rows = [dict(case=c, block=None, warmup=True, sweep=0) for c in cases]
    for block in range(8):
        for case in cases[block:] + cases[:block]:
            for sweep in range(3):
                rows.append(dict(case=case, block=block, warmup=False, sweep=sweep))
    return [dict(index=i, **r) for i, r in enumerate(rows)]


def stop(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)
    try:
        os.killpg(process.pid, 0)
    except ProcessLookupError:
        return True
    return False


def execute(argv, output, label, timeout, diagnostic=False):
    write(output / (label + '-command.json'), dict(argv=[str(a) for a in argv], timeout_seconds=timeout,
                                                sweep_timeout_seconds=30 if diagnostic else None))
    result = dict(cleanup=False, returncode=None, timed_out=False)
    env = dict(os.environ, DEBUGINFOD_URLS='')
    start = time.monotonic()
    with (output / (label + '.stdout')).open('xb') as stdout, (output / (label + '.stderr')).open('xb') as stderr:
        process = subprocess.Popen([str(a) for a in argv], stdout=subprocess.PIPE if diagnostic else stdout,
                                   stderr=stderr, start_new_session=True, env=env)
        result['pid'] = process.pid
        try:
            if diagnostic:
                # Every sweep completion resets this deadline. Preloading has the
                # same conservative bound before the first completed sweep.
                deadline = start + 30
                pending = b''
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout, selectors.EVENT_READ)
                    while selector.get_map():
                        remaining = min(start + timeout, deadline) - time.monotonic()
                        if remaining <= 0:
                            raise subprocess.TimeoutExpired(argv, timeout)
                        for key, _ in selector.select(min(remaining, .25)):
                            data = os.read(key.fileobj.fileno(), 65536)
                            if not data:
                                selector.unregister(key.fileobj)
                                break
                            stdout.write(data)
                            stdout.flush()
                            pending += data
                            while b'\n' in pending:
                                line, pending = pending.split(b'\n', 1)
                                record = json.loads(line)
                                if record.get('type') == 'sweep_end':
                                    deadline = time.monotonic() + 30
                process.wait(timeout=max(.001, start + timeout - time.monotonic()))
            else:
                process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            result['timed_out'] = True
        finally:
            result['cleanup'] = stop(process)
            if process.stdout:
                process.stdout.close()
            result.update(returncode=process.returncode, elapsed_seconds=time.monotonic()-start)
            write(output / (label + '.json'), result)
    v.check(result['cleanup'] and not result['timed_out'] and result['returncode'] == 0,
            label + ' failed: ' + str(result))
    return result


def count_schedule():
    return [dict(index=i, case=c, block=None, warmup=False, sweep=0) for i, c in enumerate(v.CASES)]


def report(rows):
    cells = []
    for case in v.CASES:
        group = [r for r in rows if r['case'] == case and not r['warmup']]
        size, ns = sum(r['bytes'] for r in group), sum(r['update_ns'] for r in group)
        cells.append(dict(case=case, bytes=size, update_ns=ns, bytes_per_second=size*1e9/ns))
    contrasts = []
    for block in range(8):
        for ai, bi in v.CONTRASTS:
            a, b = v.CASES[ai], v.CASES[bi]
            contributions = []
            ordinals = sorted({r['ordinal'] for r in rows})
            for ordinal in ordinals:
                sums = [sum(r['update_ns'] for r in rows if r['block'] == block and
                            not r['warmup'] and r['case'] == c and r['ordinal'] == ordinal) for c in (a, b)]
                contributions.append(dict(ordinal=ordinal, left_sum_ns=sums[0], right_sum_ns=sums[1],
                                          difference_sum_ns=sums[0]-sums[1]))
            left, right = (sum(r[k] for r in contributions) for k in ('left_sum_ns', 'right_sum_ns'))
            contrasts.append(dict(block=block, left=a, right=b, left_sum_ns=left, right_sum_ns=right,
                                  difference_sum_ns=left-right, mean_difference_ns=(left-right)/3,
                                  duration_ratio=left/right, contributions=contributions))
    return dict(cells=cells, contrasts=contrasts)


def report_counts(rows):
    result = []
    for case in v.CASES:
        group = [r for r in rows if r['case'] == case]
        pairs = sorted({(h['requested'], h['returned']) for r in group for h in r['histogram']})
        histogram = [dict(requested=a, returned=b, calls=sum(h['calls'] for r in group for h in r['histogram']
                     if (h['requested'], h['returned']) == (a, b))) for a, b in pairs]
        result.append(dict(case=case, files=len(group), bytes=sum(r['bytes'] for r in group),
                           read_calls=None if case.startswith('device') else sum(r['read_calls'] for r in group),
                           update_calls=None if case.startswith('device') else sum(r['update_calls'] for r in group),
                           readData_calls=sum(h['calls'] for h in histogram), histogram=histogram))
    return result


def run(audit, verification, output):
    v.check(not output.exists(), 'destination collision')
    v.check(not any(output.is_relative_to(p) or p.is_relative_to(output) for p in (audit, verification)), 'destination overlaps input')
    output.mkdir(parents=True)
    result = dict(status='blocked', stage='provenance', cleanup=True, unexecuted_schedule=schedule(), unexecuted_count_schedule=count_schedule())
    registration = dict(audit=str(audit), verification=str(verification), schedule=schedule(), count_schedule=count_schedule(),
                        retained_payload_cap=134217728, process_timeout_seconds=180, sweep_timeout_seconds=30,
                        termination_grace_seconds=5, configuration_timeout_seconds=300, compilation_timeout_seconds=300,
                        retries=0, threads=1, primary_timer='update_ns',
                        exclusions=['file open', 'memory load', 'digest comparison', 'JSON output'],
                        no_cache_drops=True, no_cpu_pinning=True, no_governor_changes=True)
    try:
        write(output / 'schedule.json', schedule())
        inputs = v.provenance(audit, verification)
        write(output / 'inputs.json', inputs)
        registration.update(runtime=inputs['runtime'], mapping=inputs['mapping'])
        write(output / 'preregistration.json', registration)
        source = output / 'source'
        source.mkdir()
        paths = [ROOT / 'tooling/preview-hash-device-mechanism' / name for name in ('CMakeLists.txt', 'main.cpp')]
        paths += [Path(__file__).resolve(), ROOT / 'scripts/verify-preview-hash-device-mechanism.py',
                  ROOT / 'tests/test_preview_hash_device_mechanism.py', ROOT / 'tooling/preview-hash-device-mechanism/README.md',
                  ROOT / 'docs/sdd/preview-hash-device-mechanism.md']
        identities = {str(p): v.digest(p) for p in paths}
        for p in paths:
            shutil.copyfile(p, source / p.name)
        for name in ('cmake', 'c++', 'readelf'):
            path = Path(shutil.which(name) or '/missing-tool').resolve()
            identities[str(path)] = v.digest(path)
        write(output / 'tool-identities.json', identities)
        write(output / 'host.json', dict(uname=list(os.uname()), cpuinfo=Path('/proc/cpuinfo').read_text(),
                                         affinity=sorted(os.sched_getaffinity(0)), environment={k: os.environ.get(k) for k in
                                         ('CXX', 'CC', 'CXXFLAGS', 'CFLAGS', 'LDFLAGS', 'CMAKE_PREFIX_PATH', 'LD_LIBRARY_PATH', 'OPENSSL_CONF', 'OPENSSL_MODULES')}))
        result['stage'] = 'configure'
        execute(['cmake', '-S', source, '-B', output / 'native', '-DCMAKE_BUILD_TYPE=Release'], output, 'configure', 300)
        result['stage'] = 'compile'
        execute(['cmake', '--build', output / 'native', '--parallel', '2'], output, 'compile', 300)
        binary = output / 'native/preview-hash-device-mechanism'
        linkage = subprocess.check_output(['ldd', str(binary)], text=True, timeout=30)
        v.check('not found' not in linkage, 'unresolved dependency')
        for name, dep in inputs['dependencies'].items():
            v.check(any(line.strip().startswith(name + ' => ') and str(Path(line.split('=>')[1].split()[0]).resolve()) ==
                        str(Path(dep['host']).resolve()) for line in linkage.splitlines()), 'linked dependency mismatch: ' + name)
        write(output / 'native-identity.json', dict(sha256=v.digest(binary), build_id=v.build_id(binary), linkage=linkage))
        result['stage'] = 'correctness'
        execute([binary, '--self-test'], output, 'correctness', 30)
        v.check(v.provenance(audit, verification) == inputs, 'pre-execution provenance drift')
        result['stage'] = 'measurement'
        measured = execute([binary, output / 'preregistration.json'], output, 'native', 180, diagnostic=True)
        result.update(measured)
        result['stage'] = 'counting'
        execute([binary, output / 'preregistration.json', '--count'], output, 'counting', 180, diagnostic=True)
        result['stage'] = 'accounting'
        identity, rows = v.replay(output / 'native.stdout', registration)
        mapped = {line.split()[-1] for line in identity['maps'].splitlines() if len(line.split()) >= 6 and line.split()[-1].startswith('/')}
        write(output / 'native-mapped-identities.json', {p: v.digest(Path(p)) for p in mapped if Path(p).is_file()})
        count_identity, count_rows = v.replay(output / 'counting.stdout', registration, True)
        mapped_count = {line.split()[-1] for line in count_identity['maps'].splitlines()
                        if len(line.split()) >= 6 and line.split()[-1].startswith('/')}
        write(output / 'counting-mapped-identities.json', {p: v.digest(Path(p)) for p in mapped_count if Path(p).is_file()})
        counts = report_counts(count_rows)
        write(output / 'counts.json', counts)
        v.check(counts == v.count_summary(count_rows), 'count arithmetic mismatch')
        summary = report(rows)
        write(output / 'summary.json', summary)
        v.check(summary == v.summaries(rows), 'independent arithmetic mismatch')
        v.check(v.provenance(audit, verification) == inputs, 'post-execution provenance drift')
        v.check(all(v.digest(Path(p)) == d for p, d in identities.items()), 'tool/source drift')
        result.update(status='complete', stage='complete', unexecuted_schedule=[], unexecuted_count_schedule=[])
        lines = ['# Qt chunk-size and buffering diagnostic', '',
                 'Signed differences use left minus right block means; positive means left takes longer.', '',
                 '| Arm | Pooled MiB/s (descriptive) |', '|---|---:|']
        for cell in summary['cells']:
            lines.append(f"| {cell['case']} | {cell['bytes_per_second']/1048576:.3f} |")
        lines += ['', '| Left / right | Block | Difference ms | Duration ratio |', '|---|---:|---:|---:|']
        for c in summary['contrasts']:
            lines.append(f"| {c['left']} / {c['right']} | {c['block']} | {c['mean_difference_ns']/1e6:+.6f} | {c['duration_ratio']:.6f} |")
        lines += ['', 'Direction agreement by contrast:']
        for ai, bi in v.CONTRASTS:
            a, b = v.CASES[ai], v.CASES[bi]
            values = [c['difference_sum_ns'] for c in summary['contrasts'] if (c['left'], c['right']) == (a, b)]
            agree = all(x > 0 for x in values) or all(x < 0 for x in values)
            lines.append(f'{a} / {b}: ' + ('consistent direction.' if agree else 'inconclusive: block directions disagree.'))
        lines += ['', '| Arm | readData calls | Public reads | Updates |', '|---|---:|---:|---:|']
        for c in counts:
            lines.append(f"| {c['case']} | {c['readData_calls']} | {c['read_calls']} | {c['update_calls']} |")
        lines += ['', 'Counts are Qt readData calls in a QFile subclass in a separate process, not syscalls. '
                  'Device public-read and hash-update counts remain unobserved. Instrumentation cannot establish identical '
                  'branches in the timed process. Effects belong to these configurations and need not be additive. '
                  'Memory timings are not subtracted to estimate exact file-I/O cost. No hardware dispatch, statistical '
                  'significance, exact elapsed decomposition, whole-preview gain or production optimization is claimed.', '']
        (output / 'REPORT.md').write_text('\n'.join(lines))
    except (ValueError, OSError, KeyError, TypeError, IndexError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        process_records = [v.read(output / (label + '.json')) for label in
                           ('configure', 'compile', 'correctness', 'native', 'counting') if (output / (label + '.json')).exists()]
        result['cleanup'] = all(record['cleanup'] for record in process_records)
        for label, planned, key in (('native', schedule(), 'unexecuted_schedule'),
                                    ('counting', count_schedule(), 'unexecuted_count_schedule')):
            completed = set()
            raw = output / (label + '.stdout')
            if raw.exists():
                for line in raw.read_text().splitlines():
                    try:
                        row = json.loads(line)
                        if row.get('type') == 'sweep_end': completed.add(row['index'])
                    except (ValueError, KeyError): pass
            result[key] = [s for s in planned if s['index'] not in completed]
        write(output / 'assessment.json', result)
        if not (output / 'REPORT.md').exists():
            (output / 'REPORT.md').write_text('# Native SHA-256 diagnostic blocked\n\nFailed gate: ' +
                result['stage'] + '\n\n' + result.get('failure', '') + '\n\n' +
                str(len(result['unexecuted_schedule'])) + ' sweeps remain uncompleted. '
                'Partial evidence is preserved. Performance interpretation is blocked. No retries were attempted.\n')
        seal(output)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('audit', 'verification', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    result = run(args.audit.resolve(), args.verification.resolve(), args.output.resolve())
    print({k: value for k, value in result.items() if k != 'unexecuted_schedule'},
          'unexecuted_sweeps=', len(result['unexecuted_schedule']))
    sys.exit(result['status'] != 'complete')
