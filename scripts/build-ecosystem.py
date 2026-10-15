#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build explicitly selected sibling sources into one development prefix."""
import argparse
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ORDER = re.search(r'^readonly MODULES=\(([^)]*)\)', (ROOT / 'scripts/install.sh').read_text(), re.M).group(1).split()


def run(*args, **kwargs):
    subprocess.run(list(map(str, args)), check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=ROOT / 'build/integration/prefix')
    parser.add_argument('--tests', action='store_true')
    args = parser.parse_args()
    prefix = args.prefix.resolve()
    env = dict(os.environ, CMAKE_PREFIX_PATH=str(prefix), QML_IMPORT_PATH=str(prefix / 'lib/qt6/qml'),
               LD_LIBRARY_PATH=str(prefix / 'lib'), QT_QPA_PLATFORM='offscreen', QSG_RHI_BACKEND='software')
    for name in ORDER:
        source = ROOT / name
        build = ROOT / 'build/integration' / name
        if name == 'holonight-icons':
            run('python3', source / 'scripts/build.py', env=env)
            if args.tests:
                run('python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v', cwd=source, env=env)
            continue
        options = ['-DBUILD_DEMO=OFF', '-DBUILD_CONTROLS_GALLERY=OFF', '-DBUILD_QT5_PROBES=OFF']
        test = 'ON' if args.tests else 'OFF'
        run('cmake', '-S', source, '-B', build, '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release',
            f'-DCMAKE_INSTALL_PREFIX={prefix}', '-DCMAKE_INSTALL_LIBDIR=lib',
            f'-DCMAKE_PREFIX_PATH={prefix}', f'-DQML_IMPORT_PATH={prefix}/lib/qt6/qml',
            f'-DBUILD_TESTS={test}', f'-DBUILD_TESTING={test}', *options, env=env)
        run('cmake', '--build', build, '--parallel', os.environ.get('JOBS', '2'), env=env)
        if args.tests:
            isolation = ['python3', source / 'scripts/run-isolated-test.py', '--hide-host'] if name == 'holonight-shell' else ['dbus-run-session', '--']
            run(*isolation, 'ctest', '--test-dir', build,
                '--output-on-failure', '--no-tests=error', env=env)
        install_env = dict(env, DESTDIR=str(build / 'stage')) if name == 'holonight-hyprlock' else env
        run('cmake', '--install', build, env=install_env)


if __name__ == '__main__':
    main()
