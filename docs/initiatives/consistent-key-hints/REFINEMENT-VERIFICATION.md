# Compact key hints follow-up verification

Date: 2026-09-20. Initiative remains **Accepted**; this is local repository
acceptance and compatibility evidence, not KH-005 integration acceptance.

## Provider and Viewer

- KH-006: provider `9723cef7371a4ca5f2967d869b26ee7ff1e3c789` is published
  to canonical origin/main and pinned after user authorization. Its local
  acceptance is recorded in the [provider SDD](../../../holonight-qt/docs/sdd/consistent-key-hints/VERIFICATION.md#kh-006-refinement-acceptance--2026-09-20).
  Latest CI checked once at that revision: CI, `in_progress`, no conclusion,
  [run 35512774792](https://github.com/lebedenko/holonight-qt/actions/runs/35512774792).
- KH-007: Viewer `2ba1e5217002bf369fbbc4223866e37e176d4879` is a clean local
  commit on main. [Acceptance and captures](../../../holonight-viewer/docs/sdd/consistent-key-hints/VERIFICATION.md#kh-007-refinement--2026-09-20)
  cover clean Release build, Debug/test builds, all 20 CTest entries after an
  affected rerun, formatting, tidy, QML policy/types/lint, licenses, staged install
  and an isolated installed runtime. Native clipboard tests remain platform-skipped.
  Viewer publication and its umbrella pin remain a separate authorization handoff.

## KH-008 Shell compatibility

Exact Shell revision: `d109fb3b4883c9d1ae40f7ec7706c9e4407e95a8`, clean
and unchanged. Built the corrected provider into Shell's private Debug prefix
with Wayland enabled, then rebuilt Shell. Qt 6.11.2 / GNU C++ 16.2.1.
Installed HnKeyHint.qml and HnKeySequenceLabel.qml hashes match provider source.

```sh
# From holonight-shell:
task build:qt-dependency NPROC=4
cmake --build build -j4
QT_QPA_PLATFORM=offscreen QML_IMPORT_PATH="$PWD/build-dependencies/prefix/lib/qt6/qml" \
  ctest --test-dir build --output-on-failure \
  -R 'launcher_input_|uqc_authentication_|uqc_source_' -j4
ctest --test-dir build --output-on-failure -j4
python3 scripts/run-isolated-test.py --hide-host \
  ctest --test-dir build --rerun-failed --output-on-failure
cmake --build build --target holonight-shell_qmllint \
  holonight_authentication_qml_qmllint -j4
```

- Build passed without compiler warnings; expected Qt private-module notices remain.
- Focused launcher, authentication and source-QML suites: **14/14 passed**,
  including audio footer assertions, both styles and fractional scale coverage.
- Full CTest initially passed **1,168/1,175**. The seven failures were D-Bus
  registration checks because the first invocation omitted Shell's required
  private-bus/filesystem wrapper. All seven passed with that wrapper. Every CTest
  entry has a passing result; unaffected tests were not repeated. This is not a
  claim that the original unwrapped run passed in full.
- Shell/authentication qmllint targets passed with existing unqualified-access
  and unresolved service-type warnings in unchanged QML.
- The normal `task build:dependencies` wrapper deliberately enforces Shell's
  standalone provider revision `8fe24ff`; it rejected the corrected sibling
  checkout. Used the explicit provider/CMake steps above to test compatibility
  with the umbrella-selected revision. Shell's standalone CI/release dependency
  pins were not changed by this verification-only package.

## KH-008 Files compatibility

Exact Files revision: `550e662089fc8d39d8120f56c04c882a06031166`. The main
Files worktree contains unrelated active implementation work, so verification
used a clean detached worktree at `/tmp/holonight-files-kh008`. That checkout
remains available for review; no Files source files or commits were changed.

Reused Viewer's private Release provider/config prefix built from exact accepted
source revisions. Qt 6.11.2 / GNU C++ 16.2.1. Its installed key-hint QML hashes
match corrected provider source.

```sh
# From /tmp/holonight-files-kh008:
cmake --preset test \
  -DCMAKE_PREFIX_PATH=/home/andrii/Projects/pet/holonight/holonight-viewer/build/deps/prefix \
  -DQML_IMPORT_PATH=/home/andrii/Projects/pet/holonight/holonight-viewer/build/deps/prefix/lib/qt6/qml
cmake --build build/test -j4
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME= QT_QUICK_BACKEND=software \
  QML_IMPORT_PATH=/home/andrii/Projects/pet/holonight/holonight-viewer/build/deps/prefix/lib/qt6/qml \
  build/test/tests/files-smoke --gtest_filter='Files.QuickLook*:Files.ModeBadgeInsertMode:Files.*Insert*'
ctest --test-dir build/test --output-on-failure
cmake --build build/test --target qml-lint qmltypes-check -j4
```

Fresh Debug test build passed without compiler warnings. **16/16 focused tests**
and **9/9 CTest suites** passed, including Quick Look geometry, focus, wrapping,
insert guidance and Fusion editing. QML lint and metadata checks passed. Full
CTest ran with the local filesystem/socket capabilities required by its fixtures.
No source regression requiring a separate product fix was found.

## Remaining integration gate

Do not treat the local Viewer commit or active Files worktree as integrated
state. Publish and pin the completed Viewer change on authorization. KH-005
still requires clean participating worktrees at published pins, review of exact
cross-repository contracts, integration checks in dependency order, and the
user's native Launcher/audio/authentication/Viewer/Files checks. No native
pointer or window-focus interaction was automated. No umbrella integration
checks were claimed by these local compatibility runs.
