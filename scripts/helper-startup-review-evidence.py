#!/usr/bin/env python3
"""Read-only evidence boundary for the offline helper decision and its verifier.

No process API is used. Historical host and /run inputs are provenance, not replay
requirements. Arithmetic and decision implementations live in separate programs.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
NAMES = ('preview-helper-startup-20261116-06', 'preview-helper-startup-native-20261116-04',
         'preview-helper-startup-execution-20261116-04', 'preview-helper-startup-report-20261116-07')
IDENTITY = ('pid', 'tid', 'service', 'observation', 'job', 'worker', 'preparation')


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inventory(root):
    require(root.is_dir() and root.resolve() == root, 'invalid evidence root')
    result = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), 'evidence symlink')
        if path.is_file():
            result[str(path.relative_to(root))] = digest(path)
    return result


def sealed(root):
    actual = inventory(root)
    require(actual == dict(read(root / 'seal.json'), **{'seal.json': digest(root / 'seal.json')}),
            'seal/inventory mismatch: ' + str(root))
    return actual


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def tool_paths(*modules):
    found = set()
    seen = set()
    def visit(value):
        if id(value) in seen or not isinstance(value, types.ModuleType):
            return
        seen.add(id(value))
        path = Path(getattr(value, '__file__', '')).absolute()
        if path.parent != ROOT / 'scripts':
            return
        found.add(path)
        for child in vars(value).values():
            if isinstance(child, types.ModuleType):
                visit(child)
    for value in modules:
        visit(value)
    return found


def bind_inputs():
    roots = [ROOT / 'build' / name for name in NAMES]
    before = {str(root): sealed(root) for root in roots}
    files = {}
    for i, root in enumerate(roots):
        record = root.parent / (root.name + '-independent.json')
        files[str(record)] = digest(record)
        checked = read(record)
        require(checked['status'] == 'passed' and checked['preparation_seal' if i == 0 else 'evidence_seal'] ==
                digest(root / 'seal.json'), 'verification-to-seal binding mismatch')
        if i:
            require(checked['outcome'] == ('built' if i == 1 else 'complete') and
                    read(root / 'assessment.json')['status'] == checked['outcome'], 'historical verification blocked')
            integrity = read(root / 'integrity.json')
            require(integrity['passed'] and all(integrity['checks'].values()), 'historical integrity failed')
            for consumed, expected in integrity['before'].items():
                require(consumed in before and before[consumed] == expected, 'historical consumed inventory mismatch')
            for name, expected in integrity['tools'].items():
                require(digest(root / 'tools' / Path(name).name) == expected, 'historical tool snapshot mismatch')
    prepared, built, execution, report = roots
    require(read(execution / 'preregistration.json')['built_seal'] == digest(built / 'seal.json'), 'build binding mismatch')
    evidence = read(report / 'evidence.json')
    require(all(evidence[k] == str(p) for k, p in zip(('package', 'built', 'execution'), roots[:3])) and
            evidence['execution_seal'] == digest(execution / 'seal.json'), 'report source binding mismatch')
    return roots, before, files


def recheck(before, files):
    return all(inventory(Path(name)) == value for name, value in before.items()) and all(
        digest(Path(name)) == value for name, value in files.items())


def fresh(output, inputs):
    require(output.absolute() == output.resolve() and output.is_relative_to(ROOT / 'build') and
            output != ROOT / 'build', 'destination must be beneath ignored build/')
    require(not output.exists(), 'destination collision')
    require(all(not output.is_relative_to(p) and not p.is_relative_to(output) for p in inputs),
            'destination overlaps evidence')
    output.mkdir(parents=True)


def accounts(roots):
    """Check raw citations and canonical span/lifecycle associations before analysis."""
    prepared, built, execution, report = roots
    values = read(report / 'accounting.json')
    require(len(values) == 36, 'invocation population mismatch')
    # The old checker's arithmetic/raw-binding functions are offline. Cache text/hash
    # reads locally because the report repeats citations in several retained views.
    texts, hashes = {}, {}
    def text(path):
        if path not in texts:
            texts[path] = path.read_text().splitlines()
        return texts[path]
    def citation(ref, prefix, suffix=None):
        path = Path(ref['file'])
        if suffix:
            path = path.with_suffix(suffix)
        require(path.is_relative_to(execution), 'foreign raw citation')
        raw = text(path)[ref['line'] - 1]
        require(raw.startswith(prefix), 'raw citation prefix mismatch')
        original = json.loads(raw[len(prefix):])
        expected = {k: v for k, v in ref.items() if k not in ('file', 'line', 'raw')}
        if prefix == 'HELPER_STARTUP ':
            for k in ('ns', 'service', 'observation', 'job', 'worker', 'preparation', 'request_generation', 'span', 'parent'):
                if isinstance(original[k], str):
                    original[k] = int(original[k])
        require(original == expected, 'raw citation identity mismatch')
    schedule = read(prepared / 'protocol.json')['schedule']
    endpoints = []
    for index, account in enumerate(values):
        pop = account['population']
        require(dict(pop, variant=account['variant'], observations=len(account['original_samples'])) ==
                dict(schedule[index], invocation=pop['invocation']), 'schedule/count mismatch')
        require(account['status'] == 'complete' and not account['issues'], 'accounting incomplete')
        raw_spans = {}
        stacks = {}
        for record in account['records']:
            require(record['raw']['text'] == text(Path(record['raw']['file']))[record['raw']['line'] - 1], 'raw text mismatch')
            citation(dict(record, file=record['raw']['file'], line=record['raw']['line']), 'HELPER_STARTUP ')
            require(record['invocation'] == pop['invocation'], 'invocation mismatch')
            clock = read(execution / 'preregistration.json')['clock']
            require((record['host'], record['boot'], record['clock']) ==
                    (clock['provenance']['host'], clock['provenance']['boot_id'], clock['name']), 'clock provenance mismatch')
            key = (record['pid'], record['span'])
            pair = raw_spans.setdefault(key, {})
            require(record['edge'] not in pair, 'duplicate helper boundary')
            pair[record['edge']] = record
            stack = stacks.setdefault((record['pid'], record['tid']), [])
            if record['edge'] == 'begin':
                require(record['parent'] == (stack[-1]['span'] if stack else None), 'helper nesting mismatch')
                stack.append(record)
            else:
                require(stack and stack[-1]['span'] == record['span'], 'unbalanced helper span')
                begin = stack.pop()
                require(begin['ns'] <= record['ns'] and all(begin[k] == record[k] for k in begin if k not in
                        ('ns', 'edge', 'outcome', 'raw')), 'helper boundary identity mismatch')
        require(not any(stacks.values()), 'unclosed helper span')
        require(len(raw_spans) == len(account['spans']), 'span inventory mismatch')
        for span in account['spans']:
            pair = raw_spans[span['pid'], span['span']]
            require(set(pair) == {'begin', 'end'} and pair['begin'] == span['begin'] and pair['end'] == span['end'] and
                    span['start'] == pair['begin']['ns'] and span['stop'] == pair['end']['ns'], 'span boundary mismatch')
            require(all(span[k] == pair['begin'][k] for k in ('pid', 'span', 'parent', 'operation')), 'span metadata mismatch')
            require(span['source_citations'], 'missing source citation')
            for c in span['source_citations']:
                path = Path(c['file'])
                require(path.is_relative_to(prepared), 'foreign source citation')
                if path not in hashes:
                    hashes[path] = digest(path)
                require(hashes[path] == c['sha256'] and text(path)[c['line'] - 1] == c['text'] and
                        '"' + span['operation'] + '"' in c['text'], 'source citation mismatch')
        lifecycle = account['lifecycle']
        raw_path = execution / 'observations' / f'{index:03}.stderr'
        legacy_events = [json.loads(line[6:]) for line in text(raw_path) if line.startswith('TRACE ')]
        for row in lifecycle['accounting']:
            for boundaries in row['boundaries'].values():
                for event in boundaries:
                    citation(event, 'TRACE ', '.stderr')
            for event in row['deliveries']:
                citation(event, 'TRACE ', '.stderr')
        for w in account['windows']:
            e = w['begin']
            candidates = [s for row in lifecycle['accounting'] for s in row['timeline']]
            candidates += lifecycle['unassigned']
            candidates = [s for s in candidates if s['phase'] == 'helper_prepare' and all(
                s[edge].get(k) == (e[k] or 0) for edge in ('begin', 'end') for k in IDENTITY)]
            require(len(candidates) == 1 and candidates[0] == w['lifecycle_binding']['legacy'], 'lifecycle binding mismatch')
            legacy = candidates[0]
            for edge in ('begin', 'end'):
                citation(legacy[edge], 'TRACE ', '.stderr')
            kind = 'setup' if legacy.get('cause') == 'setup_activity' else legacy.get('role')
            require(kind == w['lifecycle_binding']['classification'] and kind in ('setup', 'demand', 'standby'), 'lifecycle classification mismatch')
            if kind == 'demand':
                phase = 'selected_worker' if e['preparation'] is not None else 'demand_dispatch'
                keys = ('pid', 'service', 'observation', 'worker', 'preparation') + (('job',) if e['preparation'] is None else ())
                selected = [r for r in legacy_events if r['phase'] == phase and
                            (phase == 'selected_worker' or r['edge'] == 'begin') and all(r.get(k) == (e[k] or 0) for k in keys)]
                require(len(selected) == 1, 'selected demand identity mismatch')
        for e in account['endpoints']:
            require(e['invocation_index'] == index and e['variant'] == account['variant'] and
                    all(e[k] == pop[k] for k in ('arm', 'block', 'warmup', 'fixture')), 'endpoint context mismatch')
            citation(e['delivery'], 'DELIVERY ')
            endpoints.append(e)
    require(endpoints == read(report / 'endpoints.json'), 'endpoint inventory mismatch')
    require(sum(len(a['original_samples']) for a in values if not a['population']['warmup']) == 150 and
            sum(len(a['original_samples']) for a in values if a['population']['warmup']) == 6 and
            len(endpoints) == 312, 'population mismatch')
    return values
