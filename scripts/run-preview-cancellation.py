#!/usr/bin/env python3
"""Execute exactly the preregistered C/D cancellation matrix, stopping on first failure."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


smoke = load('cancellation_smoke', 'run-preview-startup-smoke.py')
validator = load('cancellation_validator', 'validate-preview-cancellation.py')
ROOT = Path(__file__).resolve().parents[1]


def integrity(package):
    preparation = json.loads((package / 'preparation.json').read_text())
    retained = smoke.preflight(Path(preparation['input']), Path(preparation['fixtures']))
    if retained != preparation['before'] or retained != preparation['after']:
        raise ValueError('retained inputs changed')
    expected = json.loads((package / 'artifacts.json').read_text())
    for label, groups in expected.items():
        for group, hashes in groups.items():
            if group == 'build':
                smoke.verify_hashes(package / label / group, hashes)
            elif smoke.inventory(package / label / group) != hashes:
                raise ValueError('changed diagnostic artifact: ' + label + '/' + group)
    smoke.verify_hashes(package, json.loads((package / 'tool-identities.json').read_text()))
    return {'retained': retained, 'artifacts': expected}


def invocation(command, scenario, env, credentials, uid):
    target = Path(command[-1])
    before = smoke.scope_snapshot(uid, env, credentials)
    smoke.write(target.with_suffix('.scopes-before.json'), before)
    if not before['isolated']:
        raise RuntimeError('helper activity blocks execution')
    process = smoke.execute(command, target, env, credentials, timeout=120)
    after = smoke.scope_snapshot(uid, env, credentials)
    smoke.write(target.with_suffix('.scopes-after.json'), after)
    checks = validator.validate_files(target, process, scenario)
    if not after['isolated']:
        checks['issues'].append({'kind': 'residual_scopes'})
    smoke.write(target.with_suffix('.parsed-traces.json'), {k: checks.get(k, []) for k in ('events', 'spans')})
    smoke.write(target.with_suffix('.ledger-checks.json'), {k: v for k, v in checks.items() if k not in ('events', 'spans')})
    return {'command': command, **process, 'issues': checks['issues'], 'scopes_isolated': after['isolated']}


def run_matrix(commands, scenarios, result, env, credentials, uid):
    for command, scenario in zip(commands, scenarios, strict=True):
        result['first_failing_command'] = command
        row = invocation(command, scenario, env, credentials, uid)
        result['invocations'].append(row)
        if row['issues'] or row['exit'] or row['timeout'] or not row['scopes_isolated']:
            raise RuntimeError('invocation failed; no subsequent invocation permitted')
    result.pop('first_failing_command', None)


def run(args):
    package = args.package.resolve()
    if os.geteuid() != 0 or args.uid <= 0:
        raise ValueError('root supervisor and ordinary uid required')
    # A prior marker is rejected before creating output or staging anything.
    if (package / 'execution-started.json').exists():
        raise FileExistsError('execution marker already exists')
    output = package / 'execution'
    output.mkdir(mode=0o755)
    user = pwd.getpwuid(args.uid)
    credentials = dict(user=args.uid, group=user.pw_gid, extra_groups=os.getgrouplist(user.pw_name, user.pw_gid))
    env = dict(os.environ, HOME=user.pw_dir, USER=user.pw_name, LOGNAME=user.pw_name,
               XDG_RUNTIME_DIR=f'/run/user/{args.uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{args.uid}/bus', QT_QPA_PLATFORM='offscreen')
    result = {'status': 'cancellation tracing validation blocked', 'invocations': [], 'qualified': False}
    runtime = Path('/run') / ('holonight-cancellation-' + package.name)
    initial = runtime_before = None
    try:
        initial = integrity(package)
        smoke.write(output / 'input-identities.json', initial)
        targets = smoke.observation_directory(output, args.uid, user.pw_gid)
        probe = targets / 'ownership-probe.json'
        subprocess.run([sys.executable, '-c', 'import pathlib,sys; pathlib.Path(sys.argv[1]).write_text("ok\\n")', str(probe)],
                       env=env, check=True, **credentials)
        if probe.stat().st_uid != args.uid or probe.stat().st_gid != user.pw_gid:
            raise ValueError('ordinary-user output ownership failed')
        smoke.write(output / 'ownership.json', {'uid': probe.stat().st_uid, 'gid': probe.stat().st_gid, 'valid': True})
        fixtures = Path(json.loads((package / 'preparation.json').read_text())['fixtures'])
        commands, scenarios = [], []
        for label in 'CD':
            for scenario in validator.SCENARIOS:
                for repeat in range(1, 4):
                    target = targets / f'{label}-{scenario}-{repeat}.json'
                    commands.append([str(package / label / 'harness-build/preview-cancellation'), str(runtime / label),
                                     str(fixtures / '3200x2400.png'), str(fixtures / 'oriented.jpg'), scenario, str(target), str(target)])
                    scenarios.append(scenario)
        staging = [[sys.executable, str(ROOT / 'scripts/manage-images-generations.py'), 'install', '--runtime', str(runtime / label),
                    '--source', str(package / label / 'runtime'), '--helper', str(package / label / 'build/holonight-images/holonight-images-helper')] for label in 'CD']
        smoke.write(output / 'preregistration.json', {
            'argv': sys.argv, 'commands': commands, 'staging_commands': staging, 'inputs': initial,
            'environment': {k: env[k] for k in ('HOME', 'USER', 'LOGNAME', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS', 'QT_QPA_PLATFORM', 'PATH')},
            'inherited_environment': {k: v for k, v in env.items() if k.startswith(('QT_', 'LD_', 'CMAKE', 'PKG_CONFIG'))},
            'credentials': credentials, 'runtime': str(runtime),
            'bounds': {'invocations': 24, 'service_lifetimes': 24, 'cancelled_or_superseded_requests': 30, 'successful_replacements': 18,
                       'warmups': 0, 'retries': 0, 'timeout_seconds': 120, 'term_grace_seconds': 5, 'barrier_timeout_seconds': 1},
            'scenario_rules': (ROOT / 'tooling/preview-cancellation/README.md').read_text(),
            'acceptance': 'All 24 invocations exit zero with valid harness JSON, acknowledged barriers, zero v3 parsing/pairing/identity issues, explicit ledger joins, no stale accepted pixels/final metadata, verified cleanup, correct ordered replacement delivery, one balanced service lifetime, no residual scopes, unchanged inputs and runtime payload.',
            'limits': 'Only these forced C/D interleavings. No performance, overhead, A/B, arbitrary race coverage or qualification claim.'})
        snapshot = smoke.scope_snapshot(args.uid, env, credentials)
        smoke.write(output / 'scopes-before.json', snapshot)
        if not snapshot['isolated']:
            raise RuntimeError('existing helper activity blocks matrix')
        with (package / 'execution-started.json').open('x') as stream:
            json.dump({'runtime': str(runtime), 'commands': commands}, stream)
        runtime.mkdir(mode=0o755)
        with (output / 'staging.log').open('x') as log:
            for command in staging:
                result['first_failing_command'] = command
                subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
        runtime_before = smoke.inventory(runtime)
        smoke.write(output / 'runtime-before.json', runtime_before)
        run_matrix(commands, scenarios, result, env, credentials, args.uid)
        if len(result['invocations']) != 24:
            raise RuntimeError('fixed workload incomplete')
        result['status'] = 'passed'
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        try:
            result['retained_and_artifact_integrity'] = initial is not None and initial == integrity(package)
        except (OSError, ValueError, KeyError) as error:
            result['retained_and_artifact_integrity'] = False
            result['integrity_failure'] = str(error)
        if runtime.exists():
            runtime_after = smoke.inventory(runtime)
            smoke.write(output / 'runtime-after.json', runtime_after)
            result['runtime_integrity'] = runtime_before is not None and runtime_after == runtime_before
        else:
            result['runtime_integrity'] = False
        try:
            snapshot = smoke.scope_snapshot(args.uid, env, credentials)
            smoke.write(output / 'scopes-final.json', snapshot)
            result['cleanup_verified'] = snapshot['isolated'] and not any(r['timeout'] for r in result['invocations'])
        except (OSError, subprocess.SubprocessError) as error:
            result['cleanup_verified'] = False
            result['scope_failure'] = str(error)
        if not all(result.get(k) for k in ('retained_and_artifact_integrity', 'runtime_integrity', 'cleanup_verified')):
            result['status'] = 'cancellation tracing validation blocked'
        smoke.write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('# Cancellation tracing\n\n' + result['status'] + '\n\n' + result.get('failure', '') +
            '\n\nSee assessment.json for the first failing command and observations/ for partial evidence. No retries, repairs or subsequent invocations after failure. No performance or qualification claim.\n')
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('--uid', required=True, type=int)
    raise SystemExit(run(parser.parse_args()))
