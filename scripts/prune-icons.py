#!/usr/bin/env python3
"""Remove unchanged obsolete icons; print retained ownership rows on stdout."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import sys


PAYLOADS = ('/usr/share/icons/HoloNight', '/usr/share/icons/HoloNight-Dark',
            '/usr/share/holonight-icons')


def read_manifest(path):
    rows = []
    for line in path.read_text().splitlines():
        row = line.split('\t')
        if len(row) != 6:
            raise ValueError(f'Invalid ownership row in {path}')
        relative = PurePosixPath(row[5])
        if not relative.is_absolute() or '..' in relative.parts:
            raise ValueError(f'Invalid ownership path: {row[5]}')
        rows.append(row)
    return rows


def prune(root, old_manifest, new_manifest):
    current = {row[5] for row in read_manifest(new_manifest)}
    obsolete = [row for row in read_manifest(old_manifest)
                if row[0] == 'holonight-icons' and row[5] not in current
                and any(row[5] == base or row[5].startswith(base + '/') for base in PAYLOADS)]
    retained = []
    for row in sorted(obsolete, key=lambda row: row[5], reverse=True):
        _, _, kind, _, expected, relative = row
        path = root / relative.lstrip('/')
        if any(parent.is_symlink() for parent in path.parents):
            retained.append(row)
            print(f'preserved obsolete path under symlinked parent: {path}', file=sys.stderr)
            continue
        if not path.exists() and not path.is_symlink():
            continue
        if kind == 'd' and path.is_dir() and not path.is_symlink():
            try:
                path.rmdir()
                continue
            except OSError:
                pass  # Preserve nonempty directories, including unowned contents.
        else:
            data = None
            if kind == 'l' and path.is_symlink():
                data = str(path.readlink()).encode()
            elif kind == 'f' and path.is_file() and not path.is_symlink():
                data = path.read_bytes()
            if data is not None and hashlib.sha256(data).hexdigest() == expected:
                path.unlink()
                continue
        retained.append(row)
        print(f'preserved modified or nonempty obsolete icon path: {path}', file=sys.stderr)
    return retained


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--old-manifest', required=True, type=Path)
    parser.add_argument('--new-manifest', required=True, type=Path)
    args = parser.parse_args()
    if not args.root.is_absolute():
        parser.error('--root must be absolute')
    try:
        for row in prune(args.root, args.old_manifest, args.new_manifest):
            print('\t'.join(row))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'error: {exc}\n')
