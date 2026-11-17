# Startup validation reuse feasibility — 2026-11-17

**Validation reuse: Deferred. Overall candidate selection: Evidence insufficient.**
This bounded source review follows the [startup evidence update](startup-evidence-update.md)
and reuses [work audit 04](../../build/preview-verification-work-20261115-04/REPORT.md).
It finds an explicit refresh path that can repeat full validation, but no retained
observation of repeated verification within one proven unchanged owner/generation.
The existing contract authorizes reuse through a validated protected-generation
lease; it does not authorize skipping validation on refresh or across owners.
No savings, optimization priority, implementation or further experiment is selected.

## Evidence boundary and source versions

Before relying on retained claims, read-only SHA-256 checks matched every member of
work audit 04's seal and every recorded `inputs.json` identity, plus all six frozen
[source citations](../../build/preview-verification-work-20261115-04/source-citations.json).
Its [passing independent verification](../../build/preview-verification-work-20261115-04-independent.json)
binds audit seal `6c2a6671b1d36a7adbd8ce18b51d3b45b06e43ed5a7776f2d144da220676d407`.
The [applicability audit](startup-validation-applicability.md) seal inventory and
recorded input file hashes also match; its [passing verification](../../build/preview-startup-applicability-20261116-05-independent.json)
binds seal `77a96dff3b8376ad14c112218b5251d9eecd5c6519c5d1d549f08a94272528ca`.
These checks reuse completed verification, rather than rerunning the auditors.

Historical baseline is qualification C at
`build/preview-corrected-qjln5jn4/C/source/`, identified by the applicability audit's
[sources.json](../../build/preview-startup-applicability-20261116-05/sources.json)
and recorded hashes, not by current checkout assumptions. Its shared harness is
[retained separately](../../build/preview-corrected-qjln5jn4/harness-source/).
The work audit cites the instrumented validation C overlay, not qualification C.
The applicability audit records the intervening tracing/validation transformations;
those relationships establish source compatibility, never identical timing,
dependencies, loading or generation identity.

Current source was reviewed separately at Images revision
`928f281586686a67584d610cd3b2a1468536c185` and File Browser revision
`dc675f68c691209b2e0e32fa20d9af1ccb30936c`. Exact comparisons found qualification
C and current files identical for Images `generation.cpp`, `verification.cpp`,
`runtime.cpp`, `helper.cpp`, and File Browser `session_pool.cpp`,
`preview_service.cpp`. Historical identities remain the frozen file hashes;
current revisions do not retroactively identify the qualification execution.
Current tests and installer contracts below are reviewed as contract evidence,
not as historical execution evidence.

The work audit's **52 distinct service constructions, each validating once**, are
reused without regenerating accounting or distributions. Its 40 measured,
two warm-up and ten setup validations remain separate. A generation wrapper and
its nested runtime validation are one payload pass, not two. Uninstrumented helper
entry points cannot be excluded merely by absence of validation traces.

## Reachable call paths

The following paths occur in both qualification C and current source unless a
caller is explicitly identified as current diagnostic tooling. Links point to the
current files whose exact historical comparisons are recorded above. The work
audit's frozen citations supply the instrumented counterparts.

| Trigger and reachable caller | Owner lifetime | Generation/lease relationship | Verification performed | Existing reuse | Evidence limitation |
| --- | --- | --- | --- | --- | --- |
| `PreviewService` construction queues `PreviewSessionPool` construction; protected runtime has `current` | One owner per pool/service | Owner constructor calls `refresh()` and publishes selected lease | Protected base/tree, selector/descriptors, shared lock, protected generation, full `verifyRuntime`, policy digest, final selection identity | Later acquisitions share selected lease | Asynchronous worker construction is not necessarily inside the service constructor body; audit establishes distinct lifetimes |
| `reusable()`, preparation, standby replacement and pool job launch | Same pool owner | `acquire()` copies selected lease; preparation captures it in worker closure; job receives lease | Acquisition does not rehash; session launch consumes validated binds | Already avoids full verification per preparation/transaction | Session recycling or a second worker does not imply another owner validation |
| Explicit `PreviewService::refreshRuntime()` → pool `refresh()` → owner `refresh()` | Same owner, new selection attempt | Clears acquisition first; builds a fresh lease after successful validation; active old leases survive | Full construction-time validation again, even if selector text matches | No refresh cache | API is callable; no caller in inspected production source or retained qualification harness. Current cancellation diagnostic calls it; retained startup audit does not establish this path executing |
| Pool job without prepared session, with acquired generation lease | Same pool owner | Lease passed through decode request to runtime launch | Launch authorization and verified binds; no second `verifyRuntime` | Lease reuse also covers protected legacy one-shot execution | A fallback is not automatically another full pass |
| Runtime launch without supplied lease, with `current` | Local `RuntimeOwner` per launch | Constructs owner, acquires lease, retains lease after local owner dies | Full generation validation | Lease covers that launch | Repeated direct calls can validate across distinct owners; this does not establish within-owner redundancy |
| Runtime launch without lease and without `current` | No reusable protected owner | Mutable development runtime, per-launch path | Full `verifyRuntime` each launch | None intentionally | Mutation/replacement between calls is permitted; equal path or payload cannot authorize omission |
| Helper `--verify-runtime` / `--verify-protected-runtime`, called by generation installer | Helper process per invocation | Installation/inspection boundary, not pool acquisition | Full runtime validation; protected variant also checks ownership/modes through ancestors and tree | No shared owner cache | Source preflight and copied/published generation checks concern different trust boundaries; not startup repetition in the retained population |

Construction and acquisition are in
[PreviewService](../../holonight-file-browser/src/preview/preview_service.cpp)
(lines 590–600), [pool](../../holonight-file-browser/src/preview/session_pool.cpp)
(lines 55–87, 176–209, 445–464), and
[RuntimeOwner](../../holonight-images/src/isolated/generation.cpp)
(lines 108–199). Explicit refresh is at service lines 812–824 and pool lines
544–563. The only current service refresh caller found outside its declaration
and implementation is the [cancellation diagnostic](../../tooling/preview-cancellation/main.cpp)
(line 73, preparation-cancellation scenario); pool tests invoke pool refresh directly.
The retained qualification harness contains no refresh caller. Callable public APIs
and diagnostic scenarios therefore do not establish repetition on measured startup.

[Runtime launch](../../holonight-images/src/isolated/runtime.cpp) lines 208–227
separates supplied-lease, local-owner and mutable-runtime branches.
[Helper main](../../holonight-images/src/isolated/helper.cpp) lines 164–176 handles
verification flags and exits; ordinary gate/readiness/session execution does not
implicitly call that verification branch. The
[generation manager](../../scripts/manage-images-generations.py) invokes the flags
in `verify()` and installation preflight. Matching bytes before copying and after
protected publication do not make those checks interchangeable.

## Integrity obligations for any later omission

The current [verification contract](../../holonight-images/src/isolated/verification.h)
requires full validation on every `verifyRuntime` call. Protected eligibility is
additional: it does not itself verify payload hashes. Existing reuse stores the
result of full validation in a lease, within this contract.

- **Protected selection:** retain root ownership and non-writable modes for every
  ancestor and tree entry; reject symlinks. Pin no-follow descriptors, validate the
  regular fixed-size selector, acquire the shared generation lock, and recheck
  selector and directory identity after validation. A manifest basename, payload
  hash match, pathname or reused object address is insufficient generation identity.
- **Inventory and hashes:** preserve manifest policy/version and session capability,
  bounded file/byte inventory, exact modes/sizes, required entries, SHA-256 of every
  listed payload and rejection of unexpected entries. A metadata-only cache would
  omit guarantees the current verifier makes.
- **Validation-to-launch binding:** launch the selected protected generation using
  binds derived from its validation and retain its lease. Read-only sandbox binds
  alone do not freeze mutable backing bytes; locks are cooperative installer
  protection, not protection from arbitrary privileged mutation.
- **Refresh/replacement:** refresh revokes new acquisitions before validation;
  failure leaves them revoked. Successful replacement publishes a new selection
  while active leases retain the old generation. Skipping validation because the
  selector string matches would require a separately justified identity and
  freshness rule; none is supplied by this review.
- **Lease retention and cleanup failure:** keep the shared lock until the last
  relevant lease is released. Cleanup failure permanently disables owner launches,
  including after refresh, and failed cleanup retains the generation beyond owner
  and session destruction until process exit. A reuse policy must preserve these
  failure semantics and conservative removal protections.
- **Mutable development runtimes:** retain per-call validation and one-shot execution;
  they never qualify for the protected prepared-session path. Do not extend lease
  reuse merely because two successful validations saw identical payloads.

Existing [generation tests](../../holonight-images/tests/isolated_generation_test.cpp)
cover mutable ancestors, lease pinning across refresh, failed/concurrent refresh
revocation, selector symlinks/digest mismatch, permanent cleanup disablement and
capabilities per selection. [Verification tests](../../holonight-images/tests/isolated_verification_test.cpp)
cover aggregate limits and inventory symlinks. The
[pool tests](../../holonight-file-browser/tests/session_pool_test.cpp) cover obsolete
preparation after refresh and permanent cleanup failure; injected operations are
scheduling contract evidence, not proof of real validation repetition.
The [session cleanup test](../../holonight-images/tests/isolated_session_test.cpp)
`FailedCleanupPinsBeyondOwnerAndSessionUntilProcessExit` checks retained lock lifetime.
These tests were inspected, not rerun.

The older [runtime-generation design](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md)
records sealed-memfd metadata and FUSE no-go results. Its statements that explicit
refresh was not implemented describe that historical design stage. Current source
already implements protected owner/lease reuse and refresh; the older snapshot
proposals neither supersede this contract nor authorize a new omission.

## Separate conclusions

1. **Repeated source call path:** explicit refresh can repeat full validation in
   one owner, including a possible unchanged selection. The current diagnostic
   caller makes this more than an unused API, but no production or qualification
   startup caller found here establishes that repeated startup path. Direct
   lease-less launches can repeat validation across separate owners. Normal pool
   acquisition/preparation already reuses validation.
2. **Retained execution:** no observation proves repeated verification within one
   unchanged owner/generation. Work audit 04 establishes 52 separate service
   lifetimes with one validation each. Its matching payloads and object addresses
   cannot bridge lifetime or generation identity; qualification generation and
   loaded-dependency limitations remain unresolved.
3. **Permission to omit work:** the current contract permits the existing protected
   lease reuse, not skipping refresh validation, mutable-runtime validation or
   installer checks. No additional integrity-preserving omission is established.

Validation reuse stays **Deferred**. The precise missing facts are an applicable
repeated execution tied to one unchanged owner/generation, and a contract proving
that the particular omitted work preserves selection, integrity, launch binding
and failure semantics. Refresh-on-unchanged-selection is only a source hypothesis,
with no claimed savings. Even a demonstrated opportunity needs a later implementation
plan; this review does not automatically select an experiment.

Streaming remains **Deferred** after completed trial 05. Read-only checks of that
trial's findings and execution seal inventories matched; the passing execution
verification binds its execution seal. Overall selection remains **Evidence
insufficient** and historical qualification remains **78/80**. The qualification
allowance and separate trial planning threshold are unchanged. Historical,
instrumented, profiled, standalone and fresh trial populations are not pooled;
no diagnostic difference is subtracted from qualification p95. Stopped trial 04
and all sealed evidence remain untouched.

Only this report is added. Local links, whitespace including this untracked file,
and the final diff were checked. Completed native/package verification is reused;
no build, suite, workload, recording, staging or measurement was run.
