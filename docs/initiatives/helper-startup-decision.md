# Offline helper-startup decision review — 2026-11-16

**Evidence insufficient.** No single helper-startup operation satisfies the approved
investigation rule. No optimization is selected. Qualification remains failed at
**78/80** numerical gates under unchanged thresholds.

The [completed diagnostic](helper-startup-diagnostic.md#completed-fresh-attempt)
remains historical evidence. This review uses its retained observations only; it
runs no workload, recorder, build, installation, or qualification check.

## Evidence and reproduction

The review binds preparation **06**, native build **04**, execution **04**, and
report **07**, including each passing independent verification record. Full seals,
inventories, raw helper/v3/v4 citations, source probes, consumed inventories, and
verification-to-seal bindings are checked. Historical host dependency hashes and
protected `/run` paths remain recorded provenance; neither current host packages nor
retained runtime staging are required to reproduce this offline review.

The [assessment tool](../../scripts/assess-preview-helper-startup.py) uses a
[read-only evidence boundary](../../scripts/helper-startup-review-evidence.py).
Its [independent verifier](../../scripts/verify-preview-helper-startup-review.py)
does not import the assessment tool. It independently sweeps interval endpoints,
reconstructs preparation membership, intersects scheduler states, and checks
populations, distributions, selections, rankings, signed comparisons, and the decision.
Both reuse the existing scheduler state reconstruction; operation intersections and
coverage arithmetic are implemented separately. New tools, their imported script
dependencies, synthetic tests, and consumed hashes are snapshotted, inputs are
rechecked afterward, and complete or blocked output is sealed. Destinations must be
fresh, disjoint directories beneath ignored `build/`; collisions are rejected and
partial evidence is preserved.

The accepted result is [review 03](../../build/preview-helper-startup-review-20261116-03/ASSESSMENT.md),
with [independent verification](../../build/preview-helper-startup-review-20261116-03-independent.json).
Its seal is recorded in that verification. The review reconciles **150 measured
observations and 300 endpoints**. The **six warm-up observations / 12 endpoints**
remain in [warmups.json](../../build/preview-helper-startup-review-20261116-03/warmups.json),
excluded from all measured summaries and votes. Earlier review directories are
retained development attempts, not replacements for the historical diagnostic.

To reproduce without executing any experiment, choose a new output name:

```sh
python3 scripts/assess-preview-helper-startup.py --output build/preview-helper-startup-review-NEW
python3 scripts/verify-preview-helper-startup-review.py build/preview-helper-startup-review-NEW
python3 -m unittest discover -s tests -p test_preview_helper_startup_review.py
```

## Accounting and selection

Each endpoint window starts at its explicitly matched v3 `startup_origin` and ends
at its raw v4 delivery timestamp. PID, service and observation bind the origin;
worker and preparation identities bind selected demand. A's unavailable preparation
ID remains unavailable and is matched through its explicit demand lifecycle, never
by timestamp proximity. Preparations are not assumed to be one per observation.

The [preparation inventory](../../build/preview-helper-startup-review-20261116-03/preparations.json)
retains 160 measured preparations: 100 successful selected-demand preparations
(25 per variant and supplemental arm), 50 successful C standby preparations, and
10 exceptional C setup preparations. Eight additional preparations belong to the
warm-ups. Setup, standby, exceptional paths, and warm-ups remain separate. Setup
preparations in this evidence finish before the endpoint origins, so their clipped
endpoint contributions are empty; their full identities and outcomes remain in the
inventory. Baseline has endpoint latency context and no supplemental substeps.

[Endpoint accounting](../../build/preview-helper-startup-review-20261116-03/endpoints.json)
retains clipped inclusive unions and inclusive sums. Rankings use disjoint leaf
scopes plus parent-exclusive residuals, including preparation residuals, rather than
adding session-readiness parents to their children. Uncovered startup time is the
part of the endpoint window outside that group's preparation scopes, including time
after helper preparation; it is not an unidentified helper operation. Per-operation
scheduler totals are task-time, not additive elapsed startup cost across threads.
Captured intervals require matching host/boot/clock/invocation, a unique covering
task lifetime, explicit boundary identity evidence, complete known-state coverage,
and no capture loss or incomplete export. Unrelated global startup warnings are
retained without invalidating reconciled target intervals.

[Distributions](../../build/preview-helper-startup-review-20261116-03/distributions.json)
cover each variant, arm, endpoint and measured block, plus pooling across blocks.
Within each variant, supplemental arm and endpoint, the five slowest traced endpoint
windows are selected with cutoff ties; every observation nearest the median is also
selected. In this evidence each slowest selection contains five observations and
each nearest-median selection contains one. Synthetic tests exercise tied cutoffs
and multiple equally near observations. Selected populations receive new operation
rankings, rather than inheriting pooled rankings.

[Signed comparisons](../../build/preview-helper-startup-review-20261116-03/effects.json)
retain both reconstructed endpoint-window differences and the original harness
block-median arm differences, independently checked against report 07. No overhead
correction or quantile subtraction is applied. Running time includes instrumentation
cost; non-runnable time identifies no blocking cause.

## Views that disagree

All 32 required C votes are retained in
[decision.json](../../build/preview-helper-startup-review-20261116-03/decision.json).
A vote is required for both endpoints, both supplemental arms, every measured block,
the pooled population, and both pooled selection classes. One uniquely largest named
operation must agree across all votes; ties, residual dominance, uncovered dominance,
or missing evidence prevent an investigation recommendation.

The following winners apply to **both pixels and metadata**. Block numbers are the
recorded zero-based block identities.

| C population | Instrumented winner | Captured winner |
| --- | --- | --- |
| Pooled, all 25 | `readiness_marker_receive` | `readiness_marker_receive` |
| Block 0 | `scope_discovery_polling` | `readiness_marker_receive` |
| Block 1 | `readiness_marker_receive` | `readiness_marker_receive` |
| Block 2 | `scope_discovery_polling` | `scope_discovery_polling` |
| Block 3 | `readiness_marker_receive` | `readiness_marker_receive` |
| Block 4 | `scope_discovery_polling` | `scope_discovery_polling` |
| Five slowest | `readiness_marker_receive` | `readiness_marker_receive` |
| Nearest median | `readiness_marker_receive` | `readiness_marker_receive` |

Block 0 disagrees between arms. Blocks 2 and 4 disagree with the pooled and selected
rankings in both arms; instrumented block 0 also disagrees with its pooled ranking.
These are unique operation winners, not ties.

Uncovered time independently rejects **all 32 votes**. For pixels, pooled
instrumented medians are 13.556 ms for marker receive, 10.528 ms for scope discovery,
and 104.078 ms uncovered; captured medians are 16.932 ms, 15.379 ms, and 104.706 ms
respectively. Across the required C pixel populations, uncovered medians range from
98.158 to 114.633 ms. These are separate distribution medians and must not be summed
to reconstruct a median endpoint.

For context only, A's largest pooled selected-demand operation is
`runtime_lease_resolution` (48.717 ms instrumented; 47.838 ms captured, pixels).
C's pooled standby winner is `scope_discovery_polling` (15.624 and 15.711 ms).
Neither supplies acceptance votes for the C selected-demand decision. The captured
C marker-receive median state times are 16.571 ms non-runnable, 0.023 ms runnable,
and 0.183 ms running; scope discovery has 15.169 ms, 0.025 ms and 0.170 ms. Separate
state medians are descriptive and do not identify what either wait depends on.

## Information that would distinguish the views

The retained parent-side scopes locate two competing waits but do not explain their
causes. In the frozen C source, `scope_discovery_polling` wraps `groupOf(...)` plus
repeated `waitForFinished(5)` polling; `readiness_marker_receive` wraps `receive(1)`
after gate write/flush. The latter has no identity-bound observation of the helper
emitting and flushing `R`. Thus these observations cannot distinguish delayed scope
visibility/polling from post-gate launcher, sandbox or helper progress, or from parent
receive scheduling. The retained scheduler states alone cannot resolve that boundary.

The smallest useful missing causal link would connect the selected preparation's
gate release, helper-side readiness-marker emission/flush, and parent receipt, with
explicit invocation/worker/preparation and process-lifetime identities on a shared
clock. For the competing scope-discovery view, the corresponding missing distinction
is when the launched scope becomes observable versus when `groupOf(...)` first sees
it. Explaining the dominant uncovered endpoint time additionally requires relating
existing non-helper v3/v4 phases to these same endpoint windows, rather than assigning
that time to a helper operation. This describes missing information only: no new
experiment is prepared or executed, and no narrower investigation is selected.

## Verification

The 17 focused synthetic tests pass with process execution disabled. They cover
identity/origin mismatches, unavailable A IDs, multiple preparations, separate setup,
standby and exceptional paths, baseline absence, nested spans, clipping, scheduler
gaps/unknown states/loss/incomplete export/identity/lifetime ambiguity, unrelated
warnings, selection ties, ranking disagreement, residual/uncovered rejection,
independent arithmetic and summary tampering, destination collisions/overlap,
input drift, inventory drift, and sealed blocked results. Independent verification
of review 03 passes with all 150 observations, 300 endpoints and six warm-ups
reconciled. Documentation links and whitespace are checked separately. Existing
native/package verification is reused; no broad container suite runs.
