#!/usr/bin/env python3
"""Private candidate-publication trial preparation and host-native builds."""
import argparse
import difflib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import contract as t
h = t.h
ERRORS = (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, KeyboardInterrupt)


def snapshot(output):
    identities = t.tools()
    (output / 'tools').mkdir()
    for path in identities:
        shutil.copyfile(path, output / 'tools' / t.snapshot_name(path))
    h.write(output / 'tools.json', identities)
    return identities


def action(output, expected, inputs, work):
    h.require(output == expected and output == output.resolve() and not os.path.lexists(output),
              'fresh fixed trial destination required')
    h.fresh(output, inputs)
    result = dict(status='blocked', decision='Evidence insufficient', attempted=[], completed=[])
    tools = {}
    try:
        tools = snapshot(output)
        work(result)
        h.require(t.tools() == tools, 'tool drift')
    except ERRORS as error:
        result.update(status='blocked', failure=str(error) or type(error).__name__)
    finally:
        unchanged = bool(tools) and t.tools() == tools
        if not unchanged:
            result.update(status='blocked', failure=result.get('failure', 'tool drift'))
        h.write(output / 'integrity.json', dict(unchanged=unchanged))
        h.write(output / 'assessment.json', result)
        (output / 'REPORT.md').write_text('# Early publication trial\n\n' + result['status'] + ': ' +
            result.get('failure', '') + '\n\nDecision: Evidence insufficient. Historical qualification 78/80 unchanged.\n')
        h.write(output / 'seal.json', h.inventory(output))
    return result


def prepare(output):
    t.prerequisite()
    def work(result):
        binding = t.prerequisite()
        h.write(output / 'binding.json', binding)
        h.write(output / 'protocol.json', t.protocol())
        retained = binding['retained']
        shutil.copyfile(retained['fixture']['path'], output / '3200x2400.png')
        for arm in t.ARMS:
            shutil.copytree(t.Q / 'C/source', output / arm / 'source')
            shutil.copytree(t.Q / 'harness-source', output / arm / 'harness-source')
            reuse = output / arm / 'harness-source/reuse.cpp'
            reuse.write_text(t.harness(reuse.read_text()))
        source = output / 'candidate/source' / t.SERVICE
        before = source.read_text()
        after = t.transform(before)
        source.write_text(after)
        (output / 'candidate.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
            fromfile='control/' + t.SERVICE, tofile='candidate/' + t.SERVICE)))
        h.require(t.prerequisite() == binding, 'retained input drift')
        result['status'] = 'prepared'
    return action(output, t.PREPARED, [t.Q, t.HISTORICAL, t.DIRECTORY], work)


def build_commands(package, output):
    rows = []
    def add(name, argv):
        rows.append(dict(name=name, argv=[str(v) for v in argv], environment=t.environment(),
            timeout_seconds=30 if name.endswith('-linkage') or name in ('compiler','cmake','dependencies') else 600, cwd=str(t.ROOT), launch=dict(start_new_session=True)))
    add('compiler', ['c++', '--version'])
    add('cmake', ['cmake', '--version'])
    add('dependencies', ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp'])
    # Compile Images and Thumbnails once. Install their identical package bytes into each arm.
    common = output / 'common'
    for component in ('holonight-images',):
        source = package / 'control/source' / component
        native = common / 'build' / component
        options = ['-DHOLONIGHT_IMAGES_ISOLATED=ON', '-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE=' + str(common / 'runtime')] if component == 'holonight-images' else ['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON']
        add(component + '-configure', ['cmake', '-S', source, '-B', native, '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=OFF', '-DCMAKE_INSTALL_PREFIX=' + str(common / 'prefix'),
            '-DCMAKE_PREFIX_PATH=' + str(common / 'prefix'), *options])
        add(component + '-compile', ['cmake', '--build', native, '--parallel', '4'])
        if component == 'holonight-images':
            add('runtime', [sys.executable, source / 'scripts/prepare-isolated-runtime.py', '--helper',
                native / 'holonight-images-helper', '--plugins', '/usr/lib/qt6/plugins', '--output', common / 'runtime'])
        add(component + '-install', ['cmake', '--install', native])
    for arm in t.ARMS:
        base = output / arm
        protected = Path('/run') / ('holonight-directional-' + __import__('hashlib').sha256(str(t.CORRECTNESS).encode()).hexdigest()[:20] + '-' + arm)
        prefix = base / 'prefix'
        thumb = base / 'build/holonight-thumbnails'
        add(arm + '-thumbnails-configure', ['cmake','-S',package / arm / 'source/holonight-thumbnails','-B',thumb,'-G','Ninja',
            '-DCMAKE_BUILD_TYPE=Release','-DBUILD_TESTING=ON','-DHOLONIGHT_THUMBNAILS_ISOLATED=ON',
            '-DCMAKE_INSTALL_PREFIX='+str(prefix),'-DCMAKE_PREFIX_PATH='+str(prefix),
            '-DHOLONIGHT_THUMBNAILS_TEST_RUNTIME='+str(protected)])
        add(arm + '-thumbnails-compile', ['cmake','--build',thumb,'--parallel','4'])
        add(arm + '-thumbnails-install', ['cmake','--install',thumb])
        source = package / arm / 'source/holonight-file-browser'
        native = base / 'build/holonight-file-browser'
        prefix = base / 'prefix'
        add(arm + '-browser-configure', ['cmake', '-S', source, '-B', native, '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=ON', '-DCMAKE_INSTALL_PREFIX=' + str(prefix),
            '-DHOLONIGHT_FILE_BROWSER_TEST_RUNTIME='+str(protected),
            '-DHOLONIGHT_FILE_BROWSER_TEST_FIXTURES='+str(t.CORRECTNESS/'fixtures'),
            '-DCMAKE_PREFIX_PATH=' + str(prefix),
            *['-DBUILD_FILE_BROWSER_' + n + '=OFF' for n in ('QUICK', 'SEARCH', 'STORAGE', 'PREVIEW_QUICK', 'MARKDOWN')]])
        add(arm + '-browser-compile', ['cmake', '--build', native, '--parallel', '4'])
        add(arm + '-browser-install', ['cmake', '--install', native])
        add(arm + '-harness-configure', ['cmake', '-S', package / arm / 'harness-source', '-B', base / 'harness-build',
            '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(prefix),
            '-DPREVIEW_REUSE_BENCHMARK=ON', '-DREUSABLE_VARIANT=ON'])
        add(arm + '-harness-compile', ['cmake', '--build', base / 'harness-build', '--parallel', '4'])
        add(arm + '-linkage', ['ldd', base / 'harness-build/preview-benchmark'])
    return rows


def command(row, output):
    target = output / 'commands'
    target.mkdir(exist_ok=True)
    name = row['name']
    h.write(target / (name + '-command.json'), row)
    result = dict(start_ns=time.monotonic_ns(), exit=None, failure=None, cleanup=False)
    process = None
    try:
        with (target / (name + '.stdout')).open('x') as out, (target / (name + '.stderr')).open('x') as err:
            process = subprocess.Popen(row['argv'], cwd=row['cwd'], env=row['environment'],
                stdout=out, stderr=err, **row['launch'])
            result['exit'] = process.wait(timeout=row['timeout_seconds'])
            h.require(result['exit'] == 0, 'command failed: ' + name)
    except ERRORS as error:
        result['failure'] = str(error) or type(error).__name__
    finally:
        try:
            start = time.monotonic()
            deadline = start + 5
            if process is not None:
                cleanup = t.e.load('trial_build_cleanup', t.ROOT / 'scripts/run-preview-cpu-profile.py')
                cleanup.terminate(process, deadline=deadline)
                try:
                    os.killpg(process.pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    raise ValueError('build process group survived')
            result['cleanup_seconds'] = time.monotonic() - start
            h.require(time.monotonic() <= deadline, 'cleanup deadline exceeded')
            result['cleanup'] = True
        except ERRORS as error:
            result['failure'] = result['failure'] or str(error)
        result['stop_ns'] = time.monotonic_ns()
        h.write(target / (name + '-result.json'), result)
    h.require(result['failure'] is None and result['cleanup'], result['failure'] or 'cleanup failed')


def build(package, output):
    t.prerequisite()
    t.phase_proof(package, 'prepared')
    def work(result):
        verifier = t.e.load('trial_preparation_verifier', t.DIRECTORY / 'offline/verify.py')
        h.require(verifier.verify(package)['outcome'] == 'prepared', 'verified preparation required')
        h.write(output / 'package.json', dict(path=str(package), seal=h.digest(package / 'seal.json')))
        h.write(output / 'environment.json', dict(host=list(os.uname()), environment=t.environment(), jobs=4,
            affinity=sorted(os.sched_getaffinity(0)), boot_id=Path('/proc/sys/kernel/random/boot_id').read_text()))
        rows = build_commands(package, output)
        h.write(output / 'schedule.json', rows)
        for row in rows:
            h.require(t.tools() == h.read(output / 'tools.json'), 'tool drift')
            if row['name'].endswith('-thumbnails-configure'):
                arm = row['name'].split('-')[0]
                shutil.copytree(output / 'common/prefix', output / arm / 'prefix')
                shutil.copytree(output / 'common/runtime', output / arm / 'runtime')
            result['attempted'].append(row['name'])
            command(row, output)
            result['completed'].append(row['name'])
            print(row['name'] + ' passed', flush=True)
        h.require(verifier.verify(package)['outcome'] == 'prepared', 'preparation drift')
        result['status'] = 'built'
    h.require(package == t.PREPARED, 'fixed prepared input required')
    return action(output, t.BUILT, [package, t.DIRECTORY], work)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('prepare').add_argument('--output', type=Path, required=True)
    p = sub.add_parser('build')
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output.absolute()) if args.action == 'prepare' else build(args.package.absolute(), args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] not in ('prepared', 'built'))
