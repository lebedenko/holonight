# Startup evidence update after the streaming trial — 2026-11-17

**Streaming: Deferred. Overall candidate selection: Evidence insufficient.**
The completed private trial supplies the previously missing startup-effect observation
for buffered 64 KiB streaming. The tested candidate missed the preregistered threshold.
Eliminating this candidate does not establish a priority between validation reuse and
SHA-256 dispatch. No further optimization or experiment is currently selected or
authorized by this addendum.

This updates the proposal dispositions in the [historical reconciliation](startup-evidence-decision.md)
and [qualification C applicability audit](startup-validation-applicability.md), preserving
their evidence and limitations. The [trial protocol](preview-streaming-trial.md),
[fresh findings](../../build/preview-streaming-trial-20261117-05-findings/REPORT.md), and
[independent execution verification](../../build/preview-streaming-trial-20261117-05-execution-independent.json)
record the completed diagnostic population separately from historical qualification.

## Completed trial

Attempt **05** completed all **202 fresh harness processes**: one excluded warm-up per
arm and **100 measured samples per arm**. Ten alternating-order blocks each retained
ten observations per arm. There were no retries, replacement samples or schedule
changes. Assessment is **complete**, independent verification passed, and protected
runtime cleanup was verified using ownership, full-tree identity and conservative
installer lease checks. The cleanup worker exited and was reaped; the private runtime
path was absent.

The trial's [statistics](../../build/preview-streaming-trial-20261117-05-execution/statistics.json)
and [assessment](../../build/preview-streaming-trial-20261117-05-execution/assessment.json)
give the following comparisons. Values are milliseconds; medians are rounded to six
decimal places and p95 uses nearest rank over each arm's measured population.

| Startup event | Control median | Candidate median | Control p95 | Candidate p95 | p95 improvement |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pixels (`first_ms`) | 121.964934 | 120.994332 | 141.951600 | 141.879322 | 0.072278 |
| Final metadata (`final_ms`) | 121.984090 | 121.042048 | 141.963726 | 141.892498 | 0.071228 |

Neither median regressed, but both p95 improvements fell below the unchanged **5 ms**
candidate-planning threshold. Both events had six negative and four positive
candidate-minus-control block median differences, and five negative and five positive
block p95 differences, with no zeros. These descriptive block comparisons do not
replace the preregistered whole-population decision: **Deferred**.

## Updated proposal dispositions

- **Buffered 64 KiB streaming — Deferred.** An identity-bound startup-effect
  observation now exists for the tested private candidate, with passing integrity
  evidence. It did not meet the performance threshold. The earlier missing-effect
  observation is no longer an outstanding gap for this candidate; neither a production
  change nor another streaming trial is selected. This result is not an upper bound
  on possible future savings or proof about every streaming implementation.
- **Avoiding repeated validation — deferred, unchanged.** The retained work audit
  establishes 52 distinct service constructions, each validating once. Repeated
  verification within one proven unchanged owner/generation and an integrity contract
  permitting reuse remain unestablished. Matching payloads or addresses do not prove
  redundancy. The streaming result supplies neither missing fact.
- **SHA-256 execution/dispatch — deferred, unchanged.** Completed CPU and mechanism
  investigations establish sampled hashing execution, without demonstrating a specific
  avoidable execution/dispatch mechanism on the applicable frozen dependency path or
  an integrity-preserving replacement. The streaming result does not establish one.

Overall selection remains **Evidence insufficient**: the remaining proposal-specific
gaps are not ranked by direct evidence to the failed startup gates. Historical
qualification loading/generation limitations also remain. No repeated broad
investigation, new assessment tool or fresh measurement is prescribed.

## Preserved boundaries and verification

Historical qualification remains **78/80**, including its two failed textured-PNG
startup gates and regression allowance of ≤max(5 ms, 10% of reference p95). The
trial's 5 ms planning threshold is separate from that allowance. No diagnostic
difference is subtracted from historical qualification p95 values, and timings,
scheduler states or sample percentages are not transferred between executions.

The [stopped attempt 04](../../build/preview-streaming-trial-20261117-04-findings/REPORT.md)
remains sealed as **Evidence insufficient**, with its one-use marker, partial
observations and separate cleanup evidence preserved. It launched three processes,
accepted only the two excluded warm-ups, and left 199 schedule entries unexecuted.
Its population is not pooled with completed attempt 05 or historical observations.

Read-only checks confirmed the findings seal and recorded input hashes, consumed
preparation/build seals, and passing verification records bound to the preparation,
build and execution seals. Findings statistics match the execution statistics and
complete assessment. Completed native loop, runtime verification, generation, cleanup,
installed-package consumer, synthetic and independent verification are reused; no
builds or test suites are rerun for this documentation-only update.

Frozen tooling, existing documents and ignored local evidence remain unchanged. This
addendum adds no API, production change, assessment tool or measurement. Its local
links, whitespace and final documentation-only diff are checked separately.
