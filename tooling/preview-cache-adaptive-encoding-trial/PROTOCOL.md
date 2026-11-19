# Adaptive PNG encoding investigation

This isolated experiment preserves both prior encoding attempts and all production
components. Frozen C and completed early-publication evidence are bound through
pinned seals, independent proofs and complete inventories. The completed encoding
investigation is additionally pinned by seal and independent proof.

Only one policy is eligible: default PNG for uniform images, unsupported formats
and SVG; compression 11 for supported nonuniform raster images. Compare active
32-bit pixels across scanlines, ignore padding, stop at first difference, and check
cancellation per row and every 4096 pixels. Formats: RGB32, ARGB32, ARGB32 premultiplied,
RGBX8888, RGBA8888, RGBA8888 premultiplied. Classification is inside synchronous store
timing; decoding, typed requests and readback are outside. Frozen C supplies all
metadata, permissions, cancellation, atomic commit and publication behavior.

Run `python3 tooling/preview-cache-adaptive-encoding-trial/run.py investigate
--output /home/andrii/Projects/pet/holonight/build/preview-cache-adaptive-encoding-trial-20261119-01-investigation
--qt-source <retained matching qpnghandler.cpp>`.

The original 16 thumbnails are extended with opaque sRGB 3200×2400 fixtures:
two-color (x < 1600 white, otherwise RGB 31,83,149); horizontal grayscale
floor(255*x/3199); panel (240,240,240 with [400,2800) × [300,2100) RGB 31,83,149).
Use the existing bounded smooth scaling at tiers 128,256,512,1024 and retained
orientation policy. Materialize and hash all 28 thumbnails before any store.
Source metadata is identical between modes. Each image/mode has one excluded
warm-up then six blocks of five measured stores, alternating mode order by block:
1,736 stores, 1,680 measured. No retries or replacement observations.

Frozen limits: configure/build 600 seconds each, linkage/mechanism 30 seconds each,
aggregate investigation 300 seconds; owned termination/reaping/group absence share
five seconds. Persist command results on every exit path. Freeze tools, sources,
inputs, libraries and compiled artifacts. A separate preload probe verifies the
installed Qt compression mapping; timing never loads the probe. Mechanism checks
also exercise all detector formats, padding, alpha, unsupported input and cancellation.

Run `offline/verify.py <evidence> --output <adjacent independent.json>`. This verifier
imports no controllers and independently reconstructs schedule, exact size arithmetic,
nearest-rank statistics, source allowlist and retained PNG pixels/alpha/color/metadata.
Every image requires 4*adaptive_bytes <= 5*default_bytes; textured-256 median and
rank-29 p95 must both strictly improve. Any failed eligibility gate means Deferred
and stops preparation, build, correctness and startup execution. Invalid/interrupted
evidence means Evidence insufficient. No detector/fixture/threshold revision is allowed.

Only eligible independently verified evidence can enter conditional startup work.
That work requires separate preparation/build/correctness/execution records, frozen
uninstrumented C, private raster-only changes, host Release builds with four jobs,
shared Images/runtime and arm-specific providers/harnesses/installed consumers;
provider CTest, installed-package resolution, all 130 behavioral checks and focused
store checks. Freeze 202 startup processes: one warm-up per arm then ten alternating
blocks of ten observations per arm, textured/count one/256/offscreen/private paths.
Preserve foreground authentication, noninteractive authorization, conservative owned
staging, 30-second workloads and five-second shared cleanup. Stop at first failure.
Recommend only if both whole-population endpoint p95 gains are >=5 ms and neither
median regresses. Block differences are descriptive, separate from selection statistics.
Historical qualification remains 78/80 and previous Deferred decisions remain unchanged.
