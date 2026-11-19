# Early pixel publication selection trial

The 2026-11-18 private startup trial yields **Deferred**. Early publication improves
pixel p95 by **20.733529 ms**, but final-metadata p95 improves by only **2.142534 ms**.
The unchanged selection gate requires both gains to be at least 5 ms, with neither
median regressing. Both medians improve, but the final-metadata requirement fails.
No candidate is selected for production.

## Scope and implementation

The [trial protocol](../../tooling/preview-cache-publication-trial/PROTOCOL.md) describes
separate prepare, build, correctness, execute and independent verification interfaces.
The trial binds the accepted overlap result, qualified correctness `-04`, their exact
independent verification records and complete sealed inventories. Frozen C sources
and harnesses are compared directly with the accepted retained source provenance.
Accepted historical independent records are reused instead of recursively rerunning
prior investigations; all fresh trial evidence receives independent verification.

Both providers start from frozen, uninstrumented C. Control stays unchanged. The
candidate publishes validated cold eligible raster pixels before synchronous thumbnail
storage and suppresses the later duplicate publication. The source and cancellation
checks, stale-result rejection, ineligible fallback, atomic storage, memory cache,
final metadata, timeout and shutdown paths retain their original ordering. No storage
thread or background writer is added. Production component repositories are unchanged.

Images and Thumbnails are compiled once against host dependencies in Release mode,
with four jobs. Both arms reuse identical installed dependency packages and runtime
payloads, and build separate File Browser providers, benchmark harnesses and installed
consumers. A fresh correctness run against those exact uninstrumented providers passes
all **130 required behavioral checks** and the installed consumers. The context-named
case maps instrumentation assertions to equivalent selected-source delivery and cache
behavior: one oriented progressive delivery, final-only EXIF, final source dimensions,
cache/pixel equality, and publication on the expected side of the commit barrier.

## Population and results

The frozen schedule contains 202 fresh processes: one excluded warm-up per arm, then
ten blocks containing ten observations per arm. Even blocks run control then early;
odd blocks reverse order. The retained textured 3200×2400 PNG is measured with startup,
count one, 256×256 and offscreen Qt. Every observation has private source and cache
directories. There are no retries, replacement observations, sample adjustments,
cache flushes, affinity changes, artificial load, tracing, profiling or publication,
cache or lease probes in the measured path.

Only ordinary benchmark endpoint timing runs on the measured path. Parent executable,
loaded inode/device and library hashes are captured after endpoint timing and service
shutdown. Helper mappings are explicitly unavailable because the helper has exited.
Protected runtime payloads, installed packages and static provider archives are bound
by the frozen build and staging records. These identities establish no historical
loading identity and no visible Files-rendering claim.

| Arm | Endpoint | Measured samples | Median ms | Nearest-rank p95 ms |
|---|---|---:|---:|---:|
| Control | Pixels | 100 | 132.710075 | 152.922874 |
| Early | Pixels | 100 | 112.058758 | 132.189345 |
| Control | Final metadata | 100 | 132.722652 | 152.935326 |
| Early | Final metadata | 100 | 130.777537 | 150.792792 |

The gate uses unrounded whole-population values. Pixel median improves by
20.6513175 ms and final-metadata median by 1.945115 ms. Nearest-rank p95 uses the
95th ordered observation of each 100-sample population. Warm-ups are excluded.

Block differences are descriptive only. Pixel median and p95 improve in all ten
blocks. Final-metadata median improves in five blocks and regresses in five;
final-metadata p95 improves in six and regresses in four. These block differences
do not replace the registered whole-population decision rule.

## Evidence and verification

All evidence resides in ignored build directories; historical evidence remains unchanged.

| Phase | Evidence directory under `build/` | Seal SHA-256 |
|---|---|---|
| Preparation | `preview-cache-publication-trial-20261118-01-prepared` | `bb60fbfc7b5705410b447bd3419e82447d6e5e8618a09a10f47c1ff5cad00a2f` |
| Native build | `preview-cache-publication-trial-20261118-01-built` | `59201a5ca7d50df6be49d69a8fc60cd8511911264795f71dfff9e3bfe73abced` |
| Fresh correctness | `preview-cache-publication-trial-20261118-01-correctness` | `4bc7b4fdc018fe44c0c9ba0f53e1297a9633297d0a0982686079678587b2f5cf` |
| Startup execution | `preview-cache-publication-trial-20261118-01-execution` | `f104bccb4ad1eab312d749943d237a55a49cf15f8512d5dfa0099c84bd4a5ed7` |

Each phase has an adjacent `-independent.json` record. Preparation and build are
independently verified; correctness independently confirms all 55 commands, 130
required checks and owned cleanup. Execution contains raw per-process commands,
results and output, scope isolation records, endpoint delivery samples, post-timing
loading identities, staging ownership/removal records, statistics and a findings report.
The workload bound is 30 seconds; process-group termination/reaping and helper-scope
proof share five seconds. Independent execution verification passes with 202 observations,
200 measured samples, no failed command, and **Deferred**. Execution completes with both
protected staging trees removed.

The focused synthetic suite passes **14 tests**, forbidding real processes. It covers
the exact decision boundary, both-endpoint gate, median regression, warm-up exclusion,
nearest-rank p95, malformed samples, schedule arithmetic, source restrictions, resealed
tampering, authorization loss, timeout, stopped schedules and cleanup failure. The
broader existing cache-publication suite passes 107 of 108 tests. Its one historical
failure expects a desktop-identity error at the now-retained correctness `-04` path;
the existing controller correctly rejects that collision first. The historical test,
controller and evidence are preserved.

Historical qualification stays **78/80**. No diagnostic duration is subtracted from
historical p95s. Streaming, validation reuse and SHA dispatch remain **Deferred**.
Another candidate requires a separate evidence-based investigation. Production changes,
full qualification, consumer rollout and deployment require a subsequent plan.

## Directional-variation encoding addendum

The subsequent [directional-variation encoding trial](preview-cache-complexity-encoding-trial.md)
keeps frozen-C synchronous publication and leaves this trial's Deferred decision unchanged.
Its corrected investigation independently passes store eligibility; preparation and host
Release builds verify. Fresh correctness stops at missing noninteractive authorization,
so the overall result is Evidence insufficient, with no staging or startup observations.

The subsequently authorized [encoding rerun](preview-cache-complexity-encoding-rerun.md) independently qualifies all 130 required behavioral checks and completes the 202-process startup trial with **Recommend**. This concerns the private directional-variation encoder; this historical early-publication trial remains Deferred. Production rollout remains outside scope.
