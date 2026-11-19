#!/usr/bin/env python3
"""Read-only retained identities. No preparation or execution imports."""
import importlib.util
from pathlib import Path
import sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('cache_retained', Path(__file__).with_name('preview-streaming-trial-evidence.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
h, ROOT, Q = s.h, s.ROOT, s.Q
DOC = ROOT / 'docs/initiatives/preview-cache-publication.md'
REVIEW = ROOT / 'docs/initiatives/startup-critical-path-review.md'
# Committed review, not the working tree's interpretation of the evidence.
REVIEW_SHA = '7266a56e132d189036462dee6233f29d68db455d80ec79a1433096da71443b6c'
FINDINGS_SHA = '4debe0331e8a7a0f37a5dab2d2ce3ed3fc84826aca060e5b919dce84684ee008'
ARMS = ('control', 'early')
SERVICE = 'holonight-file-browser/src/preview/preview_service.cpp'
RUNTIME = 'holonight-images/src/isolated/runtime.cpp'


def retained():
    value = s.retained()
    h.require(h.digest(REVIEW) == REVIEW_SHA, 'critical-path review drift')
    s.r.merge(value['files'], {str(REVIEW): REVIEW_SHA})
    for name, seal in [
            ('preview-helper-startup-review-20261116-03', '0fc193f8b8bd059445d01fd37b938e7aed50ff98c4e71bb7fd8e81eb854765a7'),
            ('preview-helper-remainder-20261116-04', 'b100c7c5b7b5e6580525b1635ab6a2a1049fc9baf24ebd081f0ee0963445164d'),
            ('preview-startup-applicability-20261116-05', '77a96dff3b8376ad14c112218b5251d9eecd5c6519c5d1d549f08a94272528ca')]:
        root = ROOT / 'build' / name
        h.require(h.digest(root / 'seal.json') == seal, 'accepted review seal drift')
        s.r.merge(value['inventories'], {str(root): s.r.accepted(root, 'complete', 'evidence_seal')})
        record = root.with_name(root.name + '-independent.json')
        s.r.merge(value['files'], {str(record): h.digest(record)})
    findings = ROOT / 'build/preview-streaming-trial-20261117-05-findings'
    h.require(h.digest(findings / 'seal.json') == FINDINGS_SHA, 'streaming findings identity')
    s.r.merge(value['inventories'], {str(findings): h.sealed(findings)})
    for path, digest in h.read(findings / 'inputs.json').items():
        h.require(h.digest(Path(path)) == digest, 'streaming consumed identity')
        s.r.merge(value['files'], {path: digest})
    for phase, outcome in [('prepared', 'prepared'), ('built', 'built'), ('execution', 'complete')]:
        root = ROOT / ('build/preview-streaming-trial-20261117-05-' + phase)
        record = root.with_name(root.name + '-independent.json')
        s.r.merge(value['inventories'], {str(root): s.r.accepted(root, outcome, 'evidence_seal')})
        s.r.merge(value['files'], {str(record): h.digest(record)})
    h.require(h.read(findings / 'assessment.json')['decision'] == 'Deferred', 'streaming decision')
    h.require(h.recheck(value['inventories'], value['files']), 'consumed evidence drift')
    return value


def snapshots():
    paths = h.tool_paths(s) | {Path(__file__), DOC, ROOT / 'tests/test_preview_cache_publication.py'}
    paths |= set((ROOT / 'scripts').glob('*preview-cache-publication*.py'))
    paths.add(s.r.PINS)
    return {str(p): h.digest(p) for p in sorted(paths)}


def schedule():
    rows = [(a, None) for a in ARMS]
    for pair in range(5):
        rows.extend((a, pair) for a in (ARMS if pair % 2 == 0 else ARMS[::-1]))
    return [dict(index=i, arm=a, pair=p, warmup=p is None, count=1) for i, (a, p) in enumerate(rows)]


def protocol():
    return dict(version=1, scenario='startup', requested_size=[256, 256], schedule=schedule(),
        processes=12, measured=10, warmups=2, retries=0, offscreen=True,
        private_cache=True, private_source=True, workload_seconds=30, shared_cleanup_seconds=5,
        cache_flushing=False, affinity_changes=False, artificial_load=False,
        clock='CLOCK_MONOTONIC nanoseconds',
        identities=['invocation', 'service', 'request', 'worker', 'preparation', 'transaction'],
        events=['eligible', 'store_entry', 'store_return', 'enqueue', 'accepted', 'adequate', 'final'],
        supporting_order='store_entry < adequate < store_return',
        native_prerequisites=['target change during commit', 'cancellation', 'timeout', 'shutdown',
            'store failure', 'pixel/metadata ordering', 'cache availability at final', 'session cleanup'],
        future_bindings=['native binaries', 'installed providers', 'runtime payloads', 'protected-generation leases',
            'actual loading identities or explicit unavailable evidence'],
        execution_capability='unvalidated', native_correctness='unvalidated', execution_commands=[],
        qualification='78/80 unchanged', streaming='Deferred', validation_reuse='Deferred',
        candidate_selection='Evidence insufficient', performance_claims=False)
