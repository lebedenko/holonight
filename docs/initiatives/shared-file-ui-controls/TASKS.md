# Shared File UI Controls — Coordination Ledger

Status: Implementation and installed-package ecosystem acceptance complete.
User-operated native functional acceptance passed; visual fine-tuning is deferred.
Each repository owns its local SDD and focused verification.
No publication, system deployment or umbrella pin changes are authorized or claimed.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| UI-001 | `holonight-qt` | Five `Holonight.Controls` types from the contract, existing selection foundations/tokens, controls-gallery examples, usage documentation and installed public-type coverage | — | [Design](../../../holonight-qt/docs/sdd/shared-file-ui-controls/README.md) | Locally verified | fac3411 (feature e4c528e) | See evidence below |
| UI-002 | `holonight-file-browser` | Shared detailed-list header/rows with gutter/editing extension points, path-to-breadcrumb adapter and reusable file-preview composition as needed; preserve installed and Core-only boundaries | UI-001 | [Design](../../../holonight-file-browser/docs/sdd/shared-file-ui-controls/README.md) | Locally verified | c816696 | See evidence below |
| UI-003 | `holonight-files` | Adopt breadcrumbs, detailed list, preview framing, metadata and labeled hints; preserve Vim modes, line numbers, editing, history, preview transitions and Quick Look | UI-001, UI-002 | [Design](../../../holonight-files/docs/sdd/shared-file-ui-controls/README.md) | Locally verified | 585cc51 | See evidence below |
| UI-004 | `holonight-viewer` | Adopt thumbnails, image-information preview frame, compatible metadata and labeled hints; preserve no-upscaling, caches, rendering, playback and footer hint priorities | UI-001 | [Design](../../../holonight-viewer/docs/sdd/shared-file-ui-controls/README.md) | Locally verified | ed83955 | See evidence below |
| UI-005 | `xdg-desktop-portal-holonight` | Editable breadcrumb location, detailed columns and newly included selected-entry preview/metadata; existing search/header/action-bar/sidebar/feedback adoption; preserve selection, native paths, filters, choices, cancellation and save validation | UI-001, UI-002 | [Design](../../../xdg-desktop-portal-holonight/docs/sdd/shared-file-ui-controls/README.md) | Locally verified | 84669a3 | See evidence below |
| UI-006 | `holonight-settings` | Wallpaper thumbnail/preview adoption plus existing navigation/settings-row/form/action/empty/loading controls; preserve favorites, folders, pending selection, display assignment and configuration conflicts | UI-001 | [Design](../../../holonight-settings/docs/sdd/shared-file-ui-controls/README.md) | Locally verified | 826af8f | See evidence below |
| UI-007 | Umbrella | Verify compatible installed providers and consumers, application regressions, ecosystem interaction and installer protections; coordinate separately authorized publication and pin updates | UI-001, UI-002, UI-003, UI-004, UI-005, UI-006 | This initiative | Verified with recorded native host exception | This ledger | See evidence below |

## Work package acceptance

- [x] UI-001: Local SDD delivered; five public controls documented and verified through gallery and installed C++/QML consumer coverage.
- [x] UI-002: Local SDD delivered; shared presentation and adapters verified, including installed consumers and Core-only/optional-component builds.
- [x] UI-003: Local SDD delivered; Files adoption and preserved application behavior verified.
- [x] UI-004: Local SDD delivered; Viewer adoption and preserved application behavior verified.
- [x] UI-005: Local SDD delivered; Portal adoption, preview failures/stale results and preserved protocol/selection/validation behavior verified.
- [x] UI-006: Local SDD delivered; Settings adoption and preserved wallpaper/configuration behavior verified.
- [x] UI-007: Authorized implementation and ecosystem acceptance complete; integration evidence and the unrelated native host exception recorded. Publication and pins remain separately authorized.

Dependencies describe interface and acceptance order. Local development may overlap
through staged installed packages under [CONTRIBUTING.md](../../../CONTRIBUTING.md).
Viewer and Settings require UI-002 only if their local designs choose File Browser
composition; record that added dependency before adopting it.

Repository completion requires a local commit and passed local verification;
it does not imply publication or ecosystem integration. Record commands, results,
dates and compatible revisions when work is performed. Native acceptance requires
host-built binaries and user-operated interaction. Publication and pin updates
require separate authorization, with providers published before dependent consumers.
No publication, deployment or umbrella pin update is claimed by this ledger.

## Executed automated evidence — 2026-10-17

Host builds consume installed provider packages. The development prefix is
`/tmp/holonight-shared-ui-prefix`; Qt uses `holonight-qt/build/dev`, other participants
use their own `build/shared-ui` directories. Configure consumers with
`-DCMAKE_PREFIX_PATH=/tmp/holonight-shared-ui-prefix`, never provider source includes.

| Check | Executed result |
|---|---|
| Qt `ctest --test-dir build/dev --output-on-failure -j 3` | 98/98 passed, including installed package, demo/gallery startup, Fusion and fractional-scale checks |
| File Browser `ctest --test-dir build/shared-ui --output-on-failure` | 12/12 passed; extended detailed-column/editor consumers and native-byte ancestor regression included |
| File Browser all optional components disabled, `build/shared-ui-core` | Core build and both CTest checks passed, including installed C++ consumer |
| Files `ctest --test-dir build/shared-ui --output-on-failure -j 2` | 20/20 passed, including 746 smoke tests and fractional-scale separator matrix; fixture-dependent/manual tests retain explicit skips |
| Viewer `ctest --test-dir build/shared-ui --output-on-failure -j 2` | 27/27 passed, including Fusion, thumbnails, information, footer, playback and installed-runtime checks |
| Settings private-bus `ctest --test-dir build/shared-ui --output-on-failure` | 86/86 passed, including wallpaper/favorites/conflicts and both opening orders |
| Portal `ctest --test-dir build/shared-ui --output-on-failure` | Both protocol/presentation and staged activation tests passed; focused preview/cursor, retirement and compact-layout coverage added |
| Files and Viewer format/import/QML metadata/QML lint targets | Passed with `QMLFORMAT=/usr/lib/qt6/bin/qmlformat` for the custom build directory |
| Settings format/QML lint targets | Passed |
| Umbrella `python3 -m unittest discover -s tests -p 'test_install*.py'` | 86 tests passed, one skipped; staging/ownership/collision/uninstall checks retained |
| Umbrella `JOBS=4 task check -- --siblings /path/to/holonight` | 121 tests passed, two expected skips, REUSE passed |

Private-bus runtime and Unix-socket fixtures need permission outside the filesystem
sandbox. Initial sandbox-denied runs are not passing evidence; the table records
successful permitted reruns. Settings uses a private bus with host activation disabled;
running its mocks against the host bus is not acceptance.

Container acceptance uses `JOBS=4 task check -- --siblings /path/to/holonight`.
The first File Browser container run caught a missing loop brace; it was corrected.
All six participating repositories passed container acceptance against current sibling
providers, including formatting, lint, installed consumers and REUSE. File Browser’s
first runs caught fixture formatting/cast/pointer-style issues; the corrected final
run passed. Portal’s CI manifest now stages Images/Thumbnails and enables Preview
and PreviewQuick, preserving optional Storage/Markdown exclusion.
The measured breadcrumb-width follow-up passed focused tests, the full QML smoke
suite, source policy, gallery startup variants and Controls QML lint.
Native ecosystem acceptance runs
`JOBS=4 python3 scripts/build-ecosystem.py --tests --prefix /tmp/holonight-shared-ui-ecosystem`.
Generated evidence stays in ignored build directories or temporary test logs.

## Native interaction acceptance

Native acceptance used the host-built executables from each participant's `build/shared-ui` with
`QML_IMPORT_PATH=/tmp/holonight-shared-ui-prefix/lib/qt6/qml`. Container binaries are
acceptance only. The requested acceptance checklist covered:

- Files: breadcrumbs and guarded navigation, Vim/edit/search/gutter flows, history,
  preview failures/transitions, pinned Quick Look and focus return.
- Viewer: thumbnail keyboard activation/no-upscaling, selectable information path,
  playback, footer priorities and Help.
- Portal: selection/save/filter/choice modes, compact preview toggle, rapid navigation,
  failed previews, cancellation, concurrent requests and native parenting.
- Settings: keyboard selection, favorites/folders, pending/apply state, display targeting,
  unavailable images and external configuration conflicts.
- All: narrow windows, live theme changes, explicit Fusion and fractional scaling.

The user reported that functional behavior works well and explicitly requested that
visual refinements be handled separately in the corresponding repositories. Native
functional acceptance is recorded as passed; visual fine-tuning is deferred by that
request. Publication, system deployment and pin updates remain separately authorized.

The first native ecosystem run passed 1,159 Shell checks but exposed that Shell’s
host isolation also hid the explicit `/tmp` provider prefix. Shell commit `0872b97`
retains existing `CMAKE_PREFIX_PATH` directories read-only. The umbrella regression
reproduced missing provider files before that fix and passed afterward, checking
both readable installed artifacts and rejected writes. Host activation remains
excluded. Shell’s full 1,161-check rerun passed with the correction. The full clean umbrella container integration passed against installed packages;
final native reruns and the host-only exception are recorded below.

The existing checkout modes are retained: Qt, Settings and Shell use detached
checkouts; File Browser, Files, Viewer and Portal remain on `main`. Implementation
working trees are clean after the local commits. Umbrella gitlinks are deliberately
not staged; updating the pinned revisions requires separate authorization.

## Final ecosystem acceptance — 2026-10-17

`JOBS=4 task check:integration -- --siblings /home/andrii/Projects/pet/holonight`
completed successfully using the pinned acceptance image. Every ecosystem suite
passed: Config 2, System Services 6, Qt 91, Appearance Adapters 8, Images 3,
Thumbnails 2, Search 6, File Browser 12, Shell 1,161, Settings 86, Viewer 27,
Files 20, Portal 2, AI 714, Package Manager 481, Greeter 8, holonightd 111 and
Hyprlock 2. The additional icons build/test step passed. Existing explicit fixture
and host-service skips remain skips. Installer/unit checks and REUSE passed before
the ecosystem build. Container binaries were not deployed.

The interrupted native run lost its temporary prefix. Verification resumed with
`JOBS=4 python3 scripts/build-ecosystem.py --tests --prefix
/home/andrii/Projects/pet/holonight/build/shared-file-ui-controls/native-prefix`,
then the same script's remaining repository sequence. Existing cached runtime paths
required restoring `/tmp/holonight-shared-ui-ecosystem` as a link to that prefix and
reconfiguring Shell, AI and Package Manager against its canonical installed Qt path.
Shell's two affected tests, AI's full 714-test suite and Package Manager's two
runtime style checks passed after rebuilding the affected targets. These were build
cache corrections, with no further source changes. All participating repositories,
Greeter, holonightd and Hyprlock passed native tests.

One unrelated native host exception remains: Package Manager's `layering_policy`
rejects the ignored local `CLAUDE.md` because it lacks the required fixture-only
repository-sync rule. That user-owned file was left untouched. The other 480 native
checks passed (including corrected runtime reruns); the clean container snapshot
excludes the ignored file and passed all 481 checks. The native monolithic command
therefore does not have an all-green result, although clean ecosystem acceptance does.

Logs and the full compatible revision map are preserved in the ignored
`build/shared-file-ui-controls/` directory, including
`shared-ui-umbrella-integration.log`, native sequence/rerun logs and `revisions.json`.
The compatible participant revisions are the local commits in the table above;
Shell's supporting isolation correction is `0872b97`.
