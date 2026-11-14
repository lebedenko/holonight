# Private delivery tracing v4

**UNCOMPILED — no runtime validation or measurements**

This supplemental diagnostic contract prepares frozen A/B/C/D traced sources for
later review. It does not establish compilability, probe overhead, queue residence,
or delivery-gap attribution. C's failed qualification and D's failed pilot remain
unchanged. Native validation and any fixed experiment need a separate plan.

The umbrella preparation tool is
[`prepare-preview-delivery-tracing.py`](../../scripts/prepare-preview-delivery-tracing.py).
It accepts the retained overhead package, completed delivery-gap analysis and an
exclusive destination beneath ignored `build/`, disjoint from both inputs. It
rechecks consumed hashes, historical tool identities, all eight frozen source and
harness inventories, and reconciles the completed delivery analysis using unchanged
historical Python accounting. There are no compiler, harness, shell or subprocess
calls. Every variant's anchors are reviewed independently in temporary trees before
any prepared source tree is emitted. Failure preserves a blocked manifest and any
partial revalidation evidence. Input and tool hashes are recorded before and after.

Only private copies change. Header paths point to a private copy of the v3 header,
whose existing event implementation is unchanged. Private context fields propagate
with its existing captured contexts and RAII bindings, including deferred pool jobs.
D's initial-window deferral is preserved. No production header, public API, protocol,
installed-package contract, timer expression or queued connection type changes.

## Records and identities

Each line is `DELIVERY ` followed by one JSON object. Historical `TRACE ` version-3
records continue unchanged; the historical parser ignores supplemental lines. The
supplemental analyzer preserves raw absolute file paths and one-based line numbers
on every parsed record and both boundaries of every complete span.

| Field | Meaning |
|---|---|
| `version` | Integer 4 |
| `ns` | Nonnegative `CLOCK_MONOTONIC` nanoseconds |
| `pid`, `tid` | Positive actual executing process and Linux thread IDs |
| `service`, `observation`, `job`, `worker`, `preparation` | Existing v3 identities, or JSON null when unavailable |
| `generation` | Private copy of preview result/request generation, or null |
| `session` | Diagnostic execution lifetime ID, or null |
| `transaction` | Diagnostic sourceTransaction wrapper ID, or null |
| `publication` | Fresh diagnostic ID for each result enqueue, or null |
| `endpoint` | `pixel_result`, `final_result`, or `unavailable`; this describes the result, not the harness predicate |
| `operation` | Independent operation or condition named below |
| `edge` | `begin`, `end`, or `point` |
| `span` | Unique diagnostic ID for begin/end pairing; null on points |
| `outcome` | Explicit outcome/reason, or `unavailable` |

Known identities are positive integers. Zero in private C++ context serializes as
JSON null, never as an invented known identity. Session identity becomes available
at execution exchange (and on retirement for stateful variants); wrapper entry can
therefore have an unavailable session. Transaction identities never replace or
increment protocol transactionId/sequence values. A separate diagnostic atomic sequence leaves the v3 identity sequence untouched.
Span pairing uses `(pid, span)`
and requires matching context, endpoint, operation and executing thread. Publication
handoffs use `(pid, publication)` and require identical contextual identities while
allowing the executing thread to differ. Historical zero identities normalize to supplemental null (in particular A/B
preparation). Missing service/job/generation endpoint identities remain unavailable.
No join uses pointer addresses or nearest timestamps. A publication ID remains unique when one callback satisfies both
endpoint predicates. Records outside result delivery can have no publication.

## Operations

Transaction spans are `transaction_wrapper`, `oneshot_ack`, `helper_exit`,
`reusable_completion_ack`, `retirement_call`, and `effective_cleanup`. Scope ends
mean wrapper return or exception exit; completion and helper-exit success are
explicitly marked `sent` (one-shot write accepted), `acknowledged` (reusable
completion validated), and `validated_exit`. Retirement distinguishes
`already_retired` from `effective_retirement`; effective cleanup separately reports
`verified`, `unverified`, or `exception`. A `not_launched` point records the existing
cleanup branch's skip. Reusable success need not retire before delivery. Later
cleanup can have unavailable transaction identity and is never assigned by proximity.

Storage spans are `store_raster`, `store_raster_delegate`, `thumbnail_store`,
`png_serialization`, and `storage_commit`. The original storeRaster short circuit
is recorded as `store.decoded_source`, `store.tier`, `store.success`, and
`store.unchanged` condition points. Each records `true`/`false` only if the original
expression evaluates it. `store_raster` has a `skipped` point on branch rejection.
The cache implementation records existing cancellation, request, image and directory
conditions; serialization and commit record `success`/`failure` independently.
Store early returns use `failure_checkpoint_N`, linked to their exact return sites
in the probe map; surrounding branches retain the failure/cancellation reason.
No predicate or cancellation load is evaluated again for tracing.

Metadata spans are `metadata_format` and `memory_insert`. Formatting preserves the
JPEG/PNG short circuit with `format.jpeg`/`format.png` condition points. Memory
insertion preserves both cancellation loads, successful outcome and unchanged
source checks with `memory.*` condition points. Rejected branches emit `skipped`.
`raster_exit` checkpoints identify the original raster return sites, including
cancellation exits before storage, publication, formatting or insertion. Source
maps retain the exact original function and replacement, including the conditions
surrounding each checkpoint. Conditions not reached remain unevaluated, not false.

Delivery spans are `enqueue_call`, `callback_execution`, `apply_result`,
`changed_emission`, and `harness_execution`. A fresh publication context is captured
by the queued callback and retained synchronously through applyResult and changed.
`result_decision` records `accepted`, `cancelled`, `stale`, or `timed_out` using the
existing branches. Harness `endpoint_pixels` and `endpoint_metadata` points remain
inside their separate original predicates, even when both are satisfied together.

The harness captures callback-entry monotonic time before its original latency
expression, then captures a monotonic timestamp immediately after that expression.
It emits `harness_entry` with the saved entry timestamp and `latency_capture` with
the saved post-capture timestamp only afterward. No harness logging precedes the
original latency capture. `harness_execution` covers the subsequent instrumented
portion, not the entire callback. Even the added timestamp captures impose
**unmeasured diagnostic overhead**; neither saved timestamp is a substitute for
the original harness latency value.

## Offline accounting and acceptance

[`analyze-preview-delivery-tracing.py`](../../scripts/analyze-preview-delivery-tracing.py)
accepts a raw stderr file, exclusive JSON output and `--variant A|B|C|D`. Supply
`--samples original-harness.json` for unchanged historical v3 lifecycle accounting;
without it, historical validation is explicitly parser-only. Supplemental accounting
is independently reported. No trace execution or experimental measurement occurs.

The report separates transaction, storage, metadata and delivery spans. Inclusive
durations remain available alongside unions; never sum nested durations as elapsed
coverage. Endpoint windows clip unions from the explicitly matched v3 decode end to
the supplemental endpoint. Missing or ambiguous decode identities leave the window
unavailable. Enqueue-call duration, enqueue-to-callback elapsed time and callback
execution duration are different fields. A callback can start before enqueue returns
and worker metadata can overlap callback execution. Enqueue-to-callback elapsed time
is **not pure queue residence**.

Missing span boundaries remain unavailable. Duplicate boundaries, malformed records,
incompatible identities, impossible ordering, invalid cleanup outcomes and invalid
endpoint attribution block assessment for the input file; raw records and provisional
intervals remain for inspection, with `assessment_available: false`. Unavailable
cleanup remains unavailable on reusable success. Repeated retirement calls never
count as effective cleanup.

Focused deterministic regressions cover lifecycle paths for A/B/C/D, repeated B
retirement, absent reusable cleanup, storage skips/failures, cancellation/stale and
timeout rejection, nested spans, worker/callback overlap, dual endpoints, cross-thread
identity propagation, malformed and ambiguous evidence, raw references, destination
and hash failures, exact anchors and D preservation. Preparation is checked with
process execution disabled. Final acceptance requires four source overlays, diffs,
inventories and probe maps, unchanged consumed hashes and independent static review.
These checks authorize no native validation, execution, deployment or publication.

## Bounded runtime validation (2026-11-13)

[`run-preview-delivery-smoke.py`](../../scripts/run-preview-delivery-smoke.py)
adds a fixed A/B/C/D startup gate: three fixtures per variant, three observations
per invocation, 120-second process-group timeout, five-second termination grace,
and no retries. It consumes the accepted reassessment, verifies frozen inputs,
stages fresh protected runtimes with the current installer, and requires original
stderr v3 lifecycle accounting plus explicit v4 delivery and transaction evidence.
Synthetic tests cover rejection and stopping before the next launch.

The [first execution assessment](../../build/preview-delivery-runtime-smoke-20261113-01/ASSESSMENT.md)
is **failed before harness execution**: 0 invocations, 0 observations, all 12 rows
unexecuted. All three current-installer staging commands returned zero. The
runner's staged-payload check incorrectly interpreted the regular `current`
generation-name marker as a directory and stopped. Retained input integrity and
final scope isolation passed. The original assessment, runner snapshot and seal
remain unchanged; no retry, uninstall or deletion occurred.

The checker now resolves the marker through `generations/<name>`, validates its
ownership record and exact payload, and checks each variant before staging the
next. A synthetic regression covers the marker contract. A separate
[read-only diagnosis](../../build/preview-delivery-runtime-smoke-20261113-01-diagnosis/diagnosis.json)
verifies the original evidence seal, all preserved staged payload hashes,
protected modes and root ownership. It launches no workloads and does not change
the failed outcome. The corrected runner has not been executed against retained
workloads. Runtime tracing and delivery correlation remain unvalidated.

These additions preserve the historical preparation claims above. They establish
no performance, overhead or gap-attribution result; C's failed qualification and
D's failed pilot conclusions remain unchanged.


## Successful bounded runtime validation (2026-11-13, attempt 02)

The [new execution assessment](../../build/preview-delivery-runtime-smoke-20261113-02/ASSESSMENT.md)
**passed all 12 invocations and 36 observations**, in the fixed A/B/C/D and
three-fixture order, without retries or timeouts. This separately authorized
attempt used fresh protected staging and the corrected runner; the first failed
attempt and its sealed evidence remain unchanged.

All observations passed exact pixel and metadata checks, v3 lifecycle accounting,
and v4 endpoint correlation (72 endpoints), including complete delivery chains
and variant-appropriate transaction acknowledgements, helper exits and cleanup.
Scope and corresponding cgroup isolation passed before and after every invocation
and at finalization. Retained input integrity and staged payload hashes, inventory,
modes and root ownership passed their final comparisons. The evidence seal was
independently rehashed after execution. Private work directories and staged
runtimes remain preserved.

During execution the document was kept at its manifest-verified historical bytes;
the preceding runtime-report section was saved separately and restored afterward.
No historical hash exception or runtime acceptance rule was changed. The earlier
statement that runtime correlation was unvalidated describes attempt 01; this
successful attempt establishes bounded startup tracing and delivery correlation.
It does not establish performance qualification, tracing overhead or completed gap
attribution. C's failed qualification and D's failed pilot remain unchanged.


## Offline delivery accounting (2026-11-14)

The [offline assessment](../../build/preview-delivery-gaps-v4-analysis-20261114-01/ASSESSMENT.md)
replayed all 12 original stderr streams with original harness samples and matched
saved accounting. All 72 endpoint windows were retained with raw references,
branch outcomes, verified frozen probe locations, category unions, separate
wrapper-envelope coverage and specific-operation uncovered intervals. Runtime
and prepared inputs remained unchanged; the output seal was independently checked.
Per-cell summaries contain counts, minima, medians and maxima only.

Accounting is complete; attribution remains incomplete. Probe locations and raw
operations are available for source inspection, but this report does not establish
causal explanations for uncovered time. V4 overhead remains unmeasured. No workload,
installer, compilation or privileged operation ran. C qualification and D pilot
conclusions remain unchanged.

## Offline audit reliability verification (2026-11-14)

Direct synthetic audit tests now cover all 12 scheduled invocations and 72 unique
endpoints using temporary manifests, inventories, hashes and source probes, with
process execution disabled and only trace replay mocked. Regressions cover strict
context matching, unavailable-transaction cleanup exclusion, wrapper envelopes,
dual endpoints, cross-thread overlap and raw references. Invalid destinations,
manifest states, probe containment/hash/line/text errors, incomplete or duplicate
windows and handoffs, replay mismatch, tampering and changes during analysis block
the audit; failures after output creation retain partial evidence and a sealed
blocked assessment. These tests do not depend on retained evidence.

The [fresh offline replay](../../build/preview-delivery-gaps-v4-analysis-20261114-04/ASSESSMENT.md)
retains exactly the original 72 endpoint rows and summaries, including identities,
timings, unions and raw references. Its seal and unchanged runtime/prepared input
inventories were independently rehashed. No workloads were launched. The related
smoke and v3 gap suites pass; the tracing suite's full historical preparation test
is blocked by a retained hash mismatch for `scripts/manage-images-generations.py`.
Historical evidence was not changed to bypass that mismatch.

Attribution remains incomplete and tracing overhead remains unmeasured. This
reliability work changes neither C qualification nor D pilot conclusions.

## Frozen-source timing review (2026-11-14)

The [sealed source review](../../build/preview-delivery-source-review-20261114-01/ASSESSMENT.md)
checks audit `20261114-04` against runtime attempt `20261113-02` and prepared
sources `20261113-03`. All 72 endpoint identities and 24 three-observation cells
are retained in `review.json`, with coverage statistics, exact raw boundaries,
frozen-source excerpts and 39 distinct cases selected by median elapsed time and
largest individual uncovered interval. Input inventories remained unchanged.

Selected largest gaps include enqueue return to callback entry, intervals between
callbacks, and transitions from acknowledgement or cleanup to storage. Frozen
control flow identifies intervening predicates and calls, but the retained
boundaries cannot separate their cost from scheduling, blocking or trace emission.
Specific-operation unions remain separate from wrapper envelopes; nested scopes
and overlapping categories are not additive. Worker/callback overlap is preserved.
The harness `pixels`/`metadata` predicates differ from publication labels; no
retained handoff satisfies both predicates. Unevaluated conditions and cleanup
without transaction identity remain unavailable for attribution.

Independent checks rehashed the review seal and consumed inventories and checked
coverage arithmetic, deterministic selections and source/raw citations. Attribution
remains incomplete and tracing overhead unmeasured. These traced observations do
not establish performance qualification or pure queue residence. The historical
preparation-test hash mismatch, C qualification and D pilot conclusions remain
unchanged. No workloads, builds or installer actions ran.

## Matched v4-versus-v3 overhead preparation (2026-11-14)

The [prepared comparison package](../../build/preview-delivery-overhead-20261114-03/ASSESSMENT.md)
is **uncompiled, unexecuted, overhead unmeasured**. The preparation-only tool
[`prepare-preview-delivery-overhead.py`](../../scripts/prepare-preview-delivery-overhead.py)
consumes the frozen v3 overhead package and v4 preparation, with runtime attempt
`20261113-02`, audit `20261114-04` and the completed frozen-source review as supporting
evidence. It invokes no subprocesses and exposes no build or execution action.

Eight explicitly named `v3`/`v4` A/B/C/D source and harness trees retain verified
private header bytes; only private header includes are relocated. Ordered unique
anchor replay exactly reproduces all retained v4 trees, and the hash-verified
preparation recipe independently confirms anchors and supplemental header content.
Source inventories, tracing diffs, probe maps, equivalence evidence, consumed input
and tool hashes, and the frozen protocol are sealed. The
[independent verification](../../build/preview-delivery-overhead-20261114-03-independent-verification.json)
rehashes the output seal and consumed inputs and verifies all eight trees, private
headers, regenerated probe maps and four replay results.

The later execution protocol fixes three fixtures, separate warm-ups, ten blocks
of ten observations, rotated variant order and alternating mode order: 264
invocations, 2,400 measured observations and 24 warm-ups. It requires original
harness pixel and final-metadata latencies, median and nearest-rank p95, signed
v4−v3 differences and all ten block comparisons. These would be host measurements
of incremental instrumentation effects within the existing startup timer.
Compilation, staging and workload execution require a separate plan. No overhead
budget, significance claim, phase subtraction or performance qualification is
introduced. Attribution remains incomplete; the historical preparation-test hash
mismatch, C qualification and D pilot conclusions remain unchanged.

## Incremental overhead execution (2026-11-14)

The approved fixed comparison now has a separate
[`measure-preview-delivery-overhead.py`](../../scripts/measure-preview-delivery-overhead.py)
runner with `build`, `execute`, and offline `report` actions. It verifies the
prepared package and precisely consumed historical inputs, keeps frozen sources
and private headers unchanged, snapshots tools and the current installer, and
uses private installed prefixes and host Release builds with four jobs. Historical
runners, installer expectations and the documented historical mismatch remain
unchanged.

The [native build assessment](../../build/preview-delivery-overhead-native-20261114-02/assessment.json)
passed all eight v3/v4 A/B/C/D builds, provider-resolution, linkage and runtime
helper checks. An earlier
[blocked build](../../build/preview-delivery-overhead-native-20261114-01/assessment.json)
retains a checker error that incorrectly required provider entries in the first
provider's CMake cache. That error was corrected before the fresh eight-build
attempt; no workloads ran in the earlier output.

The [execution assessment](../../build/preview-delivery-overhead-native-20261114-02/execution/ASSESSMENT.md)
is **blocked after one warm-up invocation**: one warm-up observation executed,
zero measured observations, and 263 invocations unexecuted. All eight protected
runtimes staged successfully. The first v3/A warm-up returned zero and passed
pixel, final-metadata, delivery-order and v3 lifecycle checks. The runner then
incorrectly required 32 private fixture copies. The frozen harness actually
creates `count * 8 + 8`: 16 for this one-observation warm-up and 88 for a measured
ten-observation block. Execution stopped before the next launch, returned nonzero,
and sealed partial evidence. No retry, replacement, repair, resampling, retained
runtime deletion or extra manager cleanup occurred.

The [independent integrity verification](../../build/preview-delivery-overhead-native-20261114-02/independent-verification.json)
checked the original tool identities before subsequent runner corrections, build
and execution seals, prepared inventories, all eight selectors and protected
runtime ownership, modes and exact payload inventories. Final runtime inventories
matched their pre-execution records; final scope isolation passed. The separate
[read-only diagnosis](../../build/preview-delivery-overhead-native-20261114-02/diagnosis/assessment.json)
replayed the saved warm-up accounting and confirmed all 16 private copies against
the original fixture, without modifying the execution evidence or its status.

The final runner corrects the copy-count check and adds guards for tool and fixture
drift, unique runtime paths, and reporting that preserves incomplete evidence.
Ten focused deterministic tests pass, including warm-up/block fixture counts,
one/ten-observation v4 gates for all variants, contamination, ownership, integrity,
timeouts, first-failure stopping, distributions and incomplete reports. The 11
unchanged delivery-smoke tests pass; the nine historical overhead tests pass with
one privileged ownership test skipped in the ordinary sandbox. Corrected execution
has **not** been run. The original executed runner snapshot remains in the native
build evidence.

The [descriptive report](../../build/preview-delivery-overhead-native-20261114-02/report-reviewed/REPORT.md)
records the incomplete outcome without calculating statistics from warm-ups.
**Incremental v4 overhead remains unmeasured.** There are no per-cell or block
performance conclusions, significance claims, causal scheduling/CPU attribution,
or changes to C qualification or D pilot conclusions. A new fixed execution
attempt requires separate authorization; the retained failed attempt is final.

## Hardened fixed overhead comparison (2026-11-14)

The approved fresh attempt at
[`preview-delivery-overhead-attempt-20261114-01`](../../build/preview-delivery-overhead-attempt-20261114-01/)
completed **264 invocations, 2,400 measured observations and 24 separate warm-ups**,
with zero failed or unexecuted invocations and no retries, repairs, resumed work,
replacement samples or fixture removal. Previous attempts remain unchanged.

The runner now uses an explicit local count-aware v4 validator without rewriting
historical tool source. It checks required consumer providers while allowing Images
an empty provider set, validates both runtime manifests against their payloads and
built helper, and rejects overlapping evidence destinations and symlink escapes.
Execution records artifact, tool, fixture, dependency and staging identities before
workloads. Final input, artifact, runtime and scope checks run independently and
retain each outcome without replacing the original failure. Reports validate seals,
scheduled commands, saved accounting, final inventories and protected selectors;
malformed invocation rows yield unavailable counts rather than invented totals.

Before native work, 18 focused deterministic tests passed, including a full synthetic
build → execute → report schedule, real one/ten-observation trace validation for
all variants, trace identity and transaction failures, fixture counts and ownership,
provider requirements, destination collisions, malformed/missing evidence,
timeout/first-failure stopping, independent finalization, replay immutability and
signed median/nearest-rank p95 statistics. The 11 historical delivery-smoke tests
passed; the nine historical overhead tests passed with the privileged ownership
test skipped in the ordinary sandbox. The historical installer mismatch remains
unchanged. No ecosystem acceptance suite or extra retained workload smoke ran.

All eight fresh Release builds used four jobs and the same host dependencies in
Images → Thumbnails → File Browser → benchmark order, with separate private prefixes
and unchanged frozen sources/private headers. The
[native build assessment](../../build/preview-delivery-overhead-attempt-20261114-01/native-build/assessment.json)
passed provider resolution, linkage, tracing-mode and both runtime-bundle checks.
Eight fresh protected runtimes preserved A's legacy layout and B/C/D's managed
selectors. Harnesses ran as UID 1000 with offscreen Qt, that user's session manager
and a successful artifact-write probe. The
[execution assessment](../../build/preview-delivery-overhead-attempt-20261114-01/execution/assessment.json)
records all four final checks passing; build and execution evidence is sealed.

The ordinary sandbox maps host root ownership to `nobody`, so the first
[offline report](../../build/preview-delivery-overhead-attempt-20261114-01/report/REPORT.md)
blocked on protected-runtime ownership. That report and its separate sandbox
verification remain retained. A fresh
[privileged offline report](../../build/preview-delivery-overhead-attempt-20261114-01/report-privileged/REPORT.md)
passed with host ownership visibility, launching no processes and rewriting no
consumed evidence. It contains every per-cell median/p95, signed v4−v3 millisecond
and percentage difference, and all ten block comparisons for pixels and final
metadata. Across the 24 endpoint cells, observed median differences range from
−2.447 to +3.631 ms and p95 differences from −8.292 to +9.745 ms; these ranges do not
replace the per-cell and block results.

The [independent verification](../../build/preview-delivery-overhead-attempt-20261114-01/independent-verification-privileged.json)
passed every check: it independently rehashed build/execution/report seals, verified
consumed inputs and final source/artifact/runtime inventories, checked all eight
protected selectors, and replayed saved accounting without changing evidence. A
separate statistics implementation reproduced all 24 endpoint cells and their ten
block comparisons exactly against both execution and report output. Build and
execution seals were rehashed again after replay.

These are descriptive measurements on this host within the original startup timer.
Negative differences are retained. No threshold, significance claim, overhead
subtraction, causal scheduling/CPU attribution or performance qualification is
introduced. C qualification and D pilot conclusions remain unchanged.

### Offline delivery-gap analysis of the completed overhead attempt

The [gap assessment](../../build/preview-delivery-overhead-gaps-20261114-01/ASSESSMENT.md)
replays all 264 sealed invocations without launching processes or accessing live
protected runtimes. It accounts for 1,200 measured v4 observations and 2,400 endpoint
windows, exactly 100 in each of 24 cells; all 24 warm-up invocations are separately
inventoried and v3 remains overhead context. The new
`scripts/analyze-preview-delivery-overhead-gaps.py` imports historical parsing,
identity and interval helpers without changing historical tools or the frozen runner.

[Endpoint accounting](../../build/preview-delivery-overhead-gaps-20261114-01/endpoints.json)
retains invocation-local identities, harness latency, decode-end elapsed time,
raw records, clipped unions, branches and overlapping operations.
[Summaries](../../build/preview-delivery-overhead-gaps-20261114-01/summary.json)
include minimum, median, nearest-rank p95 and maximum per cell and block.
The [259 selected cases](../../build/preview-delivery-overhead-gaps-20261114-01/selected.json)
retain slowest/median-harness and largest-gap reasons, tied boundary records and
[hash-verified frozen source excerpts](../../build/preview-delivery-overhead-gaps-20261114-01/source-citations.json).

The largest individual endpoint gap is bounded by enqueue return/callback entry in
1,391 windows, cleanup end/storage entry in 377 and successive callbacks in 275.
These patterns recur in the earlier source review, compared descriptively with
separate denominators. Shared intervals across endpoints are not independent events.
Actual queue insertion/dispatch boundaries and runnable/running/blocked transitions
on both threads are the minimum useful next diagnostic for the dominant cross-thread
pattern; enqueue-to-callback elapsed time is not pure queue residence.

[Final integrity checks](../../build/preview-delivery-overhead-gaps-20261114-01/integrity.json)
and [independent verification](../../build/preview-delivery-overhead-gaps-20261114-01/independent-verification.json)
retain separate outcomes. Existing native verification is reused; no builds,
workloads, installers, tuning or qualification runs were performed. The completed
[overhead report](../../build/preview-delivery-overhead-attempt-20261114-01/report-privileged/REPORT.md)
is retained without subtracting overhead or declaring tracing harmless. Current
runtime ownership is not revalidated. Unavailable-transaction cleanup and absent
short-circuit conditions remain unresolved. C qualification and D pilot conclusions
remain unchanged; new instrumentation requires a separate plan.
