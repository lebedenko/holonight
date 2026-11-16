#!/usr/bin/env python3
"""Reconcile retained startup investigations offline; never execute a workload."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('startup_reconciliation_boundary', Path(__file__).with_name('startup-reconciliation-evidence.py'))
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h

QUESTIONS = {
    'remainder': ('Which active validation boundary leads?', '150 measured / 300 endpoints; 6 warm-ups / 12 endpoints separate; baseline, instrumented and captured arms', 'Temporal coverage is not causal attribution.'),
    'helper': ('Which helper operation leads consistently?', 'Same helper execution as remainder; setup and standby separate', 'Competing waits and dominant uncovered time; scheduler states explain no cause.'),
    'validation': ('Which validation operation leads?', '600 measured / 1200 endpoints; 6 warm-ups and 22 C setup groups separate; baseline, validation and captured arms', 'Separate execution; no timing or scheduler transfer to remainder.'),
    'cpu': ('What userspace execution is sampled?', '40 measured; 20 profiled and 20 unprofiled; 2 warm-ups and setup separate', 'Sample percentages are not elapsed cost; kernel cost unresolved; sparse/zero samples unavailable.'),
    'work': ('Is verification redundant within an unchanged lifetime?', '52 service constructions including measured, warm-up and setup, not 52 measured previews', 'Distinct services do not prove unchanged owner/generation identity.'),
    'mechanism': ('How do buffering and chunk size affect hashing?', '192 measured sweeps; 8 warm-ups and 8 counting sweeps separate', 'Qt subclass counts are not syscalls or hardware dispatch evidence.'),
    'value': ('Does buffered 64 KiB justify a candidate?', '8 standalone three-sweep block contrasts; historical endpoints separate', 'Mixed directions; all below 5 ms; no upper bound or endpoint subtraction.'),
}


def gates(summary):
    failed = [g for g in summary['gates'] if not g['passed']]
    h.require(len(summary['gates']) == 80 and len(failed) == 2, 'qualification membership mismatch')
    rows = []
    for g in failed:
        h.require(g['case'] == '3200x2400.png/startup' and g['event'] in ('first_ms', 'final_ms'), 'unexpected failed gate')
        cell = summary['summary'][g['case']]
        ref, current = cell['A'][g['event']]['p95'], cell['C'][g['event']]['p95']
        allowance = max(5, ref * .1)
        rows.append(dict(g, reference_p95_ms=ref, candidate_p95_ms=current, allowance_ms=allowance,
                         allowed_p95_ms=ref+allowance, excess_ms=current-ref-allowance))
    return rows


def choose(value, lifetimes):
    h.require(value['positive_blocks'] + value['negative_blocks'] + value['zero_blocks'] == 8, 'value population mismatch')
    h.require(value['below_threshold'] == 8 and value['positive_blocks'] == 7 and value['negative_blocks'] == 1,
              'conflicting practical-value evidence')
    h.require(len(lifetimes) == 52 and all(r['validations'] == 1 and r['within_lifetime_repeated_bytes'] == 0 and
              r['generation_identity'].startswith('unproven') for r in lifetimes), 'unjustified caching claim')
    return dict(decision='Evidence insufficient', eligible=[], proposals=[
        dict(name='Buffered 64 KiB streaming', disposition='deferred', reason='7 positive and 1 negative blocks; all 8 below 5 ms; applicable whole-preview gain unproven.'),
        dict(name='Avoiding repeated validation', disposition='deferred', reason='52 distinct service constructions each validate once; unchanged owner/generation redundancy unproven.'),
        dict(name='SHA-256 execution/dispatch', disposition='deferred', reason='CPU and mechanism investigations completed; no demonstrated dispatch defect or applicable integrity-preserving replacement.')],
        next_action='No experiment prepared. Retained evidence cannot prioritize one smallest gap across the three proposals.',
        gaps=['Streaming: identity-bound effect of the proposed loop in the applicable startup validation boundary.',
              'Reuse: repeated verification within one proven unchanged owner/generation and its integrity contract.',
              'Dispatch: a specific avoidable execution/dispatch mechanism on the applicable frozen dependency path.'],
        rule='Require mechanism, applicability, integrity preservation and no unresolved contradiction; rank eligible candidates by direct evidence to failed startup gates; ties or missing evidence yield Evidence insufficient.')


def run(output):
    h.fresh(output, [h.ROOT / 'build' / n for n in b.h.NAMES] + [(h.ROOT / n).parent for n in h.read(b.PINS) if n.endswith('/seal.json')])
    inventories, files = {}, {}
    result = dict(status='blocked', decision='Evidence insufficient')
    try:
        (output / 'tools').mkdir()
        for path in [Path(__file__).resolve(), Path(__file__).with_name('verify-preview-startup-reconciliation.py'),
                     h.ROOT / 'tests/test_preview_startup_reconciliation.py', b.PINS, *h.tool_paths(b)]:
            files[str(path)] = h.digest(path)
            shutil.copy2(path, output / 'tools' / path.name)
        inventories, consumed = b.bind()
        files.update(consumed)
        for name in consumed:
            path = Path(name)
            if path.parent in (h.ROOT / 'scripts', h.ROOT / 'tests'):
                shutil.copy2(path, output / 'tools' / path.name)
        facts = b.retained()
        matrix = [dict(investigation=k, question=q, population=p, limitations=l, result=facts[k],
                       identities='inputs.json', remaining_uncertainty=l, separate_populations=facts['context']['distributions'] if k == 'work' else None) for k, (q, p, l) in QUESTIONS.items()]
        summary = h.read(h.ROOT / 'build/preview-corrected-qjln5jn4/reuse-measurement-d0nbnsxc/summary.json')
        decision = choose(facts['value'], facts['work'])
        for name, value in [('matrix', matrix), ('sources', b.source_relationships()), ('qualification', gates(summary)), ('decision', decision)]:
            h.write(output / (name + '.json'), value)
        h.write(output / 'inputs.json', dict(inventories=inventories, files=files))
        result.update(status='complete')
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result['failure'] = str(error)
    finally:
        try:
            passed = h.recheck(inventories, files)
        except (OSError, ValueError):
            passed = False
        if not passed:
            result.update(status='blocked', failure='input/tool drift')
        h.write(output / 'integrity.json', dict(passed=passed, inventories=inventories, files=files))
        h.write(output / 'assessment.json', result)
        (output / 'REPORT.md').write_text('# Offline startup reconciliation\n\n' + result['status'] + ': Evidence insufficient\n\n'
            + result.get('failure', 'All three proposals remain deferred. Qualification remains failed at 78/80. See matrix.json, sources.json, qualification.json and decision.json. Separate executions are supporting context only; no timing, scheduler state or sample share is transferred. No experiment is prepared.') + '\n')
        h.write(output / 'seal.json', h.inventory(output))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'complete')
