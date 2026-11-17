#!/usr/bin/env python3
"""Build the frozen native package; failures end this attempt without source repair."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import evidence as e

h = e.h
ERRORS = (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, KeyboardInterrupt)


def command(argv, output, name):
    argv = [str(v) for v in argv]
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen', CMAKE_BUILD_PARALLEL_LEVEL='4')
    record = dict(argv=argv, cwd=str(e.ROOT), timeout_seconds=600,
        environment={k: v for k, v in env.items() if k in
            ('PATH', 'CC', 'CXX', 'CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'CMAKE_PREFIX_PATH',
             'PKG_CONFIG_PATH', 'LD_LIBRARY_PATH', 'QT_QPA_PLATFORM', 'CMAKE_BUILD_PARALLEL_LEVEL',
             'HOLONIGHT_CACHE_INVOCATION', 'PUBLICATION_ARM', 'XDG_CACHE_HOME', 'TMPDIR')})
    h.write(output / (name + '-command.json'), record)
    result = dict(start_ns=time.monotonic_ns(), exit=None, failure=None)
    try:
        with (output / (name + '.stdout')).open('x') as stdout, (output / (name + '.stderr')).open('x') as stderr:
            process = subprocess.run(argv, cwd=e.ROOT, env=env, stdout=stdout, stderr=stderr, timeout=600)
        result['exit'] = process.returncode
        process.check_returncode()
    except ERRORS as error:
        result['failure'] = str(error) or type(error).__name__
        raise
    finally:
        result['stop_ns'] = time.monotonic_ns()
        h.write(output / (name + '-result.json'), result)


def action(output, phase, work):
    h.fresh(output, [e.PACKAGE, Path(__file__).parent, e.ROOT / 'tests'])
    result = dict(status='blocked', phase=phase, decision='Evidence insufficient',
        attempted=0, unexecuted=e.historical.protocol()['schedule'], native_correctness='unvalidated',
        staging='not attempted', loading_evidence='unavailable: no workload launched')
    try:
        identities = e.tools()
        (output / 'tools').mkdir()
        for path in identities:
            shutil.copyfile(path, output / 'tools' / Path(path).name)
        h.write(output / 'tools.json', identities)
        h.write(output / 'package.json', e.package())
        h.write(output / 'protocol.json', e.historical.protocol())
        work(result)
        h.require(e.tools() == identities, 'execution tooling drift')
        h.require(e.package() == h.read(output / 'package.json'), 'package drift')
    except ERRORS as error:
        result['failure'] = str(error) or type(error).__name__
    finally:
        try:
            unchanged = e.package() == h.read(output / 'package.json') and e.tools() == h.read(output / 'tools.json')
        except ERRORS:
            unchanged = False
        h.write(output / 'integrity.json', dict(unchanged=unchanged))
        if not unchanged:
            result.update(status='blocked', failure=result.get('failure', 'input drift'))
        h.write(output / 'assessment.json', result)
        (output / 'REPORT.md').write_text('# Private cache publication attempt\n\n' + result['status'] +
            ': ' + result.get('failure', '') + '\n\nDecision: Evidence insufficient.\n\n' +
            'No performance or visible rendering claim. Streaming and validation reuse Deferred; '
            'candidate selection Evidence insufficient; qualification 78/80 unchanged.\n')
        h.write(output / 'seal.json', h.inventory(output))
    return result


def build(output):
    def work(result):
        h.write(output / 'host.json', dict(uname=list(os.uname()), jobs=4, build_type='Release'))
        for name, argv in [('compiler', ['c++', '--version']), ('cmake', ['cmake', '--version']),
                           ('dependencies', ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp'])]:
            command(argv, output, name)
        for arm in ('control', 'early'):
            base = output / arm
            base.mkdir()
            prefix = base / 'prefix'
            for component in ('holonight-images', 'holonight-thumbnails', 'holonight-file-browser'):
                result['stage'] = arm + '/' + component
                source = e.PACKAGE / arm / 'source' / component
                native = base / 'build' / component
                options = (['-DHOLONIGHT_IMAGES_ISOLATED=ON', '-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE=' + str(base / 'runtime')]
                    if component == 'holonight-images' else ['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON']
                    if component == 'holonight-thumbnails' else
                    ['-DBUILD_FILE_BROWSER_' + n + '=OFF' for n in ('QUICK', 'SEARCH', 'STORAGE', 'PREVIEW_QUICK', 'MARKDOWN')])
                command(['cmake', '-S', source, '-B', native, '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release',
                    '-DBUILD_TESTING=OFF', '-DCMAKE_INSTALL_PREFIX=' + str(prefix),
                    '-DCMAKE_PREFIX_PATH=' + str(prefix), *options], base, component + '-configure')
                command(['cmake', '--build', native, '--parallel', '4'], base, component + '-compile')
                if component == 'holonight-images':
                    command([sys.executable, source / 'scripts/prepare-isolated-runtime.py', '--helper',
                        native / 'holonight-images-helper', '--plugins', '/usr/lib/qt6/plugins',
                        '--output', base / 'runtime'], base, 'runtime')
                command(['cmake', '--install', native], base, component + '-install')
            command(['cmake', '-S', e.PACKAGE / arm / 'harness-source', '-B', base / 'harness-build',
                '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(prefix),
                '-DPREVIEW_REUSE_BENCHMARK=ON', '-DREUSABLE_VARIANT=ON'], base, 'harness-configure')
            command(['cmake', '--build', base / 'harness-build', '--parallel', '4'], base, 'harness-compile')
        raise ValueError('native correctness gates not yet validated; execution prohibited')
    return action(output, 'build', work)


def execute(built, output):
    def work(result):
        h.sealed(built)
        h.write(output / 'built.json', dict(path=str(built), seal=h.digest(built / 'seal.json')))
        h.require(h.read(built / 'assessment.json')['status'] == 'built', 'blocked native build; no observations permitted')
        raise ValueError('native correctness gates not yet validated; execution prohibited')
    return action(output, 'execute', work)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('build').add_argument('--output', type=Path, required=True)
    execution = sub.add_parser('execute')
    execution.add_argument('--built', type=Path, required=True)
    execution.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.output.absolute()) if args.action == 'build' else execute(args.built.absolute(), args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] == 'blocked')
