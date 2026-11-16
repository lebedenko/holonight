#!/usr/bin/env python3
"""Audit frozen qualification C applicability offline; never prepare an experiment."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location('applicability_boundary', Path(__file__).with_name('startup-applicability-evidence.py'))
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h


def replay_patch(data, patch, filename):
    """Apply only the recorded unified hunks in memory, with exact positions/context."""
    lines = patch.splitlines(keepends=True)
    chunks = []
    selected = False
    for line in lines:
        if line.startswith('--- '):
            selected = line[4:].strip() == filename
        elif selected:
            if line.startswith('+++ '):
                continue
            if line.startswith('@@ '):
                chunks.append([line, []])
            else:
                h.require(chunks and line[:1] in (' ', '+', '-'), 'invalid recorded patch')
                chunks[-1][1].append(line)
    original = data.decode().splitlines(keepends=True)
    output, cursor = [], 0
    for header, body in chunks:
        match = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[^\n]*\n?', header)
        h.require(match, 'bad hunk header')
        start = int(match[1]) - 1
        before = [line[1:] for line in body if line[0] in ' -']
        after = [line[1:] for line in body if line[0] in ' +']
        h.require(start >= cursor and original[start:start+len(before)] == before, 'recorded patch context mismatch')
        h.require(len(before) == int(match[2] or 1) and len(after) == int(match[4] or 1), 'hunk count mismatch')
        output.extend(original[cursor:start]); output.extend(after)
        cursor = start + len(before)
    output.extend(original[cursor:])
    return ''.join(output).encode()


def substitute(data, rows):
    for row in rows:
        old, new = row['anchor'].encode(), row['replacement'].encode()
        h.require(data.count(old) == 1, 'ambiguous/missing recorded anchor')
        data = data.replace(old, new, 1)
    return data


def relocate(data, old, new):
    return data.replace(('#include "' + str(old) + '"').encode(),
                        ('#include "' + str(new) + '"').encode())


def source_rows(stages, delivery, validation, patch):
    result = []
    h.require(len(stages) == 7 and [s[0] for s in stages] ==
              ['qualification-C', 'CU', 'CT', 'v3-C', 'v4-C', 'baseline-C', 'validation-C'], 'incorrect A-to-C substitution')
    for index, ((left, files), (right, targets)) in enumerate(zip(stages, stages[1:])):
        h.require(files.keys() == targets.keys(), 'source membership mismatch')
        for name in sorted(files):
            p, q = files[name], targets[name]
            old, actual = p.read_bytes(), q.read_bytes()
            expected, anchors = old, []
            if index == 1:
                expected = replay_patch(old, patch, str(p))
                anchors = [dict(record=str(b.T / 'C-tracing.diff'), file=str(p))]
            elif index == 2:
                expected = relocate(old, b.T / 'trace.h', b.D / 'v3/C/trace.h')
            elif index == 3:
                anchors = [r for r in delivery if r['file'] == name]
                expected = relocate(old, b.D / 'v3/C/trace.h', b.T / 'trace.h')
                expected = substitute(expected, anchors)
                expected = relocate(expected, b.ROOT / 'build/preview-delivery-tracing-20261113-03/trace.h', b.D / 'v4/C/trace.h')
            elif index == 4:
                expected = relocate(old, b.D / 'v4/C/trace.h', b.P / 'baseline/C/trace.h')
            elif index == 5:
                anchors = [r for r in validation if r['variant'] == 'C' and r['mode'] == 'validation' and r['file'] == name]
                expected = relocate(old, b.P / 'baseline/C/trace.h', b.P / 'validation/C/trace.h')
                expected = substitute(expected, anchors)
            residual = b.diff(expected, actual)
            # Qualification-to-CU harness changes are retained as differences;
            # never smuggle them into the instrumentation allowlist.
            if index:
                h.require(not residual, 'unexplained C source edit: ' + str(q))
            result.append(dict(left=left, right=right, file=name, paths=[str(p), str(q)],
                hashes=[h.digest(p), h.digest(q)], expected_sha256=hashlib.sha256(expected).hexdigest(),
                anchors=anchors, exact_diff=b.diff(old, actual), residual=residual,
                status='different' if residual else ('exact identity' if old == actual else 'compatible under recorded transformations'),
                evidence='C-tracing.diff and C-specific anchor-review/validation anchors; exact include relocations only',
                limitation='Source relationship only; no timing, binary, dependency or generation equivalence.'))
    return result


def payload_rows(payloads):
    rows = []
    reference = payloads['qualification-C']
    for arm, entries in payloads.items():
        if arm == 'qualification-C':
            continue
        for name in sorted(reference.keys() | entries.keys()):
            a, c = reference.get(name), entries.get(name)
            rows.append(dict(arm=arm, path=name, qualification=a, diagnostic=c,
                status='unavailable' if a is None or c is None else ('exact identity' if a == c else 'different'),
                evidence='Recorded nested runtime manifests; path, size and SHA-256, inputs rechecked',
                limitation='Input payload only; outer generation inventory and actual loaded mappings are separate.'))
    return rows


def applicability(sources, payloads):
    code = [r for r in sources if r['file'].startswith('source/')]
    h.require(all(r['status'] in b.STATUSES[:2] for r in code), 'C mechanism source incompatible')
    different = sum(r['status'] == 'different' for r in payloads if r['arm'] == 'validation-C')
    return [dict(relationship=name, status=status, evidence=evidence, limitation=limit) for name, status, evidence, limit in [
        ('validation mechanism C', 'compatible under recorded transformations', 'sources.json: all production files, declarations and callers; C literal replay', 'Boundary relevance only; no substep/timing transfer.'),
        ('runtime input payload C', 'different' if different else 'exact identity', f'payloads.json: {different} different validation-C files', 'Even matching inputs do not prove generation identity or actual loading.'),
        ('qualification protected generation', 'unavailable', 'provenance.json: frozen runner removed /run staging', 'No current reconstruction; installer implementation used then is not frozen by runner provenance.'),
        ('qualification loaded dependencies', 'unavailable', 'No retained qualification mapping record', 'Later CPU/standalone mapping identities cannot substitute for this execution.'),
        ('execution conditions', 'different', 'provenance.json commands; sources.json harness residuals; reconciliation populations', 'Measured/setup/warm-up/instrumented/captured/profiled/standalone populations stay separate.')]]


def decision(matrix, facts):
    value, lives = facts['value'], facts['work']
    h.require((value['positive_blocks'], value['negative_blocks'], value['zero_blocks'], value['below_threshold']) == (7, 1, 0, 8), 'conflicting streaming evidence')
    h.require(len(lives) == 52 and all(r['validations'] == 1 and r['within_lifetime_repeated_bytes'] == 0 and
              r['generation_identity'].startswith('unproven') for r in lives), 'unsupported reuse')
    return dict(decision='Evidence insufficient', eligible=[], qualification='78/80',
        proposals=[dict(name=name, mechanism=mechanism, applicability='partial: source compatible; payload ' + matrix[1]['status'] + '; loading/generation unavailable',
                        integrity=integrity, contradictory_evidence=contradiction, disposition='deferred', eligible=False)
            for name, mechanism, integrity, contradiction in [
                ('Buffered 64 KiB streaming', 'Relevant QFile read/SHA-256 boundary; whole-startup benefit unproven',
                 'Must preserve byte coverage, EOF/errors, digest and rejection; proposed startup implementation unverified',
                 '7 positive and 1 negative standalone blocks, all below 5 ms; not an upper bound'),
                ('Avoiding repeated validation', 'No demonstrated repeated verification in one unchanged owner/generation',
                 'No integrity contract authorizes skipping/reusing validation', '52 distinct service constructions each validate once'),
                ('SHA-256 execution/dispatch', 'CPU/mechanism investigations completed; no avoidable dispatch defect demonstrated',
                 'No applicable integrity-preserving alternative established', 'Sampled hashing/dispatch is not proof of a defect or elapsed tail attribution')]],
        next_action='Retain the qualification loading/generation identity gap and the three proposal-specific mechanism gaps. Evidence cannot prioritize one smallest unresolved observation; no experiment prepared.',
        rule='Eligibility requires mechanism, applicability, integrity preservation and resolved contradictions; rank eligible candidates by direct failed-gate evidence. Matching identities alone never select streaming.',
        transfers=dict(durations=False, scheduler_states=False, sample_percentages=False, qualification_tail_attribution=False, p95_subtraction=False),
        reused='Read/hash priority and sampled hashing execution are qualitative supporting context only; completed investigations are not repeated.',
        applicability=matrix)


def dependency_rows(payloads, records):
    result = []
    for name in ('usr/lib/libQt6Core.so.6', 'usr/lib/libQt6Gui.so.6', 'usr/lib/libdbus-1.so.3', 'usr/libexec/holonight-images-helper'):
        q, v = [payloads[k][name] for k in ('qualification-C', 'validation-C')]
        outer = [(k, r['sha256']) for k, r in records['cpu_protected'].items() if k.endswith('/' + name) and r.get('sha256')]
        mirror = {k: v for k, v in records['cpu_mirror'].items() if k.endswith('/' + Path(name).name)}
        sampled = [dict(record=record['file'], mapping=m,
                    payload_status='exact identity' if m['sha256'] == v['sha256'] else 'different')
                   for record in records['cpu_recordings'] for m in record['mappings']
                   if Path(m['recorded_path']).name == Path(name).name]
        result.append(dict(path=name, qualification=q, validation=v, same_size=q['size'] == v['size'],
            status='exact identity' if q == v else 'different', cpu_outer=outer, cpu_mirror=mirror,
            recorded_build_ids_and_mappings=sampled,
            evidence='Qualification C binary/runtime inventory; validation built seal; CPU protected-runtime and symbol-mirror records',
            explanation=('Different helper builds with recorded validation instrumentation; instrumentation explains a build distinction, not each binary byte.' if 'libexec' in name else
                         'Retained records establish different bytes, but do not establish the cause. Equal size/version is not identity; no current package substituted.'),
            explained_by_frozen_provenance='partial: distinct instrumented build' if 'libexec' in name else 'unavailable',
            limitation='CPU outer runtime manifest is a different inventory scope; qualification loaded identity remains unavailable.'))
    return result


def mapping_rows(payloads, records):
    rows = []
    # The outer protected inventory contains directories/current/manifest too;
    # only the exact generation-relative usr file belongs to the payload view.
    for path, item in records['cpu_protected'].items():
        parts = Path(path).parts
        if len(parts) < 4 or parts[0] != 'generations' or parts[2] != 'usr' or not item.get('sha256'):
            continue
        name = '/'.join(parts[2:])
        payload = payloads['validation-C'].get(name)
        rows.append(dict(scope='cpu protected generation', path=path, payload_path=name,
                         recorded_sha256=item['sha256'], recorded_size=None, payload=payload,
                         status='unavailable' if payload is None else ('exact identity' if payload['sha256'] == item['sha256'] else 'different'),
                         evidence='CPU protected-runtime.json and validation nested manifest',
                         limitation='Digest correspondence only; protected inventory has no file sizes. This is not a loaded mapping or qualification generation.'))
    for name, item in records['mechanism_inputs']['dependencies'].items():
        path = 'usr/lib/' + name
        payload = payloads['validation-C'].get(path)
        qualification = payloads['qualification-C'].get(path)
        mappings = {k: v for k, v in records['mechanism_mappings'].items() if v == item['host_sha256']}
        rows.append(dict(scope='standalone mechanism', path=path, payload=payload, qualification=qualification,
                         dependency=item, mappings=mappings,
                         status='unavailable' if payload is None else ('exact identity' if payload['sha256'] == item['payload_sha256'] == item['host_sha256'] and mappings else 'different'),
                         evidence='Mechanism inputs dependencies/build IDs and native-mapped-identities.json',
                         limitation='Recorded host mapping and payload digest/build-ID binding for this standalone population; no qualification loading inference.'))
    return rows


def gates():
    summary = h.read(b.Q / 'reuse-measurement-d0nbnsxc/summary.json')
    result = []
    h.require(len(summary['gates']) == 80 and sum(g['passed'] for g in summary['gates']) == 78, 'qualification count')
    for g in summary['gates']:
        if g['passed']:
            continue
        h.require(g['case'] == '3200x2400.png/startup' and g['event'] in ('first_ms', 'final_ms'), 'wrong gate')
        cell = summary['summary'][g['case']]
        ref, current = cell['A'][g['event']]['p95'], cell['C'][g['event']]['p95']
        allowance = max(5, .1 * ref)
        result.append(dict(g, reference_p95_ms=ref, candidate_p95_ms=current, allowance_ms=allowance,
                           allowed_p95_ms=ref + allowance, excess_ms=current - ref - allowance))
    return result


def run(output):
    # Check destinations before creating anything; partial failures thereafter sealed.
    protected = [b.ROOT / name for name in h.read(b.PINS)['records']]
    protected += [(b.ROOT / name).parent for name in h.read(b.b.PINS) if name.endswith('/seal.json')]
    protected += [b.Q, b.T, b.D, b.P, b.B, b.E, b.CPU, b.M, b.R]
    h.fresh(output, protected)
    inventories, files = {}, {}
    outcome = dict(status='blocked', decision='Evidence insufficient')
    try:
        (output / 'tools').mkdir()
        for path in [Path(__file__).resolve(), Path(__file__).with_name('verify-preview-startup-applicability.py'),
                     b.ROOT / 'tests/test_preview_startup_applicability.py', b.PINS, *h.tool_paths(b)]:
            files[str(path)] = h.digest(path)
            shutil.copy2(path, output / 'tools' / path.name)
        inventories, bound = b.bind()
        files.update(bound)
        for name in bound:
            path = Path(name)
            if path.parent in (b.ROOT / 'scripts', b.ROOT / 'tests'):
                shutil.copy2(path, output / 'tools' / path.name)
        stages = b.raw_sources()
        sources = source_rows(stages, h.read(b.D / 'anchor-review.json')['C'], h.read(b.P / 'anchors.json'), (b.T / 'C-tracing.diff').read_text())
        raw = b.raw_payloads()
        payloads = payload_rows(raw)
        records = b.execution_records()
        matrix = applicability(sources, payloads)
        facts = b.b.retained()
        for name, value in [('sources', sources), ('payloads', payloads), ('dependencies', dependency_rows(raw, records)),
                            ('provenance', records), ('mappings', mapping_rows(raw, records)), ('matrix', matrix), ('decision', decision(matrix, facts)),
                            ('qualification', gates()), ('populations', h.read(b.R / 'matrix.json'))]:
            h.write(output / (name + '.json'), value)
        h.write(output / 'inputs.json', dict(inventories=inventories, files=files))
        outcome['status'] = 'complete'
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        outcome['failure'] = str(error)
    finally:
        try:
            passed = h.recheck(inventories, files)
        except (OSError, ValueError):
            passed = False
        if not passed:
            outcome.update(status='blocked', failure='input/tool drift')
        h.write(output / 'integrity.json', dict(passed=passed, inventories=inventories, files=files))
        h.write(output / 'assessment.json', outcome)
        (output / 'REPORT.md').write_text('# Qualification C applicability audit\n\n' + outcome['status'] + ': Evidence insufficient\n\n' + outcome.get('failure', 'All proposals deferred. Source compatibility alone selects no optimization. Runtime inputs differ; qualification generation/loading identities unavailable. Qualification remains 78/80. No timing, scheduler state or sample percentage transfers; no experiment prepared.') + '\n')
        h.write(output / 'seal.json', h.inventory(output))
    return outcome


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'complete')
