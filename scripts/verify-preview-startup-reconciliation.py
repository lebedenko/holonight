#!/usr/bin/env python3
"""Independent offline reconciliation checker; never imports the assessor."""
import argparse
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('checked_startup_boundary', Path(__file__).with_name('startup-reconciliation-evidence.py'))
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h


def check_gates(rows, summary):
    rejected = [g for g in summary['gates'] if g['passed'] is False]
    h.require(len(rows) == len(rejected) == 2 and len(summary['gates']) == 80, 'gate count mismatch')
    for saved, gate in zip(rows, rejected):
        h.require(all(saved[k] == v for k, v in gate.items()), 'failed gate changed')
        h.require(gate['case'] == '3200x2400.png/startup' and gate['event'] in {'first_ms', 'final_ms'}, 'wrong qualification gate')
        values = summary['summary'][gate['case']]
        a, c = [values[v][gate['event']]['p95'] for v in ('A', 'C')]
        permitted = a * 1.1 if a * .1 >= 5 else a + 5
        h.require(saved['reference_p95_ms'] == a and saved['candidate_p95_ms'] == c and
                  abs(saved['allowed_p95_ms']-permitted) < 1e-10 and
                  abs(saved['allowance_ms'] - max(5, a/10)) < 1e-10 and
                  abs(saved['excess_ms']-(c-permitted)) < 1e-10 and c > permitted, 'qualification arithmetic mismatch')


def check_decision(decision, value, lifetimes):
    h.require(value['direction'] == 'mixed; inconclusive' and value['below_threshold'] == 8 and
              (value['positive_blocks'], value['negative_blocks'], value['zero_blocks']) == (7, 1, 0), 'conflicting value evidence')
    h.require(len(lifetimes) == 52 and sum(r['validations'] for r in lifetimes) == 52 and
              all(r['validations'] == 1 and r['within_lifetime_repeated_bytes'] == 0 and
                  r['generation_identity'].startswith('unproven') for r in lifetimes), 'unsupported reuse claim')
    h.require(decision['decision'] == 'Evidence insufficient' and decision['eligible'] == [] and
              len(decision['proposals']) == 3 and {r['name'] for r in decision['proposals']} ==
              {'Buffered 64 KiB streaming', 'Avoiding repeated validation', 'SHA-256 execution/dispatch'} and
              all(r['disposition'] == 'deferred' and r['reason'] for r in decision['proposals']) and
              len(decision['gaps']) == 3 and 'cannot prioritize' in decision['next_action'], 'unjustified candidate classification')


def check_populations(matrix, facts):
    rows = {r['investigation']: r for r in matrix}
    h.require(len(rows) == len(matrix) == 7, 'duplicate investigation')
    for name, markers in {
        'remainder': ('150 measured', '6 warm-ups', 'baseline, instrumented and captured'),
        'validation': ('600 measured', '6 warm-ups', '22 C setup', 'baseline, validation and captured'),
        'cpu': ('40 measured', '20 profiled and 20 unprofiled', '2 warm-ups'),
        'mechanism': ('192 measured', '8 warm-ups', '8 counting'),
        'value': ('standalone', 'historical endpoints separate'),
        'helper': ('setup and standby separate',),
        'work': ('not 52 measured previews',),
    }.items():
        h.require(all(m in rows[name]['population'] for m in markers), 'population separation mismatch')
    h.require(rows['work']['separate_populations'] == facts['context']['distributions'], 'setup/warm-up/profile populations changed')
    h.require(all(r['separate_populations'] is None for k, r in rows.items() if k != 'work'), 'foreign population join')


def verify(output):
    h.sealed(output)
    integrity = h.read(output / 'integrity.json')
    h.require(integrity['passed'] and h.recheck(integrity['inventories'], integrity['files']), 'input/tool drift')
    for name, digest in integrity['files'].items():
        path = Path(name)
        if path.parent in (h.ROOT / 'scripts', h.ROOT / 'tests'):
            h.require(h.digest(output / 'tools' / path.name) == digest, 'tool snapshot mismatch')
    result = h.read(output / 'assessment.json')
    h.require(result['status'] in ('complete', 'blocked'), 'invalid outcome')
    if result['status'] == 'blocked':
        h.require(result.get('failure') and result['decision'] == 'Evidence insufficient', 'invalid blocked result')
    else:
        inventories, files = b.bind()
        h.require(inventories == integrity['inventories'] and all(integrity['files'].get(k) == v for k, v in files.items()), 'membership mismatch')
        h.require(h.read(output / 'inputs.json') == {k: integrity[k] for k in ('inventories', 'files')}, 'input inventory mismatch')
        facts = b.retained()
        matrix = h.read(output / 'matrix.json')
        h.require(len(matrix) == 7 and {r['investigation'] for r in matrix} == set(facts)-{'context'}, 'matrix membership mismatch')
        for row in matrix:
            h.require(row['result'] == facts[row['investigation']] and all(row[k] for k in
                      ('question', 'population', 'limitations', 'remaining_uncertainty')) and row['identities'] == 'inputs.json', 'matrix result/population mismatch')
        check_populations(matrix, facts)
        h.require(h.read(output / 'sources.json') == b.source_relationships(), 'source relationship mismatch')
        sources = h.read(output / 'sources.json')
        h.require(all(r['normalized_equal'] for r in sources[:2]) and all(r['anchors'] for r in sources[:2]), 'validation boundary incompatible')
        check_gates(h.read(output / 'qualification.json'), h.read(h.ROOT / 'build/preview-corrected-qjln5jn4/reuse-measurement-d0nbnsxc/summary.json'))
        check_decision(h.read(output / 'decision.json'), facts['value'], facts['work'])
        h.require(result == dict(status='complete', decision='Evidence insufficient'), 'assessment mismatch')
        h.require(h.recheck(inventories, integrity['files']), 'verification drift')
    return dict(status='passed', outcome=result['status'], decision=result['decision'], evidence_seal=h.digest(output / 'seal.json'), imports_assessor=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    h.require(not args.output.exists(), 'verification destination collision')
    try:
        result = verify(args.evidence.absolute())
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result = dict(status='blocked', failure=str(error))
    with args.output.open('x') as stream:
        stream.write(h.json.dumps(result, indent=2) + '\n')
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
