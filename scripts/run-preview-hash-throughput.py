#!/usr/bin/env python3
"""Build and run the preregistered, bounded host-native SHA-256 diagnostic."""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import selectors
import shutil
import signal
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hash_evidence_checks', ROOT / 'scripts/verify-preview-hash-throughput.py')
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
    for block in range(5):
        for case in cases[block:] + cases[:block]:
            for sweep in range(5):
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


def report(rows):
    # Reporting implementation is separate from the independent checker.
    def distribution(values):
        values.sort()
        return dict(count=len(values), minimum=min(values), maximum=max(values), median=statistics.median(values),
                    p95=values[math.ceil(len(values)*.95)-1])
    cells = []
    for warmup, blocks in ((True, [None]), (False, ['pooled', 0, 1, 2, 3, 4])):
        for block in blocks:
            for case in v.CASES:
                group = [r for r in rows if r['case'] == case and r['warmup'] == warmup and
                         (block == 'pooled' or r['block'] == block)]
                size, ns = sum(r['bytes'] for r in group), sum(r['update_ns'] for r in group)
                times = {}
                for r in group:
                    times[r['index']] = times.get(r['index'], 0) + r['update_ns']
                cells.append(dict(case=case, block=block, warmup=warmup, files=len(group), bytes=size, update_ns=ns,
                                  bytes_per_second=size*1e9/ns,
                                  durations={k: distribution([r[k] for r in group]) for k in ('init_ns', 'update_ns', 'final_ns')},
                                  sweep_update_ns=distribution(list(times.values())),
                                  file_bytes_per_second=distribution([r['bytes']*1e9/r['update_ns'] for r in group]),
                                  sweep_bytes_per_second=distribution([sum(r['bytes'] for r in group if r['index'] == i)*1e9/t
                                                                      for i, t in times.items()])))
    ratios = []
    for block in range(5):
        rates = {r['case']: r['bytes_per_second'] for r in cells if r['block'] == block and not r['warmup']}
        for a, b in (('qt_device', 'qt_file'), ('qt_file', 'evp_file'), ('qt_memory', 'evp_memory')):
            ratios.append(dict(block=block, numerator=a, denominator=b, ratio=rates[a]/rates[b]))
    return dict(cells=cells, ratios=ratios)


def run(audit, verification, output):
    v.check(not output.exists(), 'destination collision')
    v.check(not any(output.is_relative_to(p) or p.is_relative_to(output) for p in (audit, verification)), 'destination overlaps input')
    output.mkdir(parents=True)
    result = dict(status='blocked', stage='provenance', cleanup=True, unexecuted_schedule=schedule())
    registration = dict(audit=str(audit), verification=str(verification), schedule=schedule(), chunk_bytes=65536,
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
        paths = [ROOT / 'tooling/preview-hash-throughput' / name for name in ('CMakeLists.txt', 'main.cpp')]
        paths += [Path(__file__).resolve(), ROOT / 'scripts/verify-preview-hash-throughput.py',
                  ROOT / 'tests/test_preview_hash_throughput.py', ROOT / 'tooling/preview-hash-throughput/README.md']
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
        binary = output / 'native/preview-hash-throughput'
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
        result['stage'] = 'accounting'
        identity, rows = v.replay(output / 'native.stdout', registration)
        mapped = {line.split()[-1] for line in identity['maps'].splitlines() if len(line.split()) >= 6 and line.split()[-1].startswith('/')}
        write(output / 'mapped-identities.json', {p: v.digest(Path(p)) for p in mapped if Path(p).is_file()})
        summary = report(rows)
        write(output / 'summary.json', summary)
        v.check(summary == v.summaries(rows), 'independent arithmetic mismatch')
        v.check(v.provenance(audit, verification) == inputs, 'post-execution provenance drift')
        v.check(all(v.digest(Path(p)) == d for p, d in identities.items()), 'tool/source drift')
        result.update(status='complete', stage='complete', unexecuted_schedule=[])
        lines = ['# Native SHA-256 diagnostic', '', 'Primary throughput uses summed logical bytes / summed update time.', '',
                 '| Case | MiB/s |', '|---|---:|']
        for cell in summary['cells']:
            if cell['block'] == 'pooled':
                lines.append(f"| {cell['case']} | {cell['bytes_per_second']/1048576:.3f} |")
        lines += ['', 'Block-matched throughput ratios (numerator / denominator):', '']
        for a, b in (('qt_device', 'qt_file'), ('qt_file', 'evp_file'), ('qt_memory', 'evp_memory')):
            values = [r['ratio'] for r in summary['ratios'] if r['numerator'] == a and r['denominator'] == b]
            agree = all(x > 1 for x in values) or all(x < 1 for x in values)
            lines.append(f"{a} / {b}: " + ', '.join(f'{x:.5f}' for x in values) + f'. Directions agree: {agree}.')
        device_ratios = [r['ratio'] for r in summary['ratios'] if r['numerator'] == 'qt_device']
        recommendation = ('Investigate the Qt device buffering/read path with focused source inspection: its throughput is lower '
                          'than Qt file streaming in every block. This diagnostic alone cannot assign causality.'
                          if all(x < 1 for x in device_ratios) else
                          'The Qt device/file comparison is inconclusive for a consistent device-path penalty; no optimization is selected.')
        lines += ['', 'File-access, Qt device buffering, streaming-call overhead, scheduling and backend dispatch costs remain unresolved. '
                  'EVP provider/mapped libraries are recorded; Qt provider and hardware dispatch are not inferred. '
                  'Historical audit throughput has different timer/probe conditions and is contextual, not a paired arm. '
                  'No slow-crypto threshold, performance qualification, whole-preview gain or automatic optimization selection. ' +
                  recommendation, '']
        (output / 'REPORT.md').write_text('\n'.join(lines))
    except (ValueError, OSError, KeyError, TypeError, IndexError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        process_records = [v.read(output / (label + '.json')) for label in
                           ('configure', 'compile', 'correctness', 'native') if (output / (label + '.json')).exists()]
        result['cleanup'] = all(record['cleanup'] for record in process_records)
        if (output / 'native.json').exists():
            if result['status'] != 'complete':
                completed = set()
                for line in (output / 'native.stdout').read_text().splitlines():
                    try:
                        row = json.loads(line)
                        if row.get('type') == 'sweep_end':
                            completed.add(row['index'])
                    except (ValueError, KeyError):
                        pass
                result['unexecuted_schedule'] = [s for s in schedule() if s['index'] not in completed]
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
