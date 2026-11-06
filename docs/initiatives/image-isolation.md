# Image isolation feasibility

The first milestone has a standalone [Glycin experiment](../../holonight-images/experiments/glycin/README.md)
and a local [compatibility decision](../../holonight-images/docs/sdd/glycin-feasibility/DESIGN.md).
The [2026-11-06 Rust/Qt comparison](../../holonight-images/experiments/comparison/README.md)
now demonstrates raw Rust EXIF extraction and captured linked-SVG resources with both
candidates. **Neither qualifies for migration.** The focused color reassessment passes all
96 comparisons against an analytical reference, including valid sRGB, linear sRGB
and linear Display-P3 PNGs in RGB/RGBA at 8/16 bits. Malformed-profile assumed-sRGB
fallback is now accepted with explicit diagnostic uncertainty; it is no longer a
blocker. No incorrect valid-profile conversion was observed in these fixtures.
Other profile families, containers, CICP and HDR remain unproven. Glycin worker-error
propagation remains a source-level concern; a local report draft was not submitted.
The focused orientation/GIF reassessment passes 165 checks: all EXIF orientations
in both TIFF byte orders under Apply/Ignore, stored/display geometry, native pixels,
shrinking/no-upscale bounds, session/restart policy, known GIF frames/delays/end and
supplemental intrinsic loop declarations. Glycin requires the additional private
bounded C++ GIF block parser inside the outer sandbox; this is not a native Glycin
fact. Qt's separate native loop count fails to recognize ANIMEXTS1.0 declarations;
the supplemental scanner passes both recognized identifiers. Truncation, conflicts
and traversal budgets produce explicit unavailable facts independently of decoding.
The independent GIF disposal reassessment passes all eight small fixture cases for
direct and isolated Qt. Glycin fails opaque-background disposal 2, mixed pixels and
stable repeated exhaustion; disposal 1/3, transparency and local-palette pixels pass
those small fixtures. The larger retention traversal has pixel failures in all three
controls, so small-fixture success does not establish general compositing correctness.
All six bounded retention workloads complete and pass the unchanged 32 MiB RSS and
cgroup-anonymous growth gates after warmup; all worker scopes close empty or removed.
The local design records fixture-specific classifications, medians and unique ignored
Release evidence. These checks do not prove leak freedom or memory independent of
animation length. Playback scheduling, strict streaming bounds, active-decoder
cancellation, linked-resource acquisition, deployment and production cache/session policy remain
unproven. The older C API
results remain historical evidence, not proof of Rust API limitations.
No provider/consumer API, dependency declaration, installer rule or submodule pin changes
are included. All paths below still use the previous backend.

## Entry-point inventory and ownership

The numbered milestones follow the recommended eight-stage order. Paths are relative
to the named repository. This inventory groups entry points by parser and provenance;
it is source evidence, not runtime isolation acceptance.

| Owner | Encoded input and entry points | Milestone |
| --- | --- | --- |
| images | `src/image.cpp`: caller devices, Qt inspection/read and libwebp fallback | 2–3 |
| images | `src/metadata.cpp`: JPEG/PNG/WebP/TIFF scans and libexif facts | 4 |
| images (experiment only) | `experiments/comparison/gif-facts.h`: bounded supplemental intrinsic GIF loop scan inside the isolated helper; no decompression | 5, fixture evidence only |
| images | `src/svg.cpp`: XML validation, embedded raster `QImageReader`, QtSvg inspection/rendering | 6 |
| thumbnails | `src/cache.cpp`: replaceable freedesktop PNG pixels/text via `loadFromData`; PNG writes | 4 |
| file-browser | `src/preview/preview_service.cpp`, `thumbnail_service.cpp`, `thumbnail_decoder.cpp`: opened regular-file previews, generations and memory/disk caching | 2–4 |
| file-browser | `src/preview/svg_helper.cpp`: checked SVG bytes followed by local-path Qt renderer | 6 |
| Viewer | `apps/viewer/images/image_decoder.cpp`, `image_loader.cpp`, `decoded_image_cache.cpp`: provider first frame, workers, prefetch and raw decoded image cache | 3–4 |
| Viewer | `apps/viewer/images/frame_source.cpp`, `frame_streamer.cpp`, `animation_controller.cpp`: separate QFile/Qt GIF parser and playback | 5 |
| Viewer | `apps/viewer/image_document.cpp`, `image_canvas.cpp`, `clipboard_controller.cpp`: SVG validation, persistent renderer, local links, vector zoom and clipboard render | 6 |
| Settings | `apps/settings/src/WallpaperModel.cpp`, `WallpaperController.cpp`: discovery, header checks, validation, preview cache | 7 |
| Settings | `apps/settings/qml/WallpaperWindow.qml`: preview and selected-image file rereads | 7 |
| Shell | `apps/shell/qml/Background/Background.qml`: wallpaper file decoding and crossfade | 7 |
| Shell | `libs/holonight-services/src/mpris/MprisArtworkCache.cpp`: local/data/network acquisition, Qt decode, PNG publication and cache reread | 7 |
| Shell | `apps/shell/qml/Widgets/MprisArtwork.qml`, `MprisWidgetSurface.qml`: final artwork/cache URLs and additional artwork presentation | 7 |
| qt | `src/icons/hniconengine.cpp`, `hniconimageprovider.cpp`, `iconrenderer.cpp`: raster and SVG icons, semantic SVG rewriting | 7–8; bundled bytes trusted, external assets require provenance qualification |
| file-browser / Files | `src/icon_image_provider.cpp`, Files listing/places/inspection QML: external theme names through icon provider; qrc fallbacks | 7–8; external theme assets are not automatically trusted |
| Greeter | `qml/Background.qml`, `Main.qml`, `LoginPanel.qml`: configured background and account avatar file URLs | 7–8; additional desktop consumers, not migrated here |

Raw decoded QImages from provider/memory caches, QPixmap construction from validated
images, compositor textures and tray pixmap arrays are not encoded-file decoders.
Their dimensions, lengths and lifetime still need validation. Bundled qrc icons,
logos/backgrounds and fallback art can retain Qt rendering where provenance is fixed.
`QIcon::fromTheme` in application startup and services delegates to the external-theme
row rather than establishing trust. Hyprlock's external renderer/configuration is a
deployment boundary, not an in-process provider entry point.

## Contracts and later integration

Keep Qt public types, caller-owned open devices, application scheduling/generations and
dependency direction `thumbnails → images`. Before choosing production interfaces,
extend the demonstrated isolated typed metadata and immutable fixture-capsule mechanisms
to production QIODevice/resource acquisition with stable identities. Fixture capsules
do not establish safe acquisition of arbitrary resource trees. Prove broader color
conversion coverage and error propagation, complete animation semantics and actual-decoder cancellation;
retain the demonstrated process-tree memory ceiling and fail-closed runtime discovery.

Order later work as source limits → installed raster provider/runtime prerequisites →
metadata and cache isolation → GIF playback → SVG → desktop display → removal/audit.
Publish providers before dependent consumers only when publication is authorized.
Retain installed-package tests and installation staging, ownership, collision and
conservative uninstall protections. The experiment changes none of those surfaces.

Future integration must test installed consumers, missing/overridden loaders,
namespace denial, SVG races, external cache PNGs, GIF disposal/loop/restart, final QML
pixel delivery and trusted artwork. Full inventory closure requires a runtime trace
of each route; the source scan alone cannot establish complete isolation.

Independent GIF triage now separates oracle validity, wrapper equivalence, pixels
and exhaustion in the [provider design](../../holonight-images/docs/sdd/glycin-feasibility/DESIGN.md).
Fixture/reference self-checks pass. Raw public APIs reproduce Qt local-palette
disposal-2 and Glycin opaque-background disposal-2 failures; three-frame reductions
and 3×2 controls are confirmed in three fresh workers. Glycin also returns frames
after end for absent/finite/infinite declarations. Wrappers agree on exercised frame
outputs. Qt source supports decoder attribution; Glycin layer attribution and a
persistent-end API contract violation remain unproven. Both remain experimental;
local report drafts are unsubmitted. Existing retention/performance evidence and
umbrella pins are preserved.

The bounded single-source milestone now passes private C++ caller-device tests and
16/16 focused capture checks. `Comparison::capture` receives an open readable seekable
`QIODevice&`, seeks to zero, enforces a positive explicit limit up to 256 MiB against
actual reads (64 KiB chunks plus a one-byte overflow probe), and returns owned bytes.
Failures expose no partial payload; cancellation is cooperative around device operations.
Caller ownership/open state remain intact and final position is unspecified. Zero reads
mean EOF; changes observed during capture are included without claiming an atomic snapshot.
Both isolated candidates inspect and decode captured PNG, oriented JPEG and self-contained
SVG after original replacement/removal with matching fixture pixels; all scopes close.
The [local design](../../holonight-images/docs/sdd/glycin-feasibility/DESIGN.md) records
unique ignored evidence and provider/installed-consumer verification. Historical Python
evidence remains intact. Linked SVG resource acquisition, filesystem identity checks,
blocking-read interruption, active-decoder cancellation and production migration remain
deferred. This does not resolve the preserved GIF failures or select a backend.

The next private milestone adds explicit isolated-request cancellation via a caller-set
`threading.Event`. The serialized request thread discards cancelled replies, makes the
worker terminal and raises `RequestCancelled` only after verified scope cleanup and
launcher reaping. All terminal cleanup uses one five-second monotonic budget from
cancellation observation: scope TERM, at most one second of grace, then scope KILL as
needed. Hierarchical `cgroup.events populated=0` or cgroup removal supplies proof;
missing proof/manager support or deadline exhaustion produces a distinct cleanup error.
There is no PID-sampling fallback, automatic retry or worker restart. Close on a cancelled
worker only releases descriptors/artifacts and retains stderr.

The focused runner controls cancellation phases with bounded barriers and diagnostic
acknowledgements, including partial records, races and a TERM-resistant descendant that
requires scope KILL. The Qt/Glycin matrix repeats dispatch and final-delivery cancellation
three times in fresh cold/loaded workers using a PNG captured by the C++ probe; each case
requires exact fresh-worker recovery pixels and cleanup of both scopes. Dispatch proves
an outstanding request, not execution inside a codec instruction. Cooperative decoder
interruption remains unproven; both candidates remain experimental. The local design and
comparison README document the contract and unique ignored cancellation evidence. This
milestone preserves production contracts, pins, existing GIF failures and all previously
deferred acquisition/identity/deployment decisions.

Recorded cancellation evidence passes 35/35 checks with all 59 original/recovery scopes
verified and maximum successful cleanup 1.019 seconds. Capture checks pass 16/16,
protocol fault checks 5/5 and provider/installed-consumer CTest 3/3. Existing color,
geometry, animation, retention and performance evidence is reused. Full ecosystem and
container acceptance were not repeated for this private non-installed change.


The private linked-SVG milestone adds descriptor-pinned bounded acquisition, documented in
the [comparison README](../../holonight-images/experiments/comparison/README.md) and
[local design](../../holonight-images/docs/sdd/glycin-feasibility/DESIGN.md). Caller-owned base
and main descriptors stay pinned across byte capture and isolated manifest discovery. The
parent validates the manifest without XML/image parsing; Linux openat2 beneath/no-symlink/
no-mount-crossing resolution accepts only regular referenced files. Before/after descriptor
identity/size/nanosecond timestamps and final name revalidation reject observed changes
without retry or partial publication. Plain relative raster references, embedded raster and
valid document-local fragments are the bounded subset. Count/path/control/aggregate limits
and staging collisions are enforced independently. Original trees are never enumerated or
mounted; both candidates revalidate sealed captured byte maps inside isolation.

This is observed-change detection and immutable captured-input evidence, not an atomic
filesystem snapshot or cooperative blocking-read/codec interruption. The unique ignored
linked-* reports require independent pixels after original replacement/removal, three fresh
positive workers per candidate, discovery/render traces and hierarchical scope cleanup.
Historical fixtures and existing color/geometry/GIF/retention/performance evidence remain
available. Production APIs, consumers, dependencies, lockfiles, installer protections and
umbrella pins are preserved; neither experimental backend is selected.


Recorded linked acquisition evidence passes 36/36 with 81 verified scope cleanups and
42 exact expected renders; focused checks pass 3/3 including injected syscall unavailability.
Standalone capture/acquisition CTest passes 2/2. Existing capture (16/16), cancellation
(35/35), protocol (5/5), historical capsule (16/16) and provider/installed-consumer (3/3)
regressions pass. The local README records unique ignored report paths and matching
worker hashes; changed-source formatting, Python compilation and whitespace checks pass.
Full ecosystem/container acceptance was not repeated for this private non-installed change.

## Verified experimental runtime bundles

The private comparison now requires explicit host-native runtime preparation before
isolated launch. See the [comparison README](../../holonight-images/experiments/comparison/README.md)
for commands and the manifest contract.
Preparation discovers dependencies once, stages copied workers/plugins/loaders,
executables and MIME data, and publishes only a verified new directory. Every
isolated worker validates exact inventory, entry identity/role, modes and SHA-256
hashes before scope creation; launch never discovers or falls back to host codecs.
Only bundle runtime files and private captured capsules enter the sandbox. Absolute
host launch/manager tools receive a minimal environment. Glycin retains explicit
nested Bwrap selection, the request deadline stays 15 seconds, and scope memory/swap
limits and the five-second hierarchical terminal cleanup contract remain in force.

The bundle and manifest are trusted local artifacts: hashes detect changed/missing
contents, not upstream authenticity or concurrent trusted-file mutation. Private
runtime acceptance retains unique ignored evidence with hostile-environment checks,
three fresh independent PNG and acquired linked-SVG trials per candidate, traces,
pixels, limits and cleanup proof. No backend is selected, GIF failures are unchanged,
cooperative codec interruption remains unproven, and historical timings do not
measure this launcher. Production APIs, installed consumers, dependencies, installer
protections and umbrella pins are unchanged.


## Private runtime evidence version 2

The [comparison contract and reproduction command](../../holonight-images/experiments/comparison/README.md)
and [local design](../../holonight-images/docs/sdd/glycin-feasibility/DESIGN.md) supersede
historical version-1 runtime acceptance. Fresh reports independently require exact
scenario/artifact/scope coverage, nested child-report integrity, real native activation
controls and their deliberately broken counterparts, poisoned isolated discovery,
twelve candidate trials, structured syscall findings and exact launch-failure stages.
Child coverage remains cancellation 35, capture 16, linked acquisition 36, protocol 5
and capsules 16. Created scopes retain observed limits and hierarchical cleanup,
including constructor and recovery workers. Missing prerequisites or uncertain proof
leave failed evidence and a nonzero exit. Existing codec/retention/performance evidence
is reused; production interfaces, dependencies, lockfiles, installers, umbrella pins,
backend selection, GIF behavior and deployment remain unchanged. Local hashes provide
integrity relative to recorded files, not upstream authenticity or writer exclusion.


Fresh version-2 verification on **2026-11-06** passes **53** helper tests normally and
under `python -O`, **52** parent scenarios and all **35/16/36/5/16** child scenarios.
Independent reopening verifies **4,450 artifacts** and cleanup for all **224 created
scopes** (maximum **1.016 s**). Provider `task test` passes **3/3**, including its
installed-package consumer. The qualifying local report is
`holonight-images/build/comparison/runtime-v2-acceptance-final/report.json`; separate
validation is in `holonight-images/build/comparison/runtime-v2-independent-validation.json`.
Previous failed reports remain failed. Tracing uses recorded exit scheduling to avoid
thread-exit decoding races and rejects every unresolved syscall; these results do not
provide new performance measurements. No broad container or ecosystem acceptance was
needed for these private, non-installed fixtures and reporting changes.

Final checks pass: native acquisition CTest **2/2**, pinned formatting of new C++
fixtures, changed-C++ format checks, Python compilation and whitespace checks in both
repositories. The native socket fixture requires execution outside the agent sandbox;
its successful outside-sandbox run is the qualifying CTest result.


The private [GIF attribution audit](../../holonight-images/experiments/comparison/GIF-UPSTREAM-REPORT-DRAFT.md)
now retains 79 declared version-2 scenarios and all 144 runtime cleanup proofs, while
preserving 33 failed candidate findings. Exact Glycin loader sources and a direct
image 0.25.10 probe locate its disposal-2 background policy in the composited-frame API;
persistent exhaustion remains an application requirement without an established upstream
promise. Attribution is **blocked** because Qt tag archive checksums do not match the
matching distribution recipes. The report remains failed; neither candidate qualifies.
Unchanged GIF acceptance separately reports 16 passes and 8 failures. Existing runtime,
codec, retention and performance evidence is reused. Production APIs, dependencies,
installers and umbrella pins are unchanged, and no upstream report was submitted.
