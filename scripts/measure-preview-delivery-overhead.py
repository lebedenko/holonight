#!/usr/bin/env python3
"""Fixed descriptive v4/v3 experiment using a sealed, read-only preparation."""
import argparse
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import importlib.util


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


old = module('delivery_overhead_historical', 'measure-preview-tracing-overhead.py')
prep = module('delivery_overhead_preparation', 'prepare-preview-delivery-overhead.py')
gate = module('delivery_overhead_gate', 'run-preview-delivery-smoke.py')
require, read = gate.require, gate.read
digest, inventory, write = prep.digest, prep.inventory, prep.write
KEYS = [(mode, v) for mode in ('v3', 'v4') for v in 'ABCD']
# Reuse the exact gate with only the scheduled observation bound generalized.
namespace = dict(gate.__dict__)
source = (ROOT / 'scripts/run-preview-delivery-smoke.py').read_text()
start = source.index('def validate_trace_report(')
stop = source.index('\n\ndef validate_invocation', start)
exec(source[start:stop].replace('def validate_trace_report(report, variant):',
     'def validate_trace_report(report, variant, count):').replace('len(endpoints) == 6',
     'len(endpoints) == 2 * count').replace('for observation in (1, 2, 3):',
     'for observation in range(1, count + 1):'), namespace)
v4_gate = namespace['validate_trace_report']


def verify(package):
    seal = read(package / 'seal.json')
    require(inventory(package) == dict(seal, **{'seal.json': digest(package / 'seal.json')}), 'prepared seal mismatch')
    manifest = read(package / 'manifest.json')
    require(manifest['status'] == 'prepared' and not manifest['issues'], 'preparation blocked')
    integrity = read(package / 'input-integrity.json')
    require(integrity['unchanged'] and integrity['before'] == integrity['after'], 'preparation drift')
    # Precisely the consumed inputs; do not re-run the historical driver's broader checks.
    gate.smoke.verify_hashes(Path('/'), integrity['before'])
    for name, hashes in integrity['trees'].items():
        require(inventory(Path(name)) == hashes, 'historical tree drift: ' + name)
    for mode, variant in KEYS:
        base = package / mode / variant
        require(inventory(base) == manifest['outputs'][mode + '/' + variant], 'prepared tree drift')
        require(read(base / 'source-inventory.json') == {g: inventory(base / g) for g in prep.GROUPS}, 'source inventory drift')
        require(read(base / 'probe-to-source.json')['probes'] == prep.probes(base, mode == 'v4'), 'probe inventory drift')
        require(read(package / 'equivalence.json')[variant]['exact_replay'], 'equivalence missing')
    protocol = read(package / 'protocol.json')
    require(protocol['schedule'] == prep.schedule() and protocol['invocations'] == 264 and
            protocol['measured_observations'] == 2400 and protocol['warmups'] == 24 and
            protocol['timeout_seconds'] == 120 and protocol['termination_grace_seconds'] == 5 and protocol['retries'] == 0, 'protocol mismatch')
    return inventory(package)


def fresh(output, package):
    require(not output.is_symlink() and not output.exists(), 'fresh output required')
    require(output.is_relative_to(ROOT / 'build') and not output.is_relative_to(package) and
            not package.is_relative_to(output), 'output must be disjoint beneath ignored build/')
    output.mkdir()


def seal(output):
    write(output / 'seal.json', {k: v for k, v in inventory(output).items() if k != 'seal.json'})


def check_output(output):
    expected = read(output / 'seal.json')
    require(inventory(output) == dict(expected, **{'seal.json': digest(output / 'seal.json')}), 'output integrity drift')


def tools():
    names = ('measure-preview-delivery-overhead.py', 'measure-preview-tracing-overhead.py',
             'prepare-preview-delivery-overhead.py', 'run-preview-delivery-smoke.py',
             'run-preview-startup-smoke.py', 'analyze-preview-startup.py',
             'analyze-preview-startup-v3.py', 'analyze-preview-delivery-gaps-v3.py',
             'analyze-preview-delivery-tracing.py', 'measure-preview-reuse.py',
             'manage-images-generations.py', 'install_state.py')
    tests = ('test_measure_preview_delivery_overhead.py', 'test_preview_tracing_overhead.py',
             'test_preview_startup_smoke.py', 'test_preview_delivery_smoke.py',
             'test_preview_delivery_tracing.py')
    paths = [*(ROOT / 'scripts' / n for n in names), *(ROOT / 'tests' / n for n in tests)]
    return {str(p): digest(p) for p in paths}



def build(package, output):
    fresh(output, package)
    result = dict(status='blocked')
    try:
        before = verify(package)
        write(output / 'prepared-inventory.json', before)
        write(output / 'fixtures.json', fixture_hashes())
        identities = tools()
        write(output / 'tools.json', identities)
        snapshots = output / 'tools'
        snapshots.mkdir()
        for p in identities:
            shutil.copy2(p, snapshots / Path(p).name)
        commands_file = old.NATIVE / 'commands.json'
        recipe_evidence = old.NATIVE / 'evidence-hashes.json'
        require(digest(commands_file) == read(recipe_evidence)['commands.json'], 'historical build recipe drift')
        write(output / 'recipe-identity.json', {str(p): digest(p) for p in (commands_file, recipe_evidence)})
        saved = read(commands_file)
        environment = dict(host=list(os.uname()), environment=dict(os.environ), jobs=4)
        for name, cmd in [('compiler', ['c++', '--version']), ('dependencies', ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp']), ('cmake', ['cmake', '--version']), ('ninja', ['ninja', '--version'])]:
            environment[name] = subprocess.check_output(cmd, text=True)
        write(output / 'environment.json', environment)
        commands = []
        def run(cmd, log):
            commands.append(cmd)
            write(output / 'build-commands.json', commands)
            with log.open('x') as stream:
                subprocess.run(cmd, cwd=ROOT, check=True, stdout=stream, stderr=subprocess.STDOUT)
        for mode, variant in KEYS:
            base = output / mode / variant
            base.mkdir(parents=True)
            original = old.NATIVE / variant
            for i, row in enumerate(r for r in saved if any(str(original) + '/' in a for a in r['argv'])):
                command = []
                for a in row['argv']:
                    a = a.replace(str(original), str(base))
                    for group in prep.GROUPS:
                        a = a.replace(str(base / group), str(package / mode / variant / group))
                    command.append(a)
                run(command, base / f'build-{i:02}.log')
            caches = {}
            for cache in [*(base / 'build').glob('*/CMakeCache.txt'), base / 'reuse-harness/CMakeCache.txt']:
                entries = [s for s in cache.read_text().splitlines() if s.startswith('Holonight') and '_DIR:' in s]
                require(all(s.split('=', 1)[1].startswith(str(base / 'prefix') + '/') for s in entries), 'foreign provider resolution')
                caches[str(cache.relative_to(base))] = entries
            write(base / 'package-resolution.json', caches)
            for label, relative in [('helper', 'build/holonight-images/holonight-images-helper'), ('harness', 'reuse-harness/preview-benchmark')]:
                for kind, cmd in [('linkage', ['ldd']), ('symbols', ['nm', '-C'])]:
                    run([*cmd, str(base / relative)], base / f'{label}-{kind}.log')
                require('not found' not in (base / f'{label}-linkage.log').read_text(), 'unresolved linkage')
                symbols = (base / f'{label}-symbols.log').read_text()
                require('StandbyTrace::' in symbols, 'v3 linkage missing')
                if label == 'harness':
                    require(('DeliveryTrace::' in symbols) == (mode == 'v4'), 'v4 linkage contamination')
            require(digest(base / 'runtime/usr/libexec/holonight-images-helper') == digest(base / 'build/holonight-images/holonight-images-helper'), 'runtime helper mismatch')
            print(mode, variant, 'built', flush=True)
        require(before == verify(package), 'build input drift')
        gate.smoke.verify_hashes(Path('/'), identities)
        result['status'] = 'built'
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    write(output / 'assessment.json', result)
    seal(output)
    return int(result['status'] != 'built')


def statistics_report(rows):
    converted = []
    for index, (row, expected) in enumerate(zip(rows, prep.schedule())):
        require(row['invocation'] == expected, 'schedule mismatch')
        converted.append(dict(invocation=old.schedule()[index], samples=row['samples']))
    require(len(rows) == 264, 'incomplete experiment')
    result = old.statistics_report(converted)
    for cell in result:
        for comparison in [cell['statistics'], *(b['statistics'] for b in cell['blocks'])]:
            for value in comparison.values():
                value['v3'] = value.pop('U')
                value['v4'] = value.pop('T')
    return result


def fixture_hashes():
    provenance = read(gate.smoke.PROVENANCE)['fixtures']
    expected = {str(old.FIXTURE_ROOT / name): provenance[str(old.FIXTURE_ROOT / name)] for name in old.FIXTURES}
    gate.smoke.verify_hashes(Path('/'), expected)
    return expected


def validate_work(target, row, uid):
    work = list(target.parent.glob(target.name + '.work-*'))
    require(len(work) == 1 and (work[0] / 'cache').is_dir(), 'private work missing')
    require(all(p.stat().st_uid == uid for p in [work[0], *work[0].rglob('*')]), 'private ownership mismatch')
    fixture = old.FIXTURE_ROOT / row['fixture']
    copies = list(work[0].glob('*' + fixture.suffix))
    # The frozen harness creates count * 8 + 8 independent source files.
    require(len(copies) == row['observations'] * 8 + 8 and all(digest(p) == digest(fixture) for p in copies), 'fixture provenance mismatch')


def validate(target, row, process, uid, replay=False):
    require(process['exit'] == 0 and not process['timeout'] and process['cleanup_verified'], 'process failed or cleanup unverified')
    data = read(target)
    samples = data.get('samples', [])
    require(target.stat().st_uid == uid and data.get('scenario') == 'startup' and
            data.get('fixture') == str(old.FIXTURE_ROOT / row['fixture']) and
            not any(data.get(k) for k in ('cleanup_failure', 'setup_failure', 'incomplete')) and
            len(samples) == row['observations'], 'invalid harness completion')
    for sample in samples:
        deliveries = sample.get('deliveries', [])
        require(gate.smoke.measurement.valid_observation(sample) and len(deliveries) == 2 and
                [d.get('event') for d in deliveries] == ['pixels', 'metadata'] and
                all(d.get('selection') == 4 for d in deliveries) and
                [d.get('latency_ms') for d in deliveries] == [sample['first_ms'], sample['final_ms']], 'invalid observation')
    text = target.with_suffix('.stderr').read_text() + '\n' + target.with_suffix('.stdout').read_text()
    v3 = old.validate_trace(text, samples, str(target), row['variant'])
    if replay:
        require(read(target.with_suffix('.v3.json')) == v3, 'v3 accounting replay mismatch')
    else:
        write(target.with_suffix('.v3.json'), v3)
    require(not v3['issues'], 'v3 lifecycle failure')
    if row['mode'] == 'v3':
        require('DELIVERY ' not in text, 'supplemental contamination')
    else:
        report = gate.analyzer.analyze(text, str(target.with_suffix('.stderr').resolve()), row['variant'], samples)
        if replay:
            require(read(target.with_suffix('.v4.json')) == report, 'v4 accounting replay mismatch')
        else:
            write(target.with_suffix('.v4.json'), report)
        v4_gate(report, row['variant'], row['observations'])
    validate_work(target, row, uid)
    return samples


def staged(base, runtime, variant):
    # Existing selector checker operates on one variant at a time.
    gate.staged_payloads(base, runtime, variant)
    return gate.protected_inventory(runtime / variant)


def run_commands(commands, output, result, uid, env, credentials, integrity):
    for entry in commands:
        integrity()
        target = Path(entry['argv'][-1])
        before = gate.scope_snapshot(uid, env, credentials)
        write(target.with_suffix('.scopes-before.json'), before)
        require(before['isolated'], 'residual scopes')
        process = gate.smoke.execute(entry['argv'], target, env, credentials)
        result['invocations'].append(dict(entry, process=process, status='failed'))
        write(output / 'progress.json', result)
        after = gate.scope_snapshot(uid, env, credentials)
        write(target.with_suffix('.scopes-after.json'), after)
        samples = validate(target, entry['invocation'], process, uid)
        require(after['isolated'], 'residual scopes')
        result['invocations'][-1].update(status='passed', samples=samples)
        write(output / 'progress.json', result)
        print(len(result['invocations']), '/264 passed', flush=True)


def execute(package, built, output, uid):
    require(os.geteuid() == 0 and uid and uid > 0, 'privileged wrapper and ordinary uid required')
    require(not (built / 'execution-started.json').exists(), 'execution already started')
    account = pwd.getpwuid(uid)
    fresh(output, package)
    result = dict(status='blocked', invocations=[], qualified=False)
    runtime = Path('/run') / ('holonight-delivery-overhead-' + built.name + '-' + output.name)
    runtime_before = None
    credentials = dict(user=uid, group=account.pw_gid, extra_groups=os.getgrouplist(account.pw_name, account.pw_gid))
    env = {k: os.environ[k] for k in ('PATH', 'LANG', 'LC_ALL', 'TZ') if k in os.environ}
    installer_env = dict(env)
    env.update(HOME=account.pw_dir, USER=account.pw_name, LOGNAME=account.pw_name, XDG_RUNTIME_DIR=f'/run/user/{uid}', DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{uid}/bus', QT_QPA_PLATFORM='offscreen')
    try:
        check_output(built)
        require(read(built / 'assessment.json')['status'] == 'built', 'build blocked')
        require(verify(package) == read(built / 'prepared-inventory.json'), 'prepared drift')
        gate.smoke.verify_hashes(Path('/'), read(built / 'tools.json'))
        require(fixture_hashes() == read(built / 'fixtures.json'), 'fixture drift')
        gate.smoke.verify_hashes(Path('/'), read(built / 'recipe-identity.json'))
        targets = gate.observation_directory(output, uid, account.pw_gid)
        probe = targets / 'write-probe'
        subprocess.run([sys.executable, '-c', 'import pathlib,sys;pathlib.Path(sys.argv[1]).write_text("ok")', str(probe)], env=env, check=True, **credentials)
        require(probe.stat().st_uid == uid, 'ordinary-user write failed')
        commands = [dict(invocation=row, argv=[str(built / row['mode'] / row['variant'] / 'reuse-harness/preview-benchmark'), str(runtime / row['mode'] / row['variant']), str(old.FIXTURE_ROOT / row['fixture']), 'startup', str(row['observations']), str(targets / f'{i:03}.json')]) for i, row in enumerate(prep.schedule())]
        write(output / 'preregistration.json', dict(commands=commands, environment=env, credentials=credentials, runtime=str(runtime), fixtures=inventory(old.FIXTURE_ROOT), built_seal=digest(built / 'seal.json'), protocol=read(package / 'protocol.json')))
        require(gate.scope_snapshot(uid, env, credentials)['isolated'], 'scope isolation unavailable')
        with (built / 'execution-started.json').open('x') as marker:
            json.dump(dict(output=str(output)), marker)
        runtime.mkdir(mode=0o755)
        for mode, variant in KEYS:
            base, destination = built / mode / variant, runtime / mode
            destination.mkdir(exist_ok=True)
            if variant == 'A':
                shutil.copytree(base / 'runtime', destination / variant)
            else:
                command = [sys.executable, '-B', str(built / 'tools/manage-images-generations.py'), 'install', '--runtime', str(destination / variant), '--source', str(base / 'runtime'), '--helper', str(base / 'build/holonight-images/holonight-images-helper')]
                process = gate.smoke.execute(command, output / f'installer-{mode}-{variant}.json', installer_env, {})
                write(output / f'installer-{mode}-{variant}-status.json', process)
                require(process['exit'] == 0 and not process['timeout'] and process['cleanup_verified'], 'staging failed')
            staged(built / mode, destination, variant)
        runtime_before = gate.protected_inventory(runtime)
        write(output / 'runtime-before.json', runtime_before)
        def integrity():
            require(verify(package) == read(built / 'prepared-inventory.json'), 'input drift')
            gate.smoke.verify_hashes(built, read(built / 'seal.json'))
            gate.smoke.verify_hashes(Path('/'), read(built / 'tools.json'))
            require(fixture_hashes() == read(built / 'fixtures.json'), 'fixture drift')
            require(gate.protected_inventory(runtime) == runtime_before, 'runtime drift')
        run_commands(commands, output, result, uid, env, credentials, integrity)
        write(output / 'statistics.json', statistics_report(result['invocations']))
        result['status'] = 'complete'
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, RuntimeError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        try:
            require(verify(package) == read(built / 'prepared-inventory.json'), 'final prepared drift')
            gate.smoke.verify_hashes(Path('/'), read(built / 'tools.json'))
            require(fixture_hashes() == read(built / 'fixtures.json'), 'final fixture drift')
            gate.smoke.verify_hashes(built, read(built / 'seal.json'))
            require(runtime_before is not None and gate.protected_inventory(runtime) == runtime_before, 'final runtime drift')
            snapshot = gate.scope_snapshot(uid, env, credentials)
            write(output / 'scopes-final.json', snapshot)
            require(snapshot['isolated'], 'final scopes unverified')
            write(output / 'runtime-after.json', gate.protected_inventory(runtime))
            result['integrity_verified'] = True
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, subprocess.SubprocessError) as error:
            result.update(status='blocked', integrity_failure=str(error))
        write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('# Incremental delivery tracing overhead\n\n' + result['status'] + '\n\n' + result.get('failure', '') + '\n\nNo qualification or causal attribution claim. Retained fixtures must not be removed.\n')
        seal(output)
    return int(result['status'] != 'complete')


def render_report(output, assessment, statistics=None):
    lines = ['# Incremental v4 delivery-tracing overhead', '',
             'Status: **' + assessment['status'] + '**.', '']
    if statistics is None:
        lines += ['Failure: ' + str(assessment.get('execution_failure') or assessment.get('failure')), '',
                  f"Launched invocations: {assessment.get('launched', 0)} of 264; unexecuted: {assessment.get('unexecuted', 264)}.",
                  f"Measured observations launched: {assessment.get('measured_observations', 0)} of 2,400.", '',
                  'Statistics are unavailable. No failed or missing sample is replaced.']
    else:
        lines += ['All 2,400 measured observations are retained; only the 24 declared warm-ups are excluded.', '',
                  '| Fixture | Variant | Endpoint | Block | Statistic | v3 ms | v4 ms | v4−v3 ms | Percent |',
                  '|---|---|---|---|---|---|---|---|---|']
        for cell in statistics:
            for block, comparison in [('all', cell['statistics']), *[(str(b['block']), b['statistics']) for b in cell['blocks']]]:
                for statistic, values in comparison.items():
                    percent = 'unavailable' if values['delta_percent'] is None else f"{values['delta_percent']:+.4f}%"
                    endpoint = 'pixels' if cell['event'] == 'first_ms' else 'final metadata'
                    lines.append(f"| {cell['fixture']} | {cell['variant']} | {endpoint} | {block} | {statistic} | {values['v3']:.6f} | {values['v4']:.6f} | {values['delta_ms']:+.6f} | {percent} |")
    lines += ['', 'Medians and nearest-rank p95 describe this host and the original startup timer. '
              'Negative differences are retained; percentages for zero v3 baselines are unavailable. '
              'Host dependencies and environment are recorded in the build evidence and execution preregistration. '
              'No significance claim, threshold, overhead subtraction, scheduling/CPU attribution, '
              'or change to C qualification or D pilot conclusions is made.', '']
    (output / 'REPORT.md').write_text('\n'.join(lines))


def report(package, execution, output):
    fresh(output, package)
    try:
        verify(package)
        check_output(execution)
        result = read(execution / 'assessment.json')
        require(result['status'] == 'complete' and result['integrity_verified'], 'incomplete run')
        rows = []
        uid = read(execution / 'preregistration.json')['credentials']['user']
        for row in result['invocations']:
            target = Path(row['argv'][-1])
            saved = {suffix: digest(target.with_suffix(suffix)) for suffix in ('.v3.json', '.v4.json') if target.with_suffix(suffix).exists()}
            samples = validate(target, row['invocation'], row['process'], uid, replay=True)
            require(all(digest(target.with_suffix(s)) == h for s, h in saved.items()), 'accounting replay mismatch')
            rows.append(dict(invocation=row['invocation'], samples=samples))
        statistics = statistics_report(rows)
        require(statistics == read(execution / 'statistics.json'), 'statistics replay mismatch')
        write(output / 'statistics.json', statistics)
        write(output / 'assessment.json', dict(status='complete', independent_replay=True))
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as error:
        assessment = result if 'result' in locals() and isinstance(result, dict) else {}
        invocations = assessment.get('invocations', [])
        write(output / 'assessment.json', dict(status='blocked', failure=str(error), execution_failure=assessment.get('failure'), launched=len(invocations), unexecuted=264-len(invocations), measured_observations=sum(r['invocation']['observations'] for r in invocations if not r['invocation']['warmup']), statistics_available=False))
    assessment = read(output / 'assessment.json')
    render_report(output, assessment, read(output / 'statistics.json') if assessment['status'] == 'complete' else None)
    seal(output)
    return int(assessment['status'] != 'complete')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'execute', 'report'))
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--built', type=Path)
    parser.add_argument('--execution', type=Path)
    parser.add_argument('--uid', type=int)
    args = parser.parse_args()
    require(not args.output.is_symlink(), 'symlink output refused')
    package, output = args.prepared.resolve(), args.output.resolve()
    if args.action == 'build':
        return build(package, output)
    if args.action == 'execute':
        require(args.built is not None, '--built required')
        return execute(package, args.built.resolve(), output, args.uid)
    require(args.execution is not None, '--execution required')
    return report(package, args.execution.resolve(), output)


if __name__ == '__main__':
    sys.exit(main())
