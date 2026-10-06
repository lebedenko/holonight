# Configuration architecture integration verification

Date: 2026-10-06. Initiative remains Accepted until user-operated checks pass.

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

[Manual guide](MANUAL_CHECKS.md). Results pending; user confirmed they are running the checks. The coordinator requested concurrent-edit, per-value keep/accept, reset, invalid-document recovery and appearance/native-output observations. No desktop pointer or focus automation was performed. Manual results, date and exact implementation revisions must be recorded before CA-006 becomes Done or this initiative becomes Integrated.

## Final automated review

All participating repositories and unchanged standalone providers were clean and at canonical `origin/main` revisions after publication. Viewer's one-time hosted check for `66b1ea4fdc1878b344440dd68674a4c1f646dbeb` was in_progress, conclusion empty: [run 37445706427](https://github.com/lebedenko/holonight-viewer/actions/runs/37445706427). No hosted completion polling was performed.

Complete local logs were inspected: Files full acceptance 829 lines; Viewer clean acceptance 350 lines, static-analysis initial/resumed 147/90 lines, final licensing/import/install 38 lines and affected tests 60 lines. Final actionable diagnostics were zero; initial fixture annotation errors and sandbox socket restrictions were corrected and the affected checks passed. Documentation links and final diff were checked before checkpointing.
