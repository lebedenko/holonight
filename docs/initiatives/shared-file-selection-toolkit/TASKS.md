# Delivery and verification

- File Browser: independent provider extraction; public scanner and identities;
  optional Search/Storage/Preview/PreviewQuick/Markdown; installed consumer coverage.
- Files: installed package adoption; local editing and settings policy adapters;
  preserve operations, recursive finder, devices and preview presentation contracts.
- Viewer: shared scanner, deterministic ordering, grid movement/presentation and
  thumbnails; preserve document and portal Open behavior.
- Portal: installed Core/Quick/Search and native identity helpers; preserve protocol,
  lifecycle, filters, choices and validation.
- Umbrella: dependency order, provider manifests, ownership-transfer and collision
  regression tests; component and integration verification; manual native acceptance.
- Publication: authorized by the user; provider published before its consumers and
  all four repositories pinned by the umbrella.

Implemented in the independent provider and all three consumers. The new
repository is published at https://github.com/lebedenko/holonight-file-browser.
Consumer manifests pin its published revision and the published dependencies used in
integration acceptance. The umbrella registers the provider submodule and pins all
four repositories. Explicit `--siblings` acceptance remains available for development.

Automated verification on 2026-10-16:

- Provider: all 12 CTest entries, external C++/QML consumers for every optional
  component, separate Core-only build/install, formatting, static analysis, QML and REUSE.
  The exact publication CI command also passed with published, pinned dependencies:
  12/12 full-component tests and 2/2 Core-only tests.
- Files: all 20 CTest entries; 44 focused sorting/scanning/shutdown tests after the
  editing adapter change; QML/static checks; Release staging, isolated installed desktop
  launch, failure fixtures and filesystem-isolation tests. Host-built staged launch passes.
- Viewer: all 27 CTest entries and component acceptance; 120 focused host thumbnail/grid
  tests after native thumbnail identity changes. Portal: both tests and component acceptance.
- Umbrella: full `task check:integration -- --siblings ...` passed. The final changed
  provider/consumer sources also passed together in the resulting installed prefix:
  provider 12/12, Files 20/20, Viewer 27/27 and portal 2/2 CTest entries.
- Packaging: all 109 umbrella Python checks pass, including ownership transfer,
  overwritten staging inventories, collision refusal and conservative uninstall
  regressions. All 18 CMake install manifests have disjoint
  paths; only File Browser owns the browsing package.

New regressions cover undecodable filenames with identical display strings in refresh,
search snapshots, selected previews and cached thumbnails; root-directory snapshot
identity; refresh failure; cancellation and shutdown. Incremental ecosystem testing
prefers freshly built component libraries over a previous installation in the same prefix.

Remaining user-operated checks: Files editing, finder, devices and previews; portal
Open/Save/multiple selection; Viewer grid, thumbnails and playback. Use host builds
with the development prefix's `lib/qt6/qml` and `lib` in `QML_IMPORT_PATH` and
`LD_LIBRARY_PATH`. Container binaries remain acceptance artifacts.

## Native closure walkthrough — 2026-10-16

Preparation verified clean provider and consumer checkouts matching both umbrella
gitlinks and their locally recorded `origin/main` publication refs:

| Repository | Revision |
| --- | --- |
| File Browser | `30d3af4f8c819a9377efeab33626c4e08e2987b4` |
| Files | `d6f5e33a8b4ae10ca3bbcb3dff78d4be7446f999` |
| Viewer | `db4abc6b6f51c100fb6c3ab62fc0f92bade10f11` |
| Portal | `ca325b0c792d07df6d765902f71918effc6422e5` |

Host: Arch Linux, Linux `7.2.9-arch1-1`, Qt `6.12.0`. Existing Debug CMake
builds reference the matching source checkouts and host Qt under `/usr`;
consumers resolve the installed File Browser package from `build/file-browser/prefix`.
Unchanged sources retain the automated acceptance recorded above. Build refresh
logs use `build/file-browser/*-walkthrough-build.log`; provider installation uses
`provider-walkthrough-install.log` in that directory.
All four incremental host builds and the provider's prefix installation passed.
Files runtime linkage resolves the shared browsing libraries from that prefix and
Qt from the host. The Files walkthrough window was launched with disposable
configuration, state and cache; its user-operated scenarios remain pending.

Disposable fixtures and native runtime logs are under ignored
`build/file-browser/walkthrough-2026-10-16/`. Fixtures include editable files,
nested finder matches, text/Markdown previews, three ordered PNG images, an animated
GIF and an existing Save destination. Native launches use the development prefix's
`lib/qt6/qml` and `lib` in `QML_IMPORT_PATH` and `LD_LIBRARY_PATH`.

| Application | Required scenarios | User result |
| --- | --- | --- |
| Files | Navigation/selection; create/rename/copy/move/delete; image/text/Markdown previews | Passed by user report on 2026-10-16 |
| Files | Recursive finder | Exercised; ranking deferred to Shared Search, local traversal repair accepted natively below |
| Files | Available storage device browsing and recovery after removal | Passed by user report: all other Files checks passed |
| Portal | Single Open, multiple selection, folder selection, Save; navigation/filtering/keyboard/cancel; returned paths and overwrite confirmation | Pending |
| Viewer | Ordered browsing, thumbnail grid navigation/selection, animation play/pause, Open/cancel document behavior | Pending |

Portal and Viewer confirmation is pending. Keep the initiative awaiting manual acceptance;
unavailable scenarios do not count as passes. The separate FileChooser portal
initiative's broader acceptance remains unchanged.

### Finder triage after native feedback

The user reported poor ranking for `finder-match` under Home, slower indexing,
and suspected loss of startup background indexing. Ranking is explicitly deferred
to the [open Shared Search initiative](../shared-search-engine/TASKS.md).

Startup warmup remains connected to the first rendered frame, unchanged from
Files' immediate pre-extraction revision `d6f5e33^`. The walkthrough generated a
76 MiB Home snapshot. Focused host tests
`HomeWarmupAttachesAndPersistsAcrossModelRestart` and
`ForegroundRootPreemptsHomeAndWarmupResumes` passed (2/2). This verifies the
model lifecycle; it does not measure startup-to-index latency. The launch used an
empty disposable cache and default settings, so normal cached results and user
exclusions were not reused.

A controlled traversal comparison compiled the immediate pre-extraction scanner
against the same installed types and compared it with the current host Debug
scanner, both unoptimized, on 100 directories containing 20,000 files. Six alternating
runs returned the same 20,100 candidates: baseline 53.3–54.2 ms, extracted
186.9–191.6 ms (about 3.5 times slower). This measures traversal only, with warm
filesystem caches, not end-to-end Home indexing. Evidence and the disposable
benchmark source remain under `build/file-browser/walkthrough-2026-10-16/`;
results are in `logs/scanner-benchmark-debug.log`.

The extraction replaced lightweight recursive traversal with `walkDirectory`,
which builds full listing entries, timestamps and icon names, including entries
later discarded by hidden/exclusion policy. Treat this confirmed traversal cost
as an open extraction regression to address before toolkit closure; preserve native
path identity and existing filtering/cancellation behavior. Ranking changes and
broader indexing optimization belong to Shared Search. No product source fix or
post-fix acceptance is claimed by this triage.

### Recursive finder traversal repair — 2026-10-16

The local provider fix replaces search's listing-oriented `walkDirectory` call
with RAII-managed `opendir`/`readdir` enumeration. Native directory and entry bytes
remain authoritative; display and exclusion strings are decoded at the boundary.
Known entry types avoid metadata construction; unknown types and symlinks use
`fstatat`. Hidden names are skipped early, exclusions prune directories before
queuing, and file links/readability checks, depth-first traversal, 256-candidate
batches, final partial batches and cooperative cancellation are preserved. The
listing scanner, warmup/scheduling, ranking, public API and package layout are unchanged.

Five additional public scanner tests cover nested undecodable paths and every
candidate field, trailing slashes, hidden opt-in and exclusion/root override rules,
file/directory/broken symlinks, invalid/missing roots, permissions where meaningful,
and pre-cancellation/callback cancellation with no further publication. Host
provider search tests and all 12 provider CTests passed; 36 installed-provider
Files finder, exclusion, cache, warmup, refresh and shutdown regressions passed.
Host Files, Portal and Viewer were rebuilt against `build/file-browser/prefix`.
Core-only host checks passed 2/2. Provider container `task check` passed all
12 CTests plus formatting, clang-tidy, QML import/lint/type checks and REUSE.
Umbrella `task check:integration -- --siblings <umbrella-root>` passed with the
local traversal fix, including Files 20/20, Viewer 27/27 and Portal 2/2. The
integration snapshot preceded the behavior-preserving classification-helper
extraction for clang-tidy; final provider container acceptance and host regressions
cover that cleanup. Logs are under `build/file-browser/traversal-*.log`, including
`traversal-provider-acceptance.log`, `traversal-files-focused.log` and
`traversal-integration.log`.

The disposable comparison source, fixture, executable and logs remain under
`build/file-browser/walkthrough-2026-10-16/`. The corrected comparison uses the
same immediate pre-extraction baseline, `-O0 -g` for both implementations, one
warmup each and six measured baseline/corrected pairs in alternating runs. It
checks equivalent sets of all 20,100 display paths, relative paths and directory flags, and validates
native absolute/relative fields separately. Timing assertions remain outside CTest.
The final corrected median was **46.06 ms** (45.87–46.30 ms), versus
**55.67 ms** (54.65–56.26 ms) for the baseline: ratio **0.827**, meeting
the requirement to stay within 25% of baseline. Both scans returned 20,100
equivalent candidates. These are traversal-only warm-filesystem measurements,
not startup or cache-attachment latency. The final log is
`logs/scanner-benchmark-corrected-debug.log`; the companion build script records
the compiler/link invocation.

The user confirmed **“Works correctly”** after the requested native check with
the rebuilt host Files binary: background indexing before opening search, recursive
results, and reuse on reopening are accepted for that walkthrough. Cache state,
startup delay and selected root were not specified; this confirmation does not
measure startup/cache latency or replace the traversal benchmark above. Prior Files
passes remain accepted; ranking stays deferred to Shared Search. Toolkit closure
still requires the Portal and Viewer walkthroughs. Publication and pinning were
subsequently authorized by the user and are recorded below. System package and
desktop service changes remain outside this work.

### Traversal fix publication and pinning — 2026-10-16

The user authorized publication and pin updates after accepting the native finder
repair. The provider was published before consumer manifests were updated.

| Repository | Published revision | Change |
| --- | --- | --- |
| holonight-file-browser | `f90cea52f6f298b4fa70c611abcbed5031b78fbd` | Native traversal repair and scanner regressions |
| holonight-files | `c2a1bf464d7fec04d775cd04b9a57278fb00769f` | Provider manifest pin |
| holonight-viewer | `db5cd81f6163287e8c98fb112ec42e56eb818c98` | Provider manifest pin |
| xdg-desktop-portal-holonight | `69be1289b1873ca2ceb50e597542c3686fac6ab2` | Provider manifest pin |

The umbrella pins these four published revisions. Existing component acceptance,
installed-provider regressions, benchmark and full sibling integration evidence
above apply to the published source; consumer changes only update manifest pins.
Hosted publication acceptance is monitored separately. Native Files acceptance
remains recorded above; Portal and Viewer walkthroughs remain pending.
