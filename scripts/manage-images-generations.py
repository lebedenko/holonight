#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Publish protected Images generations without adopting or overwriting inodes.

Requires root and protected ancestors. Standalone mutable DESTDIR installation
continues to use CMake. This tool never repairs ownership. Legacy conversion is
intentionally rejected unless --maintenance-migrate is supplied: all image
consumers must be stopped before that initial conversion.
"""
import argparse
import contextlib
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

POLICY = b'holonight-images-policy-1\n'
NAME = re.compile(r'[0-9a-f]{64}')


def protected(path, directory=True):
    info = path.lstat()
    if info.st_uid != 0 or info.st_mode & 0o022 or not (
            stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)):
        raise ValueError(f'preserve unsafe or unowned resource: {path}')
    return info


def chain(path):
    for parent in reversed((path, *path.parents)):
        protected(parent)


def identity(manifest):
    return hashlib.sha256(POLICY + manifest).hexdigest()


def atomic_file(path, data):
    fd, temporary = tempfile.mkstemp(prefix='.publish-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), 0o644)
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def publish(source, destination):
    # rename() would replace an existing empty directory. Published names must
    # never be overwritten, even by a repeated publication or a racing tool.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.renameat2(-100, os.fsencode(source), -100, os.fsencode(destination), 1):
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def copy_tree(source, destination, exclude=()):
    count = total = 0

    def copy(directory_fd, output):
        nonlocal count, total
        for name in sorted(os.listdir(directory_fd)):
            if output == destination and name in exclude:
                continue
            before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if stat.S_ISDIR(before.st_mode):
                fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd)
                try:
                    if (before.st_dev, before.st_ino) != (os.fstat(fd).st_dev, os.fstat(fd).st_ino):
                        raise ValueError('source directory changed during copy')
                    (output / name).mkdir(mode=0o755)
                    copy(fd, output / name)
                finally:
                    os.close(fd)
            elif stat.S_ISREG(before.st_mode):
                count += 1
                total += before.st_size
                if count > 128 or total > 128 * 1024 * 1024 or stat.S_IMODE(before.st_mode) not in (0o644, 0o755):
                    raise ValueError('source runtime exceeds bounds or contains an invalid mode')
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
                with os.fdopen(fd, 'rb') as incoming, (output / name).open('xb') as outgoing:
                    opened = os.fstat(incoming.fileno())
                    if (opened.st_dev, opened.st_ino, opened.st_mode) != (before.st_dev, before.st_ino, before.st_mode):
                        raise ValueError('source file changed during copy')
                    remaining = before.st_size
                    while remaining:
                        chunk = incoming.read(min(65536, remaining))
                        if not chunk:
                            raise ValueError('source truncated during copy')
                        outgoing.write(chunk)
                        remaining -= len(chunk)
                    after = os.fstat(incoming.fileno())
                    if incoming.read(1) or (after.st_size, after.st_mtime_ns, after.st_ctime_ns) != (
                            before.st_size, before.st_mtime_ns, before.st_ctime_ns):
                        raise ValueError('source mutated during copy')
                    os.fchmod(outgoing.fileno(), stat.S_IMODE(before.st_mode))
            else:
                raise ValueError(f'source symlink or unsupported entry: {name}')
    fd = os.open(source, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        copy(fd, destination)
    finally:
        os.close(fd)


def verify(path, helper):
    chain(path)
    subprocess.run([str(helper), '--verify-protected-runtime', str(path)], check=True, timeout=30)
    name = identity((path / 'manifest.json').read_bytes())
    if NAME.fullmatch(path.name) and path.name != name:
        raise ValueError(f'preserve modified generation: {path}')
    return name


@contextlib.contextmanager
def lease(path, exclusive=False):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        fcntl.flock(fd, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        opened, current = os.fstat(fd), path.lstat()
        if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            raise ValueError(f'generation identity changed: {path}')
        yield
    finally:
        os.close(fd)


def remove_tree(path):
    # Called only for freshly created staging, or an owned, validated generation
    # under an exclusive lease. Never follows links or recursively repairs it.
    for child in path.iterdir():
        if stat.S_ISDIR(child.lstat().st_mode):
            remove_tree(child)
        else:
            child.unlink()
    path.rmdir()


def validate_ownership(base, manifest, new_base=False, new_lock=False):
    if manifest is None:
        return
    rows = {}
    if manifest.exists():
        chain(manifest.parent)
        protected(manifest, False)
        for line in manifest.read_text().splitlines():
            row = line.split('\t')
            if len(row) != 6:
                raise ValueError('invalid umbrella ownership row')
            if row[5] in rows:
                raise ValueError('duplicate umbrella ownership path')
            rows[row[5]] = row
    for path in (base, *base.rglob('*')):
        if (new_base and path == base) or (new_lock and path == base / '.lock'):
            continue
        relative = '/usr/libexec/holonight-images/runtime' + str(path)[len(str(base)):]
        row = rows.get(relative)
        info = path.lstat()
        directory = stat.S_ISDIR(info.st_mode)
        protected(path, directory)
        if not row or row[0] not in (('holonight-images', 'umbrella') if directory else ('holonight-images',)) or row[2] != ('d' if directory else 'f') or int(row[3], 8) != stat.S_IMODE(info.st_mode):
            raise ValueError(f'preserve unowned or modified runtime resource: {path}; resolve it manually')
        if not directory and hashlib.sha256(path.read_bytes()).hexdigest() != row[4]:
            raise ValueError(f'preserve modified runtime file: {path}; resolve it manually')


def operation_lock(args):
    parent = args.runtime.parent
    ancestor = parent
    while not os.path.lexists(ancestor):
        ancestor = ancestor.parent
    chain(ancestor)
    parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    chain(parent)
    path = parent / '.images-install.lock'
    try:
        fd = os.open(path, os.O_RDONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o644)
    except FileExistsError:
        # An interrupted first installation or an unrelated root-owned file is
        # preserved until explicitly resolved; never silently adopt a collision.
        if args.ownership_manifest is None or not args.ownership_manifest.exists():
            raise ValueError(f'preserve unowned operation lock: {path}; resolve it manually')
        chain(args.ownership_manifest.parent)
        protected(args.ownership_manifest, False)
        relative = '/usr/libexec/holonight-images/.images-install.lock'
        rows = [line.split('\t') for line in args.ownership_manifest.read_text().splitlines()]
        expected = hashlib.sha256(b'').hexdigest()
        if not any(len(row) == 6 and row[0] == 'holonight-images' and row[2:] == ['f', '644', expected, relative] for row in rows):
            raise ValueError(f'preserve unowned operation lock: {path}; resolve it manually')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = protected(path, False)
        if info.st_size != 0:
            raise ValueError(f'preserve modified operation lock: {path}')
        print(path)
    finally:
        os.close(fd)


def run(args):
    if os.geteuid() != 0:
        raise ValueError('protected generation management requires root')
    base = args.runtime
    if not base.is_absolute() or '..' in base.parts:
        raise ValueError('runtime must be a clean absolute path')
    if args.command == 'operation-lock':
        operation_lock(args)
        return
    check = getattr(args, 'check', False)
    ancestor = base.parent
    while not os.path.lexists(ancestor):
        ancestor = ancestor.parent
    chain(ancestor)
    if args.command == 'install':
        subprocess.run([str(args.helper), '--verify-runtime', str(args.source)], check=True, timeout=30)
    new_base = not os.path.lexists(base)
    if check:
        if new_base:
            return
        chain(base)
        validate_ownership(base, args.ownership_manifest)
        manage(args)
        return
    base.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    chain(base.parent)
    if new_base:
        base.mkdir(mode=0o755)
    chain(base)
    lock = base / '.lock'
    new_lock = False
    try:
        fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o644)
        new_lock = True
    except FileExistsError:
        fd = os.open(lock, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        protected(lock, False)
        fcntl.flock(fd, fcntl.LOCK_EX)
        validate_ownership(base, args.ownership_manifest, new_base, new_lock)
        manage(args)
        if getattr(args, 'emit_manifest', False):
            inventory(base, args.revision)
    finally:
        os.close(fd)


def migrate(args):
    """Maintenance-only conversion after validating every legacy ownership row."""
    base = args.runtime
    if not args.maintenance_migrate or args.ownership_manifest is None:
        raise ValueError('legacy migration requires --maintenance-migrate and --ownership-manifest; stop all image consumers')
    rows = {}
    for line in args.ownership_manifest.read_text().splitlines():
        row = line.split('\t')
        if len(row) != 6:
            raise ValueError('invalid legacy ownership record')
        if row[5] == '/usr/libexec/holonight-images/runtime' or row[5].startswith('/usr/libexec/holonight-images/runtime/'):
            if row[5] in rows:
                raise ValueError('duplicate legacy ownership record')
            rows[row[5]] = row
    for path in (base, *base.rglob('*')):
        if path == base / '.lock':
            continue
        relative = '/usr/libexec/holonight-images/runtime' + str(path)[len(str(base)):]
        row = rows.get(relative)
        info = path.lstat()
        directory = stat.S_ISDIR(info.st_mode)
        protected(path, directory)
        if not row or row[0] not in (('holonight-images', 'umbrella') if directory else ('holonight-images',)) or row[2] != ('d' if directory else 'f') or int(row[3], 8) != stat.S_IMODE(info.st_mode):
            raise ValueError(f'preserve unowned or modified legacy resource: {path}')
        if not directory and hashlib.sha256(path.read_bytes()).hexdigest() != row[4]:
            raise ValueError(f'preserve modified legacy file: {path}')
    # The management lock is outside the runtime inventory. Remove it only from
    # the copied inventory, never from the live locked base before replacement.
    if getattr(args, 'check', False):
        return
    replacement = Path(tempfile.mkdtemp(prefix='.images-conversion-', dir=base.parent))
    replacement.chmod(0o755)
    stage = replacement / 'legacy'
    stage.mkdir()
    exchanged = False
    try:
        # Copy only inventory contents through no-follow descriptors. The lock
        # is excluded from inventory and shared across the atomic conversion.
        copy_tree(base, stage, exclude=('.lock',))
        validate_ownership(stage, args.ownership_manifest)
        name = verify(stage, args.helper)
        (replacement / 'generations').mkdir(mode=0o755)
        publish(stage, replacement / 'generations' / name)
        atomic_file(replacement / 'ownership.json', (json.dumps([name]) + '\n').encode())
        atomic_file(replacement / 'current', (name + '\n').encode())
        os.link(base / '.lock', replacement / '.lock', follow_symlinks=False)
        # Linux RENAME_EXCHANGE atomically swaps directories without a missing
        # runtime window. Maintenance is still mandatory for legacy workers.
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.renameat2(-100, os.fsencode(replacement), -100, os.fsencode(base), 2):
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
        exchanged = True
        try:
            validate_ownership(replacement, args.ownership_manifest, new_lock=True)
        except (OSError, ValueError) as error:
            raise ValueError(f'legacy layout changed during conversion; preserve backup {replacement}: {error}') from error
        remove_tree(replacement)
    finally:
        if replacement.exists() and not exchanged:
            remove_tree(replacement)


def manage(args):
    base = args.runtime
    record = base / 'ownership.json'
    generation_root = base / 'generations'
    if record.exists():
        protected(record, False)
        owned = json.loads(record.read_text())
        if not isinstance(owned, list) or len(owned) > 2 or len(set(owned)) != len(owned) or any(
                not isinstance(name, str) or not NAME.fullmatch(name) for name in owned):
            raise ValueError('invalid generation ownership record')
        protected(generation_root)
    else:
        if set(p.name for p in base.iterdir()) - {'.lock'}:
            if args.command != 'install':
                raise ValueError('legacy runtime cannot be managed without maintenance conversion')
            migrate(args)
            if getattr(args, 'check', False):
                return
            return manage(args)
        owned = []
        if getattr(args, 'check', False):
            return
        generation_root.mkdir(mode=0o755)
    if set(p.name for p in generation_root.iterdir()) != set(owned):
        raise ValueError('preserve unowned generation or interrupted staging; resolve it manually')
    unexpected = set(p.name for p in base.iterdir()) - {'.lock', 'ownership.json', 'generations', 'current'}
    if unexpected:
        raise ValueError(f'preserve unowned runtime resources: {sorted(unexpected)}')
    current = None
    if os.path.lexists(base / 'current'):
        protected(base / 'current', False)
        selected = (base / 'current').read_bytes()
        if len(selected) != 65 or not selected.endswith(b'\n'):
            raise ValueError('invalid current selector')
        current = selected[:-1].decode('ascii')
        if current not in owned:
            raise ValueError('selector names an unowned generation')
    for name in owned:
        verify(generation_root / name, args.helper)
    if args.command == 'validate':
        return
    if getattr(args, 'check', False):
        if args.command == 'install':
            requested = identity((args.source / 'manifest.json').read_bytes())
            if requested not in owned and len(owned) == 2:
                if current is None:
                    raise ValueError('missing current selector; explicitly roll back before upgrading')
                retired = next(name for name in owned if name != current)
                with lease(generation_root / retired, True):
                    pass
        return
    if args.command == 'rollback':
        if args.generation not in owned:
            raise ValueError('rollback requires an owned retained generation')
        with lease(generation_root / args.generation):
            atomic_file(base / 'current', (args.generation + '\n').encode())
        return
    if args.command == 'remove':
        # Acquire every exclusive lease before removing anything. Busy or
        # modified generations preserve selection and ownership for a retry.
        with contextlib.ExitStack() as stack:
            for name in owned:
                stack.enter_context(lease(generation_root / name, True))
            for name in owned:
                remove_tree(generation_root / name)
            (base / 'current').unlink(missing_ok=True)
            atomic_file(record, b'[]\n')
        return
    source_manifest = args.source / 'manifest.json'
    if not stat.S_ISREG(source_manifest.lstat().st_mode) or source_manifest.stat().st_size > 1024 * 1024:
        raise ValueError('invalid source manifest')
    requested = identity(source_manifest.read_bytes())
    if requested in owned:
        subprocess.run([str(args.helper), '--verify-runtime', str(args.source)], check=True, timeout=30)
        atomic_file(base / 'current', (requested + '\n').encode())
        return
    # Prune an eligible retired generation before staging a third. Keep its
    # ownership until removal succeeds; never change selection on a busy lease.
    if len(owned) == 2:
        if current is None:
            raise ValueError('missing current selector; explicitly roll back before upgrading')
        retired = next(name for name in owned if name != current)
        with lease(generation_root / retired, True):
            verify(generation_root / retired, args.helper)
            remove_tree(generation_root / retired)
        owned.remove(retired)
        atomic_file(record, (json.dumps(owned) + '\n').encode())
    staging = Path(tempfile.mkdtemp(prefix='.staging-', dir=generation_root))
    try:
        staging.chmod(0o755)
        copy_tree(args.source, staging)
        name = verify(staging, args.helper)
        if name not in owned:
            publish(staging, generation_root / name)
            owned.append(name)
            # Record publication before selecting it. A crash never leaves a
            # selected unowned generation eligible for generic removal.
            atomic_file(record, (json.dumps(owned) + '\n').encode())
        atomic_file(base / 'current', (name + '\n').encode())
    finally:
        if staging.exists():
            remove_tree(staging)


def inventory(base, revision):
    paths = [base, *base.rglob('*')]
    operation = base.parent / '.images-install.lock'
    if operation.exists():
        paths.append(operation)
    for path in sorted(paths):
        info = path.lstat()
        directory = stat.S_ISDIR(info.st_mode)
        protected(path, directory)
        relative = ('/usr/libexec/holonight-images/.images-install.lock' if path == base.parent / '.images-install.lock' else '/usr/libexec/holonight-images/runtime' + str(path)[len(str(base)):])
        digest = '-' if directory else hashlib.sha256(path.read_bytes()).hexdigest()
        print('\t'.join(('holonight-images', revision, 'd' if directory else 'f',
                         format(stat.S_IMODE(info.st_mode), 'o'), digest, relative)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', 'rollback', 'remove', 'validate', 'operation-lock'))
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--helper', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--generation')
    parser.add_argument('--maintenance-migrate', action='store_true')
    parser.add_argument('--ownership-manifest', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--emit-manifest', action='store_true')
    parser.add_argument('--revision', default='managed')
    args = parser.parse_args()
    if args.command == 'install' and args.source is None:
        parser.error('install requires --source')
    try:
        run(args)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Images generation operation failed; resources preserved where possible: {error}\n')
