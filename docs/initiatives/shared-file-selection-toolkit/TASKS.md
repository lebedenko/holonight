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
