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
