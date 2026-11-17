#!/usr/bin/env python3
"""Prepare, build and execute the private, preregistered 64 KiB startup trial."""
import argparse
import difflib
import importlib.util
import math
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import time
from types import SimpleNamespace

sys.dont_write_bytecode = True

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e = load('streaming_evidence', 'preview-streaming-trial-evidence.py')
h, ROOT = e.h, e.ROOT
ENV_KEYS = ('PATH', 'CC', 'CXX', 'CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'CMAKE_PREFIX_PATH',
            'PKG_CONFIG_PATH', 'LD_LIBRARY_PATH', 'QT_QPA_PLATFORM', 'QT_PLUGIN_PATH',
            'QT_QPA_PLATFORM_PLUGIN_PATH', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS',
            'DEBUGINFOD_URLS', 'DEBUGINFOD_PROGRESS', 'PERF_BUILDID_DIR')


def environment(env):
    return {key: env.get(key) for key in ENV_KEYS}


ERRORS = (OSError, ValueError, KeyError, TypeError, IndexError, subprocess.SubprocessError, KeyboardInterrupt)


def schedule():
    rows = [dict(arm=arm, warmup=True, block=None, observation=0, count=1) for arm in e.ARMS]
    for block in range(10):
        for arm in e.ARMS if block % 2 == 0 else e.ARMS[::-1]:
            rows += [dict(arm=arm, warmup=False, block=block, observation=i, count=1) for i in range(10)]
    return [dict(index=i, **row) for i, row in enumerate(rows)]


def protocol():
    return dict(version=1, schedule=schedule(), fresh_processes=202, measured_per_arm=100,
        warmups_per_arm=1, jobs=4, build_type='Release', chunk_bytes=65536, workload_seconds=30,
        shared_cleanup_seconds=5, retries=0, recording=False, offscreen=True, cache_flushing=False,
        affinity_changes=False, artificial_load=False, additional_timed_instrumentation=False,
        rule='Both startup p95s improve by at least 5 ms and neither median regresses.',
        qualification='78/80 unchanged', historical_timing_transfer=False, overhead_correction=False,
        loading_identity='New input/build identities only; uncaptured loading identities unavailable.')


def summarize(rows, complete):
    populations, blocks, signs = {}, [], []
    measured = [r for r in rows if not r['schedule']['warmup']]
    def distribution(values):
        values = sorted(values)
        return dict(count=len(values), median=statistics.median(values),
                    p95=values[math.ceil(.95 * len(values)) - 1]) if values else None
    for arm in e.ARMS:
        populations[arm] = {event: distribution([r['sample'][event] for r in measured if r['schedule']['arm'] == arm])
                            for event in ('first_ms', 'final_ms')}
    for block in range(10):
        for event in ('first_ms', 'final_ms'):
            cells = [[r['sample'][event] for r in measured if r['schedule']['arm'] == arm and
                      r['schedule']['block'] == block] for arm in e.ARMS]
            if all(len(c) == 10 for c in cells):
                cells = [distribution(c) for c in cells]
                blocks.append(dict(block=block, event=event, **{key: cells[1][key] - cells[0][key] for key in ('median', 'p95')}))
    for event in ('first_ms', 'final_ms'):
        for key in ('median', 'p95'):
            values = [b[key] for b in blocks if b['event'] == event]
            signs.append(dict(event=event, statistic=key, negative=sum(x < 0 for x in values),
                              zero=sum(x == 0 for x in values), positive=sum(x > 0 for x in values)))
    eligible = complete and len(rows) == 202 and all(
        populations['control'][event]['p95'] - populations['candidate'][event]['p95'] >= 5 and
        populations['candidate'][event]['median'] <= populations['control'][event]['median']
        for event in ('first_ms', 'final_ms'))
    return dict(populations=populations, blocks=blocks, signs=signs,
        decision=('Recommend later production work' if eligible else 'Deferred') if complete else 'Evidence insufficient')


def action(output, inputs, work):
    h.fresh(output, inputs)
    result = dict(status='blocked', stage='preflight')
    identities = {}
    integrity = dict(passed=False)
    try:
        identities = e.tools()
        (output / 'tools').mkdir()
        for name in identities:
            shutil.copy2(name, output / 'tools' / Path(name).name)
        h.write(output / 'tools.json', identities)
        work(result)
        h.require(e.tools() == identities, 'tool drift during action')
        integrity = dict(passed=True, tools=identities, inputs=[str(p) for p in inputs])
    except ERRORS as error:
        result.update(status='blocked', failure=str(error) or type(error).__name__)
    finally:
        h.write(output / 'integrity.json', integrity)
        h.write(output / 'assessment.json', result)
        if not (output / 'REPORT.md').exists():
            (output / 'REPORT.md').write_text('# Private streaming trial\n\nStatus: ' + result['status'] +
                '\n\n' + result.get('failure', '') + '\n\nNo historical timing transfer or qualification revision.\n')
        h.write(output / 'seal.json', h.inventory(output))
    return result


def prepare(output):
    def work(result):
        inputs = e.retained()
        h.write(output / 'inputs.json', inputs)
        h.write(output / 'protocol.json', protocol())
        shutil.copy2(inputs['fixture']['path'], output / '3200x2400.png')
        for arm in e.ARMS:
            shutil.copytree(e.Q / 'C/source', output / arm / 'source')
            shutil.copytree(e.Q / 'harness-source', output / arm / 'harness-source')
        original = (output / 'control/source' / e.RELATIVE).read_text()
        changed = e.transformed(original, (output / 'tools/hash-loop.inc').read_text())
        (output / 'candidate/source' / e.RELATIVE).write_text(changed)
        (output / 'candidate.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),
            changed.splitlines(True), fromfile='control/' + e.RELATIVE, tofile='candidate/' + e.RELATIVE)))
        h.require(h.recheck(inputs['inventories'], inputs['files']), 'preparation input drift')
        result.update(status='prepared', stage='complete')
    return action(output, [e.Q, e.REVIEW], work)


def command(argv, directory, label, timeout=600):
    argv = [str(a) for a in argv]
    h.write(directory / (label + '-command.json'), dict(argv=argv, timeout_seconds=timeout))
    with (directory / (label + '.stdout')).open('x') as out, (directory / (label + '.stderr')).open('x') as err:
        value = subprocess.run(argv, stdout=out, stderr=err, timeout=timeout, env=dict(os.environ, QT_QPA_PLATFORM='offscreen'))
    h.write(directory / (label + '-process.json'), dict(exit=value.returncode))
    value.check_returncode()
    return (directory / (label + '.stdout')).read_text()


def build(package, output):
    def work(result):
        e.check_package(package, provenance=True)
        h.require(h.read(package / 'protocol.json') == protocol(), 'protocol drift')
        h.write(output / 'package.json', dict(path=str(package), seal=h.digest(package / 'seal.json')))
        h.write(output / 'environment.json', dict(host=list(os.uname()), environment=environment(os.environ), jobs=4,
            affinity=sorted(os.sched_getaffinity(0)), cpuinfo=Path('/proc/cpuinfo').read_text()))
        command(['c++', '--version'], output, 'compiler')
        command(['cmake', '--version'], output, 'cmake')
        command(['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp'], output, 'dependencies')
        dependency_paths = {}
        runtimes = {}
        for arm in e.ARMS:
            base = output / arm
            base.mkdir()
            prefix = base / 'prefix'
            result['stage'] = 'build-' + arm
            for component in ('holonight-images', 'holonight-thumbnails', 'holonight-file-browser'):
                source = package / arm / 'source' / component
                native = base / 'build' / component
                options = ['-DHOLONIGHT_IMAGES_ISOLATED=ON', '-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE=' + str(base / 'runtime')] if component == 'holonight-images' else (
                    ['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON'] if component == 'holonight-thumbnails' else
                    ['-DBUILD_FILE_BROWSER_' + n + '=OFF' for n in ('QUICK', 'SEARCH', 'STORAGE', 'PREVIEW_QUICK', 'MARKDOWN')])
                command(['cmake', '-S', source, '-B', native, '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release',
                         '-DBUILD_TESTING=OFF', '-DCMAKE_INSTALL_PREFIX=' + str(prefix), '-DCMAKE_PREFIX_PATH=' + str(prefix), *options],
                         base, component + '-configure')
                command(['cmake', '--build', native, '--parallel', '4'], base, component + '-compile')
                if component == 'holonight-images':
                    command([sys.executable, source / 'scripts/prepare-isolated-runtime.py', '--helper',
                        native / 'holonight-images-helper', '--plugins', '/usr/lib/qt6/plugins', '--output', base / 'runtime'], base, 'runtime')
                command(['cmake', '--install', native], base, component + '-install')
            command(['cmake', '-S', package / arm / 'harness-source', '-B', base / 'reuse-harness', '-G', 'Ninja',
                '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(prefix), '-DPREVIEW_REUSE_BENCHMARK=ON',
                '-DREUSABLE_VARIANT=ON'], base, 'harness-configure')
            command(['cmake', '--build', base / 'reuse-harness', '--parallel', '4'], base, 'harness-compile')
            cache = (base / 'reuse-harness/CMakeCache.txt').read_text()
            resolution = {}
            for line in cache.splitlines():
                if line.startswith(('HolonightImages_DIR:', 'HolonightThumbnails_DIR:', 'HolonightFileBrowser_DIR:')):
                    key, path = line.split('=', 1)
                    resolution[key.split(':')[0]] = path
            h.require(len(resolution) == 3 and all(Path(p).is_relative_to(prefix) for p in resolution.values()), 'installed provider resolution')
            h.write(base / 'package-resolution.json', resolution)
            identities = {}
            for label, path in [('helper', base / 'build/holonight-images/holonight-images-helper'),
                                 ('harness', base / 'reuse-harness/preview-benchmark')]:
                identities[label] = dict(sha256=h.digest(path), build_id=e.r.e.elf_id(path))
                linkage = command(['ldd', path], base, label + '-linkage')
                h.require('not found' not in linkage, 'unresolved dependency')
                for line in linkage.splitlines():
                    tokens = line.split()
                    path = tokens[2] if len(tokens) > 2 and tokens[1] == '=>' else tokens[0] if tokens else ''
                    if path.startswith('/'):
                        resolved = str(Path(path).resolve())
                        e.r.merge(dependency_paths, {resolved: h.digest(Path(resolved))})
            h.write(base / 'identities.json', identities)
            runtime = h.inventory(base / 'runtime')
            h.write(base / 'runtime-inventory.json', runtime)
            runtimes[arm] = e.r.e.payload(base / 'runtime', runtime)
            # Separate test build: timed providers retain BUILD_TESTING=OFF.
            test_build = base / 'correctness-build'
            source = package / arm / 'source/holonight-images'
            command(['cmake', '-S', source, '-B', test_build, '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release',
                '-DBUILD_TESTING=ON', '-DHOLONIGHT_IMAGES_ISOLATED=ON',
                '-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE=' + str(base / 'runtime')], base, 'correctness-configure')
            command(['cmake', '--build', test_build, '--parallel', '4', '--target', 'isolated-verification-test',
                'isolated-generation-test', 'isolated-cleanup-test', 'holonight-images-helper'], base, 'correctness-compile')
            command(['ctest', '--test-dir', test_build, '--output-on-failure', '-R',
                '^(isolated-verification|isolated-generation|isolated-cleanup|isolated-installed-package)$'], base, 'correctness-tests')
        flags = command(['pkg-config', '--cflags', '--libs', 'Qt6Core'], output, 'loop-flags').split()
        command(['c++', '-std=c++23', '-O3', '-fPIC', package / 'tools/hash-loop-test.cpp',
            '-I' + str(package / 'tools'), '-o', output / 'hash-loop-test', *flags], output, 'loop-compile')
        command([output / 'hash-loop-test'], output, 'loop-tests', timeout=30)
        changed = [n for n in runtimes['control'] if runtimes['control'][n] != runtimes['candidate'].get(n)]
        h.require(runtimes['control'].keys() == runtimes['candidate'].keys() and
                  set(changed) <= {'usr/libexec/holonight-images-helper'}, 'unexplained runtime difference')
        h.write(output / 'runtime-comparison.json', dict(changed=changed,
            explanation='Only the candidate helper and corresponding manifest identity may differ.'))
        h.write(output / 'host-dependencies.json', dependency_paths)
        h.write(output / 'correctness.json', dict(passed=True, arms=list(e.ARMS),
            checks=['runtime verification', 'generation', 'cleanup', 'installed consumer', 'actual candidate loop']))
        e.check_package(package)
        result.update(status='built', stage='complete')
    return action(output, [package], work)


def worker(request, cleanup):
    config = h.read(request)
    built, runtime, output = [Path(config[k]) for k in ('built', 'runtime', 'execution')]
    import hashlib
    expected_name = 'holonight-streaming-' + hashlib.sha256(str(output).encode()).hexdigest()[:20]
    h.require(os.geteuid() == 0 and runtime == Path('/run') / expected_name, 'invalid staging worker')
    h.require(runtime.parent == Path('/run') and runtime.name.startswith('holonight-streaming-') and
              runtime.resolve() == runtime and output.resolve() == output, 'unsafe protected path')
    e.check_built(built)
    h.require(h.digest(built / 'seal.json') == config['seal'], 'worker build identity')
    h.require(h.digest(built / 'tools/run-preview-streaming-trial.py') == h.digest(Path(__file__)), 'worker tool identity')
    sys.path.insert(0, str(built / 'tools'))
    spec = importlib.util.spec_from_file_location('streaming_installer', built / 'tools/manage-images-generations.py')
    installer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installer)
    owner = dict(built=str(built), seal=config['seal'], execution=str(output))
    if cleanup:
        h.require(h.read(runtime / 'diagnostic-owner.json') == owner and
                  e.r.e.tree(runtime) == h.read(output / 'cleanup-expected.json'), 'cleanup ownership/drift')
        for arm in e.ARMS:
            installer.run(SimpleNamespace(command='remove', runtime=runtime / arm,
                helper=built / arm / 'runtime/usr/libexec/holonight-images-helper', source=None,
                ownership_manifest=None, maintenance_migrate=False))
        installer.remove_tree(runtime)
    else:
        h.require(not os.path.lexists(runtime), 'protected staging collision')
        installer.chain(runtime.parent)
        runtime.mkdir(mode=0o755)
        h.write(runtime / 'diagnostic-owner.json', owner)
        for arm in e.ARMS:
            installer.run(SimpleNamespace(command='install', runtime=runtime / arm, source=built / arm / 'runtime',
                helper=built / arm / 'runtime/usr/libexec/holonight-images-helper', ownership_manifest=None,
                maintenance_migrate=False))
    h.write(output / ('cleanup-worker.json' if cleanup else 'stage-worker.json'), dict(passed=True))


def execute(built, output):
    def work(result):
        import hashlib
        old = load('streaming_process_support', 'run-preview-identity-baseline.py')
        cpu = load('streaming_process', 'run-preview-cpu-profile.py')
        package = e.check_built(built)
        e.check_package(package, provenance=True)
        h.require(os.geteuid() == 1000, 'ordinary desktop user required')
        marker = built.with_name(built.name + '-execution-started.json')
        with marker.open('x') as stream:
            h.json.dump(dict(output=str(output)), stream)
        runtime = Path('/run') / ('holonight-streaming-' + hashlib.sha256(str(output).encode()).hexdigest()[:20])
        h.require(not os.path.lexists(runtime), 'runtime collision')
        h.write(output / 'built.json', dict(path=str(built), seal=h.digest(built / 'seal.json')))
        h.write(output / 'protocol.json', protocol())
        h.write(output / 'environment.json', dict(host=list(os.uname()), environment=environment(cpu.offline_env()),
            affinity=sorted(os.sched_getaffinity(0)), boot_id=Path('/proc/sys/kernel/random/boot_id').read_text()))
        request = output / 'stage-request.json'
        h.write(request, dict(built=str(built), seal=h.digest(built / 'seal.json'), runtime=str(runtime),
                              runtime_name=runtime.name, execution=str(output)))
        backend = old.NativeBackend(package, None)
        backend.cpu = cpu
        def elevated(action):
            # Credential acquisition is separate from workload timing and separately repeated for cleanup.
            backend.authorize(action, output)
            argv = ['sudo', '-n', sys.executable, '-B', str(Path(__file__).resolve()), action, '--request', str(request)]
            with (output / (action + '.log')).open('x') as log:
                completed, interrupted = old.wait_elevated(argv, stdout=log, stderr=subprocess.STDOUT)
            h.write(output / (action + '-execution.json'), dict(argv=argv, exit=completed.returncode,
                      worker_reaped=True, interrupted=interrupted))
            completed.check_returncode()
            h.require(not interrupted, 'interrupted after privileged worker reaped')
        rows = []
        result.update(attempted=0, unexecuted=schedule(), cleanup_verified=False)
        outer = None
        # Fixed complete schedule, including future entries, retained before any launch.
        commands = [dict(schedule=row, argv=[str(built / row['arm'] / 'reuse-harness/preview-benchmark'),
            str(runtime / row['arm']), str(package / '3200x2400.png'), 'startup', '1',
            str(output / f"{row['index']:03}" / 'harness.json')]) for row in schedule()]
        h.write(output / 'commands.json', commands)
        try:
            backend.isolation(output / 'initial-isolation')
            elevated('stage')
            outer = e.r.e.tree(runtime)
            h.require(all(v['uid'] == 0 and not v['mode'] & 0o022 for v in outer.values()), 'unprotected staged inode')
            h.write(output / 'staged-outer.json', outer)
            h.write(output / 'cleanup-expected.json', outer)
            for arm in e.ARMS:
                generation = (runtime / arm / 'current').read_text().strip()
                h.require(generation and '/' not in generation and generation not in ('.', '..'), 'selector')
                h.require(h.inventory(runtime / arm / 'generations' / generation) ==
                          h.read(built / arm / 'runtime-inventory.json'), 'staged payload mismatch')
            for entry in commands:
                h.sealed(package)
                h.sealed(built)
                h.require(e.tools() == h.read(built / 'tools.json'), 'live tool drift')
                h.require(e.r.e.tree(runtime) == outer, 'staged identity drift')
                for path, digest in h.read(built / 'host-dependencies.json').items():
                    h.require(h.digest(Path(path)) == digest, 'host dependency drift')
                arm = entry['schedule']['arm']
                for name, relative in [('harness', 'reuse-harness/preview-benchmark'),
                                       ('helper', 'build/holonight-images/holonight-images-helper')]:
                    h.require(h.digest(built / arm / relative) == h.read(built / arm / 'identities.json')[name]['sha256'], 'binary drift')
                directory = output / f"{entry['schedule']['index']:03}"
                directory.mkdir(mode=0o700)
                backend.isolation(directory / 'before')
                result['attempted'] += 1
                h.write(output / 'progress.json', result)
                target = directory / 'harness.json'
                process = cpu.workload(entry['argv'], target, False)
                partial = h.read(directory / 'harness-recording/partial.json')
                backend.isolation(directory / 'after', deadline=partial['cleanup_deadline'])
                cleanup_stop = time.monotonic()
                h.write(directory / 'cleanup.json', dict(stopped=cleanup_stop, deadline=partial['cleanup_deadline']))
                h.require(partial['cleanup_outcomes']['passed'] and partial['gate_reaped'] and
                    not partial['timeout'] and cleanup_stop <= partial['cleanup_deadline'], 'shared cleanup failure')
                h.require(process['exit'] == 0 and not process['timeout'] and
                    (process['stop_ns'] - process['start_ns']) / 1e9 <= 30, 'workload deadline/failure')
                value = e.sample(h.read(target))
                rows.append(dict(schedule=entry['schedule'], sample=value,
                    cleanup_seconds=cleanup_stop - (partial['cleanup_deadline'] - 5)))
                h.write(output / 'observations.json', rows)
                print(f"{len(rows)}/202 passed", flush=True)
            result['status'] = 'complete'
        finally:
            result['unexecuted'] = schedule()[result['attempted']:]
            try:
                backend.isolation(output / 'final-isolation')
                if runtime.exists():
                    h.require(outer is not None and e.r.e.tree(runtime) == outer, 'partial/changed staging retained')
                    elevated('cleanup')
                h.require(not runtime.exists(), 'staging cleanup incomplete')
                e.check_built(built)
                e.check_package(package)
                result['cleanup_verified'] = True
            except ERRORS as error:
                result.update(status='blocked', cleanup_failure=str(error))
            h.write(output / 'observations.json', rows)
            complete = result['status'] == 'complete' and len(rows) == 202 and result['cleanup_verified']
            summary = summarize(rows, complete)
            h.write(output / 'statistics.json', summary)
            result.update(accepted=len(rows), decision=summary['decision'], stage='complete' if complete else 'execution')
            lines = ['# Private 64 KiB streaming startup trial', '',
                'Assessment: ' + ('complete' if complete else 'incomplete'), '', 'Decision: ' + summary['decision'], '',
                '| Arm | Endpoint | Median ms | p95 ms |', '|---|---|---:|---:|']
            for arm, events in summary['populations'].items():
                for event, stats in events.items():
                    if stats: lines.append(f"| {arm} | {event} | {stats['median']:.6f} | {stats['p95']:.6f} |")
            lines += ['', 'Block differences are candidate minus control; signs are descriptive only (statistics.json).', '',
                'New host-native builds and input identities establish no historical or uncaptured loading identity. '
                'No historical timing transfer, overhead correction, or revision of 78/80. '
                'A favorable decision authorizes no production change.', '']
            (output / 'REPORT.md').write_text('\n'.join(lines))
    return action(output, [built], work)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'build', 'execute', 'stage', 'cleanup'))
    for name in ('package', 'built', 'request', 'output'):
        parser.add_argument('--' + name, type=Path)
    args = parser.parse_args()
    if args.action in ('stage', 'cleanup'):
        worker(args.request.absolute(), args.action == 'cleanup')
    else:
        h.require(args.output is not None, '--output required')
        if args.action == 'prepare': result = prepare(args.output.absolute())
        elif args.action == 'build':
            h.require(args.package is not None, '--package required')
            result = build(args.package.absolute(), args.output.absolute())
        else:
            h.require(args.built is not None, '--built required')
            result = execute(args.built.absolute(), args.output.absolute())
        print(h.json.dumps(result, indent=2))
        sys.exit(result['status'] not in ('prepared', 'built', 'complete'))
