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
