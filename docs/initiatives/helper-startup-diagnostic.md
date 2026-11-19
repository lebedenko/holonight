# Private A/C helper-startup diagnostic — 2026-11-16

**Latest result:** the [fresh fourth attempt](#completed-fresh-attempt) completed all 36 invocations, with 150 measured observations and 300 measured endpoints. Independent verification passed. Earlier stopped attempts below remain historical.

The first native attempt **stopped during warm-ups**, after three of the frozen
36 invocations. Two baseline warm-ups passed. The instrumented A warm-up completed
its original pixel, metadata, process, v3 and v4 predicates, but the new strict
validator rejected its supplemental-to-v3 interval binding. The remaining 33
invocations were not launched. **Zero measured observations and zero measured
endpoints were collected.** No latency comparison or scheduler attribution is
supported. No optimization is selected; qualification remains failed at 78/80
numerical gates under unchanged thresholds.

## Scope and tools

The [runner](../../scripts/run-preview-helper-startup.py) has separate `build` and
`execute` actions and narrowly elevated `stage` and `record` workers. It reuses the
historical native recipes, four-job builds, original harness predicates, protected
staging, process supervision and recorder helpers. The preparation, its analyzer,
its tests, and the delivery-tracing narrative remain unchanged.

The frozen protocol contains six excluded warm-ups, then five rotating blocks
with alternate blocks reversed: 36 invocations, 150 intended measured observations
and 300 intended measured endpoints. Only startup and the retained 3200×2400 PNG
are permitted. Captured launches share instrumented binaries, receive unique
`HOLONIGHT_HELPER_INVOCATION` identities after desktop credentials are selected,
and keep a 30-second readiness/workload budget and five-second termination grace.
No extra harness smoke workloads, retries, cache flushing, affinity adjustments or
artificial load were added.

The [offline reporter](../../scripts/report-preview-helper-startup.py) adds strict
thread nesting, source operation coverage, boundary outcome and exact v3 identity
checks above the existing permissive analyzer. Setup, standby and selected demand
preparations remain separate; unavailable preparation and runtime-generation IDs
are retained explicitly. Supplemental decimal timestamps pass through the original
parser before scheduler normalization. Hostname, machine ID and boot ID are recorded
separately; trace agreement uses hostname and boot ID.

The [independent checker](../../scripts/verify-preview-helper-startup-run.py) imports
neither runner nor reporter. It verifies sealed inventories and tool snapshots,
preparation source reconstruction, schedule prefixes and remaining rows, raw and
source citations, interval arithmetic, and any available scheduler reconciliations
and summary calculations. Historical tool snapshots remain authoritative after an
explicit corrective revision; they are not overwritten with the current tools.

## Evidence and failure

- [Preparation](../../build/preview-helper-startup-20261116-05/ASSESSMENT.md), seal
  `732e4d06eaf6c93e4bb13c82133d305f77a8b6f414614d2e9e85854d35b4f84d`:
  independent static verification passed for four trees and 553 source citations.
- [Native build](../../build/preview-helper-startup-native-20261116-01/ASSESSMENT.md):
  exactly one workload-free recorder rehearsal passed before the four builds.
  Baseline/instrumented A/C built against host dependencies with private installed
  prefixes. Provider resolution, runtime manifests, native linkage and original
  versus supplemental probe symbols passed.
- [Sealed execution](../../build/preview-helper-startup-execution-20261116-01/ASSESSMENT.md):
  three invocations launched, two accepted warm-ups, the third rejected by the
  strict gate, and 33 unexecuted rows retained. There were no captured harness
  invocations. The rehearsal is not a harness invocation or observation.
- [Corrected offline replay](../../build/preview-helper-startup-report-20261116-04/REPORT.md)
  and [independent verification](../../build/preview-helper-startup-report-20261116-04-independent.json):
  all three retained invocations replay successfully; the original execution
  remains blocked. Intermediate blocked offline reports are retained separately.

In instrumented A, supplemental preparation span 1 on PID 29072/TID 29082 has
service 2, observation 1, job 3, worker 4 and unavailable preparation ID. Its v3
`helper_prepare` interval ends at 8041344458640 ns; the supplemental root ends at
8041344474344 ns, **15,704 ns later**. The supplemental scope includes final
bookkeeping after the v3 interval. The original validator incorrectly required
complete containment and therefore reported `missing/ambiguous v3 helper
preparation binding`. This is a new validator defect, not a failed harness result
or evidence of a frozen-source defect.

The offline correction binds exact process/thread/service/observation/job/worker/
preparation identities, verifies overlapping lifecycle boundaries and retains both
intervals and the supplemental tail. A's one-shot lifecycle uses its explicit
`demand_dispatch` job/worker instead of C's `selected_worker` record; A's preparation
ID stays unavailable. Regression tests cover both cases and reject foreign job or
worker identities. This correction was not used to resume or rerun the experiment.
The executed tool versions and original failure remain inside their original seals.

Four fresh root-owned runtimes remain under
`/run/holonight-helper-startup-preview-helper-startup-execution-20261116-01`, with A's
direct layout and C's generation-managed layout. Ownership, modes and payloads were
checked. Final staged/input integrity, scope/cgroup isolation and residual-process
checks all passed. No runtime was removed or production installation changed.

## Verification and limits

Focused synthetic checks passed: 16 new runner/report/checker tests, 15 unchanged
helper preparation/analyzer tests and 24 unchanged recorder tests. New tests disable
process execution. They cover exact schedules and stop-before-next-launch failures,
invocation propagation, timestamps, host/boot agreement, missing boundaries and
operations, lifecycle separation, scheduler identity/lifetime/loss/coverage, partial
recorder cleanup, destination collisions, input drift, sealed blocked outcomes,
source/raw tampering and signed block-median comparisons. The existing recorder
regressions cover readiness, shared deadlines, forced reaping and workload-failure
cleanup. Independent verification passed for native build, blocked execution and
corrected offline replay. Documentation links and whitespace were checked. No broad
container suite was run.

The intended complete-run reports use per-variant/arm endpoint distributions and
per-block signed median differences, without subtracting overhead or comparing
cross-population quantiles. No such measured summaries exist for this attempt.
Inclusive spans and concurrent preparations are non-additive; clipped unions and
parent-exclusive intervals remain available in the partial accounting. Running time
would include instrumentation cost; non-runnable time identifies no blocking cause.
No captured helper evidence was collected, and runtime-generation identity remains
unproven. A separately authorized attempt would be needed to obtain the originally
intended measured population; this attempt is closed without a retry.


## Authorized rerun after the validator fix

The explicitly requested rerun used fresh destinations and the corrected tools.
The 16 focused synthetic tests and static preparation verification passed before
live actions. One new workload-free recorder rehearsal and all four fresh native
builds passed. The [build verification](../../build/preview-helper-startup-native-20261116-02-independent.json)
passed before execution. No tool or frozen source was changed during this attempt.

The [second execution](../../build/preview-helper-startup-execution-20261116-02/ASSESSMENT.md)
stopped **before invocation 1**, after staging four fresh runtimes: the next
integrity check found host dependency drift. All **36 invocations remain
unexecuted**, with zero warm-up or measured observations. The final scope and
residual-process checks passed; input integrity failed. The generic final failure
is `execution final cleanup/integrity failed`; its retained integrity detail is
`consumed input drift: /etc/ld.so.cache`.

A [sealed host-context audit](../../build/preview-helper-startup-host-drift-20261116-01/audit.json)
confirmed four consumed paths differ from the frozen preparation:

| Path | Expected SHA-256 | Observed SHA-256 |
|---|---|---|
| `/etc/ld.so.cache` | `fc8577afce2af118c20da76d796364e03d9bcd8ab3ceb25bcbe2ab496456ad6a` | `934a7d78c2dc82b4288fd1132c8fa6bceda664f1b89bef5f81b5e06c02eccadc` |
| `/usr/lib/ld-linux-x86-64.so.2` | `f5e11cc62f8f2c24dff532982559f4303dba3b17e7450551372a88c8e7ea8757` | `0460a979877b7d7c1524d800b38205b70a7b27b294f933f05cbc92a77890b3ff` |
| `/usr/lib/libc.so.6` | `02c8c3d06180beee9c7d0392aa85736c7d19f274a81e7f8f0b3d9e28e0641524` | `5884f2c5fdfcfca450fe536c1fba8c36d89d84fb0f851522078343b402bbccd9` |
| `/usr/lib/libm.so.6` | `965106704753eefe8c31ae7da6daba3ead3d18c52b19b5fcc41178bcc4aa999d` | `05ce19136f2bbf9c588abc4a747d09c3adb9a5a1216de344f2609cca50f262e8` |

The audit confirmed the preparation, build and execution evidence seals still
match, and all four retained protected runtime inventories match their staging
records. The runtime root is
`/run/holonight-helper-startup-preview-helper-startup-execution-20261116-02`.
The independent execution checker correctly [blocked](../../build/preview-helper-startup-execution-20261116-02-independent.json)
on consumed host-input drift, and [offline reporting](../../build/preview-helper-startup-report-20261116-05/ASSESSMENT.md)
blocked for the same reason. A passing evidence seal is distinct from matching the
frozen host inputs; it does not make this execution valid.

No cause for the host changes is established by this evidence. No dependencies
were restored, no frozen hashes were changed, and no automatic restart occurred.
A new preparation bound to the current host dependencies is required before
another valid attempt. Qualification remains failed at 78/80 gates, with no
optimization selected or measured comparison available.

## Host revision and captured-warm-up validator correction

The next requested fix created a new preparation rather than editing historical
hashes. The [host-rebinding tool](../../scripts/rebind-preview-helper-startup.py)
records the four old/new dependency hashes in `host-rebind.json`. The
[independent host-revision checker](../../scripts/verify-preview-helper-startup-host.py)
checks the original preparation seal and independent verification binding, every
unmodified consumed hash, original evidence inventories, exact source reconstruction,
probe ordering, source citations, fixture and protocol. Only the four reviewed host
paths may change. Historical packages and consumed tools remain unchanged.

The [new preparation](../../build/preview-helper-startup-20261116-06/ASSESSMENT.md)
passed [independent verification](../../build/preview-helper-startup-20261116-06-independent.json),
with four trees and 553 source citations. Its seal is
`a878737485e7f1fdd03f7e4991087e94d5c9bc504dd604db371fffc50b27cd5b`.
The [third native build](../../build/preview-helper-startup-native-20261116-03/ASSESSMENT.md)
and its [independent check](../../build/preview-helper-startup-native-20261116-03-independent.json)
passed after one workload-free recorder rehearsal.

The [third execution](../../build/preview-helper-startup-execution-20261116-03/ASSESSMENT.md)
passed baseline A/C and instrumented A/C warm-ups, then stopped at the captured A
warm-up with `incomplete required preparation scheduler coverage`. Five invocations
launched, four warm-ups were accepted, 31 invocations remained unexecuted and no
measured block ran. All final input integrity, scope, residual-process and staged
payload checks passed. The [execution verification](../../build/preview-helper-startup-execution-20261116-03-independent.json)
passed for the sealed blocked outcome.

Offline inspection found a validator defect: the inherited helper analyzer rejected
all scheduler spans whenever the global reconciler reported any issue, including
unrelated tasks with unknown startup states. The captured preparation thread itself
has complete known-state coverage. The new strict reporter now retains every global
warning and requires complete reconciliation for the actual required preparation
spans. Loss, incomplete export, diagnostics, identity disagreement, ambiguous
lifetimes and unknown time inside required spans still fail. The frozen analyzer
and scheduler reconciler were not changed.

The captured warm-up retained 65 global startup warnings. Its preparation span has
56,806,623 ns running, 35,782 ns runnable and 28,557,575 ns non-runnable time, totaling
85,399,980 ns with zero unknown time. These values describe one excluded warm-up;
they are not measured population summaries or evidence of an optimization benefit.
The [corrected offline replay](../../build/preview-helper-startup-report-20261116-06/REPORT.md)
replays all five retained invocations, and its
[independent check](../../build/preview-helper-startup-report-20261116-06-independent.json)
passes raw/source bindings and interval/scheduler arithmetic. The original execution
remains blocked and its tool snapshots remain sealed.

The focused suite now has 19 passing tests, adding strict host-revision checks and
a scheduler regression that accepts complete target coverage despite unrelated
startup warnings but rejects target unknown time, loss and incomplete export.
No production behavior, qualification thresholds or optimization choice changed.


## Completed fresh attempt

The explicitly authorized fresh attempt used the verified host-revised preparation
`preview-helper-startup-20261116-06` and both validator corrections. The 19 focused
synthetic tests and independent preparation verification passed before live work.
One workload-free recorder rehearsal and all four native builds passed in
[build 04](../../build/preview-helper-startup-native-20261116-04/ASSESSMENT.md), followed by
[independent build verification](../../build/preview-helper-startup-native-20261116-04-independent.json).

[Execution 04](../../build/preview-helper-startup-execution-20261116-04/ASSESSMENT.md)
completed all **36 invocations: six excluded warm-ups and 150 measured observations**.
All five rotating measured blocks completed without retries or protocol changes.
There are zero unexecuted rows. Every correctness, v3/v4 lifecycle, input/tool
integrity, scope/cgroup isolation, residual-process and staged-payload gate passed.
The four fresh root-owned runtimes remain under
`/run/holonight-helper-startup-preview-helper-startup-execution-20261116-04`.

[Offline report 07](../../build/preview-helper-startup-report-20261116-07/REPORT.md)
replayed all original samples, lifecycle records, supplemental spans and captured
scheduler exports. It contains **300 measured endpoints**, with warm-ups and setup
excluded from measured summaries. Its [accounting](../../build/preview-helper-startup-report-20261116-07/accounting.json)
retains source/raw citations, inclusive spans, clipped unions, parent-exclusive
intervals, separate lifecycle classifications and scheduler states. Unavailable
runtime-generation identity stays explicit. Complete scheduler coverage was required
for successful captured preparation spans; global startup warnings remain recorded.

Both [execution verification](../../build/preview-helper-startup-execution-20261116-04-independent.json)
and [report verification](../../build/preview-helper-startup-report-20261116-07-independent.json)
passed. The execution seal is
`b8b502390d2829cf3dbb6f8622a450bc3e74a9a9f89f6d37fd4696d7fa10576d`;
the report seal is
`63bbdd24f764a1d680a8d49ce942b5ecea305f29452a694e228d0d642c695c12`.
Report-action ledgers describe offline actions; the execution ledger is authoritative
for the 36 harness invocations and zero unexecuted rows.

### Captured preparation state coverage

The following shares divide the sum of recorded root preparation intervals by
scheduler state within each variant/lifecycle group. They describe thread time
across the group's preparations, not elapsed critical-path cost. Concurrent standby
work is separate and must not be added to selected demand as startup latency.
Every successful root in this table has zero unknown time.

| Variant and lifecycle | Successful preparations | Median root interval, ms | Running share | Runnable share | Non-runnable share |
|---|---:|---:|---:|---:|---:|
| A selected demand | 25 | 76.820 | 63.769% | 0.116% | 36.115% |
| C selected demand | 25 | 33.939 | 3.740% | 0.231% | 96.029% |
| C concurrent standby | 25 | 29.443 | 4.496% | 0.178% | 95.326% |

The exact state totals in ns are A demand: running 1,243,690,129, runnable 2,270,162,
non-runnable 704,348,571; C demand: running 29,920,552, runnable 1,849,081,
non-runnable 768,249,887; C standby: running 34,323,218, runnable 1,358,510,
non-runnable 727,675,483. Five exceptional C setup preparations are retained
separately and excluded from these groups and measured summaries. There is no
assumption that every observation has only one preparation.

A performs runtime validation inside the helper preparation boundary; C validates
its generation during owner initialization before resolving the helper lease.
The A/C preparation difference therefore does not isolate launcher work. Running
time includes instrumentation cost. Non-runnable time establishes no blocking cause.
No scheduler result identifies removable work or a predicted optimization benefit.

### Endpoint latency and arm comparisons

The [distributions](../../build/preview-helper-startup-report-20261116-07/distributions.json)
retain pooled and per-block values for both original endpoints, with 25 measured
observations per variant/arm. Pooled values in milliseconds are:

| Variant | Arm | Pixels median / p95 | Metadata median / p95 |
|---|---|---:|---:|
| A | baseline | 137.789 / 157.867 | 137.834 / 157.888 |
| A | instrumented | 138.753 / 167.488 | 138.785 / 167.520 |
| A | captured | 139.385 / 163.096 | 139.417 / 163.136 |
| C | baseline | 139.236 / 162.707 | 139.290 / 162.894 |
| C | instrumented | 134.312 / 151.540 | 134.346 / 151.720 |
| C | captured | 138.738 / 148.926 | 138.757 / 149.131 |

[Arm effects](../../build/preview-helper-startup-report-20261116-07/effects.json)
are signed differences of matched block medians, with no overhead subtraction or
cross-population quantile subtraction. The median of the five block differences
in milliseconds is:

| Variant | Comparison, right minus left | Pixels | Metadata |
|---|---|---:|---:|
| A | instrumented minus baseline | -1.449 | -1.456 |
| A | captured minus instrumented | -9.906 | -9.708 |
| C | instrumented minus baseline | -4.301 | -4.316 |
| C | captured minus instrumented | +5.619 | +5.615 |

These small diagnostic populations and rotating block differences are descriptive;
negative values do not establish negative instrumentation cost. They are not
qualification evidence or a significance test. No optimization is selected.
Qualification remains failed at **78/80** numerical gates under unchanged thresholds.
All historical evidence remains sealed. Documentation links and whitespace checks
passed; no broad container suite or production deployment was performed.

## Offline decision review

The subsequent [offline decision review](helper-startup-decision.md) reconstructs
endpoint startup windows and operation rankings from this sealed evidence without
running another experiment. Its independently verified decision is **Evidence
insufficient**: C's block rankings disagree, and uncovered startup time dominates
all required views. The completed diagnostic above remains historical evidence;
no optimization is selected and qualification remains failed at **78/80**.
