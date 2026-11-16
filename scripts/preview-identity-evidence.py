#!/usr/bin/env python3
"""Read-only identities shared by preparation and independent verification.

No execution recipes, subprocesses, host library lookup, or build entrypoints.
"""
import importlib.util
import os
from pathlib import Path
import stat
import struct
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('identity_retained', ROOT / 'scripts/startup-applicability-evidence.py')
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h
AUDIT = ROOT / 'build/preview-startup-applicability-20261116-05'
AUDIT_SEAL = '77a96dff3b8376ad14c112218b5251d9eecd5c6519c5d1d549f08a94272528ca'
INSTALLER = ('manage-images-generations.py', 'install_state.py')
TOOLS = ('preview-identity-evidence.py', 'prepare-preview-identity-baseline.py',
         'run-preview-identity-baseline.py', 'verify-preview-identity-baseline.py')
DOC = ROOT / 'docs/initiatives/preview-identity-baseline.md'
TEST = ROOT / 'tests/test_preview_identity_baseline.py'


def protected_inputs():
    roots = {AUDIT, b.Q, b.P, b.B, b.E, b.R}
    if (AUDIT / 'integrity.json').exists():
        retained = h.read(AUDIT / 'integrity.json')
        roots.update(Path(name) for name in retained['inventories'])
        roots.update(Path(name).parent for name in retained['files']
                     if Path(name).is_relative_to(ROOT / 'build') and Path(name).parent != ROOT / 'build')
    return sorted(roots)


def ordinary(path):
    h.require(path.absolute() == path.resolve() and path.is_file(), 'symlink/foreign file: ' + str(path))
    return dict(size=path.stat().st_size, sha256=h.digest(path))


def elf_id(path):
    """Read GNU build ID without executing readelf or the retained ELF."""
    data = path.read_bytes()
    h.require(len(data) >= 64 and data[:4] == b'\x7fELF' and data[4:6] == b'\x02\x01', 'unsupported ELF identity')
    offset = struct.unpack_from('<Q', data, 32)[0]
    stride, count = struct.unpack_from('<HH', data, 54)
    h.require(stride >= 56 and offset + stride * count <= len(data), 'truncated ELF headers')
    ids = set()
    for i in range(count):
        kind, _, start, _, _, length = struct.unpack_from('<IIQQQQ', data, offset + i * stride)
        if kind != 4:
            continue
        stop = start + length
        h.require(stop <= len(data), 'truncated ELF notes')
        while start + 12 <= stop:
            names, descs, kind = struct.unpack_from('<III', data, start)
            start += 12
            h.require(start + ((names + 3) & ~3) + ((descs + 3) & ~3) <= stop, 'truncated ELF note')
            name = data[start:start + names]
            start += (names + 3) & ~3
            value = data[start:start + descs]
            start += (descs + 3) & ~3
            if kind == 3 and name == b'GNU\0':
                ids.add(value.hex())
    h.require(len(ids) <= 1, 'conflicting ELF build IDs')
    return next(iter(ids), None)


def payload(root, expected):
    """Complete nested payload membership, never an outer generation inventory."""
    h.require(h.inventory(root) == expected, 'runtime retained inventory membership/digest')
    manifest = h.read(root / 'manifest.json')
    h.require(manifest.get('version') == 1, 'runtime schema')
    rows = manifest['files']
    h.require(rows and len({r['path'] for r in rows}) == len(rows), 'runtime duplicate/empty membership')
    result = {}
    for row in rows:
        name = row['path']
        h.require(name.startswith('usr/') and '..' not in Path(name).parts, 'outer/nested inventory confusion')
        actual = ordinary(root / name)
        h.require(actual == {k: row[k] for k in ('size', 'sha256')}, 'runtime size/digest mismatch')
        result[name] = actual
    h.require(set(expected) == {'manifest.json', *result}, 'runtime missing/unlisted payload')
    return result


def retained():
    inventories, files = b.bind()
    h.require(h.digest(AUDIT / 'seal.json') == AUDIT_SEAL, 'accepted audit 05 identity')
    inventories[str(AUDIT)] = h.sealed(AUDIT)
    checked_path = AUDIT.with_name(AUDIT.name + '-independent.json')
    checked = h.read(checked_path)
    h.require(checked['status'] == 'passed' and checked['outcome'] == 'complete' and
              checked['evidence_seal'] == AUDIT_SEAL, 'accepted audit verification')
    files[str(checked_path)] = h.digest(checked_path)
    integrity = h.read(AUDIT / 'integrity.json')
    h.require(integrity['passed'] and h.recheck(integrity['inventories'], integrity['files']), 'audit chain drift')
    for name, value in integrity['files'].items():
        h.require(name not in files or files[name] == value, 'conflicting file bindings')
        files[name] = value
    provenance = h.read(b.Q / 'reuse-measurement-d0nbnsxc/provenance.json')
    historical = h.read(b.Q / 'binary-runtime-inventory.json')
    result = {}
    for variant, label, directory in [('A-fixed', 'A', 'runtime'), ('C', 'C', 'runtime-final')]:
        prefix = directory + '/'
        expected = {k[len(prefix):]: v for k, v in historical[label].items() if k.startswith(prefix)}
        root = b.Q / label / directory
        contents = payload(root, expected)
        harness = b.Q / label / 'reuse-harness/preview-benchmark'
        h.require(h.digest(harness) == historical[label]['reuse-harness/preview-benchmark'] ==
                  provenance['binaries'][label], 'qualification harness substitution')
        result[variant] = dict(harness=dict(path=str(harness), **ordinary(harness)), runtime=str(root),
                               inventory=expected, payload=contents)
        for name, value in expected.items():
            path = str(root / name)
            h.require(path not in files or files[path] == value, 'conflicting runtime bindings')
            files[path] = value
        files[str(harness)] = h.digest(harness)
    fixture = ROOT / 'build/preview-transaction-20261111-144758/fixtures/3200x2400.png'
    h.require(h.digest(fixture) == provenance['fixtures'][fixture.name], 'fixture substitution')
    files[str(fixture)] = h.digest(fixture)
    return dict(inventories=inventories, files=files, variants=result,
                fixture=dict(path=str(fixture), **ordinary(fixture)), audit_seal=AUDIT_SEAL)


def snapshots():
    paths = [ROOT / 'scripts' / name for name in (*TOOLS, *INSTALLER)] + [TEST, DOC]
    # Keep historical source verification unchanged, including its read-only modules.
    paths += list((ROOT / 'scripts').glob('*.py'))
    return {str(p): h.digest(p) for p in sorted(set(paths))}


def tree(root):
    """Outer staging view: selectors/manifest bytes, generation, modes and owners."""
    result = {}
    for path in (root, *sorted(root.rglob('*'))):
        info = path.lstat()
        row = dict(mode=stat.S_IMODE(info.st_mode), uid=info.st_uid, gid=info.st_gid)
        if stat.S_ISLNK(info.st_mode):
            h.require(path.resolve().is_relative_to(root.resolve()), 'staging symlink escape')
            row.update(kind='link', target=os.readlink(path))
        elif stat.S_ISDIR(info.st_mode):
            row.update(kind='directory')
        else:
            h.require(stat.S_ISREG(info.st_mode), 'special staging inode')
            row.update(kind='file', **ordinary(path))
            if path.name in ('manifest.json', 'ownership.json', 'diagnostic-owner.json', 'current'):
                row['bytes'] = path.read_bytes().hex()
        result[str(path.relative_to(root))] = row
    return result
