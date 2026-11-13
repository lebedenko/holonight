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

try:
    from install_state import read_manifest
except ModuleNotFoundError:
    from scripts.install_state import read_manifest

# The outer installer owns this protected journal and target-wide lock.
JOURNAL = None
BASE = None
MAINTENANCE = False


def journal_intent(path, source=None, data=None, remove=False):
    if JOURNAL is None or not path.is_relative_to(BASE):
        return
    record = json.loads(JOURNAL.read_text())
    states = record.setdefault('allowed', {})
    def add(target, state):
        name = str(target.relative_to(BASE))
        choices = states.setdefault(name, [])
        if not choices and not os.path.lexists(target):
            choices.append(None)
        if not choices or choices[-1] != state:
            choices.append(state)
    if remove:
        for target in (path, *path.rglob('*')) if path.is_dir() else (path,):
            add(target, None)
    elif source is not None:
        for incoming in (source, *source.rglob('*')):
            relative = incoming.relative_to(source)
            info = incoming.lstat()
            add(path / relative, ['d', format(stat.S_IMODE(info.st_mode), 'o'), '-'] if incoming.is_dir()
                else ['f', format(stat.S_IMODE(info.st_mode), 'o'), hashlib.sha256(incoming.read_bytes()).hexdigest()])
    elif data is not None:
        add(path, ['f', '644', hashlib.sha256(data).hexdigest()])
        record.setdefault('writes', {})[str(path.relative_to(BASE))] = data.decode()
    else:
        add(path, ['d', '755', '-'])
    # Journal is outside BASE, so publication cannot recursively journal itself.
    atomic_file(JOURNAL, (json.dumps(record) + '\n').encode())


def journal_start(args):
    global JOURNAL, BASE
    JOURNAL = getattr(args, 'transaction_journal', None)
    BASE = args.runtime
    if JOURNAL is None:
        return
    chain(JOURNAL.parent)
    if not JOURNAL.exists():
        journal = JOURNAL
        JOURNAL = None
        if BASE.exists():
            validate_ownership(BASE, args.ownership_manifest)
        JOURNAL = journal
        states = {}
        if BASE.exists():
            for path in (BASE, *BASE.rglob('*')):
                info = path.lstat()
                protected(path, path.is_dir())
                states[str(path.relative_to(BASE))] = [[
                    'd' if path.is_dir() else 'f', format(stat.S_IMODE(info.st_mode), 'o'),
                    '-' if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()]]
        atomic_file(JOURNAL, (json.dumps({'allowed': states, 'writes': {}}) + '\n').encode())
        return
    protected(JOURNAL, False)
    record = json.loads(JOURNAL.read_text())
    allowed = record['allowed']
    if BASE.exists():
        for path in (BASE, *BASE.rglob('*')):
            if path.name.startswith('.staging-') or any(part.startswith('.staging-') for part in path.relative_to(BASE).parts):
                raise ValueError(f'interrupted staging preserved: {path}; resolve it manually')
            info = path.lstat()
            protected(path, path.is_dir())
            state = ['d' if path.is_dir() else 'f', format(stat.S_IMODE(info.st_mode), 'o'),
                     '-' if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()]
            if state not in allowed.get(str(path.relative_to(BASE)), []):
                raise ValueError(f'transaction conflict in Images runtime: {path}')
    for name, states in allowed.items():
        if not os.path.lexists(BASE / name) and None not in states:
            raise ValueError(f'transaction resource unexpectedly missing: {BASE / name}')
    # Complete already-authorized control publications. Payloads are verified by
    # manage() before selection is consumed by a successful installer return.
    with contextlib.ExitStack() as leases:
        for name, states in allowed.items():
            path = BASE / name
            if len(Path(name).parts) == 2 and Path(name).parts[0] == 'generations' and states[-1] is None and path.exists():
                leases.enter_context(lease(path, exclusive=True))
        for name, states in sorted(allowed.items(), key=lambda item: -len(Path(item[0]).parts)):
            path = BASE / name
            if states and states[-1] is None and os.path.lexists(path):
                if path.is_dir():
                    path.rmdir()
                else:
                    path.unlink()
    for name, data in record.get('writes', {}).items():
        if name == 'ownership.json':
            data = json.dumps([generation for generation in json.loads(data)
                               if (BASE / 'generations' / generation).exists()]) + '\n'
        path = BASE / name
        if path.parent.exists():
            atomic_file(path, data.encode())


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
    journal_intent(path, data=data)
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
    journal_intent(destination, source=source)
    # rename() would replace an existing empty directory. Published names must
    # never be overwritten, even by a repeated publication or a racing tool.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.renameat2(-100, os.fsencode(source), -100, os.fsencode(destination), 1):
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))
    for parent in {source.parent, destination.parent}:
        fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


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
    journal_intent(path, remove=True)
    # Called only for freshly created staging, or an owned, validated generation
    # under an exclusive lease. Never follows links or recursively repairs it.
    for child in path.iterdir():
        if stat.S_ISDIR(child.lstat().st_mode):
            remove_tree(child)
        else:
            journal_intent(child, remove=True)
            child.unlink()
    journal_intent(path, remove=True)
    path.rmdir()


def validate_ownership(base, manifest, new_base=False, new_lock=False):
    if manifest is None:
        return
    rows = {}
    if manifest.exists():
        chain(manifest.parent)
        protected(manifest, False)
        rows = read_manifest(manifest)
    if JOURNAL is not None:
        permitted = json.loads(JOURNAL.read_text())['allowed']
        for path in (base, *base.rglob('*')):
            info = path.lstat()
            protected(path, path.is_dir())
            state = ['d' if path.is_dir() else 'f', format(stat.S_IMODE(info.st_mode), 'o'),
                     '-' if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()]
            relative = '/usr/libexec/holonight-images/runtime' + str(path)[len(str(base)):]
            row = rows.get(relative)
            if state not in permitted.get(str(path.relative_to(base)), []) and (not row or state != row[2:5]):
                raise ValueError(f'preserve unowned or modified runtime resource: {path}')
        return
    for path in (base, *base.rglob('*')):
        if MAINTENANCE and path == base / '.lock':
            info = protected(path, False)
            if info.st_size or stat.S_IMODE(info.st_mode) != 0o644:
                raise ValueError(f'preserve changed legacy lock: {path}')
            continue
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
    parent = args.runtime.parent
    ancestor = parent
    while not os.path.lexists(ancestor):
        ancestor = ancestor.parent
    chain(ancestor)
    if not getattr(args, 'check', False):
        parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    directory = parent if parent.exists() else ancestor
    chain(directory)
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        run_locked(args)
    finally:
        os.close(fd)


def run_locked(args):
    global MAINTENANCE, JOURNAL, BASE
    JOURNAL, BASE = None, args.runtime
    MAINTENANCE = getattr(args, 'maintenance_migrate', False)
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
    # Legacy lock quarantine is explicit maintenance, after full payload validation.
    if MAINTENANCE and base.exists():
        validate_ownership(base, args.ownership_manifest)
        if not (base / 'ownership.json').exists():
            # Verify the complete legacy bundle through a protected no-follow
            # copy, excluding only the reserved management lock.
            with tempfile.TemporaryDirectory(prefix='.legacy-validation-', dir=base.parent) as temporary:
                validation = Path(temporary) / 'runtime'
                validation.mkdir(mode=0o755)
                copy_tree(base, validation, exclude=('.lock',))
                verify(validation, args.helper)
        reserved = [p for p in (base / '.lock', base.parent / '.images-install.lock') if os.path.lexists(p)]
        for path in reserved:
            chain(path.parent)
            info = protected(path, False)
            if info.st_size or stat.S_IMODE(info.st_mode) != 0o644:
                raise ValueError(f'preserve changed legacy lock: {path}')
        if reserved and not check:
            journal = getattr(args, 'transaction_journal', None)
            if journal is None:
                raise ValueError('lock quarantine requires the umbrella durable transaction journal')
            quarantine = Path(tempfile.mkdtemp(prefix='legacy-lock-quarantine-', dir=journal.parent))
            evidence = [(path, path.lstat()) for path in reserved]
            atomic_file(quarantine / 'intent.json', (json.dumps([
                {'path': str(path), 'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
                 'uid': info.st_uid, 'size': info.st_size, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}
                for path, info in evidence]) + '\n').encode())
            directory = os.open(journal.parent, os.O_RDONLY | os.O_DIRECTORY)
            os.fsync(directory)
            os.close(directory)
            for index, (path, before) in enumerate(evidence):
                # Recheck immediately before moving; no adoption or deletion.
                info = protected(path, False)
                if (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (before.st_dev, before.st_ino, before.st_mode, before.st_size, before.st_mtime_ns, before.st_ctime_ns):
                    raise ValueError(f'legacy lock changed before quarantine: {path}')
                os.rename(path, quarantine / str(index))
                directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
                os.fsync(directory)
                os.close(directory)
            directory = os.open(quarantine, os.O_RDONLY | os.O_DIRECTORY)
            os.fsync(directory)
            os.close(directory)
    operation = base.parent / '.images-install.lock'
    if os.path.lexists(operation) and not MAINTENANCE:
        chain(operation.parent)
        info = protected(operation, False)
        rows = read_manifest(args.ownership_manifest) if args.ownership_manifest else {}
        row = rows.get('/usr/libexec/holonight-images/.images-install.lock')
        if (info.st_size or stat.S_IMODE(info.st_mode) != 0o644 or not row or row[0] != 'holonight-images'
                or row[2:5] != ['f', '644', hashlib.sha256(b'').hexdigest()]):
            raise ValueError(f'preserve stranded legacy operation lock: {operation}; use explicit maintenance migration')
    journal_start(args)
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
        journal_intent(base)
        base.mkdir(mode=0o755)
    chain(base)
    fd = os.open(base.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        validate_ownership(base, args.ownership_manifest, new_base)
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
        # Both sides of the conversion are authorized before the exchange.
        journal_intent(base, remove=True)
        journal_intent(base, source=replacement)
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
        # Retain the validated legacy backup for explicit maintenance review.
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
        initialized = {'generations'} if JOURNAL is not None and generation_root.is_dir() and not any(generation_root.iterdir()) else set()
        if set(p.name for p in base.iterdir()) - {'.lock'} - initialized:
            if args.command != 'install':
                raise ValueError('legacy runtime cannot be managed without maintenance conversion')
            migrate(args)
            if getattr(args, 'check', False):
                return
            return manage(args)
        owned = []
        if getattr(args, 'check', False):
            return
        journal_intent(generation_root)
        generation_root.mkdir(mode=0o755, exist_ok=True)
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
        if args.command == 'remove':
            with contextlib.ExitStack() as stack:
                for name in owned:
                    stack.enter_context(lease(generation_root / name, True))
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
            journal_intent(record, data=b'[]\n')
            for name in owned:
                remove_tree(generation_root / name)
            journal_intent(base / 'current', remove=True)
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
            journal_intent(record, data=(json.dumps([name for name in owned if name != retired]) + '\n').encode())
            remove_tree(generation_root / retired)
        owned.remove(retired)
        atomic_file(record, (json.dumps(owned) + '\n').encode())
    staging = Path(tempfile.mkdtemp(prefix='.staging-', dir=JOURNAL.parent if JOURNAL else generation_root))
    try:
        staging.chmod(0o755)
        copy_tree(args.source, staging)
        name = verify(staging, args.helper)
        if name not in owned:
            # Persist control intent before publishing the generation inode.
            journal_intent(record, data=(json.dumps([*owned, name]) + '\n').encode())
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
    parser.add_argument('--transaction-journal', type=Path)
    args = parser.parse_args()
    if args.command == 'install' and args.source is None:
        parser.error('install requires --source')
    try:
        run(args)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Images generation operation failed; resources preserved where possible: {error}\n')
