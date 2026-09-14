#!/usr/bin/env python3
"""Prepare an immutable Batch 3 kit from published sources; preserve earlier kits."""
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
    args = parser.parse_args()
    docs = Path(__file__).resolve().parent
    root = docs.parents[2]
    kit = args.resume.resolve() if args.resume else Path(tempfile.mkdtemp(prefix='holonight-uqc207-', dir='/tmp'))
    if kit.parent != Path('/tmp') or not kit.name.startswith('holonight-uqc207-'):
        parser.error('expected /tmp/holonight-uqc207-*')
    if (kit / 'READY').exists():
        parser.error('preserve released kits; create a fresh kit')
    kit.mkdir(exist_ok=True)
    kit.chmod(0o755)
    work = root / '.cache' / kit.name
    work.mkdir(exist_ok=True)
    (work / 'logs').mkdir(exist_ok=True)
    prefix = kit / 'prefix'
    (root / '.cache/uqc207-kit').write_text(str(kit) + '\n')

    def run(name, command, env=None):
        command = list(map(str, command))
        print(name, flush=True)
        with (work / 'logs' / (name + '.log')).open('a') as log:
            result = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=900)
        with (work / 'results.jsonl').open('a') as output:
            output.write(json.dumps(dict(name=name, command=command, exit_status=result.returncode)) + '\n')
        if result.returncode:
            raise SystemExit(f'{name} failed; inspect {work}/logs/{name}.log; resume with --resume {kit}')

    revisions = {}
    for name in ('holonight-config', 'holonight-qt', 'holonight-ai', 'holonight-settings',
                 'holonight-system-services', 'holonight-shell'):
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
        raise SystemExit('Sources changed while preparing; use a fresh kit')
    previous.write_text(json.dumps(revisions, indent=2) + '\n')
    for name in ('config', 'qt'):
        run(name + '-build', ['cmake', '--build', root / ('holonight-' + name) / 'build', '-j', '4'])
        run(name + '-install', ['cmake', '--install', root / ('holonight-' + name) / 'build', '--prefix', prefix])
    for name, source in (('system-services', root / 'holonight-system-services'),
                         ('shell-config', root / 'holonight-shell/libs/holonight-shell-config')):
        build = work / 'build' / name
        run(name + '-configure', ['cmake', '-S', source, '-B', build, '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Debug', '-DBUILD_TESTING=OFF', '-DCMAKE_INSTALL_LIBDIR=lib',
            f'-DCMAKE_INSTALL_PREFIX={prefix}', f'-DCMAKE_PREFIX_PATH={prefix}'])
        run(name + '-build', ['cmake', '--build', build, '-j', '4'])
        run(name + '-install', ['cmake', '--install', build])
    for name in ('ai', 'settings'):
        build = work / 'build' / name
        run(name + '-configure', ['cmake', '-S', root / ('holonight-' + name), '-B', build,
            '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Debug', '-DBUILD_TESTS=ON', '-DBUILD_TESTING=ON',
            '-DCMAKE_INSTALL_LIBDIR=lib', f'-DCMAKE_INSTALL_PREFIX={prefix}', f'-DCMAKE_PREFIX_PATH={prefix}',
            f'-DHOLONIGHT_QML_IMPORT_PATH={prefix}/lib/qt6/qml'])
        targets = ['holonight-chat', 'test_runtime_controls'] if name == 'ai' else ['holonight-settings', 'settings_controls_acceptance']
        run(name + '-build', ['cmake', '--build', build, '-j', '4', '--target', *targets])
        run(name + '-install', ['cmake', '--install', build])
    observer = root / 'holonight-qt/docs/sdd/unified-qtquick-controls/audit/render-diagnostics.cpp'
    flags = subprocess.check_output(['pkg-config', '--cflags', '--libs', 'Qt6Quick', 'Qt6Qml'], text=True).split()
    run('render-observer-build', ['g++', '-std=c++23', '-shared', '-fPIC', observer,
                                 '-o', prefix / 'lib/render-diagnostics.so', *flags])
    shutil.copy2(observer, kit / 'render-diagnostics.cpp')
    for name in ('guided-session.py', 'guided-app.py', 'rendering-test.py', 'FINDINGS.md'):
        shutil.copy2(docs / name, kit / name)
    shutil.copy2(root / 'holonight-qt/docs/sdd/unified-qtquick-controls/audit/auth-test/terminal.sh', kit)
    terminal = f'/bin/sh {kit}/terminal.sh'
    (kit / 'hyprland.conf').write_text(f'monitor = , preferred, auto, 1\nexec-once = {terminal}\n'
        f'bind = SUPER, Return, exec, {terminal}\nbind = SUPER SHIFT, E, exit,\nbind = SUPER, Q, killactive,\n')
    packages = ['haruna', 'neochat', 'tokodon', 'qt6-base', 'qt6-declarative', 'kirigami', 'kirigami-addons', 'hyprpolkitagent', 'hyprland']
    (kit / 'PROVIDER.txt').write_text(subprocess.check_output(['pacman', '-Q', *packages], text=True))
    (kit / 'README.md').write_text((docs / 'RENDERING-BATCH3.md').read_text().replace('__KIT__', str(kit)))
    env = dict(os.environ, LD_LIBRARY_PATH=str(prefix / 'lib'), PYTHONDONTWRITEBYTECODE='1')
    for style in ('Holonight', 'Fusion'):
        for scale in ('1', '1.25'):
            case = work / f'acceptance-{style}-{scale}'
            case.mkdir(exist_ok=True)
            (case / 'empty-path').mkdir(exist_ok=True)
            isolated = ['python3', root / 'holonight-shell/scripts/run-isolated-test.py', 'env',
                        f'LD_LIBRARY_PATH={prefix}/lib', f'QT_QUICK_CONTROLS_STYLE={style}', f'QT_SCALE_FACTOR={scale}',
                        f'UQC_IMPORT_PATH={prefix}/lib/qt6/qml', f'QML_IMPORT_PATH={prefix}/lib/qt6/qml']
            run(f'provider-{style}-{scale}', isolated + [root / 'holonight-qt/build/tests/holonight_runtime_composite_tests',
                '--gtest_filter=SharedRendering.*'], env)
            run(f'ai-{style}-{scale}', isolated + [work / 'build/ai/tests/runtime/test_runtime_controls'], env)
            run(f'settings-{style}-{scale}', isolated + [f'HOLONIGHT_APPEARANCE_FILE={case}/appearance.toml',
                f'PATH={case}/empty-path', work / 'build/settings/apps/settings/settings_controls_acceptance'], env)
    run('actual-staged-processes', ['python3', root / 'holonight-shell/scripts/run-isolated-test.py',
        'python3', docs / 'verify-rendering-kit.py', kit, '--logs', work / 'runtime', '--diagnostics'], env)
    run('collector-tests', ['python3', root / 'tests/test_guided_app.py'])
    for path in kit.glob('*.py'):
        ast.parse(path.read_text())
    run('terminal-syntax', ['sh', '-n', kit / 'terminal.sh'])
    (kit / 'SHA256SUMS').write_text('\n'.join(
        f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(kit)}'
        for path in sorted(kit.rglob('*')) if path.is_file()) + '\n')
    (kit / 'READY').write_text('Verified rendering candidate; manual findings and actual-app evidence gaps remain open.\n')
    archive = work / (kit.name + '.tar.gz')
    with tarfile.open(archive, 'w:gz') as saved:
        saved.add(kit, arcname=kit.name)
    # Test restoration at the exact configured path, preserving the original tree.
    kit.rename(kit.with_name(kit.name + '-before-restore'))
    run('restoration', ['python3', docs / 'restore-rendering-kit.py', archive])
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (work / 'archive.sha256').write_text(digest + '  ' + archive.name + '\n')
    print(f'READY {kit}\nArchive {archive}\nSHA256 {digest}', flush=True)


if __name__ == '__main__':
    main()
