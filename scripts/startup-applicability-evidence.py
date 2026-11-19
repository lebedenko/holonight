#!/usr/bin/env python3
"""Read-only retained inputs for the C applicability audit. No recipes are imported."""
import difflib
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location('applicability_retained', Path(__file__).with_name('startup-reconciliation-evidence.py'))
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h
ROOT = h.ROOT
PINS = Path(__file__).with_name('startup-applicability-pins.json')
Q = ROOT / 'build/preview-corrected-qjln5jn4'
T = ROOT / 'build/preview-tracing-overhead-20261112'
D = ROOT / 'build/preview-delivery-overhead-20261114-03'
P = ROOT / 'build/preview-validation-20261115-04-prepared'
B = ROOT / 'build/preview-validation-20261115-04-built'
E = ROOT / 'build/preview-validation-20261115-04-execution'
CPU = ROOT / 'build/preview-cpu-profile-20261115-03-execution'
M = ROOT / 'build/preview-hash-device-mechanism-20261116-01'
R = ROOT / 'build/preview-startup-reconciliation-20261116-03'
STATUSES = ('exact identity', 'compatible under recorded transformations', 'different', 'unavailable')


def bind():
    inventories, files = b.bind()
    files[str(PINS)] = h.digest(PINS)
    def accept(path, expected):
        h.require(path.is_relative_to(ROOT / 'build') and not path.is_symlink(), 'foreign retained input')
        h.require(h.digest(path) == expected, 'retained input drift: ' + str(path))
        h.require(str(path) not in files or files[str(path)] == expected, 'conflicting bindings')
        files[str(path)] = expected
    for name, expected in h.read(PINS)['records'].items():
        accept(ROOT / name, expected)
    inventories[str(R)] = h.sealed(R)
    checked = h.read(R.with_name(R.name + '-independent.json'))
    h.require(checked['status'] == 'passed' and checked['outcome'] == 'complete' and
              checked['evidence_seal'] == h.digest(R / 'seal.json'), 'reconciliation 03 not accepted')
    integrity = h.read(R / 'integrity.json')
    h.require(integrity['passed'] and h.recheck(integrity['inventories'], integrity['files']), 'reconciliation chain drift')
    files.update(integrity['files'])
    h.require(all(inventories.get(k) == v for k, v in integrity['inventories'].items()), 'reconciliation membership conflict')
    # Historical inventories, not hashes computed now, bind qualification C.
    frozen = h.read(Q / 'freeze.json')
    source = frozen['source_inventories']['C']
    h.require(h.inventory(Q / 'C/source') == source, 'qualification C source inventory mismatch')
    for name, expected in source.items():
        accept(Q / 'C/source' / name, expected)
    for name, expected in h.read(Q / 'binary-runtime-inventory.json')['C'].items():
        accept(Q / 'C' / name, expected)
    for name, expected in h.read(Q / 'harness-inventory-final.json').items():
        accept(Q / 'harness-source' / name, expected)
    runner = Q / 'reuse-measurement-d0nbnsxc/runner.py'
    accept(Q / 'runner-final.py', h.read(Q / 'final-tooling-inventory.json')['scripts/measure-preview-reuse.py'])
    provenance = h.read(Q / 'reuse-measurement-d0nbnsxc/provenance.json')
    h.require(provenance['reference_freeze'] == h.digest(Q / 'freeze.json') and
              provenance['binaries']['C'] == frozen['candidate_binaries']['C'] ==
              files[str(Q / 'C/reuse-harness/preview-benchmark')], 'qualification C binary binding')
    h.require(all(h.read(Q / 'post-run-identity-checks.json').values()), 'qualification post-run drift')
    for name, expected in provenance['fixtures'].items():
        accept(ROOT / 'build/preview-transaction-20261111-144758/fixtures' / name, expected)
    # Selective historical inventory membership: do not demand mutable build trees
    # match an older seal, or treat an unrecorded current inventory as historical.
    pre = h.read(T / 'pre-audit-seal.json')
    prep = h.read(T / 'preparation.json')
    for variant in ('CU', 'CT'):
        for group in ('source', 'harness-source'):
            inv = prep['pairs'][variant][group]
            h.require(h.inventory(T / variant / group) == inv, 'C tracing source membership')
            for name, expected in inv.items():
                h.require(pre[variant + '/' + group + '/' + name] == expected, 'C pre-audit binding')
                accept(T / variant / group / name, expected)
    accept(T / 'C-tracing.diff', pre['C-tracing.diff'])
    seal = h.read(D / 'seal.json')
    for name in ('anchor-review.json', 'C-tracing.diff'):
        accept(D / name, seal[name])
    for variant in ('v3', 'v4'):
        for group in ('source', 'harness-source'):
            base = D / variant / 'C' / group
            actual = h.inventory(base)
            prefix = variant + '/C/' + group + '/'
            expected = {k[len(prefix):]: v for k, v in seal.items() if k.startswith(prefix)}
            h.require(actual == expected, 'delivery C membership')
            for name, digest in expected.items():
                accept(base / name, digest)
    # Every file subsequently read is in a retained inventory or an explicit pin.
    return inventories, files


def raw_sources():
    stages = [('qualification-C', Q / 'C/source', Q / 'harness-source'),
              ('CU', T / 'CU/source', T / 'CU/harness-source'),
              ('CT', T / 'CT/source', T / 'CT/harness-source'),
              ('v3-C', D / 'v3/C/source', D / 'v3/C/harness-source'),
              ('v4-C', D / 'v4/C/source', D / 'v4/C/harness-source'),
              ('baseline-C', P / 'baseline/C/source', P / 'baseline/C/harness-source'),
              ('validation-C', P / 'validation/C/source', P / 'validation/C/harness-source')]
    return [(label, {group + '/' + name: base / name for group, base in
                    [('source', source), ('harness-source', harness)] for name in h.inventory(base)})
            for label, source, harness in stages]


def diff(left, right):
    return list(difflib.unified_diff(left.decode().splitlines(), right.decode().splitlines(), lineterm=''))


def manifest(path):
    value = h.read(path)
    h.require(value.get('version') == 1 and value.get('sessionProtocol') == 1, 'wrong manifest schema')
    rows = value['files']
    h.require(rows and len({r['path'] for r in rows}) == len(rows), 'duplicate/empty manifest')
    result = {}
    for row in rows:
        name = row['path']
        h.require(not Path(name).is_absolute() and '..' not in Path(name).parts and
                  name.startswith('usr/') and isinstance(row['size'], int) and row['size'] > 0 and
                  len(row['sha256']) == 64, 'invalid nested runtime entry')
        file = path.parent / name
        h.require(file.stat().st_size == row['size'] and h.digest(file) == row['sha256'], 'manifest payload drift')
        result[name] = {k: row[k] for k in ('size', 'sha256')}
    h.require(set(h.inventory(path.parent)) == set(result) | {'manifest.json'}, 'missing/unlisted runtime entry')
    return result


def raw_payloads():
    return {'qualification-C': manifest(Q / 'C/runtime-final/manifest.json'),
            'baseline-C': manifest(B / 'baseline/C/runtime/manifest.json'),
            'validation-C': manifest(B / 'validation/C/runtime/manifest.json')}


def citation(path, needles):
    lines = path.read_text().splitlines()
    rows = [dict(line=i, text=line) for i, line in enumerate(lines, 1) if any(n in line for n in needles)]
    h.require(rows, 'missing execution-path citation: ' + str(path))
    return dict(file=str(path), sha256=h.digest(path), excerpts=rows)


def execution_records():
    """Preserve raw historical staging, mappings and populations without replay."""
    runner = Q / 'reuse-measurement-d0nbnsxc/runner.py'
    qualification = h.read(Q / 'reuse-measurement-d0nbnsxc/provenance.json')
    validation = h.read(E / 'preregistration.json')
    cpu = h.read(CPU / 'preregistration.json')
    fixtures = h.read(P / 'fixtures.json')
    h.require(fixtures == validation['fixture_hashes'] and all(
        qualification['fixtures'].get(Path(path).name) == expected for path, expected in fixtures.items()), 'fixture identity conflict')
    h.require(all(command['argv'][2] in fixtures for command in cpu['commands']), 'CPU fixture path conflict')
    for path in (E / 'stage-validation-C.json', CPU / 'stage-request.json'):
        stage = h.read(path)
        h.require(stage['built'] == str(B) and stage['built_seal'] == h.digest(B / 'seal.json') and
                  stage['mode'] == 'validation' and stage['variant'] == 'C', 'C staging binding conflict')
    h.require("('runtime-final' if label in ('B', 'C') else 'runtime')" in runner.read_text(), 'C runtime selection changed')
    return dict(fixture_binding=dict(status='exact identity', identities=fixtures,
                evidence='Qualification fixture digests; prepared fixtures.json; validation fixture_hashes; CPU command paths',
                limitation='Same fixture bytes; caches, processes, populations and execution conditions remain distinct.'),
                runner_relationship=dict(saved=str(runner), final=str(Q / 'runner-final.py'),
                saved_sha256=h.digest(runner), final_sha256=h.digest(Q / 'runner-final.py'),
                diff=diff(runner.read_bytes(), (Q / 'runner-final.py').read_bytes()), status='different',
                evidence='Saved execution runner and separately recorded final-tooling inventory',
                limitation='Saved runner is audit-checkpointed retained content, not independently historically hash-attested. Final tooling adds failure retention after this execution; it is not substituted for the saved runner.'),
                runner=citation(runner, ['source =', 'generations.run', 'helper=package', 'command =',
                                        'runtime_root', 'QT_QPA_PLATFORM', 'count =', 'warmup']),
                startup=citation(Q / 'harness-source/reuse.cpp', ['startup', 'make_unique<PreviewService>', 'clock.start', 'selected_at']),
                callers=[citation(Q / 'C/source' / name, needles) for name, needles in [
                    ('holonight-images/src/isolated/verification.cpp', ['verifyRuntime', 'hash.addData', 'file.open']),
                    ('holonight-images/src/isolated/generation.cpp', ['Generation::', 'verifyRuntime', 'refresh', 'validate']),
                    ('holonight-file-browser/src/preview/session_pool.cpp', ['refresh', 'generation_', 'Generation']),
                    ('holonight-file-browser/src/preview/preview_service.cpp', ['runtime_options_', 'refresh', 'SessionPool'])]],
                qualification=h.read(Q / 'reuse-measurement-d0nbnsxc/provenance.json'),
                staging_validation=h.read(E / 'stage-validation-C.json'), staging_cpu=h.read(CPU / 'stage-request.json'),
                validation_commands=h.read(E / 'preregistration.json'), cpu_commands=h.read(CPU / 'preregistration.json'),
                cpu_recordings=[dict(file=str(p), sha256=h.digest(p), mappings=h.read(p))
                    for p in sorted((CPU / 'observations').glob('*-recording/mirror-sources.json'))],
                validation_linkage={mode: {kind: h.read(B / mode / 'C' / (kind + '-identity.json'))
                    for kind in ('harness', 'helper')} for mode in ('baseline', 'validation')},
                cpu_protected=h.read(CPU / 'protected-runtime.json'), cpu_mirror=h.read(CPU / 'symbol-mirror.json'),
                mechanism_inputs=h.read(M / 'inputs.json'), mechanism_mappings=h.read(M / 'native-mapped-identities.json'),
                limitation='Qualification /run staging was removed by the frozen runner. No retained loaded-dependency map for that execution. Input manifest identity is not proof of actual loaded dependencies; no current host or /run files consulted.')
