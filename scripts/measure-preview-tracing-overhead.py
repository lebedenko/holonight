#!/usr/bin/env python3
"""One fixed descriptive matched v3 startup comparison; no qualification or retries."""
import argparse
import difflib
import importlib.util
import json
import math
import os
from pathlib import Path
import pwd
import re
import shutil
import statistics
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

smoke = module('overhead_smoke', ROOT / 'scripts/run-preview-startup-smoke.py')
digest, inventory, write = smoke.digest, smoke.inventory, smoke.write
FIXTURES = smoke.FIXTURES
NATIVE = ROOT / 'build/preview-startup-native-validation-3wim1co2'
BASE = ROOT / 'build/preview-corrected-qjln5jn4'
STANDBY = ROOT / 'build/preview-standby-drbq1ofy'
FIXTURE_ROOT = ROOT / 'build/preview-transaction-20261111-144758/fixtures'
RETAINED = [BASE, STANDBY, NATIVE, smoke.REVIEW,
            ROOT / 'build/preview-startup-runtime-smoke-20261112-v3-01',
            ROOT / 'build/preview-startup-runtime-smoke-20261112-v3-02',
            ROOT / 'build/preview-cancellation-tracing-wxuflfvn',
            ROOT / 'build/preview-cancellation-tracing-837893f4',
            ROOT / 'build/preview-cancellation-supervisor-20261112']


def schedule():
    rows = []
    for fixture in FIXTURES:
        for variant in 'ABCD':
            for mode in 'UT':
                rows.append(dict(fixture=fixture, variant=variant, mode=mode, warmup=True, block=None, count=1))
        for block in range(10):
            order = 'ABCD'[block % 4:] + 'ABCD'[:block % 4]
            for variant in order:
                for mode in ('UT' if block % 2 == 0 else 'TU'):
                    rows.append(dict(fixture=fixture, variant=variant, mode=mode, warmup=False, block=block, count=10))
    return [dict(row, index=index) for index, row in enumerate(rows)]


def comparison(untraced, traced):
    def dist(values):
        if not values or any(isinstance(v, bool) or not isinstance(v, (int, float)) or
                             not math.isfinite(v) or v < 0 for v in values):
            raise ValueError('missing or invalid latency')
        return dict(median=statistics.median(values), p95=sorted(values)[math.ceil(.95 * len(values)) - 1])
    u, t = dist(untraced), dist(traced)
    return {k: dict(U=u[k], T=t[k], delta_ms=t[k] - u[k],
                    delta_percent=100 * (t[k] - u[k]) / u[k] if u[k] else None) for k in u}


def statistics_report(rows):
    expected = schedule()
    if len(rows) != len(expected) or any(r['invocation'] != e for r, e in zip(rows, expected)):
        raise ValueError('missing, reordered or duplicate invocation')
    for r in rows:
        if len(r['samples']) != r['invocation']['count'] or any(not smoke.measurement.valid_observation(s) for s in r['samples']):
            raise ValueError('missing or invalid sample')
    result = []
    for fixture in FIXTURES:
        for variant in 'ABCD':
            for event in ('first_ms', 'final_ms'):
                selected = [r for r in rows if not r['invocation']['warmup'] and
                            r['invocation']['fixture'] == fixture and r['invocation']['variant'] == variant]
                def values(mode, block=None):
                    return [s[event] for r in selected if r['invocation']['mode'] == mode and
                            (block is None or r['invocation']['block'] == block) for s in r['samples']]
                if any(len(values(mode)) != 100 for mode in 'UT'):
                    raise ValueError('100 samples per mode required')
                result.append(dict(fixture=fixture, variant=variant, event=event,
                                   statistics=comparison(values('U'), values('T')),
                                   blocks=[dict(block=b, statistics=comparison(values('U', b), values('T', b))) for b in range(10)]))
    return result


def normalized(data):
    return re.sub(rb'#include "[^"\n]*/trace.h"', b'#include "PACKAGE/trace.h"', data)


def compare_trees(a, b, diff):
    aa, bb = inventory(a), inventory(b)
    differences = []
    for name in sorted(aa.keys() | bb.keys()):
        left = normalized((a / name).read_bytes()) if name in aa else b''
        right = normalized((b / name).read_bytes()) if name in bb else b''
        if left != right:
            differences.append(name)
            diff.extend(difflib.unified_diff(left.decode().splitlines(True), right.decode().splitlines(True),
                                           fromfile=str(a / name), tofile=str(b / name)))
    return differences


def retained_snapshot():
    # Includes blocked evidence, private fixture copies, sources and historical binaries.
    packages = {str(p): inventory(p) for p in RETAINED}
    for p in RETAINED[4:]:
        execution = p / 'execution' if 'cancellation' in p.name else p
        prereg = json.loads((execution / 'preregistration.json').read_text())
        runtime = Path(prereg.get('runtime_root', prereg.get('runtime', '')))
        if not runtime.is_absolute() or not runtime.is_dir():
            raise ValueError('retained protected runtime missing: ' + str(p))
        current = inventory(runtime)
        if current != json.loads((execution / 'runtime-after.json').read_text()):
            raise ValueError('retained staged payload changed: ' + str(runtime))
        packages[str(runtime)] = current
    return packages


def verify_retained():
    smoke.preflight(NATIVE, FIXTURE_ROOT)
    frozen = json.loads((BASE / 'freeze.json').read_text())
    for v in 'ABC':
        if inventory(BASE / v / 'source') != frozen['source_inventories'][v]:
            raise ValueError('frozen untraced source mismatch: ' + v)
    for p in RETAINED[4:]:
        assessment = json.loads((p / ('execution/assessment.json' if 'cancellation' in p.name else 'assessment.json')).read_text())
        if not assessment.get('cleanup_verified'):
            raise ValueError('retained cleanup unverified: ' + str(p))
    supervisor = RETAINED[-1]
    blocked = json.loads((supervisor / 'blocked-package-identities.json').read_text())
    for path, hashes in blocked.items():
        smoke.verify_hashes(ROOT / 'build' / path, hashes)
    summary = json.loads((supervisor / 'final-validation-summary.json').read_text())
    for row in summary['preserved_fixture_copies']:
        if digest(Path(row['path'])) != row['sha256'] or not row['matches_retained']:
            raise ValueError('preserved fixture changed')


def tool_hashes():
    names = ('measure-preview-tracing-overhead.py', 'run-preview-startup-smoke.py',
             'analyze-preview-startup.py', 'measure-preview-reuse.py',
             'manage-images-generations.py', 'prepare-preview-startup-tracing.py',
             'prepare-preview-standby-diagnostic.py')
    paths = [ROOT / 'scripts' / n for n in names] + [ROOT / 'tests/test_preview_tracing_overhead.py']
    return {str(p): digest(p) for p in paths}


def prepare(output):
    output.mkdir()  # exclusive; never adopt a prior preparation
    write(output / 'intent.json', dict(argv=sys.argv, cwd=str(ROOT), protocol=schedule(), qualification=False))
    verify_retained()
    before = retained_snapshot()
    write(output / 'retained-before.json', before)
    v3 = module('retained_v3', smoke.REVIEW / 'prepare.py')
    legacy = module('retained_phases', smoke.REVIEW / 'prepare-preview-standby-diagnostic.py')
    shutil.copyfile(smoke.REVIEW / 'trace.h', output / 'trace.h')
    checks = {}
    for v in 'ABCD':
        untraced = BASE / v if v != 'D' else STANDBY / 'pilot/D'
        replay = output / 'replay' / v
        shutil.copytree(untraced / 'source', replay / 'source')
        shutil.copytree(BASE / 'harness-source', replay / 'harness-source')
        legacy.instrument(replay / 'source', replay / 'harness-source', output / 'trace.h')
        v3.overlay(replay, output / 'trace.h')
        diff = []
        checks[v] = {g: compare_trees(replay / g, NATIVE / v / g, diff) for g in ('source', 'harness-source')}
        (replay / 'equivalence.diff').write_text(''.join(diff))
    write(output / 'equivalence.json', checks)
    if any(names for variant in checks.values() for names in variant.values()):
        raise ValueError('tracing-only equivalence not established; stop before builds')
    pairs = {}
    for v in 'ABCD':
        for mode in 'UT':
            base = output / (v + mode)
            src = (BASE / v if v != 'D' else STANDBY / 'pilot/D') if mode == 'U' else NATIVE / v
            shutil.copytree(src / 'source', base / 'source')
            shutil.copytree(BASE / 'harness-source' if mode == 'U' else src / 'harness-source', base / 'harness-source')
            if mode == 'T':
                for path in [* (base / 'source').rglob('*.cpp'), * (base / 'harness-source').glob('*.cpp')]:
                    path.write_bytes(re.sub(rb'#include "[^"\n]*/trace.h"',
                                           ('#include "' + str(output / 'trace.h') + '"').encode(), path.read_bytes()))
            harness = base / 'harness-source/reuse.cpp'
            text = harness.read_text()
            anchor = '  QTemporaryDir directory;'
            if text.count(anchor) != 1:
                raise ValueError('private directory anchor changed')
            harness.write_text(text.replace(anchor, '  QTemporaryDir directory(QString::fromLocal8Bit(argv[5]) + ".work-XXXXXX");\n  directory.setAutoRemove(false);'))
            pairs[v + mode] = {g: inventory(base / g) for g in ('source', 'harness-source')}
        diff = []
        for group in ('source', 'harness-source'):
            for name in inventory(output / (v + 'U') / group):
                a, b = output / (v + 'U') / group / name, output / (v + 'T') / group / name
                if a.read_bytes() != b.read_bytes():
                    diff.extend(difflib.unified_diff(a.read_text().splitlines(True), b.read_text().splitlines(True), fromfile=str(a), tofile=str(b)))
        (output / (v + '-tracing.diff')).write_text(''.join(diff))
    write(output / 'preparation.json', dict(tools=tool_hashes(), pairs=pairs, retained_unchanged=before == retained_snapshot(),
          equivalence=checks, harness_review='Identical setup, fixtures, checks, QElapsedTimer start and callback latency capture; tracing only. Both modes preserve private fixture/cache directories identically.'))


def verify_prepared(package):
    if (package / 'execution-started.json').exists():
        raise ValueError('execution already started; no repair or rebuild permitted')
    manifest = json.loads((package / 'preparation.json').read_text())
    smoke.verify_hashes(ROOT, manifest['tools'])
    if not manifest['retained_unchanged']:
        raise ValueError('retained input changed during preparation')
    for key, groups in manifest['pairs'].items():
        for group, expected in groups.items():
            if inventory(package / key / group) != expected:
                raise ValueError('prepared source changed: ' + key + '/' + group)
    return manifest


def build(package):
    verify_prepared(package)
    commands = []
    def run(command, target):
        commands.append(command)
        write(package / 'build-commands.json', commands)
        with target.open('x') as log:
            subprocess.run(command, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
    run(['sudo', '-A', sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_preview_tracing_overhead.py', '-v'], package / 'focused-tests.log')
    write(package / 'verification.json', dict(passed=True, tests='focused-tests.log', historical='Unchanged analyzer/startup/cancellation results reused after retained identity verification.'))
    environment = dict(host=list(os.uname()), relevant={k: v for k, v in os.environ.items() if
        k.startswith(('QT_', 'LD_', 'CMAKE', 'PKG_CONFIG')) or k in ('PATH', 'CXX', 'CC', 'CXXFLAGS', 'CFLAGS', 'LDFLAGS')}, jobs=4)
    for name, command in [('compiler', ['c++', '--version']), ('dependencies', ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp']), ('cmake', ['cmake', '--version']), ('ninja', ['ninja', '--version'])]:
        environment[name] = subprocess.check_output(command, text=True)
    write(package / 'environment.json', environment)
    saved = json.loads((NATIVE / 'commands.json').read_text())
    artifacts = {}
    for v in 'ABCD':
        for mode in 'UT':
            key = v + mode
            base = package / key
            selected = [r['argv'] for r in saved if any(str(NATIVE / v) + '/' in a for a in r['argv'])]
            for i, cmd in enumerate(selected):
                command = [a.replace(str(NATIVE / v), str(base)) for a in cmd]
                run(command, base / f'command-{i:02}.log')
            caches = {}
            for path in [* (base / 'build').glob('*/CMakeCache.txt'), base / 'reuse-harness/CMakeCache.txt']:
                entries = [s for s in path.read_text().splitlines() if ('_DIR:' in s or 'LIBRARY:' in s or 'CMAKE_PREFIX_PATH:' in s) and not s.startswith('//')]
                caches[str(path.relative_to(base))] = entries
                for entry in entries:
                    if entry.startswith('Holonight') and '_DIR:' in entry and not entry.split('=', 1)[1].startswith(str(base / 'prefix') + '/'):
                        raise ValueError('provider resolution outside installed prefix: ' + entry)
            write(base / 'package-resolution.json', caches)
            for label, exe in [('helper', base / 'build/holonight-images/holonight-images-helper'), ('harness', base / 'reuse-harness/preview-benchmark')]:
                for name, command in [('dependencies', ['ldd', str(exe)]), ('symbols', ['nm', '-C', str(exe)]), ('elf', ['readelf', '-h', '-d', '-Ws', str(exe)])]:
                    run(command, base / (label + '-' + name + '.log'))
                if 'not found' in (base / (label + '-dependencies.log')).read_text():
                    raise ValueError('unresolved linkage')
                traced = 'StandbyTrace::' in (base / (label + '-symbols.log')).read_text()
                if label == 'harness' and traced != (mode == 'T'):
                    raise ValueError('unexpected trace linkage mode')
            artifacts[key] = {g: inventory(base / g) for g in ('source', 'harness-source', 'prefix', 'runtime')}
            artifacts[key]['binaries'] = {n: digest(base / n) for n in ('reuse-harness/preview-benchmark', 'build/holonight-images/holonight-images-helper')}
            print(key, 'built and linkage checked', flush=True)
    write(package / 'artifacts.json', artifacts)
    verify_prepared(package)
    if json.loads((package / 'retained-before.json').read_text()) != retained_snapshot():
        raise ValueError('retained input changed during builds')
    # All source reviews, commands, dependencies, focused checks and artifacts sealed before execution.
    seal = inventory(package)
    write(package / 'seal.json', seal)


def check_seal(package):
    smoke.verify_hashes(package, json.loads((package / 'seal.json').read_text()))
    smoke.verify_hashes(ROOT, json.loads((package / 'preparation.json').read_text())['tools'])


def validate_trace(text, samples, source, variant):
    # Reuse the unchanged smoke lifecycle checks for an arbitrary fixed block size.
    events, spans, issues = smoke.analysis.parse_trace(text, source)
    rows, errors, unassigned = smoke.analysis.account(events, spans, samples, source, variant)
    issues.extend(errors)
    count = len(samples)
    if not events or any(e.get('version') != 3 for e in events):
        issues.append(dict(kind='requires_v3'))
    if len(rows) != count or any(r['status'] != 'associated' or r['unknown'] for r in rows):
        issues.append(dict(kind='all_observations_associated_required'))
    constructions = [s for s in spans if s['phase'] == 'service_construction']
    keys = {(s['begin']['pid'], s['begin'].get('service')) for s in constructions}
    if len(constructions) != count + 1 or len(keys) != count + 1 or sorted(s['begin'].get('observation', -1) for s in constructions) != list(range(count + 1)):
        issues.append(dict(kind='setup_and_demands_required'))
    for construction in constructions:
        b = construction['begin']
        owned = [s for s in spans if (s['begin']['pid'], s['begin'].get('service')) == (b['pid'], b.get('service'))]
        destruction = [s for s in owned if s['phase'] == 'service_destruction']
        shutdown = [s for s in owned if s['phase'] == 'service_shutdown']
        if not (len(destruction) == 1 and construction['stop'] <= destruction[0]['start'] and
                all(s['begin'].get('role') == s['end'].get('role') == 'shutdown' and
                    construction['stop'] <= s['start'] <= s['stop'] <= destruction[0]['stop'] for s in shutdown + destruction)):
            issues.append(dict(kind='incomplete_service_shutdown', service=b.get('service')))
    if any((e['pid'], e.get('service')) not in keys for e in events):
        issues.append(dict(kind='foreign_service_lifetime'))
    if variant in 'CD':
        for observation in range(1, count + 1):
            selected = [e for e in events if e.get('observation') == observation and e['phase'] == 'selected_worker']
            jobs = [s for s in spans if s['begin'].get('observation') == observation and s['phase'] == 'pool_job']
            if len(selected) != 1 or len(jobs) != 1 or not selected[0].get('preparation'):
                issues.append(dict(kind='selected_preparation_required', observation=observation))
    return dict(accounting=rows, unassigned=unassigned, issues=issues, service_lifetimes=len(constructions), events=len(events))


def validate(target, invocation, process, uid):
    data = json.loads(target.read_text())
    samples = data.get('samples', [])
    text = target.with_suffix('.stderr').read_text() + '\n' + target.with_suffix('.stdout').read_text()
    if invocation['mode'] == 'T':
        trace = validate_trace(text, samples, str(target), invocation['variant'])
    else:
        trace = dict(issues=[dict(kind='unexpected_trace')] if 'TRACE ' in text else [])
    write(target.with_suffix('.validation.json'), trace)
    if (process['exit'] or process['timeout'] or not process['cleanup_verified'] or data.get('scenario') != 'startup' or
            data.get('fixture') != str(FIXTURE_ROOT / invocation['fixture']) or data.get('cleanup_failure') or
            data.get('incomplete') or len(samples) != invocation['count'] or trace['issues']):
        raise ValueError('process, sample count, completion or trace validation failed: ' + target.name)
    for sample in samples:
        deliveries = sample.get('deliveries', [])
        if (not smoke.measurement.valid_observation(sample) or len(deliveries) != 2 or
                [d.get('event') for d in deliveries] != ['pixels', 'metadata'] or
                any(d.get('selection') != 4 for d in deliveries) or
                [d.get('latency_ms') for d in deliveries] != [sample['first_ms'], sample['final_ms']]):
            raise ValueError('invalid content, delivery timestamp or ordering: ' + target.name)
    if target.stat().st_uid != uid:
        raise ValueError('ordinary-user ownership required')
    work = list(target.parent.glob(target.name + '.work-*'))
    if len(work) != 1 or not (work[0] / 'cache').is_dir():
        raise ValueError('preserved fixture/cache directory required')
    copies = list(work[0].glob('*.' + invocation['fixture'].split('.')[-1]))
    if len(copies) != invocation['count'] * 8 + 8:
        raise ValueError('fixture copy count mismatch')
    fixture_hash = digest(FIXTURE_ROOT / invocation['fixture'])
    for p in [work[0], *work[0].rglob('*')]:
        if p.stat().st_uid != uid:
            raise ValueError('private fixture/cache ownership mismatch')
    if any(digest(p) != fixture_hash for p in copies):
        raise ValueError('private fixture provenance mismatch')
    return samples


def run_invocations(commands, output, result, uid, env, credentials):
    rows = []
    for row in commands:
        invocation, command = row['invocation'], row['argv']
        target = Path(command[-1])
        result['first_failing_command'] = row
        before = smoke.scope_snapshot(uid, env, credentials)
        write(target.with_suffix('.scopes-before.json'), before)
        if not before['isolated']:
            raise RuntimeError('helper activity prevents isolated invocation')
        process = smoke.execute(command, target, env, credentials)
        result['invocations'].append(dict(row, process=process))
        write(output / 'progress.json', result)
        after = smoke.scope_snapshot(uid, env, credentials)
        write(target.with_suffix('.scopes-after.json'), after)
        samples = validate(target, invocation, process, uid)
        if not after['isolated']:
            raise RuntimeError('residual helper scopes; cleanup unverified')
        rows.append(dict(invocation=invocation, samples=samples))
        print(f"{invocation['index'] + 1}/264 validated", flush=True)
    return rows


def execute(package, uid):
    if os.geteuid() != 0 or uid <= 0:
        raise ValueError('sudo -A wrapper and ordinary uid required')
    if (package / 'execution-started.json').exists():
        raise FileExistsError('execution already started; retries prohibited')
    output = package / 'execution'
    output.mkdir()
    output.chmod(0o755)
    account = pwd.getpwuid(uid)
    credentials = dict(user=uid, group=account.pw_gid, extra_groups=os.getgrouplist(account.pw_name, account.pw_gid))
    env = dict(os.environ, HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name,
               XDG_RUNTIME_DIR=f'/run/user/{uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{uid}/bus', QT_QPA_PLATFORM='offscreen')
    result = dict(status='tracing overhead measurement blocked', invocations=[], qualified=False)
    runtime = Path('/run') / ('holonight-overhead-' + package.name)
    runtime_before = None
    try:
        check_seal(package)
        verify_retained()
        if json.loads((package / 'retained-before.json').read_text()) != retained_snapshot():
            raise ValueError('retained inputs changed before execution')
        targets = smoke.observation_directory(output, uid, account.pw_gid)
        probe = targets / 'ownership-probe'
        subprocess.run([sys.executable, '-c', 'import pathlib,sys;pathlib.Path(sys.argv[1]).write_text("ok")', str(probe)], env=env, check=True, **credentials)
        if probe.stat().st_uid != uid:
            raise ValueError('ordinary-user write probe failed')
        commands = []
        for row in schedule():
            key = row['variant'] + row['mode']
            commands.append(dict(invocation=row, argv=[str(package / key / 'reuse-harness/preview-benchmark'), str(runtime / key),
                str(FIXTURE_ROOT / row['fixture']), 'startup', str(row['count']), str(targets / f"{row['index']:03}-{key}-{row['fixture']}.json")]))
        write(output / 'preregistration.json', dict(commands=commands, environment={k: env[k] for k in ('HOME', 'USER', 'LOGNAME', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS', 'QT_QPA_PLATFORM', 'PATH')},
              inherited_relevant={k: v for k, v in env.items() if k.startswith(('QT_', 'LD_', 'CMAKE', 'PKG_CONFIG'))}, credentials=credentials,
              statistics='100 measured samples per cell; median and nearest-rank p95; signed T-U ms and percent relative to U; zero baseline percent null; retain ten block comparisons; warmups excluded.',
              bounds=dict(invocations=264, measured=2400, warmups=24, timeout_seconds=120, term_grace_seconds=5, retries=0),
              failure='Stop at first execution, sample, trace, identity, lifecycle, ownership, cleanup or integrity failure. Timeout cleanup unverified. No repairs, retries, changed expectations or replacements after marker.',
              limits='Full v3 instrumentation effect within existing startup timer only, including bookkeeping/logging inside the window; descriptive host results, no significance claim, threshold, phase subtraction, causal explanation or qualification.',
              staging='A copies frozen legacy payload; B/C/D use manage-images-generations.py install; separate protected runtime for every variant/mode.',
              seal_sha256=digest(package / 'seal.json'), runtime=str(runtime), argv=sys.argv))
        before = smoke.scope_snapshot(uid, env, credentials)
        write(output / 'scopes-before.json', before)
        if not before['isolated']:
            raise RuntimeError('scope supervision unavailable or existing helper activity')
        with (package / 'execution-started.json').open('x') as marker:
            json.dump(dict(preregistration_sha256=digest(output / 'preregistration.json')), marker)
        runtime.mkdir(mode=0o755)
        with (output / 'staging.log').open('x') as log:
            for v in 'ABCD':
                for mode in 'UT':
                    key = v + mode
                    base = package / key
                    if v == 'A':
                        shutil.copytree(base / 'runtime', runtime / key)
                    else:
                        command = [sys.executable, str(ROOT / 'scripts/manage-images-generations.py'), 'install', '--runtime', str(runtime / key), '--source', str(base / 'runtime'), '--helper', str(base / 'build/holonight-images/holonight-images-helper')]
                        subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT, timeout=120)
        for p in [runtime, *runtime.rglob('*')]:
            if p.stat().st_uid != 0 or p.stat().st_mode & 0o022:
                raise ValueError('protected staging ownership/mode failed: ' + str(p))
        runtime_before = inventory(runtime)
        write(output / 'runtime-before.json', runtime_before)
        rows = run_invocations(commands, output, result, uid, env, credentials)
        write(output / 'statistics.json', statistics_report(rows))
        result.pop('first_failing_command', None)
        result['status'] = 'complete'
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        try:
            check_seal(package)
            verify_retained()
            result['retained_integrity'] = json.loads((package / 'retained-before.json').read_text()) == retained_snapshot()
            result['artifact_integrity'] = True
        except (OSError, ValueError, KeyError) as error:
            result['retained_integrity'] = False
            result['artifact_integrity'] = False
            result['integrity_failure'] = str(error)
        if runtime.exists():
            after = inventory(runtime)
            write(output / 'runtime-after.json', after)
            result['runtime_integrity'] = runtime_before is not None and runtime_before == after
        else:
            result['runtime_integrity'] = False
        try:
            snapshot = smoke.scope_snapshot(uid, env, credentials)
            write(output / 'scopes-final.json', snapshot)
            result['cleanup_verified'] = snapshot['isolated'] and not any(r['process']['timeout'] for r in result['invocations'])
        except (OSError, subprocess.SubprocessError):
            result['cleanup_verified'] = False
        if not all(result.get(k) for k in ('retained_integrity', 'artifact_integrity', 'runtime_integrity', 'cleanup_verified')):
            result['status'] = 'tracing overhead measurement blocked'
        write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('# Tracing overhead\n\n' + result['status'] + '\n\n' + result.get('failure', '') + '\n\nSee assessment.json, preregistration.json and observations/. No qualification change.\n')
    return 0 if result['status'] == 'complete' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'build', 'execute'))
    parser.add_argument('package', type=Path)
    parser.add_argument('--uid', type=int)
    args = parser.parse_args()
    package = args.package.resolve()
    if args.action == 'execute':
        raise SystemExit(execute(package, args.uid))
    if args.action == 'prepare':
        prepare(package)
    else:
        build(package)


if __name__ == '__main__':
    main()
