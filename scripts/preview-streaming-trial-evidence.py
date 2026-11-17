#!/usr/bin/env python3
"""Read-only trial evidence boundary. No runner, build recipes, or process API."""
import difflib
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('streaming_retained', Path(__file__).with_name('preview-identity-review-evidence.py'))
r = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r)
h = r.h
ROOT = h.ROOT
Q = r.e.b.Q
REVIEW = ROOT / 'build/preview-identity-review-20261117-03'
REVIEW_SEAL = '5856c6e014e06c2a356baddb078b39ae79f0e82af4a24eacf7957e2cd7705ac9'
RELATIVE = 'holonight-images/src/isolated/verification.cpp'
ARMS = ('control', 'candidate')
DOC = ROOT / 'docs/initiatives/preview-streaming-trial.md'
TOOLS = [ROOT / 'scripts' / n for n in ('preview-streaming-trial-evidence.py',
    'run-preview-streaming-trial.py', 'verify-preview-streaming-trial.py',
    'run-preview-identity-baseline.py', 'run-preview-cpu-profile.py',
    'run-preview-delivery-scheduler.py', 'manage-images-generations.py', 'install_state.py')]


def tools():
    paths = set(TOOLS) | h.tool_paths(r)
    paths |= {ROOT / 'tests/test_preview_streaming_trial.py', DOC}
    paths |= set((ROOT / 'tooling/preview-streaming-trial').glob('*'))
    # Snapshot the transitive runner support modules without importing them.
    paths |= set((ROOT / 'scripts').glob('*.py'))
    return {str(p): h.digest(p) for p in sorted(paths) if p.is_file()}


def check_tools(root):
    identities = h.read(root / 'tools.json')
    h.require(identities == tools(), 'tool drift')
    h.require(len({Path(name).name for name in identities}) == len(identities), 'snapshot name collision')
    for name, digest in identities.items():
        h.require(h.digest(root / 'tools' / Path(name).name) == digest, 'tool snapshot drift')
    return identities


def retained():
    value = r.bind()
    h.require(h.digest(REVIEW / 'seal.json') == REVIEW_SEAL, 'accepted review identity')
    r.merge(value['inventories'], {str(REVIEW): r.accepted(REVIEW, 'complete', 'evidence_seal')})
    r.merge(value['files'], {str(REVIEW / 'seal.json'): REVIEW_SEAL,
        str(REVIEW.with_name(REVIEW.name + '-independent.json')):
        h.digest(REVIEW.with_name(REVIEW.name + '-independent.json'))})
    source = h.read(Q / 'freeze.json')['source_inventories']['C']
    harness = h.read(Q / 'harness-inventory-final.json')
    h.require(h.inventory(Q / 'C/source') == source and h.inventory(Q / 'harness-source') == harness,
              'complete frozen C source/harness membership')
    for root, inventory in ((Q / 'C/source', source), (Q / 'harness-source', harness)):
        r.merge(value['files'], {str(root / name): digest for name, digest in inventory.items()})
    fixture = ROOT / 'build/preview-transaction-20261111-144758/fixtures/3200x2400.png'
    expected = h.read(Q / 'reuse-measurement-d0nbnsxc/provenance.json')['fixtures'][fixture.name]
    r.merge(value['files'], {str(fixture): expected})
    h.require(h.digest(fixture) == expected, 'fixture binding')
    value.update(source=source, harness=harness, fixture=dict(path=str(fixture), sha256=expected))
    return value


def transformed(original, loop):
    """Only the hashing loop changes; the buffer is reused across runtime files."""
    anchor = '  for (auto value : manifest["files"].toArray()) {'
    condition = '!hash.addData(&file)'
    h.require(original.count(anchor) == 1 and original.count(condition) == 1, 'candidate literal anchors')
    return original.replace(anchor, '  char runtimeHashBuffer[65536];\n' +
        '\n'.join('  ' + line for line in loop.splitlines()) + '\n' + anchor, 1).replace(
        condition, '!streamRuntimeHash(file, hash, info.st_size, runtimeHashBuffer)', 1)


def check_package(package, provenance=False):
    h.sealed(package)
    h.require(h.read(package / 'assessment.json')['status'] == 'prepared', 'preparation incomplete')
    inputs = h.read(package / 'inputs.json')
    if provenance:
        h.require(inputs == retained(), 'retained preparation binding')
    h.require(h.recheck(inputs['inventories'], inputs['files']), 'retained input drift')
    check_tools(package)
    loop = (package / 'tools/hash-loop.inc').read_text()
    for arm in ARMS:
        for group, origin, inventory in (('source', Q / 'C/source', inputs['source']),
                                        ('harness-source', Q / 'harness-source', inputs['harness'])):
            target = package / arm / group
            h.require(set(h.inventory(target)) == set(inventory), 'private source membership')
            for name in inventory:
                expected = (origin / name).read_bytes()
                if arm == 'candidate' and group == 'source' and name == RELATIVE:
                    expected = transformed(expected.decode(), loop).encode()
                h.require((target / name).read_bytes() == expected, 'private source transformation: ' + name)
    original = (package / 'control/source' / RELATIVE).read_text()
    candidate = (package / 'candidate/source' / RELATIVE).read_text()
    expected_diff = ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
        fromfile='control/' + RELATIVE, tofile='candidate/' + RELATIVE))
    h.require((package / 'candidate.diff').read_text() == expected_diff, 'candidate patch drift')
    h.require(h.digest(package / '3200x2400.png') == inputs['fixture']['sha256'], 'private fixture drift')
    return inputs


def check_built(built):
    h.sealed(built)
    check_tools(built)
    assessment = h.read(built / 'assessment.json')
    h.require(assessment['status'] == 'built', 'build incomplete')
    binding = h.read(built / 'package.json')
    package = Path(binding['path'])
    h.require(h.digest(package / 'seal.json') == binding['seal'], 'build/package binding')
    h.require(h.read(built / 'correctness.json')['passed'], 'native correctness incomplete')
    runtimes = {}
    for arm in ARMS:
        base = built / arm
        runtimes[arm] = r.e.payload(base / 'runtime', h.read(base / 'runtime-inventory.json'))
        h.require(runtimes[arm]['usr/libexec/holonight-images-helper']['sha256'] ==
                  h.digest(base / 'build/holonight-images/holonight-images-helper'), 'matching runtime helper')
        h.require(h.read(base / 'identities.json') == {name: dict(sha256=h.digest(base / path),
                  build_id=r.e.elf_id(base / path)) for name, path in
                  [('helper', 'build/holonight-images/holonight-images-helper'), ('harness', 'reuse-harness/preview-benchmark')]},
                  'native binary identity')
        resolutions = h.read(base / 'package-resolution.json')
        h.require(set(resolutions) == {'HolonightImages_DIR', 'HolonightThumbnails_DIR',
                  'HolonightFileBrowser_DIR'}, 'missing installed provider binding')
        for provider, resolved in resolutions.items():
            h.require(Path(resolved).is_relative_to(base / 'prefix'), 'consumer used foreign provider: ' + provider)
    h.require(runtimes['control'].keys() == runtimes['candidate'].keys(), 'dependency payload membership differs')
    changed = [name for name in runtimes['control'] if runtimes['control'][name] != runtimes['candidate'][name]]
    h.require(set(changed) <= {'usr/libexec/holonight-images-helper'}, 'unexplained dependency payload changes')
    h.require(h.read(built / 'runtime-comparison.json') == dict(changed=changed,
              explanation='Only the candidate helper and corresponding manifest identity may differ.'), 'runtime comparison drift')
    for path, digest in h.read(built / 'host-dependencies.json').items():
        h.require(h.digest(Path(path)) == digest, 'host dependency drift: ' + path)
    return package


def sample(value):
    import math
    rows = value.get('samples', [])
    h.require(len(rows) == 1 and not value.get('cleanup_failure'), 'sample count/cleanup')
    row = rows[0]
    h.require(all(row.get(k) is True for k in ('success', 'setup_success', 'correct_pixels', 'correct_metadata'))
              and not row.get('cleanup_failure') and not row.get('harness_timeout'), 'startup correctness')
    h.require(all(type(row.get(k)) in (int, float) and math.isfinite(row[k]) for k in ('first_ms', 'final_ms'))
              and 0 <= row['first_ms'] <= row['final_ms'], 'startup timers')
    return row
