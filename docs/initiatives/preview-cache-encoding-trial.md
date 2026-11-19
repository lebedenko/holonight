# PNG cache encoding investigation

The corrected 2026-11-18 investigation yields **Deferred**. Both permitted settings
improve the primary textured-PNG store median and p95, but neither satisfies the
25% encoded-size cap for every corpus image. No candidate is selected. The plan's
investigation stop gate applies; candidate preparation, provider qualification and
the 202-process startup trial are not required or run. Production components are
unchanged, and these store measurements make no startup-performance claim.

## Corrected retry

The user authorized fixing and retrying the interrupted attempt. The retry uses a
new fixed directory, `build/preview-cache-encoding-trial-20261118-02-investigation`.
Attempt 01 remains unchanged with its original Evidence insufficient outcome.

The aggregate investigation now has a frozen 300-second bound, distinct from the
30-second limit per startup observation. Configure/build retain 600 seconds each;
linkage and mechanism verification retain 30 seconds each. Every command persists
its PID, exit, failure, timeout flag, timestamps, reaping, group-absence check and
cleanup duration before propagating errors. Timeout, interruption, launch failure,
nonzero exit and cleanup failure stop execution. Owned cleanup shares five seconds.
All three typed request objects are prepared outside the store timer, removing the
candidate wrappers' request-construction overhead from the timed region.

The host Release build with four jobs succeeded. The aggregate corpus process
completed in 37.133330211 seconds, including untimed generation and readback. All
five commands succeeded, with owned groups reaped and absent. Cleanup took at most
0.0764027570039616 seconds per command. No retries or replacement observations occurred
within attempt 02, and no protected staging or desktop helper workload was created.

## Mechanism and preserved behavior

The [protocol](../../tooling/preview-cache-encoding-trial/PROTOCOL.md) binds frozen C,
the completed early-publication trial, its pinned independent records and inventories,
and retained fixture provenance. Historical sources, tooling and evidence stay intact.

Installed Qt 6.12.0-5 records qtbase revision
`025bdad181de241e81bf853c8a2d7bf3d19261a9` in its SBOM. Matching qpnghandler.cpp has
SHA-256 `7a352b8542df1fc7cc44f84a308035d8200fa660d2e11c7f5d93ffd7aa228852`.
Its mapping `(compression * 9) / 91` maps settings 11 and 0 to libpng levels 1 and 0.
A separate live interposition probe confirms option support and both levels, resolving
the SBOM's dirty-build label for this mechanism. No probe is loaded during store timing.
Runtime libraries, the executable, probe and three store archives receive hashes
before the investigation and are checked again during independent verification.

Private namespace-renamed copies of the real synchronous cache store preserve
metadata tagging, permissions, QSaveFile, cancellation checks and atomic commit.
Default keeps QImage::save; the two settings replace that writer call with explicit
QImageWriter compression. The retained installed Images package supplies existing
orientation and bounded decoding. Generated flat and varying-alpha images use sRGB
and smooth bounded scaling. Source URI, timestamp, size and revision match across modes.

## Corpus, correctness and selection

All 16 images cover textured PNG, flat color, varying alpha and the retained oriented
JPEG at tiers 128, 256, 512 and 1024. The small JPEG remains 20×40 at every tier under
the existing no-upscale policy. Each image/mode has one excluded warm-up and 30 stores
in six blocks of five; mode order rotates by block. All **1,488 stores** completed,
including **1,440 measured stores**. Decode, request setup and readback remain outside
timing. Timing includes tagging, directory/entry permissions, encoding and atomic commit.

Every round trip preserved pixels, alpha, color space and required cache metadata.
Independent Pillow decoding also checked the retained encoded bytes, dimensions,
RGBA hashes, alpha, embedded ICC data where present, and required text fields.
The independent verifier reconstructed the complete schedule and all statistics.

Primary textured-256 whole-population statistics, excluding warm-ups:

| Mode | Median ms | Nearest-rank p95 ms | Encoded bytes |
|---|---:|---:|---:|
| Default | 18.4744625 | 29.620730 | 72,051 |
| Compression 11 | 9.283363 | 12.267767 | 83,990 |
| Compression 0 | 7.2346975 | 9.341542 | 148,428 |

Both candidate medians and rank-29-of-30 p95s strictly improve, but exact size
comparisons disqualify both. Compression 11 fails on these flat-color thumbnails:

| Image | Default bytes | Compression 11 bytes | Exact failed size comparison |
|---|---:|---:|---|
| flat-256 | 1,440 | 2,053 | 8,212 > 7,200 |
| flat-512 | 2,449 | 5,018 | 20,072 > 12,245 |
| flat-1024 | 5,666 | 16,191 | 64,764 > 28,330 |

The comparisons are `4 × candidate_bytes > 5 × default_bytes`. Compression 0 fails
on 14 of 16 images: every image except textured-1024 and alpha-128. It fails the
primary image as well. Eligibility and tie-breaking use unrounded whole populations;
there is no eligible setting to rank or take into startup qualification.

Primary block gains below are descriptive only. Each block contains five measured
stores per mode, so its nearest-rank p95 is its maximum. Positive values favor the
explicit setting; these block differences do not replace the registered selection rule.

| Block | 11 median gain ms | 11 p95 gain ms | 0 median gain ms | 0 p95 gain ms |
|---|---:|---:|---:|---:|
| 0 | 8.377266 | 7.971629 | 11.215586 | 10.892346 |
| 1 | 9.228540 | 8.616470 | 11.208030 | 13.226130 |
| 2 | 10.323203 | 10.691830 | 12.920069 | 13.651824 |
| 3 | 9.939044 | 17.202596 | 10.705344 | 16.927511 |
| 4 | 8.678952 | 20.330558 | 8.971815 | 20.415837 |
| 5 | 8.537735 | 16.533027 | 12.103476 | 21.933601 |

## Evidence and verification

Attempt 02 seal SHA-256:
`2c89ddd5215722f40beaa516d9573c114edaa9c591aabdcc1bf2f209cd4da28e`.
Its adjacent `-independent.json` record has SHA-256
`db6eb58380fae376558c8762e0f6cc446eb4318f8bc29211a1d9ecd18c1ce31f`.
Independent verification passes with Deferred, no selected setting, all 1,488 stores,
1,440 measured stores and verified cleanup. It reconstructs commands, sources,
provenance, frozen inputs, compiled identities, raw observations, correctness and
statistics without importing the controller. A copy of these findings resides adjacent
to the ignored evidence directory as `-findings.md`.

All **18 focused tests** pass with real processes forbidden. They cover eligibility,
exact per-image size boundaries, tie-breaking, warm-up exclusion, nearest-rank p95,
malformed/interrupted/reordered evidence, source restrictions, timeout and interruption
records, authorization/launch failure, nonzero exit, cleanup failure, fabricated cleanup
and resealed stopped-evidence rejection. The real Release build and independently
verified complete investigation exercise the corrected successful command path.

Attempt 01 remains sealed at
`f7375f273dcc0d899fad9ca9ca78dd66525844a208a9a9967da10b9fabd1d58e`.
Its 30-second aggregate timeout and missing timeout-result record are historical
limitations; cleanup remains independently unverified for that attempt. No old record
is repaired retrospectively and no partial file from it enters the retry's population.

The selected-candidate preparation/build/correctness/execution interfaces remain
unimplemented because this complete investigation meets the explicit no-eligible-mode
stop condition. They would be required for a future eligible candidate. No provider
CTest, 130-case startup-candidate qualification, installed-consumer rollout or startup
trial is claimed by this result.

Historical qualification remains **78/80**. Early publication, buffered streaming,
validation reuse and SHA dispatch remain **Deferred**. No diagnostic duration is
subtracted from historical results; production changes and full qualification remain
outside this plan.
