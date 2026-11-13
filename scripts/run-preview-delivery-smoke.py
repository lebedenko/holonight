#!/usr/bin/env python3
"""Fixed 12-invocation v4 delivery smoke; no retries, rebuilds or qualification."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import pwd
import re
import shutil
import stat
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


smoke = module('delivery_smoke_startup', 'run-preview-startup-smoke.py')
analyzer = module('delivery_smoke_analysis', 'analyze-preview-delivery-tracing.py')
FIXTURES = smoke.FIXTURES
digest, inventory, write = smoke.digest, smoke.inventory, smoke.write
scope_snapshot = smoke.scope_snapshot
observation_directory = smoke.observation_directory
HISTORICAL = 'c7a48da92d29e8a4963d66478092ad93685bf65ff0c886f598e4eaba37981f44'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def preflight(package, reassessment, prepared, fixtures):
    consumed = {}
    def hashes(base, expected):
        smoke.verify_hashes(base, expected)
        consumed.update({str(base / n): h for n, h in expected.items()})
    for base in (package, reassessment):
        hashes(base, read(base / 'evidence-hashes.json'))
        consumed[str(base / 'evidence-hashes.json')] = digest(base / 'evidence-hashes.json')
    accepted = read(reassessment / 'acceptance.json')
    require(accepted['accepted'] and accepted['variants'] == dict.fromkeys('ABCD', True), 'reassessment not accepted')
    require(all(r['passed'] for r in read(reassessment / 'results.json').values()), 'failed reassessment result')
    retained = read(reassessment / 'retained-before.json')
    require(retained == read(reassessment / 'retained-after.json'), 'reassessment integrity mismatch')
    hashes(Path('/'), retained)
    manifest = read(prepared / 'manifest.json')
    require(manifest['status'] == 'prepared' and manifest['unchanged'] and not manifest['issues'] and manifest['before'] == manifest['after'], 'prepared manifest invalid')
    expected = dict(manifest['after'])
    require(expected.pop(str(ROOT / 'scripts/manage-images-generations.py')) == HISTORICAL, 'historical installer exception mismatch')
    expected[str(package / 'historical-manage-images-generations.py')] = HISTORICAL
    hashes(Path('/'), expected)
    hashes(prepared, {'trace.h': manifest['header_sha256']})
    for v in 'ABCD':
        require(inventory(prepared / v) == manifest['outputs'][v], 'prepared inventory mismatch: ' + v)
        hashes(prepared / v, manifest['outputs'][v])
        maps = read(prepared / v / 'probe-to-source.json')
        for ref in maps['probes']:
            p = Path(ref['file'])
            require(p.is_relative_to(prepared / v) and digest(p) == ref['sha256'] and p.read_text().splitlines()[ref['line'] - 1] == ref['text'], 'probe map mismatch')
        hashes(package / v, read(package / v / 'artifacts.json'))
        for kind, relative in (('helper', 'build/holonight-images/holonight-images-helper'), ('harness', 'reuse-harness/preview-benchmark')):
            hashes(package / v, {relative: read(reassessment / f'{v}-{kind}-metadata.json')['sha256']})
        resolutions = read(package / v / 'package-resolution.json')
        for relative, entries in resolutions.items():
            actual = [s for s in (package / v / relative).read_text().splitlines() if s.startswith('Holonight') and '_DIR:' in s]
            require(actual == entries and all(s.split('=', 1)[1].startswith(str(package / v / 'prefix') + '/') for s in actual), 'package resolution mismatch')
        bundles = []
        for group in ('runtime', 'prefix/libexec/holonight-images/runtime'):
            base = package / v / group
            m = read(base / 'manifest.json')
            files = m['files']
            require(set(inventory(base)) == {r['path'] for r in files} | {'manifest.json'} and len(files) == len({r['path'] for r in files}), 'runtime inventory mismatch')
            for r in files:
                p = base / r['path']
                require(digest(p) == r['sha256'] and p.stat().st_size == r['size'] and stat.S_IMODE(p.stat().st_mode) == r['mode'], 'runtime payload mismatch')
            require(digest(base / 'usr/libexec/holonight-images-helper') == digest(package / v / 'build/holonight-images/holonight-images-helper'), 'runtime helper mismatch')
            bundles.append(m)
        require(bundles[0] == bundles[1], 'runtime manifests differ')
    provenance = read(smoke.PROVENANCE)['fixtures']
    hashes(fixtures, {n: provenance[str(fixtures / n)] for n in FIXTURES})
    for p in [smoke.PROVENANCE, prepared / 'manifest.json', Path(__file__), * (ROOT / 'scripts').glob('*.py')]:
        consumed[str(p)] = digest(p)
    return consumed


def protected_inventory(root):
    result = {}
    for p in [root, *sorted(root.rglob('*'))]:
        info = p.lstat()
        require(info.st_uid == 0 and (p.is_symlink() or not info.st_mode & 0o022), 'unprotected runtime: ' + str(p))
        result[str(p.relative_to(root))] = dict(mode=stat.S_IMODE(info.st_mode), uid=info.st_uid, gid=info.st_gid,
            link=os.readlink(p) if p.is_symlink() else None, sha256=digest(p) if p.is_file() else None)
    return result


def trace_validation(text, samples, source, variant, output=None):
    report = analyzer.analyze(text, source, variant, samples)
    try:
        validate_trace_report(report, variant)
    except ValueError as error:
        report['runtime_gate_failure'] = str(error)
        raise
    finally:
        if output is not None:
            write(output, report)
    return report


def validate_trace_report(report, variant):
    require(not report['issues'] and report['events'], 'v3/v4 trace issues or missing v4 records')
    events, spans = report['events'], report['spans']
    endpoints = [e for e in events if e['operation'].startswith('endpoint_')]
    require(len(endpoints) == 6, 'six unique endpoints required')
    for observation in (1, 2, 3):
        selected = [e for e in endpoints if e['observation'] == observation]
        require(sorted(e['operation'] for e in selected) == ['endpoint_metadata', 'endpoint_pixels'], 'missing or duplicate endpoints')
        require(len({tuple(e[k] for k in ('pid', *analyzer.IDENTITIES) if k != 'publication') for e in selected}) == 1, 'endpoint identities conflict')
        for e in selected:
            require(all(e[k] is not None for k in ('service', 'observation', 'job', 'worker', 'generation', 'session', 'transaction', 'publication')), 'explicit endpoint identity required')
            handoff = [h for h in report['handoffs'] if h['pid'] == e['pid'] and h['publication'] == e['publication']]
            require(len(handoff) == 1 and not handoff[0].get('unavailable') and not handoff[0].get('decision_unavailable'), 'incomplete handoff')
            for op in ('enqueue_call', 'callback_execution', 'apply_result', 'changed_emission'):
                found = [s for s in spans if s['operation'] == op and analyzer.identity(s['begin']) == analyzer.identity(e)]
                require(len(found) == 1 and found[0]['begin']['line'] < found[0]['end']['line'], 'missing or misordered required handoff span')
        endpoint = selected[0]
        owned = [s for s in spans if all(s['begin'][k] == endpoint[k] for k in ('pid', 'service', 'observation', 'job', 'worker', 'preparation', 'generation', 'session', 'transaction'))]
        required = {'reusable_completion_ack': 'acknowledged'} if variant in 'CD' else {'oneshot_ack': 'sent', 'helper_exit': 'validated_exit', 'effective_cleanup': 'verified'}
        for op, outcome in required.items():
            found = [s for s in owned if s['operation'] == op]
            require(len(found) == 1 and found[0]['end']['outcome'] == outcome and found[0]['begin']['line'] < found[0]['end']['line'] and found[0]['stop'] <= min(e['ns'] for e in selected), 'missing or invalid transaction evidence: ' + op)


def validate_invocation(target, variant, process, uid, fixture):
    data = read(target)
    samples = data.get('samples', [])
    require(process['exit'] == 0 and not process['timeout'] and process['cleanup_verified'], 'process failed or timeout; cleanup unverified')
    require(target.stat().st_uid == uid, 'output ownership mismatch')
    require(data.get('scenario') == 'startup' and data.get('fixture') == str(fixture) and not data.get('cleanup_failure') and not data.get('setup_failure') and not data.get('incomplete') and len(samples) == 3, 'invalid harness completion')
    for sample in samples:
        deliveries = sample.get('deliveries', [])
        require(smoke.measurement.valid_observation(sample) and len(deliveries) == 2 and [d.get('event') for d in deliveries] == ['pixels', 'metadata'] and all(d.get('selection') == 4 for d in deliveries) and [d.get('latency_ms') for d in deliveries] == [sample['first_ms'], sample['final_ms']], 'invalid content or endpoint observations')
    trace_validation(target.with_suffix('.stderr').read_text(), samples, str(target.with_suffix('.stderr').resolve()), variant, target.with_suffix('.accounting.json'))
    work = list(target.parent.glob(target.name + '.work-*'))
    require(len(work) == 1 and (work[0] / 'cache').is_dir(), 'private cache missing')
    require(all(p.stat().st_uid == uid for p in [work[0], *work[0].rglob('*')]), 'private work ownership mismatch')
    copies = list(work[0].glob('*' + fixture.suffix))
    require(len(copies) == 32 and all(digest(p) == digest(fixture) for p in copies), 'private fixture provenance mismatch')


def schedule(package, runtime, fixtures, targets):
    return [[str(package / v / 'reuse-harness/preview-benchmark'), str(runtime / v),
             str(fixtures / fixture), 'startup', '3', str(targets / f'{v}-{fixture}.json')]
            for v in 'ABCD' for fixture in FIXTURES]


def staged_payloads(package, runtime, variants='ABCD'):
    for v in variants:
        base = runtime / v
        payload = base
        if v != 'A':
            marker = base / 'current'
            require(marker.is_file() and not marker.is_symlink(), 'invalid generation marker')
            name = marker.read_text().strip()
            require(re.fullmatch(r'[0-9a-f]{64}', name) is not None, 'invalid generation name')
            require(read(base / 'ownership.json') == [name], 'unexpected generation ownership')
            require({p.name for p in (base / 'generations').iterdir()} == {name}, 'unexpected retained generation')
            payload = base / 'generations' / name
        require(payload.is_dir() and not payload.is_symlink() and inventory(payload) == inventory(package / v / 'runtime'), 'staged payload mismatch: ' + v)



def run_commands(commands, result, uid, env, credentials):
    for command in commands:
        target = Path(command[-1])
        row = dict(command=command, status='failed')
        before = scope_snapshot(uid, env, credentials)
        write(target.with_suffix('.scopes-before.json'), before)
        require(before['isolated'], 'scope supervision unavailable or residual scopes')
        result['invocations'].append(row)
        process = smoke.execute(command, target, env, credentials)
        row.update(process)
        write(target.with_suffix('.status.json'), process)
        after = scope_snapshot(uid, env, credentials)
        write(target.with_suffix('.scopes-after.json'), after)
        validate_invocation(target, target.name[0], process, uid, Path(command[2]))
        require(after['isolated'], 'residual scopes; cleanup unverified')
        row['status'] = 'passed'


def run(args):
    package, fixtures, output = (p.resolve() for p in (args.package, args.fixtures, args.output))
    if os.geteuid() != 0 or args.uid <= 0:
        raise ValueError('root wrapper and ordinary --uid required')
    account = pwd.getpwuid(args.uid)
    credentials = dict(user=args.uid, group=account.pw_gid,
                       extra_groups=os.getgrouplist(account.pw_name, account.pw_gid))
    installer_env = {k: os.environ[k] for k in ('PATH', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ') if k in os.environ}
    installer_env.setdefault('PATH', os.defpath)
    env = dict(installer_env, HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name,
               XDG_RUNTIME_DIR=f'/run/user/{args.uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{args.uid}/bus',
               QT_QPA_PLATFORM='offscreen')
    require(output.is_relative_to(ROOT / 'build') and all(not output.is_relative_to(p.resolve()) and not p.resolve().is_relative_to(output) for p in (args.package, args.reassessment, args.prepared, args.fixtures)), 'output must be disjoint and beneath ignored build/')
    output.mkdir()  # Exclusive even before preregistration; never adopt earlier evidence.
    output.chmod(0o755)
    result = {'status': 'runtime tracing smoke validation blocked', 'invocations': [], 'qualified': False}
    runtime_root = Path('/run') / ('holonight-delivery-smoke-' + output.name)
    runtime_created = False
    commands = schedule(package, runtime_root, fixtures, output / 'observations')
    runtime_before = None
    before = None
    try:
        before = preflight(package, args.reassessment.resolve(), args.prepared.resolve(), fixtures)
        write(output / 'input-identities.json', before)
        targets = observation_directory(output, args.uid, account.pw_gid)
        cache = targets / 'qt-cache'
        cache.mkdir(mode=0o700)
        os.chown(cache, args.uid, account.pw_gid)
        env['XDG_CACHE_HOME'] = str(cache)
        # Exercise the privileged wrapper's ordinary-user write path before any workload.
        probe = targets / 'ownership-probe.json'
        subprocess.run([sys.executable, '-c', 'import pathlib,sys; pathlib.Path(sys.argv[1]).write_text("ok\\n")', str(probe)],
                       env=env, check=True, **credentials)
        if probe.stat().st_uid != args.uid:
            raise ValueError('ordinary-user output ownership failed')
        runtime_root = Path('/run') / ('holonight-delivery-smoke-' + output.name)
        commands = schedule(package, runtime_root, fixtures, targets)
        write(output / 'preregistration.json', {
            'argv': sys.argv, 'cwd': str(Path.cwd()), 'commands': commands,
            'environment': env, 'installer_environment': installer_env,
            'inherited_environment': {k: v for k, v in env.items() if k.startswith(('QT_', 'LD_', 'CMAKE', 'PKG_CONFIG'))},
            'credentials': credentials, 'installer_credentials': {'uid': os.geteuid(), 'gid': os.getegid(), 'groups': os.getgroups()}, 'inputs': before, 'runtime_root': str(runtime_root),
            'staging_commands': [[sys.executable, str(ROOT / 'scripts/manage-images-generations.py'), 'install', '--runtime', str(runtime_root / label), '--source', str(package / label / 'runtime'), '--helper', str(package / label / 'build/holonight-images/holonight-images-helper')] for label in 'BCD'],
            'legacy_staging': {'copytree': [str(package / 'A/runtime'), str(runtime_root / 'A')]},
            'bounds': {'invocations': 12, 'observations': 36, 'setup_services': 12, 'timeout_seconds': 120, 'term_grace_seconds': 5, 'retries': 0},
            'acceptance': 'All observations valid; v3/v4 parser, identity and accounting issues zero; four balanced service lifetimes per invocation, with destruction end as cleanup completion and optional shutdown spans checked for pairing, identity, role and ordering; no helper scopes; unchanged retained inputs and runtime payloads.',
            'transaction_acceptance': 'A/B: one-shot ack sent, helper validated exit, effective cleanup verified; C/D: reusable completion acknowledged; explicit endpoint identities and complete unique handoffs required; unrelated unavailable evidence retained.',
            'limits': 'Startup/shutdown trace continuity only; no cancellation, performance comparison, overlap target or qualification.'})
        shutil.copy2(__file__, output / 'runner.py')
        for name in ('manage-images-generations.py', 'install_state.py'):
            shutil.copy2(ROOT / 'scripts' / name, output / name)
        snapshot = scope_snapshot(args.uid, env, credentials)
        write(output / 'scopes-before.json', snapshot)
        if not snapshot['isolated']:
            raise RuntimeError('existing helper activity or unavailable scope supervision')
        with (output / 'execution-started.json').open('x') as marker:
            json.dump({'runtime_root': str(runtime_root)}, marker)
        runtime_root.mkdir(mode=0o755)
        runtime_created = True
        for label in 'ABCD':
            base = package / label
            if label == 'A':
                shutil.copytree(base / 'runtime', runtime_root / label)
            else:
                command = [sys.executable, str(ROOT / 'scripts/manage-images-generations.py'), 'install',
                    '--runtime', str(runtime_root / label), '--source', str(base / 'runtime'),
                    '--helper', str(base / 'build/holonight-images/holonight-images-helper')]
                process = smoke.execute(command, output / ('installer-' + label + '.json'), installer_env, {})
                result.setdefault('installer_verification_launches', []).append(dict(argv=command, **process))
                write(output / 'staging-progress.json', result)
                if process['exit'] or process['timeout']:
                    raise RuntimeError('installer failed: ' + label)
            staged_payloads(package, runtime_root, label)
            write(output / ('staged-' + label + '.json'), protected_inventory(runtime_root))

        staged_payloads(package, runtime_root)
        runtime_before = protected_inventory(runtime_root)
        write(output / 'runtime-before.json', runtime_before)
        run_commands(commands, result, args.uid, env, credentials)
        result.pop('first_failing_command', None)
        result['status'] = 'passed'
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        try:
            after = preflight(package, args.reassessment.resolve(), args.prepared.resolve(), fixtures)
            result['retained_integrity'] = before is not None and before == after
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            result['retained_integrity'] = False
            result['integrity_failure'] = str(error)
        if runtime_created:
            try:
                runtime_after = protected_inventory(runtime_root)
                write(output / 'runtime-after.json', runtime_after)
                staged_payloads(package, runtime_root)
                result['runtime_integrity'] = runtime_before is not None and runtime_before == runtime_after
            except (OSError, ValueError) as error:
                result['runtime_integrity'] = False
                result['runtime_failure'] = str(error)
        else:
            result['runtime_integrity'] = False
        try:
            snapshot = scope_snapshot(args.uid, env, credentials)
            write(output / 'scopes-final.json', snapshot)
            result['cleanup_verified'] = snapshot['isolated'] and not any(p.get('timeout', True) for p in result['invocations'] + result.get('installer_verification_launches', []))
        except (OSError, subprocess.SubprocessError) as error:
            result['cleanup_verified'] = False
            result['scope_failure'] = str(error)
        if not all(result.get(k) for k in ('retained_integrity', 'runtime_integrity', 'cleanup_verified')):
            result['status'] = 'failed'
        result['rows'] = [dict(argv=c, status=next((r['status'] for r in result['invocations'] if r['command'] == c), 'unexecuted')) for c in commands]
        result['passed_observations'] = sum(r['status'] == 'passed' for r in result['invocations']) * 3
        if len(result['invocations']) != 12 or result['passed_observations'] != 36:
            result['status'] = 'failed'
        write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('# Runtime tracing smoke\n\n' + result['status'] + '\n\n' +
            result.get('failure', '') + '\n\nSee assessment.json, preregistration.json and observations/. '
            'No qualification or performance claim; cancellation and overhead remain unverified.\n' + '\n'.join(r['status'] + ': ' + Path(r['argv'][-1]).name for r in result['rows']) + '\n')
        write(output / 'seal.json', inventory(output))
    return 0 if result['status'] == 'passed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('package', 'reassessment', 'prepared', 'fixtures', 'output'):
        parser.add_argument(name, type=Path)
    parser.add_argument('--uid', type=int, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args))


if __name__ == '__main__':
    main()
