#!/usr/bin/env python3
"""Read-only retained evidence boundary; no remainder arithmetic or process APIs."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location('remainder_review_boundary', Path(__file__).with_name('helper-startup-review-evidence.py'))
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)
REVIEW = h.ROOT / 'build/preview-helper-startup-review-20261116-03'


def bind():
    roots, before, files = h.bind_inputs()
    before[str(REVIEW)] = h.sealed(REVIEW)
    record = REVIEW.with_name(REVIEW.name + '-independent.json')
    checked = h.read(record)
    h.require(checked['status'] == 'passed' and checked['outcome'] == 'complete' and
              checked['evidence_seal'] == h.digest(REVIEW / 'seal.json'), 'review verification binding mismatch')
    files[str(record)] = h.digest(record)
    integrity = h.read(REVIEW / 'integrity.json')
    h.require(integrity['passed'] and h.recheck(integrity['inventories'], integrity['files']), 'review consumed input drift')
    files.update(integrity['files'])
    accounts = h.accounts(roots)
    # Recheck every retained v3/v4 citation, including contextual spans, against raw
    # data. v3 citations historically name .json, but their lines refer to stderr.
    probes = h.read(roots[0] / 'probe-to-source.json')
    for probe in probes:
        path = Path(probe['file'])
        h.require(path.is_relative_to(roots[0]) and h.digest(path) == probe['sha256'] and
                  path.read_text().splitlines()[probe['line']-1] == probe['text'], 'frozen probe mismatch')
    texts = {}
    def citation(event, prefix):
        path = Path(event['file']).with_suffix('.stderr')
        h.require(path.is_relative_to(roots[2]), 'foreign trace citation')
        if path not in texts:
            texts[path] = path.read_text().splitlines()
        raw = texts[path][event['line']-1]
        h.require(raw.startswith(prefix), 'trace prefix mismatch')
        actual = h.json.loads(raw[len(prefix):])
        h.require(actual == {k: v for k, v in event.items() if k not in ('file', 'line')}, 'trace citation mismatch')
    for account in accounts:
        for row in account['lifecycle']['accounting']:
            for span in row['timeline']:
                for edge in ('begin', 'end'):
                    citation(span[edge], 'TRACE ')
        for endpoint in account['endpoints']:
            for span in endpoint['operations']:
                for edge in ('begin', 'end'):
                    citation(span[edge], 'DELIVERY ')
    return roots, before, files, accounts, probes
