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

## Opt-in production raster capability

The [isolated raster design](../../holonight-images/docs/sdd/isolated-raster/DESIGN.md)
adds a separate `HolonightImages::Isolated` target, synchronous caller-owned client,
C++ helper/launcher and explicitly prepared host-native runtime bundle. Its scope
is inspection, structured metadata and first-frame PNG/JPEG/BMP/TIFF/WebP/GIF.
Raw pixels retain precision, alpha, palette and named/untagged color; other valid
profiles are explicitly unsupported. Existing provider APIs and all application
consumers remain unchanged. This limited capability does not qualify animation,
SVG or a full backend migration; the GIF failures and blocked attribution audit
remain open. Umbrella pins and installation ownership/collision/conservative
uninstall policies are unchanged. No deployment or publication is authorized here.

Provider and relocated installed-consumer verification must qualify the new transport
and installed runtime independently of the experiment. Relevant integration covers
runtime faults, cancellation/descendant cleanup and actual staged artifact ownership.
Future consumer migration remains a separate milestone after these provider gates.

Fresh native Release verification passes **8/8** provider/runtime CTest entries,
including the relocated installed consumer. Actual staged runtime ownership,
collision rejection and conservative uninstall pass. The local design records
122 decode comparisons and fresh startup/transfer/scope-memory measurements.
Focused pinned-container compilation, package staging and changed-source checks
are used alongside native runtime evidence. Full integration remains stopped by
pre-existing formatting violations in two unchanged experimental files; no full
ecosystem rerun, application migration, deployment or publication is included.

## Default File Browser raster milestone

The [File Browser consumer design](../../holonight-file-browser/docs/sdd/isolated-raster/DESIGN.md)
records default isolated source inspection, metadata and first-frame decoding,
including all cached PNG reads and SVG-derived thumbnails. Thumbnails exposes an
optional Isolated target while retaining the legacy API for Viewer. The accepted
limits remain six qualified first-frame formats, 256 MiB encoded input and named
or untagged color; unsupported profiles have no in-process fallback.

Normal umbrella staging now builds Images with isolation, explicitly prepares its
host-native bundle, verifies it at install, and installs it before isolated
Thumbnails and File Browser. Preflight requires bubblewrap, systemd tools and the
existing Qt imageformats package. Ordinary manifests, collision rejection and
conservative uninstall remain authoritative. Images exports a prefix-relative
runtime directory for explicit staged/relocated consumers; deployment defaults
never contain DESTDIR. Runtime artifact ownership tests remain applicable.

The Images integration gate now passes, superseding the formatting-blocked status
above. The two experimental edits are formatting-only; additional fuzz-harness
lint corrections were needed to finish that gate. Native cache/preview and
installed QML pixel-delivery checks pass. Current-sibling File Browser container
acceptance exposes unrelated live-appearance failures, recorded in the local SDD.
No provider pins, Viewer migration, deployment or publication are included.


## Isolated preview application acceptance follow-up

The [File Browser SDD](../../holonight-file-browser/docs/sdd/isolated-raster/DESIGN.md#application-acceptance-follow-up-2026-11-08)
records the completed automated follow-up and exact reproduction/manual commands.
The full current-sibling File Browser gate now passes (12 main tests, 2 Core-only
checks, static analysis, formatting, QML and REUSE). Its appearance failures were
fixture defects: environment-provided prefixes were omitted from plugin discovery,
and live updates could precede deferred watcher initialization. Assertions were
preserved and fixed waits replaced with bounded rendered readiness checks.

Files and portal composition accept explicit runtime values while production entry
points retain installation defaults. Non-installed acceptance hosts exercise actual
application QML: Files pane, Quick Look and grid, and chooser dock/drawer. The chooser
uses explicit private non-activating bus connections while Images retains the real
user-session settings. No portal grid thumbnails or production environment discovery
were introduced.

Staged and relocated host-native presentation matrices pass, including cold decoding,
disk/memory reuse, SVG-derived PNG cache reads, selection/resizing, source/cache
cancellation without cache commits, shutdown/late replies and timeout/unavailable
presentation. The old prefix is absent during relocated checks; installed Preview and
PreviewQuick consumers also pass. Focused Files regressions pass 107/107, portal
lifecycle/presentation regressions pass, and portal staged activation/Settings/demo
checks pass 3/3. Existing Images, Thumbnails and real ownership evidence is reused;
codec behavior, cleanup contracts, worker counts and deadlines are unchanged.

**Manual native observations are recorded.** The user reports that executable checks
passed; close-during-load could not be performed because the fixtures loaded too
quickly, so that native interaction remains unverified (automated pending-work
shutdown coverage passes). Optional unavailable-runtime manual checks were not
separately confirmed. Rapid selection briefly showed a loading indicator even for
small fixtures, consistent with the previously measured isolation latency increase;
this milestone does not optimize it. Prepared launch commands are
`bash build/isolated-preview-manual.sh files` and
`bash build/isolated-preview-manual.sh portal` from this umbrella. The SDD provides the
checklist and limitations. Evidence is ignored under `build/isolated-acceptance-*`;
no native pointer/focus interaction was automated. No commits, publication, deployment,
Viewer migration or revision-pin update is included.

## Fast live-service preview revisits

The [File Browser cache-validity contract](../../holonight-file-browser/docs/sdd/isolated-raster/DESIGN.md#fast-in-memory-raster-revisits-2026-11-08)
now reuses successful oriented dimensions and EXIF alongside decoded pixels before
isolated inspection. Each request still opens and verifies the source descriptor;
identity includes device/inode/size and nanosecond modification/change times and is
rechecked before accepting a hit. A mismatch invalidates the memory candidate and
refreshes the disk-fallback identity. This detects observed changes, not an atomic
filesystem snapshot. The two-entry/64 MiB cache remains service-local.

Adequate previously validated memory entries remain usable when the runtime becomes
unavailable or invalid. Misses, resolution upgrades and fresh services still require
the verified runtime. Cold/disk isolation, SVG validation, grid caches, loading
indicators, deadlines and provider boundaries are unchanged. The linked SDD records
correctness, latency evidence and manual native revisit commands; raw evidence stays
under ignored `build/warm-preview`. Images, Thumbnails and ownership evidence is
reused because their tested inputs are unchanged. No deployment, publication, commits
or revision-pin updates are included.

For 100 measured revisits at each size, final median/p95 improved from **87.84/105.75
ms to 2.15/2.28 ms** for 160×80 PNGs and from **83.30/99.10 ms to 2.15/2.19 ms** for
1600×1200 PNGs. Both targets pass; separate launch evidence shows zero added helpers
for the 200 warm hits. Native provider tests pass 32/32, Files focused regressions
107/107, and Files/chooser offscreen acceptance passes. Current-sibling integration
passes 12 main and 2 Core-only tests plus quality gates; the final identity-refresh
edge case has subsequent focused native/package and source checks. The user confirmed that manual native
warm revisits passed and authorized publication and revision-pin updates.

## Publication and pinning (2026-11-08)

After the user confirmed the manual warm-revisit checks passed, the milestone was
committed and published in provider order. Consumer provider manifests now name the
exact published sibling revisions used for acceptance, and the umbrella pins those
commits. Files and chooser provider staging explicitly prepares the isolated Images
bundle and enables isolated Thumbnails, matching File Browser's staging workflow.
The umbrella also preserves the independently published greeter pin through a merge.
No native deployment was performed.

The native provider/package, Files focused, Files/chooser rendered acceptance and
warm latency evidence above remains applicable. Installer dependency checks pass
14/14; staging-order checks pass with the real ownership test's prior evidence
reused. Full consumer container acceptance was additionally attempted before
publication. The chooser gate passes 58 individual tests plus activation, Settings
and demo CTest entries, but fails `previewFollowsCursorAndCancellation`: its default
private-bus/container invocation cannot verify isolated helper cleanup/launcher
reaping. The three explicit native-only scenarios remain skipped in that invocation.
Files passes 19/22 CTest entries; `files-smoke`, `files-native-preview-observer`
and `files-unknown-dimensions` fail. These suites still assume runtime decoding
in the container or an application-local synthetic image plugin, which the isolated
helper does not load. Both full consumer gates remain failed, not replacements for
the qualifying native acceptance.
Logs are retained under umbrella `build/publish-isolation` and the component
`build/acceptance` directories. Full consumer CI still needs its runtime-dependent
legacy tests separated from the container-only execution environment and synthetic
codec expectations adapted to the isolated boundary.

## Preview overhead measurement groundwork (incomplete)

The [baseline tooling](../../tooling/preview-benchmark/README.md) freezes historical
sources, binaries, package prefixes, samples and build metadata before building
new host-native Release packages. The full archived pre-isolation File Browser
tree matches `caec685` (A); B fixes File Browser `2f86c9b`, Images `c1f6da5` and
Thumbnails `9462bac`. Historical Debug and unspecified-configuration numbers are
excluded from the new comparison. The evidence root is ignored
`build/preview-experiments-ak2cd2cp`; earlier failed preparation attempts remain
in separate uniquely named directories.

**This is not completion of the three optimization experiments.** Session reuse,
runtime-generation reuse and bounded prestarted workers remain unimplemented.
No optimization has been retained, no ready-worker target is claimed, and provider
interfaces, presentation, deadlines, deployment and revision pins are unchanged.
Experiment 0 still needs phase attribution, helper/validation/capture counters,
cleanup/resource sampling and an actual grid-scheduler control. The current
`grid-decode` case measures only its synchronous decoder.

The first measurement run retains an invalid upgrade case: the original harness
accepted idle pane state before the resize debounce dispatched an upgrade. Its
`INVALID-UPGRADE.txt` explicitly excludes those rows. The corrected harness waits
for requested-resolution pixels and records delivered/required dimensions; fresh
harness binaries and affected-case runs must remain separate from that evidence.
The reviewed comparison combines 4,800 unaffected original samples with 800
corrected upgrade samples, giving 100 attempts for each fixture/case/baseline.
Its table and raw-input hashes are under
`build/preview-experiments-ak2cd2cp/reviewed-comparison`. Both cleanup-verification
failures remain: one grid-decode request and one corrected upgrade setup. Neither
failure has an established cause. Native execution inside the
agent sandbox separately failed cleanup verification, while the approved native
smoke check succeeded. These results do not replace protocol, mutation, rendered
Files/chooser, relocation or worker-lifecycle acceptance.

All six evidence-tool tests pass, both harness revisions compile against the
installed A/B Release packages, and changed-source formatting, Python compilation
and whitespace checks pass. Independent reopening verifies the four historical
archive hashes and all four benchmark binary hashes. Provider code is unchanged;
its security/regression suites and application acceptance have not been rerun for
this tooling-only groundwork. The comparison remains incomplete as specified above.

## Cleanup diagnostic milestone (2026-11-08)

**Diagnostics implemented; historical cause unresolved.** The
[Images design](../../holonight-images/docs/sdd/isolated-raster/DESIGN.md#cleanup-attribution-milestone-2026-11-08)
records private structured cleanup reports and failure-only versioned JSON through
the existing diagnostic string. Reports preserve the original operation failure,
manager start/exit/timeout/output evidence, failed stage, scope identity,
hierarchical observation/proof and launcher state. Unknown observations never
supply proof; streams and serialized reports are bounded. Public APIs, statuses,
wire protocol, UI messages, cancellation precedence and deadlines remain intact.

A deterministic regression exposed permissive parsing of contradictory population
records; the parser now rejects those records and distinguishes observation errors
from confirmed removal. This robustness correction is not attributed to either
historical failure. Native Release provider/runtime and installed/relocated checks
pass **9/9**, deterministic cleanup/capture/protocol checks pass **3/3**, focused
File Browser isolation passes **5/5**, and existing native Files/chooser offscreen
acceptance passes against fresh diagnostic packages.

The separate [installed-provider probe](../../tooling/cleanup-diagnostic/README.md)
completed **1,000 preview-shaped cycles / 3,000 successful operations** in
**291.613 seconds**, rotating all four frozen fixtures through inspection, source
decoding and cached-PNG decoding. No cleanup failure recurred. Complete operation
records are in `build/cleanup-diagnostic-20261108/native-probe.jsonl`; provider
builds and regression evidence are in
`holonight-images/build/cleanup-diagnostic-20261108`. An initial relative-runtime
invocation is explicitly excluded as invalid preparation evidence. All original
A/B artifacts, invalid upgrade rows and both historical failures remain intact.
No cause or historical fix is claimed. Remaining measurements and session/worker
optimization remain deferred; no deployment, publication or pin updates occurred.

## Experiment 0 missing evidence (2026-11-09)

**Instrumentation implemented; measurements remain incomplete after cleanup
recurrences.** The [benchmark tooling](../../tooling/preview-benchmark/README.md#experiment-0-attribution-and-scheduler-evidence-2026-11-09)
adds fresh installed PreviewQuick controls and diagnostic-only source overlays.
The [Images notes](../../holonight-images/docs/sdd/isolated-raster/DESIGN.md#experiment-0-attribution-2026-11-09)
and [File Browser notes](../../holonight-file-browser/docs/sdd/isolated-raster/DESIGN.md#experiment-0-scheduler-control-2026-11-09)
state their contracts. No production implementation, worker default, public API,
wire protocol, deadline, UI message, cache policy or revision pin changed.

Evidence is retained under:

- `build/preview-scheduler-gemqcx9e/scheduler-run-q_6ddudo`: **418 exploratory** batches,
  stopped on B's oriented-JPEG cancellation batch. A has 70 batches per workload;
  B has 70 cold, 70 warm and 68 cancellation batches. There is one failed batch.
  These batches repeated one fixture each and rotated fixtures between batches,
  so **all are excluded from the requested mixed-fixture control**. The final
  harness cycles all four fixtures within every batch and passes in-process smoke
  checks. No corrected B measurement was started after the recurrence; the
  requested 600 mixed-fixture batches remain outstanding.
- `build/preview-diagnostic-1t39b7cm/diagnostic-run-011eht42`: **216/280** service
  samples and **544** correlated provider calls (272 source inspections, 242
  source decodes, 30 cached-PNG decodes). One operation returned cleanup failure;
  64 planned samples remain missing.
- `build/preview-diagnostic-1t39b7cm/resource-run-a5m00p3u`: **84/84** samples,
  **220/220** successful provider operations, and **5,115** resource observations.

Both affected runs stopped without retry or an additional manager cleanup.
The scheduler failure was the fourth surviving request: 12 cancelled-before-start,
four started, three delivered, all 16 responses finished, and zero pending work.
Frozen B reports only that hierarchical cleanup or launcher reaping was unverified.
The D recurrence preserves the full structured diagnostic: the operation succeeded,
launcher state was NotRunning, hierarchical proof returned **unreadable**, elapsed
cleanup was zero milliseconds, and no manager commands were issued. This localizes
the failed observation; it does not establish its cause or explain either historical
failure. Subsequent settled absence is not substituted for failed cleanup proof.
The original A/B matrix, invalid upgrade evidence and both historical failures are
unchanged. D uses Images `a772a67` with unchanged consumer revisions and is neither
replacement B nor an optimization candidate.

Diagnostic attribution has no missing helper timing records, telemetry overflow or
truncation in the captured operations. Median parent phases across the 544 calls
are runtime validation **49.58 ms**, launcher/readiness **32.78 ms**, capture
**0.014 ms**, response receipt/validation **2.33 ms**, acknowledgement/exit
**1.19 ms**, and cleanup **4.05 ms**. Helper provider execution has median
**1.98 ms** and serialization **0.048 ms**. These are nested distributions over
mixed operations, not additive end-to-end estimates or codec-only timings.
The median unexplained parent interval is **0.222 ms**; the full report keeps
missing worker intervals for the synchronous grid case explicit.

Both exploratory scheduler baselines deliver warm batches with zero decoder starts. In the
captured cancellation batches, A records 838 before-start cancellations and two
after decoder entry; B records 816 before-start and none after entry. Controlled
barrier tests independently cover both cases. Image validation checks non-null
returned pixels and bounds; synthetic barrier tests check exact pixels. Scheduler
latencies remain exploratory: some preparation/static-analysis work overlapped
this pass, the run is incomplete, and no rendered QML frames were measured.

Resource evidence records all 220 pre-ack CPU and memory readings. Individual
scope memory.peak reaches **45,629,440 bytes**; the sampled concurrent scope peak
is **39,145,472 bytes**, and sampled parent RSS reaches **60,801,024 bytes**.
These independent maxima must not be added. The maximum simultaneously sampled
RSS-plus-scope value is **95,617,024 bytes**, with the accounting/shared-page
caveat in the README. Parent RSS has eight unavailable observations, scope
sampling has eight incomplete discovery observations, and the composite has 16
missing observations. The largest observed sampling interval is **11.30 ms**.
All 28 resource-pass one-second snapshots observe zero tracked scope processes;
parent memory snapshots remain in the report. None of this proves leak freedom.

**Recommendation:** investigate the newly preserved cleanup observation before
selecting an optimization or filling the stopped runs. Once that gate is resolved,
runtime-generation reuse is the best-supported next experiment to evaluate:
repeated runtime validation dominates these diagnostic operations. This is a
conditional experiment recommendation, not an implementation decision or a
retain/reject result. Session reuse and prestarted workers remain out of scope.

Verification: deterministic evidence tests, scheduler barrier checks against A/B/D,
provider capture/protocol/cleanup tests, native Release provider/runtime and
installed/relocated checks (**9/9**), focused File Browser isolation (**5/5**), and
existing Files/chooser offscreen acceptance pass. C++ analyzer checks pass using
a copied command database with the unsupported GCC-only flag removed; source
formatting, Python compilation and whitespace checks pass. Formatting-only patch
normalization reuses these semantic checks. No unrelated container gates were
rerun. No deployment, publication, pin update or optimization was performed.

## Cleanup observation correction and excluded iteration (2026-11-09)

**The implementation and verification are complete; Experiment 0 evidence is not.**
The scheduler requirement is now **frozen A versus corrected B2**, superseding
the unfinished A/B scheduler requirement. Frozen A/B latency remains historical
comparison evidence. Both historical failures, both previously recorded recurrences,
and the excluded homogeneous scheduler run above remain unchanged. None is
attributed to the reproduced race without direct evidence.

The cleanup regression first failed on the prior implementation: an initially
empty scope was observed empty again, the launcher was reaped, and a redundant
final observation was unreadable. The implementation failed before observing the
subsequent confirmed removal. The correction uses one final bounded observation
loop, checking current hierarchical state and launcher state together, without
latching an earlier empty observation. Private filesystem injection covers
disappearance between lookup and open/read; only a fresh directory ENOENT after
an events-file failure proves removal. Permission errors, persistent unreadability,
malformed/contradictory population records, populated groups, deadline exhaustion
and unreaped launchers remain failures. The existing diagnostic gains stage,
syscall errno, fresh-directory-check outcome, the latest 32 observations, total
count and explicit truncation. Cancellation/result suppression, TERM/KILL policy,
runtime statuses, translated messages and the preview deadline are unchanged.
See the [Images design](../../holonight-images/docs/sdd/isolated-raster/DESIGN.md#cleanup-observation-correction-2026-11-09)
and [File Browser note](../../holonight-file-browser/docs/sdd/isolated-raster/DESIGN.md#corrected-experiment-0-control-2026-11-09).

### Packaging defect discovered during measurement

The initial preparation incorrectly used `git apply` inside an archive below the
umbrella repository. Git silently skipped the `diff --git` cleanup correction
paths and returned success. The declared B2/D2 delta was therefore **not applied**,
although diagnostic overlays were present. This agent-produced packaging error
invalidates those artifacts as corrected evidence. Source-hash inspection after
the recurrence established this mismatch; a new deterministic nested-repository
patch test reproduces it. Preparation now stops parent repository discovery,
requires every declared patch target to change, and verifies corrected snapshot
hashes against the intended source before building. Execution rejects corrected
metadata without this verification. All snapshots, package inventories, logs,
raw results and original reports remain preserved. Added `EXCLUSION.json` and
`summary-audit.json` files explain the mismatch without rewriting original reports.

`build/preview-iteration-8a6an044` ran all passes sequentially, after builds and
checks, and stopped on the first native client-returned cleanup failure:

| Pass on mislabeled artifacts | Planned | Attempted | Completed | Failed | Excluded from corrected evidence | Not attempted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Lifecycle cycles | 1,000 | 1,000 | 1,000 | 0 | 1,000 | 0 |
| D2-labeled attribution samples | 280 | 280 | 280 | 0 | 280 | 0 |
| D2-labeled resource samples | 84 | 84 | 84 | 0 | 84 | 0 |
| A/B2-labeled scheduler batches | 600 | 50 | 49 | 1 | 50 | 550 |

The lifecycle pass had 3,000 operations and no cap shortfall. Attribution recorded
696 provider operations with no missing provider results or helper timing records;
these are observations of the prior implementation, not qualifying D2 results.
The scheduler failure occurred at invocation 49 (the tenth B2-labeled warm batch),
during setup. It preserved 16 finished setup responses and did not start the timed
warm batch. Thus **551 timed batch observations are missing**, including failed
setup; 550 batches were never attempted. Fixture identity/settings validate all
50 attempted batches, including the failed mixed setup. The original report's
one workload exclusion conflated missing timed output with invalid fixture identity;
the audit separates them. All 50 are excluded from corrected comparison because
of the packaging mismatch. A completed 10 cold, 10 warm and 10 cancel batches;
the B2-labeled implementation completed 10 cold and nine timed warm batches. No
B2-labeled cancellation batch ran.

Evidence locations:

- Lifecycle and iteration gate: `build/preview-iteration-8a6an044`.
- Excluded attribution: `build/preview-diagnostic-h474ihmo/diagnostic-run-b8acf5fr`.
- Excluded resources: `build/preview-diagnostic-h474ihmo/resource-run-sf_d78gr`.
- Stopped/excluded scheduler: `build/preview-scheduler-8e1qu5ry/scheduler-run-medw8pyq`.

The surviving failure diagnostic reports a successful operation, no manager
commands, zero elapsed cleanup milliseconds, a reaped launcher and an unreadable
hierarchical observation. It lacks the new observation fields, consistent with
the frozen old source. This does not establish the syscall cause, nor prove or
disprove the corrected implementation. No retry or additional manager cleanup
was performed. The recurrence gates off further native **measurement** passes
for this iteration, including after repairing packaging.

### Corrected artifacts and verification

Fresh, verified packages are `build/preview-scheduler-f2c1ty8f` (A/B2) and
`build/preview-diagnostic-ymcm3gs7` (D2). B2 and D2 retain File Browser
`2f86c9b20c1a628d149a391e357acb83e878556a` and Thumbnails
`9462bacf7a7f7fdfb8f6eddb2edf1dac63ed75aa`; Images is based on
`b7e881ff81efc6d75304e1381cb68ddf6fdb0770` plus the exact archived correction.
A retains its original full revisions. Pre-build source inventories, patch hashes,
overlay hashes, compile commands/flags, runtime manifests and executable hashes
identify the inputs and outputs. Existing overlay contexts apply and validate
against the corrected implementation. B2 has no timing probes.

Verification is recorded under `build/cleanup-race-verification` and
`holonight-images/build/cleanup-race-release`: 16 deterministic cleanup tests,
provider capture/protocol regressions, native Release provider/installed/relocated
and runtime checks (9/9 across focused invocations), and scheduler barriers against
each final A/B2/D2 package. The nested-patch, malformed JSON, truncated telemetry,
missing-helper, partial-run, mixed-workload and stop-gate tooling regressions pass.
The initial sandboxed runtime verification was denied user-bus access before
helper startup; the same installed/relocated and runtime checks passed with native
access. A stale development bundle was rejected by installation before preparing
a fresh native bundle. These verification setup failures are separate from the
native measurement recurrence.

Focused File Browser and offscreen Files/chooser acceptance were rebuilt against
the corrected package after detecting the packaging error. Source formatting,
Python compilation, whitespace and focused C++ static analysis are checked.
The analyzer uses a copied compilation database without unsupported GCC flags;
existing trailing-comma warnings on unchanged runtime lines are excluded. No
unrelated container gate, deployment, publication, optimization or pin update was
performed.

**Remaining gate:** corrected lifecycle, D2 attribution/resource measurements and
all 600 qualifying A/B2 scheduler batches remain unmeasured this iteration.
Corrected timing/resource gaps are therefore complete, rather than zero estimates.
Runtime-generation reuse remains a conditional next experiment only after this
cleanup/evidence gate passes. Session reuse and prestarted workers stay out of scope.

## Fresh corrected Experiment 0 preparation (2026-11-09)

The fresh iteration stopped during its artifact audit, before any measured launch.
Evidence is preserved in umbrella `build/preview-iteration-qyruwtid/audit.json`
and `summary.json`; the earlier preparation-only rejection of additional CTest
logs remains in `build/preview-iteration-ec_m4h1w`. These are separate from all
historical native runs, failures and exclusions.

Requested artifacts remain scheduler `build/preview-scheduler-f2c1ty8f` (A/B2),
diagnostic `build/preview-diagnostic-ymcm3gs7` (D2), the rebuilt
`build/cleanup-race-verification/probe/cleanup-diagnostic`, and frozen fixtures in
`build/preview-experiments-ak2cd2cp/measure-fivw3ih0/fixtures`. B2/D2 correction
provenance agrees. The probe SHA-256 is
`30f9db400e358974f05a676fc5b0345838541855e4f9b13983688714afe39af6`.

B2's recorded `build/holonight-images/install_manifest.txt` differs from its
frozen inventory: expected SHA-256
`42f04300fb75b3bf77a6fe41a21460811491cdd63095bc98ce367c9606e0f325`
(9,701 bytes), observed
`5c93d2e527707c3879ff5c140ae8216de920c24b5a1d42a97451e88c833f79c0`
(10,205 bytes). Its current entries use the acceptance prefix. This is an
inventory mismatch, not evidence of a binary defect or a historical failure's
cause. The required stop-on-mismatch rule prevents measurement or rebuilding.
The audit does not certify the remaining preparation checks after that stop.
Additional CTest temporary logs are recorded separately; changed recorded files
are always rejected.

| Pass | Planned | Attempted | Completed | Failed | Excluded | Unattempted | Missing timed observations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Lifecycle cycles | 1,000 | 0 | 0 | 0 | 0 | 1,000 | 3,000 operations |
| D2 attribution | 280 | 0 | 0 | 0 | 0 | 280 | 280 |
| D2 resources | 84 | 0 | 0 | 0 | 0 | 84 | 84 |
| A/B2 scheduler | 600 | 0 | 0 | 0 | 0 | 600 | 600 |

There is no cap shortfall, runtime cleanup result, telemetry, helper timing,
resource read or sampling interval from this iteration. All native passes are
unattempted; none is inferred successful. Existing cleanup, provider,
installed/relocated, scheduler-barrier and Files/chooser acceptance remains reused
as previously recorded. Focused Python tooling verification passes 25 tests,
including zero-exit lifecycle failures, valid cap shortfalls, missing/truncated
output, partial denominators and artifact mismatch preventing launch. Python
compilation and whitespace checks pass. No production code, public API,
optimization, package rebuild, deployment, publication or pin update was made.

The runner now audits recorded package inventories and runtime manifests before
workload preflight, compares frozen fixture hashes, and preserves an explicit
preparation failure ledger. Lifecycle output is inspected regardless of exit
status; failed runtime/provider records and malformed or missing output gate
later passes while preserving valid partial observations. The ten-minute probe
cap remains unchanged. **Completion remains gated on resolving the inventory
identity discrepancy and then obtaining the entire corrected measurement matrix
with successful cleanup verification.** Runtime-generation reuse remains deferred.

## Corrected Experiment 0 completed (2026-11-09)

The new native iteration `build/preview-iteration-m9uucbpj` passed lifecycle,
D2 attribution, separately sampled D2 resources, and A/B2 scheduler control in that
order. `summary.json`, `audit.json`, child directories and the independent
`validation.json` retain the evidence. No builds, tests or static analysis ran
concurrently with measurement. Earlier preparation stops, native failures,
exclusions, reports, manifests and inventories remain historical and unchanged;
in particular `preview-iteration-qyruwtid` remains a failed preparation audit.

The explicitly selected `--acceptance-install-prefix` exception applies only to
B2's `build/holonight-images/install_manifest.txt`. Every entry must start with the
complete acceptance prefix plus `/`. Replacing that prefix in memory with
`build/preview-scheduler-f2c1ty8f/B2/prefix` reproduced the frozen SHA-256
`42f04300fb75b3bf77a6fe41a21460811491cdd63095bc98ce367c9606e0f325`
and 9,701 bytes, from observed SHA-256
`5c93d2e527707c3879ff5c140ae8216de920c24b5a1d42a97451e88c833f79c0`
and 10,205 bytes. Mode remained 0644. The full absolute prefixes and proof are in
`audit.json`. No manifest or inventory was rewritten. Without the option the
mismatch still fails. Added, removed, reordered, changed or differently prefixed
entries, mode changes and unrelated artifacts remain rejected. Only the two
previously named CTest temporary logs are allowed as additional inventory entries.

The audit verified 859 A, 871 B2 and 873 D2 recorded entries, installed runtime
manifests, correction provenance and all four frozen fixture hashes. Identities:

| Artifact | SHA-256 |
| --- | --- |
| Scheduler provenance | `5badbae16503e5738bff35a3c0cbd229960feca4e8be9660e3ce36062a25b280` |
| Diagnostic provenance | `62335285bce760c48b55d57449313a4bc9ebf341fd14c983d621e31821635ba8` |
| A inventory | `dbfc4f74bdb5aab1e60b766e52d59afe2a2ca2ba9edf34bff58125ba6b4bc8be` |
| B2 inventory | `9d6a0ef8084555b4a31fa6972471b231e44bba4b283c584bb6203d1b00a34127` |
| D2 inventory | `dfe77978474d043a86c76b197c7faa59dd886913eb4e7d50b074477641db2cf6` |
| Lifecycle probe | `30f9db400e358974f05a676fc5b0345838541855e4f9b13983688714afe39af6` |
| A scheduler executable | `e6df1cc698560e503a62d309ad74c5b63d22f3c6c9e87d88d12fb3f159ea3999` |
| B2 scheduler executable | `204dc837099dbce2841f9f9daba0cc2155a1c1f27754f38374202fad32b6e6b1` |
| D2 benchmark executable | `3c15a3ee7974f044d65e49d9f6eb6adac991477372589a1180a967a31a82fb85` |

Both Images libraries in the probe's recorded link inputs match B2: core
`2bda998d5efc77191dc92c692cc49ec5824c684b7151f52f80d15ac1c05dc0aa`,
isolated client
`a25db0128ac15fa0c4b8d8d414b3462766899221b87de7533e502d640508d7f8`.
Source revisions, correction hashes, executable inventories, tool snapshots,
workload descriptions and fixture hashes remain in package provenance and the
new audit. Cleanup/provider, installed/relocated, scheduler-barrier and
Files/chooser acceptance was reused unchanged; there was no rebuild or broad
acceptance rerun.

| Pass | Planned | Requested | Observed attempted | Completed | Failed | Excluded | Unattempted | Unreported requested | Missing timed observations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Lifecycle cycles | 1,000 | 1,000 | 1,000 | 1,000 | 0 | 0 | 0 | 0 | 0 operations |
| D2 attribution | 280 | 280 | 280 | 280 | 0 | 0 | 0 | 0 | 0 |
| D2 resources | 84 | 84 | 84 | 84 | 0 | 0 | 0 | 0 | 0 |
| A/B2 scheduler | 600 | 600 | 600 | 600 | 0 | 0 | 0 | 0 | 0 |

Lifecycle completed all 3,000 operations in 281.751 seconds, with no failed or
partial cycles and no cap shortfall. Attribution recorded 696 provider operations;
resources recorded 220. All provider results reported runtime success, with no
missing results, malformed/truncated telemetry, dropped records or missing helper
timelines. Both passes recorded 28 post-drain scope snapshots, all with zero scopes
and processes and no surviving tracked cgroup. Scheduler batches all drained;
cleanup failures were zero throughout. These checks establish cleanup for this
iteration, while one-second snapshots do not establish general leak freedom or
resolve historical failure causes. No retries or additional manager cleanup ran.

Each scheduler baseline/workload has 100 mixed batches: four copies of each
fixture, two threads, 256-pixel boxes. Both warm setup and timed fixture identities
were independently validated. Warm timed batches started zero decoders for A and
B2. Baseline order alternated in ten-batch blocks.

| Scheduler control | Median ms | p95 ms | Maximum ms |
| --- | ---: | ---: | ---: |
| A cold | 118.892 | 123.350 | 124.374 |
| B2 cold | 1,303.886 | 1,362.580 | 1,451.102 |
| A warm | 0.209 | 0.269 | 0.295 |
| B2 warm | 0.218 | 0.377 | 0.521 |
| A cancellation | 51.057 | 56.952 | 69.006 |
| B2 cancellation | 361.447 | 395.292 | 411.972 |

Attribution parent-phase medians were 47.111 ms runtime validation, 27.226 ms
launcher readiness, 3.209 ms cleanup and 0.186 ms unexplained parent time. The
independent helper execution median was 1.516 ms and reply serialization 0.041 ms.
These are nested observations, not additive independent latency components.
D2 instrumentation and resource sampling remain separate from scheduler controls
and frozen original A/B latency; none qualifies a candidate optimization.

Resource sampling requested 10 ms; actual intervals were 8.984–11.534 ms and all
intervals remain in the child report. Parent RSS, concurrent scopes, and their
concurrently sampled sum peaked independently at 60,829,696, 40,087,552, and
90,849,280 bytes. Their unavailable-read counts were 2, 6 and 8 respectively;
missing reads were never replaced with zero. Individual cgroup `memory.peak`
maximum was 46,485,504 bytes in this pass and remains separate from concurrent
sampled maxima. All 220 pre-ack CPU/memory reads were available. Transient peaks
between samples remain unobserved; scheduler response delivery is not rendered
QML frame latency.

The measurement runner and child tools were snapshotted before execution.
Focused verification passed 29 tests before native work, plus Python compilation
and whitespace checks. A subsequent parent reporting-only fix recovers partial
counts from retained child evidence when its summary is missing or malformed,
while still gating later passes; the final suite passes 30 tests. It did not
change or rerun measured operations or rewrite their reports. Preparation findings
also accumulate through read-only correction and inventory checks before gating.

**Corrected Experiment 0 is complete for the requested matrix and lifecycle.**
Runtime-generation reuse is now a reasonable next experiment to design, given
validation/readiness costs relative to helper execution, but any reuse must first
define fail-closed runtime identity and invalidation rules and preserve cleanup,
mutation and relocation contracts. No reuse implementation or performance change
was made. Deployment, publication, commits, pins, session reuse and prestarted
workers remain outside this iteration.

## Runtime-generation reuse design decision (2026-11-09)

The [Images design](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md)
records the approved **explicit-refresh contract**: a ready immutable generation
remains usable after source edits, removal or replacement until explicit refresh.
Refresh blocks new leases; existing leases may finish. Failed refresh leaves new
acquisitions unavailable without stale fallback; a later explicit refresh can recover.
Production retains full per-operation validation.

The private host-native sealed-memfd experiment is **no-go at the storage gate**.
Images `build/runtime-memfd-feasibility-eYAKqdW8/` preserves sources, commands,
hashes, host details and structured results. Using a disposable copy of the frozen
B2 helper, content seals blocked writes, truncation and shared writable mappings.
Even with `F_SEAL_EXEC`, a separate same-user process could chmod the captured
helper from `0755` to `0777` through the owner's proc descriptor. Exact validated
mode metadata therefore remained mutable. Frozen source inventories were unchanged;
all six probe children were reaped and parent descriptor counts returned to baseline.

The required stop gate prevented runtime launches and further owner implementation.
Gate/sandbox identity, full sealed-generation validation, refresh/lifetime behavior,
hierarchical cleanup and generation resource bounds remain unqualified. This is
not a content-seal bypass or a speedup result. The local design records the precise
failure and outstanding prerequisites. No production interfaces, installer behavior,
deployment, frozen packages or pins changed.

The [metadata contract review](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#metadata-contract-review-2026-11-09)
recommends **retaining exact mode immutability and the no-go**. Source validation
metadata, generation identity records and live backing metadata are distinct.
Mutable read/write bits do not undo content seals, but that does not qualify
special bits, ownership, security attributes or loader behavior. Same-user access
through owner proc descriptors remains in scope. Making the owner non-dumpable
would also deny ordinary launch descendants that need those paths; protection
requires a proven legitimate transport, not just attacker denial. The local
review maps invariants to evidence and uncertainty using Linux v7.0 sources and
primary documentation; matching the recorded Arch 7.2.14 host remains a prerequisite.

The bounded next experiment requires a different mechanism to pass static and
metadata gates before transport, functional or lifecycle work. It must preserve
exact modes and bind every consumer to validated objects while qualifying
ownership/security policy. No narrower contract is approved or proposed by this
review; any future narrowing requires explicit approval. Acquisition source modes,
exact inventory, location-independent identity and approved explicit-refresh
ordering stay unchanged. Verification was document/code/evidence review and
whitespace checks only; successful probe checks were reused, not rerun.

The [unprivileged static mechanism gate](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#unprivileged-storage-static-mechanism-gate-2026-11-09)
qualified **neither candidate**. Private tmpfs read-only publication is reversible
when the same-user namespace owner can regain mount authority; dropping builder
capabilities is insufficient. A sealed image served through FUSE has read-only
format properties, but daemon/connection isolation, security metadata policy,
mount substitution, launch access and bounded lifetime remain unresolved. Neither
mechanism establishes protection before unsandboxed gate execution.

The review found kernel FUSE support and existing FUSE mounts; missing `/dev/fuse`
in the sandbox's overlaid `/dev` does not prove host absence. SquashFUSE was not
found in the visible binaries/package database. These are development-host
observations. Portable qualification requires specific kernel/tool capabilities
and policy, not exact distribution patch identity; investigate patches only for
a concrete relevant semantic difference. Unavailable source is not a mechanism
failure.

The [bounded portable FUSE follow-up](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#portable-fuse-qualification-follow-up-2026-11-09)
assesses one adapted SquashFUSE 0.6.1 construction: a sealed image, dedicated
unprivileged daemon and parent-held leaf handles. **Retain no-go.** Daemon-local
non-dumpability does not suffice in a user namespace owned by the same user;
keeping the daemon in the original namespace instead leaves an unprotected
startup interval unless a protected bootstrap is established. Parent-memory
trust does not exclude attacks on this new daemon. Neither changing parent
security nor assuming stronger host tracing policy is accepted here.

Pinned leaves resist later mountpoint substitution, but do not authenticate FUSE
replies. The design specifies required no-xattr/ACL/capability image policy,
exact modes and mapped ownership, and distinguishes image metadata from effective
LSM execution policy. Served immutability, pre-gate enforcement, parent-proc
reopening through QProcess/systemd/gate/bubblewrap and bounded daemon lifetime
remain unresolved. Direct user-namespace FUSE mounting is a source-established
primitive; protected mounting/transfer, image tooling, resource caps and teardown
require adaptation. Payload limits do not cover daemon/cache/queue overhead by
themselves. These concrete blockers, rather than missing distribution patches,
stop qualification. No construction is selected and no metadata probe is ready
or authorized. The memfd no-go, exact modes, inventory, location-independent
identity and explicit-refresh contract are retained, without a privileged broker or broader parent security changes. This
step used read-only inspection and whitespace checks only; no native experiments,
builds, deployment, commits or pin changes were made.

## Full runtime validation profile (2026-11-09)

The [Images validation-only profile](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#full-per-operation-validation-profile-2026-11-09)
completed one bounded host-native run. **Retain full per-operation validation
unchanged; generation reuse remains no-go.** No worthwhile optimization preserving
every check was established.

Private baseline and instrumented Release builds used identical archived Images
source and host dependencies. Only the private copy received instrumentation.
The preserved 60-payload, 87,198,752-byte runtime matched its earlier inventory and
was copied with modes intact. All ten valid/fault cases produced the expected
matching results. Five warm-ups per variant preceded 100 measured validations per
variant in alternating-order pairs, using persistent harnesses and one validation
at a time. No runtime payload, decoder, scope or sandbox was launched.

Baseline total median/p95 was **42.457/42.886 ms**; instrumented was
**42.760/43.196 ms**, a **0.713% median increase**, below the 10% attribution gate.
Combined reading/SHA-256 checking had a **40.894-ms median**, accounting for
**95.610%** at the median of per-call total fractions. Reading and hashing cannot
be separated from that interval. Median phase coverage was **99.973%**. All 200
measured validations succeeded with no missing observations or failures; descriptor
counts stayed at five, all four harnesses were reaped, and both runtime inventories
remained unchanged. These are warm-cache, validation-only measurements on one host;
they do not predict whole-preview savings or replace the historical 47.1106485-ms
validation median. No new phase is subtracted from historical measurements.

Evidence is in ignored Images `build/runtime-profile-nodkmzws/`, including archived
source, overlay patches, provenance, binary hashes, raw observations, per-file
bytes/timings, summary and verification. Seven focused accounting tests passed
before measurement. Private overlay review and whitespace checks completed; the
preview matrix and installed-package suite were not rerun because production and
installation behavior are unchanged. The single recommendation is to keep the
existing validator. No production optimization, public API, caching, freshness or
security-policy change, deployment, publication, commit or pin update is included.

## Qt SHA-256 path review (2026-11-09)

Historical review: its source-checksum blocker is superseded by the
[provenance reconciliation below](#qt-package-source-provenance-reconciliation-2026-11-09).
The candidate remains unqualified.

The [bounded Images review](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#qt-sha-256-path-review-2026-11-09)
ends with **stop with no qualified candidate**. Installed QtCore 6.12.0-3 binary
inspection confirms a 1 KiB device-read loop and OpenSSL EVP initialization,
updates and finalization. QFile/QIODevice buffering means this is not evidence
of one syscall per KiB. CPU SHA-NI capability does not establish actual provider
or assembly dispatch in the validator.

Exactly one candidate was reviewed: a bounded 64 KiB streaming loop feeding the
same Qt SHA-256 object, retaining every validation check. It plausibly reduces
repeated read/update overhead, but the combined read/hash timing cannot estimate
savings. Current Qt stops on zero or negative reads and returns `atEnd()`;
unconditionally rejecting negative reads would change its acceptance policy.
Larger requests also change buffering/error boundaries, whose equivalence remains
unqualified. No stronger concurrent-mutation protection is claimed.

Fresh primary Arch recipes confirm package versions and the recorded Qt source
checksum, but the cached Qt tag archive still does not match that checksum.
Exact distribution-source provenance remains unresolved; binary correspondence
does not close that gap. Installed library paths, hashes/build IDs, source revision,
patch review, commands, disassembly and findings are retained in ignored Images
`build/qt-sha256-review-20261109/`. The local design records the semantic comparison,
unchanged manifest/path/inventory/regular-file/exact-mode/size/required-entry/full
SHA-256 checks, and correctness obligations should this candidate be reconsidered.

Production validation and public APIs remain unchanged; generation reuse remains
no-go. Historical measurements are preserved. This step used document/evidence
review and whitespace checks in both repositories, with no tests, builds,
benchmarks, frozen-runtime execution/modification, installation, deployment,
commits or pin updates. No private experiment is qualified or executed.

## Qt package-source provenance reconciliation (2026-11-09)

The [bounded Images investigation](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#qt-package-source-provenance-reconciliation-2026-11-09)
ends with **provenance reconciled; no qualified candidate**. Makepkg's
`download_git()` disables `export-subst` and `export-ignore` before its checksum
command runs. Applying that documented sanitation only in a fresh primary Qt
clone reproduces the recipe SHA-256
`d97ef157dc50bdf0425337e9adede8135ab508a4ab2f1abae7e9cfc42c5f86db`.
Without it, both fresh and cached clones produce the historical `f24f…6208` hash.
The archive differences are 38 restored attribute/ignore files and an
unsubstituted `.tag`; the seven reviewed hashing/I/O files are unchanged.

The cached Qt package signature verifies with existing distribution trust, and
its QtCore payload matches the installed library hash/build ID. The signed build
metadata matches the fresh Arch recipe. Fresh Qt tag/commit/tree identities match
the cache; the build-version makepkg script matches the installed script. The two
recipe patches and three primary cherry-picks do not directly edit the reviewed
files. Evidence, commands, hashes and source citations are retained in the local
design and ignored Images `build/qt-provenance-20261109/`. This reconciles source
provenance; it does not independently reproduce the installed binary or resolve
OpenSSL provider/assembly attribution.

Recommend a separate bounded correctness review of the same 64 KiB loop before
qualification. No implementation, read/error tests or benchmark was performed.
Production validation and public APIs remain unchanged; generation reuse remains
no-go. Historical review and measurements are preserved. Verification covered
package/source identity, exact checksum reproduction, archive contents/metadata,
patch target paths, citations, document agreement and whitespace checks in both
repositories. No builds, frozen-runtime execution/modification, installation,
trust changes, alternative backend/storage investigation, commits, publication or
pin updates were performed. The cached sources and `holonight-grub/` were untouched.

## Bounded hash correctness review (2026-11-09)

**Bounded correctness agreement established.** The private
[Images experiment and evidence](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#bounded-hash-correctness-review-2026-11-09)
compared the installed Qt device overload with the same reviewed 65,536-byte
loop. Installed QtCore still matches the reconciled `6.12.0-3` SHA-256/build ID;
no repeated provenance investigation was needed.

All 98 device pairs agreed: 14 ordinary buffered QFile sizes (including NULs and
boundary cases), two device guards, 72 buffered/unbuffered seekable-device fault
cases and ten actual borrowed-descriptor QFile error cases. Controlled negative
reads with end true completed with the prefix digest in both variants; they did
not match the full input. Real descriptor invalidation before hashing or after
controlled byte offsets produced read errors, end false and failure in both.
Read request/return counts remain diagnostics, not equality requirements.

Both host-native validators, built from one Images HEAD archive, matched expected
verdicts for all ten existing valid/manifest/content/mode/symlink cases. Only the
candidate archive received the guarded device-call replacement. The 61-entry
preserved B2 inventory matched before copying and after testing; each variant and
case had a fresh disposable copy. Frozen payloads were never executed. All 231
command children were reaped with no timeout, failure or retry. Four focused
runner tests and whitespace checks passed; evidence remains in ignored Images
`build/hash-correctness-h3eyasci/` with hashes in the local design.

This is finite agreement, not universal error equivalence or concurrent-mutation
protection. A separate bounded performance experiment may be considered; no
benchmark was run and worthwhile savings remain unestablished. Production
validation, APIs and installation are unchanged, production integration is not
authorized, and generation reuse remains **no-go**. Historical measurements and
provenance findings above remain intact. No deployment, installation, commit,
publication or pin update occurred; Grub was untouched.

## Bounded hash performance experiment (2026-11-09)

**Worthwhile savings not demonstrated.** The
[Images full-validation experiment](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#bounded-hash-performance-experiment-2026-11-09)
completed three warm-cache blocks with 50 measured pairs each, after five excluded
warm-up pairs per block. The fixed gates required median paired savings of at
least 4 ms and 10%, and candidate p95 at most 105% of baseline p95, in every block
and pooled. These are practical gates, not statistical significance claims.

| Block | Baseline median / p95 ms | Candidate median / p95 ms | Median paired savings ms / % |
| --- | ---: | ---: | ---: |
| 1 | 41.851 / 42.804 | 40.685 / 41.247 | 1.158 / 2.758% |
| 2 | 42.223 / 44.863 | 41.141 / 42.398 | 1.064 / 2.500% |
| 3 | 42.380 / 44.169 | 41.482 / 42.630 | 1.027 / 2.480% |
| Pooled | 42.101 / 43.932 | 41.071 / 42.345 | 1.114 / 2.654% |

Every block missed both savings thresholds; all p95 gates passed. All ten
validator cases agreed in both variants, and the unchanged 98-case device
evidence was reused. Installed QtCore identity, candidate/source/overlay identity,
frozen and disposable inventories, metadata, descriptors and child cleanup
checks passed. All samples are retained, without retries or trimming.

Evidence is in ignored Images `build/hash-performance-cyws85n4/`, with hashes,
host context, qualification details and limits in the linked local design.
Seven focused tooling tests passed before execution; post-run idle-watchdog
hardening added an eighth passing test, recorded separately without repeating
the measurement. Both repository whitespace checks passed. No full preview or
installed-package suite, deployment, installation, commit, publication or pin
update was performed. Grub was untouched.

The conclusion is limited to this host, preserved B2 fixture and warm-cache
full-validation workload. It implies neither whole-preview savings, universal
error equivalence nor concurrent-mutation protection. Production integration
remains a separate decision and is not justified by the agreed savings gate;
generation reuse remains **no-go**. Historical findings above remain intact.


## Hash candidate closure and launcher-readiness review (2026-11-09)

**Close the 64 KiB hash candidate without production integration.** The
[Images evidence review](../../holonight-images/docs/sdd/runtime-generation-reuse/DESIGN.md#hash-candidate-closure-and-next-target-evidence-review-2026-11-09)
checked preserved policy/observation/summary hashes and recomputed three complete
blocks: 150 measured validations per variant, with 15 excluded warm-ups each.
Pooled paired savings remain **1.114 ms / 2.654%**. Every block and pooled result
misses both savings gates; all p95 gates pass. Retain the bounded 98-device-pair
and ten-validator-case agreement, without claiming universal error equivalence.

Corrected Experiment 0 tool/provenance/inventory/executable/fixture identities,
D2 overlays and archived Images source matched the relevant recorded hashes.
Independent validation, child reports, attempt intervals and cleanup records
agree: 1,000 lifecycle cycles / 3,000 successful operations, 280 attribution
cases / 696 operations, 84 resource cases / 220 operations, and 600 scheduler
batches. Parent/helper medians and scheduler median/p95 were recomputed read-only;
no frozen evidence was regenerated. Both D2 passes retain 28 settled zero-scope
snapshots. The acceptance-prefix-only manifest exception remains historical.

| Existing measurement | Median ms | Denominator / limitation |
| --- | ---: | --- |
| D2 validation | 47.111 | 696 operations, zero missing |
| D2 readiness | 27.226 | Inspection 27.486 (348), source decode 27.103 (308), cached PNG decode 26.755 (40); zero missing |
| D2 request / response receipt | 0.035 / 1.780 | 696 each; response includes helper work, not pure transfer |
| D2 helper execution / serialization | 1.516 / 0.041 | 696 each, zero missing; nested within parent work |
| D2 acknowledgement / cleanup | 0.882 / 3.209 | 696 each, zero missing |
| A/B2 cold scheduler | 118.892 / 1,303.886 | 100 mixed batches each; warm medians 0.209 / 0.218 with zero decoder starts |
| Validation-only baseline | 42.457 | 100 calls; separate warm-cache profile, not replacement D2 timing |

The local review preserves per-operation-kind parent timings. Consumer phases
have 460 observations and 40 missing among 500 jobs. Separate resource sampling
has unavailable parent/scope/combined reads of 2/6/8; all 220 pre-ack reads are
available. Scheduler has 100 batches per variant/workload and zero missing timed
samples; cancellation medians remain 51.057 / 361.447 ms. These domains remain
separate: no median addition or cross-experiment subtraction predicts speedups.

Archived instrumentation starts readiness just before QProcess starts systemd-run
and ends after the parent receives the sandbox helper's `R`. Current launch code
preserves the sequence: process startup, scope discovery, actual memory/swap limit
verification, gate release, bubblewrap setup, helper loading/initialization and
readiness delivery. Validation and command construction precede this timer;
request framing/transfer follows it. D2's `helper_launch` event marks QProcess
startup; its `scope` event occurs after readiness. Neither times scope discovery
or sandbox startup separately. Five-ms wait bounds do not prove polling dominance;
systemd, bubblewrap, loading and observation delays are unresolved contributors.

Retain full per-operation validation and the generation-reuse **no-go**. Do not
reopen hash tuning, storage mechanisms, session reuse or prestarted workers.
Verification was read-only evidence/source review, document consistency and both
repository whitespace checks. No builds, benchmarks, payloads, test suites,
experiment tooling, installation, deployment, commits, publication or pins changed;
frozen evidence and Grub remain untouched.

**Recommend a separate launcher-readiness profiling design.** Determine which
internal intervals account for the approximately 27-ms interval, distinguishing
execution from parent observation delay. Proposed boundaries are pre-start,
QProcess-start completion, scope discovery, verified limits, gate write/consumption
and pre-exec, sandbox-helper entry, readiness flush and parent receipt. Account for
overlap, clock comparability, missing data and instrumentation overhead; do not
attribute unresolved pre-entry time to the loader or sandbox without observations.
Preserve full validation, fresh scopes/helpers, verified limits before release,
sandbox security, protocol, cancellation/deadlines and hierarchical terminal cleanup.
This recommends a design only; it does not authorize or implement the experiment.

## Bounded launcher-readiness profiling design (2026-11-09)

The [dedicated Images specification](../../holonight-images/docs/sdd/launcher-readiness-profile/DESIGN.md)
defines a future private host-native Release experiment for source inspection,
source decode and cached PNG decode separately. Three serial blocks contain
three excluded warm-up pairs and 20 measured reference/detailed pairs per kind:
**180 measured calls and 27 warm-ups per variant**. Both variants derive from
one archived revision and use disposable, fully validated runtime bundles.

Observation boundaries cover process start, scope discovery, verified limits,
gate write/consumption/exec, helper entry, readiness flush and parent receipt.
The design requires comparable monotonic clocks, bounded stderr capture through
exec, actual wait observations and per-call overlap accounting. Bubblewrap and
dynamic-loader work remain combined where the observations cannot separate them;
flush completion and parent receipt need not occur in that order.

Detailed/reference outer-readiness median and nearest-rank p95 ratios must each
be at most **1.10**, per kind in every block and pooled by kind. These are practical
instrumentation-overhead gates, not significance or optimization gates. Failed
gates or incomplete evidence yield no qualified attribution; retain all samples
without retries, trimming or budget expansion. Future focused tooling and runtime
qualification must cover success, cancellation, timeout, failed readiness and
bounded termination/reaping with hierarchical cleanup proof and partial evidence.

Historical measurements and hash-candidate closure are preserved. Full validation,
fresh helpers/scopes, verified limits before release and sandbox/protocol/lifecycle
contracts remain required. Generation reuse remains **no-go**; hash tuning,
storage mechanisms, session reuse and prestarted workers stay closed. Verification
for this documentation change is current/archived source review, three-document
consistency and whitespace checks only. No builds, tests, benchmarks, runtime
payloads, production/API/dependency/installation changes, commits or publication;
frozen evidence, Grub and pins remain untouched. The design is ready for separate
implementation review and authorizes neither implementation nor execution.


## Bounded launcher-readiness run outcome (2026-11-09)

The authorized [Images private experiment](../../holonight-images/docs/sdd/launcher-readiness-profile/DESIGN.md#execution-results-2026-11-09)
ended with **no qualified attribution**. Both host-native Release variants built,
but qualification stopped on call six: a private fault-controller race cancelled
before helper entry. Five cases passed; cleanup of the final case proved cgroup
removal and launcher reaping after TERM/KILL in 1.021 seconds. Thirty qualification
calls and all 414 measurement/warm-up slots remained unattempted; there are no
qualified distributions or overhead ratios. The executed snapshot remains intact;
a controller correction passed offline checks without a native retry. Production,
installation, frozen evidence and pins are unchanged. Generation reuse remains
**no-go** and all previously closed optimization directions stay closed.


## Ranked launcher-readiness follow-up (2026-11-09)

The authorized [follow-up profile](../../holonight-images/docs/sdd/launcher-readiness-profile/DESIGN.md#ranked-follow-up-results-2026-11-09) completed all 36 qualification calls
and the unchanged 414-call schedule (180 measured and 27 warm-ups per variant),
without recovery, replacement or trimming. **No qualified attribution**:
source-decode block 1 p95 (1.2746), block 3 median (1.1055), pooled p95 (1.1207),
and cached-PNG block 2 p95 (1.2056) exceeded the 1.10 overhead limit.

Descriptively, all kinds and blocks had the same median ranking: startup through
observed scope discovery, combined sandbox/helper loading, verified limits to
gate consumption, helper initialization to parent readiness receipt, actual
limit verification, then gate consumption to pre-exec. The first interval led
58/60 detailed measured calls per kind, with pooled medians of 15.797 ms for
inspection, 15.815 ms for source decode and 15.779 ms for cached PNG decode.
Full per-block/pool counts, median/p95 durations, per-call shares, largest counts,
nested timings and actual waits are in the linked SDD and retained summary.
These remain descriptive observations because the full overhead gate failed.

Evidence is retained in Images `build/launcher-readiness-7cv0vdaw`; the original
failed attempt remains unchanged. Fresh reference/detailed host-native Release
builds succeeded. All 450 calls have verified cleanup and reaped launchers;
all recorded cgroups were removed at final audit. Tooling, fixture and runtime
inventories remained unchanged. Seventeen focused tests, changed-Python syntax
and whitespace checks pass; no unrelated suites were repeated. This is readiness,
not total decode latency: scope observation is not pure systemd time and
bubblewrap/loader work cannot be separated. No historical savings are inferred.
Production/API behavior, installation, dependencies and pins remain unchanged;
generation reuse remains no-go and closed optimization directions stay closed.
No commits or publications were created.


### Offline readiness review (2026-11-09)

The [paired-sample review](../../holonight-images/docs/sdd/launcher-readiness-profile/DESIGN.md#offline-paired-sample-review-2026-11-09) retains **no qualified attribution**.
All 180 measured pairs were preserved. Median detailed-minus-reference paired
differences were +0.172 ms for inspection, +2.028 ms for source decode and
+0.130 ms for cached PNG decode; pair-order and within-block effects were mixed.
Failed tails span discovery waits, gate delay and combined sandbox/helper
loading. Roughly 96% of P0→S was spent in observed discovery waits, but actual
scope availability was not timestamped, so this is not removable-delay evidence.
Reference samples contain only outer boundaries; detailed child clock probes
and diagnostic writes remain an unquantified potential observer effect.

No demonstrated tooling defect explains the four failed gates. Accept the
current attribution limit; do not repeat the broad run or optimize production
from these observations. Any further work should first design a focused,
minimally intrusive way to distinguish scope availability from parent discovery,
with comparable parent observations and valid clock qualification. No new run
was performed or authorized by this review. Original evidence remains unchanged;
reproducible offline outputs are in Images `build/launcher-readiness-review-20261109`.
Verification covered retained-data consistency, reproduced gate ratios, input
hashes, script syntax, source inspection and whitespace. Closed optimization
directions and the generation-reuse no-go remain unchanged.

### Focused experiment design draft (2026-11-09)

The [Images scope-discovery plan](../../holonight-images/docs/sdd/launcher-readiness-profile/DESIGN.md#focused-scope-discovery-experiment-plan-2026-11-09)
proposes a parent-only, inspection-only experiment bounding membership visibility
versus parent discovery using existing reads. Read semantics and monotonic scope
membership must first pass a feasibility review. Control and observed variants
share parent boundaries; additional query/wait timestamps are overhead-gated for
both discovery and outer readiness. The proposed cap is 150 calls with no retry.
This draft authorizes no implementation, native execution or production change;
previous evidence and closed optimization directions remain unchanged.

### Focused scope-discovery execution outcome (2026-11-09)

**No qualified scope-discovery attribution.** The subsequently authorized
[Images parent-only experiment](../../holonight-images/docs/sdd/launcher-readiness-profile/DESIGN.md#focused-scope-discovery-execution-outcome-2026-11-09)
completed all 150 calls (12 qualification, 18 excluded warm-ups, 120 measured
inspections). Conditional host-source feasibility, qualification, cleanup,
completeness and integrity passed. Outer-readiness gates failed for block 0's
median ratio (1.113138) and block 1's p95 ratio (1.183387), above 1.10; passing pooled
and discovery gates cannot override them. There was no retry or recovery.
Descriptive uncertainty width: pooled median 5.146505 ms, p95 5.291018 ms, maximum
5.616598 ms, with zero censored calls among 60 measured observed calls. Evidence
and complete statistics remain in Images `build/scope-discovery-9zyg2nw0`.
Verification included the existing 17 and new 13 focused tests, native Release
builds and prepared bundles, overlay review, syntax/formatting/whitespace checks
and a reproduced post-run audit. Production contracts, installation, historical
verdicts and closed optimization directions remain unchanged. No decoding result,
exact availability timestamp, savings estimate or removable wait is inferred.

## Consumer acceptance lanes and local publication gate

Files and chooser register portable CTest selections and explicit required host
selections (`task test:isolated`). Checked-in inventories cover every enumerated
case exactly once and reject stale names. Presentation-only cases stay portable;
isolated inspection, source/cache decoding, cancellation and cleanup run on the
host. Opt-in performance/native-interaction cases retain their existing controls;
they are not substitutes for required runtime acceptance. No production API,
codec allowlist, runtime discovery, installer protection or UI behavior changes.

Prepare Files' synthetic runtime with its `scripts/prepare-test-runtime.py`, using
the host helper and a fresh ignored output directory. Only this non-installed
bundle substitutes the private TIFF codec. The portable subprocess trap and host
known-size positive control are required evidence; worker failure is never a
successful unknown-dimension rejection.

The local publication gate uses explicit executable and evidence paths:

```sh
python3 scripts/check-isolated-previews.py \
  --prefix "$PREFIX" \
  --runtime "$PREFIX/libexec/holonight-images/runtime" \
  --test-runtime "$PWD/holonight-files/build/unknown-size-runtime" \
  --files "$PWD/holonight-files/build/dev/tests/files-native-preview-lab" \
  --files-tests "$PWD/holonight-files/build/dev/tests/files-smoke" \
  --unknown-tests "$PWD/holonight-files/build/dev/tests/files-unknown-dimensions" \
  --portal "$PWD/xdg-desktop-portal-holonight/build/dev/tests/portal-tests" \
  --provider "$PROVIDER_BUILD/tests/isolated-package-test/build/isolated-consumer" \
  --fixtures "$PROVIDER_BUILD/tests/fixtures" \
  --output "$PWD/build/isolated-consumer-evidence"
```

Use a disposable host-native staged prefix, never `/usr` or `/usr/local`.
Build the installed-provider probe and both consumers against that same prefix.
Use fresh build directories or explicitly update cached `HolonightImages_DIR`,
`HolonightThumbnails_DIR` and `HolonightFileBrowser_DIR`: changing
`CMAKE_PREFIX_PATH` alone does not replace previously cached package locations.
The output must be new and outside the prefix. The gate runs existing installed
provider acceptance, consumer host selections, passive Files observation and
rendered application checks. It copies the prefix for relocation, temporarily
renames the original so it is unavailable, and restores it in a `finally` block.
Each invocation gets separate configuration/cache/data/state directories.
Commands, results and logs are retained; `complete.json` appears only after both
phases succeed. Missing user manager, namespaces, cgroup support, invalid runtime,
failed/skipped required tests and incomplete execution fail the gate. Images
continues to use the real session manager; only the chooser gets the private,
non-activating bus. Existing provider cleanup checks remain authoritative.

Run offline runner checks before integration:

```sh
python3 scripts/check-isolated-previews-test.py
python3 holonight-files/scripts/check-test-lane.py
python3 xdg-desktop-portal-holonight/scripts/check-test-lane.py
```

Run both consumer container gates with the current sibling providers when testing
unpublished coordinated changes (`task check -- --siblings "$UMBRELLA"`). Hosted
runner provisioning, deployment, publication and pin updates are outside this gate.

## Viewer static raster consumer

Viewer now routes raster metadata and first-frame decode through separate isolated
operations on its existing worker. Its [local design](../../holonight-viewer/docs/sdd/isolated-static-raster/DESIGN.md)
defines explicit runtime configuration, separate runtime/provider statuses, incomplete
EXIF handling, cancellation and successful-cache-only behavior. The consumer makes no
atomic-snapshot claim and has no in-process fallback. Its format policy is PNG, JPEG,
BMP, TIFF, WebP and GIF, with named/untagged color spaces only; unsupported valid profiles
are rejected. SVG remains available through its existing path.

Viewer's portable/private-bus and required host lanes are distinct. Installed and
relocated host-native probes pass explicit runtime paths to document and thumbnail
composition and exercise rendered output with the original prefix unavailable. Final
acceptance on 2026-11-09 passed 209 portable and 182 required host cases, CLI opening,
24 container CTest checks, static/QML/package checks and both installed rendering
phases; the Viewer SDD records the evidence. Container binaries are package
acceptance only. GIF playback after frame zero and SVG still execute in-process: this
is static-raster isolation, not complete Viewer isolation. Installer protections,
provider APIs/protocols, publication and dependency pins are unchanged.

## Registered repository publication (2026-11-10)

With publication and pinning authorized, all 19 registered component repositories
were checked against their configured remote `main` branches. Thirteen branches
advanced, including the Images, File Browser, Files, Viewer and portal work recorded
above. Twelve consumer manifests now pin the published provider revisions in dependency
order; all 42 provider entries agree with the coordinated component heads. The umbrella
gitlinks record those heads. Package Manager and Greeter were fast-forwarded to their
already-published remote tips before their pin updates. The unregistered Grub repository
remains untouched, as explicitly requested.

Existing implementation acceptance evidence was reused. Pin updates preserve manifest
ordering and build options and were checked for valid full hashes, remote reachability,
clean component worktrees and dependency consistency. Images' recorded full integration
entry-point limitation from experimental formatting remains; this publication does not
claim that unrelated gate was repaired. No deployment or image publication was performed.
