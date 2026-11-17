#!/usr/bin/env python3
"""Independent offline review verifier; imports no assessor or execution recipe."""
import argparse
import importlib.util
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('review_verified_evidence', Path(__file__).with_name('preview-identity-review-evidence.py'))
e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e)
h = e.h
PRODUCTS = ('population-statistics', 'block-comparisons', 'block-signs', 'dependency-comparisons',
            'proposal-decisions', 'historical')


def schedule():
    combinations = [('A-fixed', False), ('A-fixed', True), ('C', False), ('C', True)]
    rows = [(None, 0, v, c) for v, c in combinations]
    for block in range(5):
        order = combinations[block % 4:] + combinations[:block % 4]
        if block % 2:
            order = order[::-1]
        rows.extend((block, sample, v, c) for v, c in order for sample in range(5))
    return [dict(invocation=i, block=b, sample=s, variant=v, captured=c, warmup=b is None, count=1)
            for i, (b, s, v, c) in enumerate(rows)]


def check_timing(observations, populations, blocks, signs):
    h.require([o['schedule'] for o in observations] == schedule(), 'observation schedule membership')
    def quantile(data, median=False):
        data = sorted(data)
        h.require(len(data) in (5, 25) and all(type(x) in (int, float) and math.isfinite(x) and x >= 0
                  for x in data), 'invalid sample population')
        return data[len(data) // 2] if median else data[(95 * len(data) + 99) // 100 - 1]
    expected_p, expected_b, expected_s = {}, [], []
    for captured in (False, True):
        for variant in ('A-fixed', 'C'):
            cells = {}
            for event in ('first_ms', 'final_ms'):
                data = [o['sample'][event] for o in observations if o['schedule']['block'] is not None and
                        o['schedule']['variant'] == variant and o['schedule']['captured'] == captured]
                h.require(len(data) == 25, 'population count')
                cells[event] = dict(count=25, median=quantile(data, True), p95=quantile(data))
            expected_p[variant + ('/captured' if captured else '/uncaptured')] = cells
        for block in range(5):
            for event in ('first_ms', 'final_ms'):
                data = {v: [o['sample'][event] for o in observations if o['schedule']['block'] == block and
                    o['schedule']['captured'] == captured and o['schedule']['variant'] == v] for v in ('A-fixed', 'C')}
                expected_b.append(dict(captured=captured, block=block, event=event,
                    C_minus_A_fixed_median=quantile(data['C'], True) - quantile(data['A-fixed'], True),
                    C_minus_A_fixed_p95=quantile(data['C']) - quantile(data['A-fixed'])))
        for event in ('first_ms', 'final_ms'):
            for statistic in ('median', 'p95'):
                counts = dict(positive=0, negative=0, zero=0)
                for row in expected_b:
                    if row['captured'] == captured and row['event'] == event:
                        difference = row['C_minus_A_fixed_' + statistic]
                        counts['positive' if difference > 0 else 'negative' if difference < 0 else 'zero'] += 1
                expected_s.append(dict(captured=captured, event=event, statistic=statistic, **counts))
    h.require((populations, blocks, signs) == (expected_p, expected_b, expected_s), 'timing arithmetic/signs')


def check_decision(value, historical):
    h.require(set(value) == {'decision', 'eligible', 'qualification', 'ranking', 'experiment', 'proposals', 'overhead_correction', 'historical_timing_transfer', 'rule'} and
        value['decision'] == 'Evidence insufficient' and value['eligible'] == [] and
        value['qualification'] == '78/80 unchanged' and value['ranking'] is None and value['experiment'] is None and
        value['overhead_correction'] is False and value['historical_timing_transfer'] is False and
        value['rule'] == 'Require demonstrated mechanism, applicability, integrity preservation and resolved contradictions; identity correspondence and timing direction alone establish no eligibility.',
        'unsupported optimization claim')
    h.require(all(p.get('review') == 'New captured identities refine dependency correspondence only. Historical qualification and uncaptured loading identities remain unavailable; retained mechanism and integrity gaps remain unresolved.' for p in value['proposals']), 'unsupported proposal review claim')
    h.require([{k: val for k, val in p.items() if k != 'review'} for p in value['proposals']] == historical['proposals'] and len(value['proposals']) == 3 and
        all(p['disposition'] == 'deferred' and p['eligible'] is False and
            all(p[k] for k in ('mechanism', 'applicability', 'integrity', 'contradictory_evidence'))
            for p in value['proposals']), 'proposal requirements/gaps')


def verify(output):
    h.sealed(output)
    result = h.read(output / 'assessment.json')
    h.require(result == dict(status='complete', decision='Evidence insufficient'), 'assessment incomplete/unsupported')
    tools = e.snapshots()
    h.require(h.read(output / 'tools.json') == tools and h.inventory(output / 'tools') ==
              {Path(p).name: v for p, v in tools.items()}, 'tool snapshot membership/drift')
    inputs = e.bind()
    h.require(h.read(output / 'inputs.json') == inputs and
              h.read(output / 'integrity.json') == dict(passed=True, **inputs), 'input/integrity claims')
    observations = h.read(e.EXECUTION / 'observations.json')
    products = {name: h.read(output / (name + '.json')) for name in PRODUCTS}
    check_timing(observations, products['population-statistics'], products['block-comparisons'], products['block-signs'])
    check_decision(products['proposal-decisions'], h.read(e.AUDIT / 'decision.json'))
    history = e.historical()
    dependencies = e.dependencies(observations, h.read(e.EXECUTION / 'ledgers.json'), history)
    h.require(products['dependency-comparisons'] == dependencies, 'dependency correspondence/membership claims')
    h.require(products['historical'] == dict(identities=history, applicability=h.read(e.AUDIT / 'matrix.json'),
        reconciliation=h.read(e.RECONCILIATION / 'matrix.json'), qualification_loading='unavailable',
        uncaptured_loading='unavailable'), 'historical scope claims')
    h.require((output / 'REPORT.md').read_text() == e.report(result, products['population-statistics'],
        products['block-signs'], dependencies, products['proposal-decisions']), 'human report claims')
    names = {n + '.json' for n in PRODUCTS} | {'assessment.json', 'inputs.json', 'integrity.json',
        'tools.json', 'REPORT.md', 'seal.json'} | {'tools/' + Path(p).name for p in tools}
    h.require(set(h.inventory(output)) == names, 'review artifact membership')
    h.require(h.recheck(inputs['inventories'], dict(inputs['files'], **tools)), 'verification input drift')
    return dict(status='passed', outcome='complete', decision='Evidence insufficient',
        evidence_seal=h.digest(output / 'seal.json'), imports_assessor=False, imports_execution_recipes=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    destination = args.output.absolute()
    h.require(destination == destination.resolve() and not destination.exists() and
        not destination.is_relative_to(args.evidence.absolute()) and
        all(not destination.is_relative_to(p) for p in e.protected()), 'result collision/overlap')
    try:
        result = verify(args.evidence.absolute())
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result = dict(status='blocked', failure=str(error))
    with destination.open('x') as stream:
        stream.write(h.json.dumps(result, indent=2) + '\n')
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
