#!/usr/bin/env python3
"""Check or prune obsolete payload strictly inside the Images runtime."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import stat

RUNTIME = '/usr/libexec/holonight-images/runtime'


def read_manifest(path):
    entries = {}
    if not path.exists():
        return entries
    for line in path.read_text().splitlines():
        row = line.split('\t')
        if len(row) != 6:
            raise ValueError(f'invalid ownership row in {path}')
        name = PurePosixPath(row[5])
        if not name.is_absolute() or '..' in name.parts or str(name) != row[5]:
            raise ValueError(f'invalid ownership path: {row[5]}')
        if row[5] == RUNTIME or row[5].startswith(RUNTIME + '/'):
            if row[5] in entries:
                raise ValueError(f'duplicate ownership path: {row[5]}')
            entries[row[5]] = row
    return entries


def reconcile(root, old, new, prune):
    previous = read_manifest(old)
    current = read_manifest(new)
    if not current:
        return
    base = root / RUNTIME.lstrip('/')
    conflicts = []
    obsolete = []
    for parent in (base, *base.parents):
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            raise ValueError(f'{parent}: unsafe runtime parent; move it outside the runtime or resolve it manually')

    def inspect(path):
        relative = '/' + str(path.relative_to(root))
        mode = path.lstat().st_mode
        kind = 'd' if stat.S_ISDIR(mode) else 'f' if stat.S_ISREG(mode) else '?'
        row = previous.get(relative)
        staged = current.get(relative)
        reason = None
        if kind == '?':
            reason = 'symlink or unsupported entry type'
        elif staged and staged[2] != kind:
            reason = 'incompatible entry type'
        elif kind == 'f' and (row is None or row[0] != 'holonight-images' or row[2] != 'f'):
            reason = 'unowned runtime file'
        elif not staged:
            if row is None or row[2] != kind:
                reason = 'unowned obsolete entry'
            elif kind == 'f' and (format(stat.S_IMODE(mode), 'o') != row[3]
                                  or hashlib.sha256(path.read_bytes()).hexdigest() != row[4]):
                reason = 'modified obsolete file'
            else:
                obsolete.append(path)
        if reason:
            conflicts.append(f'{path}: {reason}; move it outside the runtime or resolve it manually')
        if kind == 'd':
            for child in sorted(path.iterdir()):
                inspect(child)

    if base.exists():
        inspect(base)
    for name, row in current.items():
        if row[2] not in ('f', 'd') or (row[2] == 'f' and row[0] != 'holonight-images'):
            conflicts.append(f'{name}: invalid staged runtime ownership or type')
    if conflicts:
        raise ValueError('\n'.join(conflicts))
    if prune:
        for path in sorted(obsolete, key=lambda p: len(p.parts), reverse=True):
            if path.is_dir():
                path.rmdir()  # Any unexpected contents must block, never be removed recursively.
            else:
                path.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--old-manifest', required=True, type=Path)
    parser.add_argument('--new-manifest', required=True, type=Path)
    parser.add_argument('--prune', action='store_true')
    args = parser.parse_args()
    if not args.root.is_absolute() or '..' in args.root.parts:
        parser.error('--root must be an absolute path without ..')
    try:
        reconcile(args.root, args.old_manifest, args.new_manifest, args.prune)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Images runtime reconciliation failed: {exc}\n')
