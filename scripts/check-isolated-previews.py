#!/usr/bin/env python3
"""Host-native application preview acceptance against an explicit installed prefix."""
import argparse
import os
import json
import shutil
import time
from pathlib import Path
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]


def png(color):
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', 160, 80, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress((b'\0' + bytes(color) * 160) * 80)) + chunk(b'IEND', b''))


def run(command, env, output, name, timeout=600):
    record = {'command': command, 'environment': {key: env[key] for key in env if key.startswith(('XDG_', 'QT_', 'QML_', 'LD_'))}}
    started = time.monotonic()
    try:
        with (output / (name + '.log')).open('w') as log:
            result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
        record['returncode'] = result.returncode
        if result.returncode:
            raise RuntimeError(f'{name} failed ({result.returncode}); see {output / (name + ".log")}')
    except Exception as error:
        record['error'] = str(error)
        raise
    finally:
        record['seconds'] = time.monotonic() - started
        (output / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
    print(f'{name}: passed', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('prefix', 'runtime', 'test-runtime', 'files', 'files-tests', 'unknown-tests', 'portal', 'provider', 'fixtures', 'output'):
        parser.add_argument('--' + name, type=lambda value: Path(value).resolve(), required=True)
    args = parser.parse_args()
    runtime = args.runtime
    for path in (runtime / 'manifest.json', args.prefix / 'lib/cmake/HolonightFileBrowser/HolonightFileBrowserConfig.cmake',
                 args.files, args.files_tests, args.unknown_tests, args.portal, args.provider,
                 args.test_runtime / 'manifest.json', args.fixtures / 'sample.png'):
        if not path.exists():
            parser.error(f'Required runtime, executable or provider fixture missing: {path}')
    if args.prefix in (Path('/'), Path('/usr'), Path('/usr/local')):
        parser.error('Use a disposable staged prefix; relocation temporarily hides it')
    if args.test_runtime.is_relative_to(args.prefix):
        parser.error('Synthetic test runtime must remain outside the installed prefix')
    if args.output.is_relative_to(args.prefix):
        parser.error('Evidence must be outside the staged prefix')
    if not args.runtime.is_relative_to(args.prefix):
        parser.error('Production runtime must be inside the staged prefix for relocation')
    args.output.mkdir(parents=True, exist_ok=False)
    # Preserve evidence even when prerequisites fail. Images needs the real user bus.
    run(['systemctl', '--user', 'show', '--property=Version', '--value'], os.environ.copy(), args.output, 'user-manager', 15)
    if not Path('/sys/fs/cgroup/cgroup.controllers').is_file():
        raise RuntimeError('Unified cgroup support required')
    run(['bwrap', '--unshare-user', '--unshare-pid', '--ro-bind', '/usr', '/usr',
         '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib', '/lib64',
         '--proc', '/proc', '--dev', '/dev', '/usr/bin/true'], os.environ.copy(), args.output, 'namespaces', 15)
    fixtures = args.output / 'fixtures'
    fixtures.mkdir()
    (fixtures / '01-red.png').write_bytes(png((255, 0, 0)))
    (fixtures / '02-blue.png').write_bytes(png((0, 0, 255)))
    (fixtures / '03-vector.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="160" height="80">'
                                         '<rect width="160" height="80" fill="#00ff00"/></svg>')
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
               QML_IMPORT_PATH=str(args.prefix / 'lib/qt6/qml'),
               LD_LIBRARY_PATH=str(args.prefix / 'lib'), QT_QPA_PLATFORMTHEME='', QT_FORCE_STDERR_LOGGING='1',
               XDG_CONFIG_HOME=str(args.output / 'config'), XDG_DATA_HOME=str(args.output / 'data'), XDG_STATE_HOME=str(args.output / 'state'))
    private_bus = ['python3', str(ROOT / 'xdg-desktop-portal-holonight/scripts/private-bus.py'),
                   '--config', str(ROOT / 'xdg-desktop-portal-holonight/tests/dbus-session.conf'), '--']
    def acceptance(prefix, phase):
        runtime = prefix / args.runtime.relative_to(args.prefix)
        environment = dict(env, QML_IMPORT_PATH=str(prefix / 'lib/qt6/qml'), LD_LIBRARY_PATH=str(prefix / 'lib'))
        commands = {
            'provider': [str(args.provider), str(runtime), str(args.fixtures)],
            'unknown-trap': ['python3', str(ROOT / 'holonight-files/scripts/test-lane.py'),
                '--framework', 'gtest', '--inventory', str(ROOT / 'holonight-files/tests/unknown-dimensions-lanes.json'),
                '--lane', 'portable', '--', str(args.unknown_tests)],
            'unknown-dimensions': ['python3', str(ROOT / 'holonight-files/scripts/test-lane.py'),
                '--framework', 'gtest', '--inventory', str(ROOT / 'holonight-files/tests/unknown-dimensions-lanes.json'),
                '--lane', 'host', '--runtime', str(args.test_runtime), '--', str(args.unknown_tests)],
            'files-tests': ['python3', str(ROOT / 'holonight-files/scripts/test-lane.py'),
                '--framework', 'gtest', '--inventory', str(ROOT / 'holonight-files/tests/lanes.json'),
                '--lane', 'host', '--runtime', str(runtime), '--', str(args.files_tests)],
            'files-observer': ['python3', str(ROOT / 'holonight-files/scripts/check-native-observer.py'),
                str(args.files), str(runtime)],
            'files-rendered': [str(args.files), '--verify-isolated-preview', '--image-runtime', str(runtime), str(fixtures)],
            'portal': ['python3', str(ROOT / 'xdg-desktop-portal-holonight/scripts/test-lane.py'),
                '--framework', 'qt', '--inventory', str(ROOT / 'xdg-desktop-portal-holonight/tests/lanes.json'),
                '--lane', 'host', '--runtime', str(runtime), '--', *private_bus,
                str(args.portal), '--fixtures', str(fixtures)],
        }
        for name, command in commands.items():
            name = phase + '-' + name
            isolated_env = dict(environment)
            for key in ('CONFIG', 'CACHE', 'DATA', 'STATE'):
                isolated_env['XDG_' + key + '_HOME'] = str(args.output / name / key.lower())
            command = [str(prefix / Path(part).relative_to(args.prefix))
                       if Path(part).is_absolute() and Path(part).is_relative_to(args.prefix) else part
                       for part in command]
            run(command, isolated_env, args.output, name)

    acceptance(args.prefix, 'staged')
    relocated = args.output / 'relocated-prefix'
    shutil.copytree(args.prefix, relocated, symlinks=True)
    hidden = args.prefix.with_name(args.prefix.name + '.acceptance-hidden')
    if hidden.exists():
        raise RuntimeError(f'Refusing existing relocation backup: {hidden}')
    args.prefix.rename(hidden)
    try:
        if args.prefix.exists():
            raise RuntimeError('Original prefix remains available')
        acceptance(relocated, 'relocated')
    finally:
        hidden.rename(args.prefix)
    (args.output / 'complete.json').write_text(json.dumps({'staged': True, 'relocated': True}) + '\n')


if __name__ == '__main__':
    main()
