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

### Public dispatch and scheduler preparation

The [fresh preparation](../../build/preview-delivery-scheduler-20261114-05/ASSESSMENT.md)
consumes the sealed `preview-delivery-overhead-20261114-03` preparation and
`preview-delivery-overhead-gaps-20261114-01` analysis. All four private v4 source
and harness trees are retained with patches, exact byte replay, hashed probe
locations/excerpts, and independent final input integrity results. Historical
sources, runners and evidence remain unchanged. Earlier preparation iterations
remain retained; `-05` is the reviewed preparation.

`scripts/prepare-preview-delivery-scheduler.py` adds a separate `SCHEDULER` version 1
stream. The private application subclass brackets public `QEvent::MetaCall`
delivery, delegates once and returns the original result; scope destruction emits
the exit on both return and exception propagation. Nested thread-local dispatch
identities are restored on exit and never copied into worker context. Publication
links capture their timestamp before diagnostic output. Original v3/v4 record
formats and queued invocation remain unchanged. Dispatch entry, callback entry and
invoke return stay distinct; callback entry may precede invoke return. Exact queue
insertion is unavailable; none of these intervals establish queue residence.

`scripts/analyze-preview-delivery-scheduler.py` accepts `--accounting`,
`--supplemental`, optional `--scheduler`, and a fresh `--output` beneath ignored
`build/`. Accounting is a JSON array of `{invocation, accounting, clock}` wrappers
around saved v4 analyzer reports. Supplemental input is a JSON array of emitted
records with an added invocation identifier; retain file/line references when
normalizing saved output. Invocation identifiers must be unique strings. The
analyzer retains raw records and indexes, invocation-local publication identities,
nested dispatches, concurrent publications, missing/ambiguous links and signed
invoke-return/dispatch boundaries. Without scheduler input, scheduler attribution
is explicitly unavailable.

The normalized scheduler contract is version 1: `clock` has `name` equal to
`CLOCK_MONOTONIC` and explicit shared host/boot `provenance`, identical to accounting.
No timing-based clock alignment is permitted. Capture `start_ns`/`stop_ns` bound
ordered `events` and `tasks`. Each task has `key: [pid, tid, lifetime]`, lifetime
`start_ns`/`stop_ns`, and initial state `running`, `runnable`, `non_runnable` or
`unknown`; initial running state requires `cpu`. Task-ID reuse requires disjoint
lifetimes. Switch events contain `kind: switch`, `ns`, `cpu`, `prev`, `next` and
`prev_state` (`runnable` or `non_runnable`). Wakeups contain `kind: wakeup`, `ns`,
`cpu` and `task`; the CPU is the event CPU, not an inferred target CPU. Lost records
contain `kind: loss`, `ns` and positive `count`. Unknown initial state, missing
transitions, loss, ambiguous lifetimes and insufficient coverage prevent complete
attribution. Intervals are clipped per thread and boundary window; overlapping
thread/endpoint views remain non-additive. Non-runnable time proves no particular
blocking cause. This input is a normalization contract, not a perf decoder.

The [read-only feasibility report](../../build/preview-delivery-scheduler-20261114-05/host-feasibility.json)
identifies perf 7.3.4-1, kernel 7.3.4-arch1-1 and Qt 6.12.0, retaining binary and
package identity hashes. Scheduler tracepoint formats and trace-clock visibility
were denied in this environment. They remain unverified prerequisites for a later
pilot; no escalation, registration, permission change or kernel tuning was done.
Preparation success does not establish scheduler-capture readiness.

Verification: 16 focused scheduler/preparation test checks, 24 directly relevant
overhead preparation/gap checks and 13 v4 gap-analysis checks passed. Offline tests
disable process launch, exercise identity collisions and ordering, scheduler
preemption/wakeups/migration/lifetime reuse, loss and coverage, destination reuse,
symlink escapes, replay/source mismatches, input drift and sealed partial failures.
Existing native verification is reused. **Uncompiled, unexecuted, incremental
overhead unmeasured**: no native builds, capture, workloads, installation or tuning.
Unavailable-transaction cleanup, unevaluated conditions, C's failed qualification
and D's failed pilot remain unresolved or unchanged.

The historical tracing preparation suite passed 15 of 16 checks; its full-preparation
check remains blocked by the recorded `manage-images-generations.py` hash mismatch.
That historical script and its consumed evidence were not modified.
[Independent verification](../../build/preview-delivery-scheduler-20261114-05-verification.json)
reconstructs all 152 patches and checks 135 citations, the package seal, tool hashes
and unchanged consumed trees. Whitespace checks passed.

### Bounded scheduler pilot: stopped at recorder readiness

The [reviewed blocked report](../../build/preview-delivery-scheduler-pilot-20261114-01-report-reviewed/REPORT.md)
retains the outcome of the approved **B / `160x80.png`** pilot. Exactly one
uncaptured observation ran. It passed correctness, v3/v4 accounting, supplemental
publication linkage, private-work provenance, isolation and cleanup. Recorder
readiness then failed, so **the ten-observation captured invocation never
launched**. There were no workload retries, other fixtures or automatic expansion.
No scheduler attribution or captured-gap recurrence conclusion is available.

The [execution preparation](../../build/preview-delivery-scheduler-20261114-06/ASSESSMENT.md)
retains all four private source variants. Preparation verification independently
reconstructs allowed header relocation, application substitutions, includes and
publication probes from frozen inputs; it verifies complete patches and exact
probe excerpts rather than trusting recorded replacement text. Dispatch identities
now use their own atomic counter. Preparation `-05`, historical tools, consumed
evidence, production sources and historical hash mismatches remain unchanged.
The [final tooling preparation](../../build/preview-delivery-scheduler-20261114-07/ASSESSMENT.md)
also freezes the subsequent offline parser and acknowledgement corrections. It
was not built or executed after the pilot stopped; B's compiled sources remain
bound to `-06`.

[Elevated preflight](../../build/preview-delivery-scheduler-pilot-20261114-01-preflight-privileged/ASSESSMENT.md)
verified consumed seals, source/probe identities, fixture hashes, the previously
verified installer snapshot, installed dependencies, perf options, all six
scheduler tracepoint formats and recording access. It retains kernel, perf, Qt,
host and boot identities, and a small non-preview access probe with explicit
`CLOCK_MONOTONIC` recording attributes (`use_clockid=1`, `clockid=1`). The initial
sandbox preflight was retained as blocked by tracepoint access. `sudo -A` supplied
the scoped privilege; no permissions, sysctls or kernel settings were changed.

[Only B was built](../../build/preview-delivery-scheduler-pilot-20261114-01-native-privileged/assessment.json)
against host dependencies using the recorded Release recipe and four jobs:
Images → Thumbnails → File Browser → harness. Installed-package resolution,
runtime payloads, linkage and a small native dispatch test passed. The native test
covers nested delivery, true/false return preservation, exception propagation and
v4 identity-sequence independence without preview work. The unprivileged build
attempt stopped before compilation because it could not read protected perf
preflight data; the privileged build consumed that data without changing its
permissions. One fresh protected managed runtime was staged with the sealed
installer snapshot and its ownership/collision protections. The harness ran as
UID 1000 with its session environment and offscreen Qt.

The [original execution failure](../../build/preview-delivery-scheduler-pilot-20261114-01-execution/assessment.json)
is `recorder readiness failed`. The recorder used all CPUs, six scheduler
tracepoints, `CLOCK_MONOTONIC`, no stacks and 256 pages per CPU. It was finalized
without launching the captured workload. Raw `perf.data`, recorder streams,
commands, boot identity, partial bounds and the successful uncaptured observation
remain sealed. The original runner required a newline-only acknowledgement;
[upstream perf writes the terminating NUL too](https://github.com/torvalds/linux/blob/master/tools/perf/util/evlist.c#L2311).
The runner now accepts and saves the documented acknowledgement framing, including
fragmented reads. This correction was tested offline, with no second pilot.
The original acknowledgement bytes were not retained, so the framing mismatch is
a supported explanation rather than a byte-confirmed diagnosis.

The [reviewed report](../../build/preview-delivery-scheduler-pilot-20261114-01-report-reviewed/assessment.json)
preserves the original error and independently verifies consumed seals, patches,
citations, uncaptured accounting/linkage and protected runtime integrity. It saves
a nanosecond perf export and recorder clock header before offline normalization.
The partial scheduler stream covers recorder setup only; it does not cover a
preview invocation. [Final integrity](../../build/preview-delivery-scheduler-pilot-20261114-01-execution/integrity.json),
[execution checks](../../build/preview-delivery-scheduler-pilot-20261114-01-execution/execution-final-checks.json)
and [independent report checks](../../build/preview-delivery-scheduler-pilot-20261114-01-report-reviewed/integrity.json)
passed, including unchanged inputs/artifacts/runtime, empty helper scopes and no
residual preview processes. Protected runtime and fixture evidence remain retained.

`scripts/run-preview-delivery-scheduler.py` provides `preflight`, `build`, `execute`
and `report` actions with fresh, disjoint destinations beneath ignored `build/`.
Execution is fixed to one uncaptured observation followed by one ten-observation
invocation, with a 30-second workload/capture bound and five-second termination
or finalization grace. A built-artifact execution marker prevents reuse. Failure
stops dependent actions and seals partial artifacts with separate final checks.
`scripts/normalize-preview-delivery-perf.py` consumes saved perf exports, recording
metadata and explicit task-identity records; it and the analyzer launch no
processes. File/line/raw references are retained. Task exit is kept distinct from
the final switch-out, and initial state remains unknown until established.

Scheduler contract version 2 preserves version 1 input support. External task keys
may have a null process ID; a tracepoint TID never invents a task-group identity.
Idle task lifetimes are separate per CPU. `diagnostics` scope identity/lifetime
uncertainty to affected tasks, while `export_complete=false`, loss or incompatible
clock provenance prevents complete attribution. Unresolved target identities,
unknown state or missing transitions in a target window also prevent completion;
unrelated incomplete initial history does not invalidate all target windows.
Actual per-thread dispatch stacks reject sibling overlap, wrong enclosing
publication ownership, duplicate/orphan records and cross-thread identity
conflicts. Invoke return, dispatch entry and callback entry remain separate, with
signed ordering differences. Positive return-to-callback windows retain clipped
running, runnable, non-runnable and unknown time for both publication threads,
split at dispatch entry. Overlapping thread/endpoint views are non-additive;
non-runnable time identifies no blocking cause and exact queue insertion is absent.

Verification: 33 focused scheduler/preparation/pilot checks, 24 directly affected
overhead preparation/gap checks, 18 overhead-runner checks and 13 v4 gap-analysis
checks passed. Offline tests forbid process launches and cover preparation edits,
probe omissions, nesting, identity independence, external wakeups, migration,
idle CPUs, reuse, unknown history, missing transitions, clocks, malformed/truncated
input, loss, raw references, recorder ordering/framing/timeouts, fixed limits,
first-failure stopping, destination reuse, symlink escapes, input drift and sealed
partial failures. Broader native verification was reused; no ecosystem acceptance
suite ran. Whitespace checks passed. Incremental overhead remains unmeasured;
unavailable-transaction cleanup, unevaluated conditions, C qualification and D
pilot conclusions remain unchanged.

## Recorder rehearsal attempt 2026-11-14 (-02)

The separately bounded attempt stopped at its recorder-only preflight. No build,
managed runtime, uncaptured observation or captured preview invocation ran, and
there was no recorder retry. Preparations `-05` through `-07`, the first pilot and
its execution marker remain unchanged.

[Fresh preparation -08](../../build/preview-delivery-scheduler-20261114-08/ASSESSMENT.md)
retains all four source variants and freezes the corrected runner and focused
regressions. Preflight now uses the capture control-pipe/acknowledgement and
shutdown path, immediately finalizing after readiness without a preview workload.
Successful rehearsal requires explicit monotonic clock/boot provenance, all six
configured tracepoints, a saved nanosecond export, successful normalization and
no capture loss. Recorder process identity, acknowledgement bytes and readiness
bounds are retained. Shutdown shares one five-second deadline: four seconds for
graceful termination and the remaining second for forced termination and explicit
reaping. A timeout remains a failure even after successful cleanup; the original
error is preserved separately from cleanup evidence. Residual-process checks
include perf recorders as well as preview processes. Production interfaces and
scheduler versions 1/2 remain unchanged.

The [single elevated rehearsal](../../build/preview-delivery-scheduler-pilot-20261114-02-preflight/assessment.json)
used `sudo -A` without changing permissions, sysctls or kernel settings. It received
acknowledgement bytes `61636b0a00` (`ack\n\0`) after 498,665,104 ns. Perf wrote raw
recording data, then returned `-2` after SIGINT. Shutdown therefore failed the
existing successful-exit requirement with `recorder failed`; it did not time out,
did not require forced termination and explicitly reaped the child. This proves
the acknowledgement exchange on this host but does **not** establish successful
recorder finalization or authorize dependent work.

The [reviewed blocked report](../../build/preview-delivery-scheduler-pilot-20261114-02-report-reviewed/REPORT.md)
retains the original failure and independently verifies consumed inventories,
seals, current preparation source reconstruction and citations. It saves a
nanosecond export and header from the retained raw recording; the header records
all six scheduler tracepoints with `use_clockid=1, clockid=1`. The rehearsal did not
reach normalization, so export completeness and loss-free capture are not claimed.
All preflight and reviewed-report final integrity checks passed, with isolated
helper scopes and no residual preview or recorder processes. No runtime was
staged. Signed publication boundaries, both-thread interval accounting and gap
recurrence are unavailable because no preview invocation ran.

The [first report](../../build/preview-delivery-scheduler-pilot-20261114-02-report/assessment.json)
is also sealed and preserved. It retained `recorder failed` and separately recorded
`header replay mismatch`: historical preparation `-05` predates the corrected
header. The report-only correction verifies that historical input by its consumed
inventory and seal, while reconstructing the current preparation against current
rules. The reviewed report performs no new recording or workload execution.

Verification: 36 focused scheduler/preparation/pilot tests passed, including
NUL-terminated and fragmented acknowledgements, EOF/malformed replies, early
recorder exit, readiness timeout, graceful shutdown, forced termination/reaping,
the shared shutdown deadline, first-error preservation, blocked build gating and
sealed partial artifacts. Offline normalizer/analyzer tests remain process-launch
free. Whitespace checks passed. No ecosystem acceptance, performance qualification,
overhead measurement, C/D reassessment or production changes were performed.

## Corrected SIGINT shutdown and fresh pilot 2026-11-14 (-03)

Shutdown now accepts `-SIGINT` only after recorder readiness and a SIGINT sent by
the runner itself. Early signal exits, other signals, forced termination and
shutdown timeouts remain failures. Export, clock/boot, tracepoint, normalization
and loss checks remain mandatory. Regression coverage includes expected versus
unsolicited SIGINT exits and other-signal rejection.

[Preparation -09](../../build/preview-delivery-scheduler-20261114-09/ASSESSMENT.md)
freezes all four variants and the corrected tooling. The
[single fresh elevated rehearsal](../../build/preview-delivery-scheduler-pilot-20261114-03-preflight/assessment.json)
passed acknowledgement, expected SIGINT shutdown, reaping, all six tracepoints,
explicit monotonic clock/boot provenance, export, normalization and no-loss checks.
The [fresh host-native B build](../../build/preview-delivery-scheduler-pilot-20261114-03-native/assessment.json)
then passed the recorded four-job Release recipe, installed-package resolution,
runtime payload and linkage checks, and the native dispatch test.

The [sealed execution](../../build/preview-delivery-scheduler-pilot-20261114-03-execution/assessment.json)
staged one protected managed runtime and ran as UID 1000 with offscreen Qt.
Exactly one uncaptured observation passed correctness, v3/v4 accounting,
supplemental linkage, input/runtime integrity, isolation and cleanup. Exactly one
ten-observation captured invocation then completed. Recorder readiness and
shutdown passed, including explicit reaping with no timeout or forced termination.
No workload was repeated or fixture set expanded; the build execution marker
remains retained.

The attempt stopped at `scheduler attribution incomplete`. All 20 publication
rows linked with no publication-linkage issues. Signed invoke-return-to-dispatch
intervals range from 15,408 to 237,088 ns; dispatch-to-callback intervals from
2,295 to 28,274 ns; invoke-return-to-callback intervals from 39,605 to 244,555 ns.
All callback entries follow invoke return. Both-thread interval accounting is
retained in `analysis.json`, but complete attribution is unavailable. The saved
export produced 26 normalizer diagnostics, including scheduler records rendered
with TID `-1`, which the current parser rejects. `export_complete` is false;
no loss records were parsed, which does not establish a complete loss-free stream.
Scheduler diagnostics also include missing transitions, inconsistent CPU ownership
and missing wakeups. No parser or attribution repair was made during this attempt.

For example, the first publication's 191,318 ns return-to-callback window has
provisional receiver totals of 45,507 ns running, 5,892 ns runnable and 139,919 ns
non-runnable, while its publisher interval remains unknown. Both thread views are
marked incomplete. These are diagnostic intervals, not a qualified scheduler
explanation. No conclusion about recurrence of the historical gap is established.

The [reviewed report](../../build/preview-delivery-scheduler-pilot-20261114-03-report-reviewed/REPORT.md)
independently verifies consumed sources/citations, inventories, seals, uncaptured
accounting, protected runtime, normalization and analysis replay. Raw recording,
nanosecond exports, clock headers and both-thread intervals remain sealed.
Execution and reviewed-report final checks all passed, including runtime integrity,
scope isolation and absence of residual preview or recorder processes. The
[first report](../../build/preview-delivery-scheduler-pilot-20261114-03-report/assessment.json)
remains preserved: its additional replay comparison failure was caused by tuple
identities becoming JSON lists. The report-only correction compares serialized
JSON representations; the replay is equivalent and attribution remains blocked.
The interruption during reporting caused no additional workload execution.

Verification: 37 focused scheduler/preparation/pilot tests and whitespace checks
passed. Earlier attempts and preparations are preserved. No ecosystem acceptance,
performance qualification, overhead measurement, C/D reassessment, production
changes or unrelated `holonight-grub/` changes were performed.

## Offline unknown-prefix correction for pilot -03

The user-authorized offline reanalysis preserves the original capture and all
sealed blocked assessments. The earlier description of “26 unparsed records” was
imprecise: there were **14 unparsed final switch records and 12 resulting exit
without final switch diagnostics**, totaling 26 normalizer diagnostics.

The normalizer now accepts the explicit unknown sentinel `-1` in either sample
prefix PID/TID field. Other negative values and malformed identities still fail
parsing. Scheduler task identities continue to come from tracepoint payloads and
corroborated publication records; sample-prefix identities never supply an invented
TGID. The regression reproduces final switch-out after process exit, checks raw
references and payload identities, and forbids process launches. It failed before
the correction and passed afterward.

[Fresh offline normalization](../../build/preview-delivery-scheduler-pilot-20261114-03-offline-normalized-01/assessment.json)
recovers all 14 final switches. The saved export is now complete with no normalizer
diagnostics and no parsed loss records. The
[fresh offline analysis](../../build/preview-delivery-scheduler-pilot-20261114-03-offline-analysis-01/assessment.json)
reports `attribution_complete=true` for all 20 publication rows and 40 thread
windows. Signed boundary intervals are unchanged. Both-thread running, runnable,
non-runnable and unknown totals and splits remain available per publication.
The first receiver window retains the previously reported 45,507 ns running,
5,892 ns runnable and 139,919 ns non-runnable; its accounting is now complete.

There remain 32 missing-switch-transition and 31 missing-wakeup-or-duplicate-running
scheduler diagnostics outside complete target windows. These are retained under
the existing scoped uncertainty rules; no attribution rules were relaxed. Complete
target accounting does not imply complete initial history for every recorded task,
and non-runnable time establishes no blocking cause.

The [independent offline report](../../build/preview-delivery-scheduler-pilot-20261114-03-offline-report-01/REPORT.md)
seals replayed analysis and tool snapshots. Original capture seals, consumed input
inventories/seals, current preparation source reconstruction/citations, offline
input hashes, normalization/analysis replay, protected runtime integrity, isolation
and residual-process checks passed. No recording, native build or preview workload
was launched for this correction. The original execution remains historically
blocked; the new offline report establishes complete target attribution from its
retained export.

Verification: 39 focused scheduler/preparation/pilot tests and whitespace checks
passed. Changes are limited to the offline parser, focused tests and this note.

## Interpretation of the completed B scheduler pilot (2026-11-14)

The [sealed offline interpretation](../../build/preview-delivery-scheduler-interpretation-20261114-03/REPORT.md)
uses the original `-03` execution, corrected normalization and analysis, and the
historical overhead gap package. The new
[`report-preview-delivery-scheduler.py`](../../scripts/report-preview-delivery-scheduler.py)
verifies seals, consumed hashes, frozen-source reconstruction and citations,
replays accounting and corrected scheduler analysis, and seals a blocked report
on failure. Original blocked execution and analysis assessments remain unchanged.
No builds, recorders, preview workloads or live-runtime checks ran.

All ten captured observations are retained separately from the single uncaptured
observation. The captured group has 20 endpoints, 20 unique publications and 40
complete thread windows; the uncaptured observation has two endpoints and two
publications, with scheduler states unavailable. Endpoint ownership follows
accounting identities and invocation-local publication linkage, including the
possibility that one publication satisfies both harness predicates. Publication
labels are not substituted for the pixel/metadata predicates. No cross-invocation
join uses publication IDs or timestamp proximity.

The historical enqueue-return → callback-entry boundary pattern appears in this
pilot: all 20 captured publication intervals are positive. Using those same
boundaries for both datasets gives the following descriptive nanosecond values.
Each pilot endpoint has ten samples; its nearest-rank p95 is therefore its maximum.
Each historical endpoint has 100 samples from ten invocations. The combined views
in `summary.json` retain their separate unique-publication denominators.

| Dataset | Endpoint | Observations / endpoints / publications | Minimum ns | Median ns | p95 ns | Maximum ns |
|---|---|---|---:|---:|---:|---:|
| Captured pilot | Pixels | 10 / 10 / 10 | 39,605 | 120,870 | 191,318 | 191,318 |
| Historical B / 160x80.png | Pixels | 100 / 100 / 100 | 4,239 | 93,855.5 | 160,057 | 173,198 |
| Captured pilot | Metadata | 10 / 10 / 10 | 54,125 | 166,443.5 | 244,555 | 244,555 |
| Historical B / 160x80.png | Metadata | 100 / 100 / 100 | 51,271 | 154,822 | 239,260 | 403,109 |

The largest pixel window is observation 1, publication 16: 191,318 ns, comprising
168,705 ns before dispatch entry and 22,613 ns from dispatch to callback. The
receiver has 45,507 ns running, 5,892 ns runnable and 139,919 ns non-runnable; the
publisher has 95,195 ns running and 96,123 ns non-runnable. The largest metadata
window is observation 4, publication 112: 244,555 ns, comprising 237,088 ns before
dispatch and 7,467 ns afterward. Its receiver has 86,421 ns running, 12,198 ns
runnable and 145,936 ns non-runnable; its publisher has 29,068 ns running and
215,487 ns non-runnable. Both selected receivers are running throughout their
respective dispatch-to-callback intervals. Every target thread window has zero
unknown time. These overlapping thread views must not be summed.

[Publication rows](../../build/preview-delivery-scheduler-interpretation-20261114-03/publications.json)
retain all signed return/dispatch/callback intervals, both-thread states and splits
at dispatch entry.
[Selected timelines](../../build/preview-delivery-scheduler-interpretation-20261114-03/selected-timelines.json)
retain tied maxima, establishing scheduler transitions and exact raw references;
[raw citations](../../build/preview-delivery-scheduler-interpretation-20261114-03/raw-citations.json)
and [source citations](../../build/preview-delivery-scheduler-interpretation-20261114-03/source-citations.json)
retain file hashes, line numbers and records or frozen probe excerpts. The 32
missing-switch-transition and 31 missing-wakeup-or-duplicate-running diagnostics
remain preserved. They occur outside the complete target windows; resolved target
lifetimes, coverage and reconciled state totals justify retaining complete target
accounting under the unchanged scheduler rules.

Verification: 12 new process-launch-free reporting regressions and all 39 existing
scheduler/preparation/pilot checks passed. They cover endpoint mapping, duplicate
and overlapping publications, invocation-local identity collisions, signed
intervals, thread and dispatch-split reconciliation, tied maxima, ten-sample
statistics, raw citation mismatch, destination rejection, input drift and sealed
failures. The [independent verification](../../build/preview-delivery-scheduler-interpretation-20261114-03-verification.json)
checks input/output seals and hashes, normalization and analysis replay, endpoint
ownership, all observations, summary denominators and statistics, selections,
thread arithmetic and source/raw citations without importing the reporting tool.
Scoped elevation read protected retained evidence without changing permissions.
Whitespace checks passed. Earlier sealed exploratory reports remain preserved.

Instrumentation differs, so the distributions establish neither statistical
significance nor a change in the underlying distribution. No recurrence threshold
was invented. Non-runnable time identifies no blocking cause, and enqueue-return
→ callback-entry is not pure queue residence. Overhead remains unmeasured; no
subtraction, production/API change, performance qualification or C/D reassessment
is made.

Recommendation: these complete, sub-millisecond pilot windows do not by themselves
justify another experiment. A separately approved matched experiment would be
justified only to investigate the larger historical metadata tail or quantify
recurrence under comparable instrumentation; this ten-observation pilot cannot
answer that question. No further experiment was executed.

## Retained startup bottleneck priorities (2026-11-14)

The [sealed offline report](../../build/preview-startup-bottlenecks-20261114-06/REPORT.md)
replays only the 20 measured v4 A/C invocations for `3200x2400.png`: 200
observations, 400 endpoints and 400 invocation-local unique publications. Existing
validated matched overhead summaries are reused; the full 264-invocation audit
is not repeated. The corrected-reference qualification and completed B/small-PNG
scheduler interpretation remain separate context. No builds, recordings, preview
workloads, live-runtime inspections or qualification runs were performed.

C's median per-observation trace-window shares rank **pre-decode**, then decode
exchange, then post-decode for both endpoints. Pre-decode has approximately 63.6%
median share, 86.514 ms median duration and 106.814 ms nearest-rank p95. A's
corresponding durations are 84.848 ms median and 102.082 ms p95. C's decode
exchange has 29.912 ms median and 38.925 ms p95; post-decode has 19.315 ms median
and 21.518 ms p95 for pixels, and 19.361 ms median and 21.532 ms p95 for metadata.
The selected slowest harness observations support the same pre-decode priority.
These shares use each trace-origin-to-endpoint window, not the original harness
timer. They are neither optimization gains nor causes of the separate failed gate.

[Observation rows](../../build/preview-startup-bottlenecks-20261114-06/observations.json)
retain original harness latency, explicit coarse boundaries, clipped operation
unions, nested spans, overlap excess, uncovered intervals and full timelines.
[Pooled and block distributions](../../build/preview-startup-bottlenecks-20261114-06/distributions.json)
include minimum, median, nearest-rank p95 and maximum with explicit observation,
endpoint and publication denominators.
[Rankings](../../build/preview-startup-bottlenecks-20261114-06/rankings.json)
retain A's distributions alongside C's; overlapping spans are never added and
quantiles are never subtracted.
[Selected timelines](../../build/preview-startup-bottlenecks-20261114-06/selected-timelines.json)
include five slowest harness samples with cutoff ties, every nearest-median tie
and every largest-uncovered-interval tie.
[Publication rows](../../build/preview-startup-bottlenecks-20261114-06/publications.json)
preserve signed return-to-callback windows and count dual-endpoint publications
once. Exact raw and frozen v3/v4 source citations are retained separately.

The [provenance](../../build/preview-startup-bottlenecks-20261114-06/provenance.json)
records unavailable normalized source equivalence between traced A and this
qualification's A-fixed freeze; those runs are not assumed interchangeable.
[Qualification context](../../build/preview-startup-bottlenecks-20261114-06/qualification-context.md)
preserves the original outcome. The B pilot's scheduler states are not assigned
to A/C. Next investigate the observed pre-decode interval. Discriminating its
hypotheses requires matched qualification-time phase evidence, normalized source
comparison, A/C scheduler/blocking evidence and finer validation/transport/work
boundaries. No follow-up experiment was executed. Historical thresholds, C's
failed qualification and D's failed pilot remain unchanged.

Verification: 10 process-launch-free reporter regressions, 12 scheduler reporting,
8 overhead gap, 13 v4 gap and 7 v3 gap checks passed. They cover ownership,
missing/ambiguous boundaries, clipped nested coverage, signed publications,
dual endpoints, denominators, deterministic rankings, tied selections, quantiles,
input drift and sealed blocked assessments. The
[independent replay](../../build/preview-startup-bottlenecks-20261114-06-verification.txt)
checks the output seal, all 20 selected invocations, coverage arithmetic,
distributions, rankings, selections, publication windows and source/raw citations
without importing the reporter. Scoped elevation reads protected retained hashes;
permissions are unchanged. Whitespace checks passed. Broader unchanged verification
is reused; production and public APIs are unchanged.

## Retained pre-decode phase priorities (2026-11-15)

The [sealed offline drill-down](../../build/preview-predecode-20261115-06/REPORT.md)
replays the same 20 measured v4 A/C large-PNG invocations. It verifies 400 endpoint
mappings, then analyzes 200 invocation-local observations once each: pixel and
metadata pre-decode boundaries, spans and ownership agree. Their endpoint-window
shares differ because delivery times differ; both original harness latencies and
endpoint references remain preserved. Existing matched overhead and scheduler
verification are reused without another workload or scheduler analysis.

C's largest disjoint phase set is **generation validation + runtime validation**:
56.773% median share of pre-decode, 66.328% nearest-rank p95 share, 49.280 ms median
and 58.113 ms p95 elapsed time. Runtime validation is nested inside generation
validation. The next group is helper preparation outside measured nested spans:
34.161% median share, 28.418 ms median and 42.681 ms p95. Inspect exchange outside
nested acquisition follows at 4.799% median share and 4.220 ms median; source
capture follows at 1.939% and 1.657 ms. Every selected C class—including the five
slowest pre-decode observations with cutoff ties, nearest-median ties, largest
uncovered-gap ties and existing endpoint harness selections—has the same dominant
validation group. These overlapping selections are descriptive, not independent
samples.

Inclusive generation validation is 50.068 ms median / 59.113 ms p95; its time
outside runtime validation, computed per observation before summarizing, is
0.673 ms / 1.065 ms. Inclusive C helper preparation is 28.423 ms / 42.683 ms.
A's runtime validation is 48.629 ms / 58.347 ms, nested inside its 78.437 ms /
94.932 ms helper preparation. A helper time outside nested measured spans is
28.140 ms / 41.052 ms. These distributions are not obtained by subtracting
quantiles. A's generation phases remain absent by design; other missing phases
remain unavailable. Measurements do not establish a validation speedup.

[Observation rows](../../build/preview-predecode-20261115-06/observations.json)
retain clipped inclusive spans, phase unions, disjoint segments labelled by their
active phase set, uncovered time and parent interval subtraction.
[Endpoint mappings](../../build/preview-predecode-20261115-06/endpoint-mappings.json)
preserve both harness endpoints.
[Pooled/per-block distributions](../../build/preview-predecode-20261115-06/distributions.json)
include count, minimum, median, nearest-rank p95 and maximum.
[Rankings](../../build/preview-predecode-20261115-06/rankings.json) include zero
coverage for valid observations where a phase-set group is absent, with A beside
C. [Selected timelines](../../build/preview-predecode-20261115-06/selected-timelines.json)
and [selection comparisons](../../build/preview-predecode-20261115-06/selection-comparison.json)
retain all ties and compare group shares without adding overlapping intervals.

The [source comparison](../../build/preview-predecode-20261115-06/source-comparison.json)
resolves the earlier unavailable source relationship: recorded literal anchors
reproduce v4 from frozen AT, matched v3 differs from AT only in the private trace
include path, and an explicit allowlist of private v3 tracing/include edits
reconstructs every production-source byte of AU. AU's complete source inventory
matches this qualification's A-fixed inventory exactly. The comparison records
all transformations, the exact U/T diff and empty residual/qualification diffs;
it executes no historical recipe. This proves source equivalence under those
private tracing transformations, not binary, runtime or timing equivalence.
Historical qualification results remain separate and unchanged.

[Frozen call-chain excerpts](../../build/preview-predecode-20261115-06/source-boundaries.md),
[source citations](../../build/preview-predecode-20261115-06/source-citations.json)
and [raw citations](../../build/preview-predecode-20261115-06/raw-citations.json)
link the probes to construction, pool demand preparation, RuntimeOwner::refresh,
verifyRuntime, helper launch/readiness, capture and inspect/decode exchange.
Generation validation includes protected-tree checks and verifyRuntime; the latter
contains manifest parsing, attribute checks, file reads/SHA-256 and inventory
traversal. C helper preparation resolves an existing lease before launcher/scope,
gate and readiness work; A validates inside helper preparation. No durations are
assigned to individual uninstrumented calls, hashing, launcher operations or
scheduling.

The narrowest next investigation is inside runtime validation, supported by both
median and selected-tail evidence. A separately approved measurement would need
boundaries for protected-tree traversal, manifest read/parse, file attributes,
file reads/hash computation and final inventory traversal, plus matched A/C
scheduler switch/wakeup and blocking evidence to distinguish running work,
runnable delay and non-runnable waits. The secondary helper hypothesis requires
launcher start, scope discovery/limit verification, gate release and readiness
boundaries; transport requires separate writes/reads. No experiment was executed.
These retained elapsed times are not causes of the separate failed qualification,
optimization gains or overhead-adjusted measurements. C's qualification and D's
pilot conclusions remain unchanged.

Verification: 18 new process-launch-free regressions and 56 affected existing
reporting/accounting checks passed. Coverage includes endpoint deduplication and
ownership, clipping, nesting, cross-thread overlap, disjoint reconciliation,
missing phases, per-observation subtraction, deterministic ranking, tied
selections, quantiles, restricted source reconstruction, qualification differences,
provenance mismatches, destination rejection, input drift and sealed failures.
The [independent replay](../../build/preview-predecode-20261115-06-verification.json)
uses a [standalone verifier](../../build/verify-preview-predecode-20261115.py)
without importing the reporter and checks seals/hashes, all observation arithmetic,
distributions, rankings, selections, source transformations and citations.
Protected evidence was read with scoped `sudo -A`; permissions were unchanged.
Whitespace checks passed. No builds, recordings, preview workloads, live-runtime
inspection, API changes or qualification reruns were performed.

## A/C validation and scheduler protocol (2026-11-15)

The private diagnostic tooling is
[`prepare-preview-validation.py`](../../scripts/prepare-preview-validation.py),
[`run-preview-validation.py`](../../scripts/run-preview-validation.py),
[`report-preview-validation.py`](../../scripts/report-preview-validation.py), and
[`verify-preview-validation.py`](../../scripts/verify-preview-validation.py).
Only ignored copies of frozen A/C source and harness trees receive probes. No
production source, installed package, public API, launcher expression, harness
latency expression, qualification threshold or historical outcome changes.

Preparation resolves the frozen inputs through the completed pre-decode report,
checks recorded seals and inventories, repeats A/A-fixed reconstruction, and
replays recorded v4 anchors as literal data without executing historical recipes.
The fixture identity comes from the bound execution preregistration, rather than
assuming the previous reporter consumed the fixture directly. All A/C probe
anchors are reviewed before emitting source trees. Baseline copies retain v4;
validation copies append an independent RAII stream. Source inventories, literal
anchors, diffs, tool snapshots and probe citations are sealed. Preparation performs
no compilation or process launch.

Each `VALIDATION` record has invocation-local `(pid, validation)` and `(pid, span)`
identities, a parent span, actual executing thread, existing service/observation/
job/worker/preparation context, manifest ordinal (`-1` outside file work), operation,
edge, monotonic timestamp and exit outcome. Validation and span sequences do not
advance v3/v4 identities. Nested runtime validation has its own validation identity
and retains its generation parent. RAII records balanced exceptional exits; accepted
measurements require successful original correctness gates and returned exits.

Runtime probes cover initial path/manifest checks, manifest reading, parsing and
policy, file-record preparation, attributes, open, **combined reading and hashing**,
digest comparison, required files and inventory traversal. `hash.addData(&file)`
remains the original combined operation. Its short circuit with open and digest
comparison is preserved. C additionally measures protected base/generation trees,
selector/descriptors, nested runtime validation, manifest open/read, parse/policy,
digest and final identity checks. No finer helper instrumentation is introduced.
The built runtime manifest freezes the ordinal-to-relative-path/size/digest mapping.

The fixed budget is 100 observations per variant per arm:

| Arm | Private configuration | Scheduler |
|---|---|---|
| Baseline | Existing v4 | Off |
| Validation | v4 plus validation probes | Off |
| Captured | Same validation binary | On |

Six separate one-observation warm-ups precede ten blocks. Each block contains all
six combinations, with ten observations per invocation: 66 invocations, 606 total
observations, including 600 measured observations and 1,200 measured endpoint
mappings. Starting order is A-baseline, C-baseline, A-validation, C-validation,
A-captured, C-captured. Block `b` rotates this order left by `b % 6`, then reverses
it when `b` is odd. No cache flushing, affinity changes, artificial load or retries
are permitted.

The runner prepares four native configurations using the retained installed-provider
build sequence and four jobs. It records commands, host tools, dependency resolution,
binary hashes and linkage. Builds and workloads run as the desktop user. Scoped
`sudo -A` workers stage A's one-shot layout and C's protected generation layout
under a fresh `/run/holonight-validation-*` root, or operate the recorder; evidence
and diagnostic runtimes are preserved. All workload, staging and recorder commands
are registered before staging or workloads. A single preview-free recorder rehearsal
checks readiness, monotonic clock metadata, export and shutdown before warm-ups.
The existing six scheduler tracepoints, all CPUs, 256 mmap pages per CPU and no
stack sampling are retained. Sessions have 30 seconds including readiness, plus
five seconds for termination. The shared recorder's optional bounds metadata keeps
its B-pilot defaults and behavior unchanged.

Offline accounting replays original v3/v4 records, checks both endpoint pre-decode
boundaries and ownership before deduplicating, and retains original harness timers,
inclusive spans, clipped unions, disjoint work groups, uncovered intervals and
per-observation parent subtraction. Rankings use the deepest active measured work
on each thread; enclosing spans remain separate. Shares use each observation's
validation window. File activity is aggregated within an observation before any
distribution is computed. Captured windows require an unambiguous task lifetime,
matching clock, no capture loss and complete running/runnable/non-runnable coverage.
Raw transitions and source/record citations remain available. Nested scheduler
windows and concurrent threads are non-additive.

Pooled and per-block distributions retain count, minimum, median, nearest-rank p95
and maximum. C's groups sort by median share, p95 share and label, with A alongside.
Selections retain the five slowest validation/pre-decode/harness observations with
cutoff ties, all nearest-median ties and largest-uncovered-gap ties. Selection and
between-arm priority disagreements are explicit. Baseline→validation and
validation→captured harness differences describe probe/recorder effects under this
protocol. No overhead is subtracted and no significance or acceptance threshold is
invented. Running time cannot isolate hashing CPU cost, and non-runnable time
identifies no I/O or blocking cause. A next investigation requires agreement between
internal phase rankings and selected-tail evidence.

### Stopped preparation attempt 01

The [sealed preparation assessment](../../build/preview-validation-20261115-01-prepared/ASSESSMENT.md)
is **blocked before source overlays, builds or workloads**. It retained the fixed
protocol and a successful A/A-fixed reconstruction, then reported `output integrity
drift` while checking the historical v3 preparation package. Exactly **zero**
invocations and observations were launched; all 66 invocations remain unexecuted.
No recorder rehearsal, staging or privileged runtime change occurred.

The [read-only diagnosis](../../build/preview-validation-20261115-01-diagnosis/REPORT.md)
identifies an overly strict new checker, rather than changed sealed source bytes.
That historical preparation seal predates appended execution and reporting evidence.
Its originally sealed files remain unchanged; full-directory equality incorrectly
rejected the appended evidence. The corrected checker verifies every originally
sealed file while retaining strict complete inventories for the frozen source trees
and newer sealed packages. The failed assessment and seal remain unchanged, and
byte-identical snapshots reproduce its recorded preparation-tool and test hashes.

The stop-on-first-failed-gate rule was honored: **no corrected preparation or
experimental retry was executed**. The remaining tooling was implemented and tested
using synthetic files and deterministic recorder fixtures. It remains uncompiled
and unvalidated against native workloads. No validation-sub-operation or A/C
scheduler conclusion, overhead estimate or optimization recommendation is available
from this attempt. C's failed qualification and D's failed pilot remain unchanged.

Verification: 27 new process-launch-free regressions and 107 affected existing
checks passed. They cover literal source replay, expression/exception preservation,
span ownership and nesting, file mappings, per-observation interval arithmetic,
complete scheduler coverage and lifetime errors, quantiles, deterministic rankings,
tied selections, schedule counts/order, stopping before another launch, provenance
and fixture binding, input drift and sealed failures. Existing deterministic
recorder regressions cover readiness failure, timeout, SIGINT shutdown and partial
evidence. The independent verifier imports no new validation reporter; it checked
the failed preparation seal, consumed hashes (using exact historical tool snapshots),
retained provenance, zero observations and 66 unexecuted invocations. Native
build/linkage, full measurement accounting and final experimental replay remain
unexecuted because the first preparation gate failed.

### Native build and stopped recorder rehearsal, attempt 02 (2026-11-15)

The separately authorized fresh attempt passed
[preparation](../../build/preview-validation-20261115-02-prepared/ASSESSMENT.md)
and all four [native builds](../../build/preview-validation-20261115-02-built/ASSESSMENT.md).
Baseline and validation A/C used the retained installed-provider sequence, four
build jobs and host dependencies (Qt 6.12.0, libexif 0.6.26 and libwebp 1.6.0).
Dependency resolution, helper/harness hashes and linkage, runtime payloads and
manifest ordinal mappings passed. All four protected diagnostic runtimes were
staged successfully and remain preserved under
`/run/holonight-validation-preview-validation-20261115-02-execution`.

The [execution assessment](../../build/preview-validation-20261115-02-execution/ASSESSMENT.md)
is **blocked at the preview-free recorder rehearsal**. Readiness acknowledgement
and SIGINT shutdown passed; the recorder was reaped without timeout or forced
termination. Its subsequent root-run `perf report` rejected the desktop-owned
`perf.data` under perf's ownership check. This is an export-reader identity error
in the new runner. Zero warm-up or measured observations were launched, and all
66 scheduled invocations remain unexecuted. Final artifact/runtime integrity,
scope isolation and residual-process checks passed. No retry occurred.

A separate [sealed read-only diagnosis](../../build/preview-validation-20261115-02-diagnosis/REPORT.md)
retains successful desktop-user header and raw export commands against the original
recording, without changing its ownership, permissions or bytes. Offline checks
confirm CLOCK_MONOTONIC, all six tracepoints, complete normalization and no recorded
capture loss. These supplemental checks do not retroactively pass the failed
rehearsal and provide no target validation windows or startup measurements.

The recorder helper now accepts optional export environment/credentials. The A/C
worker keeps recording privileged and drops only the offline readers to the desktop
file owner. Existing B-pilot defaults, capture options, readiness/shutdown logic and
session budgets remain unchanged. A deterministic regression checks that recorder
launch retains its credentials while both readers receive the desktop credentials;
51 focused recorder and validation regressions passed. Whitespace checks passed.
The repaired helper was not used for another rehearsal or workload invocation.

Independent verification, without importing the new validation reporter, checked
all three original seals, consumed hashes, literal source reconstruction, eight
native binary identities and linkage, four ordinal mappings, protected payloads,
pre-registration, original readiness/shutdown evidence, offline clock/export and
zero workload counts. The original execution seal and failure remain unchanged.
Native compilation is now established for the private probe configurations;
accepted balanced runtime spans, 600-observation accounting, A/C scheduler
attribution, probe/recorder effects and an optimization recommendation remain
unavailable. C's qualification and D's pilot conclusions remain unchanged.

### Desktop-only analysis and stopped warm-up accounting, attempt 03 (2026-11-15)

The authorized rerun passed fresh
[preparation](../../build/preview-validation-20261115-03-prepared/ASSESSMENT.md),
all four [native configurations](../../build/preview-validation-20261115-03-built/ASSESSMENT.md),
protected staging and the preview-free recorder rehearsal. Both offline readers
ran with desktop credentials. Scheduler identity extraction and normalization were
moved out of the privileged recorder worker and ran as UID 1000; their retained
output files are desktop-owned. The common build/orchestration/report boundary now
also rejects root callers before creating output. Root remains limited to the
protected staging worker and recorder control. B-pilot defaults and capture budgets
are unchanged.

The [original execution](../../build/preview-validation-20261115-03-execution/ASSESSMENT.md)
passed A-baseline, C-baseline and A-validation warm-ups. The fourth, C-validation,
completed with correct pixels/metadata, original v3/v4 accounting and process
cleanup, but the new validation accounting rejected `unowned validation spans`.
C constructs an initial setup service before observation 1. Its generation/runtime
validation has a known service identity and an unavailable observation identity;
these extra spans were absent from the initial analyzer's test model. The runner
stopped at that accounting gate. Original accepted warm-ups remain three; four
warm-up harness samples exist. **Zero measured observations were launched and all
62 remaining invocations remain unexecuted.** Final input/artifact/runtime integrity,
scope isolation and residual-process checks passed.

The [sealed read-only diagnosis](../../build/preview-validation-20261115-03-diagnosis/REPORT.md)
retains corrected offline accounting for all four existing warm-up observations,
eight endpoint mappings and one separate setup-validation group. No recorder or
workload was repeated. Setup activity retains `observation: null` and binds to the
original v3 `setup_activity` construction and generation/runtime boundaries using
explicit invocation/process/service/thread context and enclosing spans. A measured
service with missing observation identity, missing/ambiguous setup bindings,
foreign processes, exceptional exits or overlap with observation windows remains
an error. No setup activity is assigned to an observation, pooled into distributions
or discarded. Full reports now retain it in `setup-validations.json`, with raw
citations; online per-invocation sidecars support exact replay.

An independent desktop-user verifier, using no sudo and importing no new validation
reporter, checked all original seals and archived tool identities, source
reconstruction, eight binary/linkage identities, four manifest ordinal mappings,
protected payloads, successful rehearsal/clock/export, all original invocation
correctness and cleanup gates, phase arithmetic, every raw validation span and its
ownership, setup v3 citations and all eight endpoint mappings. It confirms complete
separate ownership of the setup spans without manufacturing observation identities.
The original failure and counts remain unchanged; the offline correction does not
resume or complete the stopped experiment.

Verification: 57 focused recorder/validation regressions and 41 affected existing
pre-decode/endpoint/accounting checks passed; whitespace checks passed. New tests
cover the root-action guard, privilege separation of recording versus readers,
desktop-only normalization, preserved loss evidence and explicit setup ownership
with missing/ambiguous/foreign/overlapping cases. Existing broader unchanged
verification is reused. Captured A/C validation windows, the 600-observation
experiment, distributions, overhead effects and an optimization recommendation
remain unavailable. C qualification and D pilot conclusions are unchanged.

## Completed matched validation/scheduler diagnostic, attempt 04 (2026-11-15)

The [sealed decision report](../../build/preview-validation-20261115-04-findings/REPORT.md)
completes the approved experiment: **66 invocations, 600 measured observations,
1,200 measured endpoint mappings and six separately reported warm-ups**. All four
fresh native configurations, installed-provider resolution, binary/linkage checks,
protected staging, recorder rehearsal, original pixel/metadata/lifecycle/cleanup
gates, balanced new spans and captured scheduler target coverage passed. No
workload retries occurred. All 23 recordings and diagnostic runtimes are retained.
The earlier failed attempts remain unchanged.

The operation to investigate next is **combined file reading and SHA-256** through
`QCryptographicHash::addData(&file)`. For C, its median per-observation share of the
validation window is 96.262% without recording and 96.312% with recording. The
respective median durations are 47.908 ms and 47.270 ms, with nearest-rank p95
57.644 ms and 57.259 ms. A's median durations are 48.069 ms and 48.165 ms.
Both arms' pooled rankings and every retained C selection class agree on this
priority. No internal quantiles are subtracted and no overhead is removed.

In captured C observations, the median per-observation running share of this
combined operation is 99.850%; runnable share is 0.150%. No non-runnable or unknown
time is observed in these read/hash windows. A's corresponding running/runnable
medians are 99.946%/0.054%. Running includes kernel work and cannot isolate hashing
CPU cost from copying, memory/page-fault effects or diagnostic logging. These
scheduler states identify no I/O or blocking cause and establish no universal
absence of blocking.

Per-file activity is first summarized within each observation. Each file's
distributions then use 100 observations per variant/arm. C's largest median
contributor in both arms is `usr/lib/libicudata.so.78` (33,112,920 bytes): 15.730 ms
without recording and 15.723 ms with recording. QtCore and QtGui follow, with their
secondary order swapped between arms. Lower operation order also differs:
generation-manifest digest and the nested-runtime residual swap ranks 17/18;
all operation/file order differences are retained in the sealed findings.
Profile the combined loop, including these
payloads, to distinguish hashing, copying, memory effects and logging before
selecting an optimization. No follow-up workload or production optimization was
performed, and these measurements do not predict a gain.

Original harness latency differences remain descriptive. C's pixel medians are
136.363 ms baseline, 138.302 ms validation and 137.004 ms captured; A's are
141.656 ms, 142.635 ms and 141.529 ms. Both endpoint distributions, negative recorder
differences, pooled/per-block count/minimum/median/nearest-rank-p95/maximum,
deterministic rankings and all tied selections remain in the
[full report](../../build/preview-validation-20261115-04-analysis/REPORT.md).
No significance, overhead subtraction, acceptance threshold, qualification rerun or
C/D reassessment is made.

Setup validation remains separate: all 22 invocation-level C setup groups retain
null observation identities and explicit v3 setup bindings. The measured tables
contain only the 600 scheduled measured observations. Builds, workloads, readers,
normalization, reporting and independent verification ran as the desktop user;
scoped sudo was limited to protected staging and live recording.

After collection, offline replay was made to reuse each parsed scheduler timeline,
index task transitions, cache citation file reads and use JSON-compatible task
keys. Exact sealed-sidecar replay passed for captured warm-ups and ten-observation
A/C batches. Four new process-launch-free cache/JSON/citation regressions and 57
focused existing checks passed; valid unchanged broader verification is reused.
These offline changes preserve the gates, source expressions, recordings and
original harness timers. They do not rerun or alter measurements.

The [independent replay](../../build/preview-validation-20261115-04-independent-verification.json)
imports no new validation reporter and verifies all original seals, source
transformations, schedule/counts, observation and setup ownership, phase and
scheduler arithmetic, distributions, rankings, tied selections, effects and
citations. [Supplementary verification](../../build/preview-validation-20261115-04-findings/independent-verification.json)
checks file/state statistics, ordinal mappings, all recording sessions, 132
before/after scope gates, eight native binary identities, package resolution and
protected host payloads. Separate warm-up verification checks both captured
warm-ups. Direct raw-stack replay verifies depths, parent/operation/ordinal fields
and raw/clipped boundaries for all 158,358 fine spans across the 66 invocations.
Whitespace checks passed. The completed diagnostic supports a specific
next investigation inside validation; C's failed qualification and D's failed
pilot remain unchanged.

## Focused C userspace CPU profile (2026-11-15)

This private attribution experiment reuses attempt 04's unchanged validation/C
harness, helper, runtime manifest and `3200x2400.png`. It makes no production
change, qualification rerun, validation-policy change or buffer-tuning experiment.
The tools are [preparation](../../scripts/prepare-preview-cpu-profile.py),
[desktop runner](../../scripts/run-preview-cpu-profile.py),
[offline reporter](../../scripts/report-preview-cpu-profile.py) and
[independent replay](../../scripts/verify-preview-cpu-profile.py).

The fixed schedule has a separate one-observation warm-up per arm, unprofiled
first, followed by four blocks of five observations per arm. Blocks 0/2 run
unprofiled first; blocks 1/3 run profiled first. This permits exactly ten harness
invocations, 40 measured observations and two warm-ups. No replenishment, trimming
or retries are permitted. Both arms use the same desktop-owned gate, which reports
readiness and blocks before exec. In the profiled arm perf attaches to that PID,
acknowledges enablement and only then permits exec without changing PID.

The task-scoped recorder uses `cpu-clock:u`, strict 999 Hz frequency, inherited
worker/descendant sampling, DWARF call chains with a 16 KiB stack snapshot,
`CLOCK_MONOTONIC` and 256 mmap pages. There is no all-CPU recording, scheduler
tracepoint or privileged-recorder fallback. Readiness consumes the 30-second
session budget; termination has five seconds. A single synthetic rehearsal must
verify attachment, exec identity, thread/descendant inheritance, monotonic sample
boundaries, stack export and shutdown before any harness invocation. The first
execution, integrity, cleanup, accounting or capture-loss failure stops the run.
Scoped sudo is limited to the existing conservative installer staging one fresh
protected C runtime. Prior markers, generations and runtimes remain retained.

Preparation checks the sealed native artifacts, source provenance, prior linkage
and provider-resolution results, fixture, manifest ordinals and payload hashes.
No rebuild is needed. Current payload/host ELF hashes and build IDs are recorded;
historical disassembly supplies no symbol identity. QtCore, OpenSSL and libc debug
files must match those build IDs and contain debug information, lines and symbol
tables. Downloads go into a fresh ignored cache without installing packages.
Automatic downloads are disabled during recording and offline export. A private
symbol mirror uses ordinary files compatible with the conservative evidence
sealer. The sealed cache and sized symbol ranges keep unknown addresses explicit
instead of attributing them to a nearby exported symbol.

Offline tooling joins samples to half-open read/hash spans using recording-local
PID/TID and monotonic boundaries. Original validation span ownership and setup
bindings are reused: setup has unavailable observation identities and is reported
separately. Exclusive self categories are hashing/dispatch, Qt I/O/buffering,
userspace copying, demonstrated probe logging and other/unresolved. A generic
write or formatting frame alone does not demonstrate probe logging. Inclusive
stack presence is separate and non-additive. Raw addresses, periods, unresolved
frames and depth-limited stacks are retained. A depth below the exporter limit
does not prove that the 16 KiB snapshot captured the complete stack.

Shares are computed within each observation before pooled/per-block
count/minimum/median/nearest-rank-p95/maximum distributions. Count and period
weighting remain separate; zero-sample windows are unavailable. File views retain
frozen manifest ordinals, including ICU data and QtCore/QtGui. Sparse per-file
sampling limits interpretation. Validation and both original harness endpoints
retain p95-cutoff tails including all ties. Unprofiled-to-profiled harness
differences are instrumentation effects: no overhead subtraction, significance
or gain is inferred. Any next investigation needs agreement across blocks and
tails, considering whether unresolved samples could reverse the priority.
Conclusions concern sampled userspace execution; kernel cost and an exact elapsed
time decomposition remain unresolved.

### Stopped rehearsal and retained evidence

The [first preparation](../../build/preview-cpu-profile-20261115-01-prepared/assessment.json)
sealed a sandbox network failure without launching workloads. With network access,
the [second preparation](../../build/preview-cpu-profile-20261115-02-prepared/assessment.json)
passed: all three downloaded debug files match the frozen payload build IDs.
The [input identities](../../build/preview-cpu-profile-20261115-02-prepared/inputs.json)
record harness SHA-256
`f1c6c6927396a2316216663166808ae593b306c31047abaa0d3104b246021143`
and build ID `7d06706cf373a0218d85c7fb5313616c48bac113`.

One fresh runtime was staged through the frozen installer. During the single
synthetic recorder rehearsal, desktop-owned task-attached perf failed to open
`cpu-clock:u`; its [stderr](../../build/preview-cpu-profile-20261115-01-execution/rehearsal-recording/recorder.stderr)
reports restricted performance-monitoring access with `perf_event_paranoid=2`.
This is an observed attachment failure despite the earlier permission check, not
evidence about hashing, copying, buffering or logging. No permission settings were
changed and no privileged recording or rehearsal retry was attempted.

The [stopped assessment](../../build/preview-cpu-profile-20261115-01-execution/assessment.json)
retains **zero harness invocations, zero measured observations, zero warm-ups and
all ten invocations unexecuted**. Recorder acknowledgement was empty; the gate was
never released, so the synthetic workload also did not execute. Both recorder and
gate were reaped; final scope isolation and residual-process checks passed. The
protected runtime is retained. No samples or next userspace target are available.

Initial evidence sealing exposed a tooling error: the symbol mirror contained
symlinks rejected by the existing sealer. After the run stopped, those links were
materialized as identical bytes, with their original destinations recorded in
[the repair manifest](../../build/preview-cpu-profile-20261115-01-execution/symfs-link-repair.json).
The original launch tool snapshots match their recorded hashes. The runner now
copies mirror files directly; this offline repair did not retry execution or
alter the recorder failure. The stopped execution and blocked offline analysis
are sealed separately.

[Independent replay](../../build/preview-cpu-profile-20261115-01-independent.json)
imports no new reporter or runner and verifies seals, consumed payload/fixture
identities, manifest mapping, symbol identities, original launch tool snapshots,
fixed command order, recorder settings, disabled downloads, empty acknowledgement,
unreleased gate, reaping and zero-launch accounting. The analysis correctly
refuses to report a completed experiment. Nineteen process-launch-free
[focused regressions](../../tests/test_preview_cpu_profile.py) cover schedule
counts/order, task scope, readiness and shutdown fixtures with a shared
termination deadline, half-open boundaries,
separate setup ownership, exclusive stack categories, unknown/sized/truncated
frames, count/period weighting, zero samples, JSON report replay, cutoff ties,
missing/mismatched symbols, sealed failures and tamper detection. Successful live
attachment/export, sample classification and complete-run independent replay
remain unverified because the required rehearsal failed.

### Synthetic CPU-recorder diagnosis (2026-11-15)

The approved follow-up diagnosed recording with synthetic Python processes only.
The stopped experiment, original tool snapshots, seals, ordinary-file symbol
mirror and protected `/run` runtime were checked without modification. All ten
original harness invocations remain unexecuted. A new profiling experiment still
requires a separate plan.

`run-preview-cpu-profile.py diagnose --output <fresh-ignored-build-directory>`
registers four comparisons before recording: perf-launched and task-attached,
each with minimal `cpu-clock:u` recording and with the complete original options.
It uses `perf record -vv` under installed `strace`, restricted to event opening,
mapping and control syscalls. Each case has a 30-second budget and one shared
five-second cleanup deadline. It records desktop credentials, capabilities,
seccomp, namespaces, kernel/tool identities, security settings and resource
limits. The earlier successful permission check could not be located as a
reproducible command plus context, so remains explicitly unverified.

The [comparison evidence](../../build/preview-cpu-diagnostic-20261115-02/assessment.json)
shows:

| Launch | Minimal | Original complete options |
| --- | --- | --- |
| Perf-launched synthetic | passed | event opening denied, `EACCES` |
| Task-attached gated synthetic | passed | event opening denied, `EACCES`; gate not released |

The full event attributes request `PERF_SAMPLE_CALLCHAIN` with
`exclude_kernel=1` but without `exclude_callchain_kernel=1`. DWARF adds user
register/stack capture and sets `exclude_callchain_user=1`; that does not exclude
kernel callchains. The kernel's
[callchain access check](https://kernel.googlesource.com/pub/scm/linux/security/vulns/+/247fced16dfe16f1ac614ea092d62c8bf5a62c8f)
explains the observed `EACCES` at paranoid level 2. This is an unintended recorder
request for kernel callchains, rather than evidence that all unprivileged task
sampling is prohibited. The focused repair adds `--user-callchains`, whose
[documented effect](https://android.googlesource.com/kernel/common/+/c645c11a2dba116bad3ee43e08e330db8f03ede6/tools/perf/Documentation/perf-record.txt)
is to exclude kernel callchains. Frequency, DWARF stack size, monotonic clock,
256 mmap pages, timestamps, periods, inheritance and attach-before-release remain
unchanged. Diagnostic comparisons continue to reproduce the original options.

The [single untraced confirmation](../../build/preview-cpu-confirmation-20261115-01/assessment.json)
then failed later with `Permission error mapping pages` at the required 256-page
setting. There was no acknowledgement or gate release; both groups were reaped,
and descriptors closed. No retry was performed. This run therefore did not
validate exec identity, inherited samples, stack export or offline sample replay;
those acceptance checks remain unavailable. The fresh ordinary-file symbol mirror
was independently verified unchanged.

The desktop context was UID/GID 1000, no effective or permitted capabilities,
`Seccomp: 0`, kernel `7.3.4-arch1-1`, perf `7.3.4-1`, `perf_event_paranoid=2`,
`perf_event_mlock_kb=516`, and soft/hard `RLIMIT_MEMLOCK=8388608` bytes. With 32
CPUs, 256 data pages plus a metadata page per CPU at 4096 bytes need 33,685,504
bytes. The recorded perf allowance plus memlock limit provides at most
25,296,896 bytes before other consumption. This budget calculation is consistent
with the mapping error; the confirmation was intentionally untraced, so its
mapping syscall errno was not captured. The
[kernel resource-control documentation](https://docs.kernel.org/admin-guide/perf-security.html#memory-allocation)
explains the combined limits. No policy, limits, capabilities or recorder
privilege were changed, and no smaller buffer or alternative attachment mode was
substituted. Recording remains blocked under the approved settings.

The runner now retains the first exception, errno where supplied, complete
recorder stderr, gate/recorder identities, acknowledgement bytes and release
state. Cleanup attempts both groups independently and closes every descriptor
with separate outcomes, even after another cleanup fails. Forced cleanup stops
the diagnostic sequence. `confirm` is a separate synthetic-only entrypoint;
neither diagnostic entrypoint calls staging or the harness scheduler.
`verify-preview-cpu-profile.py --diagnostic <directory> --output <fresh-json>` and
`--confirmation <directory> --output <fresh-json>` independently check seals,
comparison ordering/options, syscall citations, cleanup and preserved inputs,
without importing the runner or reporter. Verification accepts a sealed blocked
confirmation as an accurately reported failure, not as recording success.

A preliminary diagnostic command incorrectly placed verbosity before `record`,
which printed perf build features and exited without opening an event or launching
a synthetic process. That [sealed preliminary attempt](../../build/preview-cpu-diagnostic-20261115-01/assessment.json)
was preserved; the corrected four-case sequence ran once in its own directory.
Process-launch-free CPU regressions and affected scheduler recorder tests passed.
The [sealed diagnostic report](../../build/preview-cpu-diagnostic-20261115-report/report.md)
contains comparison and confirmation bindings, final tooling snapshots, focused
verification results and the unresolved restriction. Native build/linkage results
were reused; no ecosystem rebuild was performed.


### Offline frozen-symbol recovery

`run-preview-cpu-profile.py replay-confirmation --confirmation <sealed-confirmation>
--output <fresh-build-directory>` reuses the original recording in place. It never
records, stages, builds or launches a workload. The replay preserves raw MMAP2
records and completes an ordinary-file copy of the frozen symbol mirror using
only local ELF files matching recorded build IDs. Missing identities, changed
sources and destination collisions block recovery. Readers disable debuginfod
and build-ID cache writes. Future confirmations complete dependencies after
recording and distinguish recording, mirror, export and rehearsal failures;
workload errors remain separate.

`verify-preview-cpu-profile.py --replay <sealed-replay> --output <fresh-json>`
independently checks source bindings, mappings, ELF identities, mirror hashes,
reader outputs, original capture/cleanup and all three marker-bounded stacks.
Verification output stays outside the replay seal; failures produce structured
JSON and a nonzero exit. Legacy post-recording failures must be reproduced from
sealed evidence. A successful recovery has its own status and never changes the
original blocked confirmation or authorizes any of the ten harness invocations.

### Fixed live CPU attempt after accepted recovery

The [second offline recovery](../../build/preview-cpu-replay-20261115-02/assessment.json)
and its [final independent verification](../../build/preview-cpu-replay-20261115-02-final-independent.json)
accepted the recovered recording. The original blocked confirmation remains
historical: the recovery corrected incomplete symbol-mirror handling and does
not retroactively turn the original export failure into recording failure.

The runner now provides read-only `preflight-execution --package <prepared-package>
--output <prospective-execution-directory>`. Execution repeats admission before
reserving the destination. It binds desktop host namespaces, accepted recovery,
consumed historical seals, frozen artifacts/debug identities, installer identities,
tool snapshots and the fixed commands before staging. Every recording must
complete its ordinary-file mirror before export; evidence retains raw mappings,
ELF build IDs, hashed non-ELF exclusions and source hashes. Existing mirror bytes
remain intact and the final inventory is sealed. Failure stages and a readable
assessment survive a stopped attempt. Independent replay checks host/runtime
integrity, recorded commands, acknowledgement/release ordering, rehearsal stacks,
mapping classifications, source identities and reproduced reader output.

The [fresh execution](../../build/preview-cpu-profile-20261115-02-execution/assessment.json)
passed host preflight and staged one fresh protected C runtime. Its single
rehearsal passed attachment, acknowledgement, unchanged exec PID, cleanup and
multiframe main-thread, worker-thread and descendant sampling. The unprofiled
one-observation warm-up passed. The profiled warm-up finished its workload and
recorder cleanup, but mapping completion stopped on the unavailable recorded
path `/usr/libexec/holonight-images-helper`. No mirror/export retry or replacement
attempt was made. The raw mapping evidence and recording remain sealed; no
historical evidence or protected runtime was removed.

Two harness invocations launched, one warm-up was accepted, zero measured
observations were accepted, and eight invocations remain unexecuted. The
[analysis](../../build/preview-cpu-profile-20261115-02-analysis/assessment.json)
therefore reports blocked. [Independent execution verification](../../build/preview-cpu-profile-20261115-02-independent.json)
passed for the accurately stopped result; [final verification](../../build/preview-cpu-profile-20261115-02-final-verification.json)
also covers the blocked analysis. Verification success is not experiment
completion. The required ten successful invocations and 40 measured observations
were not achieved.

There are no measured block distributions, p95 tails, exclusive self-category
shares or separate inclusive-presence results to prioritize userspace activity.
The attribution evidence is inconclusive; no next performance investigation,
gain or significance claim follows. Kernel cost and exact elapsed-time
decomposition remain unresolved. Focused CPU regressions use forbidden real
process launches and cover schedule accounting, mirror-before-export ordering,
report arithmetic, namespace/destination rejection, identities and tampering.
Unchanged scheduler and native results were reused without rebuilding.

### Helper namespace correction and successful fixed rerun

The user authorized correcting helper availability and rerunning the experiment.
The helper had executed successfully: its path inside the workload filesystem
namespace, `/usr/libexec/holonight-images-helper`, was unavailable to the host
symbol reader. The private symbol mirror now includes an ordinary-file copy at
that namespace path, taken from the prepared native helper with matching SHA-256
and build ID. Recorded mapping identities are still required before export.
No host installation, workload, payload, recorder setting or production behavior
changed. Offline checking of the previous warm-up's raw mappings resolved all
224 ELF paths with matching identities before the fresh attempt. The runner also
binds the stopped attempt's execution/analysis seals and inventories all retained
CPU experiment runtimes during preflight and subsequent integrity checks.

The [third execution](../../build/preview-cpu-profile-20261115-03-execution/assessment.json)
completed one rehearsal and all ten harness invocations, accepting two warm-ups
and 40 measured observations. The six recordings retain individual mapping and
source-hash evidence, and the shared ordinary-file mirror has a sealed final
inventory. [Independent execution verification](../../build/preview-cpu-profile-20261115-03-independent.json)
and [final execution/report verification](../../build/preview-cpu-profile-20261115-03-final-verification.json)
passed. Historical seals and old/new protected runtime inventories remained
unchanged. Earlier blocked attempts remain sealed and separate.

The [report](../../build/preview-cpu-profile-20261115-03-analysis/REPORT.md)
contains the block timing distributions; its `observations.json`, `summary.json`,
`tails.json` and `setup.json` retain observation, frozen-file-ordinal, tail and
separate setup views. Within measured read/hash spans, 792 sampled userspace
self observations break down as follows. All selected samples have the same
recorded period, so count and period shares agree.

| Exclusive self category | Samples | Count and period share |
|---|---:|---:|
| Hashing/dispatch | 777 | 98.11% |
| Qt I/O/buffering | 5 | 0.63% |
| Userspace copying | 5 | 0.63% |
| Demonstrated probe logging | 0 | 0% |
| Other/unresolved | 5 | 0.63% |

Hashing/dispatch shares in blocks 0–3 are 97.40%, 97.46%, 98.62% and 98.92%.
The two validation p95-tail observations (invocation 7, observations 2 and 4,
including all cutoff ties) contain 100% and 95.74% hashing self samples. Pixel
and metadata tails select invocation 3 observation 2 and invocation 4 observation
3, with 97.73% and 97.37% hashing shares. Across the measured spans there are
3,167 unresolved frames among 18,188 frames, including three unresolved leaves,
and zero truncated stacks. Unresolved caller frames are not additional self
samples; even assigning every other/unresolved self sample to one competitor
cannot reverse the priority.

Inclusive stack presence is separate and non-additive: `verifyRuntime` appears
in 791 measured samples, `SHA256_Update_thunk` in 773, and
`sha256_block_data_order_shaext` in 769. These counts must not be added to the
exclusive self categories. The largest frozen-file sample counts are ordinal 31
(`libicudata.so.78`, 275), ordinal 7 (`libQt6Gui.so.6`, 96), ordinal 5
(`libQt6Core.so.6`, 95) and ordinal 18 (`libcrypto.so.4`, 58). Sparse small-file
windows remain unsuitable for ranking individual files. Separate setup read/hash
spans contain 241 samples: 231 hashing, four Qt I/O, one copying, one demonstrated
probe logging and four other/unresolved; 965 frames are unresolved and none of
the setup stacks are truncated.

The next investigation should examine SHA-256 execution/dispatch and the volume
of repeated runtime verification within the existing integrity contract. Blocks,
validation tails and endpoint tails agree on that userspace priority. This is an
investigation recommendation, not authorization to weaken validation or alter
production behavior. Sampling covers read/hash spans rather than an exact
elapsed-time decomposition; kernel cost remains unresolved. No performance gain
or statistical significance is claimed. All 46 focused CPU tests and whitespace
checks passed; unchanged native and scheduler results were reused without a
rebuild or symbol download.

## Offline runtime verification work audit, 2026-11-15

The [sealed work audit](../../build/preview-verification-work-20261115-04/REPORT.md)
reconciles the successful CPU `-03` execution's raw validation spans with its
saved observations and setup records. The new
`scripts/audit-preview-verification-work.py` consumes execution/report paths and
writes a fresh ignored build directory; `scripts/verify-preview-verification-work.py`
independently replays raw spans and manifest accounting without importing the
audit or its reporter. The [independent result](../../build/preview-verification-work-20261115-04-independent.json)
binds the audit seal. Consumed seals, manifest payloads and frozen source hashes
are checked before analysis and again before sealing output.

Each runtime pass validates 60 frozen manifest ordinals totaling **87,215,960
bytes**. Forty measured passes infer **3,488,638,400 bytes**; two warm-ups infer
174,431,920 bytes and ten setup passes infer 872,159,600 bytes, retained as separate
populations. The enclosing generation validation contributes no second payload
pass. Zero-byte files contribute zero bytes. These byte counts follow successful
full-file validation and are not direct read counters.

Summed measured read/hash elapsed time is 1,925,287,578 ns, giving pooled combined
reading/hash throughput of approximately **1.812 GB/s** (decimal). Per-arm pooled
rates are 1.814 GB/s unprofiled and 1.810 GB/s profiled. These rates use summed bytes
and durations, may include scheduling delays, and do not isolate crypto CPU
throughput. Per-validation median validation/read-hash/residual times are
49.919/48.065/1.785 ms; nearest-rank p95 values are 61.231/59.442/2.530 ms.
Quantiles describe their own populations and are not additive. JSON outputs
retain per-file, per-block, per-arm and pooled distributions, raw citations and
the existing validation/pixel/metadata p95-tail membership including ties. CPU
sample attribution remains separate from elapsed throughput.

All 52 observed validations belong to distinct invocation/PID/service lifetimes:
40 observation constructions, two warm-up constructions and ten setup
constructions. The frozen service queues session-pool construction on its worker;
the pool constructs `RuntimeOwner`, whose constructor calls `refresh()`. Its
`generation_validation` probe encloses the observed validation root. The service
constructor body's end therefore does not end asynchronous owner construction.
Matching lifecycle identity and frozen call paths support these classifications;
timestamp proximity and reused object addresses do not establish ownership.

The source audit retains hashes and line excerpts for owner construction/refresh,
pool construction/refresh, service construction/refresh, fallback launch validation
and helper verification. Explicit service/pool refresh entrypoints have no distinct
refresh-call probe in this frozen version. Additional unexplained roots must block
classification rather than being called redundant. Helper verification paths are
not all instrumented: absence of a trace cannot prove their absence. Matching
payload content across service lifetimes does not prove unchanged generation
identity. No repeated pass within one unchanged owner/generation lifetime is
established.

Select exactly one follow-up: a **bounded native Qt-versus-installed-backend
SHA-256 throughput diagnostic** using the frozen payload. This audit alone cannot
establish unexpectedly slow cryptographic throughput. The proposal remains a
subsequent step; no diagnostic, workload, recording, build, staging operation,
symbol download or production change was performed for this audit. Mutable-runtime
full validation, generation identity, ownership checks, leases and installer
protections remain intact. No gain or significance claim is made.

Verification covers successful and blocked offline paths, nested generation/runtime
spans, separate service lifetimes, setup/warm-up separation, zero-byte files,
missing/repeated ordinals, duplicate/missing/exceptional spans, nonpositive durations,
p95 ties, input/source/manifest/seal tampering, output collisions and independently
detected accounting tampering after resealing. A second explicit refresh without
lifecycle identity is rejected rather than inferred. Seven focused tests, 37
validation/parser regressions and 46 CPU regressions passed, with process-launch
entrypoints forbidden in the new tests. Existing native and scheduler results were
reused. Whitespace checks passed.

## Native SHA-256 diagnostic implementation and blocked run, 2026-11-15

The standalone [native harness](../../tooling/preview-hash-throughput/README.md),
`scripts/run-preview-hash-throughput.py` and independent stdlib-only
`scripts/verify-preview-hash-throughput.py` implement the approved five-case,
64 KiB SHA-256 comparison. Preparation checks the sealed audit, successful
independent-verification binding, frozen manifest and host Qt/libcrypto/libc
hashes/build IDs. The runner preserves source/tool snapshots, Release build
commands/flags, binary/linkage identity, host/CPU identity, raw streams, the full
rotated schedule and process cleanup records. File opening/loading, digest checks
and output remain outside the primary update timer; initialization and finalization
have separate durations. The checker recomputes raw counts, bytes, distributions
and block-matched ratios, rejecting missing/duplicate rows and accounting changes
even after resealing. No production code or older validator/candidate experiment
was changed.

The [sealed attempt](../../build/preview-hash-throughput-20261115-01/assessment.json)
passed provenance, host Release configuration/build and native digest correctness,
but exited before emitting any identity or sweep rows: `actual EVP provider
unavailable`. The installed OpenSSL did not expose a provider through the legacy
EVP descriptor used by the initial provider probe. The process returned 1 in
approximately 58 ms; cleanup succeeded. All **130 scheduled sweeps remain
unexecuted**, including all five warm-ups and 125 measured sweeps. There is no
throughput result, block-direction comparison, optimization selection, performance
qualification or whole-preview gain claim. The investigation is **inconclusive**.
Historical audit throughput remains contextual because its timer/probe conditions
differ. Crypto dispatch, streaming overhead, Qt device behavior and file-access
costs remain unresolved.

The implementation now fetches SHA-256 once outside per-file timers, uses that
implementation for every EVP context and records its provider. Native correctness
also checks that initialized contexts retain the fetched provider, covering the
provider-reporting gap missed by the initial test. The corrected harness was
rebuilt against host dependencies and passed its correctness test; it has not run
the frozen experiment. The failed attempt's sealed source snapshots and binary
remain unchanged. No retry was launched because the approved protocol explicitly
prohibits retries. A fresh measurement requires authorization.

[Independent partial-evidence verification](../../build/preview-hash-throughput-20261115-01-independent.json)
checks the seal, provenance/payload/dependency identities, retained tool/source
snapshots, native binary identity, successful preparation/correctness records,
empty raw stdout, complete unexecuted schedule and failed-process cleanup. It
retains blocked experiment status and prohibits performance interpretation.
Twelve focused Python regressions and native correctness passed after the fix;
coverage includes schedule rotation, warm-up exclusion, zero bytes, pooled-rate
arithmetic, nearest-rank p95 ties, malformed/duplicate/missing output, wrong
digests, nonpositive durations, provenance drift, destination collisions,
termination/kill/reap cleanup and accounting tampering after resealing. Existing
native, scheduler and CPU-profile results were reused. Whitespace checks passed.
No staging, preview/helper launch, container build, symbol download, profiler
recording, package installation, deployment or publication occurred. Runtime
validation, generation identity, ownership checks, leases and installer
protections remain unchanged.

## Authorized native SHA-256 diagnostic completion, 2026-11-15

After explicit authorization to launch a fresh attempt with the tested provider
fix, the [sealed native run](../../build/preview-hash-throughput-20261115-02/REPORT.md)
completed the fixed schedule without retries or adaptive changes. Its single
persistent process returned 0 in 5.011 seconds and cleanup succeeded. All 125
measured sweeps (25 per case) reconcile **7,500 per-file rows** and
**10,901,995,000 logical bytes**. Five excluded warm-ups retain 300 separate rows
and 436,079,800 logical bytes. No scheduled sweep remains unexecuted. The earlier
blocked attempt remains sealed and contributes no performance observations.

Pooled primary throughput divides summed logical bytes by summed update/read-hash
durations; initialization, finalization, opening/loading, digest checks and output
are excluded from that primary comparison:

| Case | MiB/s |
|---|---:|
| Qt device | 2063.522 |
| Qt file streaming | 2102.771 |
| EVP file streaming | 2098.979 |
| Qt memory streaming | 2410.330 |
| EVP memory streaming | 2424.506 |

Block-matched throughput ratios, in block order 0–4, are:

| Numerator / denominator | Block 0 | Block 1 | Block 2 | Block 3 | Block 4 | Direction agrees |
|---|---:|---:|---:|---:|---:|---|
| Qt device / Qt file | 0.97702 | 0.98891 | 0.97588 | 0.98051 | 0.98439 | Yes, below 1 |
| Qt file / EVP file | 1.01172 | 1.00189 | 0.99453 | 1.00831 | 0.99270 | No |
| Qt memory / EVP memory | 0.99652 | 0.98788 | 1.00975 | 0.98638 | 0.99031 | No |

The evidence supports one investigation recommendation: inspect Qt's device
buffering/read path, since Qt device throughput was lower than Qt file streaming
in every block. This is source investigation, not an optimization selection or a
causal attribution. Qt/EVP streaming directions do not agree across blocks.
File-access costs, device buffering, streaming-call overhead, scheduling and
backend dispatch remain unresolved. The recorded EVP provider is `default`;
actual mappings include `/usr/lib/libQt6Core.so.6.12.0`,
`/usr/lib/libcrypto.so.4` and `/usr/lib/libc.so.6`, matching the frozen identities.
These observations do not establish Qt's provider or hardware dispatch. The
historical audit's approximately 1.812 GB/s combined read/hash rate remains
contextual because its timer/probe conditions differ; it is not a paired arm.
No slow-crypto threshold, significance claim, performance qualification or
whole-preview gain claim is introduced.

[Independent verification](../../build/preview-hash-throughput-20261115-02-independent.json)
replays all raw rows against the frozen manifest and recomputes counts, bytes,
separate warm-up/per-block/pooled distributions and all 15 matched ratios. It
checks the complete schedule, process bounds/cleanup, Release compile flags,
consumed audit/provenance seals, payload hashes, native binary identity,
source/tool identities and mapped dependency identities. The evidence includes
[raw output](../../build/preview-hash-throughput-20261115-02/native.stdout),
[distributions and ratios](../../build/preview-hash-throughput-20261115-02/summary.json),
[preregistration](../../build/preview-hash-throughput-20261115-02/preregistration.json)
and [completion assessment](../../build/preview-hash-throughput-20261115-02/assessment.json).
The 12 focused Python regressions and corrected native correctness result from
the preceding implementation were reused; the runner also passed its native
correctness gate before measurement. No concurrent test/build workload was
launched during measurement. Only this initiative note changed for the authorized
run; generated evidence remains under ignored `build/`. Whitespace checks passed.
Production validation, generation identity, ownership checks, leases and installer
protections remain unchanged. No deployment or publication occurred.

### Qt device-path source and binary investigation (2026-11-16)

The [offline audit](../../build/preview-hash-device-path-20261116-06/REPORT.md)
reuses completed run `preview-hash-throughput-20261115-02` and its passing
independent-verification binding. Both historical measurement attempts remain
intact. No new benchmark, build, recording, symbol download or production change
was performed; existing native, scheduler and CPU-profile results are reused.

Recomputing primary `update_ns` from every raw row gives the following mean
full-payload sweep durations. Each arm has five sweeps per block over all 60
ordinals and 87,215,960 logical bytes. Differences are **device minus streaming**;
adjacent sweeps are not treated as individually paired observations.

| Block | Qt device ms | Qt 64 KiB streaming ms | Signed difference ms | Existing throughput ratio |
| --- | ---: | ---: | ---: | ---: |
| 0 | 40.308347 | 39.381915 | +0.926432 | 0.97701638 |
| 1 | 40.273175 | 39.826353 | +0.446822 | 0.98890523 |
| 2 | 40.514648 | 39.537543 | +0.977105 | 0.97588268 |
| 3 | 40.078402 | 39.297171 | +0.781231 | 0.98050742 |
| 4 | 40.363407 | 39.733262 | +0.630145 | 0.98438820 |

The equal-block mean difference is **+0.752347 ms** per full-payload sweep.
[Per-file accounting](../../build/preview-hash-device-path-20261116-06/accounting.json)
retains every ordinal and negative contribution; this payload has no zero-byte
files, and fixtures cover their accounting. Each
file contributes its device block mean minus its streaming block mean. Integer
five-sweep differences sum exactly to the full-payload difference before division
by 5,000,000 to obtain mean milliseconds. These are descriptive elapsed-time
observations, not production savings estimates or significance claims.

The [identity record](../../build/preview-hash-device-path-20261116-06/identity.json)
binds installed `libQt6Core.so.6.12.0` to the member extracted from cached
`qt6-base 6.12.0-5`: SHA-256
`5205d073601b17d36c2e988378157747870122fef75b81d3ef5e38e05ca26f77`,
build ID `a6c99e3c0418a2ae0f6147f6bfe9c87fa338ade2`. The retained debug file
matches that build ID and its historically sealed hash. Arch packaging revision
`b289afcf8a3c03b5215bfb9ce3139f37536b6051` has the exact `.BUILDINFO` recipe
SHA-256 `e39eef05adc04cdec70ff5f32057c6f8bda8bcfaff721c8a2eb32cd809bb0d8c`.

**Source-level limitation:** the primary Qt repository's retrieved `v6.12.0`
commit is `025bdad181de241e81bf853c8a2d7bf3d19261a9`, but its Git tar archive
SHA-256 `f24f106cee5f49a1e0778ec84301467640f6fdbbbcdf61e77623c119ab966208`
differs from recipe checksum
`d97ef157dc50bdf0425337e9adede8135ab508a4ab2f1abae7e9cfc42c5f86db`.
The archive, recipe, two checksum-validated packaging patches, four cherry-pick
diffs, revision identifiers and primary retrieval URLs are retained in
[source provenance](../../build/preview-hash-device-path-20261116-06/source-provenance.json).
Packaging scripts were not executed and no package was installed. Candidate Qt
sources therefore do not support exact-build source conclusions. The mechanism
findings below use independently bound binary evidence and frozen harness source.

[SHA-256 and inclusive line citations](../../build/preview-hash-device-path-20261116-06/citations.json)
cover the frozen harness and relevant disassembly. Public
`QCryptographicHash::addData(QIODevice*)` jumps to the private routine at
`0x30dce0`, identified by matching debug symbols. At `0x30dd2b` it passes
`0x400` (1,024) bytes to `QIODevice::read`; `0x30dd3e` loops on positive read
results and the body calls the hash-update routine. By comparison, frozen harness
`main.cpp` uses a 65,536-byte buffer, hashes positive chunks, rejects negative
reads and unexpected zero reads, and stops on zero. The device arm additionally
checks `file.error()` and `atEnd()` and obtains `pos()` inside the primary timer;
the streaming arm maintains its byte offset. File opening and digest finalization
are outside this timer.

Compiled `QIODevicePrivate` construction stores `0x4000` (16,384) as its default
buffer chunk; its read routine has buffering and direct-read branches.
`QRingBuffer::read` contains a `memcpy` call. `QFileDevice::readData` delegates to
the file engine with error-handling branches; the Unix `QFSFileEngine::read`
contains `read`/`fread` calls and retry/error branches. Thus the binary supports
smaller device API requests and additional buffered-copy machinery. Assuming
ordinary full reads, 1 KiB requests require more read/hash-update API iterations
than 64 KiB requests. This conditional expectation does not establish actual
syscall counts, selected branches, cache behavior, provider selection, hardware
dispatch or which mechanism accounts for the observed elapsed-time difference.

The investigation recommendation is to resolve the source archive checksum
mismatch against the package builder's retained VCS input before attributing
costs or selecting an optimization. The stdlib-only
`verify-preview-hash-device-path.py` independently checks evidence bindings,
package/debug identities, provenance, citations, disassembly and raw block/file
arithmetic without importing the auditor. Its
[passing verification](../../build/preview-hash-device-path-20261116-06-independent.json)
binds the final audit seal. Focused fixtures cover signed reconciliation,
zero-byte files, missing/duplicate ordinals, identity and citation mismatches,
destination collisions, sealed partial failures and accounting tampering after
resealing. Generated evidence remains under ignored `build/`.

### Correction: makepkg Git archive policy (2026-11-16)

The earlier source archive mismatch omitted makepkg's Git attribute sanitization.
The [corrected audit](../../build/preview-hash-device-path-20261116-10/REPORT.md)
binds the previous sealed audit and passing verification, copies its retained Git
repositories, and reads the cached `pacman 7.1.0.r9.g54d9411-4` package matching
Qt's `.BUILDINFO`. Retained package metadata and the makepkg Git helper establish
its configuration isolation and `* -export-subst -export-ignore` override; the
package contains no `etc/makepkg.d/gitconfig`. No packaging scripts were executed.

Under explicit archive policy `makepkg-git-v1`, the Qt archive SHA-256 is
`d97ef157dc50bdf0425337e9adede8135ab508a4ab2f1abae7e9cfc42c5f86db`, exactly
the unchanged recipe checksum. This resolves the archive mismatch only.
Reconstruction with zero fuzz fails in the first packaging patch,
`qt6-base-cflags.patch`: hunk 1 for `mkspecs/common/gcc-base.conf` fails at line 40.
The application output and partial reconstruction are retained. The second patch
and four cherry-picks cannot establish exact prepared sources after this failure;
complete exact-source tracing and its source citations remain gated. The earlier
binary findings remain supported by the matched binary evidence.

The [independent verification](../../build/preview-hash-device-path-20261116-10-independent.json)
reproduces archive policy and patch failure, validates partial sources and retains
all five blocks and 60 ordinals of unchanged signed accounting. The historical
audit also passes the updated checker using ordinary Git attributes. Thirteen
focused tests cover existing accounting/identity protections plus export attributes,
configuration isolation, unchanged source inputs, policy/attribute/member tampering,
prior binding and clean/failed patch applications with additions/deletions.
Historical evidence and conclusions remain intact. No benchmarks, builds,
recordings, downloads, installation, production changes or optimization selection
were performed; existing native, scheduler and CPU-profile results are reused.

### Recipe-faithful preparation and exact retained source trace (2026-11-16)

The [fresh audit](../../build/preview-hash-device-path-20261116-15/REPORT.md)
binds audit `preview-hash-device-path-20261116-10` and its passing verification.
Archive policy remains `makepkg-git-v1`; reconstruction now records
`recipe-prepare-v1`. The original archive checksum and packaging patches are
unchanged. Git 2.56.1 and GNU patch 2.8.1 match `.BUILDINFO`, and their executable
identities are retained. Preparation uses only retained Git objects and local tools,
in a disposable repository with isolated configuration and disabled hooks.

All six recipe operations pass. The first gcc-base hunk of
`qt6-base-cflags.patch` applies at line 40 with fuzz 1; its unique intended edits
are checked against whole-file expectations and the differing `QMAKE_CFLAGS_APP`
context remains unchanged. No other hunk uses fuzz. `qt6-base-nostrip.patch`
applies cleanly, followed by all four ordered `git cherry-pick -n` commands.
[Preparation evidence](../../build/preview-hash-device-path-20261116-15/preparation.json)
retains command arguments, exit codes, output, before/after file hashes and modes,
and staged/working-tree binary-diff hashes. Patch backup/reject artifacts are
retained when present. Earlier trial directories remain sealed, including the
failed local-object transfer attempts; no historical evidence was rewritten.

The checksum-bound, recipe-prepared source now corroborates the existing matched
binary findings. [Function citations](../../build/preview-hash-device-path-20261116-15/citations.json)
include hashes, full function text and inclusive ranges:

- `qcryptographichash.cpp:944–965` forwards to the private implementation, requests
  1024 bytes repeatedly, hashes positive reads and returns `device->atEnd()`.
  This agrees with the retained binary's `0x400` request and positive-read loop.
- `qiodevice.cpp:1015–1058,1063–1193` covers the public and private read paths.
  The private implementation first consumes buffered data. With buffering enabled
  and no peek/transaction retention, a request at least the buffer chunk size can
  read directly into the caller's buffer; smaller requests refill the ring buffer.
  `qiodevice_p.h:33–34,115` sets the default chunk size to 16384.
  `qringbuffer.cpp:239–252` copies buffered bytes with `memcpy`, corroborating
  the retained constructor and ring-buffer disassembly.
- `qfiledevice.cpp:479–502` checks flushing, delegates to the engine, propagates
  errors and invalidates cached size after short reads; `383–411` checks buffered
  data and engine/size state for `atEnd()`.
- `qfsfileengine.cpp:587–600` delegates to `nativeRead`;
  `qfsfileengine_unix.cpp:144–200` handles sequential FILE streams specially and
  otherwise calls `readFdFh`. `qfsfileengine.cpp:605–659` contains the FILE/fd
  branches, `fread`/`read` calls and error handling, consistent with retained
  binary calls. Source branches do not establish which branch ran.

The [independent verification](../../build/preview-hash-device-path-20261116-15-independent.json)
reconstructs preparation in a separate temporary repository without importing
reporter code and compares operation results and retained sources. All five
blocks and 60 ordinals of signed accounting remain byte-for-byte unchanged.
Seventeen focused tests cover known fuzz, strict rejection, unchanged context,
ambiguous/unexpected placement, failed patches, ordered commits, renames with and
without edits, additions/deletions, executable modes, conflicts, retained partial
results, policy/result/source tampering, and prior identity/accounting protections.
The historical `-10` audit passes the updated checker under its original policy.
Retained tool snapshots match the implementation and whitespace checks pass.

Exact source means verified recipe-prepared contents for retained files. It does
not establish reproducible compilation, runtime branch selection, syscall counts,
or attribution of the elapsed difference. Existing native, scheduler, CPU-profile,
package and debug evidence is reused. No benchmarks, builds, recordings, downloads,
installation, production changes or optimization selection were performed.

## Qt chunk-size and buffering mechanism diagnostic — 2026-11-16

The [standalone protocol](../sdd/preview-hash-device-mechanism.md) independently
varies chunk size and QFile buffering without changing production behavior. The
[single sealed run](../../build/preview-hash-device-mechanism-20261116-01/REPORT.md)
binds exact-source audit `preview-hash-device-path-20261116-15`, its passing
verification and the unchanged throughput/payload provenance chain. The host Qt
Core Release executable passed native correctness before one single-threaded
timing process and a separate counting process. No concurrent builds/tests,
retries, cache drops, pinning or governor changes occurred.

The fixed schedule completed eight excluded warm-ups, 192 measured sweeps
(11,520 file rows and 16,745,464,320 logical bytes), then eight untimed counting
sweeps. All 60 manifest ordinals, including empty files, retained their order.
Every file matched its digest and byte count; file arms also passed error-free
EOF and final-position checks. Timing and counting processes took 8.411 and
0.392 seconds respectively, within the preregistered bounds; cleanup succeeded.
Opening, preloading, buffer allocation, common post-read validation, comparison
and output remained outside the primary read/update timer.

The following ranges summarize all eight three-sweep block means. Signed
milliseconds are left minus right; ratios are left / right durations. Every
block's magnitude, ratio and signed per-file integer reconciliation is retained
in [summary.json](../../build/preview-hash-device-mechanism-20261116-01/summary.json).

| Left / right | Signed difference range, ms | Duration ratio range | Block directions |
|---|---:|---:|---|
| Stream 1K buffered / stream 64K buffered | +0.484 to +1.677 | 1.01215–1.04272 | 8 positive |
| Stream 1K unbuffered / stream 64K unbuffered | +10.706 to +14.160 | 1.27221–1.36138 | 8 positive |
| Device buffered / device unbuffered | −12.085 to −9.417 | 0.77090–0.81139 | 8 negative |
| Stream 1K buffered / stream 1K unbuffered | −12.781 to −9.517 | 0.76040–0.80979 | 8 negative |
| Stream 64K buffered / stream 64K unbuffered | −0.463 to +0.461 | 0.98835–1.01173 | Mixed; inconclusive |
| Device buffered / stream 1K buffered | −1.036 to +0.122 | 0.97429–1.00303 | Mixed; inconclusive |
| Device unbuffered / stream 1K unbuffered | −2.491 to +0.890 | 0.95329–1.01716 | Mixed; inconclusive |
| Memory 1K / memory 64K | −0.175 to +0.370 | 0.99495–1.01078 | Mixed; inconclusive |

These contrasts support a configuration-specific chunk-size effect in both file
buffering modes, larger with buffering disabled, and a buffering effect at 1 KiB.
They do not establish a consistent separate device-interface penalty at equal
1 KiB chunks. Effects need not be additive. Pooled throughput is descriptive;
no adjacent-sweep pairing or subtraction of memory timings estimates exact I/O cost.

The [separate counting output](../../build/preview-hash-device-mechanism-20261116-01/counting.stdout)
and [joint histograms](../../build/preview-hash-device-mechanism-20261116-01/counts.json)
show the same readData request populations for device and explicit 1 KiB arms
within each buffering mode:

| Arm | readData request sizes and counts | Explicit public reads | Explicit hash updates |
|---|---|---:|---:|
| Device buffered | 5,469 × 16,384 bytes; 5,298 × 0 bytes | Unobserved | Unobserved |
| Device unbuffered | 85,260 × 1,024 bytes | Unobserved | Unobserved |
| Stream 1K buffered | 5,469 × 16,384 bytes; 5,298 × 0 bytes | 85,260 | 85,200 |
| Stream 1K unbuffered | 85,260 × 1,024 bytes | 85,260 | 85,200 |
| Stream 64K buffered | 1,424 × 65,536 bytes | 1,424 | 1,364 |
| Stream 64K unbuffered | 1,424 × 65,536 bytes | 1,424 | 1,364 |
| Memory 1K | None | 0 | 85,200 |
| Memory 64K | None | 0 | 1,364 |

Each file arm's returned-size histogram independently reconciles to 87,215,960
bytes. Public reads include terminal EOF reads. Zero-byte readData requests are
retained as Qt buffer-drain notifications. Counts come from a forwarding QFile
subclass in another process; they cannot prove identical branches in ordinary
QFile timing arms and are not syscall counts. Hardware dispatch, statistical
significance, exact elapsed-time decomposition and whole-preview gains remain
unclaimed. No production optimization is selected.

Retained evidence includes [preregistration](../../build/preview-hash-device-mechanism-20261116-01/preregistration.json),
[source/tool snapshots](../../build/preview-hash-device-mechanism-20261116-01/source),
[raw timings](../../build/preview-hash-device-mechanism-20261116-01/native.stdout),
host/CPU identity, build commands/flags, dependency hashes/build IDs, binary/linkage
and both process mapping identities, cleanup records and the
[completion assessment](../../build/preview-hash-device-mechanism-20261116-01/assessment.json).
The [independent stdlib-only verification](../../build/preview-hash-device-mechanism-20261116-01-independent.json)
replays timing coverage, counting histograms, signed arithmetic, snapshots, seals
and consumed provenance without importing the runner or reporter. Focused
verification covers ten Python fixtures and the native standard/empty, boundary,
partial-chunk, eight-arm/counting-equivalence and failure cases. Unaffected prior
verification and historical evidence are preserved.

### Buffered 64 KiB hashing practical-value assessment (2026-11-16)

The [offline protocol](../sdd/preview-hash-value.md) records the **5 ms per-preview
planning threshold** before assessment and reuses the unchanged passing independent
verifications for `preview-hash-device-mechanism-20261116-01` and
`preview-verification-work-20261115-04`. Seals, verification bindings, recursive
consumed identities, frozen payload mapping, dependency/process mappings and source
citations were rechecked without reconstruction, builds or workload reruns.

The **new post hoc direct comparison** is device buffered minus explicit stream
64K buffered, recomputed from raw timing rows rather than added prior effects.
All eight three-sweep block means, ratios and signed per-ordinal integer contributions,
including empty files, are retained in
[arithmetic.json](../../build/preview-hash-value-20261116-02/arithmetic.json).

| Block | Signed difference, ms | Device / stream duration ratio |
|---|---:|---:|
| 0 | +1.160586 | 1.02950010 |
| 1 | +1.151952 | 1.02926801 |
| 2 | +1.300482 | 1.03318440 |
| 3 | +1.204901 | 1.03071444 |
| 4 | −0.552415 | 0.98612639 |
| 5 | +1.411246 | 1.03595370 |
| 6 | +1.468762 | 1.03773350 |
| 7 | +1.118073 | 1.02838540 |

Seven blocks favor streaming; one favors device hashing. Directions are mixed
and inconclusive. All eight observed differences are below 5 ms; none equals or
exceeds it. **Defer a private A/B experiment on current evidence.** This decision
does not establish an upper bound or prove that a future implementation cannot
save 5 ms. A candidate experiment requires its own plan.

The [sealed report](../../build/preview-hash-value-20261116-02/report.md) places
these results alongside historical validation, read/hash, pixel and metadata
latencies. Measured, warm-up and setup populations remain separate, as do profiled
and unprofiled groups. Measured unprofiled validation/read-hash medians are
50.393/48.302 ms; pixel/metadata medians are 133.050/133.151 ms. These historical
latencies are a separate measurement population: no standalone difference is
subtracted from an endpoint, no quantiles are combined, and no exact critical-path
saving is claimed. Explicit execution/invocation/observation identities reconcile
historical endpoints within the same retained execution.

Frozen citations place validation in RuntimeOwner construction/refresh and read/hash
in verifyRuntime. All 52 accounted service lifetimes have one validation each;
distinct constructions do not demonstrate redundant validation within one unchanged
owner/generation lifetime. Generation identity remains unproven.

Evidence includes the [protocol](../../build/preview-hash-value-20261116-02/protocol.json),
[input bindings](../../build/preview-hash-value-20261116-02/inputs.json),
[context distributions and identities](../../build/preview-hash-value-20261116-02/context.json),
tool/test snapshots, source citations, lifetimes, machine-readable decision and
sealed completion assessment. Verification uses seven focused Python fixtures,
one offline assessment, the
[independent stdlib-only checker](../../build/preview-hash-value-20261116-02-independent.json),
snapshot comparisons and whitespace checks. Production code, prior evidence and
existing uncommitted work are preserved.
