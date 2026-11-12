#!/usr/bin/env python3
"""Run the preregistered four-variant startup diagnostic and single pilot.

Root publishes protected fixtures only. Every benchmark runs as the ordinary
user. All fixtures and observations are retained, including numerical failures.
This deliberately cannot report full qualification.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
LABELS = ('A', 'B', 'C', 'D')


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


measurement = module('reuse', 'measure-preview-reuse.py')
generations = module('generations', 'manage-images-generations.py')


def observation_directory(output, mode, uid, gid):
    target = output / (mode + '-observations')
    target.mkdir()
    # Only the wrapper needs privilege. The ordinary-user harness creates its
    # own JSON files; inheriting the wrapper's ownership silently loses samples.
    os.chown(target, uid, gid)
    return target


def trace_overlap(paths):
    """Count requests with standby preparation overlapping a demand exchange.

    Runtime and pool events share native thread IDs; the pool_job identifies the
    demand slot and service. An exchange on that thread can overlap preparation
    only on the other slot. Process, request and monotonic time disambiguate
    recycled addresses. Old-service shutdown events are never treated as demand.
    """
    overlaps, missing = [], []
    for path in paths:
        events = [json.loads(line[6:]) for line in path.read_text().splitlines() if line.startswith('TRACE ')]
        def end_of(begin):
            return next((e for e in events if e['tid'] == begin['tid'] and e['object'] == begin['object'] and
                         e['phase'] == begin['phase'] and e['edge'] == 'end' and e['ns'] >= begin['ns']), None)
        jobs = [e for e in events if e['phase'] == 'pool_job' and e['edge'] == 'begin']
        if len(jobs) != 10:
            missing.append(str(path))
        for job in jobs:
            job_end = end_of(job)
            if job_end is None:
                missing.append(str(path) + ': unmatched job')
                continue
            exchanges = [e for e in events if e['tid'] == job['tid'] and
                         '_exchange_including_transport' in e['phase'] and e['edge'] == 'begin' and
                         job['ns'] <= e['ns'] <= job_end['ns']]
            # Worker preparation explicitly carries the control/service pointer
            # and slot. Do not confuse a previous service's deferred startup or
            # shutdown with this request when samples share a harness process.
            preparations = [e for e in events if e['phase'] == 'pool_worker_prepare' and e['edge'] == 'begin' and
                            e['object'] == job['object'] and e['slot'] != job['slot'] and
                            job['ns'] <= e['ns'] <= job_end['ns']]
            total = 0
            for begin in exchanges:
                end = end_of(begin)
                if end is None:
                    missing.append(str(path) + ': unmatched exchange')
                    continue
                for prepare in preparations:
                    prepared = end_of(prepare)
                    if prepared is None:
                        missing.append(str(path) + ': unmatched preparation')
                        continue
                    total += max(0, min(end['ns'], prepared['ns']) - max(begin['ns'], prepare['ns']))
            overlaps.append({'log': str(path), 'request': job['request'], 'service': job['object'],
                             'demand_slot': job['slot'], 'overlap_ms': total / 1e6})
    return {'requests': overlaps, 'missing_jobs': missing, 'overlapping_requests': sum(r['overlap_ms'] > 0 for r in overlaps)}


def pilot_assessment(records):
    rows, gates = {}, []
    for fixture in measurement.FIXTURES:
        rows[fixture] = {}
        for label in LABELS:
            values = records[(label, fixture)]
            rows[fixture][label] = {event: measurement.distribution([r[event] for r in values])
                                    for event in ('first_ms', 'final_ms')}
        for event in ('first_ms', 'final_ms'):
            a, c, d = (rows[fixture][label][event] for label in ('A', 'C', 'D'))
            limit = a['p95'] + max(5, a['p95'] * .1)
            gates.append({'fixture': fixture, 'event': event, 'candidate_p95': d['p95'],
                          'reference_p95': a['p95'], 'unchanged_p95': c['p95'], 'limit': limit,
                          'change_ms': d['p95'] - c['p95'], 'change_percent': (d['p95']/c['p95']-1)*100,
                          'passed': d['p95'] <= limit})
    # "both large-image startup p95 values" means pixels and final metadata
    # for the regressed 3200x2400 PNG; report all other fixtures as well.
    return {'summary': rows, 'gates': gates, 'passed': all(g['passed'] for g in gates) and
            all(g['change_ms'] < 0 for g in gates if g['fixture'] == '3200x2400.png')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('--uid', type=int, default=int(os.environ.get('SUDO_UID', '-1')))
    args = parser.parse_args()
    if os.geteuid() != 0 or args.uid <= 0:
        parser.error('root is needed only for protected fixtures; --uid must be ordinary')
    output = args.package.resolve()
    ready = json.loads((output / 'ready.json').read_text())
    previous, fixtures = Path(ready['previous']), Path(ready['fixtures'])
    prereg = json.loads((output / 'preregistration.json').read_text())
    account = pwd.getpwuid(args.uid)
    runtime_root = Path(tempfile.mkdtemp(prefix='holonight-standby-', dir='/run'))
    runtime_root.chmod(0o755)
    # Exclusive marker prohibits a second pilot, including after an interrupted run.
    with (output / 'measurement-started.json').open('x') as marker:
        json.dump({'runtime_root': str(runtime_root), 'uid': args.uid}, marker)
    shutil.copy2(__file__, output / 'runner.py')
    env = dict(os.environ, HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name,
               XDG_RUNTIME_DIR=f'/run/user/{args.uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{args.uid}/bus', QT_QPA_PLATFORM='offscreen')
    cgroups = Path(f'/sys/fs/cgroup/user.slice/user-{args.uid}.slice/user@{args.uid}.service')
    def scopes():
        return {str(p) for p in cgroups.glob('**/holonight-images-*.scope')}
    initial_scopes = scopes()
    bases = {(mode, label): output / mode / label if mode == 'diagnostic' or label == 'D' else previous / label
             for mode in ('diagnostic', 'pilot') for label in LABELS}
    identities = {f'{mode}/{label}': {str(p): measurement.digest(p) for p in
                  (base / 'reuse-harness/preview-benchmark', base / 'build/holonight-images/holonight-images-helper')}
                  for (mode, label), base in bases.items()}
    (output / 'measurement-inputs.json').write_text(json.dumps(identities, indent=2) + '\n')
    failure = None
    result = {'qualified': False, 'runtime_root': str(runtime_root)}
    try:
        for mode in ('diagnostic', 'pilot'):
            target_dir = observation_directory(output, mode, args.uid, account.pw_gid)
            runtimes = {}
            for label in LABELS:
                base = bases[(mode, label)]
                runtime = runtime_root / mode / label
                runtime.parent.mkdir(exist_ok=True)
                source = base / ('runtime-final' if mode == 'pilot' and label in ('B', 'C') else 'runtime')
                if label == 'A':
                    shutil.copytree(source, runtime)
                else:
                    generations.run(SimpleNamespace(runtime=runtime, source=source, helper=base / 'build/holonight-images/holonight-images-helper',
                        command='install', ownership_manifest=None, maintenance_migrate=False))
                runtimes[label] = runtime
            records = {(label, fixture): [] for label in LABELS for fixture in measurement.FIXTURES}
            failures = []
            def run(label, fixture, count, tag):
                target = target_dir / (tag + '.json')
                command = [str(bases[(mode, label)] / 'reuse-harness/preview-benchmark'), str(runtimes[label]),
                           str(fixtures / fixture), 'startup', str(count), str(target)]
                with target.with_suffix('.log').open('x') as log:
                    process = subprocess.run(command, env=env, user=args.uid, group=account.pw_gid,
                        extra_groups=os.getgrouplist(account.pw_name, account.pw_gid), stdout=log, stderr=subprocess.STDOUT, timeout=max(60, count * 40))
                data = json.loads(target.read_text()) if target.exists() else {}
                observations = data.get('samples', [])
                if not tag.startswith('warmup'):
                    records[(label, fixture)].extend(observations)
                if process.returncode or data.get('cleanup_failure') or len(observations) != count or any(not measurement.valid_observation(r) for r in observations):
                    failures.append(f'{tag}: exit {process.returncode}, invalid observations or cleanup')
                if scopes() - initial_scopes:
                    failures.append(f'{tag}: residual helper scopes: {sorted(scopes() - initial_scopes)}')
            for fixture in measurement.FIXTURES:
                for label in LABELS:
                    run(label, fixture, 1, f'warmup-{label}-{fixture}')
                for block in range(10):
                    for label in LABELS[block % 4:] + LABELS[:block % 4]:
                        run(label, fixture, 10, f'block-{block:02}-{label}-{fixture}')
                    print(mode, fixture, (block + 1) * 10, flush=True)
            result[mode] = {'failures': failures, 'assessment': pilot_assessment(records) if not failures else None}
            if mode == 'diagnostic':
                overlap = {label: trace_overlap(sorted(target_dir.glob(f'block-*-{label}-*.log'))) for label in ('C', 'D')}
                result['overlap'] = overlap
                supported = (all(len(v['requests']) == 400 and not v['missing_jobs'] for v in overlap.values()) and
                             overlap['C']['overlapping_requests'] > 0 and overlap['D']['overlapping_requests'] == 0)
                result['trace_support'] = supported
                if failures or not supported:
                    raise RuntimeError('diagnostic invalid or overlap evidence inconclusive; stop before pilot')
            elif failures or not result[mode]['assessment']['passed']:
                raise RuntimeError('single startup pilot failed; stop without production correction or qualification')
            (output / (mode + '-result.json')).write_text(json.dumps(result, indent=2) + '\n')
        result['eligible_for_correction'] = True
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        failure = str(error)
        result['failure'] = failure
        print(failure, flush=True)
    result['identities_unchanged'] = all(measurement.digest(Path(p)) == value for group in identities.values() for p, value in group.items())
    result['fixtures_unchanged'] = all(measurement.digest(fixtures / name) == value for name, value in prereg['fixtures'].items())
    result['shutdown_verified'] = not (scopes() - initial_scopes)
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    raise SystemExit(1 if failure or not all(result[k] for k in ('identities_unchanged', 'fixtures_unchanged', 'shutdown_verified')) else 0)


if __name__ == '__main__':
    main()
