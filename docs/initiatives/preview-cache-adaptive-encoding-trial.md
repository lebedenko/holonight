# Adaptive PNG cache encoding investigation

The fixed adaptive rule yields **Deferred**. Uniform thumbnails retain default PNG
encoding and byte sizes, but nonuniform two-color, gradient and panel thumbnails
exceed the 25% per-image growth limit at tiers 256, 512 and 1024. All nine failures
are disqualifying. No policy, fixture or threshold was adjusted after observation.
Production components and both previous encoding attempts remain unchanged.

The [protocol](../../tooling/preview-cache-adaptive-encoding-trial/PROTOCOL.md)
registers the isolated experiment. Private namespace-renamed frozen-C stores use
unchanged default encoding or compression 11 for supported nonuniform raster input.
The detector compares active 32-bit pixels, ignores padding, exits at first difference,
and checks cancellation during long scans. Unsupported formats and SVG retain the
default writer. Classification is inside synchronous store timing. Request construction,
decode and readback are outside; metadata, color, permissions, cancellation and atomic
commit remain inherited from frozen C. No provider publication code was changed.

## Frozen inputs and execution

Pinned seals, independent proofs and complete inventories bind frozen C, the completed
early-publication trial and the completed prior encoding investigation. All 28 thumbnails
were materialized as RGBA bytes with hashes and a manifest before measured stores.
The original 16-image corpus retains its orientation/scaling policy. Three deterministic
opaque sRGB 3200×2400 fixtures add two-color, horizontal grayscale gradient and rectangular
panel images, each smoothly bounded to 128,256,512,1024. Source metadata matches across
modes. The oriented JPEG remains 20×40 under the existing no-upscale policy.

Host Release configure/build used four jobs and the retained installed Images package.
All five commands succeeded. Separate untimed mechanism checks verified compression
mapping plus six detector formats, differing row padding, alpha differences, unsupported
format fallback, empty images and cancellation. No preload probe ran during timing.
Every image/mode excluded one warm-up and retained 30 stores in six blocks of five,
alternating mode order by block: **1,736 total stores; 1,680 measured**. No retries,
replacement observations, protected staging or desktop startup workload occurred.

The complete investigation process took 44.179176 seconds including setup/readback and cleanup, within its frozen 300-second aggregate limit. Configure/build each retained a 600-second limit; linkage/mechanism each retained 30 seconds. Command results persist exit, PID, timing, failure flags, reaping and group absence. Shared five-second owned cleanup passed for every command, taking at most 0.076585 seconds.

## Selection statistics

Whole-population textured-256 statistics exclude warm-ups. P95 is nearest rank,
observation 29 of 30; exact values, rather than rounded display values, determine eligibility.

| Mode | Median ms | P95 ms | Encoded bytes |
|---|---:|---:|---:|
| default | 19.7310745 | 35.015413 | 72,056 |
| adaptive | 10.0672510 | 14.030942 | 83,995 |

Both primary statistics improve, but eligibility requires every image to satisfy
`4 × adaptive_bytes ≤ 5 × default_bytes`. These images fail:

| Image | Default bytes | Adaptive bytes | Exact failed comparison |
|---|---:|---:|---|
| two-color-256 | 1,454 | 2,206 | 8,824 > 7,270 |
| two-color-512 | 2,462 | 5,314 | 21,256 > 12,310 |
| two-color-1024 | 5,679 | 16,775 | 67,100 > 28,395 |
| gradient-256 | 1,444 | 2,063 | 8,252 > 7,220 |
| gradient-512 | 2,463 | 5,054 | 20,216 > 12,315 |
| gradient-1024 | 5,692 | 16,274 | 65,096 > 28,460 |
| panel-256 | 1,470 | 2,296 | 9,184 > 7,350 |
| panel-512 | 2,479 | 5,324 | 21,296 > 12,395 |
| panel-1024 | 5,698 | 17,048 | 68,192 > 28,490 |

Uniform flat thumbnails retain identical default/adaptive encoded bytes at all four
tiers. Every image round trip preserves pixels, alpha, Qt color space and required
cache metadata. The independent verifier additionally decodes retained PNG bytes with
Pillow and checks dimensions, RGBA hashes, alpha, metadata and embedded ICC when present.
It verifies materialized inputs, command contracts, source allowlists, runtime libraries,
compiled artifacts, complete schedule and statistics without importing controllers.

## Descriptive block differences

These differences are descriptive and do not replace whole-population selection.
Positive values favor adaptive. Each block has five stores per mode, so its p95 is
its maximum. There is no startup-performance claim.

| Block | Median gain ms | P95 gain ms |
|---|---:|---:|
| 0 | 6.331970 | 5.649194 |
| 1 | 5.989317 | 7.874126 |
| 2 | 9.218061 | 9.494402 |
| 3 | 10.421408 | 23.780104 |
| 4 | 9.130790 | 9.876105 |
| 5 | 10.201539 | 24.302345 |

## Verification and stop gate

All **16 process-forbidden synthetic tests** pass. Coverage includes exact per-image
size boundaries, eligibility, warm-up exclusion, nearest-rank p95, malformed/reordered
populations, source restrictions and resealed source tampering, authorization/launch
failure, timeout, interruption, nonzero exit, cleanup failure and fabricated cleanup.
Detector behavior also passed the compiled native mechanism checks described above.

Independent verification passes with Deferred, no selected candidate, all 1,736 stores,
1,680 measured stores and verified cleanup. Evidence remains in the ignored directory
`build/preview-cache-adaptive-encoding-trial-20261119-01-investigation`.

Evidence seal SHA-256: `77946b3adf2c93565d5ff8acc364c800d884ab88a1a71ff3a47ad2bf5cc79ce7`.

Adjacent independent record SHA-256: `126513debeb20571d3fe58a9b5dd86153a25feea5cf5e452bd8553319a6144a5`.

The explicit investigation stop gate applies. Conditional preparation, build,
correctness and execution tooling was not implemented or invoked; it would be
required before proceeding with any eligible future policy. Provider CTest,
installed-consumer rollout, 130-case behavioral qualification and the 202-process
startup trial were therefore not run or claimed. No startup recommendation is made.
A revised detector or compression policy requires a separate investigation.

Historical qualification remains **78/80**; previous Deferred decisions are unchanged.
