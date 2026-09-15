#!/usr/bin/env python3
"""Prepare and verify a fresh immutable Batch 7 kit from canonical greeter sources."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume', type=Path)
    parser.add_argument('--g07', action='store_true')
    args = parser.parse_args()
    docs = Path(__file__).resolve().parent
    root = docs.parents[2]
    package = 'uqc216' if args.g07 else 'uqc212'
    kit = args.resume.resolve() if args.resume else Path(tempfile.mkdtemp(prefix=f'holonight-{package}-', dir='/tmp'))
    if kit.parent != Path('/tmp') or not kit.name.startswith(f'holonight-{package}-'):
        parser.error(f'expected /tmp/holonight-{package}-*')
    if (kit / 'READY').exists():
        parser.error('preserve released kits; use a fresh kit')
    kit.mkdir(exist_ok=True)
    kit.chmod(0o755)
    work = root / '.cache' / kit.name
    (work / 'logs').mkdir(parents=True, exist_ok=True)
    (root / f'.cache/{package}-kit').write_text(str(kit) + '\n')
    prefix = kit / 'prefix'

    def run(name, command, env=None):
        command = list(map(str, command))
        print(name, flush=True)
        with (work / 'logs' / (name + '.log')).open('a') as log:
            result = subprocess.run(command, cwd=root, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=900)
        with (work / 'results.jsonl').open('a') as record:
            record.write(json.dumps(dict(name=name, command=command, exit_status=result.returncode)) + '\n')
        if result.returncode:
            raise SystemExit(f'{name} failed; inspect {work}/logs/{name}.log; resume with --resume {kit}')

    revisions = {}
    for name in ('holonight-config', 'holonight-qt', 'holonight-greeter'):
        repo = root / name
        if subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], text=True):
            raise SystemExit('Uncommitted source: ' + name)
        revision = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        remote = subprocess.check_output(['git', '-C', str(repo), 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
        if revision != remote:
            raise SystemExit('Source differs from canonical main: ' + name)
        revisions[name] = revision
    previous = kit / 'revisions.json'
    if previous.exists() and json.loads(previous.read_text()) != revisions:
        raise SystemExit('Sources changed during preparation; create a fresh kit')
    previous.write_text(json.dumps(revisions, indent=2) + '\n')
    # These dependency builds were produced by the verified greeter Taskfile.
    for name in ('config', 'qt'):
        build = root / 'holonight-greeter/build/dependencies' / name
        run(name + '-build', ['cmake', '--build', build, '-j', '4'])
        run(name + '-install', ['cmake', '--install', build, '--prefix', prefix])
    build = work / 'build'
    run('greeter-configure', ['cmake', '-S', root / 'holonight-greeter', '-B', build,
        '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Debug', '-DBUILD_TESTING=ON',
        '-DCMAKE_INSTALL_LIBDIR=lib', f'-DCMAKE_INSTALL_PREFIX={prefix}',
        f'-DCMAKE_PREFIX_PATH={prefix}', f'-DHolonightQt_DIR={prefix}/lib/cmake/HolonightQt'])
    run('greeter-build', ['cmake', '--build', build, '-j', '4'])
    run('greeter-install', ['cmake', '--install', build])
    observer = root / 'holonight-qt/docs/sdd/unified-qtquick-controls/audit/render-diagnostics.cpp'
    flags = subprocess.check_output(['pkg-config', '--cflags', '--libs', 'Qt6Quick', 'Qt6Qml'], text=True).split()
    run('observer-build', ['g++', '-std=c++23', '-shared', '-fPIC', observer,
                           '-o', prefix / 'lib/render-diagnostics.so', *flags])
    shutil.copy2(observer, kit)
    if args.g07:
        caret = root / 'holonight-greeter/docs/sdd/unified-qtquick-controls/audit/caret-diagnostics.cpp'
        run('caret-observer-build', ['g++', '-std=c++23', '-shared', '-fPIC', caret,
                                    '-o', prefix / 'lib/caret-diagnostics.so', *flags])
        shutil.copy2(caret, kit)
    for name in ('guided-session.py', 'guided-app.py', 'verify-greeter-kit.py'):
        shutil.copy2(docs / name, kit)
    shutil.copy2(root / 'holonight-qt/docs/sdd/unified-qtquick-controls/audit/auth-test/terminal.sh', kit)
    terminal = f'/bin/sh {kit}/terminal.sh'
    (kit / 'sway.conf').write_text(f'output * scale 1\nexec {terminal}\n'
        f'bindsym Mod4+Return exec {terminal}\nbindsym Mod4+Shift+e exit\nbindsym Mod4+q kill\n')
    packages = ('qt6-base', 'qt6-declarative', 'hyprpolkitagent', 'sway', 'hyprland')
    (kit / 'PROVIDER.txt').write_text(subprocess.check_output(['pacman', '-Q', *packages], text=True))
    (kit / 'README.md').write_text((docs / ('GREETER-G07.md' if args.g07 else 'GREETER-BATCH7.md')).read_text().replace('__KIT__', str(kit)))
    mask = ['bwrap', '--die-with-parent', '--bind', '/', '/', '--dev', '/dev', '--proc', '/proc']
    for base in ('/usr/lib', '/usr/local/lib'):
        module = Path(base) / 'qt6/qml/Holonight'
        if module.is_dir():
            mask += ['--tmpfs', str(module)]
        for pattern in ('*holonight*.so*', '*HoloNight*.so*'):
            for path in Path(base).glob(pattern):
                if path.is_file() and not path.is_symlink():
                    mask += ['--ro-bind', '/dev/null', str(path)]
    mask += ['--']
    run('staged-runtime-matrix', mask + ['ctest', '--test-dir', build, '-V', '-R', '^runtime_(Holonight|Fusion)_'])
    for scale in ('1', '1.25'):
        run('installed-launches-' + scale, mask + ['python3', root / 'holonight-greeter/scripts/check-runtime-launches.py',
            prefix / 'bin/holonight-greeter', prefix, '--scale', scale,
            '--forbid-path', build, '--logs', work / ('installed-' + scale)])
    run('staged-process-origins-dpr-exits', mask + ['python3', docs / 'verify-greeter-kit.py', kit, work / 'runtime'])
    if args.g07:
        run('staged-caret-graphics', mask + ['python3', root / 'holonight-greeter/scripts/check-caret-graphics.py',
            build / 'greeter_runtime_tests', prefix, '--logs', work / 'caret-graphics'])
    run('collector-tests', ['python3', root / 'tests/test_guided_app.py'])
    for path in kit.glob('*.py'):
        ast.parse(path.read_text())
    run('terminal-syntax', ['sh', '-n', kit / 'terminal.sh'])
    (kit / 'SHA256SUMS').write_text('\n'.join(
        f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(kit)}'
        for path in sorted(kit.rglob('*')) if path.is_file() and path.name != 'SHA256SUMS') + '\n')
    (kit / 'READY').write_text(('G07 diagnostic kit' if args.g07 else 'Batch 7') +
                               ' locally verified; four Sway manual runs pending.\n')
    archive = work / (kit.name + '.tar.gz')
    with tarfile.open(archive, 'w:gz') as saved:
        saved.add(kit, arcname=kit.name)
    kit.rename(kit.with_name(kit.name + '-before-restore'))
    run('restoration', ['python3', docs / 'restore-rendering-kit.py', archive])
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (work / 'archive.sha256').write_text(digest + '  ' + archive.name + '\n')
    print(f'READY {kit}\nArchive {archive}\nSHA256 {digest}', flush=True)


if __name__ == '__main__':
    main()
