# Size-aware icons and shared Qt recoloring — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SAI-001 | `holonight-icons` | Document size-aware artwork and lookup contract | — | [SDD](../../../holonight-icons/docs/sdd/size-aware-icons/README.md) | Done | `39760d6` | `task verify` (40 tests); GTK 3 recoloring and GTK 4 recognition, 2026-09-25; merged upstream and `task verify` passed (41 tests), 2026-09-26 |
| SAI-002 | `holonight-qt` | Size-aware engine and explicit QML API | — | [SDD](../../../holonight-qt/docs/sdd/size-aware-icons/README.md) | Done | `0d5bdf0` | Qt build; 96 non-accelerated CTests, platform bootstrap, 17 focused tests; 6 accelerated checks after one retry, 2026-09-25 |
| SAI-003 | `holonight-shell` | Migrate icon callers | SAI-002 | [SDD](../../../holonight-shell/docs/sdd/size-aware-icons/README.md) | Done | `fbfe8f7` | QML lint/types; `task test` (1170), 2026-09-25; rebuilt against published providers and QML harness passed (5), 2026-09-26 |
| SAI-004 | `holonight-files` | Preserve icon choices under explicit rendering | SAI-002 | [SDD](../../../holonight-files/docs/sdd/size-aware-icons/README.md) | Done | `b73e2eb` | Focused icons (15); lint, format, import, types, install, license, tidy, 2026-09-25; CTest passed (27) against published providers, 2026-09-26 |
| SAI-005 | `holonight-ai` | Migrate provider asset rendering | SAI-002 | [SDD](../../../holonight-ai/docs/sdd/size-aware-icons/README.md) | Done | `9f28e6c` | QML lint, 2026-09-25; `task test` passed (714) against published providers, 2026-09-26 |
| SAI-006 | `holonight-settings` | Migrate navigation asset | SAI-002 | [SDD](../../../holonight-settings/docs/sdd/size-aware-icons/README.md) | Done | `d5cd9f1` | QML types and QML lint exit 0 with two false missing-property warnings, 2026-09-25; `task test` passed (53) against published providers, 2026-09-26 |
| SAI-007 | `holonight-pkg-manager` | Migrate package assets | SAI-002 | [SDD](../../../holonight-pkg-manager/docs/sdd/size-aware-icons/README.md) | Done | `cee638e` | QML lint, 2026-09-25; `task test` passed (259) against published providers, 2026-09-26 |
| SAI-008 | `holonight-viewer` | Migrate empty-state asset | SAI-002 | [SDD](../../../holonight-viewer/docs/sdd/size-aware-icons/README.md) | Done | `d1de0e9` | Merged upstream; `task check` passed and CTest passed (24) against published providers, 2026-09-26 |
| SAI-009 | umbrella | Verify published pins and manual ecosystem checks | SAI-001–SAI-008 | — | In Progress | — | All 15 module heads published and verified on canonical remotes; `task icons:verify`, `task test:installer` (27 tests), and root REUSE lint passed, 2026-09-26. Full ecosystem and Dolphin checks remain pending. |

Allowed states: `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`. A repository task is `Done` only after local verification. Record integration commands, results, and date in SAI-009 before setting the initiative to `Integrated`.

All 15 changed module worktrees were clean, and their local heads matched their canonical remote `main` heads before pinning on 2026-09-26. Seven additional modules carry the repository-wide Conventional Commit guidance; Greeter also updated its exact provider revision checks. The 1.5 DPR OpenGL separator test in SAI-002 failed once during the six-test run and passed when rerun alone; it is outside the changed icon paths. The Settings qmllint warnings concern `HnIcon.rendering` and `HnIcon.Semantic`, both present in the installed provider QML.

## Published CI snapshot — 2026-09-26

This is the latest available `main` run per repository at the single check after publication. A successful Licensing run verifies licensing only; it does not stand in for an application build. Pending runs were not polled for completion.

| Repository | Run revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|---|
| `holonight-ai` | `9f28e6c` | Licensing | completed | success | [36192160242](https://github.com/lebedenko/holonight-ai/actions/runs/36192160242) |
| `holonight-appearance-adapters` | `276c240` | Licensing | completed | success | [36190620828](https://github.com/lebedenko/holonight-appearance-adapters/actions/runs/36190620828) |
| `holonight-config` | `03fa635` | Licensing | completed | success | [36190618702](https://github.com/lebedenko/holonight-config/actions/runs/36190618702) |
| `holonight-files` | `b73e2eb` | Build and checks | in_progress | — | [36192284294](https://github.com/lebedenko/holonight-files/actions/runs/36192284294) |
| `holonight-greeter` | `dc07ab9` | CI | in_progress | — | [36192222489](https://github.com/lebedenko/holonight-greeter/actions/runs/36192222489) |
| `holonight-hyprlock` | `69b957d` | Licensing | completed | success | [36190617457](https://github.com/lebedenko/holonight-hyprlock/actions/runs/36190617457) |
| `holonight-icons` | `39760d6` | Theme verification | completed | success | [36190535855](https://github.com/lebedenko/holonight-icons/actions/runs/36190535855) |
| `holonight-images` | `ac11f23` | Build and checks | completed | success | [36190627692](https://github.com/lebedenko/holonight-images/actions/runs/36190627692) |
| `holonight-pkg-manager` | `cee638e` | CI | in_progress | — | [36192154077](https://github.com/lebedenko/holonight-pkg-manager/actions/runs/36192154077) |
| `holonight-qt` | `0d5bdf0` | Licensing | completed | success | [36190535232](https://github.com/lebedenko/holonight-qt/actions/runs/36190535232) |
| `holonight-settings` | `d5cd9f1` | Licensing | completed | success | [36192283914](https://github.com/lebedenko/holonight-settings/actions/runs/36192283914) |
| `holonight-shell` | `fbfe8f7` | CI | in_progress | — | [36192128928](https://github.com/lebedenko/holonight-shell/actions/runs/36192128928) |
| `holonight-system-services` | `8787a48` | Licensing | completed | success | [36190629203](https://github.com/lebedenko/holonight-system-services/actions/runs/36190629203) |
| `holonight-viewer` | `d1de0e9` | Build and checks | in_progress | — | [36192507822](https://github.com/lebedenko/holonight-viewer/actions/runs/36192507822) |
| `holonightd` | `6abf980` | Licensing | completed | success | [36190625479](https://github.com/lebedenko/holonightd/actions/runs/36190625479) |
