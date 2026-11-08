#!/usr/bin/env python3
"""Host-native application preview acceptance against an explicit installed prefix."""
import argparse
import os
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('prefix', 'runtime', 'files', 'portal', 'fixtures', 'output'):
        parser.add_argument('--' + name, type=lambda value: Path(value).resolve(), required=True)
    args = parser.parse_args()
    runtime = args.runtime
    for path in (runtime / 'manifest.json', args.prefix / 'lib/cmake/HolonightFileBrowser/HolonightFileBrowserConfig.cmake',
                 args.files, args.portal, args.fixtures / 'sample.png'):
        if not path.exists():
            parser.error(f'Required runtime, executable or provider fixture missing: {path}')
    # Fail early; do not replace the real session bus with the portal's test bus.
    subprocess.run(['systemctl', '--user', 'show-environment'], stdout=subprocess.DEVNULL, check=True)
    subprocess.run(['bwrap', '--unshare-user', '--unshare-pid', '--ro-bind', '/usr', '/usr',
                    '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib', '/lib64',
                    '--proc', '/proc', '--dev', '/dev', '/usr/bin/true'], check=True)
    args.output.mkdir(parents=True, exist_ok=False)
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
    commands = {
        'files': [str(args.files), '--verify-isolated-preview', '--image-runtime', str(runtime), str(fixtures)],
        'portal': ['python3', str(ROOT / 'xdg-desktop-portal-holonight/scripts/private-bus.py'),
                   '--config', str(ROOT / 'xdg-desktop-portal-holonight/tests/dbus-session.conf'), '--',
                   str(args.portal), 'isolatedPreviewPresentation', 'isolatedPreviewErrors', '--image-runtime', str(runtime),
                   '--fixtures', str(fixtures)],
    }
    for name, command in commands.items():
        env['XDG_CACHE_HOME'] = str(args.output / (name + '-cache'))
        with (args.output / (name + '.log')).open('w') as log:
            result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=120)
        if result.returncode:
            raise RuntimeError(f'{name} acceptance failed ({result.returncode}); see {args.output / (name + ".log")}')
        print(f'{name}: rendered presentation passed', flush=True)


if __name__ == '__main__':
    main()
