#!/usr/bin/env python3
"""Prepare a sealed, offline v4-versus-v3 comparison; never launch processes."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ('source', 'harness-source')
SUPPORT = ('preview-delivery-runtime-smoke-20261113-02',
           'preview-delivery-gaps-v4-analysis-20261114-04',
           'preview-delivery-source-review-20261114-01')
WARNING = 'uncompiled, unexecuted, overhead unmeasured'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    result = {}
    require(root.is_dir(), 'missing tree: ' + str(root))
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), 'symlink: ' + str(path))
        if path.is_file():
            result[str(path.relative_to(root))] = digest(path)
    return result


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def child(root, name):
    path = root / name
    require(not Path(name).is_absolute() and '..' not in Path(name).parts,
            'unsafe relative path: ' + str(name))
    require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),
            'path escapes input: ' + str(path))
    return path


def schedule():
    rows = []
    for fixture in ('160x80.png', '3200x2400.png', 'oriented.jpg'):
        for variant in 'ABCD':
            for mode in ('v3', 'v4'):
                rows.append(dict(fixture=fixture, variant=variant, mode=mode,
                                 warmup=True, block=None, observations=1))
        for block in range(10):
            variants = 'ABCD'[block % 4:] + 'ABCD'[:block % 4]
            for variant in variants:
                for mode in (('v3', 'v4') if block % 2 == 0 else ('v4', 'v3')):
                    rows.append(dict(fixture=fixture, variant=variant, mode=mode,
                                     warmup=False, block=block, observations=10))
    return rows


def probes(base, supplemental):
    rows = []
    for group in GROUPS:
        for path in sorted((base / group).rglob('*.cpp')):
            for line, text in enumerate(path.read_text().splitlines(), 1):
                matched = ('DeliveryTrace::' in text or 'delivery_' in text) if supplemental else 'StandbyTrace::' in text
                if matched:
                    rows.append(dict(file=str(path), line=line, text=text, sha256=digest(path)))
    return rows


def replay(trees, anchors):
    result = dict(trees)
    for entry in anchors:
        name, old, new = entry['file'], entry['anchor'], entry['replacement']
        require(name in result and old and result[name].count(old.encode()) == 1,
                'missing/duplicate anchor: ' + name + ': ' + entry['operation'])
        result[name] = result[name].replace(old.encode(), new.encode(), 1)
    return result


def prepare(v3, v4, output):
    require(not output.is_symlink(), 'fresh destination required')
    v3, v4, output = (p.resolve() for p in (v3, v4, output))
    supports = [ROOT / 'build' / name for name in SUPPORT]
    require(ROOT / 'build' in output.parents and '/build/' in (ROOT / '.gitignore').read_text().splitlines(),
            'destination must be under ignored build/')
    require(all(not output.is_relative_to(p) and not p.is_relative_to(output)
                for p in (v3, v4, *supports)), 'destination must be disjoint from inputs')
    require(not output.exists(), 'fresh destination required')
    output.mkdir()
    before, issues, equivalence, outputs, input_trees = {}, [], {}, {}, {}

    def read(path, expected=None):
        require(not path.is_symlink(), 'symlink input: ' + str(path))
        actual = digest(path)
        before.setdefault(str(path), actual)
        require(before[str(path)] == actual, 'input drift: ' + str(path))
        require(expected is None or actual == expected, 'integrity mismatch: ' + str(path))
        return path.read_bytes()

    def load(path, expected=None):
        return json.loads(read(path, expected))

    def sealed(root):
        seal = load(root / 'seal.json')
        require(isinstance(seal, dict) and bool(seal), 'empty seal: ' + str(root))
        return seal

    def consume_seal(root):
        seal = sealed(root)
        for name, expected in seal.items():
            read(child(root, name), expected)
        return seal

    try:
        read(Path(__file__).resolve())
        read(ROOT / 'tests/test_preview_delivery_overhead.py')
        # Only consumed v3 source/harness files are checked against its pre-execution seal.
        # Historical binaries and unrelated mutable tools are not inputs to this preparation.
        seal = sealed(v3)
        prep = load(v3 / 'preparation.json', seal['preparation.json'])
        require(all(prep['equivalence'][v][g] == [] for v in 'ABCD' for g in GROUPS),
                'v3 preparation equivalence is blocked')
        manifest = load(v4 / 'manifest.json')
        require(manifest['status'] == 'prepared' and manifest['unchanged']
                and not manifest['issues'] and manifest['before'] == manifest['after'],
                'v4 preparation is blocked')
        for root, state in zip(supports, ('passed', 'complete', 'complete')):
            support_seal = consume_seal(root)
            name = 'status.json' if root == supports[-1] else 'assessment.json'
            require(name in support_seal and load(root / name)['status'] == state,
                    'support evidence is blocked: ' + str(root))
        # Bind the v4 manifest/trees to the completed review's recorded inventory.
        reviewed = load(supports[-1] / 'integrity.json')
        require(reviewed['before'] == reviewed['after'] and reviewed['unchanged'], 'review input drift')
        for root in (v4, *supports[:2]):
            expected = reviewed['before'][str(root)]
            require(inventory(root) == expected, 'reviewed input inventory mismatch: ' + str(root))
            input_trees[str(root)] = expected
        # The review consumes the whole prepared package, including its manifest.
        for name, sha in input_trees[str(v4)].items():
            read(child(v4, name), sha)
        recipe = ROOT / 'scripts/prepare-preview-delivery-tracing.py'
        recipe_bytes = read(recipe, manifest['before'][str(recipe)])
        syntax = ast.parse(recipe_bytes)
        supplemental = next(ast.literal_eval(n.value) for n in syntax.body
                            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'HEADER' for t in n.targets))
        # Extract only the recorded pure filesystem patch recipe, not its historical driver.
        patch_node = next(n for n in syntax.body if isinstance(n, ast.FunctionDef) and n.name == 'patch')
        namespace = {'re': re}
        exec(compile(ast.Module(body=[patch_node], type_ignores=[]), str(recipe), 'exec'), namespace)
        header3 = read(v3 / 'trace.h', seal['trace.h'])
        require(b'DELIVERY ' not in header3, 'supplemental records in v3 header')
        context = b'  const char* role="setup";'
        require(header3.count(context) == 1, 'missing/duplicate header context anchor')
        expected_header = header3.replace(context, context + b'\n  unsigned long long delivery_generation=0, delivery_session=0, delivery_transaction=0, delivery_publication=0;\n  const char* delivery_endpoint="unavailable";') + supplemental.encode()
        header4 = read(v4 / 'trace.h', manifest['header_sha256'])
        require(header4 == expected_header, 'v4 header recipe mismatch')
        anchors = load(v4 / 'anchor-review.json')
        write(output / 'anchor-review.json', anchors)
        (output / 'preparation-recipe.py').write_bytes(recipe_bytes)
        with tempfile.TemporaryDirectory(prefix='delivery-overhead-') as temporary:
            for variant in 'ABCD':
                frozen = {}
                for mode, root, expected in (('v3', v3 / (variant + 'T'), prep['pairs'][variant + 'T']),
                                             ('v4', v4 / variant, None)):
                    if mode == 'v4':
                        require(inventory(root) == manifest['outputs'][variant], 'v4 output inventory mismatch: ' + variant)
                        for name, sha in manifest['outputs'][variant].items():
                            read(child(root, name), sha)
                        expected = load(root / 'source-inventory.json')
                    files = {}
                    for group in GROUPS:
                        require(inventory(root / group) == expected[group], 'incomplete source inventory: ' + str(root / group))
                        input_trees[str(root / group)] = expected[group]
                        for name, sha in expected[group].items():
                            relative = group + '/' + name
                            files[relative] = read(child(root, relative), sha)
                            if mode == 'v3':
                                require(seal.get(variant + 'T/' + relative) == sha, 'source missing from v3 seal: ' + relative)
                    frozen[mode] = files
                require(set(frozen['v3']) == set(frozen['v4']), 'unauthorized source file differences')
                recorded = load(v4 / variant / 'probe-to-source.json')
                require(recorded['anchors'] == anchors[variant], 'probe anchor mismatch')
                require(recorded['probes'] == probes(v4 / variant, True), 'probe map mismatch: ' + variant)
                reproduced = replay(frozen['v3'], anchors[variant])
                require(reproduced == frozen['v4'], 'anchor replay mismatch: ' + variant)
                recipe_tree = Path(temporary) / variant
                for group in GROUPS:
                    shutil.copytree(v3 / (variant + 'T') / group, recipe_tree / group)
                recipe_anchors = namespace['patch'](recipe_tree, v4 / 'trace.h', variant)
                require(recipe_anchors == anchors[variant], 'unauthorized source differences: recipe anchors: ' + variant)
                # Exact replay and exact recipe anchors prove setup, checks, timer, latency,
                # fixture/cache preservation and D deferral are unchanged except recorded probes.
                diffs = []
                for name, old in frozen['v3'].items():
                    new = frozen['v4'][name]
                    if old != new:
                        diffs.extend(difflib.unified_diff(old.decode().splitlines(True), new.decode().splitlines(True),
                                                        fromfile='v3/' + name, tofile='v4/' + name))
                (output / (variant + '-tracing.diff')).write_text(''.join(diffs))
                equivalence[variant] = dict(exact_replay=True, recipe_anchors=True, anchors=len(anchors[variant]),
                                            harness_setup_checks_timer_latency_preserved=True,
                                            fixture_cache_preservation=True, initial_deferral_preserved=variant == 'D')
                write(output / 'equivalence.json', equivalence)
                for mode, header, original_header in (('v3', header3, v3 / 'trace.h'), ('v4', header4, v4 / 'trace.h')):
                    base = output / mode / variant
                    base.mkdir(parents=True)
                    (base / 'trace.h').write_bytes(header)
                    old_include = ('#include "' + str(original_header) + '"').encode()
                    new_include = ('#include "' + str(base / 'trace.h') + '"').encode()
                    for name, data in frozen[mode].items():
                        path = child(base, name)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        # Relocate only the exact private header directive; preserve every other byte.
                        path.write_bytes(data.replace(old_include, new_include))
                    write(base / 'source-inventory.json', {g: inventory(base / g) for g in GROUPS})
                    write(base / 'probe-to-source.json', dict(probes=probes(base, mode == 'v4')))
                    outputs[mode + '/' + variant] = inventory(base)
        write(output / 'protocol.json', dict(schedule=schedule(), invocations=264, measured_observations=2400,
              warmups=24, timeout_seconds=120, termination_grace_seconds=5, retries=0,
              stop_on_first_failure=['execution', 'correctness', 'trace', 'isolation', 'cleanup', 'integrity'],
              validation='v3 lifecycle in both modes; no DELIVERY in v3; v4 endpoint validation in v4',
              reporting='Original harness pixel and final-metadata latency: median and nearest-rank p95; signed v4−v3 milliseconds and percentages relative to v3; all ten block comparisons. Exclude warm-ups; retain negative differences; zero baselines have unavailable percentages.',
              interpretation='Host measurements of incremental instrumentation effects within the existing startup timer. No overhead budget, significance claim, phase subtraction or performance qualification.'))
    except (OSError, ValueError, KeyError, TypeError, StopIteration, SyntaxError) as error:
        issues.append(str(error))
    for name, expected in input_trees.items():
        try:
            require(inventory(Path(name)) == expected, 'input tree drift: ' + name)
        except (OSError, ValueError) as error:
            issues.append(str(error))
    after = {name: digest(Path(name)) if Path(name).is_file() else None for name in before}
    if before != after:
        issues.append('consumed inputs changed')
    result = dict(status='blocked' if issues else 'prepared', warning=WARNING, issues=issues,
                  inputs=dict(v3=str(v3), v4=str(v4), support=[str(p) for p in supports]), outputs=outputs)
    write(output / 'input-integrity.json', dict(before=before, after=after, unchanged=before == after, trees=input_trees))
    write(output / 'manifest.json', result)
    (output / 'ASSESSMENT.md').write_text('# Delivery tracing overhead preparation\n\nStatus: **' + result['status'] + '**.\n\n**' + WARNING + '**.\n\n' +
        ('\n'.join(issues) if issues else 'Eight source/harness trees accepted by exact ordered replay and recorded recipe checks.') +
        '\n\nPreparation only. Compilation, staging and execution require a separate plan. Attribution remains incomplete; C qualification and D pilot conclusions and the historical preparation-test mismatch remain unchanged.\n')
    write(output / 'seal.json', inventory(output))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('v3', 'v4', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    try:
        result = prepare(args.v3, args.v4, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
    print(result['status'], args.output)
    return int(result['status'] != 'prepared')


if __name__ == '__main__':
    sys.exit(main())
