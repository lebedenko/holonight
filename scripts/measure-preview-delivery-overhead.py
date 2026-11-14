#!/usr/bin/env python3
"""Fixed descriptive v4/v3 experiment using a sealed, read-only preparation."""
import argparse
import json
import os
from pathlib import Path
import pwd
import shutil
import stat
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
RUNTIME_ROOT = Path('/run')
KEYS = [(mode, v) for mode in ('v3', 'v4') for v in 'ABCD']
def v4_gate(report, variant, count):
    require(not report['issues'] and report['events'], 'v3/v4 trace issues or missing v4 records')
    events, spans = report['events'], report['spans']
    endpoints = [e for e in events if e['operation'].startswith('endpoint_')]
    require(len(endpoints) == 2 * count, 'two unique endpoints per observation required')
    for observation in range(1, count + 1):
        selected = [e for e in endpoints if e['observation'] == observation]
        require(sorted(e['operation'] for e in selected) == ['endpoint_metadata', 'endpoint_pixels'], 'missing or duplicate endpoints')
        require(len({tuple(e[k] for k in ('pid', *gate.analyzer.IDENTITIES) if k != 'publication') for e in selected}) == 1, 'endpoint identities conflict')
        for e in selected:
            require(all(e[k] is not None for k in ('service', 'observation', 'job', 'worker', 'generation', 'session', 'transaction', 'publication')), 'explicit endpoint identity required')
            handoff = [h for h in report['handoffs'] if h['pid'] == e['pid'] and h['publication'] == e['publication']]
            require(len(handoff) == 1 and not handoff[0].get('unavailable') and not handoff[0].get('decision_unavailable'), 'incomplete handoff')
            for op in ('enqueue_call', 'callback_execution', 'apply_result', 'changed_emission'):
                found = [s for s in spans if s['operation'] == op and gate.analyzer.identity(s['begin']) == gate.analyzer.identity(e)]
                require(len(found) == 1 and found[0]['begin']['line'] < found[0]['end']['line'], 'missing or misordered required handoff span')
        endpoint = selected[0]
        owned = [s for s in spans if all(s['begin'][k] == endpoint[k] for k in ('pid', 'service', 'observation', 'job', 'worker', 'preparation', 'generation', 'session', 'transaction'))]
        required = {'reusable_completion_ack': 'acknowledged'} if variant in 'CD' else {'oneshot_ack': 'sent', 'helper_exit': 'validated_exit', 'effective_cleanup': 'verified'}
        for op, outcome in required.items():
            found = [s for s in owned if s['operation'] == op]
            require(len(found) == 1 and found[0]['end']['outcome'] == outcome and found[0]['begin']['line'] < found[0]['end']['line'] and found[0]['stop'] <= min(e['ns'] for e in selected), 'missing or invalid transaction evidence: ' + op)


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


def fresh(output, *consumed):
    require(not output.is_symlink() and not output.exists(), 'fresh output required')
    require(output == output.resolve() and output.is_relative_to((ROOT / 'build').resolve()) and
            all(not output.is_relative_to(p.resolve()) and not p.resolve().is_relative_to(output)
                for p in consumed), 'output must be disjoint beneath ignored build/')
    protected = [*old.RETAINED, old.FIXTURE_ROOT, *(ROOT / 'build' / n for n in prep.SUPPORT)]
    if consumed and (consumed[0] / 'input-integrity.json').is_file():
        integrity = read(consumed[0] / 'input-integrity.json')
        protected += [Path(n) for n in integrity['trees']]
        protected += [Path(n).parent for n in integrity['before']]
    require(all(not output.is_relative_to(p.resolve()) and not p.resolve().is_relative_to(output)
                for p in protected), 'destination overlaps consumed historical evidence')
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



def providers(base):
    expected = {
        'build/holonight-images/CMakeCache.txt': set(),
        'build/holonight-thumbnails/CMakeCache.txt': {'HolonightImages'},
        'build/holonight-file-browser/CMakeCache.txt': {'HolonightImages', 'HolonightThumbnails'},
        'reuse-harness/CMakeCache.txt': {'HolonightImages', 'HolonightThumbnails', 'HolonightFileBrowser'},
    }
    caches = {}
    for relative, required in expected.items():
        entries = [s for s in (base / relative).read_text().splitlines()
                   if s.startswith('Holonight') and '_DIR:' in s]
        require({s.split('_DIR:', 1)[0] for s in entries} == required, 'required provider resolution missing')
        for entry in entries:
            path = Path(entry.split('=', 1)[1])
            require(path.is_relative_to(base / 'prefix') and path.resolve().is_relative_to(base / 'prefix'), 'foreign provider resolution')
        caches[relative] = entries
    return caches


def bundles(base):
    manifests = []
    for group in ('runtime', 'prefix/libexec/holonight-images/runtime'):
        bundle = base / group
        manifest = read(bundle / 'manifest.json')
        files = manifest['files']
        require(set(inventory(bundle)) == {r['path'] for r in files} | {'manifest.json'} and
                len(files) == len({r['path'] for r in files}), 'runtime inventory mismatch')
        for row in files:
            path = prep.child(bundle, row['path'])
            require(digest(path) == row['sha256'] and path.stat().st_size == row['size'] and
                    stat.S_IMODE(path.stat().st_mode) == row['mode'], 'runtime payload mismatch')
        require(digest(bundle / 'usr/libexec/holonight-images-helper') ==
                digest(base / 'build/holonight-images/holonight-images-helper'), 'runtime helper mismatch')
        manifests.append(manifest)
    require(manifests[0] == manifests[1], 'runtime manifests differ')


def built_integrity(built, execution):
    expected = read(built / 'seal.json')
    actual = inventory(built)
    marker = actual.pop('execution-started.json', None)
    if marker is not None:
        require(read(built / 'execution-started.json') == dict(output=str(execution)), 'execution marker mismatch')
    require(actual == dict(expected, **{'seal.json': digest(built / 'seal.json')}), 'built inventory drift')


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
            write(base / 'package-resolution.json', providers(base))
            bundles(base)
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
        result['invocations'].append(dict(entry, status='failed'))
        write(output / 'progress.json', result)
        process = gate.smoke.execute(entry['argv'], target, env, credentials)
        result['invocations'][-1]['process'] = process
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
    fresh(output, package, built)
    result = dict(status='blocked', invocations=[], qualified=False)
    runtime = RUNTIME_ROOT / ('holonight-delivery-overhead-' + built.parent.name + '-' + built.name + '-' + output.name)
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
        write(output / 'preregistration.json', dict(built=str(built), prepared=str(package), host=list(os.uname()), tools=read(built / 'tools.json'), fixture_identities=read(built / 'fixtures.json'), dependencies={mode + '/' + variant: read(built / mode / variant / 'package-resolution.json') for mode, variant in KEYS}, staging_commands=[dict(mode=mode, variant=variant, source=str(built / mode / variant / 'runtime'), destination=str(runtime / mode / variant), helper=str(built / mode / variant / 'build/holonight-images/holonight-images-helper')) for mode, variant in KEYS], commands=commands, environment=env, credentials=credentials, runtime=str(runtime), fixtures=inventory(old.FIXTURE_ROOT), built_seal=digest(built / 'seal.json'), protocol=read(package / 'protocol.json')))
        require(gate.scope_snapshot(uid, env, credentials)['isolated'], 'scope isolation unavailable')
        with (built / 'execution-started.json').open('x') as marker:
            json.dump(dict(output=str(output)), marker)
        require(not runtime.exists() and not runtime.is_symlink(), 'runtime destination reused')
        runtime.mkdir(mode=0o755)
        staging_commands = []
        for mode, variant in KEYS:
            base, destination = built / mode / variant, runtime / mode
            destination.mkdir(exist_ok=True)
            if variant == 'A':
                staging_commands.append(dict(copytree=[str(base / 'runtime'), str(destination / variant)]))
                write(output / 'staging-commands.json', staging_commands)
                shutil.copytree(base / 'runtime', destination / variant)
            else:
                command = [sys.executable, '-B', str(built / 'tools/manage-images-generations.py'), 'install', '--runtime', str(destination / variant), '--source', str(base / 'runtime'), '--helper', str(base / 'build/holonight-images/holonight-images-helper')]
                staging_commands.append(dict(argv=command))
                write(output / 'staging-commands.json', staging_commands)
                process = gate.smoke.execute(command, output / f'installer-{mode}-{variant}.json', installer_env, {})
                write(output / f'installer-{mode}-{variant}-status.json', process)
                require(process['exit'] == 0 and not process['timeout'] and process['cleanup_verified'], 'staging failed')
            staged(built / mode, destination, variant)
        runtime_before = gate.protected_inventory(runtime)
        write(output / 'runtime-before.json', runtime_before)
        def integrity():
            require(verify(package) == read(built / 'prepared-inventory.json'), 'input drift')
            built_integrity(built, output)
            gate.smoke.verify_hashes(Path('/'), read(built / 'tools.json'))
            require(fixture_hashes() == read(built / 'fixtures.json'), 'fixture drift')
            require(gate.protected_inventory(runtime) == runtime_before, 'runtime drift')
        run_commands(commands, output, result, uid, env, credentials, integrity)
        write(output / 'statistics.json', statistics_report(result['invocations']))
        result['status'] = 'complete'
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, RuntimeError, subprocess.SubprocessError) as error:
        result['failure'] = str(error)
    finally:
        checks = {}
        def checked(name, action):
            try:
                action()
                checks[name] = dict(passed=True)
            except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, RuntimeError, subprocess.SubprocessError) as error:
                checks[name] = dict(passed=False, failure=str(error))
        def inputs():
            final = verify(package)
            write(output / 'final-input-inventory.json', final)
            require(final == read(built / 'prepared-inventory.json'), 'final prepared drift')
            gate.smoke.verify_hashes(Path('/'), read(built / 'tools.json'))
            require(fixture_hashes() == read(built / 'fixtures.json'), 'final fixture drift')
        def artifacts():
            write(output / 'final-artifact-inventory.json', inventory(built))
            built_integrity(built, output)
        def runtimes():
            after = gate.protected_inventory(runtime)
            write(output / 'runtime-after.json', after)
            require(runtime_before is not None and after == runtime_before, 'final runtime drift')
            for mode, variant in KEYS:
                staged(built / mode, runtime / mode, variant)
        def scopes():
            snapshot = gate.scope_snapshot(uid, env, credentials)
            write(output / 'scopes-final.json', snapshot)
            require(snapshot['isolated'], 'final scopes unverified')
        for name, action in [('inputs', inputs), ('artifacts', artifacts), ('runtime', runtimes), ('scopes', scopes)]:
            checked(name, action)
        result['final_checks'] = checks
        result['integrity_verified'] = all(c['passed'] for c in checks.values())
        if not result['integrity_verified']:
            result['status'] = 'blocked'
        write(output / 'assessment.json', result)
        (output / 'ASSESSMENT.md').write_text('# Incremental delivery tracing overhead\n\n' + result['status'] + '\n\n' + result.get('failure', '') + '\n\nNo qualification or causal attribution claim. Retained fixtures must not be removed.\n')
        seal(output)
    return int(result['status'] != 'complete')


def render_report(output, assessment, statistics=None):
    lines = ['# Incremental v4 delivery-tracing overhead', '',
             'Status: **' + assessment['status'] + '**.', '']
    if statistics is None:
        lines += ['Failure: ' + str(assessment.get('execution_failure') or assessment.get('failure')), '',
                  f"Launched invocations: {assessment.get('launched')} of 264; failed: {assessment.get('failed')}; unexecuted: {assessment.get('unexecuted')}.",
                  f"Validated warm-up observations available: {assessment.get('warmup_observations')} of 24.",
                  f"Validated measured observations available: {assessment.get('measured_observations', 0)} of 2,400.", '',
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
    consumed = [package, execution]
    try:
        built_name = read(execution / 'preregistration.json')['built']
        require(isinstance(built_name, str) and Path(built_name).is_absolute(), 'invalid artifact root')
        consumed.append(Path(built_name))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    fresh(output, *consumed)
    try:
        verify(package)
        check_output(execution)
        result = read(execution / 'assessment.json')
        prereg = read(execution / 'preregistration.json')
        built = Path(prereg['built'])
        require(digest(built / 'seal.json') == prereg['built_seal'], 'build seal mismatch')
        built_integrity(built, execution)
        gate.smoke.verify_hashes(Path('/'), read(built / 'tools.json'))
        require(fixture_hashes() == read(built / 'fixtures.json'), 'report fixture drift')
        gate.smoke.verify_hashes(Path('/'), read(built / 'recipe-identity.json'))
        require(read(execution / 'scopes-final.json')['isolated'], 'final scopes unverified')
        require(all(result['final_checks'][name]['passed'] for name in ('inputs', 'artifacts', 'runtime', 'scopes')), 'failed final checks')
        require(verify(package) == read(execution / 'final-input-inventory.json') == read(built / 'prepared-inventory.json'), 'final source mismatch')
        require(inventory(built) == read(execution / 'final-artifact-inventory.json'), 'final artifact mismatch')
        require(read(execution / 'runtime-before.json') == read(execution / 'runtime-after.json'), 'saved runtime mismatch')
        runtime = Path(prereg['runtime'])
        require(gate.protected_inventory(runtime) == read(execution / 'runtime-after.json'), 'final runtime mismatch')
        for mode, variant in KEYS:
            staged(built / mode, runtime / mode, variant)
        expected_commands = [dict(invocation=row, argv=[str(built / row['mode'] / row['variant'] / 'reuse-harness/preview-benchmark'), str(runtime / row['mode'] / row['variant']), str(old.FIXTURE_ROOT / row['fixture']), 'startup', str(row['observations']), str(execution / 'observations' / f'{i:03}.json')]) for i, row in enumerate(prep.schedule())]
        require(prereg['commands'] == expected_commands, 'scheduled commands mismatch')
        require(result['status'] == 'complete' and result['integrity_verified'], 'incomplete run')
        rows = []
        uid = read(execution / 'preregistration.json')['credentials']['user']
        require(len(result['invocations']) == 264, 'incomplete experiment')
        for row, expected in zip(result['invocations'], expected_commands):
            require(row['invocation'] == expected['invocation'] and row['argv'] == expected['argv'] and row['status'] == 'passed', 'saved command mismatch')
            target = Path(row['argv'][-1])
            saved = {suffix: digest(target.with_suffix(suffix)) for suffix in ('.v3.json', '.v4.json') if target.with_suffix(suffix).exists()}
            samples = validate(target, row['invocation'], row['process'], uid, replay=True)
            require(samples == row['samples'], 'saved samples mismatch')
            require(all(digest(target.with_suffix(s)) == h for s, h in saved.items()), 'accounting replay mismatch')
            rows.append(dict(invocation=row['invocation'], samples=samples))
        statistics = statistics_report(rows)
        require(statistics == read(execution / 'statistics.json'), 'statistics replay mismatch')
        write(output / 'statistics.json', statistics)
        write(output / 'assessment.json', dict(status='complete', independent_replay=True))
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, RuntimeError) as error:
        assessment = result if 'result' in locals() and isinstance(result, dict) else {}
        invocations = assessment.get('invocations')
        valid = isinstance(invocations, list) and len(invocations) <= 264
        if valid:
            valid = all(isinstance(r, dict) and r.get('invocation') == expected and
                        r.get('status') in ('passed', 'failed')
                        for r, expected in zip(invocations, prep.schedule()))
        counts = dict(launched=None, failed=None, unexecuted=None, measured_observations=None, warmup_observations=None)
        if valid:
            counts.update(launched=len(invocations), failed=sum(r['status'] == 'failed' for r in invocations), unexecuted=264-len(invocations))
            # Only saved, validated samples count as available observations.
            for warmup, key in [(False, 'measured_observations'), (True, 'warmup_observations')]:
                counts[key] = sum(len(r['samples']) for r in invocations
                                  if r['invocation']['warmup'] == warmup and r['status'] == 'passed'
                                  and isinstance(r.get('samples'), list) and len(r['samples']) == r['invocation']['observations'])
        write(output / 'assessment.json', dict(status='blocked', failure=str(error), execution_failure=assessment.get('failure'), **counts, statistics_available=False))
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
    require(args.output.absolute() == args.output.resolve(), 'symlink output ancestors refused')
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
