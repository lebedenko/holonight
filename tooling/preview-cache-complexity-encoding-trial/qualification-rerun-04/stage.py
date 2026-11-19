#!/usr/bin/env python3
"""Scoped protected-generation staging using the conservative umbrella installer."""
import argparse
import hashlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace
import correctness as c

h, e = c.h, c.e


def runtime_path(output, arm):
    return Path('/run') / ('holonight-directional-' + hashlib.sha256(str(output).encode()).hexdigest()[:20] + '-' + arm)


def load_installer():
    # Match direct script execution so the installer's sibling imports resolve under sudo.
    previous = list(sys.path)
    sys.path.insert(0, str(e.ROOT / 'scripts'))
    try:
        return e.load('publication_installer', e.ROOT / 'scripts/manage-images-generations.py')
    finally:
        sys.path[:] = previous


def worker(output, arm, remove=False):
    h.require(os.geteuid() == 0 and arm in ('control', 'candidate'), 'scoped root staging required')
    h.require(output == output.resolve() and output.parent == e.ROOT / 'build' and
              output.name in (c.t.CORRECTNESS.name, c.t.EXECUTION.name), 'unsafe staging request')
    binding = h.read(output / 'built.json')
    built = Path(binding['path'])
    h.require(h.digest(built / 'seal.json') == binding['seal'] and built == c.t.BUILT, 'staging build binding')
    for name, digest in h.read(output / 'tools.json').items():
        h.require(h.digest(Path(name)) == digest, 'staging tool drift')
    installer = load_installer()
    runtime = runtime_path(output, arm)
    owner = dict(output=str(output), arm=arm, built=str(built), seal=binding['seal'])
    owner_path = output / (arm + '-staging.json')
    if remove:
        expected = h.read(owner_path)
        h.require(expected['owner'] == owner and c.tree(runtime) == expected['tree'], 'staging ownership/drift; retained')
        installer.run(SimpleNamespace(command='remove', runtime=runtime,
            helper=built / arm / 'runtime/usr/libexec/holonight-images-helper', source=None,
            ownership_manifest=None, maintenance_migrate=False))
        installer.remove_tree(runtime)
        # The installer removes only its owned tree and refuses changed contents.
        h.require(not os.path.lexists(runtime), 'staging removal incomplete')
        h.write(output / (arm + '-staging-cleanup.json'), dict(removed=True, owner=owner))
    else:
        c.t.prerequisite()
        c.t.phase_proof(built, 'built')
        h.require(not os.path.lexists(runtime), 'staging collision')
        installer.run(SimpleNamespace(command='install', runtime=runtime, source=built / arm / 'runtime',
            helper=built / arm / 'runtime/usr/libexec/holonight-images-helper',
            ownership_manifest=None, maintenance_migrate=False))
        generation = (runtime / 'current').read_text().strip()
        h.require(h.inventory(runtime / 'generations' / generation) == h.inventory(built / arm / 'runtime'),
                  'staged payload mismatch; retained')
        h.write(owner_path, dict(owner=owner, tree=c.tree(runtime), runtime=str(runtime)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--arm', choices=('control', 'candidate'), required=True)
    parser.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    worker(args.output.absolute(), args.arm, args.remove)
