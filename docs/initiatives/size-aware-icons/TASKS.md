# Size-aware icons and shared Qt recoloring — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SAI-001 | `holonight-icons` | Document size-aware artwork and lookup contract | — | [SDD](../../../holonight-icons/docs/sdd/size-aware-icons/README.md) | Done | `64c53e3` | `task verify` (40 tests); GTK 3 recoloring and GTK 4 recognition, 2026-09-25 |
| SAI-002 | `holonight-qt` | Size-aware engine and explicit QML API | — | [SDD](../../../holonight-qt/docs/sdd/size-aware-icons/README.md) | Done | `0d5bdf0` | Qt build; 96 non-accelerated CTests, platform bootstrap, 17 focused tests; 6 accelerated checks after one retry, 2026-09-25 |
| SAI-003 | `holonight-shell` | Migrate icon callers | SAI-002 | [SDD](../../../holonight-shell/docs/sdd/size-aware-icons/README.md) | Done | `2fa1858` | QML lint/types; `task test` (1170); QML harness (5), 2026-09-25 |
| SAI-004 | `holonight-files` | Preserve icon choices under explicit rendering | SAI-002 | [SDD](../../../holonight-files/docs/sdd/size-aware-icons/README.md) | Done | `b73e2eb` | Focused icons (15); CTest (27); lint, format, import, types, install, license, tidy, 2026-09-25 |
| SAI-005 | `holonight-ai` | Migrate provider asset rendering | SAI-002 | [SDD](../../../holonight-ai/docs/sdd/size-aware-icons/README.md) | Done | `fcb6e6c` | QML lint; `task test` (714), 2026-09-25 |
| SAI-006 | `holonight-settings` | Migrate navigation asset | SAI-002 | [SDD](../../../holonight-settings/docs/sdd/size-aware-icons/README.md) | Done | `d5cd9f1` | `task test` (53); QML types; QML lint exits 0 with two false missing-property warnings, 2026-09-25 |
| SAI-007 | `holonight-pkg-manager` | Migrate package assets | SAI-002 | [SDD](../../../holonight-pkg-manager/docs/sdd/size-aware-icons/README.md) | Done | `a2ff95d` | QML lint; `task test` (259), 2026-09-25 |
| SAI-008 | `holonight-viewer` | Migrate empty-state asset | SAI-002 | [SDD](../../../holonight-viewer/docs/sdd/size-aware-icons/README.md) | Done | `1e54c00` | CTest (24); lint, types, format, import, license, install, 2026-09-25 |
| SAI-009 | umbrella | Verify published pins and manual ecosystem checks | SAI-001–SAI-008 | — | Planned | — | Awaiting publication/pins, umbrella checks, and Dolphin check after artwork replacement |

Allowed states: `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`. A repository task is `Done` only after local verification. Record integration commands, results, and date in SAI-009 before setting the initiative to `Integrated`.

All repository commits above are local and unpublished as of 2026-09-25. Their worktrees are clean, but the umbrella still pins the original revisions. The 1.5 DPR OpenGL separator test in SAI-002 failed once during the six-test run and passed when rerun alone; it is outside the changed icon paths. The Settings qmllint warnings concern `HnIcon.rendering` and `HnIcon.Semantic`, both present in the installed provider QML. No hosted CI run is claimed for these commits.
