#!/usr/bin/env python3
"""Read-only membership/provenance boundary. No process execution or decisions."""
import difflib
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location('reconciliation_retained', Path(__file__).with_name('helper-startup-remainder-evidence.py'))
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
h = b.h
ROOT = h.ROOT
PINS = Path(__file__).with_name('startup-reconciliation-pins.json')


def bind():
    roots, inventories, files, accounts, probes = b.bind()
    pins = h.read(PINS)
    files[str(PINS)] = h.digest(PINS)
    seen = set()
    def identity(path, expected):
        path = Path(path)
        h.require(h.digest(path) == expected, 'consumed identity drift: ' + str(path))
        h.require(str(path) not in files or files[str(path)] == expected, 'conflicting dependency identity')
        files[str(path)] = expected
        if path.name == 'seal.json' and path.parent not in seen:
            seen.add(path.parent)
            inventories[str(path.parent)] = h.sealed(path.parent)
            inputs = path.parent / 'inputs.json'
            if inputs.exists():
                for name, value in h.read(inputs).get('identities', {}).items():
                    # Host mappings remain historical provenance. Retained files and
                    # dependency snapshots are checked, not current installations.
                    if Path(name).is_relative_to(ROOT / 'build'):
                        identity(name, value)
    for name, expected in pins.items():
        identity(ROOT / name, expected)
    for name in pins:
        path = ROOT / name
        if path.name.endswith('verification.json') or path.name.endswith('independent.json'):
            record = h.read(path)
            h.require(record.get('status') == 'passed', 'historical verification failed')
            for key, value in record.items():
                if key.endswith('seal') or key.endswith('seal_sha256'):
                    h.require(value in files.values(), 'verification seal not consumed')
    final = h.read(ROOT / 'build/preview-validation-20261115-04-final-verification.json')
    for name, value in final['input_seals'].items():
        h.require(files.get(name + '/seal.json') == value, 'validation provenance mismatch')
    # Raw frozen citations, not source names alone.
    work = ROOT / 'build/preview-verification-work-20261115-04'
    citations = h.read(work / 'source-citations.json')
    for citation in citations:
        path = Path(citation['file'])
        expected = citation.get('sha256')
        h.require(expected and h.digest(path) == expected, 'frozen source identity mismatch')
        files[str(path)] = expected
        lines = path.read_text().splitlines()
        for excerpt in citation['excerpts']:
            h.require(lines[excerpt['line']-1] == excerpt['text'], 'frozen source citation mismatch')
    return inventories, files


def source_relationships():
    old = ROOT / 'build/preview-validation-20261115-04-prepared'
    new = ROOT / 'build/preview-helper-startup-20261116-06'
    anchors = h.read(old / 'anchors.json')
    result = []
    for relative in ('holonight-images/src/isolated/verification.cpp',
                     'holonight-images/src/isolated/generation.cpp',
                     'holonight-file-browser/src/preview/session_pool.cpp',
                     'holonight-file-browser/src/preview/preview_service.cpp'):
        paths = [root / 'baseline/C/source' / relative for root in (old, new)]
        lines = [p.read_text().splitlines() for p in paths]
        anchor_rows = [a for a in anchors if a['variant'] == 'C' and a['file'] == 'source/' + relative]
        for a in anchor_rows:
            h.require(a['anchor'] in '\n'.join(lines[0]), 'instrumentation anchor absent')
        # Only the exact generated include line may be normalized; preserve all
        # remaining differences in the machine-readable unified diff.
        normalized = [[line if not (i == 0 and line == '#include "' + str(root / 'baseline/C/trace.h') + '"')
                       else '#include "<frozen-trace.h>"' for i, line in enumerate(text)]
                      for root, text in zip((old, new), lines)]
        result.append(dict(file=relative, paths=[str(p) for p in paths], hashes=[h.digest(p) for p in paths],
                           anchors=anchor_rows, instrumented_diffs=[dict(path=str(path), sha256=h.digest(path), diff=list(difflib.unified_diff(lines[i], path.read_text().splitlines(), lineterm=''))) for i, path in enumerate([old / 'validation/C/source' / relative, new / 'instrumented/C/source' / relative])], normalized_equal=normalized[0] == normalized[1],
                           residual_diff=list(difflib.unified_diff(*normalized, lineterm='')),
                           exact_diff=list(difflib.unified_diff(*lines, lineterm='')),
                           establishes='boundary compatibility only; timing and runtime-generation identity unproven'))
    return result


def retained():
    def read(name, file):
        return h.read(ROOT / 'build' / name / file)
    return dict(
        remainder=read('preview-helper-remainder-20261116-04', 'decision.json'),
        helper=read('preview-helper-startup-review-20261116-03', 'decision.json'),
        validation=read('preview-validation-20261115-04-findings', 'validation-summary.json'),
        cpu=dict(summary=read('preview-cpu-profile-20261115-03-analysis', 'summary.json'), sampled=[{k: r[k] for k in ('invocation', 'observation', 'sampled')} for r in read('preview-cpu-profile-20261115-03-analysis', 'observations.json') if r['arm'] == 'profiled']),
        work=read('preview-verification-work-20261115-04', 'lifetimes.json'),
        mechanism=read('preview-hash-device-mechanism-20261116-01', 'summary.json'),
        value=read('preview-hash-value-20261116-02', 'decision.json'),
        context=read('preview-hash-value-20261116-02', 'context.json'))
