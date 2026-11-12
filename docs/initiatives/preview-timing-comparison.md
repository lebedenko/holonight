# Preview timings and corrected-reference qualification

## Native validation of reviewed v3 tracing overlays

**Native build validation passed for A/B/C/D.** The unchanged overlays compiled,
linked and privately installed against host dependencies; their installed-package
harnesses built successfully. Runtime staging, permitted protocol detection and
installation-time runtime verification passed. Static dependency, package-resolution,
trace-symbol and integrity checks passed. See the
[build assessment and retained evidence](../../build/preview-startup-native-validation-3wim1co2/ASSESSMENT.md).

This establishes build readiness only. No harness, preview workload, benchmark or
timing analysis ran. Qt callback behavior, runtime trace continuity, cancellation
interleavings and instrumentation overhead remain unverified. Qualification and
D's failed pilot remain unchanged. The source-readiness account below is historical.

## Reviewed startup tracing readiness

The [source-linked readiness assessment](../../build/preview-startup-tracing-v3-release-review/ASSESSMENT.md)
concludes **ready for native build validation**. Fresh A/B/C/D
[v3 private overlays](../../build/preview-startup-tracing-v3-release-review/README.md)
remain **uncompiled**. The review repaired stale callback context, premature job
allocation, preparation linkage and analyzer validation. D retains its frozen
deferral. [Exact diffs, inventories and invocation](../../build/preview-startup-tracing-v3-release-review/manifest.json)
are retained; previous preparations and assessments remain preserved.

The final [offline analysis](../../build/preview-startup-audit-v9/ASSESSMENT.md)
accounts for 1,600 diagnostic and 1,600 separate pilot observations, plus 16
warm-ups per mode, with zero analysis failures. C/D overlap reproduces
**400/400 and 0/400**. [Input hashes](../../build/preview-startup-audit-v9/input-manifest.json)
remain unchanged. The attribution audit retains 14,743 service-control/shutdown
spans and 1,232 setup spans separately. All 1,616 historical diagnostic
observations still lack explicit lifecycle identities and exact startup/full
construction boundaries; recovered associations depend on the frozen harness.
These counts do not establish a complete startup critical path.

V3 adds preparation identity and selected-worker linkage. Queued handoffs capture
context at scheduling; synchronous publication, transaction and readiness
callbacks inherit execution context. Startup origin, allocation plus complete
construction, constructor body and completion are distinct boundaries. The
analyzer validates identity claims, preserves partial accounting, clips phase
unions to delivery windows and reports unresolved overlap as unavailable.
Generation phases are absent by design only for A.

All 21 focused Python tests pass. Native compilation, Qt callback behavior,
logging effects and runtime interleavings remain unverified. **Qualification
and D's failed pilot remain unchanged.** No build, benchmark, diagnostic run,
production change, deployment or publication occurred. Native build validation
requires a separate decision; readiness does not authorize diagnostic execution.

## Fresh bounded scheduling comparison: unsuccessful pilot

A fresh preregistered diagnostic and one uninstrumented startup pilot completed
with all 3,200 measured observations valid, plus separate warm-ups. Correlated
standby preparation overlaps demand in 400/400 C jobs and 0/400 D jobs. Input
identities remain unchanged and no residual helper scopes remain. Earlier failed
runs and their execution markers are preserved.

D passes all eight unchanged startup allowances against contemporaneous A-fixed,
but fails the required large-PNG improvement over unchanged C:

| Large-PNG event | A-fixed p95 | C p95 | D p95 | D versus C |
| --- | ---: | ---: | ---: | ---: |
| pixels | 138.477 ms | 146.922 ms | 150.800 ms | +3.878 ms / +2.64% |
| final metadata | 138.507 ms | 146.928 ms | 150.809 ms | +3.881 ms / +2.64% |

The bounded cycle stops unsuccessfully. No production scheduling change, further
tuning, full qualification or resource rerun follows. Existing qualification remains
failed. Host-linked private overlays were built only where required; the pilot
reused matching A-fixed/B/C binaries. Preflight verified frozen sources and 451
binary/runtime/harness/fixture identities. All 40 tooling tests pass, and all seven
standby tests also pass through `sudo -A`, including ordinary-user artifact writes.

See the [assessment](../../build/preview-standby-drbq1ofy/ASSESSMENT.md),
[preregistration](../../build/preview-standby-drbq1ofy/preregistration.json),
[complete results and gates](../../build/preview-standby-drbq1ofy/result.json),
[diagnostic decision and traces](../../build/preview-standby-drbq1ofy/diagnostic-result.json)
and [preflight identities](../../build/preview-standby-drbq1ofy/preflight-identities.json).
Protected fixtures and all raw logs/observations remain retained. No samples were
replaced or previous execution markers reset.

## Initial standby contention diagnostic: inconclusive

The bounded follow-up stops before the startup pilot or a production correction.
Private instrumented native Release builds distinguish A-fixed, B, unchanged C and
D (C with initial standby deferral). Across 400 startup jobs each, unchanged C shows
standby preparation overlapping demand inspect/decode exchanges in 400/400 traces;
D shows 0/400. Exchange durations include transport overhead. This demonstrates
overlap and its removal, but does not establish a startup latency improvement.

The privileged runner created its observation directory without assigning ownership
to the ordinary benchmark user. All 176 harness invocations exited 5 when saving
JSON: **1,600 measured timing observations are missing**, plus separate warm-ups.
Every trace and failure is retained. Numerical medians, p95, absolute/percentage
improvements and startup gate results are unavailable. The run returned nonzero;
binary/fixture identities remained unchanged and no residual helper scopes remained.
Protected runtime fixtures are preserved. No samples were replaced or repeated.

The runner ownership correction passes seven tooling regressions, including a
privileged-wrapper/ordinary-user write test; 30 existing experiment-tooling tests
also pass. No pilot, production change or qualification run followed this invalid
diagnostic. Both previous failed comparisons remain unchanged and unqualified.

See the [diagnostic assessment](../../build/preview-standby-arb90t5w/ASSESSMENT.md),
[preregistered inputs](../../build/preview-standby-arb90t5w/preregistration.json),
[all failures and correlated traces](../../build/preview-standby-arb90t5w/result.json)
and [binary identities](../../build/preview-standby-arb90t5w/measurement-inputs.json).

## Corrected-reference comparison: qualification failed

**The cancellation/cleanup race is resolved in A-fixed, but strict qualification remains failed.** The single preregistered comparison collected all 12,000 observations (4,000 per variant), plus separate warm-ups, without correctness, protocol, cleanup or missing-observation failures. Of 80 numerical gates, 78 pass. Large textured PNG startup fails the p95 regression gate for both pixels and final metadata.

| Startup event, 3200×2400 PNG | A-fixed p95 | C p95 | Change | Allowed C p95 |
| --- | ---: | ---: | ---: | ---: |
| first_ms | 127.828 ms | 142.332 ms | +14.504 ms (+11.35%) | 140.611 ms |
| final_ms | 127.835 ms | 142.340 ms | +14.505 ms (+11.35%) | 140.619 ms |

The gate remains p95 regression ≤max(5 ms, 10%). No samples were replaced, no full comparison was rerun, and no allowance was changed. No further performance optimization is included.

A-fixed contains only the cancellation-order correction to original A: after launch starts, discover scope ownership before honoring cancellation, then check cancellation with the trusted gate still closed. Per-call validation, fresh-helper execution, startup deadlines and cleanup budgets remain unchanged. B and C source inventories, benchmark binaries and helper binaries match their original frozen identities. Host dependencies remain GCC 16.2.1, Qt 6.12.0, libexif 0.6.26 and libwebp 1.6.0.

Final metadata below is milliseconds, median / p95. **Original A** belongs to the earlier failed comparison; **A-fixed** is the corrected reference in the new run. Cross-run original-A/A-fixed shifts are descriptive, not a controlled measurement of the cancellation patch.

| Fixture / scenario | Original A (failed comparison) | A-fixed | C, new run | C−A-fixed median / p95 |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png/ready | 96.619 / 115.678 | 82.902 / 98.231 | 0.946 / 2.198 | -81.956 ms (-98.86%) / -96.033 ms (-97.76%) |
| 160x80.png/disk | 99.301 / 120.906 | 85.041 / 104.376 | 1.560 / 2.520 | -83.480 ms (-98.17%) / -101.857 ms (-97.59%) |
| 160x80.png/memory | 0.330 / 0.508 | 0.325 / 0.385 | 0.326 / 0.509 | +0.001 ms (+0.23%) / +0.124 ms (+32.21%) |
| 160x80.png/startup | 99.878 / 116.096 | 89.426 / 108.541 | 85.857 / 102.588 | -3.569 ms (-3.99%) / -5.953 ms (-5.48%) |
| 1600x1200.png/ready | 101.012 / 120.900 | 96.583 / 111.005 | 6.256 / 13.112 | -90.326 ms (-93.52%) / -97.893 ms (-88.19%) |
| 1600x1200.png/disk | 95.496 / 115.016 | 88.380 / 104.348 | 1.855 / 2.892 | -86.526 ms (-97.90%) / -101.456 ms (-97.23%) |
| 1600x1200.png/memory | 0.321 / 0.510 | 0.316 / 0.414 | 0.315 / 0.364 | -0.001 ms (-0.21%) / -0.050 ms (-12.14%) |
| 1600x1200.png/startup | 100.039 / 122.442 | 101.773 / 116.616 | 99.810 / 112.788 | -1.962 ms (-1.93%) / -3.828 ms (-3.28%) |
| 3200x2400.png/ready | 130.767 / 153.037 | 120.413 / 134.930 | 36.523 / 40.417 | -83.890 ms (-69.67%) / -94.514 ms (-70.05%) |
| 3200x2400.png/disk | 96.532 / 119.613 | 81.663 / 95.940 | 3.681 / 5.118 | -77.981 ms (-95.49%) / -90.822 ms (-94.67%) |
| 3200x2400.png/memory | 0.194 / 0.354 | 0.174 / 0.380 | 0.180 / 0.346 | +0.005 ms (+3.07%) / -0.034 ms (-8.91%) |
| 3200x2400.png/startup | 127.800 / 148.996 | 116.040 / 127.835 | 119.518 / 142.340 | +3.478 ms (+3.00%) / +14.505 ms (+11.35%) |
| oriented.jpg/ready | 93.689 / 115.271 | 84.455 / 106.271 | 0.971 / 2.085 | -83.484 ms (-98.85%) / -104.186 ms (-98.04%) |
| oriented.jpg/disk | 98.135 / 122.370 | 86.816 / 105.624 | 1.742 / 2.489 | -85.074 ms (-97.99%) / -103.135 ms (-97.64%) |
| oriented.jpg/memory | 0.181 / 0.348 | 0.179 / 0.345 | 0.179 / 0.338 | +0.000 ms (+0.18%) / -0.006 ms (-1.79%) |
| oriented.jpg/startup | 95.834 / 109.713 | 87.058 / 104.739 | 91.035 / 109.068 | +3.977 ms (+4.57%) / +4.328 ms (+4.13%) |

Lightweight ready previews and every disk-hit gate pass. The large textured ready decode remains separately reported; its disk hits are still gated. Memory, recycling, cancellation-depletion and every navigation regression gate pass.

Separate C resource diagnostics pass: at most 2 helpers, 6.836 MiB retained idle scope memory (≤64 MiB), idle expiry without replacement, 14 observed workers across recycling, and complete shutdown. Its protected generation contains 61 files / 87,221,117 bytes. A-fixed’s separate lifecycle/resource diagnostic also passes: at most one helper, zero retained idle scope memory, bounded runtime storage and complete shutdown. Existing generation-bound and candidate integration evidence is reused after identity verification. Native interactive presentation and low-end hardware remain outside qualification.

Ten assessment regressions and nine A-fixed provider/installed-package checks pass. Native runtime fault checks pass. Separate deterministic cancellation diagnostics reproduce original A’s empty-scope-identity cleanup failure and post-discovery gate write; A-fixed passes cancellation before launch, between launch and discovery, and immediately after discovery, with zero gate writes, exactly one cleanup after launch, and failure precedence for unverified cleanup.

**Evidence retention:** the new run’s saved runner returned failure for the numerical gates, but removed its transient `/run` runtime root after successful execution and before numerical assessment. The frozen source/runtime inputs and every raw observation remain intact. The final tooling now assesses numerical gates before fixture removal; a regression verifies preservation and failing exit status without discarding valid numerical distributions. This tooling correction does not change or rerun the frozen experiment. Original failed fixtures and the original failed comparison remain unchanged.

- [New frozen comparison, including every absolute and percentage change](../../build/preview-corrected-qjln5jn4/reuse-measurement-d0nbnsxc/comparison.md), [raw summary](../../build/preview-corrected-qjln5jn4/reuse-measurement-d0nbnsxc/summary.json), [provenance](../../build/preview-corrected-qjln5jn4/reuse-measurement-d0nbnsxc/provenance.json).
- [Preregistered protocol](../../build/preview-corrected-qjln5jn4/PREREGISTRATION.md), [frozen source inventories and build environment](../../build/preview-corrected-qjln5jn4/freeze.json), [baseline patch audit](../../build/preview-corrected-qjln5jn4/baseline-diff-audit.json), [post-run identity checks](../../build/preview-corrected-qjln5jn4/post-run-identity-checks.json).
- [Cancellation diagnostics](../../build/preview-corrected-qjln5jn4/cancellation-diagnostics-v3.jsonl), [native fault checks](../../build/preview-corrected-qjln5jn4/native-runtime-faults.log), [C resource diagnostics](../../build/preview-corrected-qjln5jn4/resources-C/summary.json), [A-fixed resource diagnostics](../../build/preview-corrected-qjln5jn4/resources-A-fixed/summary.json).

No deployment, publication, umbrella pin changes or unrelated GRUB changes were made. **Neither original A nor the corrected-reference comparison is qualified.**

## Original frozen comparison (failed)

Date: 2026-11-12. All times are **milliseconds, median / p95**. These measure service pixel delivery and final source metadata, not a painted QML frame.

## Summary

Isolation initially added substantial preview overhead. The transaction implementation immediately before the latest work still needed roughly **94–131 ms median** for a ready source preview and **95–99 ms** for disk hits. The current reusable-worker implementation reduces these to **1.2–6.7 ms** for lightweight ready previews and **1.7–3.9 ms** for disk hits. The textured large-image source decode remains about **36 ms**.

Warm ready previews are now in the same millisecond range as the historical in-process implementation. **Genuine startup remains roughly 94–137 ms median**, because validation and first-worker creation still have to occur.

## What the three stages mean

| Stage | Implementation | Evidence |
| --- | --- | --- |
| Before isolation | Historical in-process decoder, with no sandbox/helper | Historical transaction comparison, variant A |
| Before latest improvements | Isolated source transaction; repeated runtime validation and a fresh helper per transaction | Latest frozen comparison, variant A |
| Current | Protected generation validation reuse, reusable helpers and the two-slot preview scheduler | Latest frozen comparison, variant C |

Each displayed distribution has **100 successful observations**. Fixture hashes match across both runs. Recorded native Release build inputs also match: **GCC 16.2.1, Qt 6.12.0, libexif 0.6.26 and libwebp 1.6.0**. Both comparisons used separate warm-ups and alternating blocks of ten. Host page caches were not flushed.

The historical and latest harnesses differ: historical `first` is a first request with service construction outside timing; current `ready` explicitly warms a worker with another source. Therefore the historical first-request column is context, **not a controlled three-way ready-worker experiment**. Disk and memory cases represent the corresponding cache paths, but cross-run differences still should not be interpreted as precise causal savings. The before-latest/current pair uses the same latest harness.

## Pixels: source previews

Historical first-request timings versus latest ready-preview timings; construction is outside these measurements.

| Fixture | Before isolation: first | Before latest: ready | Current: ready | Median reduction vs before latest |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png | 2.168 / 3.756 | 96.596 / 115.667 | 1.833 / 3.147 | 94.763 ms (98.1%) |
| 1600x1200.png | 12.107 / 18.587 | 101.000 / 120.886 | 6.645 / 14.427 | 94.356 ms (93.4%) |
| 3200x2400.png | 35.447 / 41.871 | 130.759 / 153.022 | 36.144 / 41.853 | 94.615 ms (72.4%) |
| oriented.jpg | 1.235 / 2.315 | 93.584 / 115.246 | 1.240 / 2.456 | 92.344 ms (98.7%) |

The 3200×2400 texture is source-decode work, reported separately from the lightweight ready-preview target.

## Pixels: disk-cache hits

| Fixture | Before isolation | Before latest | Current | Median reduction vs before latest |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png | 1.233 / 1.757 | 99.283 / 120.895 | 1.734 / 2.755 | 97.550 ms (98.3%) |
| 1600x1200.png | 1.416 / 2.096 | 95.478 / 114.992 | 2.016 / 3.403 | 93.462 ms (97.9%) |
| 3200x2400.png | 1.975 / 2.305 | 96.522 / 119.590 | 3.839 / 4.610 | 92.684 ms (96.0%) |
| oriented.jpg | 0.934 / 1.446 | 98.116 / 122.191 | 1.836 / 2.981 | 96.280 ms (98.1%) |

## Pixels: decoded-memory hits

| Fixture | Before isolation | Before latest | Current | Current − before latest, median / p95 |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png | 0.162 / 0.341 | 0.320 / 0.478 | 0.309 / 0.451 | -0.010 / -0.028 ms |
| 1600x1200.png | 0.161 / 0.345 | 0.314 / 0.487 | 0.278 / 0.469 | -0.036 / -0.019 ms |
| 3200x2400.png | 0.311 / 0.470 | 0.167 / 0.329 | 0.308 / 0.332 | +0.141 / +0.003 ms |
| oriented.jpg | 0.159 / 0.217 | 0.170 / 0.330 | 0.172 / 0.331 | +0.002 / +0.001 ms |

Memory hits are sub-millisecond. Absolute differences are more useful here than percentages.

## Final source metadata

Final metadata follows pixels and includes source dimensions and EXIF. The source/ready comparability caveat above also applies here.

| Fixture | Case | Before isolation | Before latest | Current |
| --- | --- | ---: | ---: | ---: |
| 160x80.png | first / ready | 2.171 / 3.792 | 96.619 / 115.678 | 1.840 / 3.166 |
| 160x80.png | disk | 1.237 / 1.807 | 99.301 / 120.906 | 1.747 / 2.769 |
| 160x80.png | memory | 0.163 / 0.343 | 0.330 / 0.508 | 0.316 / 0.469 |
| 1600x1200.png | first / ready | 12.111 / 18.591 | 101.012 / 120.900 | 6.661 / 14.441 |
| 1600x1200.png | disk | 1.418 / 2.099 | 95.496 / 115.016 | 2.026 / 3.562 |
| 1600x1200.png | memory | 0.161 / 0.433 | 0.321 / 0.510 | 0.284 / 0.471 |
| 3200x2400.png | first / ready | 35.449 / 41.878 | 130.767 / 153.037 | 36.155 / 41.859 |
| 3200x2400.png | disk | 1.989 / 2.306 | 96.532 / 119.613 | 3.849 / 4.619 |
| 3200x2400.png | memory | 0.313 / 0.470 | 0.194 / 0.354 | 0.314 / 0.344 |
| oriented.jpg | first / ready | 1.325 / 2.472 | 93.689 / 115.271 | 1.248 / 2.467 |
| oriented.jpg | disk | 1.044 / 1.602 | 98.135 / 122.370 | 1.846 / 3.005 |
| oriented.jpg | memory | 0.161 / 0.337 | 0.181 / 0.348 | 0.180 / 0.340 |

## Genuine startup: not the ready-worker path

The latest startup scenario starts timing **before service construction**. The older pre-isolation run did not measure this equivalent scenario, so that value is unavailable rather than inferred.

| Fixture | Before isolation | Before latest: final metadata | Current: final metadata | p95 change |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png | Not measured | 99.878 / 116.096 | 97.631 / 113.902 | -2.194 ms (-1.9%) |
| 1600x1200.png | Not measured | 100.039 / 122.442 | 101.242 / 122.909 | +0.466 ms (+0.4%) |
| 3200x2400.png | Not measured | 127.800 / 148.996 | 136.716 / 161.171 | +12.175 ms (+8.2%) |
| oriented.jpg | Not measured | 95.834 / 109.713 | 94.089 / 113.512 | +3.799 ms (+3.5%) |

## Qualification and limitations

- Current and protected one-shot variants each recorded **4,000 successful observations** across the full latest matrix. All calculated numerical gates pass. Lightweight ready and every disk-hit case meet median ≤30 ms / p95 ≤50 ms.
- Across pixels and metadata, maximum memory-hit median/p95 regressions are **0.141 / 0.003 ms**. The largest startup p95 regression is **8.171%**, within the 10% allowance for that fixture.
- **Strict overall qualification remains incomplete.** The frozen before-latest baseline recorded **eight cleanup-flagged observations and 17 missing placeholders** in PNG navigation at 100-ms intervals. These are outside the successful ready/disk/memory/startup rows above, but leave the full navigation reference unqualified. None were removed or replaced.
- The earlier historical transaction run had no missing/failed qualifying observations, but its own strict acceptance gate failed because of small memory-hit p95 regressions. It is historical evidence, not a retrospective pass.
- No equivalent pre-isolation samples exist for the latest startup, recycling, cancellation-depletion or interval-navigation scenarios. Historical burst timings are not substituted for them.
- These are host-native service measurements; native interactive presentation and low-end hardware performance are not qualified.

## Source evidence

- [Historical before-isolation and transaction comparison](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/comparison-final.md), [raw summary](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/summary.json), [provenance](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/provenance.json).
- [Latest full comparison](../../build/preview-reuse-dgi4528s/reuse-measurement-ml9f0eu3/comparison.md), [raw summary](../../build/preview-reuse-dgi4528s/reuse-measurement-ml9f0eu3/summary.json), [provenance](../../build/preview-reuse-dgi4528s/reuse-measurement-ml9f0eu3/provenance.json).
- [Implementation, resource and verification assessment](../../build/preview-reuse-dgi4528s/ASSESSMENT.md).
- [Current cross-project contract and assessment](immutable-runtime-standby.md).

## Bounded v3 runtime tracing smoke

**Corrected smoke run passed:** all 12 fixed startup invocations across A/B/C/D
and the three fixtures passed, covering 36 observations and 48 service lifetimes
including setup. There were zero parser, identity, accounting or lifecycle issues,
no timeouts or residual helper scopes, and retained-input and staged-runtime
payload integrity passed after execution. No retries or replacement observations
were used. See the [fresh assessment](../../build/preview-startup-runtime-smoke-20261112-v3-02/assessment.json),
[preregistration](../../build/preview-startup-runtime-smoke-20261112-v3-02/preregistration.json)
and [per-invocation evidence](../../build/preview-startup-runtime-smoke-20261112-v3-02/observations/).

The corrected runner uses a paired `service_destruction` end as completion of the
destructor's cleanup path. The retained destructors wait for worker cleanup and
do not require a call to the separate `shutdown()` method. Any `service_shutdown`
records that are present must still pass pairing, identity, role and ordering
checks. Twelve focused runner tests passed under the privileged wrapper, including
ordinary-user output ownership and regressions for destructor-only completion,
incomplete cleanup and attribution to another lifetime. No native sources,
binaries or runtime bundles were rebuilt or modified. The earlier 21 Python
results were reused after verifying their recorded inputs remained unchanged.
Success is limited to these startup/shutdown executions; cancellation, overhead,
performance and broader qualification remain unverified, and D's failed pilot is
unchanged.

The earlier blocked run is retained unchanged below.

**Runtime tracing smoke validation blocked.** The fixed run stopped after its first
invocation, A / `160x80.png` / `startup` / count 3. All three observations passed
pixel/metadata validation and v3 trace association, with zero parser, identity or
accounting issues. All four services (setup included) had balanced construction
and destruction spans, but no `service_shutdown` records; the runner's explicit
shutdown-completion requirement therefore failed for all four lifetimes. No later
invocations, retries or replacement observations ran.

The harness exited zero without timeout. Scope snapshots found no remaining
helpers, and post-run checks confirmed retained-input and staged-runtime payload
integrity. Runtime fixtures and partial evidence remain preserved. See the
[assessment and first failing command](../../build/preview-startup-runtime-smoke-20261112-v3-01/assessment.json),
[preregistration](../../build/preview-startup-runtime-smoke-20261112-v3-01/preregistration.json)
and [trace accounting and lifecycle checks](../../build/preview-startup-runtime-smoke-20261112-v3-01/observations/A-160x80.png.accounting.json).
The runner and focused synthetic tests add no production changes. The retained
21 Python results remain applicable because their recorded inputs are unchanged.
This result makes no performance, cancellation, overhead or qualification claim;
D's failed pilot and existing qualification limits remain unchanged.

## Bounded C/D cancellation tracing diagnostic

**Cancellation tracing validation blocked.** The preregistered 24-invocation matrix
stopped after C / preparation / repetition 1. The harness exited zero, acknowledged
all required preparation barriers, verified cancelled preparation cleanup without
readiness/gate opening, and confirmed correct replacement pixels, oriented dimensions
and full formatted EXIF. Its only ledger issue was `replacement_delivery`: the
accepted-result probe requires a non-null image to label a callback successful,
while the final accepted metadata callback carries no image payload. This diagnostic
classification limitation prevents a pass; it does not establish a production defect.
No overlay or expectation was repaired after execution began, and the remaining
23 invocations, including all D and destruction/active/cleanup cases, did not run.

Both private C/D provider/harness builds passed against host dependencies. Fourteen
focused synthetic Python tests and four native barrier/supervisor checks without
helpers passed. The unchanged v3 parser/identity checks and the single service's
construction/destruction checks passed. Ordinary-user output ownership was verified
under the privileged wrapper; scope snapshots found no residual helpers, cleanup
was verified, and post-run retained-input/private-artifact and staged-runtime payload
integrity passed. Historical packages, both startup-smoke runs and runtime fixtures
remain preserved. This result provides no performance, overhead or qualification claim.

See the [final assessment](../../build/preview-cancellation-tracing-wxuflfvn/FINAL-ASSESSMENT.md),
[preregistration](../../build/preview-cancellation-tracing-wxuflfvn/execution/preregistration.json),
[first failing command](../../build/preview-cancellation-tracing-wxuflfvn/execution/assessment.json),
[overlay review](../../build/preview-cancellation-tracing-wxuflfvn/review.json),
and [invocation evidence](../../build/preview-cancellation-tracing-wxuflfvn/execution/observations/).

## Corrected C/D cancellation diagnostic

**Cancellation tracing validation blocked.** The metadata-only final-result probe
was corrected to classify runtime/raster/error status independently of image payload.
The new ledger checks join publication, application attempt and acceptance by
observed identity/selection/payload, and require successful pixels before final
metadata. Preparation/build tooling now automatically verifies the focused tests,
records commands and seals artifact/tool identities before execution.

A fresh fixed matrix passed all nine C preparation, active-cancellation and
replacement-during-cleanup invocations. It stopped at C destruction repetition 1:
the supervisor thread's `active_release` diagnostic row had service ID 0 because
its thread-local tracing context was not propagated. The separate ledger validator
reported `foreign_diagnostic_service`. The harness exited zero, both requests
avoided successful delivery and cleanup passed; this diagnostic attribution failure
does not establish a production destruction defect. No repair, changed expectation
or retry followed. The remaining 14 invocations, including all D cases, did not run.

Both fresh private native builds, 18 focused Python tests and five helper-free C++
checks passed. All 10 harnesses exited zero with no timeouts, and their v3 TRACE
parsing/pairing/identity and service-lifecycle checks passed. Observed totals are
10 service lifetimes, 11 cancelled requests and nine recoveries; the complete
24-invocation requirements remain unmet. Ordinary-user ownership, helper-scope
cleanup, retained/private-artifact integrity and staged-runtime payload integrity
passed. All 20 runtime fixture copies match retained provenance; the earlier failed
package and both startup-smoke runs remain unchanged. No performance, overhead or
qualification claim follows.

See the [corrected-run assessment](../../build/preview-cancellation-tracing-837893f4/FINAL-ASSESSMENT.md),
[preregistration](../../build/preview-cancellation-tracing-837893f4/execution/preregistration.json),
[first failing command](../../build/preview-cancellation-tracing-837893f4/execution/assessment.json),
[review](../../build/preview-cancellation-tracing-837893f4/review.json),
[focused verification](../../build/preview-cancellation-tracing-837893f4/verification.json),
and [final counts and integrity evidence](../../build/preview-cancellation-tracing-837893f4/final-validation-summary.json).

## Supervisor-context C/D cancellation validation

**Cancellation tracing validation passed.** The private diagnostic supervisor now
binds a context captured by value on the service-owning thread immediately before
thread creation. The shared harness/native-test helper matches cancelled destructor
acknowledgement by service and observation, preserves the remaining captured fields,
and records its actual thread ID. Missing context or acknowledgement fails and
releases all gates. The production diagnostic deadline remains one second;
destructor ownership, event processing, cleanup, the v3 header, metadata-success
classification and strict ledger acceptance remain unchanged. No public API or
production source was changed.

Both fresh private C/D builds passed against host dependencies, sequentially with
four compilation jobs and private installed prefixes. Nineteen focused Python
regressions and nine helper-free native checks passed before provider builds,
including context restoration, foreign service/observation rejection, uncancelled
acknowledgement rejection, missing context, timeout and safe gate release.

All 24 preregistered invocations passed in the fixed C-then-D scenario order:
24 balanced service lifetimes, 30 cancelled/superseded requests and 18 successful
recoveries. All six real destruction supervisor handoffs preserve service and
observation, use a distinct thread, and order cancellation before release before
active-worker resumption. Identity, lifecycle, cleanup and content checks passed;
there were no timeouts, repairs, expectation changes, retries or replacement
executions after the marker. The initial sudo authentication failure created no
marker or invocation; execution proceeded with sudo -A.

Ordinary-user ownership, private caches/fixtures, clean helper scopes, retained
input/private-artifact integrity and staged-runtime payload integrity passed.
All 48 preserved fixture copies match retained provenance. Both earlier blocked
packages remain byte-for-byte unchanged. Historical analyzer, preparation and
startup results were reused; holonight-icons and holonight-grub were excluded.
This validates only the forced cancellation interleavings and makes no performance,
overhead or qualification claim. No deployment, publication or commit follows.

See the [final assessment](../../build/preview-cancellation-supervisor-20261112/FINAL-ASSESSMENT.md),
[preregistration](../../build/preview-cancellation-supervisor-20261112/execution/preregistration.json),
[runner assessment](../../build/preview-cancellation-supervisor-20261112/execution/assessment.json),
[review](../../build/preview-cancellation-supervisor-20261112/review.json),
[focused verification](../../build/preview-cancellation-supervisor-20261112/verification.json),
[final counts and integrity](../../build/preview-cancellation-supervisor-20261112/final-validation-summary.json),
and [blocked-package identities](../../build/preview-cancellation-supervisor-20261112/blocked-package-identities.json).


## Matched v3 startup tracing overhead

**Measurement complete.** All 264 preregistered invocations completed: 2,400
measured observations and 24 separate warm-ups. Nine focused synthetic tests passed
before the eight fresh host builds, which ran sequentially A/U through D/T with
four compilation jobs and separate installed prefixes. Installed-package linkage
checks passed. Replaying the retained phase and v3 preparers against frozen
untraced copies reproduced every reviewed traced source and harness after
normalizing only package-local `trace.h` include paths. Both harness modes preserve
private fixture/cache directories identically; setup, correctness checks, timer
placement and delivery timestamps retain the same boundaries. A denotes A-fixed;
U is untraced and T uses the full reviewed v3 instrumentation.

All pixel, metadata, delivery-order, completion and cleanup checks passed. T had
zero parser, identity, accounting or lifecycle issues, with 1,344 balanced service
lifetimes including setup services; U emitted no TRACE records. Ordinary-user
ownership, clean helper scopes, retained-input/private-artifact integrity and
protected staged-payload integrity passed. All 21,504 preserved fixture copies
match retained provenance. The successful startup/cancellation evidence and both
blocked cancellation packages remain unchanged. No timeout, repair, expectation
change, retry or replacement execution occurred after the marker.

The table reports milliseconds and signed `T−U` differences; percentages are
relative to U. Median and nearest-rank p95 use 100 measured samples per cell,
excluding warm-ups. Exact values and all ten per-block comparisons are retained
in the statistics artifact. A zero-baseline percentage would be unavailable.

| Variant | Fixture | Event | U median ms | T median ms | T−U ms | T−U % | U p95 ms | T p95 ms | T−U ms | T−U % |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 160x80.png | pixels | 94.583 | 91.296 | -3.287 | -3.475 | 147.838 | 125.751 | -22.086 | -14.939 |
| A | 160x80.png | final metadata | 94.611 | 91.320 | -3.291 | -3.478 | 147.863 | 125.779 | -22.084 | -14.935 |
| B | 160x80.png | pixels | 94.450 | 93.137 | -1.313 | -1.390 | 167.066 | 124.945 | -42.120 | -25.212 |
| B | 160x80.png | final metadata | 94.460 | 93.159 | -1.301 | -1.378 | 167.082 | 125.166 | -41.916 | -25.087 |
| C | 160x80.png | pixels | 89.777 | 88.223 | -1.554 | -1.731 | 124.020 | 110.694 | -13.326 | -10.745 |
| C | 160x80.png | final metadata | 89.796 | 88.247 | -1.549 | -1.726 | 124.038 | 110.886 | -13.151 | -10.603 |
| D | 160x80.png | pixels | 89.205 | 88.036 | -1.169 | -1.310 | 110.244 | 110.966 | +0.722 | +0.655 |
| D | 160x80.png | final metadata | 89.219 | 88.069 | -1.151 | -1.290 | 110.274 | 111.005 | +0.731 | +0.663 |
| A | 3200x2400.png | pixels | 141.323 | 137.757 | -3.566 | -2.523 | 247.893 | 370.144 | +122.251 | +49.316 |
| A | 3200x2400.png | final metadata | 141.334 | 137.777 | -3.557 | -2.517 | 247.910 | 370.188 | +122.279 | +49.324 |
| B | 3200x2400.png | pixels | 133.031 | 131.732 | -1.298 | -0.976 | 166.232 | 155.365 | -10.867 | -6.537 |
| B | 3200x2400.png | final metadata | 133.050 | 131.751 | -1.299 | -0.976 | 166.241 | 155.391 | -10.850 | -6.527 |
| C | 3200x2400.png | pixels | 128.344 | 125.847 | -2.497 | -1.945 | 153.211 | 155.204 | +1.993 | +1.301 |
| C | 3200x2400.png | final metadata | 128.381 | 125.862 | -2.519 | -1.962 | 153.244 | 155.225 | +1.982 | +1.293 |
| D | 3200x2400.png | pixels | 130.331 | 135.127 | +4.795 | +3.679 | 159.798 | 160.256 | +0.458 | +0.287 |
| D | 3200x2400.png | final metadata | 130.345 | 135.224 | +4.879 | +3.743 | 159.925 | 160.274 | +0.349 | +0.218 |
| A | oriented.jpg | pixels | 89.955 | 94.005 | +4.050 | +4.502 | 151.720 | 130.550 | -21.170 | -13.953 |
| A | oriented.jpg | final metadata | 89.977 | 94.028 | +4.050 | +4.502 | 151.773 | 130.603 | -21.170 | -13.949 |
| B | oriented.jpg | pixels | 89.295 | 87.451 | -1.844 | -2.065 | 124.937 | 121.265 | -3.672 | -2.939 |
| B | oriented.jpg | final metadata | 89.367 | 87.473 | -1.894 | -2.119 | 124.952 | 121.289 | -3.664 | -2.932 |
| C | oriented.jpg | pixels | 88.372 | 85.080 | -3.292 | -3.725 | 211.049 | 164.996 | -46.053 | -21.821 |
| C | oriented.jpg | final metadata | 88.466 | 85.094 | -3.371 | -3.811 | 211.071 | 165.019 | -46.052 | -21.818 |
| D | oriented.jpg | pixels | 89.206 | 84.403 | -4.803 | -5.385 | 144.162 | 99.664 | -44.498 | -30.866 |
| D | oriented.jpg | final metadata | 89.218 | 84.424 | -4.794 | -5.373 | 144.186 | 99.676 | -44.511 | -30.870 |

These are descriptive host measurements without a statistical-significance claim
or numerical overhead budget. Negative differences are retained. The comparison
covers full v3 bookkeeping and logging inside the existing measured startup
window; pre-timer work and total lifecycle cost are outside it. A read-only
historical integrity audit also ran during the small-PNG measured blocks, around
invocations 59–70, as recorded in the execution-context evidence. No values are
subtracted from trace phases, and these results do not provide a causal
explanation of earlier performance failures. D remains the frozen deferral
variant; its failed pilot and existing qualification are unchanged.

The sandbox's final ownership audit saw protected root-owned paths as UID 65534.
The unchanged read-only audit passed against the host filesystem view, confirming
UID 0 and protected modes; its earlier sandbox result is preserved. This repeated
no harness invocation. The initial sandboxed sudo failure occurred before provider
builds or the execution marker. No production/public API change, deployment,
publication, umbrella-pin update, automatic commit or follow-on experiment occurred.

See the [complete report](../../build/preview-tracing-overhead-20261112/FINAL-ASSESSMENT.md),
[exact statistics and per-block differences](../../build/preview-tracing-overhead-20261112/execution/statistics.json),
[preregistration and all commands](../../build/preview-tracing-overhead-20261112/execution/preregistration.json),
[runner assessment](../../build/preview-tracing-overhead-20261112/execution/assessment.json),
[equivalence proof](../../build/preview-tracing-overhead-20261112/equivalence.json),
[preparation and harness review](../../build/preview-tracing-overhead-20261112/preparation.json),
[focused test output](../../build/preview-tracing-overhead-20261112/focused-tests.log),
[build commands](../../build/preview-tracing-overhead-20261112/build-commands.json),
[environment and dependencies](../../build/preview-tracing-overhead-20261112/environment.json),
[pre-execution seal](../../build/preview-tracing-overhead-20261112/seal.json),
[retained input and protected-runtime inventories](../../build/preview-tracing-overhead-20261112/retained-before.json),
[final counts, ownership and fixture provenance](../../build/preview-tracing-overhead-20261112/final-validation-summary.json),
[execution context and supplementary integrity verification](../../build/preview-tracing-overhead-20261112/supplementary-retained-verification.json),
and [preserved sandbox ownership audit](../../build/preview-tracing-overhead-20261112/sandbox-final-validation-summary.json).

### Offline retained v3 startup accounting (2026-11-12)

The [standalone assessment](../../build/preview-startup-v3-analysis-20261112-02/ASSESSMENT.md)
reparsed the retained overhead package without executing native workloads. All 264
preregistered invocations reconciled: each mode has 1,200 measured observations
and 12 warm-ups; T has 1,344 service lifetimes, including 132 setup services.
Raw stderr line references, semantic accounting and lifecycle results agree with
retained validation. Consumed evidence hashes and recorded tool identities passed;
[before/after hashes](../../build/preview-startup-v3-analysis-20261112-02/input-integrity.json)
are unchanged, with no [attribution or integrity issues](../../build/preview-startup-v3-analysis-20261112-02/attribution-issues.json).

Pixel and metadata windows start at the explicit startup origin and end at their
respective trace probes. These differ from harness timer latencies: origin precedes
timer start and probes follow latency capture. The
[pooled and block summaries](../../build/preview-startup-v3-analysis-20261112-02/phase-summary.json)
retain phase presence and median/nearest-rank p95 durations, full construction and
constructor-body boundaries, coverage unions, unnamed gaps and identity-linked
standby overlap. Inclusive phase durations are not additive. Broad job, dispatch
and lifecycle envelopes are excluded from coverage; missing phases remain
unavailable and A's generation phases remain absent by design. U supplies latency
context without trace identities or phase estimates. Warm-ups,
[setup activity](../../build/preview-startup-v3-analysis-20261112-02/setup-activity.json),
service-control work and post-delivery cleanup remain distinguishable in the
[per-observation accounting](../../build/preview-startup-v3-analysis-20261112-02/accounting.json).

All five selected A large-PNG tails for each endpoint came from block 9. The
slowest pixel observation (sample 0) had a 510.112 ms origin-to-probe window,
376.625 ms covered union and 133.487 ms unnamed elapsed time; its final-metadata
window was 510.144 ms with 133.520 ms unnamed. Its helper preparation lasted
215.702 ms and decode exchange including transport lasted 122.123 ms, while
runtime validation was nested inside preparation. These inclusive intervals do
not partition the delay. The slowest B/C/D pixel windows were respectively
175.355/175.977/169.806 ms, with 20.767/23.054/19.299 ms unnamed. The
[five tails per variant and endpoint](../../build/preview-startup-v3-analysis-20261112-02/tails.json)
and assessment preserve origin-relative timelines, readiness/delivery markers,
roles, gaps and raw line links.

C had observed standby-preparation overlap with demand exchanges in all 300
measured observations for each endpoint; D had none before either delivery.
These counts describe this corpus, without requiring historical overlap counts
to recur. Exchange intervals include transport. Neither these observations,
phase quantiles nor T/U differences explain causality or CPU cost; gaps remain
unexplained elapsed time. The
[completed overhead report](../../build/preview-tracing-overhead-20261112/FINAL-ASSESSMENT.md)
and its host-activity limitation still apply. No overhead was subtracted, no
threshold introduced, and C's failed qualification and D's failed pilot remain
unchanged. No follow-on experiment is prescribed.

The new offline adapter and six focused regressions passed. Historical tools were
reused only after their recorded hashes matched. No native builds, benchmarks,
deployment, publication, pin changes or commits were performed. Earlier assessments
remain unchanged.

### Offline retained v3 delivery-gap audit (2026-11-12)

The [delivery-gap assessment](../../build/preview-delivery-gaps-v3-analysis-20261112-05/ASSESSMENT.md)
reconciles all 264 invocations, 2,424 observations and 1,344 traced service
lifetimes with the completed startup analysis. The unchanged historical parser
and lifecycle validation were reused after recorded tool identities matched.
All observations and streams passed retained hashes; the frozen source files
passed package inventories. The [input-integrity record](../../build/preview-delivery-gaps-v3-analysis-20261112-05/input-integrity.json)
records 1,119 consumed input/tool hashes before and after, unchanged.

The [source-path map](../../build/preview-delivery-gaps-v3-analysis-20261112-05/source-path-map.json)
inspects A/B/C/D independently, retaining hashes, line ranges, branch conditions,
thread handoffs and existing trace boundaries. Decode exchange includes response
transport, parsing and checks. Successful one-shot transactions acknowledge and
wait for helper exit and verified cleanup; reusable sessions validate a completion
acknowledgement. After transaction return, conditional synchronous thumbnail
storage precedes pixel enqueue. PNG/JPEG metadata formatting and conditional
memory-cache insertion follow pixel enqueue and precede final-result publication.
Queued callbacks apply results on the service thread and emit `changed`; the
harness captures latency before its endpoint probes. Worker metadata work can
overlap application of the pixel result. Source ordering establishes neither
conditional branch execution nor elapsed cost in an individual observation.

The [pooled and per-block summaries](../../build/preview-delivery-gaps-v3-analysis-20261112-05/summary.json)
report presence, unavailable reasons and median/nearest-rank p95 for each endpoint.
For measured large PNGs, decode-exchange-end-to-pixel delivery is:

| Variant | Present | Median ms | p95 ms |
|---|---:|---:|---:|
| A | 100 | 26.092 | 68.929 |
| B | 100 | 21.480 | 25.416 |
| C | 100 | 18.632 | 22.181 |
| D | 100 | 18.783 | 24.000 |

A has a unique applicable cleanup boundary in every measured observation.
B has two compatible demand cleanup spans, so cleanup-end intervals remain
ambiguous rather than selecting the nearest span. C/D have no applicable demand
cleanup before delivery, consistent with reusable completion; their cleanup-end
intervals remain unavailable. These limitations do not invalidate the distinct,
unambiguous decode-end intervals. The [per-observation intervals](../../build/preview-delivery-gaps-v3-analysis-20261112-05/intervals.json)
retain clipped historical coverage unions, unnamed gaps, intervening spans and
markers, and raw file/line references. Warm-ups, setup and post-delivery work do
not enter measured summaries; U remains separately labeled harness-latency context.

The [selected examples](../../build/preview-delivery-gaps-v3-analysis-20261112-05/selected-examples.json)
preserve the previous five slowest harness observations per variant and endpoint,
plus five observations nearest each cell's harness-latency median, with block/sample
tie-breaking. These median-near examples are descriptive comparisons, not matched
controls. The slowest A large-PNG pixel example (block 9, sample 0) has a 151.182 ms
decode-end interval, 21.416 ms intersecting coverage and 129.766 ms unnamed elapsed
time; its cleanup-end interval is 124.119 ms. The corresponding final-metadata
intervals are 151.215 ms and 124.152 ms. The report links raw timelines for every
selected tail and comparison. These gaps cannot be assigned to thumbnail storage,
queue residence, CPU work or scheduling from retained evidence.

The assessment ends with an ordered minimum probe specification: distinguish
transaction completion/return and effective retirement from repeated retirement
calls; record storage branch decisions and serialization/commit boundaries,
metadata preparation and memory-cache insertion; then connect endpoint enqueue,
callback entry, `applyResult`, signal emission and harness capture. Propagate
publication, transaction, job and service-lifetime identities across thread
handoffs while retaining actual executing pid/tid. No probes or optimizations
were implemented. Inclusive durations remain non-additive; no overhead is
subtracted or threshold introduced. The overhead report's host-activity limitation,
C's failed qualification and D's failed pilot remain unchanged.

Seven focused regressions passed. [Independent verification](../../build/preview-delivery-gaps-v3-analysis-20261112-05/independent-verification.json)
checked all 3,030 available endpoint/boundary intervals including retained warm-ups,
21,807 raw references, 1,054 assessment links, source ranges/hashes, exact historical
tail selection and unchanged consumed hashes. Earlier development runs that blocked
on ambiguous source-map anchors remain under ignored `build/`; the linked run is
complete with no issues. No native builds, benchmarks, runtime instrumentation,
deployment, publication, pin changes or commits were performed.

### Private delivery-path probe preparation (2026-11-13)

**UNCOMPILED — no runtime validation or measurements.** The
[private delivery preparation](../../build/preview-delivery-tracing-20261113-03/README.md)
provides independent A/B/C/D source and harness overlays covering transaction
wrapper return, one-shot acknowledgement/helper exit, reusable completion,
retirement calls versus effective cleanup, conditional raster storage and nested
PNG serialization/commit, metadata formatting/cache insertion, and publication
handoffs through applyResult, changed emission and separate harness endpoints.
The [supplemental v4 contract](delivery-tracing-v4.md) documents explicit unavailable
identities, independent span/publication IDs, short-circuit condition recording,
latency-capture ordering and the unmeasured overhead of timestamp capture itself.
Original v3 TRACE records and their historical parser remain unchanged.

The [manifest](../../build/preview-delivery-tracing-20261113-03/manifest.json)
records successful historical evidence reconciliation, exact source inventories,
recorded tool identities, unchanged before/after hashes and private output hashes.
Per-variant review artifacts are
[A diff](../../build/preview-delivery-tracing-20261113-03/A/overlay.diff),
[B diff](../../build/preview-delivery-tracing-20261113-03/B/overlay.diff),
[C diff](../../build/preview-delivery-tracing-20261113-03/C/overlay.diff), and
[D diff](../../build/preview-delivery-tracing-20261113-03/D/overlay.diff), with
[A probe map](../../build/preview-delivery-tracing-20261113-03/A/probe-to-source.json),
[B probe map](../../build/preview-delivery-tracing-20261113-03/B/probe-to-source.json),
[C probe map](../../build/preview-delivery-tracing-20261113-03/C/probe-to-source.json), and
[D probe map](../../build/preview-delivery-tracing-20261113-03/D/probe-to-source.json).
Each variant also retains its source-inventory.json. All anchors were checked on
temporary copies before emitting the four prepared source trees.

Sixteen [focused regressions](../../build/preview-delivery-tracing-tests-20261113.log)
passed, including synthetic lifecycle, nested/overlapping interval, publication,
rejection, endpoint, malformed-record and preparation-integrity cases. Full
preparation passed with subprocess and shell execution disabled. Seven unchanged
historical delivery-gap regressions also passed.
[Independent static verification](../../build/preview-delivery-tracing-20261113-03/independent-verification.json)
rechecked 2,671 consumed hashes and 297 probe references, recomputed every diff,
reversed every recorded patch back to the frozen sources, and checked timer
expressions, cancellation-load counts, queued connection types, unchanged v3 event
implementation, separate diagnostic identity allocation and D's initial deferral.
The [verification script](../../build/verify-preview-delivery-tracing.py) is retained
with its hash in that record. An earlier blocked anchor-review attempt and a
superseded prepared development output remain under ignored build/.

The new offline analyzer reports transaction, storage, metadata and delivery spans
separately, preserving inclusive durations and clipped unions. It distinguishes
enqueue-call duration, enqueue-to-callback elapsed time and callback execution;
missing evidence remains unavailable and incompatible evidence blocks assessment.
Synthetic validation establishes accounting behavior only. No diagnostic workload
was executed, no native sources were built, and no overhead or delivery-gap
attribution is established. Previous assessments, the overhead host-activity
limitation, C's failed qualification and D's failed pilot remain unchanged. Native
validation and any fixed diagnostic experiment require a separately planned step.
No deployment, publication, pin changes or commit were performed.
