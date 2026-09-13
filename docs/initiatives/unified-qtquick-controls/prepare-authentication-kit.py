#!/usr/bin/env python3
"""Stage a published Batch 2 authentication kit and release only after verification."""
import argparse
import ast
import hashlib
import io
import json
import os
import re
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
    shell = root / 'holonight-shell'
    kit = args.resume.resolve() if args.resume else Path(tempfile.mkdtemp(prefix='holonight-uqc205-b2_', dir='/tmp'))
    if kit.parent != Path('/tmp') or not kit.name.startswith('holonight-uqc205-b2_'):
        parser.error('expected a fresh /tmp/holonight-uqc205-b2_* directory')
    if (kit / 'READY').exists():
        parser.error('preserve released kits; create a fresh kit')
    work = root / '.cache' / kit.name
    work.mkdir(parents=True, exist_ok=True)
    (work / 'logs').mkdir(exist_ok=True)
    (root / '.cache/uqc205-batch2-kit').write_text(str(kit) + '\n')
    kit.chmod(0o755)
    prefix = kit / 'prefix'

    def run(name, command, env=None):
        command = list(map(str, command))
        print(name, flush=True)
        with (work / 'logs' / (name + '.log')).open('a') as output:
            result = subprocess.run(command, cwd=root, env=env, stdout=output, stderr=subprocess.STDOUT, timeout=900)
        with (work / 'results.jsonl').open('a') as output:
            output.write(json.dumps(dict(name=name, command=command, exit_status=result.returncode)) + '\n')
        if result.returncode:
            raise SystemExit(f'{name} failed; inspect {work}/logs/{name}.log; resume with --resume {kit}')

    revisions = {}
    for name in ('holonight-config', 'holonight-qt', 'holonight-system-services', 'holonight-shell'):
        repo = root / name
        if subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], text=True):
            raise SystemExit('STOP: uncommitted source: ' + name)
        revision = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        remote = subprocess.check_output(['git', '-C', str(repo), 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
        if remote != revision:
            raise SystemExit('STOP: source must match canonical main: ' + name)
        revisions[name] = revision
    revision_file = kit / 'revisions.json'
    if revision_file.exists() and json.loads(revision_file.read_text()) != revisions:
        raise SystemExit('STOP: revisions changed during preparation; create a fresh kit')
    revision_file.write_text(json.dumps(revisions, indent=2) + '\n')
    for name in ('config', 'qt', 'system-services'):
        run(name + '-install', ['cmake', '--install', shell / 'build-dependencies' / name, '--prefix', prefix])
    run('shell-install', ['cmake', '--install', shell / 'build', '--prefix', prefix])
    if not (kit / 'owned-auth').exists():
        run('existing-authentication-machinery', ['python3', docs / 'prepare-cancellation-kit.py', kit])
    source = (kit / 'owned-auth/auth-test.py').read_text()
    tree = ast.parse(source)
    functions = [ast.get_source_segment(source, node) for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in ('identity', 'output')]
    assert len(functions) == 2
    (kit / 'session_identity.py').write_text('import os\nimport subprocess\n\n' + '\n\n'.join(functions) + '\n')
    for name in ('registration.py', 'bounded_challenge.py'):
        shutil.copy2(kit / 'owned-auth' / name, kit / name)
    for name in ('authentication-test.py', 'guided-session.py'):
        shutil.copy2(docs / name, kit / name)
    terminal = f'/bin/sh {kit}/terminal.sh'
    (kit / 'hyprland.conf').write_text(
        f'monitor = , preferred, auto, 1\nexec-once = {terminal}\n'
        f'bind = SUPER, Return, exec, {terminal}\n'
        'bind = SUPER SHIFT, E, exit,\nbind = SUPER, Q, killactive,\n')
    versions = subprocess.check_output(['pacman', '-Q', 'qt6-base', 'qt6-declarative', 'hyprpolkitagent', 'hyprland', 'sway'], text=True)
    (kit / 'PROVIDER.txt').write_text(versions)
    guide = (docs / 'AUTHENTICATION-BATCH2.md').read_text().replace('__KIT__', str(kit))
    guide = re.sub(r'/tmp/holonight-uqc205-b2_[a-z0-9_]+', str(kit), guide)
    (kit / 'README.md').write_text(guide)
    env = dict(os.environ, LD_LIBRARY_PATH=str(prefix / 'lib'), PYTHONDONTWRITEBYTECODE='1')
    mask = ['bwrap', '--die-with-parent', '--bind', '/', '/', '--dev', '/dev', '--proc', '/proc',
            '--tmpfs', '/usr/lib/qt6/qml/Holonight']
    for pattern in ('*holonight*.so*', '*HoloNight*.so*'):
        for path in Path('/usr/lib').glob(pattern):
            if path.is_file() and not path.is_symlink():
                mask += ['--ro-bind', '/dev/null', str(path)]
    isolated = mask + ['--', 'python3', shell / 'scripts/run-isolated-test.py', 'env',
                       f'LD_LIBRARY_PATH={prefix}/lib', f'QML_IMPORT_PATH={prefix}/lib/qt6/qml']
    for style in ('Holonight', 'Fusion'):
        for scale in ('1', '1.25'):
            run(f'installed-authentication-{style}-{scale}', isolated + [f'QT_QUICK_CONTROLS_STYLE={style}',
                f'QT_SCALE_FACTOR={scale}', f'UQC_POLKIT_EXECUTABLE={prefix}/libexec/holonight-polkit-agent',
                f'UQC_POLKIT_LOG={work}/logs/installed-{style}-{scale}.log', 'LD_DEBUG=libs', 'QT_LOGGING_RULES=*.debug=true;*.info=true',
                shell / 'build/tests/test_holonight_authentication',
                '--gtest_filter=PolkitAgentProcess.*:DirectFailureAndAuthorityCancellation/*/2'], env)
            run(f'compiled-real-model-{style}-{scale}', isolated + [f'QT_QUICK_CONTROLS_STYLE={style}',
                f'QT_SCALE_FACTOR={scale}', f'UQC_AUTH_EVIDENCE_DIR={work}/rendered',
                shell / 'build/tests/test_holonight_compiled_controls', '-input',
                shell / 'tests/qml/tst_AuthenticationRealModel.qml'], env)
    run('installed-launches', mask + ['--', 'python3', shell / 'scripts/run-isolated-test.py', 'env',
        f'LD_LIBRARY_PATH={prefix}/lib', 'UQC_ISOLATED=1', 'python3', shell / 'tests/test_quick_controls_launch.py',
        '--build', shell / 'build', '--prefix', shell / 'build-dependencies/prefix', '--logs', work / 'logs/relocated-launches'], env)
    run('staged-runtime-evidence', isolated + ['python3', docs / 'verify-authentication-kit.py', kit,
        '--logs', work / 'logs'], env)
    run('helper-regressions', ['python3', root / 'tests/test_authentication_kit.py'], env)
    run('wrong-user-refusal', ['python3', root / 'tests/check_authentication_kit_refusals.py', kit], env)
    for path in kit.rglob('*.py'):
        ast.parse(path.read_text())
    run('terminal-syntax', ['sh', '-n', kit / 'terminal.sh'])
    for name in ('config', 'qt', 'system-services'):
        cache = shell / 'build-dependencies' / name / 'CMakeCache.txt'
        shutil.copy2(cache, work / (name + '-CMakeCache.txt'))
    shutil.copy2(__file__, work / 'prepare-authentication-kit.py')
    checksums = [f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(kit)}'
                 for path in sorted(kit.rglob('*')) if path.is_file()]
    (kit / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')
    archive = work / (kit.name + '.tar.gz')
    # Restoration verifies checksums before writing the first READY marker.
    with tarfile.open(archive, 'w:gz') as saved:
        saved.add(kit, arcname=kit.name)
        ready = b'Verified Batch 2 authentication checkpoint; see revisions.json and SHA256SUMS.\n'
        member = tarfile.TarInfo(kit.name + '/READY')
        member.size = len(ready)
        member.mode = 0o644
        saved.addfile(member, io.BytesIO(ready))
    preserved = kit.with_name(kit.name + '-before-restore')
    if preserved.exists():
        raise SystemExit('STOP: preserve previous restoration attempt')
    kit.rename(preserved)
    run('archive-restoration', ['python3', docs / 'restore-authentication-kit.py', archive])
    run('released-refusals', ['python3', root / 'tests/check_authentication_kit_refusals.py', kit, archive], env)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (work / 'archive.sha256').write_text(digest + '  ' + archive.name + '\n')
    print(f'READY: {kit}\nArchive: {archive}\nSHA256: {digest}', flush=True)


if __name__ == '__main__':
    main()
