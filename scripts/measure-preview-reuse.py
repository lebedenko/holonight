#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Alternate frozen native Release A/B/C blocks against protected disposable runtimes.

Requires root only to publish /run fixtures; harnesses execute as the invoking
ordinary user. Historical evidence is never overwritten. Lifecycle/resource
qualification is separate from this latency run.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import pwd
import shutil
import statistics
import subprocess
import tempfile
from types import SimpleNamespace

SCENARIOS = ('ready', 'disk', 'memory', 'startup', 'recycle', 'cancel-depletion',
             'navigation-0', 'navigation-25', 'navigation-100', 'navigation-250')
FIXTURES = ('160x80.png', '1600x1200.png', '3200x2400.png', 'oriented.jpg')
LABELS = ('A', 'B', 'C')
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('generations', ROOT / 'scripts/manage-images-generations.py')
generations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generations)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def distribution(values):
    ordered = sorted(values)
    return {'median': statistics.median(ordered), 'p95': ordered[math.ceil(len(ordered) * .95) - 1]} if ordered else None


def valid_observation(row):
    first, final = row.get('first_ms'), row.get('final_ms')
    return (row.get('success') is True and row.get('setup_success') is True and
            row.get('correct_pixels') is True and row.get('correct_metadata') is True and
            not row.get('cleanup_failure') and not row.get('harness_timeout') and
            all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                for value in (first, final)) and 0 <= first <= final)


def assess(records, scenarios, samples):
    summary = {}
    passed = samples == 100 and set(scenarios) == set(SCENARIOS)
    gates = []
    for fixture in FIXTURES:
        for scenario in scenarios:
            rows = {}
            for label in LABELS:
                observations = records.get((label, fixture, scenario), [])
                failures = sum(not valid_observation(row) for row in observations)
                missing = samples - len(observations)
                events = {event: distribution([row[event] for row in observations
                                              if isinstance(row.get(event), (int, float)) and math.isfinite(row[event]) and row[event] >= 0])
                          for event in ('first_ms', 'final_ms')}
                rows[label] = {**events, 'observations': len(observations), 'failures': failures, 'missing': missing}
                passed &= not failures and not missing and all(events.values())
            key = fixture + '/' + scenario
            summary[key] = rows
            for event in ('first_ms', 'final_ms'):
                a, c = rows['A'][event], rows['C'][event]
                if not a or not c:
                    gates.append({'case': key, 'event': event, 'passed': False, 'reason': 'missing observations'})
                    passed = False
                    continue
                target = True
                reason = 'textured/large source decode reported separately'
                if scenario == 'disk' or (scenario == 'ready' and fixture != '3200x2400.png'):
                    target = c['median'] <= 30 and c['p95'] <= 50
                    reason = 'median <=30 ms; p95 <=50 ms'
                elif scenario == 'memory':
                    target = c['median'] - a['median'] <= .2 and c['p95'] - a['p95'] <= .2
                    reason = 'median and p95 regression <=0.2 ms'
                elif scenario not in ('ready', 'disk'):
                    target = c['p95'] <= a['p95'] + max(5, a['p95'] * .1)
                    reason = 'p95 regression <=max(5 ms, 10%)'
                gates.append({'case': key, 'event': event, 'passed': target, 'reason': reason})
                passed &= target
    return {'latency_targets_met': bool(passed), 'qualifying_sample_count': samples == 100,
            'summary': summary, 'gates': gates,
            'overall_qualification': 'incomplete: installation, lifecycle, resource and consumer gates are separate'}


def report(data):
    lines = ['# Protected generation / reusable preview comparison', '',
             'Native service delivery, milliseconds (median / p95). A: frozen transaction baseline; '
             'B: protected one-shot with owner validation reuse; C: reusable sessions and scheduler.', '',
             '| Fixture / scenario / event | A | B | C | B−A ms (%) median / p95 | C−A ms (%) median / p95 |',
             '| --- | ---: | ---: | ---: | ---: | ---: |']
    for case, rows in data['summary'].items():
        for event in ('first_ms', 'final_ms'):
            values = [rows[label][event] for label in LABELS]
            if not all(values):
                lines.append(f'| {case} / {event} | incomplete | incomplete | incomplete | — | — |')
                continue
            a, b, c = values
            cells = [f'{value["median"]:.3f} / {value["p95"]:.3f}' for value in values]
            def change(value):
                return ' / '.join(f'{value[key]-a[key]:+.3f} ({(value[key]/a[key]-1)*100:+.1f}%)'
                                  if a[key] else 'undefined' for key in ('median', 'p95'))
            lines.append(f'| {case} / {event} | ' + ' | '.join(cells + [change(b), change(c)]) + ' |')
    failures = [gate for gate in data['gates'] if not gate['passed']]
    lines += ['', 'Latency targets met: **' + str(data['latency_targets_met']).lower() + '**.', '',
              'Overall qualification: **incomplete**. Lifecycle, installation, resource and installed-consumer '
              'evidence must also pass; this report alone cannot establish completion.', '',
              f'Failed latency gates: {len(failures)}. Failures and missing observations remain in summary.json.',
              'Source decoding of the textured large fixture is reported separately from lightweight ready targets. '
              'Every disk-hit fixture is subject to the disk target. No low-end hardware qualification is claimed.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('fixtures', type=Path)
    parser.add_argument('--uid', type=int, default=int(os.environ.get('SUDO_UID', '-1')))
    parser.add_argument('--samples', type=int, default=100)
    parser.add_argument('--scenarios', nargs='+', choices=SCENARIOS, default=SCENARIOS)
    args = parser.parse_args()
    if os.geteuid() != 0 or args.uid <= 0:
        parser.error('requires root and an ordinary invoking UID')
    if args.samples != 1 and (args.samples <= 0 or args.samples % 10):
        parser.error('--samples must be 1 (smoke) or a positive multiple of ten')
    package, fixtures = args.package.resolve(), args.fixtures.resolve()
    account = pwd.getpwuid(args.uid)
    output = Path(tempfile.mkdtemp(prefix='reuse-measurement-', dir=package))
    os.chown(output, args.uid, account.pw_gid)
    print(output, flush=True)
    runtime_root = Path(tempfile.mkdtemp(prefix='holonight-preview-measurement-', dir='/run'))
    runtime_root.chmod(0o755)
    provenance = {'fixtures': {name: digest(fixtures / name) for name in FIXTURES},
                  'binaries': {label: digest(package / label / 'reuse-harness/preview-benchmark') for label in LABELS},
                  'harness_inventory': digest(package / 'harness-inventory-final.json'),
                  'scenarios': args.scenarios, 'samples': args.samples, 'block_size': min(10, args.samples),
                  'warmups': 'one separate sample per fixture/scenario/variant',
                  'recycling': 'fresh harness process/service for every sample; variant blocks remain ten samples',
                  'runtime_root': str(runtime_root), 'uid': args.uid,
                  'p95_estimator': 'nearest rank', 'navigation_intermediate_selections': 4,
                  'qualification': 'latency only; no low-end hardware claim'}
    (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    shutil.copy2(__file__, output / 'runner.py')
    env = dict(os.environ, HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name,
               XDG_RUNTIME_DIR=f'/run/user/{args.uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{args.uid}/bus',
               QT_QPA_PLATFORM='offscreen')
    runtimes = {}
    records = {}
    observation_failures = []
    failure = None
    try:
        for label in LABELS:
            runtime = runtime_root / label
            source = package / label / ('runtime-final' if label in ('B', 'C') else 'runtime')
            if label == 'A':
                shutil.copytree(source, runtime)
            else:
                generations.run(SimpleNamespace(runtime=runtime, source=source,
                    helper=package / label / 'build/holonight-images/holonight-images-helper', command='install',
                    ownership_manifest=None, maintenance_migrate=False))
            runtimes[label] = runtime
        def run(label, fixture, scenario, count, tag):
            # Reset the transaction count for each recycling observation. Reusing
            # a service between samples moves the 32-start boundary into setup.
            if scenario == 'recycle' and count > 1:
                for sample in range(count):
                    run(label, fixture, scenario, 1, f'{tag}-sample-{sample:02}')
                return
            target = output / (tag + '.json')
            command = [str(package / label / 'reuse-harness/preview-benchmark'), str(runtimes[label]),
                       str(fixtures / fixture), scenario, str(count), str(target)]
            with target.with_suffix('.log').open('x') as log:
                process = subprocess.run(command, env=env, user=args.uid, group=account.pw_gid,
                    extra_groups=os.getgrouplist(account.pw_name, account.pw_gid), stdout=log, stderr=subprocess.STDOUT,
                    timeout=max(60, count * 40))
            data = json.loads(target.read_text()) if target.exists() else {}
            observations = data.get('samples', [])
            if not tag.startswith('warmup'):
                records.setdefault((label, fixture, scenario), []).extend(observations)
            if process.returncode or data.get('cleanup_failure') or len(observations) != count or any(
                    not valid_observation(row) for row in observations):
                message = f'{tag}: failed observations or cleanup; exit {process.returncode}'
                observation_failures.append(message)
                print(message, flush=True)
        for fixture in FIXTURES:
            for scenario in args.scenarios:
                for label in LABELS:
                    run(label, fixture, scenario, 1, f'warmup-{label}-{fixture}-{scenario}')
                size = min(10, args.samples)
                for block in range(args.samples // size):
                    order = LABELS[block % 3:] + LABELS[:block % 3]
                    for label in order:
                        run(label, fixture, scenario, size, f'block-{block:02}-{label}-{fixture}-{scenario}')
                    print(f'{fixture} {scenario}: {(block + 1) * size}/{args.samples} each variant', flush=True)
        for name in FIXTURES:
            if digest(fixtures / name) != provenance['fixtures'][name]:
                raise RuntimeError('fixture changed during frozen measurement')
        # Each harness has already drained its workers. Verify binary evidence
        # stayed frozen; never remove fixtures after any failed observation.
        for label in LABELS:
            if digest(package / label / 'reuse-harness/preview-benchmark') != provenance['binaries'][label]:
                raise RuntimeError('binary changed during frozen measurement')
        if observation_failures:
            raise RuntimeError('; '.join(observation_failures))
        for label in ('B', 'C'):
            generations.run(SimpleNamespace(runtime=runtimes[label], helper=package / label /
                'build/holonight-images/holonight-images-helper', command='remove', ownership_manifest=None,
                maintenance_migrate=False))
        shutil.rmtree(runtime_root)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        failure = str(error)
        print(failure, flush=True)
    data = assess(records, args.scenarios, args.samples)
    data['failure'] = failure
    data['preserved_runtime_root'] = str(runtime_root) if runtime_root.exists() else None
    data['latency_targets_met'] &= failure is None
    (output / 'summary.json').write_text(json.dumps(data, indent=2) + '\n')
    (output / 'comparison.md').write_text(report(data))
    print('Latency targets met:', data['latency_targets_met'], flush=True)
    return 1 if failure else 0


if __name__ == '__main__':
    raise SystemExit(main())
