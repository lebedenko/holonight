#!/usr/bin/env python3
"""Bounded v3 startup tracing validation; no pilot, retries or qualification."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pwd
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ('160x80.png', '3200x2400.png', 'oriented.jpg')
REVIEW = ROOT / 'build/preview-startup-tracing-v3-release-review'
PROVENANCE = ROOT / 'build/preview-transaction-20261111-144758/measurement-r_z8c7dw/provenance.json'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


analysis = module('startup_analysis', 'analyze-preview-startup.py')
measurement = module('smoke_measurement', 'measure-preview-reuse.py')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(path):
    return {str(p.relative_to(path)): digest(p) for p in sorted(path.rglob('*')) if p.is_file()}


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def verify_hashes(base, expected):
    failures = []
    for name, value in expected.items():
        path = base / name
        if not path.is_file() or digest(path) != value:
            failures.append(str(path))
    if failures:
        raise ValueError('changed or missing inputs: ' + ', '.join(failures))


def preflight(package, fixtures):
    verify_hashes(package, json.loads((package / 'evidence-hashes.json').read_text()))
    verify_hashes(ROOT, json.loads((package / 'python-input-hashes.json').read_text()))
    verify_hashes(REVIEW, json.loads((REVIEW / 'artifact-hashes.json').read_text()))
    manifest = json.loads((REVIEW / 'manifest.json').read_text())
    if manifest['before'] != manifest['after']:
        raise ValueError('reviewed sources changed')
    verify_hashes(REVIEW, {n: manifest[k] for n, k in (
        ('trace.h', 'header_sha256'), ('prepare.py', 'tool_sha256'),
        ('prepare-preview-standby-diagnostic.py', 'dependency_tool_sha256'))})
    for label in 'ABCD':
        if inventory(REVIEW / label) != manifest['outputs'][label]:
            raise ValueError('reviewed output mismatch: ' + label)
        for group, expected in manifest['after'][label].items():
            if inventory(Path(manifest['input']) / 'diagnostic' / label / group) != expected:
                raise ValueError('historical source mismatch: ' + label + '/' + group)
        for group in ('source', 'harness-source'):
            if inventory(package / label / group) != inventory(REVIEW / label / group):
                raise ValueError('native source copy mismatch: ' + label + '/' + group)
    artifacts = json.loads((package / 'artifact-evidence.json').read_text())
    for label in 'ABCD':
        verify_hashes(package / label, artifacts[label]['hashes'])
        for group in ('runtime', 'prefix'):
            expected = {n.removeprefix(group + '/'): h for n, h in artifacts[label]['hashes'].items() if n.startswith(group + '/')}
            if inventory(package / label / group) != expected:
                raise ValueError('native payload inventory mismatch: ' + label + '/' + group)
    provenance = json.loads(PROVENANCE.read_text())['fixtures']
    expected = {name: provenance[str(fixtures / name)] for name in FIXTURES}
    verify_hashes(fixtures, expected)
    return {'fixtures': expected, 'artifacts': artifacts,
            'control_hashes': {str(p): digest(p) for p in (PROVENANCE, REVIEW / 'manifest.json', REVIEW / 'artifact-hashes.json', package / 'evidence-hashes.json', ROOT / 'scripts/manage-images-generations.py', ROOT / 'scripts/measure-preview-reuse.py')},
            'reused_python_results': '21 passed; all recorded Python inputs unchanged'}


def trace_validation(text, samples, source, variant):
    events, spans, issues = analysis.parse_trace(text, source)
    rows, errors, unassigned = analysis.account(events, spans, samples, source, variant)
    issues.extend(errors)
    if not events or any(e.get('version') != 3 for e in events):
        issues.append({'kind': 'requires_v3'})
    if len(rows) != 3 or any(r['status'] != 'associated' or r['unknown'] for r in rows):
        issues.append({'kind': 'three_associated_observations_required'})
    # The shared accounting API computes these historical metrics internally.
    # Omit them from smoke evidence: this run makes no performance/overlap claim.
    for row in rows:
        for key in ('standby_overlap_ms', 'covered_union_ms', 'observable_window_ms', 'phases'):
            row.pop(key, None)
    lifetimes = []
    constructions = [s for s in spans if s['phase'] == 'service_construction']
    keys = {(s['begin']['pid'], s['begin'].get('service')) for s in constructions}
    if len(constructions) != 4 or len(keys) != 4:
        issues.append({'kind': 'four_service_lifetimes_required'})
    if sorted(s['begin'].get('observation', -1) for s in constructions) != [0, 1, 2, 3]:
        issues.append({'kind': 'setup_and_three_demands_required'})
    for construction in constructions:
        b = construction['begin']
        owned = [s for s in spans if (s['begin']['pid'], s['begin'].get('service')) == (b['pid'], b.get('service'))]
        destruction = [s for s in owned if s['phase'] == 'service_destruction']
        shutdown = [s for s in owned if s['phase'] == 'service_shutdown']
        # Destruction waits for worker cleanup without calling shutdown(). Its
        # paired end is completion evidence; validate shutdown() only if invoked.
        valid = (len(destruction) == 1 and
                 construction['stop'] <= destruction[0]['start'] and
                 all(s['begin'].get('role') == s['end'].get('role') == 'shutdown' and
                     construction['stop'] <= s['start'] <= s['stop'] <= destruction[0]['stop']
                     for s in shutdown + destruction))
        lifetimes.append({'pid': b['pid'], 'service': b.get('service'), 'observation': b.get('observation'),
                          'setup': b.get('observation') == 0, 'construction': construction,
                          'destruction': destruction, 'shutdown': shutdown,
                          'completion': destruction[0]['end'] if valid else None, 'valid': valid})
        if not valid:
            issues.append({'kind': 'incomplete_service_shutdown', 'service': b.get('service')})
    if any((e['pid'], e.get('service')) not in keys for e in events):
        issues.append({'kind': 'foreign_service_lifetime'})
    if variant in 'CD':
        for observation in (1, 2, 3):
            selected = [e for e in events if e.get('observation') == observation and e['phase'] == 'selected_worker']
            jobs = [s for s in spans if s['begin'].get('observation') == observation and s['phase'] == 'pool_job']
            if len(selected) != 1 or len(jobs) != 1 or not selected[0].get('preparation'):
                issues.append({'kind': 'selected_preparation_required', 'observation': observation})
    return {'events': events, 'accounting': rows, 'unassigned': unassigned,
            'lifecycles': lifetimes, 'issues': issues}


def execute(command, target, env, credentials, timeout=120):
    """Preserve separate streams; timeout always supervises the entire process group."""
    timed_out = False
    with target.with_suffix('.stdout').open('x') as stdout, target.with_suffix('.stderr').open('x') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env,
                                   start_new_session=True, **credentials)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            # A parent may have exited while its descendants still hold the group.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            code = process.wait()
    return {'exit': code, 'timeout': timed_out, 'cleanup_verified': not timed_out}


def validate_invocation(target, variant, process):
    failure = None
    try:
        data = json.loads(target.read_text())
    except (OSError, ValueError) as error:
        data = {}
        failure = 'missing or invalid harness JSON: ' + str(error)
    samples = data.get('samples', [])
    trace = trace_validation(target.with_suffix('.stderr').read_text() + '\n' +
                             target.with_suffix('.stdout').read_text(), samples, str(target.with_suffix('.log')), variant)
    write(target.with_suffix('.accounting.json'), trace)
    if (process['exit'] or process['timeout'] or data.get('cleanup_failure') or
            data.get('incomplete') or len(samples) != 3 or
            any(not measurement.valid_observation(s) for s in samples) or trace['issues']):
        failure = failure or 'exit, observation, trace or lifecycle validation failed'
    if failure:
        raise RuntimeError(f'{target.name}: {failure}')


def scope_snapshot(uid, env, credentials):
    command = ['systemctl', '--user', 'list-units', '--all', '--plain', '--no-legend',
               '--no-pager', 'holonight-images-*.scope']
    result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15, **credentials)
    cgroup = Path(f'/sys/fs/cgroup/user.slice/user-{uid}.slice/user@{uid}.service')
    paths = sorted(str(p) for p in cgroup.glob('**/holonight-images-*.scope'))
    return {'argv': command, 'exit': result.returncode, 'stdout': result.stdout,
            'stderr': result.stderr, 'cgroups': paths,
            'isolated': result.returncode == 0 and not result.stdout.strip() and not paths and cgroup.is_dir()}


def observation_directory(output, uid, gid):
    target = output / 'observations'
    target.mkdir()
    os.chown(target, uid, gid)
    return target


def run_commands(commands, result, uid, env, credentials):
    for command in commands:
        result['first_failing_command'] = command
        target = Path(command[-1])
        snapshot = scope_snapshot(uid, env, credentials)
        write(target.with_suffix('.scopes-before.json'), snapshot)
        if not snapshot['isolated']:
            raise RuntimeError('helper activity prevents isolated invocation')
        process = execute(command, target, env, credentials)
        result['invocations'].append(dict(command=command, **process))
        snapshot = scope_snapshot(uid, env, credentials)
        write(target.with_suffix('.scopes-after.json'), snapshot)
        validate_invocation(target, target.name[0], process)
        if not snapshot['isolated']:
            raise RuntimeError('residual helper scopes; cleanup unverified')


def run(args):
    package, fixtures, output = (p.resolve() for p in (args.package, args.fixtures, args.output))
    if os.geteuid() != 0 or args.uid <= 0:
        raise ValueError('root wrapper and ordinary --uid required')
    account = pwd.getpwuid(args.uid)
    credentials = dict(user=args.uid, group=account.pw_gid,
                       extra_groups=os.getgrouplist(account.pw_name, account.pw_gid))
    env = dict(os.environ, HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name,
               XDG_RUNTIME_DIR=f'/run/user/{args.uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{args.uid}/bus',
               QT_QPA_PLATFORM='offscreen')
    output.mkdir()  # Exclusive even before preregistration; never adopt earlier evidence.
    output.chmod(0o755)
    result = {'status': 'runtime tracing smoke validation blocked', 'invocations': [], 'qualified': False}
    runtime_root = None
    runtime_before = None
    before = None
    try:
        before = preflight(package, fixtures)
        write(output / 'input-identities.json', before)
        targets = observation_directory(output, args.uid, account.pw_gid)
        # Exercise the privileged wrapper's ordinary-user write path before any workload.
        probe = targets / 'ownership-probe.json'
        subprocess.run([sys.executable, '-c', 'import pathlib,sys; pathlib.Path(sys.argv[1]).write_text("ok\\n")', str(probe)],
                       env=env, check=True, **credentials)
        if probe.stat().st_uid != args.uid:
            raise ValueError('ordinary-user output ownership failed')
        runtime_root = Path('/run') / ('holonight-startup-smoke-' + output.name)
        commands = [[str(package / label / 'reuse-harness/preview-benchmark'), str(runtime_root / label),
                     str(fixtures / fixture), 'startup', '3', str(targets / f'{label}-{fixture}.json')]
                    for label in 'ABCD' for fixture in FIXTURES]
        write(output / 'preregistration.json', {
            'argv': sys.argv, 'cwd': str(Path.cwd()), 'commands': commands,
            'environment': {k: env[k] for k in ('HOME', 'USER', 'LOGNAME', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS', 'QT_QPA_PLATFORM', 'PATH')},
            'inherited_environment': {k: v for k, v in env.items() if k.startswith(('QT_', 'LD_', 'CMAKE', 'PKG_CONFIG'))},
            'credentials': credentials, 'inputs': before, 'runtime_root': str(runtime_root),
            'staging_commands': [[sys.executable, str(ROOT / 'scripts/manage-images-generations.py'), 'install', '--runtime', str(runtime_root / label), '--source', str(package / label / 'runtime'), '--helper', str(package / label / 'build/holonight-images/holonight-images-helper')] for label in 'BCD'],
            'legacy_staging': {'copytree': [str(package / 'A/runtime'), str(runtime_root / 'A')]},
            'bounds': {'invocations': 12, 'observations': 36, 'setup_services': 12, 'timeout_seconds': 120, 'term_grace_seconds': 5, 'retries': 0},
            'acceptance': 'All observations valid; v3 parser, identity and accounting issues zero; four balanced service lifetimes per invocation, with destruction end as cleanup completion and optional shutdown spans checked for pairing, identity, role and ordering; no helper scopes; unchanged retained inputs and runtime payloads.',
            'limits': 'Startup/shutdown trace continuity only; no cancellation, performance comparison, overlap target or qualification.'})
        shutil.copy2(__file__, output / 'runner.py')
        snapshot = scope_snapshot(args.uid, env, credentials)
        write(output / 'scopes-before.json', snapshot)
        if not snapshot['isolated']:
            raise RuntimeError('existing helper activity or unavailable scope supervision')
        with (output / 'execution-started.json').open('x') as marker:
            json.dump({'runtime_root': str(runtime_root)}, marker)
        runtime_root.mkdir(mode=0o755)
        with (output / 'staging.log').open('x') as log:
            for label in 'ABCD':
                base = package / label
                if label == 'A':
                    shutil.copytree(base / 'runtime', runtime_root / label)
                else:
                    subprocess.run([sys.executable, str(ROOT / 'scripts/manage-images-generations.py'), 'install',
                        '--runtime', str(runtime_root / label), '--source', str(base / 'runtime'),
                        '--helper', str(base / 'build/holonight-images/holonight-images-helper')],
                        stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
        runtime_before = inventory(runtime_root)
        write(output / 'runtime-before.json', runtime_before)
        run_commands(commands, result, args.uid, env, credentials)
        result.pop('first_failing_command', None)
        result['status'] = 'passed'
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        try:
            after = preflight(package, fixtures)
            result['retained_integrity'] = before is not None and before == after
        except (OSError, ValueError, KeyError) as error:
            result['retained_integrity'] = False
            result['integrity_failure'] = str(error)
        if runtime_root and runtime_root.exists():
            runtime_after = inventory(runtime_root)
            write(output / 'runtime-after.json', runtime_after)
            result['runtime_integrity'] = runtime_before is not None and runtime_before == runtime_after
        else:
            result['runtime_integrity'] = False
        try:
            snapshot = scope_snapshot(args.uid, env, credentials)
            write(output / 'scopes-final.json', snapshot)
            result['cleanup_verified'] = snapshot['isolated'] and not any(p['timeout'] for p in result['invocations'])
        except (OSError, subprocess.SubprocessError) as error:
            result['cleanup_verified'] = False
            result['scope_failure'] = str(error)
        if not all(result.get(k) for k in ('retained_integrity', 'runtime_integrity', 'cleanup_verified')):
            result['status'] = 'runtime tracing smoke validation blocked'
        write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('# Runtime tracing smoke\n\n' + result['status'] + '\n\n' +
            result.get('failure', '') + '\n\nSee assessment.json, preregistration.json and observations/. '
            'No qualification or performance claim; cancellation and overhead remain unverified.\n')
    return 0 if result['status'] == 'passed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('package', 'fixtures', 'output'):
        parser.add_argument(name, type=Path)
    parser.add_argument('--uid', type=int, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args))


if __name__ == '__main__':
    main()
