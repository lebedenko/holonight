#!/usr/bin/env python3
"""Read-only pinned evidence boundary; no execution recipes or process APIs."""
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('review_identity', Path(__file__).with_name('preview-identity-evidence.py'))
e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e)
h = e.h
ROOT = h.ROOT
PINS = Path(__file__).with_name('preview-identity-review-pins.json')
EXECUTION = ROOT / 'build/preview-identity-execution-20261117-03'
PREPARATION = ROOT / 'build/preview-identity-baseline-20261117-04'
REHEARSAL = ROOT / 'build/preview-identity-rehearsal-20261117-05'
AUDIT = e.AUDIT
RECONCILIATION = e.b.R


def merge(target, source):
    for key, value in source.items():
        h.require(key not in target or target[key] == value, 'conflicting binding: ' + key)
        target[key] = value


def protected():
    roots = {EXECUTION, PREPARATION, REHEARSAL, AUDIT, RECONCILIATION}
    for path in (PREPARATION / 'inputs.json', AUDIT / 'integrity.json'):
        value = h.read(path)
        roots.update(Path(p) for p in value['inventories'])
        roots.update(Path(p) for p in value['files'])
    return sorted(roots)


def accepted(root, outcome, key):
    inventory = h.sealed(root)
    checked = h.read(root.with_name(root.name + '-independent.json'))
    h.require(checked['status'] == 'passed' and checked['outcome'] == outcome and
              checked[key] == h.digest(root / 'seal.json') and not checked.get('synthetic', False),
              'accepted verification-to-seal binding')
    h.require(h.read(root / 'assessment.json')['status'] == outcome, 'assessment outcome binding')
    return inventory


def bind():
    inventories, files = {}, {str(PINS): h.digest(PINS)}
    pins = h.read(PINS)
    for name, expected in pins.items():
        path = ROOT / name
        h.require(h.digest(path) == expected, 'pinned evidence drift: ' + name)
        merge(files, {str(path): expected})
    for root, outcome, key in [(EXECUTION, 'complete', 'evidence_seal'),
            (PREPARATION, 'prepared', 'preparation_seal'), (REHEARSAL, 'rehearsed', 'evidence_seal'),
            (AUDIT, 'complete', 'evidence_seal'), (RECONCILIATION, 'complete', 'evidence_seal')]:
        inventories[str(root)] = accepted(root, outcome, key)
    for path in (PREPARATION / 'inputs.json', AUDIT / 'integrity.json'):
        value = h.read(path)
        if path.name == 'integrity.json':
            h.require(value['passed'], 'historical integrity failed')
        merge(inventories, value['inventories'])
        merge(files, value['files'])
    h.require(h.recheck(inventories, files), 'retained provenance drift')
    h.require(h.read(EXECUTION / 'preparation.json') == dict(path=str(PREPARATION),
              seal=h.digest(PREPARATION / 'seal.json')), 'execution preparation binding')
    h.require(h.read(EXECUTION / 'capability-verification.json') ==
              h.read(REHEARSAL.with_name(REHEARSAL.name + '-independent.json')), 'rehearsal binding')
    return dict(inventories=inventories, files=files)


def snapshots():
    paths = [ROOT / 'scripts' / n for n in ('assess-preview-identity-review.py',
        'verify-preview-identity-review.py', 'preview-identity-review-evidence.py')]
    paths += [PINS, ROOT / 'tests/test_preview_identity_review.py']
    paths += sorted(h.tool_paths(e))
    return {str(p): h.digest(p) for p in paths}


def identity_status(left, right):
    if not left or not right or not left.get('sha256') or not right.get('sha256'):
        return 'unavailable'
    return 'exact content' if left['sha256'] == right['sha256'] else 'different bytes'


def correspond(path, candidates):
    """Exact paths first; aliases are candidates, never silently selected."""
    exact = [r for r in candidates if r['path'].lstrip('/') == path.lstrip('/')]
    if exact:
        return exact, 'exact path' if len(exact) == 1 else 'ambiguous'
    name = Path(path).name
    family = name.split('.so')[0] if '.so' in name else name
    found = [r for r in candidates if (Path(r['path']).name.split('.so')[0]
             if '.so' in Path(r['path']).name else Path(r['path']).name) == family]
    return found, 'alias candidate' if len(found) == 1 else ('ambiguous' if found else 'unavailable')


def historical():
    rows = []
    variants = h.read(PREPARATION / 'inputs.json')['variants']
    for variant, value in variants.items():
        for path, identity in value['payload'].items():
            rows.append(dict(origin='qualification-' + variant, kind='runtime input', path=path, **identity))
    for row in h.read(AUDIT / 'payloads.json'):
        rows.append(dict(origin=row['arm'], kind='runtime input', path=row['path'], **row['diagnostic']))
    for row in h.read(AUDIT / 'mappings.json'):
        rows.append(dict(origin=row['scope'], kind='historical record', path=row['path'],
                         sha256=row.get('recorded_sha256', row.get('dependency', {}).get('host_sha256')),
                         size=row.get('recorded_size'), build_id=row.get('dependency', {}).get('build_id'), record=row))
    for row in h.read(AUDIT / 'dependencies.json'):
        for record in row['recorded_build_ids_and_mappings']:
            mapping = record['mapping']
            rows.append(dict(origin='CPU loaded mapping', kind='loaded mapping',
                path=mapping['recorded_path'], sha256=mapping['sha256'],
                build_id=mapping['build_id'], record=record))
    # Retain full original records, including CPU and standalone hashing build IDs.
    return rows


def dependencies(observations, ledgers, history):
    rows = []
    for variant, ledger in sorted(ledgers.items()):
        for key, identity in sorted(ledger.items()):
            scope, path = key.split(':', 1)
            occurrences = []
            for observation in observations:
                schedule = observation['schedule']
                if schedule['variant'] != variant or not schedule['captured']:
                    continue
                mappings = [m for m in observation['identities']['mappings'] if
                            m['scope'] == scope and m['path'] == path]
                if mappings:
                    h.require(all({k: m[k] for k in identity} == identity for m in mappings), 'mapping identity conflict')
                    occurrences.append(dict(schedule=schedule, processes=[{k: m[k] for k in
                        ('pid', 'start', 'namespace', 'event_index')} for m in mappings]))
            peers, relation = correspond(path, [dict(path=k.split(':', 1)[1], **v) for k, v in
                ledgers['C' if variant == 'A-fixed' else 'A-fixed'].items() if k.startswith(scope + ':')])
            rows.append(dict(variant=variant, scope=scope, path=path, **identity, observations=occurrences,
                historical_correspondences=[dict(origin=origin, correspondence=correspond(path, group)[1],
                    candidates=[dict(record=r, content=identity_status(identity, r))
                        for r in correspond(path, group)[0]]) for origin, group in
                    [(origin, [r for r in history if r['origin'] == origin])
                        for origin in sorted({r['origin'] for r in history})]],
                counterpart=dict(correspondence=relation, candidates=[dict(record=r,
                    content=identity_status(identity, r)) for r in peers]),
                highlight=any(s in path.lower() for s in ('helper', 'qt6core', 'crypto', 'ssl', 'b2', 'sha'))))
    return rows


def report(result, populations=None, signs=None, dependencies=None, choice=None):
    text = '# Offline identity-bound startup review\n\n' + result['status'] + ': Evidence insufficient\n\n'
    if result['status'] != 'complete':
        return text + result.get('failure', 'Incomplete evidence') + '\n'
    text += ('Qualification remains **78/80**. All three proposals remain deferred; no ranking or experiment. '
        'Zero builds, workloads, recordings, staging operations or qualification reruns.\n\n'
        'Runtime input correspondence is distinct from loaded bytes. Mappings establish identities only for '
        'the captured observations listed in dependency-comparisons.json, including separate warm-ups and '
        'desktop/sandbox process attribution. Historical qualification and uncaptured loading identities '
        'remain unavailable. Alias candidates and ambiguous path correspondences are explicit. '
        'Equal sizes or build IDs do not establish byte identity.\n\n'
        '| Population | Event | Count | Median ms | Nearest-rank p95 ms |\n|---|---|---:|---:|---:|\n')
    for population, cells in sorted(populations.items()):
        for event, cell in sorted(cells.items()):
            text += f"| {population} | {event} | {cell['count']} | {cell['median']} | {cell['p95']} |\n"
    text += '\nSigned differences are C minus A-fixed; positive means C is slower. Descriptive only; no new acceptance threshold.\n\n'
    for row in signs:
        text += f"- {'Captured' if row['captured'] else 'Uncaptured'} {row['event']} {row['statistic']}: {row['positive']} positive, {row['negative']} negative, {row['zero']} zero blocks.\n"
    text += '\nHighlighted helper, QtCore and hashing dependencies (full identities and historical candidates in dependency-comparisons.json):\n\n'
    for row in dependencies:
        if row['highlight']:
            summaries = []
            for correspondence in row['historical_correspondences']:
                states = sorted({c['content'] for c in correspondence['candidates']})
                summaries.append(correspondence['origin'] + ': ' + correspondence['correspondence'] + ', ' + '/'.join(states or ['unavailable']))
            text += f"- {row['variant']} {row['scope']} `{row['path']}`: " + '; '.join(summaries) + '.\n'
    text += '\nDeferred proposals and retained gaps:\n\n'
    for p in choice['proposals']:
        text += '- ' + p['name'] + ': ' + p['mechanism'] + '; ' + p['integrity'] + '; ' + p['contradictory_evidence'] + '.\n'
    return text + ('\nNo timing transfer, capture-overhead subtraction or causal dispatch inference. '
        'See historical.json for retained source/payload/mapping provenance and proposal-decisions.json for the evidence matrix.\n')
