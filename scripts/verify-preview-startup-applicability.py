#!/usr/bin/env python3
"""Independent offline C audit verifier. Never imports the auditor or a recipe."""
import argparse
import difflib
import hashlib
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('checked_applicability_boundary', Path(__file__).with_name('startup-applicability-evidence.py'))
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h


def include(data, old, new):
    return data.replace(f'#include "{old}"'.encode(), f'#include "{new}"'.encode())


def check_sources(rows, stages, delivery, validation, patch):
    h.require([s[0] for s in stages] == ['qualification-C', 'CU', 'CT', 'v3-C', 'v4-C', 'baseline-C', 'validation-C'], 'incorrect A-to-C substitution')
    expected_keys = [(a[0], z[0], n) for a, z in zip(stages, stages[1:]) for n in sorted(a[1])]
    h.require([(r['left'], r['right'], r['file']) for r in rows] == expected_keys, 'source relationship membership')
    recorded_patch = {}
    for a, z in zip(stages, stages[1:]):
        h.require(a[1].keys() == z[1].keys(), 'source file membership')
    for row in rows:
        index = next(i for i, (name, _) in enumerate(stages) if name == row['left'])
        name = row['file']
        p, q = stages[index][1][name], stages[index+1][1][name]
        original, actual = p.read_bytes(), q.read_bytes()
        reverse, anchors = actual, []
        if index == 1:
            # Independently reproduce the entire recorded C diff, including hunk
            # positions, context, filenames, all source and harness files.
            recorded_patch[name] = ''.join(difflib.unified_diff(original.decode().splitlines(keepends=True),
                actual.decode().splitlines(keepends=True), fromfile=str(p), tofile=str(q)))
            anchors = [dict(record=str(b.T / 'C-tracing.diff'), file=str(p))]
            reverse = original
        elif index == 2:
            reverse = include(actual, b.D / 'v3/C/trace.h', b.T / 'trace.h')
        elif index == 3:
            anchors = [r for r in delivery if r['file'] == name]
            reverse = include(actual, b.D / 'v4/C/trace.h', b.ROOT / 'build/preview-delivery-tracing-20261113-03/trace.h')
            for edit in reversed(anchors):
                replacement = edit['replacement'].encode()
                h.require(reverse.count(replacement) == 1, 'unexplained delivery edit')
                reverse = reverse.replace(replacement, edit['anchor'].encode(), 1)
            reverse = include(reverse, b.T / 'trace.h', b.D / 'v3/C/trace.h')
        elif index == 4:
            reverse = include(actual, b.P / 'baseline/C/trace.h', b.D / 'v4/C/trace.h')
        elif index == 5:
            anchors = [r for r in validation if r['variant'] == 'C' and r['mode'] == 'validation' and r['file'] == name]
            for edit in reversed(anchors):
                replacement = edit['replacement'].encode()
                h.require(reverse.count(replacement) == 1, 'unexplained validation edit')
                reverse = reverse.replace(replacement, edit['anchor'].encode(), 1)
            reverse = include(reverse, b.P / 'validation/C/trace.h', b.P / 'baseline/C/trace.h')
        if index:
            h.require(reverse == original, 'unexplained C source edits')
        residual = b.diff(original, actual) if index == 0 else []
        status = 'different' if residual else ('exact identity' if original == actual else 'compatible under recorded transformations')
        expected_hash = hashlib.sha256(original if index == 0 else actual).hexdigest()
        h.require(row['paths'] == [str(p), str(q)] and row['hashes'] == [h.digest(p), h.digest(q)] and
                  row['anchors'] == anchors and row['residual'] == residual and row['exact_diff'] == b.diff(original, actual) and
                  row['expected_sha256'] == expected_hash and row['status'] == status, 'source derivation mismatch')
        h.require(row['evidence'] and row['limitation'], 'source limitations absent')
    ordered = sorted(recorded_patch, key=lambda n: (not n.startswith('source/'), n))
    h.require(''.join(recorded_patch[n] for n in ordered) == patch, 'recorded C patch mismatch')
    h.require(all(r['status'] in b.STATUSES[:2] for r in rows if r['file'].startswith('source/')), 'C mechanism source incompatible')


def check_payloads(rows, payloads):
    keys = [(arm, path) for arm in payloads if arm != 'qualification-C'
            for path in sorted(payloads['qualification-C'].keys() | payloads[arm].keys())]
    h.require([(r['arm'], r['path']) for r in rows] == keys, 'duplicate/missing manifest comparison')
    for row in rows:
        a = payloads['qualification-C'].get(row['path'])
        c = payloads[row['arm']].get(row['path'])
        status = 'unavailable' if None in (a, c) else ('exact identity' if a == c else 'different')
        h.require(row['qualification'] == a and row['diagnostic'] == c and row['status'] == status and
                  row['evidence'] and row['limitation'], 'manifest identity mismatch')


def check_dependencies(rows, raw, records):
    names = ['usr/lib/libQt6Core.so.6', 'usr/lib/libQt6Gui.so.6', 'usr/lib/libdbus-1.so.3', 'usr/libexec/holonight-images-helper']
    h.require([r['path'] for r in rows] == names, 'dependency membership')
    for row in rows:
        name = row['path']
        q, v = raw['qualification-C'][name], raw['validation-C'][name]
        outer = [[k, r['sha256']] for k, r in records['cpu_protected'].items() if k.endswith('/' + name) and r.get('sha256')]
        mirror = {k: v for k, v in records['cpu_mirror'].items() if k.endswith('/' + Path(name).name)}
        h.require(row['qualification'] == q and row['validation'] == v and row['same_size'] == (q['size'] == v['size']) and
                  row['status'] == ('exact identity' if q == v else 'different') and row['cpu_outer'] == outer and
                  row['cpu_mirror'] == mirror, 'dependency identity mismatch')
        sampled = [dict(record=record['file'], mapping=m,
                    payload_status='exact identity' if m['sha256'] == v['sha256'] else 'different')
                   for record in records['cpu_recordings'] for m in record['mappings']
                   if Path(m['recorded_path']).name == Path(name).name]
        h.require(row['recorded_build_ids_and_mappings'] == sampled, 'recorded build-ID/mapping mismatch')
        h.require(row['explained_by_frozen_provenance'] == ('partial: distinct instrumented build' if 'libexec' in name else 'unavailable'), 'unjustified dependency explanation')


def check_mappings(rows, payloads, records):
    protected = {}
    for path, item in records['cpu_protected'].items():
        parts = path.split('/')
        if len(parts) >= 4 and parts[0] == 'generations' and parts[2] == 'usr' and item.get('sha256'):
            protected[path] = item
    cpu = [r for r in rows if r['scope'] == 'cpu protected generation']
    standalone = [r for r in rows if r['scope'] == 'standalone mechanism']
    h.require(len(rows) == len(cpu) + len(standalone) and [r['path'] for r in cpu] == list(protected), 'outer/nested membership mismatch')
    for row in cpu:
        relative = '/'.join(row['path'].split('/')[2:])
        payload = payloads['validation-C'].get(relative)
        digest = protected[row['path']]['sha256']
        status = 'unavailable' if payload is None else ('exact identity' if payload['sha256'] == digest else 'different')
        h.require(row['payload_path'] == relative and row['payload'] == payload and row['recorded_size'] is None and
                  row['recorded_sha256'] == digest and row['status'] == status, 'outer/nested identity confusion')
    dependencies = records['mechanism_inputs']['dependencies']
    h.require([r['path'] for r in standalone] == ['usr/lib/' + n for n in dependencies], 'mechanism membership')
    for row, item in zip(standalone, dependencies.values()):
        payload = payloads['validation-C'].get(row['path'])
        loaded = {k: v for k, v in records['mechanism_mappings'].items() if v == item['host_sha256']}
        status = 'unavailable' if payload is None else ('exact identity' if payload['sha256'] == item['payload_sha256'] == item['host_sha256'] and loaded else 'different')
        h.require(row['payload'] == payload and row['qualification'] == payloads['qualification-C'].get(row['path']) and
                  row['dependency'] == item and row['mappings'] == loaded and row['status'] == status, 'mechanism mapping mismatch')


def check_matrix(matrix, rows):
    names = ['validation mechanism C', 'runtime input payload C', 'qualification protected generation', 'qualification loaded dependencies', 'execution conditions']
    h.require([r['relationship'] for r in matrix] == names, 'matrix membership')
    differences = sum(r['status'] == 'different' for r in rows if r['arm'] == 'validation-C')
    statuses = ['compatible under recorded transformations', 'different' if differences else 'exact identity', 'unavailable', 'unavailable', 'different']
    h.require([r['status'] for r in matrix] == statuses and all(r['evidence'] and r['limitation'] for r in matrix), 'unsupported applicability')
    h.require(matrix[1]['evidence'] == f'payloads.json: {differences} different validation-C files', 'payload count mismatch')


def check_decision(value, matrix, facts):
    h.require(set(value) == {'decision', 'eligible', 'qualification', 'proposals', 'next_action', 'rule', 'transfers', 'reused', 'applicability'}, 'unsupported decision claim')
    practical = facts['value']
    h.require(practical['direction'] == 'mixed; inconclusive' and
              [practical[k] for k in ('positive_blocks', 'negative_blocks', 'zero_blocks', 'below_threshold')] == [7, 1, 0, 8], 'streaming contradiction lost')
    lives = facts['work']
    h.require(len(lives) == 52 and all(r['validations'] == 1 and r['within_lifetime_repeated_bytes'] == 0 and
              r['generation_identity'].startswith('unproven') for r in lives), 'unsupported reuse claim')
    h.require(value['decision'] == 'Evidence insufficient' and value['eligible'] == [] and value['qualification'] == '78/80' and
              value['applicability'] == matrix and value['transfers'] == dict(durations=False, scheduler_states=False,
              sample_percentages=False, qualification_tail_attribution=False, p95_subtraction=False), 'unjustified transfer/candidate')
    proposals = value['proposals']
    h.require([r['name'] for r in proposals] == ['Buffered 64 KiB streaming', 'Avoiding repeated validation', 'SHA-256 execution/dispatch'], 'proposal membership')
    for row in proposals:
        h.require(set(row) == {'name', 'mechanism', 'applicability', 'integrity', 'contradictory_evidence', 'disposition', 'eligible'} and
                  row['disposition'] == 'deferred' and row['eligible'] is False and
                  row['applicability'] == 'partial: source compatible; payload ' + matrix[1]['status'] + '; loading/generation unavailable' and
                  all(row[k] for k in ('mechanism', 'integrity', 'contradictory_evidence')), 'unsupported proposal')
    # Classifications are checked above against raw retained facts. Narrative
    # fields must also stay within that evidence; resealing must not permit a
    # fabricated saving, integrity guarantee or reuse policy in free text.
    narratives = [
        ('Relevant QFile read/SHA-256 boundary; whole-startup benefit unproven',
         'Must preserve byte coverage, EOF/errors, digest and rejection; proposed startup implementation unverified',
         '7 positive and 1 negative standalone blocks, all below 5 ms; not an upper bound'),
        ('No demonstrated repeated verification in one unchanged owner/generation',
         'No integrity contract authorizes skipping/reusing validation',
         '52 distinct service constructions each validate once'),
        ('CPU/mechanism investigations completed; no avoidable dispatch defect demonstrated',
         'No applicable integrity-preserving alternative established',
         'Sampled hashing/dispatch is not proof of a defect or elapsed tail attribution')]
    h.require(all(tuple(row[k] for k in ('mechanism', 'integrity', 'contradictory_evidence')) == expected
                  for row, expected in zip(proposals, narratives)), 'unsupported proposal narrative')
    h.require(value['next_action'] == 'Retain the qualification loading/generation identity gap and the three proposal-specific mechanism gaps. Evidence cannot prioritize one smallest unresolved observation; no experiment prepared.' and
              value['rule'] == 'Eligibility requires mechanism, applicability, integrity preservation and resolved contradictions; rank eligible candidates by direct failed-gate evidence. Matching identities alone never select streaming.' and
              value['reused'] == 'Read/hash priority and sampled hashing execution are qualitative supporting context only; completed investigations are not repeated.', 'unsupported decision narrative')
    h.require('all below 5 ms' in proposals[0]['contradictory_evidence'] and
              'each validate once' in proposals[1]['contradictory_evidence'] and
              'completed' in proposals[2]['mechanism'] and 'cannot prioritize' in value['next_action'] and
              'no experiment prepared' in value['next_action'] and 'Matching identities alone never select streaming' in value['rule'], 'next action changed')


def check_gates(rows):
    summary = h.read(b.Q / 'reuse-measurement-d0nbnsxc/summary.json')
    failures = [g for g in summary['gates'] if not g['passed']]
    h.require(len(summary['gates']) == 80 and len(failures) == len(rows) == 2, 'gate membership')
    for row, gate in zip(rows, failures):
        h.require(all(row[k] == v for k, v in gate.items()) and gate['case'] == '3200x2400.png/startup' and
                  gate['event'] in ('first_ms', 'final_ms'), 'failed gate changed')
        cell = summary['summary'][gate['case']]
        a, c = [cell[arm][gate['event']]['p95'] for arm in ('A', 'C')]
        allowance = max(5, a / 10)
        h.require(row['reference_p95_ms'] == a and row['candidate_p95_ms'] == c and
                  abs(row['allowance_ms'] - allowance) < 1e-10 and abs(row['allowed_p95_ms'] - (a + allowance)) < 1e-10 and
                  abs(row['excess_ms'] - (c - a - allowance)) < 1e-10, 'qualification arithmetic/subtraction')


def check_populations(rows, retained):
    h.require(rows == retained, 'population mixing')


def verify(output):
    h.sealed(output)
    integrity = h.read(output / 'integrity.json')
    h.require(integrity['passed'] and h.recheck(integrity['inventories'], integrity['files']), 'input/tool drift')
    for name, digest in integrity['files'].items():
        if Path(name).parent in (b.ROOT / 'scripts', b.ROOT / 'tests'):
            h.require(h.digest(output / 'tools' / Path(name).name) == digest, 'snapshot mismatch')
    required_tools = [Path(__file__).resolve(), Path(__file__).with_name('audit-preview-startup-applicability.py'),
                      b.ROOT / 'tests/test_preview_startup_applicability.py', b.PINS, *h.tool_paths(b)]
    h.require(all(integrity['files'].get(str(p)) == h.digest(p) for p in required_tools), 'required tool membership')
    result = h.read(output / 'assessment.json')
    h.require(result['status'] in ('complete', 'blocked') and result['decision'] == 'Evidence insufficient', 'invalid audit result')
    if result['status'] == 'complete':
        h.require({p.name for p in output.iterdir()} == {'tools', 'inputs.json', 'integrity.json', 'assessment.json', 'REPORT.md',
                  'seal.json', 'sources.json', 'payloads.json', 'dependencies.json', 'provenance.json', 'mappings.json',
                  'matrix.json', 'decision.json', 'qualification.json', 'populations.json'}, 'audit artifact membership')
        inventories, files = b.bind()
        h.require(integrity['inventories'] == inventories and all(integrity['files'].get(k) == v for k, v in files.items()), 'consumed membership')
        h.require(h.read(output / 'inputs.json') == {k: integrity[k] for k in ('inventories', 'files')}, 'inputs mismatch')
        check_sources(h.read(output / 'sources.json'), b.raw_sources(), h.read(b.D / 'anchor-review.json')['C'],
                      h.read(b.P / 'anchors.json'), (b.T / 'C-tracing.diff').read_text())
        raw = b.raw_payloads()
        rows = h.read(output / 'payloads.json')
        check_payloads(rows, raw)
        records = b.execution_records()
        h.require(h.read(output / 'provenance.json') == records, 'execution provenance mismatch')
        check_dependencies(h.read(output / 'dependencies.json'), raw, records)
        check_mappings(h.read(output / 'mappings.json'), raw, records)
        matrix = h.read(output / 'matrix.json')
        check_matrix(matrix, rows)
        check_decision(h.read(output / 'decision.json'), matrix, b.b.retained())
        check_gates(h.read(output / 'qualification.json'))
        check_populations(h.read(output / 'populations.json'), h.read(b.R / 'matrix.json'))
        h.require(h.recheck(inventories, integrity['files']), 'verification drift')
    else:
        h.require(result.get('failure'), 'unexplained blocked result')
    return dict(status='passed', outcome=result['status'], decision=result['decision'],
                evidence_seal=h.digest(output / 'seal.json'), imports_auditor=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    h.require(not args.output.exists() and not args.output.absolute().is_relative_to(args.evidence.absolute()), 'verification destination collision/overlap')
    try:
        result = verify(args.evidence.absolute())
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result = dict(status='blocked', failure=str(error))
    with args.output.open('x') as stream:
        stream.write(h.json.dumps(result, indent=2) + '\n')
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed' or result.get('outcome') != 'complete')
