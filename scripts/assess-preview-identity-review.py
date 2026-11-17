#!/usr/bin/env python3
"""Assess the retained identity baseline offline without launching processes."""
import argparse
import importlib.util
import math
from pathlib import Path
import shutil
import statistics
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('review_evidence', Path(__file__).with_name('preview-identity-review-evidence.py'))
e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e)
h = e.h


def timing(observations):
    populations, blocks, signs = {}, [], []
    for captured in (False, True):
        for variant in ('A-fixed', 'C'):
            selected = [o for o in observations if not o['schedule']['warmup'] and
                (o['schedule']['variant'], o['schedule']['captured']) == (variant, captured)]
            h.require(len(selected) == 25, 'population must have 25 measured samples')
            cells = {}
            for event in ('first_ms', 'final_ms'):
                values = sorted(o['sample'][event] for o in selected)
                h.require(all(type(x) in (int, float) and math.isfinite(x) and x >= 0 for x in values), 'invalid timing')
                cells[event] = dict(count=25, median=statistics.median(values), p95=values[23])
            populations[variant + ('/captured' if captured else '/uncaptured')] = cells
        for block in range(5):
            for event in ('first_ms', 'final_ms'):
                groups = [[o['sample'][event] for o in observations if not o['schedule']['warmup'] and
                    (o['schedule']['variant'], o['schedule']['captured'], o['schedule']['block']) ==
                    (variant, captured, block)] for variant in ('A-fixed', 'C')]
                h.require(all(len(g) == 5 for g in groups), 'block membership')
                a, c = groups
                blocks.append(dict(captured=captured, block=block, event=event,
                    C_minus_A_fixed_median=statistics.median(c) - statistics.median(a),
                    C_minus_A_fixed_p95=max(c) - max(a)))
        for event in ('first_ms', 'final_ms'):
            for statistic in ('median', 'p95'):
                differences = [r['C_minus_A_fixed_' + statistic] for r in blocks
                               if r['captured'] == captured and r['event'] == event]
                signs.append(dict(captured=captured, event=event, statistic=statistic,
                    positive=sum(x > 0 for x in differences), negative=sum(x < 0 for x in differences),
                    zero=sum(x == 0 for x in differences)))
    return populations, blocks, signs


def decision(historical):
    h.require(historical['decision'] == 'Evidence insufficient' and not historical['eligible'] and
              len(historical['proposals']) == 3, 'unsupported historical eligibility')
    return dict(decision='Evidence insufficient', eligible=[], qualification='78/80 unchanged',
        ranking=None, experiment=None, overhead_correction=False, historical_timing_transfer=False,
        rule='Require demonstrated mechanism, applicability, integrity preservation and resolved contradictions; identity correspondence and timing direction alone establish no eligibility.',
        proposals=[dict(p, disposition='deferred', eligible=False,
            review='New captured identities refine dependency correspondence only. Historical qualification and uncaptured loading identities remain unavailable; retained mechanism and integrity gaps remain unresolved.')
            for p in historical['proposals']])



def run(output):
    h.fresh(output, e.protected())
    inputs, tools = {}, {}
    result = dict(status='blocked', decision='Evidence insufficient')
    try:
        tools = e.snapshots()
        (output / 'tools').mkdir()
        for path in tools:
            shutil.copy2(path, output / 'tools' / Path(path).name)
        h.write(output / 'tools.json', tools)
        inputs = e.bind()
        h.write(output / 'inputs.json', inputs)
        observations = h.read(e.EXECUTION / 'observations.json')
        populations, blocks, signs = timing(observations)
        history = e.historical()
        dependencies = e.dependencies(observations, h.read(e.EXECUTION / 'ledgers.json'), history)
        choice = decision(h.read(e.AUDIT / 'decision.json'))
        historical = dict(identities=history, applicability=h.read(e.AUDIT / 'matrix.json'),
            reconciliation=h.read(e.RECONCILIATION / 'matrix.json'),
            qualification_loading='unavailable', uncaptured_loading='unavailable')
        for name, value in [('population-statistics', populations), ('block-comparisons', blocks),
                ('block-signs', signs), ('dependency-comparisons', dependencies),
                ('proposal-decisions', choice), ('historical', historical)]:
            h.write(output / (name + '.json'), value)
        result['status'] = 'complete'
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result['failure'] = str(error)
    try:
        passed = bool(inputs) and h.recheck(inputs['inventories'], dict(inputs['files'], **tools))
    except (OSError, ValueError):
        passed = False
    if not passed:
        result.update(status='blocked', failure=result.get('failure', 'input/tool drift'))
    h.write(output / 'integrity.json', dict(passed=passed, **inputs))
    h.write(output / 'assessment.json', result)
    (output / 'REPORT.md').write_text(e.report(result, locals().get('populations'), locals().get('signs'),
        locals().get('dependencies'), locals().get('choice')))
    h.write(output / 'seal.json', h.inventory(output))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'complete')
