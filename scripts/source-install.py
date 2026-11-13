#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prepare native component payloads and explicitly deploy or resume them."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from install_catalog import BASE_PACKAGES, CATALOG, select
from install_state import (STATE, RUNTIME, ancestors, atomic, digest, inventory, lock,
                           manifest_text, parse_manifest, protected_ancestors, protected_copy, read_manifest, row_state, snapshot, sync)

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.source-install'


def run(*args, **kwargs):
    return subprocess.run(list(map(str, args)), check=True, **kwargs)


def output(*args):
    return subprocess.check_output(list(map(str, args)), text=True).strip()


def host_identity():
    return hashlib.sha256(output('pacman', '-Q').encode()).hexdigest()


def source_identity(name):
    source = ROOT / name
    revision = output('git', '-C', source, 'rev-parse', 'HEAD')
    status = output('git', '-C', source, 'status', '--porcelain', '--untracked-files=normal')
    checksum = hashlib.sha256()
    files = subprocess.check_output(['git', '-C', str(source), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'])
    for relative in sorted(set(files.split(b'\0')) - {b''}):
        path = source / os.fsdecode(relative)
        checksum.update(relative + b'\0')
        if path.is_symlink() or path.is_file():
            checksum.update(digest(path).encode())
            checksum.update(str(path.lstat().st_mode).encode())
        else:
            checksum.update(b'missing-or-submodule')
    return {'revision': revision, 'identity': checksum.hexdigest(), 'dirty': bool(status)}


def preflight(selection, pinned):
    release = Path('/etc/os-release').read_text()
    if not any('arch' in line.lower() for line in release.splitlines() if line.startswith(('ID=', 'ID_LIKE='))):
        raise ValueError('source installation requires Arch Linux or an Arch-derived distribution')
    if os.environ.get('HOLONIGHT_EXTERNAL_PREFIX'):
        raise ValueError('system deployment requires package-managed external libraries')
    for tool in ('git', 'cmake', 'ninja', 'pkg-config', 'pacman', 'c++'):
        if not shutil.which(tool):
            raise ValueError(f'missing required command: {tool}')
    packages = set(BASE_PACKAGES)
    for name in selection:
        packages.update(CATALOG[name].packages)
        if 'desktop' in CATALOG[name].hooks:
            packages.add('desktop-file-utils')
    run('pacman', '-T', *sorted(packages))
    run('c++', '-std=c++23', '-x', 'c++', '-fsyntax-only', '-',
        input='#include <expected>\nint main(){std::expected<int,int> v(1); return *v-1;}\n', text=True)
    if 'holonight-greeter' in selection:
        run('getent', 'passwd', 'greeter', stdout=subprocess.DEVNULL)
    for name in selection:
        if not (ROOT / name / '.git').exists():
            raise ValueError(f'component is not initialized: {name}')
        if pinned:
            expected = output('git', '-C', ROOT, 'ls-tree', 'HEAD', name).split()[2]
            if output('git', '-C', ROOT / name, 'rev-parse', 'HEAD') != expected:
                raise ValueError(f'{name} differs from the umbrella pin')


def merge_prefix(payload, prefix):
    """Keep identical staged entries and mtimes; ownership was checked separately."""
    for path in sorted(payload.rglob('*')):
        target = prefix / path.relative_to(payload)
        ancestors(target)
        state = snapshot(path)
        if state[0] == 'd':
            target.mkdir(parents=True, exist_ok=True)
        elif snapshot(target) != state:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink() or target.is_file():
                target.unlink()
            if path.is_symlink():
                target.symlink_to(os.readlink(path))
            else:
                shutil.copy2(path, target)


def prepare(selection, args):
    coordinated = not args.components
    mode = 'coordinated' if coordinated else 'selected-' + hashlib.sha256('\n'.join(selection).encode()).hexdigest()[:16]
    cache = WORK if coordinated else WORK / 'caches' / mode
    cache.mkdir(parents=True, exist_ok=True)
    # A stable prefix is part of the build configuration. Reconcile inventories,
    # rather than discarding the prefix and forcing dependent rebuilds.
    prefix = cache / ('stage' if coordinated else 'prefix')
    prefix.mkdir(exist_ok=True)
    previous = read_manifest(cache / 'prefix.tsv')
    if not (cache / 'prefix.tsv').exists() and any(prefix.iterdir()):
        # Import the previous installer's recorded inventories while retaining
        # its existing build and prefix paths. Never infer ownership by filename.
        owners = {}
        for component in CATALOG:
            recorded = cache / 'module-paths' / component
            if recorded.exists():
                for path in recorded.read_text().splitlines():
                    if path in owners and owners[path] != component:
                        raise ValueError(f'duplicate legacy staged ownership: {path}')
                    owners[path] = component
        for path, row in inventory(prefix, 'umbrella', 'legacy-cache').items():
            if row[2] != 'd' and path not in owners:
                raise ValueError(f'unrecorded legacy staged entry: {path}; preserve or explicitly discard the old stage before preparing again')
            row[0] = owners.get(path, 'umbrella')
            previous[path] = row
    current = {}
    attempt = Path(tempfile.mkdtemp(prefix='prepared-', dir=WORK))
    atomic(attempt / 'status.json', json.dumps({'status': 'preparing', 'selection': selection}))
    host = host_identity()
    components = {}
    for name in selection:
        source = ROOT / name
        identity = source_identity(name)
        print(f'==> Preparing {name}' + (' (dirty checkout)' if identity['dirty'] else ''), flush=True)
        payload = attempt / name
        payload.mkdir()
        build = cache / 'build' / name
        options = ['CMAKE_BUILD_TYPE=Release', 'CMAKE_INSTALL_PREFIX=/usr',
                   f'CMAKE_PREFIX_PATH={prefix}/usr', 'BUILD_TESTS=OFF', 'BUILD_TESTING=OFF',
                   'ENABLE_COVERAGE=OFF', *CATALOG[name].options]
        if name == 'holonight-appearance-adapters':
            options += [f'HOLONIGHT_QT_DIR={prefix}/usr', f'HOLONIGHT_CONFIG_DIR={prefix}/usr']
        if name in ('holonight-file-browser', 'holonight-viewer', 'holonight-files', 'xdg-desktop-portal-holonight'):
            options += [f'QML_IMPORT_PATH={prefix}/usr/lib/qt6/qml']
        if name == 'holonight-ai':
            options += [f'HOLONIGHT_QML_IMPORT_PATH={prefix}/usr/lib/qt6/qml']
        if name == 'holonight-icons':
            run('python3', source / 'scripts/stage.py', '--destdir', payload)
            if shutil.which('gtk-update-icon-cache'):
                for theme in ('HoloNight', 'HoloNight-Dark'):
                    run('gtk-update-icon-cache', '-q', '-t', '-f', payload / 'usr/share/icons' / theme)
        else:
            run('cmake', '-S', source, '-B', build, '-G', 'Ninja', '-U', '*[Hh]olo*_DIR', *['-D' + option for option in options])
            run('cmake', '--build', build, '--parallel')
            if name == 'holonight-images':
                bundle = (Path((build / 'installer-runtime.path').read_text())
                          if (build / 'installer-runtime.path').exists() else build / 'installer-runtime')
                bundle_key = hashlib.sha256((digest(build / 'holonight-images-helper') + digest(source / 'scripts/prepare-isolated-runtime.py') + host).encode()).hexdigest()
                key_file = build / 'installer-runtime.key'
                valid = key_file.exists() and key_file.read_text() == bundle_key and bundle.is_dir()
                if valid:
                    valid = subprocess.run([str(build / 'holonight-images-helper'), '--verify-runtime', str(bundle)]).returncode == 0
                if not valid:
                    bundle = Path(tempfile.mkdtemp(prefix='runtime-', dir=build)) / 'bundle'
                    run('python3', source / 'scripts/prepare-isolated-runtime.py', '--helper',
                        build / 'holonight-images-helper', '--plugins', '/usr/lib/qt6/plugins', '--output', bundle)
                    # Keep failed/old bundles for diagnosis; the pointer is published only after verification.
                    atomic(build / 'installer-runtime.path', str(bundle))
                elif (build / 'installer-runtime.path').exists():
                    bundle = Path((build / 'installer-runtime.path').read_text())
                atomic(key_file, bundle_key)
                run('cmake', '-S', source, '-B', build, f'-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE={bundle}')
            run('cmake', '--install', build, env=dict(os.environ, DESTDIR=str(payload)))
        if source_identity(name) != identity:
            raise ValueError(f'source changed while preparing {name}; prepare again')
        rows = inventory(payload, name, identity['revision'])
        for path, row in rows.items():
            if path in current and (row[2] != 'd' or current[path][2:4] != row[2:4]):
                raise ValueError(f'multiple components install {path}: {current[path][0]} and {name}')
            if path in previous and previous[path][0] == name:
                previous.pop(path)
            current[path] = row
        # Remove obsolete staged provider entries before configuring a consumer.
        for path, row in list(previous.items()):
            if row[0] == name:
                target = prefix / path.lstrip('/')
                if snapshot(target) == row_state(row):
                    if row[2] == 'd':
                        try:
                            target.rmdir()
                        except OSError:
                            pass
                    else:
                        target.unlink()
                previous.pop(path)
        merge_prefix(payload, prefix)
        atomic(cache / 'prefix.tsv', manifest_text({**previous, **current}), 0o644)
        components[name] = {**identity, 'options': options, 'inventory': rows, 'host': host}
        if name == 'holonight-images':
            components[name]['bundle_inputs'] = bundle_key
    if 'xdg-desktop-portal-holonight' in selection:
        validate_portal(attempt / 'xdg-desktop-portal-holonight')
    if host_identity() != host:
        raise ValueError('host packages changed during preparation; prepare again')
    record = {'selection': selection, 'host': host, 'components': components, 'root': str(args.root),
              'protected_images': args.protected_images_runtime or args.root == Path('/'),
              'adopt': args.adopt_existing, 'maintenance': args.maintenance_migrate_images_runtime}
    atomic(attempt / 'prepared.json', json.dumps(record, sort_keys=True))
    atomic(WORK / 'prepared.path', str(attempt))
    return attempt, record


def validate_portal(payload):
    descriptor = payload / 'usr/share/xdg-desktop-portal/portals/holonight.portal'
    service = payload / 'usr/share/dbus-1/services/org.freedesktop.impl.portal.desktop.holonight.service'
    executable = payload / 'usr/libexec/xdg-desktop-portal-holonight'
    if not all(path.is_file() and not path.is_symlink() for path in (descriptor, service, executable)):
        raise ValueError('unified portal payload is incomplete')
    if ('DBusName=org.freedesktop.impl.portal.desktop.holonight' not in descriptor.read_text().splitlines()
            or 'Interfaces=org.freedesktop.impl.portal.FileChooser;org.freedesktop.impl.portal.Settings;' not in descriptor.read_text().splitlines()
            or 'Name=org.freedesktop.impl.portal.desktop.holonight' not in service.read_text().splitlines()):
        raise ValueError('unified portal identity or interfaces are incorrect')


def validate_prepared(attempt, record):
    if host_identity() != record['host']:
        raise ValueError('host dependencies changed; run install again without --resume to prepare again')
    for name, component in record['components'].items():
        actual = inventory(attempt / name, name, component['revision'])
        parse_manifest(manifest_text(actual))
        if actual != component['inventory']:
            raise ValueError(f'prepared payload changed: {name}; prepare again')


def save_transaction(state, transaction):
    atomic(state / 'transaction.json', json.dumps(transaction, sort_keys=True))


def approved(args, selection):
    print('==> Deployment selection: ' + ', '.join(selection), flush=True)
    if not args.yes and input(f'Deploy prepared operation into {args.root}? [y/N] ').lower() not in ('y', 'yes'):
        raise ValueError('operation cancelled; prepared payloads retained for --resume')


def package_collision(root, name):
    run('pacman', '--root', root, '-Q', stdout=subprocess.DEVNULL)
    return subprocess.run(['pacman', '--root', str(root), '-Qo', '--', name],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def new_transaction(root, state, selection, incoming, removing, adopt, attempt=None, defer=False):
    old = read_manifest(state / 'manifest.tsv')
    intended = {name: row for name, row in old.items() if row[0] not in selection or row[2] == 'd'}
    actions = []
    for name in sorted(set(old) | set(incoming), key=lambda n: (len(Path(n).parts), n)):
        prior, row = old.get(name), incoming.get(name)
        if row and prior and row[2] != 'd' and prior[0] not in (*selection, 'umbrella'):
            raise ValueError(f'path belongs to unselected component: {name}')
        if not row and (not prior or prior[0] not in selection):
            continue
        path = root / name.lstrip('/')
        if root == Path('/'):
            protected_ancestors(path)
        try:
            actual = snapshot(path)
        except ValueError:
            if not removing:
                raise
            print(f'preserved path under symlinked parent: {path}', file=sys.stderr)
            if prior:
                intended[name] = prior
            continue
        if row:
            if row[2] == 'd':
                if actual and actual[0] != 'd':
                    raise ValueError(f'installation directory is occupied: {path}')
            elif actual and not prior:
                if not adopt or name == '/usr/share/xdg-desktop-portal/portals/holonight.portal':
                    raise ValueError(f'unmanaged collision: {path}; use --adopt-existing for migration')
                if package_collision(root, name):
                    raise ValueError(f'package-owned collision: {path}')
            elif actual and actual != row_state(prior) and actual != row_state(row):
                raise ValueError(f'preserve modified path: {path}; resolve it manually')
            intended[name] = row
            if row[2] == 'd' and actual:
                row = [*row[:3], actual[1], *row[4:]]
                intended[name] = row
            actions.append({'path': name, 'previous': actual, 'intended': row_state(row),
                            'owner': row[0], 'backup': bool(actual and not prior and row[2] != 'd')})
        elif actual and actual != row_state(prior):
            print(f'preserved modified path: {path}', file=sys.stderr)
            intended[name] = prior
        elif actual:
            actions.append({'path': name, 'previous': actual, 'intended': None, 'owner': prior[0]})
            intended.pop(name, None)
        else:
            intended.pop(name, None)
    if removing:
        scheduled = {action['path'] for action in actions}
        for name, row in old.items():
            if row[2] != 'd' or name in scheduled or any(p.startswith(name + '/') and r[2] != 'd' for p, r in intended.items()):
                continue
            path = root / name.lstrip('/')
            try:
                actual = snapshot(path)
            except ValueError:
                continue
            if actual == row_state(row):
                actions.append({'path': name, 'previous': actual, 'intended': None, 'owner': row[0]})
                intended.pop(name, None)
            elif actual is None:
                intended.pop(name, None)
    # Directories are removed last. Failure to remove nonempty shared directories is harmless.
    actions.sort(key=lambda a: (a['intended'] is None, -len(Path(a['path']).parts)
                               if a['intended'] is None else len(Path(a['path']).parts), a['path']))
    transaction = {'selection': selection, 'previous_manifest': old, 'manifest': intended, 'actions': actions,
                   'attempt': str(attempt) if attempt else None, 'removing': removing,
                   'done': [], 'status': 'pending', 'root': str(root)}
    if not defer:
        save_transaction(state, transaction)
    return transaction


def backup_adoptions(root, state, transaction):
    # Complete every durable backup before changing any target payload.
    for action in transaction['actions']:
        if not action.get('backup'):
            continue
        path = root / action['path'].lstrip('/')
        backup = state / ('adoption-backup-' + Path(transaction['attempt']).name) / action['path'].lstrip('/')
        ancestors(backup)
        if os.path.lexists(backup):
            if snapshot(backup) != action['previous']:
                raise ValueError(f'adoption backup changed: {backup}')
            continue
        if snapshot(path) != action['previous']:
            raise ValueError(f'adoption source changed before backup: {path}')
        backup.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if path.is_symlink():
            backup.symlink_to(os.readlink(path))
            sync(backup.parent)
        else:
            atomic(backup, path.read_bytes(), int(action['previous'][1], 8))
        if snapshot(backup) != action['previous']:
            raise ValueError(f'adoption backup does not match approved previous state: {backup}')
        for parent in (backup.parent, *backup.parent.parents):
            sync(parent)
            if parent == state:
                break


def execute(root, state, transaction):
    if transaction['attempt']:
        payload = Path(transaction['attempt'])
        validate_prepared(payload, json.loads((payload / 'prepared.json').read_text()))
    backup_adoptions(root, state, transaction)
    images_step(root, state, transaction)
    for index, action in enumerate(transaction['actions']):
        path = root / action['path'].lstrip('/')
        if root == Path('/'):
            protected_ancestors(path)
        actual = snapshot(path)
        expected = action['intended']
        if index in transaction['done']:
            if actual != expected and not (expected is None and action['previous'][0] == 'd' and actual and actual[0] == 'd'):
                raise ValueError(f'completed transaction path changed; preserved: {path}')
            continue
        if actual != action['previous'] and actual != expected:
            raise ValueError(f'transaction conflict; preserved: {path}')
        transaction['active'] = index
        save_transaction(state, transaction)  # Intent is durable before each mutation.
        if actual != expected:
            if expected is None:
                if actual and actual[0] == 'd':
                    try:
                        path.rmdir()
                    except OSError:
                        prior = transaction['previous_manifest'].get(action['path'])
                        if prior:
                            transaction['manifest'][action['path']] = prior
                elif actual:
                    path.unlink()
            elif expected[0] == 'd':
                path.mkdir(parents=True, exist_ok=True, mode=int(expected[1], 8))
                # Existing shared directories retain their host permissions.
            else:
                source = Path(transaction['attempt']) / action['owner'] / action['path'].lstrip('/')
                path.parent.mkdir(parents=True, exist_ok=True)
                if expected[0] == 'f':
                    atomic(path, source.read_bytes(), int(expected[1], 8))
                else:
                    temporary = path.parent / ('.holonight-link-' + str(os.getpid()))
                    temporary.symlink_to(os.readlink(source))
                    os.replace(temporary, path)
                    sync(path.parent)
            sync(path.parent)
        if actual is None and action['previous'] and action['previous'][0] == 'd':
            transaction['manifest'].pop(action['path'], None)
        transaction['done'].append(index)
        save_transaction(state, transaction)
    if transaction.get('attempt') and 'holonight-images' in transaction['selection'] and not transaction.get('images'):
        helper = Path(transaction['attempt']) / 'holonight-images' / RUNTIME.lstrip('/') / 'usr/libexec/holonight-images-helper'
        run(helper, '--verify-runtime', root / RUNTIME.lstrip('/'))
    if 'holonight-icons' in transaction['selection'] and not transaction['removing']:
        for theme in ('HoloNight', 'HoloNight-Dark'):
            name = f'/usr/share/icons/{theme}/icon-theme.cache'
            if name in transaction['manifest']:
                path = root / name.lstrip('/')
                if snapshot(path) != row_state(transaction['manifest'][name]):
                    raise ValueError(f'icon cache changed: {path}')
                os.utime(path, None, follow_symlinks=False)
    # A repeated publication is safe only while the manifest matches either side.
    current = read_manifest(state / 'manifest.tsv')
    if current not in (transaction['previous_manifest'], transaction['manifest']):
        raise ValueError('ownership manifest changed during transaction; preserved')
    atomic(state / 'manifest.tsv', manifest_text(transaction['manifest']), 0o644)
    transaction['published'] = True
    save_transaction(state, transaction)
    refresh(root, transaction['selection'], transaction['removing'], state, transaction)
    image_journal = state / 'images-transaction.json'
    if image_journal.exists():
        os.replace(image_journal, state / 'images-transaction.completed.json')
        sync(state)
    transaction['status'] = 'complete'
    save_transaction(state, transaction)


def runtime_path(path):
    return path == RUNTIME or path.startswith(RUNTIME + '/') or path == '/usr/libexec/holonight-images/.images-install.lock'


def images_command(root, state, images, check=False):
    command = ['python3', str(ROOT / 'scripts/manage-images-generations.py'), images['command'],
               '--runtime', str(root / RUNTIME.lstrip('/')), '--ownership-manifest', str(state / 'manifest.tsv'),
               '--helper', images.get('helper', str(Path(images.get('source', '/')) / 'usr/libexec/holonight-images-helper')),
               '--revision', images['revision']]
    if images['command'] == 'install':
        command += ['--source', images['source']]
    if images.get('maintenance'):
        command += ['--maintenance-migrate']
    if check:
        command += ['--check']
    else:
        command += ['--emit-manifest', '--transaction-journal', str(state / 'images-transaction.json')]
    return subprocess.check_output(command, text=True)


def images_step(root, state, transaction):
    images = transaction.get('images')
    if not images:
        return
    if transaction.get('images_done'):
        if not transaction.get('images_preserved'):
            for name, row in transaction.get('images_inventory', {}).items():
                if snapshot(root / name.lstrip('/')) != row_state(row):
                    raise ValueError(f'completed Images transaction path changed: {name}')
        return
    if transaction['removing'] and not (state / 'images-transaction.json').exists():
        try:
            images_command(root, state, images, check=True)
        except subprocess.CalledProcessError:
            # Preserve failures detected before any mutation. Failures after intent
            # publication remain pending so partial removals can resume safely.
            print('preserved managed Images runtime: modified, unowned, busy, or unverifiable; ownership records retained', file=sys.stderr)
            transaction['images_preserved'] = True
            transaction['images_done'] = True
            save_transaction(state, transaction)
            return
    rows = parse_manifest(images_command(root, state, images))
    transaction['manifest'] = {p: r for p, r in transaction['manifest'].items() if not runtime_path(p)}
    transaction['manifest'].update(rows)
    transaction['images_inventory'] = rows
    transaction['images_done'] = True
    save_transaction(state, transaction)


def refresh(root, selection, removing, state=None, transaction=None):
    hooks = {hook for name in selection for hook in CATALOG[name].hooks}
    commands = []
    if root != Path('/'):
        if 'greeter' in hooks and not removing:
            commands.append(['systemd-tmpfiles', f'--root={root}', '--create', 'holonight-greeter.conf'])
    else:
        if 'libraries' in hooks or any(name in selection for name in ('holonight-images', 'holonight-system-services', 'holonight-file-browser')):
            commands.append(['ldconfig'])
        if 'services' in hooks:
            commands.append(['systemctl', 'daemon-reload'])
        if 'desktop' in hooks:
            commands.append(['update-desktop-database', '/usr/share/applications'])
            if shutil.which('kbuildsycoca6'):
                commands.append(['env', 'XDG_MENU_PREFIX=arch-', 'kbuildsycoca6', '--noincremental'])
        if 'greeter' in hooks and not removing:
            commands.append(['systemd-tmpfiles', '--create', 'holonight-greeter.conf'])
    for command in commands:
        if transaction is not None and command in transaction.get('refresh_done', []):
            continue
        run(*command)
        if transaction is not None:
            transaction.setdefault('refresh_done', []).append(command)
            save_transaction(state, transaction)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', 'uninstall', 'deploy'))
    parser.add_argument('components', nargs='*', choices=None)
    parser.add_argument('--root', type=Path, default=Path('/'))
    parser.add_argument('--yes', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--resume', action='store_true', help='deploy saved payloads without configuring or building')
    parser.add_argument('--adopt-existing', action='store_true')
    parser.add_argument('--protected-images-runtime', action='store_true')
    parser.add_argument('--maintenance-migrate-images-runtime', action='store_true')
    parser.add_argument('--prepared', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not args.root.is_absolute() or '..' in args.root.parts:
        raise ValueError('--root must be a clean absolute path')
    ancestors(args.root / STATE)
    if args.command == 'deploy':
        deploy(args)
        return
    if args.command == 'uninstall':
        if args.root == Path('/') and os.geteuid() != 0:
            os.execvp('sudo', ['sudo', 'python3', str(Path(__file__).resolve()), *sys.argv[1:]])
        state = args.root / STATE
        with lock(state, protected=args.root == Path('/')):
            previous = read_manifest(state / 'manifest.tsv')
            transaction = pending(state)
            if args.resume and transaction and transaction['removing']:
                selection = transaction['selection']
                if args.components and set(args.components) != set(selection):
                    raise ValueError('--resume requires the saved removal selection')
            else:
                if not previous:
                    raise ValueError(f'no umbrella source-install manifest exists at {state}')
                selection = select(args.components, {row[0] for row in previous.values() if row[2] != 'd'}, removing=True)
            if args.check:
                return
            approved(args, selection)
            if transaction is None:
                transaction = new_transaction(args.root, state, selection, {}, True, False)
            elif not args.resume or not transaction['removing'] or transaction['selection'] != selection:
                raise ValueError('pending transaction exists; retry the original operation with --resume')
            if 'holonight-images' in selection and RUNTIME + '/ownership.json' in previous and 'images' not in transaction:
                candidates = [args.root / p.lstrip('/') for p, row in previous.items()
                              if p.startswith(RUNTIME + '/generations/') and p.endswith('/usr/libexec/holonight-images-helper')
                              and snapshot(args.root / p.lstrip('/')) == row_state(row)]
                transaction['images'] = {'command': 'remove', 'helper': str(candidates[0]) if candidates else '/bin/false', 'revision': 'managed'}
                transaction['actions'] = [a for a in transaction['actions'] if not runtime_path(a['path'])]
                transaction['manifest'].update({p: r for p, r in previous.items() if runtime_path(p)})
                save_transaction(state, transaction)
            execute(args.root, state, transaction)
        return
    with lock(WORK):
        if args.resume:
            if args.components:
                raise ValueError('--resume uses the saved selection; omit component names')
            attempt = Path((WORK / 'prepared.path').read_text())
            record = json.loads((attempt / 'prepared.json').read_text())
            if str(args.root) != record['root']:
                raise ValueError('--resume requires the original --root')
            validate_prepared(attempt, record)
        else:
            old = read_manifest(args.root / STATE / 'manifest.tsv')
            selection = select(args.components, {row[0] for row in old.values() if row[2] != 'd'})
            print('==> Expanded selection: ' + ', '.join(selection), flush=True)
            preflight(selection, pinned=not args.components)
            for provider in {dep for name in selection for dep in CATALOG[name].dependencies} - set(selection):
                provider_rows = {p: r for p, r in old.items() if r[0] == provider and r[2] != 'd'}
                for path, row in provider_rows.items():
                    if snapshot(args.root / path.lstrip('/')) != row_state(row):
                        raise ValueError(f'installed provider {provider} is modified or incomplete: {path}')
                # Externally installed providers are resolved and version-checked by CMake
                # during preparation, before any target deployment.
            if args.check:
                return
            attempt, record = prepare(selection, args)
        approved(args, record['selection'])
        command = ['python3', str(Path(__file__).resolve()), 'deploy', '--prepared', str(attempt), '--root', str(args.root)]
        if args.root == Path('/') and os.geteuid() != 0:
            command.insert(0, 'sudo')
        run(*command)
        if args.root == Path('/') and 'holonight-viewer' in record['selection']:
            if os.geteuid() == 0:
                print('==> Skipping Viewer preference extension for direct root installation')
            else:
                run('python3', ROOT / 'scripts/extend-viewer-defaults.py',
                    '/usr/share/applications/org.holonight.Viewer.desktop')


def pending(state):
    path = state / 'transaction.json'
    if not path.exists():
        return None
    ancestors(path)
    if os.geteuid() == 0 and (path.stat().st_uid != 0 or path.stat().st_mode & 0o022):
        raise ValueError('unprotected transaction record')
    if path.is_symlink():
        raise ValueError('unsafe transaction record')
    transaction = json.loads(path.read_text())
    return transaction if transaction['status'] != 'complete' else None


def deploy(args):
    attempt = args.prepared
    record = json.loads((attempt / 'prepared.json').read_text())
    if record['root'] != str(args.root):
        raise ValueError('saved preparation belongs to a different target root')
    validate_prepared(attempt, record)
    state = args.root / STATE
    with lock(state, protected=args.root == Path('/')):
        old = read_manifest(state / 'manifest.tsv')
        expanded = select(record['selection'], {r[0] for r in old.values() if r[2] != 'd'})
        if expanded != record['selection']:
            raise ValueError('installed dependents changed since preparation; prepare again')
        transaction = pending(state)
        if transaction and transaction.get('prepared_origin', transaction['attempt']) != str(attempt):
            raise ValueError('another deployment is pending; resume its saved payloads')
        if transaction is None:
            protected_attempt = Path(tempfile.mkdtemp(prefix='payload-', dir=state))
            for name in record['selection']:
                protected_copy(attempt / name, protected_attempt / name)
            validate_prepared(protected_attempt, record)
            atomic(protected_attempt / 'prepared.json', json.dumps(record))
            incoming = {}
            for name, component in record['components'].items():
                for path, row in component['inventory'].items():
                    if path in incoming and (row[2] != 'd' or incoming[path][2:4] != row[2:4]):
                        raise ValueError(f'duplicate payload ownership: {path}')
                    incoming[path] = (['umbrella', 'shared', *row[2:]] if row[2] == 'd' else row)
            images = None
            if not record['protected_images'] and 'holonight-images' in record['selection']:
                combined = protected_attempt / 'deployment.tsv'
                atomic(combined, manifest_text(incoming), 0o644)
                run('python3', ROOT / 'scripts/reconcile-images-runtime.py', '--root', args.root,
                    '--old-manifest', state / 'manifest.tsv', '--new-manifest', combined)
            if record['protected_images'] and 'holonight-images' in record['selection']:
                images = {'command': 'install', 'source': str(protected_attempt / 'holonight-images' / RUNTIME.lstrip('/')),
                          'revision': record['components']['holonight-images']['revision'], 'maintenance': record['maintenance']}
                images_command(args.root, state, images, check=True)
                incoming = {path: row for path, row in incoming.items() if not runtime_path(path)}
            prior = read_manifest(state / 'manifest.tsv')
            for theme in ('HoloNight', 'HoloNight-Dark'):
                name = f'/usr/share/icons/{theme}/icon-theme.cache'
                if name in incoming and name not in prior and snapshot(args.root / name.lstrip('/')) and f'/usr/share/icons/{theme}/index.theme' in prior:
                    print(f'==> Preserving unowned legacy cache: {name}')
                    incoming.pop(name)
            transaction = new_transaction(args.root, state, record['selection'], incoming, False, record['adopt'], protected_attempt, defer=True)
            transaction['prepared_origin'] = str(attempt)
            if images:
                transaction['images'] = images
                # Managed resources are exclusively changed through generation leases.
                transaction['actions'] = [a for a in transaction['actions'] if not runtime_path(a['path'])]
                transaction['manifest'].update({p: r for p, r in transaction['previous_manifest'].items() if runtime_path(p)})
            save_transaction(state, transaction)
        execute(args.root, state, transaction)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        sys.exit(f'error: {error}; prepared payloads and transaction evidence retained')
