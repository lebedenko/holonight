#!/usr/bin/env python3
"""Owned protected staging for the single publication observation attempt."""
import argparse
import os
from pathlib import Path
from types import SimpleNamespace
import correctness as c
import stage

h, e = c.h, c.e
OUTPUT_NAME = 'preview-cache-publication-execution-20261118-01'


def worker(output, arm, remove=False):
    h.require(os.geteuid() == 0 and arm in ('control', 'early'), 'scoped root staging required')
    h.require(output == output.resolve() and output.parent == e.ROOT / 'build' and
              output.name == OUTPUT_NAME, 'unsafe diagnostic staging request')
    binding = h.read(output / 'binding.json')['built']
    built = Path(binding['path'])
    h.require(built == built.resolve() and h.digest(built / 'seal.json') == c.BUILT_SEAL == binding['seal'],
              'staging provider binding')
    for path, digest in h.read(output / 'tools.json').items():
        h.require(h.digest(Path(path)) == digest, 'staging tool drift')
    installer = stage.load_installer()
    runtime = stage.runtime_path(output, arm)
    owner = dict(output=str(output), arm=arm, built=str(built), seal=binding['seal'])
    record = output / (arm + '-staging.json')
    if remove:
        expected = h.read(record)
        h.require(expected['owner'] == owner and c.tree(runtime) == expected['tree'], 'staging ownership/drift; retained')
        installer.run(SimpleNamespace(command='remove', runtime=runtime,
            helper=built / arm / 'runtime/usr/libexec/holonight-images-helper', source=None,
            ownership_manifest=None, maintenance_migrate=False))
        installer.remove_tree(runtime)
        h.require(not os.path.lexists(runtime), 'staging removal incomplete')
        h.write(output / (arm + '-staging-cleanup.json'), dict(removed=True, owner=owner))
    else:
        h.require(not os.path.lexists(runtime), 'staging collision')
        installer.run(SimpleNamespace(command='install', runtime=runtime, source=built / arm / 'runtime',
            helper=built / arm / 'runtime/usr/libexec/holonight-images-helper',
            ownership_manifest=None, maintenance_migrate=False))
        generation = (runtime / 'current').read_text().strip()
        payload = runtime / 'generations' / generation
        h.require(h.inventory(payload) == h.inventory(built / arm / 'runtime'), 'staged payload mismatch; retained')
        info = payload.stat()
        h.write(record, dict(owner=owner, tree=c.tree(runtime), runtime=str(runtime), generation=generation,
            generation_identity=dict(device=str(info.st_dev), inode=str(info.st_ino))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--arm', choices=('control', 'early'), required=True)
    parser.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    worker(args.output.absolute(), args.arm, args.remove)
