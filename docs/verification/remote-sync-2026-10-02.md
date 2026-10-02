# Remote synchronization — 2026-10-02

The user authorized pulling and merging remote changes, resolving conflicts, publishing unpublished work,
and pinning every submodule to its latest synchronized commit. Histories were merged without rebasing or
force-pushing. Existing feature commits remain intact.

## Merge decisions

- Qt: merged remote `main` into the lowercase-key-hints branch, then fast-forwarded local `main` to that
  merge for publication. The feature branch remains available.
- Viewer: retained the explicit configured provider environment in `task run` while adopting the remote
  Taskfile structure. `task --dry run` confirms the provider QML/library paths.
- Files: merged the search-index lifecycle implementation with remote tooling changes without conflicts.
- Umbrella: retained the current shared-search/configuration initiative entries and added the remote
  developer-tooling entry. Remote published gitlinks were retained in the merge checkpoint; the final pin
  update follows successful repository publication.
- All other submodules fast-forwarded to fetched `origin/main`; working trees were clean before merging.

## Local verification

Toolchain: GCC 16.2.1 and Qt 6.11.2. Provider revision ledgers in Files and Viewer match the synchronized
checkouts. Provider artifacts were rebuilt where their revision signature changed.

Clean acceptance for Qt, Files and Viewer used `cmake --preset test -B build/sync-acceptance-20261002`,
`cmake --build build/sync-acceptance-20261002 -j 4`, then
`ctest --test-dir build/sync-acceptance-20261002 --output-on-failure` (Qt uses `QT_QPA_PLATFORM=offscreen`).
Complete build logs were reviewed. Files and Viewer had no compiler warnings. Qt reports existing private-Qt
ABI notices, QTP0004 and an unused QML_IMPORT_PATH variable; no compiler warnings were introduced.

| Check | Result |
|---|---|
| Qt clean build and CTest | Passed, 95/95 |
| Qt key-hint/key-sequence focused tests | Passed, 7/7 |
| Qt test-tool discovery unit tests | Passed, 8/8 |
| Qt provider/example QML import policies | Passed |
| Qt `all_qmllint` | Passed with existing warnings outside the changed controls |
| Qt added regression clang-tidy | Passed with compiler-incompatible flag removed; line filter covers added test only |
| Qt broad smoke-file clang-tidy | Failed on existing diagnostics; initial invocation also included a GCC-only flag |
| Files clean build and CTest | Passed, 21/21 outside sandbox |
| Files `task check` | Debug/Release builds, 27/27 tests and formatting passed; stopped at existing clang-tidy errors |
| Viewer clean build and CTest | Passed, 25/25 outside sandbox |
| Viewer `task check` | Debug/Release builds, 25/25 tests and formatting passed; stopped on 7 existing header diagnostics while checking animation_controller.cpp |
| Files and Viewer formatting | Passed with `QMLFORMAT=/usr/lib/qt6/bin/qmlformat` |
| Files and Viewer QML lint, metadata and import policies | Passed |
| Qt, Files and Viewer REUSE | Passed outside sandbox |
| Files and Viewer staged installation | Passed |
| Umbrella tooling unit tests | Passed, 11/11 |
| Umbrella installer unit tests | Passed, 35/35 |
| Changed Git diffs | `git diff --check` passed |
| Tooling drift check | Reports Viewer’s retained intentional trailing-comma clang-tidy exception |

Sandbox-denied socket/D-Bus tests were rerun outside the sandbox. Explicit configured Qt tool overrides were
used for the acceptance workflows. Files retains its recorded isolated-container/native acceptance evidence
in `holonight-files/docs/sdd/search-index-lifecycle/VERIFICATION.md`; this sync does not change the container
or installation contracts, and those manual checks were not repeated. Local logs are `/tmp/holonight-sync-*.log`.

This is a Git synchronization and pin update. It does not mark any initiative Integrated or claim full ecosystem
runtime acceptance. Existing lint limitations remain reported rather than suppressed or changed during the sync.

## Publication and CI

CI is checked once after repository publication. The snapshot records the latest available run even when its
revision differs from the new pin; an older run is not acceptance evidence for the pinned revision. No CI polling
or waiting is performed. The gitlinks are the authoritative revision manifest.


Snapshot time (UTC): `2026-10-02T17:39:35.690266+00:00`. All 17 checkout commits equal their canonical remote `main` heads.

| Repository | Latest run revision | Status | Conclusion | Run |
|---|---|---|---|---|
| holonight-qt | `79ab555a886af469c9d5fd91b455c1e391008e0c` | completed | success | [Licensing](https://github.com/lebedenko/holonight-qt/actions/runs/37041836294) |
| holonight-shell | `73bb62749c72fe442871033a5d4092d346f40cf3` | completed | failure | [CI](https://github.com/lebedenko/holonight-shell/actions/runs/37033854181) |
| holonight-icons | `402ed3a3cf858a3095941a75a7fceb2351fe6f9e` | completed | failure | [Theme verification](https://github.com/lebedenko/holonight-icons/actions/runs/37033848557) |
| holonight-ai | `f29550841ba1a6bff4bb1ba06c0402b0165096f2` | completed | failure | [CI](https://github.com/lebedenko/holonight-ai/actions/runs/37033848172) |
| holonight-pkg-manager | `d62451e4b75589b87b323dad16bfdb8ac63903ee` | completed | success | [Licensing](https://github.com/lebedenko/holonight-pkg-manager/actions/runs/37033851373) |
| holonight-settings | `9500f21885af4d794a095a2ee7519df2898005c8` | completed | success | [Licensing](https://github.com/lebedenko/holonight-settings/actions/runs/37033853642) |
| holonightd | `281e824bbe107dfe1a1825bd34bf1d78a98f09b8` | completed | success | [Licensing](https://github.com/lebedenko/holonightd/actions/runs/37033856448) |
| holonight-appearance-adapters | `4a226b1c3af836dc8a9bd452aace94417384b41e` | completed | success | [Licensing](https://github.com/lebedenko/holonight-appearance-adapters/actions/runs/37033847979) |
| holonight-config | `b185c8404368cee6b2729ee17ffbcc671ba41cf3` | completed | success | [Licensing](https://github.com/lebedenko/holonight-config/actions/runs/37033848292) |
| holonight-greeter | `f0ecd224ad991c0ec13ff472fd015174eac150ee` | completed | failure | [CI](https://github.com/lebedenko/holonight-greeter/actions/runs/37033849777) |
| holonight-system-services | `6938984c7fd4ffd165668beca19ea403abf954c4` | completed | success | [Licensing](https://github.com/lebedenko/holonight-system-services/actions/runs/37033855038) |
| holonight-hyprlock | `2af2a7b843f2608639861446e88b2831cd4bae1d` | completed | success | [Licensing](https://github.com/lebedenko/holonight-hyprlock/actions/runs/37033847645) |
| holonight-viewer | `2f388a4a5f46c318644f4225ab4f5cff054c3cda` | completed | success | [Licensing](https://github.com/lebedenko/holonight-viewer/actions/runs/37042109274) |
| holonight-files | `dea9ba0c5cdbe4ffdcd7950ca75b5e84c6b744ab` | completed | failure | [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/37041636611) |
| holonight-images | `c76142cbb69b69c962164f8ed82948d8daa9a367` | completed | success | [Build and checks](https://github.com/lebedenko/holonight-images/actions/runs/37033851715) |
| holonight-thumbnails | — | Missing | No available runs | — |
| holonight-search | — | Missing | No available runs | — |

Failed runs are reported for Shell, Icons, AI, Greeter and Files. These results do not block the user-authorized
pin update and are not claimed to pass. Thumbnails and Search have no available runs. Qt and Viewer
latest Licensing runs succeeded at their published merge revisions; this one-run-per-repository snapshot
does not establish that every hosted workflow passed. No implementation correction was made after publication.

After publishing the umbrella pin commit `b3b4e992c4e852186a2088bb76b693b6b0071abd`, its latest
[Licensing run](https://github.com/lebedenko/holonight/actions/runs/37042305614) was `in_progress` with no
conclusion. This observation predates the documentation-only wording correction; it is not CI evidence for
that later documentation commit. No further CI query was made.
