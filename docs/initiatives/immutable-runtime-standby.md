# Immutable runtime and one-shot standby gate

Date: 2026-11-11. Outcome: **no-go for this iteration**. Retain the current
fully validated on-demand source-preview transaction path.

The [Images feasibility report](../../holonight-images/docs/sdd/immutable-runtime-standby/DESIGN.md)
assesses the single permitted candidate: a system-managed, versioned, read-only
SquashFS runtime. Host checks confirm that image creation/inspection tools are
absent. Kernel SquashFS support is configured as a module, and disposable user
and mount namespace creation succeeds, but no image was constructed or mounted.
This is an unproven prerequisite, not an intrinsic rejection of SquashFS.

The existing native runtime passes full validation and fits the proposed bounds:
61 regular files and 87,212,389 bytes including its manifest, below 128 files and
128 MiB. This does not prove mounted immutability or execution binding. Protected
backing-image publication, old-alias/proc mutation resistance, exact mounted gate
and sandbox inputs, lease pinning and bounded mount teardown remain untested.
The current installer/uninstaller manage a mutable directory and do not supply
the required generation mount lifecycle across upgrade, rollback, reboot and
removal. Their staging, ownership, collision and conservative removal protections
remain unchanged.

The plan's explicit gate stop condition therefore prevents prepared-transaction
and standby implementation. Images retains synchronous runtime validation;
Thumbnails and File Browser retain existing transaction/cache ownership. No new
consumer contract or build/install dependency is introduced. A future qualified
change would follow Images → Thumbnails → File Browser → Files/chooser, with
provider/installed-package, Core-only and staged/relocated rendered acceptance
after the relevant contracts change.

Evidence is retained in
[`build/immutable-runtime-gate-20261111/evidence.json`](../../build/immutable-runtime-gate-20261111/evidence.json).
Checks cover host capabilities, disposable namespace creation, full existing
runtime validation, independent payload hashes/modes/sizes, proposed aggregate
bounds, documentation links and whitespace. No production code changes mean no
build or application acceptance reruns are needed. No standby latency samples
exist; the ≤30 ms median / ≤50 ms p95 targets and resource budgets are untested.
Historical [transaction results](source-preview-transaction.md) remain intact.
No host deployment, publication, umbrella pin update or alternative optimization
is included.

## Subsequent bounded-reuse implementation work

The subsequently approved plan permits protected root-owned directories and
bounded worker reuse; SquashFS is no longer a prerequisite. The gate outcome
above remains historical. Implementation now follows the
[Images contract](../../holonight-images/docs/sdd/bounded-sandbox-reuse/DESIGN.md)
and the [File Browser contract](../../holonight-file-browser/docs/sdd/responsive-previews/DESIGN.md).
Qualification is **incomplete**; passing implementation tests alone does not
establish that the responsiveness problem is solved.

Images owns fresh-copy generation publication, validated shared directory leases,
synchronous owner selection epochs, reusable session protocol and hierarchical
retirement. File Browser owns two worker slots, one active transaction, latest
pending selection, memory-cache concurrency, cancellation scheduling and recycling.
The umbrella installer owns collision checks, retained-generation ownership,
explicit maintenance migration and conservative uninstall. Mutable development
prefixes retain fully validated one-shot execution. Dependency order is Images →
Thumbnails → File Browser → Files/chooser. There is no deployment, publication or
umbrella pin update.

The frozen native Release comparison and exact fixture/source/build inventories
are retained under `build/preview-reuse-dgi4528s`. A is the original transaction
baseline; B adds protected owner validation reuse with one-shot execution; C adds
reusable sessions and scheduling. Historical transaction evidence is unchanged.
The new runner records pixels and final metadata separately, keeps incorrect and
missing observations, and alternates blocks of ten after separate warm-ups.
A one-sample smoke run checks the harness and cannot qualify performance.

For the recycling scenario C executes all 32 started transactions. A/B already
launch and retire on every transaction, so four setup transactions establish the
same three-source/two-entry-cache state; repeating their identical startup setup
32 times would add cost without exercising a recycling boundary. Every measured
pool miss remains included. This is the sole setup reduction from the supplied
comparison plan.

Current verification includes Images provider/installed-package tests, native
session protocol/deadline/cleanup fixtures, generation lifecycle and managed
installer fixtures, deterministic scheduler policies, File Browser preview
regressions, Thumbnails provider tests and a Core-only installed consumer.
The full File Browser provider suite and installed Core/Quick/QML/component
consumers have passed, after removing stale cached SDK selections and running
native sandbox checks with user-session access. The qualifying 100-sample
comparison, remaining Files/chooser integration acceptance and sustained resource
measurements must pass before reporting targets met. Recycling samples launch a
fresh harness/service for each observation, while retaining alternating blocks
of ten; this keeps each 32-start boundary independent of earlier samples.
No low-end hardware qualification is claimed.

## Native and package verification, 2026-11-12

Protected generation/owner fixtures, fresh-copy publication, leases, rollback,
busy upgrades, maintenance migration and conservative managed uninstall pass.
Images passes 11 provider/package checks after refreshing its explicit Debug
runtime bundle. Native sessions pass repeated-transaction, cancellation,
callback/protocol/crash, descendant, startup/transaction deadline and failed-cleanup
lease-retention checks. Ten deterministic scheduling tests cover lifecycle policy,
including idle expiry after acquisition revocation. The latter regression was
observed failing before its guard was corrected.

File Browser container acceptance passes the full 12-test provider/installed
C++/QML suite, pinned formatting/static analysis, QML checks, licensing and two
Core-only tests. Native preview regressions pass. Files and chooser pass offscreen
rendered preview/cancellation acceptance against protected reusable fixtures.
Files staging and chooser staged D-Bus activation pass. A freshly assembled,
relocated mutable prefix passes both rendered consumers and an installed
PreviewQuick C++ consumer, exercising fully validated one-shot execution. Native
interactive desktop acceptance and low-end hardware qualification are not claimed.

A mixed development prefix initially selected obsolete headers for the native
Files build; selecting one consistent installed include namespace resolved that
crash. Initial container scratch-directory and stale prepared Debug bundle
failures are retained with their corrected checks. They are not counted as
successful acceptance attempts.

The first full latency attempt exposed a frozen-baseline cleanup failure during
startup cancellation. Its diagnostics and missing observations remain preserved.
The candidate now establishes scope identity before honoring cancellation after
launch, while keeping the trusted gate closed and the startup deadline active.
Native preparation-cancellation coverage passes. The final runner continues
independent cases after failed observations and retains the affected runtime root.
The complete comparison is still required before qualification can be closed.

## Frozen comparison assessment

Outcome: **partially solved; strict qualification remains incomplete**.
The [full native comparison and assessment](../../build/preview-reuse-dgi4528s/ASSESSMENT.md)
contains baseline, protected one-shot and reusable results with absolute and
percentage changes, pixels and final metadata separately, and every failure.
The original [raw comparison](../../build/preview-reuse-dgi4528s/reuse-measurement-ml9f0eu3/comparison.md)
and [machine-readable summary](../../build/preview-reuse-dgi4528s/reuse-measurement-ml9f0eu3/summary.json)
remain intact.

All calculated numerical gates pass. Both new variants have 4,000 successful
observations. Reusable lightweight ready final metadata is at most 6.661 ms median
and 14.441 ms p95; every disk-hit fixture is at most 3.850 ms median and 4.619 ms
p95. Across pixels and final metadata, the largest memory-hit median regression
is 0.141 ms and p95 regression is 0.003 ms. The largest genuine-startup p95
regression is 12.175 ms / 8.171%, within the 10% allowance for that fixture.
Recycling and cancellation-depletion p95 improve by at least 74.646 ms and
78.759 ms respectively across the measured events.

The frozen transaction baseline has eight cleanup-flagged observations and
17 missing placeholders, all in PNG navigation at 100-ms selection intervals.
Its affected timing distributions are partial. The strict all-variant comparison
therefore fails its zero-failure requirement even though the candidate's observed
outputs and numerical gates pass. The original baseline is not modified and
failed trials are not selectively replaced. An exact successful original-baseline
navigation reference remains unresolved, so this task is not declared complete.

Final sustained candidate diagnostics observe a maximum of two helpers and
7.832 MiB retained idle scope memory, verified idle expiry without replacement,
no helper preparation for an adequate memory hit, and no remaining scopes after
shutdown. Its protected generation contains 61 files / 87,221,117 bytes including
the manifest. These measurements use memory.current and are separate from latency.

Final Files preview/thumbnail/Quick Look regressions pass 201 tests; four opt-in
performance tests are skipped in favor of the frozen harness. The first broad
Files invocation omitted its explicit runtime and selected the unchanged older
host installation; that failed run is retained. The corrected invocation uses
the prepared runtime. A final privileged fixture also confirms that a writable
source descriptor held before publication, including an ordinary-user proc-fd
alias, cannot mutate the fresh protected inode and does not change source ownership.
No deployment, publication, umbrella pin changes or low-end hardware claim is made.

## Corrected-reference qualification

The original failed comparison above remains unchanged. A separately frozen A-fixed
comparison resolves its cancellation/cleanup race but **does not close qualification**.
All 12,000 observations were collected with zero correctness, protocol, cleanup or
missing-observation failures; large-PNG startup p95 fails both pixel and metadata gates.
Metadata p95 increases from 127.835 ms to 142.340 ms: +14.505 ms / +11.35%, beyond the
unchanged 10% allowance. All other numerical gates pass. No full-run retry or selective
sample replacement was performed.

A-fixed changes only cancellation ordering in the original transaction runtime. B/C
frozen source and binary identities match; their existing integration and
generation-lifecycle evidence remains applicable. Nine A-fixed
provider/installed-package checks, native fault checks, deterministic cancellation
boundaries and ten assessment regressions pass. Separate C diagnostics verify the
two-helper cap, 6.836 MiB retained idle memory, idle expiry, generation storage bounds
and complete shutdown. Separate A-fixed diagnostics pass with one helper, zero retained
idle memory and complete shutdown. The original baseline race and its failures remain
historical evidence; the corrected reference does not retroactively validate them.

The [updated timing
report](preview-timing-comparison.md#corrected-reference-comparison-qualification-failed)
and [new assessment](../../build/preview-corrected-qjln5jn4/ASSESSMENT.md) identify
original A and A-fixed separately, give absolute/percentage changes and link all raw
evidence. They also document that the saved runner removed its transient runtime root
before numerical assessment; frozen runtime inputs and raw observations remain, and the
final tooling now preserves such fixtures with regression coverage. No deployment,
publication, pin changes, further performance optimization, native interactive or
low-end hardware qualification is included.

## Initial standby contention follow-up

The bounded diagnostic is **inconclusive and stopped before the pilot**. Four private
instrumented variants distinguish A-fixed, B, unchanged C and initial-standby-deferral
D. Traces show concurrent standby preparation in 400/400 unchanged-C startup jobs
and 0/400 D jobs, but the wrapper-owned output directory prevented ordinary-user
harnesses from saving timing JSON. All 1,600 measured observations are missing;
all 176 invocation failures and trace logs remain intact. No latency improvement or
startup gate pass is inferred from tracing.

The run returned nonzero, preserved protected fixtures, verified unchanged input
hashes and found no residual helper scopes. The ownership fix passes an ordinary-user
write regression under the privileged wrapper. Seven new tooling regressions and
30 existing experiment-tooling tests pass. No samples were replaced or rerun; no
production correction, provider/consumer change, full qualification, deployment,
publication, pin update or GRUB change followed. Both earlier comparisons remain
failed. See the [timing report](preview-timing-comparison.md#initial-standby-contention-diagnostic-inconclusive)
and [retained assessment](../../build/preview-standby-arb90t5w/ASSESSMENT.md).

## Fresh bounded scheduling comparison

The fresh diagnostic is valid, but the single startup pilot is **unsuccessful**.
All 3,200 measured observations are complete and valid. Correlated preparation
overlap occurs in 400/400 unchanged-C jobs and 0/400 initial-deferral D jobs.
Nevertheless, D's large-PNG pixels/metadata p95 worsen by 3.878/3.881 ms (+2.64%)
against contemporaneous C. All eight startup allowances against contemporaneous
A-fixed pass, but the independent improvement requirement fails.

The cycle therefore stops without a production scheduler change, another tuning
cycle, full qualification comparison or repeated resource diagnostics. Earlier
failed runs remain unchanged; strict qualification remains failed. Frozen source,
host dependency, binary, harness and fixture identities were verified before
measurement; final input hashes and helper shutdown checks pass. Ordinary-user
artifact writes pass through the privileged wrapper before measurement.

The [timing report](preview-timing-comparison.md#fresh-bounded-scheduling-comparison-unsuccessful-pilot)
and [retained assessment](../../build/preview-standby-drbq1ofy/ASSESSMENT.md) link
preregistration, raw diagnostic/pilot observations and complete gates. No public
API, deployment, publication or pin change is made. Deferred follow-ups remain
outside this experiment.
