# PNG cache encoding investigation

This private investigation consumes sealed frozen C and the completed independently
verified early-publication trial. Historical sources, tooling and evidence stay intact.
Production changes and full qualification are outside this experiment.

Run `run.py investigate --output <absolute fixed investigation path> --qt-source
<matching qpnghandler.cpp>`. The destination is
`build/preview-cache-encoding-trial-20261118-02-investigation`. Collisions are errors.
Attempt 01 remains sealed and is never reused. The user authorized this corrected
retry after its aggregate timeout. Command limits are frozen before execution:
600 seconds each for configure/build, 30 seconds each for linkage/mapping, and
300 seconds for the complete investigation (including untimed setup and readback).
The startup workload limit remains 30 seconds per observation. Every launched
command records its result even after timeout, interruption, launch failure or
cleanup failure. Group termination, reaping and absence proof share five seconds;
failure stops the schedule with no replacement command or sample.
The dependency source is pinned to Qt's installed SBOM revision
`025bdad181de241e81bf853c8a2d7bf3d19261a9`, retrieved from
https://raw.githubusercontent.com/qt/qtbase/025bdad181de241e81bf853c8a2d7bf3d19261a9/src/gui/image/qpnghandler.cpp.
Its compression mapping is `(compression * 9) / 91`. A separate LD_PRELOAD probe
confirms the live writer passes levels 1 and 0 to libpng for settings 11 and 0.
Unsupported options, unexpected levels or unresolved source identities stop execution.
No probe is loaded during store timing. Resolved runtime libraries receive SHA-256 identities.

Private copies of the real synchronous Thumbnails cache implementation are compiled
against host dependencies in Release mode with four jobs. Only namespace names and
the PNG writer call differ. Default uses the unchanged `QImage::save` call; the other
two use `QImageWriter::setCompression(11)` or `(0)`. All metadata, permissions,
QSaveFile, cancellation, commit and replacement behavior come from frozen C.
All three typed request aggregates are prepared outside the store timer. Compiled
executable, probe and store archives receive identities before mechanism/timing runs.

The frozen corpus consists of the retained 3200×2400 textured PNG and oriented JPEG,
plus deterministic flat RGB and varying-alpha images, each at 128, 256, 512 and 1024.
Images uses the retained installed library and its orientation/scaling policy for
the retained inputs; generated images use the same smooth bounded scaling. Generated
colors are sRGB. Decode and setup stay outside store timing. The source URI, timestamp,
size and revision are identical across modes for each image. Each cell has one excluded
warm-up and 30 stores in six blocks of five, rotating mode order by block. There are
1,488 stores total, 1,440 measured. Time covers the whole synchronous store, including
tagging, permissions and atomic commit. Decode/readback and evidence copies are untimed.

Require identical decoded RGBA pixels, alpha, color space and required cache metadata.
Every image must satisfy `4 * candidate_bytes <= 5 * default_bytes` using exact bytes.
Eligible modes also strictly improve median and nearest-rank p95 (rank 29 of 30) on
textured-256. Choose lowest p95, median, total corpus bytes, then setting 11.
Exploratory store timings make no startup gain claim.

Run `offline/verify.py <investigation> --output <adjacent independent.json>` for
independent command, source, provenance, schedule, pixel/metadata and selection
reconstruction without importing controllers. Evidence is sealed, tools snapshotted,
and inputs frozen before compilation. Failed or interrupted evidence is Evidence
insufficient. A complete valid investigation with no eligible setting is Deferred;
stop before candidate preparation, qualification or startup execution.
Attempt 01's independent audit remains available through the original fixed path;
its missing timeout record is still unverified and is not repaired retrospectively.

If a mode qualifies, the remaining approved plan requires separate preparation,
build, correctness and execution evidence, with independently verified prerequisites,
unchanged C control, a raster-only candidate edit (SVG unchanged), one shared Images
build and arm-specific Thumbnails/File Browser/harness/installed consumers, provider
CTest, all 130 behavioral cases and focused store checks. Freeze the full 202-process
startup schedule before execution: one excluded warm-up per arm, then ten alternating
blocks of ten per arm at startup/count one/256×256/offscreen. Use foreground desktop
authentication, noninteractive authorization before protected operations, owned staging,
30-second workloads and a shared five-second cleanup bound. Stop on first failure;
no retries, replacements, cache flushing, affinity changes or artificial load.
Recommend only for both endpoint p95 gains >=5 ms and neither median regressing.
Historical qualification remains 78/80; all prior candidates remain Deferred.
