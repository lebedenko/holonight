# Broader startup critical-path review — 2026-11-17

**Selected follow-up investigation: cache storage before first pixel publication.**
This selects one bounded question about ordering, not an optimization, measurement,
instrumentation change or executable experiment protocol. Overall candidate selection
remains **Evidence insufficient**. Streaming and validation reuse remain **Deferred**;
SHA-256 dispatch remains deferred. Historical qualification remains **78/80**.

## Evidence and source boundary

Read-only SHA-256 checks matched the sealed inventories and recorded consumed file
and inventory hashes of accepted [helper review 03](../../build/preview-helper-startup-review-20261116-03/ASSESSMENT.md),
[remainder 04](../../build/preview-helper-remainder-20261116-04/REPORT.md),
[applicability audit 05](../../build/preview-startup-applicability-20261116-05/REPORT.md),
[identity review 03](../../build/preview-identity-review-20261117-03/REPORT.md), and
[validation work audit 04](../../build/preview-verification-work-20261115-04/REPORT.md).
Their passing independent verification records bind the following seal hashes:

| Retained result | Seal SHA-256 | Passing verification |
| --- | --- | --- |
| Helper review 03 | `0fc193f8b8bd059445d01fd37b938e7aed50ff98c4e71bb7fd8e81eb854765a7` | [record](../../build/preview-helper-startup-review-20261116-03-independent.json) |
| Remainder 04 | `b100c7c5b7b5e6580525b1635ab6a2a1049fc9baf24ebd081f0ee0963445164d` | [record](../../build/preview-helper-remainder-20261116-04-independent.json) |
| Applicability 05 | `77a96dff3b8376ad14c112218b5251d9eecd5c6519c5d1d549f08a94272528ca` | [record](../../build/preview-startup-applicability-20261116-05-independent.json) |
| Identity review 03 | `5856c6e014e06c2a356baddb078b39ae79f0e82af4a24eacf7957e2cd7705ac9` | [record](../../build/preview-identity-review-20261117-03-independent.json) |
| Validation work 04 | `6c2a6671b1d36a7adbd8ce18b51d3b45b06e43ed5a7776f2d144da220676d407` | [record](../../build/preview-verification-work-20261115-04-independent.json) |

The completed streaming trial's [findings](../../build/preview-streaming-trial-20261117-05-findings/REPORT.md)
seal inventory and recorded input hashes also matched. Preparation, build and
execution seal inventories matched their passing verification bindings; execution
seal is `f495614252e69527999677b3d03db5d2651ad0b86df5cd87c0b077d4fedbaa09`.
The [streaming update](startup-evidence-update.md) supersedes the identity review's
older missing-startup-effect statement for that tested candidate. Its completed
trial missed the planning threshold. The [reuse review](startup-validation-reuse-review.md)
finds a callable refresh path, but no proven repeated validation within one unchanged
owner/generation. No evidence discrepancy was found or repaired.

Historical baseline is retained qualification C in
`build/preview-corrected-qjln5jn4/C/source/`, with identities recorded by audit 05's
[source relationships](../../build/preview-startup-applicability-20261116-05/sources.json)
and consumed inventories. Its [shared harness](../../build/preview-corrected-qjln5jn4/harness-source/reuse.cpp)
is separate from production source. A-fixed comparison uses retained A source and
the corrected shared harness, not the earlier uncorrected timing origin.

Current checkouts were inspected separately: Images
`928f281586686a67584d610cd3b2a1468536c185`, File Browser
`dc675f68c691209b2e0e32fa20d9af1ccb30936c`, Thumbnails
`945aedf4256c0d2e6c358c2fa3cee8e49316c651`, and Files
`4deab396a0f959be9959d3f5785e535ccc546774`.
Exact byte comparisons found C and current source identical for File Browser
`preview_service.cpp`, `session_pool.cpp`, `thumbnail_service.cpp`; Images
`generation.cpp`, `client.cpp`, `capture.cpp`, `runtime.cpp`, `helper.cpp`,
`protocol.cpp`; and Thumbnails `cache.cpp`. Current `tooling/preview-benchmark/reuse.cpp`
also matches the retained harness; its README differs, so historical harness
semantics below come from retained code. The current Files caller is production
reachability evidence only, not a frozen qualification caller or loading identity.

A has no C session-pool implementation. Its service uses the one-shot transaction
path; C adds deferred pool submission, session readiness, standby preparation and
cache synchronization. A's thumbnail delegate and cache implementation are byte
identical to C's, and its service also stores before publishing pixels (A lines
284–296 versus C lines 307–320). Thus this ordering is a common startup opportunity,
not an established explanation for C-minus-A-fixed regression. Source compatibility
does not establish timing or binary equivalence. Historical transient generation
and loaded-dependency gaps remain; the later identity review resolves mappings only
for its own captured observations, not historical or uncaptured executions.

## Startup dependency sequence

Links below point to current files compared with retained C above; line references
describe that common source. This sequence distinguishes prerequisites from overlap.

1. The current production [selection controller](../../holonight-files/apps/files/preview/preview_selection.cpp)
   `syncPreviewTarget()` passes the selected entry, revision and native path to
   `PreviewService::setTarget()`. The retained startup harness instead starts its
   clock, constructs a fresh service with a 256×256 pane request, then calls its
   `target()` helper without waiting for readiness (`reuse.cpp` lines 115–119,
   197–245). Private cache and copied sources precede timing; startup is distinct
   from ready, disk and memory scenarios. First adequate pixels and final non-busy
   metadata are observed through `changed`, not at the worker's decode return.
2. [Service construction](../../holonight-file-browser/src/preview/preview_service.cpp)
   lines 590–598 queues pool construction before `startJob()` queues source work
   (lines 840–910) on the same control worker. [Pool construction](../../holonight-file-browser/src/preview/session_pool.cpp)
   lines 55–87 synchronously creates the protected `RuntimeOwner`, whose
   [refresh](../../holonight-images/src/isolated/generation.cpp) validates selection
   before publishing a lease. This delays queued source open/sniff. Once validated,
   `prepare(0)` runs on a slot thread, allowing preparation to overlap subsequent
   control-worker source work. Validation-before-launch is required; source sniff
   need not inherently wait for it, but moving that work requires a separate safe
   scheduling design. Acquisitions already reuse the validated lease.
3. `runPreviewJob()` opens a nonblocking, close-on-exec descriptor, verifies a
   regular file, records source identity, sniffs MIME and checks memory candidates.
   A cold raster miss transfers a duplicated descriptor through `defer` and
   `makeRasterJob`; the slot rechecks identity before decoding. Pool `schedule()`
   (lines 316–372) waits for preparation and refuses concurrent active/retiring
   work. That refusal protects cancellation cleanup; it is not freely removable
   queueing. `transactionStarted()` may prepare standby concurrently after actual
   dispatch, within the two-helper cap.
4. [Runtime preparation](../../holonight-images/src/isolated/runtime.cpp) lines
   290–344 starts systemd-run, discovers the owned cgroup via `groupOf()`, verifies
   actual memory/swap limits, writes `G` and attempts to flush it, then receives `R` and
   session readiness. [Helper main](../../holonight-images/src/isolated/helper.cpp)
   lines 148–158 gates exec before image input; lines 180–201 initialize helper
   I/O and emit/flush readiness. Scope ownership, limits and gate-before-input are
   security dependencies. Parent discovery polling and marker receipt are distinct
   boundaries; neither waiting state identifies a cause.
5. [Client run](../../holonight-images/src/isolated/client.cpp) captures bounded
   source bytes before transaction dispatch; [capture](../../holonight-images/src/isolated/capture.cpp)
   seeks the verified device and checks cancellation, errors and input ceiling.
   A reusable session is already prepared at this point. The transaction sends
   source once for inspection, tries eligible cached PNG candidates, and can decode
   the retained source without retransmitting it. Runtime lines 347–439 enforce
   sequence/transaction identities, reply bounds and completion acknowledgement.
   [Wire serialization](../../holonight-images/src/isolated/protocol.cpp)
   `replyControl()`/`parseReply()` copies bounded raw pixel rows and validates their
   layout/color information; this is separate from PNG encoding for disk storage.
   Neither eliminating source retention nor bypassing completion is authorized.
6. On successful original decode with a valid tier and unchanged source,
   service `decodeImage()` lines 307–320 calls `ThumbnailService::storeRaster()`
   **before** its progressive `publish(result)`. The [delegate](../../holonight-file-browser/src/preview/thumbnail_service.cpp)
   lines 128–133 synchronously calls [cache store](../../holonight-thumbnails/src/cache.cpp)
   lines 207–264: eligibility, metadata tags, private file, PNG serialization,
   cancellation checkpoint and atomic commit. Store failure is best effort and
   does not itself invalidate decoded pixels. Thus persistence precedes pixels
   in source order without supplying their decode validity.
7. Service lines 321–340 format source EXIF and populate the bounded memory cache;
   the raster job publishes the final metadata result. `publish` queues
   `applyResult()` onto the service thread, which rejects stale generations and
   timed-out results and preserves progressive pixel/metadata behavior (lines
   860–863, 913–962). Worker publication and consumer delivery are separate events.
   Session retirement/cleanup and shutdown remain required even if publication
   ordering is investigated.

## Four bounded hypotheses

The following table has one hypothesis per review area. “Support” means support for
further investigation, not measured savings or authorization to change behavior.

| Area and reachable hypothesis | Applicable retained evidence | Proposed avoidable ordering and integrity obligations | Contradictory evidence / limitation | Smallest missing observation; supporting / rejecting outcomes |
| --- | --- | --- | --- | --- |
| Service/pool: fresh startup source open/sniff waits behind owner construction on the control queue. | C constructor and harness above; remainder 04 identifies validation as the leading disjoint active set in all 32 required C views. | Source-only preparation might overlap validation; launch must still require a validated lease. Preserve descriptor identity, cancellation, latest pending demand, worker ownership, caps and retirement barriers. | Validation duration is not overlap savings. Helper preparation already overlaps source work after constructor return. No retained source-ready/validation overlap budget establishes useful independent work. | Same-observation source-work eligibility and validation completion relation. Support: meaningful independent source work is ready while validation blocks its queue. Reject: source prerequisites arrive later or work is negligible. Requires resolving an additional scheduling/ownership boundary before a safe approach is concrete; not selected. |
| Launcher/readiness: the 5 ms discovery polling cadence adds avoidable delay after the owned scope is observable. | Review 03's frozen polling caller and competing scope/marker distributions. | A later design could react sooner to owned-scope visibility; preserve proven scope identity, actual limits, gate-before-input and cancellation-safe cleanup. | Winners disagree across required views; non-runnable states identify no cause. Scope creation and post-gate helper progress can explain the waits without polling loss. | Identity-bound scope visibility versus first successful parent discovery. Support: visibility precedes recognition with polling delay. Reject: recognition promptly follows visibility. This still leaves the separate helper-emission/receipt question; not selected. |
| Transfer/decode/serialization: raw-pixel materialization/copying unnecessarily extends the successful reply path. | Runtime/protocol source above; remainder 04 retains decode exchange as a separate active set. | A later representation might avoid a copy while preserving immutable bounded reply ownership, format/stride/color validation, source retention, cancellation and completion. | Decode exchange includes helper work and transport; raw copies are not PNG serialization. No retained copy-specific coverage or demonstrated replacement establishes removable work. Already retained source avoids retransmission. | Same-transaction copy-only coverage versus decode/transport. Support: removable materialization occupies meaningful serial coverage. Reject: copies are small or required for validated ownership. A concrete contract-preserving alternative is still missing, so this does not qualify. |
| Cache/store/delivery: successful cold raster pixels wait for best-effort disk persistence before the first publish. | Direct C and A ordering; remainder 04's disjoint nested store/PNG active set; cache failure and progressive-delivery tests below. | Investigate eligibility to queue the existing progressive pixels after successful transaction return and before store, keeping store and final completion on their existing bounded worker path. Preserve source checks, cancellation, atomic/private cache writes, final metadata ordering and cleanup. No background writer is proposed. | Common to A/C; store is smaller than validation. No retained result proves earlier consumer delivery or a startup p95 improvement. Main-thread delivery can lag a queued publish. Cache readiness at final completion must remain. | One identity-bound relation between validated pixel eligibility, the existing store interval and consumer delivery opportunity. Support: eligible same-generation pixels could be consumed while store is outstanding. Reject: a required prerequisite or consumer unavailability keeps delivery after store. This is the selected question. |

Existing [remainder distributions](../../build/preview-helper-remainder-20261116-04/distributions.json)
are reused without new rankings: pooled C pixel medians for the disjoint nested
raster/store/PNG active set are **12.333 ms instrumented** and **12.284 ms captured**;
decode exchange is **29.945 / 28.473 ms**, and leading validation is
**47.531 / 48.656 ms**. These are separate distributions, not additive medians,
copy costs, removable time or qualification-tail attribution. Store scopes and PNG
children must not be added. Review 03's 150 measured observations/300 endpoints
remain separate from six warm-ups/12 endpoints and from setup/standby preparations.
The validation work audit's 52 owners each validate once; they are not 52 redundant
checks. No waiting-state, CPU-sample or cross-population timing inference is used.

## Selected question and limits for later planning

**Question:** On the cold, tier-eligible raster startup path, is validated progressive
pixel delivery held behind disk-cache persistence even though the current consumer
could accept those same pixels while the store remains outstanding?

This has the strongest direct evidence of an optional serial dependency among the
four areas: source order is explicit, a disjoint store population already exists,
and store failure does not veto pixels. A plausible bounded approach is to consider
the existing progressive publish earlier while leaving store and final completion
on the same worker. It avoids adding a second storage lifetime or unbounded work.
This is a feasibility direction, not an approved edit. The larger validation set
does not establish avoidable overlap, and the helper waits require additional causal
boundaries. No tie remains under the plan's evidence-first selection rule; selecting
this investigation does not rank optimization candidates by expected gain.

The single missing observation is the eligibility/store/delivery relation described
in the table. Its source boundaries are successful `sourceTransaction()` return,
the unchanged-source/tier checks, `storeRaster()` entry/return, progressive publication
and `applyResult()`/first adequate-pixel notification. Reuse existing matched store
and delivery boundaries where available; this report specifies no probes or recorder.
The relation must distinguish a storage prerequisite from merely delayed consumer
dispatch. Observing store before publish alone reconfirms source order but cannot
establish that earlier consumer delivery is possible.

Any later evidence needs exact source/helper/harness/runtime and dependency identities;
protected selection and validated-lease identity; source descriptor/revision, requested
size, cache tier/miss and decode outcome; invocation, service lifetime, request generation,
worker, preparation and transaction identities; explicit process lifetimes and one
clock for related events. Unavailable identities remain unavailable. Match preparation
and transaction explicitly, never by nearby timestamps or reused addresses. Main-thread
eligibility and receipt must refer to the same live, non-cancelled, non-timed-out request.

A supporting outcome establishes a real interval in which complete validated pixels
are eligible and the consumer can accept them while best-effort store continues,
without changing final metadata/cache readiness or cancellation semantics. A rejecting
outcome identifies a required pre-publication dependency, no consumer opportunity
before store ends, or no eligible store path. Ambiguous identity/order or inadequate
coverage yields **Evidence insufficient**, not a supporting outcome. Neither outcome
alone establishes savings, a 5 ms gain, or qualification acceptance.

Scope excludes validation/hashing changes, earlier gate release, launcher changes,
wire/protocol changes, new threads or asynchronous cache lifetimes, SVG, warm memory
or disk hits, standby optimization, threshold changes and fresh qualification.
Final metadata must not report completion before the preserved store/memory-cache
work finishes. A later implementation plan must resolve interactions with target
changes, timeout, shutdown and image retention before proposing an edit or measurement.

## Contract review and verification

Existing tests were inspected as contract evidence, not rerun:

- [Isolated preview tests](../../holonight-file-browser/tests/isolated_preview_test.cpp):
  `TargetChangeWhileCommittingDropsOldPixelsAndCache` requires superseded work to
  leave no old cache/pixels; `DiskHitKeepsSourceExifOrientationAndNotificationOrder`
  preserves source facts and pixels-before-metadata; memory-checkpoint tests reject
  cancelled, superseded, timed-out and shutdown replies. Earlier publication must
  retain generation checks and must not claim permission to publish stale results.
- [Cache tests](../../holonight-thumbnails/tests/cache_test.cpp): cancellation at
  commit keeps the previous image; concurrent stores remain readable; private
  permissions and write-failure-as-miss are explicit contracts.
- [Pool tests](../../holonight-file-browser/tests/session_pool_test.cpp): latest
  pending selection, two-helper cap, obsolete preparation after refresh, permanent
  cleanup disablement and retirement before standby decode constrain overlap.
- [Transaction tests](../../holonight-images/tests/isolated_transaction_test.cpp)
  and [session tests](../../holonight-images/tests/isolated_session_test.cpp) retain
  source isolation, bounded candidates, completion validation and cancellation
  poisoning. [Cleanup tests](../../holonight-images/tests/isolated_cleanup_test.cpp)
  require cancellation during completion/cleanup to win delivery.

Only this report is added. Local links and whitespace, including the untracked
report, and the final diff were checked. Completed verification is reused; no builds,
suites, staging, workloads, recordings, new accounting or measurements were run.
Sealed evidence and stopped streaming trial 04 remain unchanged. Historical,
instrumented, captured, profiled, standalone, identity-baseline and streaming-trial
populations remain separate. No diagnostic duration is subtracted from qualification
p95, and the qualification allowance and trial planning threshold remain unchanged.
