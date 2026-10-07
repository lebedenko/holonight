# Configuration architecture integration verification

Automated standalone verification: 2026-10-06. Manual result reported: 2026-10-07. Final integration completed on 2026-10-07.

## Published implementation acceptance

The [ledger](TASKS.md) records exact canonical published revisions, dependency handoffs, clean acceptance commands/results and one-time hosted CI observations for Config, Qt, Shell, adapters and Settings. Hosted observations are historical checks at publication; queued/in-progress observations are not passing evidence. Config's final rollback correction completed hosted CI successfully.

Config acceptance preceded Qt; validated Shell and adapter handoffs preceded Settings v2 GUI writes. The final Config change binds rollback to the captured physical target; it does not change reader/effective appearance contracts. Reader, Shell and adapter focused compatibility follow-ups against that provider passed. Settings clean acceptance consumed the final Config, Qt, Shell configuration package and system-services revisions. Shell application installation is unnecessary for the exported schema package.

## Standalone consumer verification

Both consumer SDK prefixes contain Config `d6a392b41991f70a004d58f7694c7b6115cb7280`, Qt `98803bca05e16ae0d0784a6cb43b0ace561385de`, system-services `398804a7cce5a57f9f6870c4e7ec99e9b1f3ddaa`, images `d834984dc413dc9e56f7f3157fa605d6a8667088` and thumbnails `2284b1822b0f8f856677e14d21d91e8fa10bd98c`; Files also consumes search `26067775e2eac3d9a779b3114dfbddc96834c7de`. Provider cache metadata confirms clean source hashes, revisions, GCC 16.2.1 and Qt 6.11.2. Compatible unchanged provider artifacts were reused. System-services was prepared before Qt. Neither prefix contains Shell or Settings packages.

Tests use a disposable HOME and XDG config/data/state/runtime beneath each repository's `build/configuration-integration/home`, with runtime mode 0700 and the explicit installed provider library/import paths. Private D-Bus/headless rendering checks run outside the socket-restricted sandbox. User configuration is untouched.

| Consumer | Commands | Result |
|---|---|---|
| Files, `4d95dd7737217a84e06aedd83755c041650c024b` | Prepare accepted standalone providers; `task build PRESET=test`; focused CTest (`files-smoke`, provider revisions, Fusion editing); `task check` | Focused 3/3 and full CTest 27/27 passed; all remaining full acceptance checks passed (source/test tidy, format, QML lint/type/import, licensing and staged install). |
| Viewer, `66b1ea4fdc1878b344440dd68674a4c1f646dbeb` (CA-006a) | Clean external CMake Debug build with `BUILD_TESTING=ON`, `/usr` install prefix and explicit SDK/import paths; `ctest --test-dir build/configuration-architecture-acceptance --output-on-failure`; QML lint/type checks; format, full tidy, REUSE, import and staged install checks | Clean CTest 27/27, QML lint/type checks passed; all final source/test analysis, format, REUSE, import and staged-install contracts passed. Corrected annotation-only fixture follow-up: 24/24 tests passed. |

### Viewer baseline fixture failures

The original four failures reproduced in isolation at Viewer `75752baac40257d6191d7be3fcba7477e3e1dea9` with accepted Qt and with the previous pinned Qt `c434d6821140d5269550cb2388820f9cbfb2e163`, rebuilt in a separate untracked baseline SDK. They were not configuration regressions. Three grid assertions compared a fractional viewport with pixel-rounded scrolling; one loading assertion relied on ambient `/tmp` containing an image so the controller could enter grid mode. CA-006a aligns the fixture viewport to integer pixels and creates a discoverable image in a private temporary directory, retaining the original containment/loading assertions and cancellation-controlled decoder. All four focused regressions passed after correction. No Viewer product behavior or application configuration changed.

### Installed runtimes

Each `scripts/prepare-runtime-check.sh` stages accepted installed providers and the application's Release payload under `/usr`. Container builds use existing local images verified to have GCC 16.2.1/Qt 6.11.2. Run `docker run --rm --network none holonight-configuration-files-runtime` and the corresponding Viewer image with no source/workspace mounts. Files runs as its ordinary test user. Neither image contains Shell, Settings or their configuration package.

- Files installed-runtime script passed permissions, RPATH, installed desktop association and GIO launch checks. Image: `sha256:3d0e30171b9171b03abc24f0d91590f5d848c66c72f23df7f35724a1d2f03ac8`.
- Viewer installed-runtime script passed format decoders, metadata/negative controls, CLI opening and GIO launches for seven formats. The cached base image lacked AppStream; only the disposable context was amended to install that validation tool. Qt remained 6.11.2. Image: `sha256:9948acf9f8f34e24e6e17b8cf31c7f71a2a49b8cebe4d6cec18b1621add4fb01`.
- Both installed applications started headlessly for three seconds with a private sparse appearance v2 document, light scheme, purple accent, retained comment and unknown future table. No error diagnostics; byte comparison confirmed the appearance document was unchanged.

Detailed command/output artifacts are retained under each consumer's `build/configuration-integration/`: provider preparation, focused builds/tests, baseline/fixed Viewer regressions, clean acceptance, static/installed contracts, runtime image builds, installed runtime and appearance-v2 runtime logs. These ignored artifacts are local evidence, not published product files.

## User-operated checks

[Manual guide](MANUAL_CHECKS.md). On 2026-10-07 the user reported all checks passed: concurrent editing, per-value resolution, reset, invalid-document recovery and appearance application checks. The only observed issue was repeated `HnSettingsRow`/`HnSeparator` implicit-height binding-loop warnings, tracked by CA-002b. Native adapter availability was not separately enumerated; this report does not claim every desktop-specific adapter was installed. No desktop pointer or focus automation was performed. These checks used Config `d6a392b41991f70a004d58f7694c7b6115cb7280`, Qt `98803bca05e16ae0d0784a6cb43b0ace561385de`, Shell `e490ff73f3da4b3a671aaf0496c8dbdc94a53ff8`, adapters `95a9078e8d4f0b2d9c5a69ee6040388558eb9251` and Settings `7bec8a8a20127bfa04c72edfdf380866959c3b48`. The subsequent separator-only correction requires automated warning-sensitive consumer verification; configuration behavior and effective appearance contracts remain unchanged.

## Final automated review

All participating repositories and unchanged standalone providers were clean and at canonical `origin/main` revisions after publication. Viewer's one-time hosted check for `66b1ea4fdc1878b344440dd68674a4c1f646dbeb` was in_progress, conclusion empty: [run 37445706427](https://github.com/lebedenko/holonight-viewer/actions/runs/37445706427). No hosted completion polling was performed.

Complete local logs were inspected: Files full acceptance 829 lines; Viewer clean acceptance 350 lines, static-analysis initial/resumed 147/90 lines, final licensing/import/install 38 lines and affected tests 60 lines. Final actionable diagnostics were zero; initial fixture annotation errors and sandbox socket restrictions were corrected and the affected checks passed. Documentation links and final diff were checked before checkpointing.

## Separator warning correction — 2026-10-07

Qt `8eadfa36396315da56d734a83b2145b6d71d51cc` fixes synchronous geometry re-entry while evaluating Settings row implicit height, and computes paint bounds after thickness-driven resizing. A warning-sensitive six-row layout fixture reproduces the user's exact warning on the previous revision. Six DPR rendering registrations pass after correction; synchronous thickness/visibility and physical coverage contracts remain intact. Config reader, schema and editing contracts are unchanged.

Focused source/test analysis and format passed. Clean Qt `task ci` passed build-test and licensing at `build/ci/20261007T163140Z-z1y22sdx/`, 98/98 registrations; complete 1043/27-line logs reviewed. Five expected CMake private-module ABI notices were checked against matching Qt/toolchain versions; no actionable or runtime binding-loop diagnostics remained. The clean lane consumes Config d6a392b.

Unchanged Settings was built in `build/separator-qt-acceptance` with `CMAKE_PREFIX_PATH` naming the isolated corrected Qt install and its accepted Config/System/Shell SDK. `tests/check_settings_startup.py` passed four production startup modes and two controls acceptance modes at DPR 1.25 and 1.5625 (12/12), verifying loaded plugin origins and rejecting unexpected diagnostics. Logs: `build/separator-provider-acceptance-build.log`, `build/separator-provider-startup.log`. No Settings source changes.

Published canonical Qt revision confirmed before pinning. One-time hosted [CI observation](https://github.com/lebedenko/holonight-qt/actions/runs/37653739282): exact revision in_progress, conclusion empty. No hosted polling performed.

## Final integration — 2026-10-07

After CA-002b publication/pinning, `task deps` refreshed Settings, Files and Viewer SDKs. Provider-state metadata confirms Qt `8eadfa36396315da56d734a83b2145b6d71d51cc` and clean source hashes in all three prefixes. A process-mapping inspection found no applications using those SDKs before refresh.

Accepted-provider follow-ups, with explicit SDK `LD_LIBRARY_PATH` and isolated headless/D-Bus environments:

- Settings: `ctest --test-dir build/test -R 'settings_startup|settings_controls' --output-on-failure`: 6/6 passed, 15.10 seconds; no unexpected diagnostics.
- Files: `ctest --test-dir build/test -R 'files-separator|files-provider-revisions' --output-on-failure`: 13/13 passed, 8.11 seconds.
- Viewer: `ctest --test-dir build/test -R 'viewer-menu-separators|viewer-runtime-probe' --output-on-failure`: 11/11 passed, 73.53 seconds.

For each standalone consumer, install the accepted Qt SDK build into a disposable DESTDIR payload with `cmake --install build/deps/holonight-qt --prefix /usr`. Derive a final runtime image from the already verified matching runtime by copying only that payload. Run `docker run --rm --network none holonight-configuration-files-final` and `holonight-configuration-viewer-final`: both complete installed-runtime scripts passed. No Shell/Settings, source mounts or network access were added. Final image IDs: Files `sha256:a8a74c9bebd55076a4dc87ac54d56b31cad9eb83aa857d91778af4fd9735e3b3`; Viewer `sha256:bb8f6b1bbce55e1bd093543b73682a310d20707b4b373d6e23a1836365c5a5dd`.

Final follow-up logs: each consumer's `build/separator-final-providers.log`, `build/separator-final-consumer-tests.log`, `build/separator-final-runtime-image.log` and `build/separator-final-installed-runtime.log`. Complete outputs were inspected; no actionable errors or runtime binding-loop warnings remained. Earlier full consumer acceptance remains applicable to unchanged code; the affected separator/runtime checks were repeated at the final provider revision.

Umbrella closure checks: `task license-check` passed for the umbrella and initialized submodules; `task test:installer` passed 37/37 in 181.525 seconds; `bash -n scripts/install.sh scripts/install-dependencies.sh scripts/uninstall.sh` passed. Logs: `build/configuration-final-licensing.log`, `build/configuration-final-installer.log`. Local documentation links and `git diff --check` passed. Final audit compared each participating/provider HEAD with the authoritative gitlink and canonical origin/main; all matched and all submodules were clean.

The user-reported manual pass is retained at its recorded revisions. The subsequent change is confined to separator geometry, with warning-sensitive rendering and actual Settings consumer checks passing; configuration editing, reload, conflict and adapter behavior are unchanged. All acceptance requirements are satisfied. CA-006 is Done and the initiative is Integrated.
