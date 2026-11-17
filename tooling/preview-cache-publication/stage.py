#!/usr/bin/env python3
"""Scoped protected-generation staging using the conservative umbrella installer."""
import argparse
import hashlib
import os
from pathlib import Path
from types import SimpleNamespace
import correctness as c

h, e = c.h, c.e


def runtime_path(output, arm):
    return Path('/run') / ('holonight-publication-' + hashlib.sha256(str(output).encode()).hexdigest()[:20] + '-' + arm)


def worker(output, arm, remove=False):
    h.require(os.geteuid() == 0 and arm in ('control', 'early'), 'scoped root staging required')
    h.require(output == output.resolve() and output.parent == e.ROOT / 'build' and
              output.name == 'preview-cache-publication-correctness-20261118-02', 'unsafe staging request')
    binding = h.read(output / 'built.json')
    built = Path(binding['path'])
    h.require(h.digest(built / 'seal.json') == c.BUILT_SEAL == binding['seal'], 'staging build binding')
    for name, digest in h.read(output / 'tools.json').items():
        h.require(h.digest(Path(name)) == digest, 'staging tool drift')
    installer = e.load('publication_installer', e.ROOT / 'scripts/manage-images-generations.py')
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
    parser.add_argument('--arm', choices=('control', 'early'), required=True)
    parser.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    worker(args.output.absolute(), args.arm, args.remove)
