# Retained startup remainder — 2026-11-16

The next source-bound investigation is **runtime verification inside generation
validation**. The disjoint active-phase set
`v3:generation_validation + v3:runtime_validation` has the uniquely largest median
duration in all **32 required C views**: both endpoints, both supplemental arms,
each of five blocks, pooled observations, and the exact pooled slowest-with-ties
and nearest-median selections from review 03. This is temporal coverage, not causal
attribution or an optimization recommendation.

The earlier [helper decision](helper-startup-decision.md) remains **Evidence
insufficient** for selecting a helper operation. Its competing helper waits and
scheduler results remain context. Qualification remains failed at **78/80** under
unchanged thresholds. No experiment is prepared or executed.

## Evidence and accounting

The [offline reporter](../../scripts/report-preview-helper-remainder.py) binds
accepted review **03**, preparation **06**, native build **04**, execution **04**,
report **07**, and all passing verification-to-seal records. The shared
[read-only evidence boundary](../../scripts/helper-startup-remainder-evidence.py)
checks sealed inventories, consumed hashes, raw v3/v4 citations, and frozen probes.
Historical host hashes and `/run` paths remain provenance; no current installation
or runtime staging is required.

The accepted [result 04](../../build/preview-helper-remainder-20261116-04/REPORT.md)
has [passing independent verification](../../build/preview-helper-remainder-20261116-04-independent.json).
The [verifier](../../scripts/verify-preview-helper-remainder.py) never imports the
new reporter. It reconstructs the windows, helper remainder, phase intersections,
disjoint sweep, decode partitions, distributions, selections, rankings and decision.
It also independently replays review 03's accounting and signed arm comparisons.
Tools and consumed hashes are snapshotted, inputs are rechecked, and complete or
blocked results are sealed in fresh, disjoint directories beneath ignored `build/`.
Development attempts remain retained; only the independently verified result is accepted.

All **150 measured observations / 300 endpoints** reconcile exactly per endpoint:
explained remainder plus still-unmeasured remainder equals the original selected
helper-uncovered duration. **Six warm-ups / 12 endpoints** remain separate.
Baseline receives full-window context because it has no supplemental helper partition.

Startup origin and delivery agree exactly with review 03. Its selected-demand
`uncovered_intervals` are reconstructed by subtracting the identity-matched
supplemental preparation roots. Demand precursor and selected-worker identities
remain distinct; service-control ownership and unavailable IDs remain explicit.
No span is assigned by timestamp proximity. V3 uses the existing phase allowlist
without `helper_prepare`; v4 excludes `transaction_wrapper` and `retirement_call`.
Broad envelopes, setup, standby, shutdown, and helper-boundary discrepancies remain
context. Inclusive phase unions are retained separately from disjoint active sets.
Pre-decode, decode exchange and post-decode partitions use explicitly matched decode
boundaries; missing or ambiguous boundaries block assessment.

The pooled C pixel medians below are separate distributions and must not be added
to reconstruct a median endpoint. Shares are per-observation ratios before summarizing.

| Metric | Instrumented | Captured |
| --- | ---: | ---: |
| Original helper-uncovered remainder | 104.078 ms | 104.706 ms |
| Explained remainder | 103.386 ms | 103.839 ms |
| Still-unmeasured remainder | 0.768 ms | 0.807 ms |
| Leading validation active set | 47.531 ms | 48.656 ms |
| Leading set share of remainder | 46.461% | 47.233% |
| Decode exchange active set | 29.945 ms | 28.473 ms |
| Nested raster/store/PNG serialization active set | 12.333 ms | 12.284 ms |

The complete [distributions](../../build/preview-helper-remainder-20261116-04/distributions.json)
retain variant, arm, endpoint, block, pooling, selection membership, absolute durations,
shares, availability, and inclusive coverage. The [decision votes](../../build/preview-helper-remainder-20261116-04/decision.json)
enumerate all required views. A and baseline supply context only. Signed arm
comparisons remain descriptive, with no overhead correction or quantile subtraction.

## Smallest missing causal distinction

The [startup evidence reconciliation](startup-evidence-decision.md) clarifies that
finer validation, CPU and hashing-mechanism observations already exist in separate
populations. The gap below applies to this execution; those earlier results provide
supporting context without decomposing these newer durations.

The frozen C `RuntimeOwner::refresh()` begins `generation_validation` and calls
`Isolation::verifyRuntime(directory)`. That function begins `runtime_validation` in
`verification.cpp`. Its retained scope covers manifest parsing, per-file attribute
checks, file open/read/SHA-256 verification, and final inventory traversal. The two
nested phases describe one interval; their durations are never added.

The smallest useful missing distinction is identity-bound elapsed coverage of the
per-file open/read/SHA-256 verification versus the other checks within this
`verifyRuntime` call, tied to the same service-control observation and validated
generation. `hash.addData(&file)` combines reading and hashing; existing boundaries
cannot distinguish those costs or waiting. The sealed source files and per-endpoint
probe citations locate this boundary, but supply no substep timing. Helper scheduler
states supply no scheduler inference for this earlier validation interval. This is
missing information for one investigation, not an experiment specification or a
claim that hashing causes the observed duration.

## Reproduction and verification

Choose a fresh destination; collisions and overlapping evidence paths are rejected:

```sh
python3 scripts/report-preview-helper-remainder.py --output build/preview-helper-remainder-NEW
python3 scripts/verify-preview-helper-remainder.py build/preview-helper-remainder-NEW
python3 -m unittest discover -s tests -p test_preview_helper_remainder.py
```

The focused synthetic tests disable process execution and cover identity mismatches,
unavailable IDs, nested/concurrent spans, clipping, envelope exclusion, setup/standby
separation, helper-boundary discrepancies, missing/ambiguous decode boundaries,
selection ties, unavailable versus zero, ranking disagreement, baseline context,
collisions/overlap, input drift, tampering and sealed blocked failures. Existing
native/package verification is reused. No workloads, recorders, builds,
installations, qualification checks or broad container suite run.
