#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared conservative ownership and durable deployment state."""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

STATE = 'var/lib/holonight/source-install'
RUNTIME = '/usr/libexec/holonight-images/runtime'


def digest(path):
    return hashlib.sha256(os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()).hexdigest()


def ancestors(path):
    for parent in reversed(path.parents):
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            raise ValueError(f'unsafe installation parent: {parent}')


def protected_ancestors(path):
    ancestors(path)
    for parent in reversed(path.parents):
        if parent.exists():
            info = parent.lstat()
            if info.st_uid != 0 or info.st_mode & 0o022:
                raise ValueError(f'unprotected installation ancestor: {parent}')


def read_manifest(path):
    if not os.path.lexists(path):
        return {}
    ancestors(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'unsafe manifest: {path}')
    parent, info = path.parent.stat(), path.lstat()
    if parent.st_uid == 0 and not parent.st_mode & 0o022 and (info.st_uid != 0 or info.st_mode & 0o022):
        raise ValueError(f'unprotected ownership manifest: {path}')
    return parse_manifest(path.read_text())


def parse_manifest(text):
    rows = {}
    for line in text.splitlines():
        row = line.split('\t')
        if len(row) != 6:
            raise ValueError('invalid six-column ownership manifest')
        owner, revision, kind, mode, checksum, name = row
        parts = name.split('/')
        if (not owner or not revision or kind not in ('d', 'f', 'l') or not name.startswith('/')
                or name == '/' or any(p in ('', '.', '..') for p in parts[1:])
                or any(ord(c) < 32 for c in name) or name.startswith('/' + STATE)
                or (mode != '-' if kind == 'l' else not re.fullmatch(r'[0-7]{3,4}', mode))
                or (kind != 'l' and re.fullmatch(r'[0-7]{3,4}', mode) and int(mode, 8) > 0o777)
                or (checksum != '-' if kind == 'd' else not re.fullmatch(r'[0-9a-f]{64}', checksum))):
            raise ValueError(f'invalid ownership row: {line}')
        if name in rows:
            raise ValueError(f'duplicate ownership path: {name}')
        rows[name] = row
    for name in rows:
        for parent in Path(name).parents:
            if str(parent) in rows and rows[str(parent)][2] != 'd':
                raise ValueError(f'non-directory manifest ancestor: {parent}')
    return rows


def manifest_text(rows):
    return ''.join('\t'.join(rows[name]) + '\n' for name in sorted(rows))


def snapshot(path):
    ancestors(path)
    if not os.path.lexists(path):
        return None
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode):
        return ['l', '-', digest(path)]
    if stat.S_ISREG(info.st_mode):
        return ['f', format(stat.S_IMODE(info.st_mode), 'o'), digest(path)]
    if stat.S_ISDIR(info.st_mode):
        return ['d', format(stat.S_IMODE(info.st_mode), 'o'), '-']
    raise ValueError(f'unsupported installation entry: {path}')


def row_state(row):
    return row[2:5] if row else None


def inventory(stage, owner, revision):
    rows = {}
    for path in sorted(stage.rglob('*')):
        name = '/' + str(path.relative_to(stage))
        rows[name] = [owner, revision, *snapshot(path), name]
    return rows


def atomic(path, data, mode=0o600):
    ancestors(path)
    fd, temporary = tempfile.mkstemp(prefix='.intent-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data.encode() if isinstance(data, str) else data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync(path.parent)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def sync(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextlib.contextmanager
def lock(directory, protected=False):
    ancestors(directory)
    if protected:
        protected_ancestors(directory)
    # The public manifest remains readable to unprivileged preparation. Private
    # payload snapshots and transaction files use their own restrictive modes.
    directory.mkdir(parents=True, exist_ok=True, mode=0o755 if protected else 0o700)
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        info = os.fstat(fd)
        if protected and (info.st_uid != 0 or info.st_mode & 0o022):
            raise ValueError(f'unsafe persistent state directory: {directory}')
        fcntl.flock(fd, fcntl.LOCK_EX)
        if (info.st_dev, info.st_ino) != (directory.stat().st_dev, directory.stat().st_ino):
            raise ValueError('state directory changed while locking')
        yield
    finally:
        os.close(fd)


def protected_copy(source, destination):
    """Copy approved bytes into fresh inodes without following source links."""
    destination.mkdir(mode=0o700)
    def copy(incoming, output):
        for name in sorted(os.listdir(incoming)):
            before = os.stat(name, dir_fd=incoming, follow_symlinks=False)
            target = output / name
            if stat.S_ISDIR(before.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=incoming)
                try:
                    opened = os.fstat(child)
                    if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                        raise ValueError('source directory changed during protected copy')
                    target.mkdir(mode=stat.S_IMODE(before.st_mode))
                    copy(child, target)
                finally:
                    os.close(child)
            elif stat.S_ISLNK(before.st_mode):
                target.symlink_to(os.readlink(name, dir_fd=incoming))
            elif stat.S_ISREG(before.st_mode):
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=incoming)
                with os.fdopen(fd, 'rb') as stream, target.open('xb') as outgoing:
                    opened = os.fstat(stream.fileno())
                    if (opened.st_dev, opened.st_ino, opened.st_mode) != (before.st_dev, before.st_ino, before.st_mode):
                        raise ValueError('source file changed during protected copy')
                    remaining = before.st_size
                    while remaining:
                        chunk = stream.read(min(65536, remaining))
                        if not chunk:
                            raise ValueError('source file truncated during protected copy')
                        outgoing.write(chunk)
                        remaining -= len(chunk)
                    after = os.fstat(stream.fileno())
                    if stream.read(1) or (after.st_size, after.st_mtime_ns, after.st_ctime_ns) != (before.st_size, before.st_mtime_ns, before.st_ctime_ns):
                        raise ValueError('source file mutated during protected copy')
                    outgoing.flush()
                    os.fchmod(outgoing.fileno(), stat.S_IMODE(before.st_mode))
                    os.fsync(outgoing.fileno())
            else:
                raise ValueError(f'unsupported source entry: {name}')
        sync(output)
    fd = os.open(source, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        copy(fd, destination)
    finally:
        os.close(fd)
