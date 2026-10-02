# Local CI Rehearsal — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| CI-001 | `holonightd` | Rehearse all push validation via task ci | — | [SDD](../../../holonightd/docs/sdd/local-ci/README.md) | Done | `5e7425d`, `78ee744` (local) | 2026-10-02: all container lanes pass; host format-check/tidy-src/test pass after user-requested corrections (111 tests). Fault injection and 245-file isolation pass. No publication or pin update |
| CI-002 | `holonight-config` | Rehearse all push validation via task ci | CI-001 | [SDD](../../../holonight-config/docs/sdd/local-ci/README.md) | Done | `11f7e99`, `ee96ef8` (local) | 2026-10-02: all three container lanes and host format/tidy/test pass; 143-file isolation and assertion regressions pass. No publication/pin update |
| CI-003 | `holonight-qt` | Rehearse all push validation via task ci | CI-002 | [SDD](../../../holonight-qt/docs/sdd/local-ci/README.md) | Done | `a2b2c2d`, `9fdbb3c` (local) | 2026-10-02: clean container build/test/static and licensing lanes pass (97 CTest cases); host build/format/tidy-src and focused tests pass. Launcher regressions and 1,644-file isolation pass. Qt5, Qt6.11.1 and Config fe69a59 preserved; no publication/pin update |
| CI-004 | `holonight-images` | Rehearse all push validation via task ci | CI-003 | Pending | Ready | — | Baseline c76142cbb69b69c962164f8ed82948d8daa9a367; preserve Release provider, installed-package and plugin-isolation CTest checks; freeze Qt/tool/image-codec environment |
| CI-005 | `holonight-thumbnails` | Rehearse all push validation via task ci | CI-004 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-006 | `holonight-search` | Rehearse all push validation via task ci | CI-005 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-007 | `holonight-system-services` | Rehearse all push validation via task ci | CI-006 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-008 | `holonight-icons` | Rehearse all push validation via task ci | CI-007 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-009 | `holonight-hyprlock` | Rehearse all push validation via task ci | CI-008 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-010 | `holonight-appearance-adapters` | Rehearse all push validation via task ci | CI-009 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-011 | `holonight-ai` | Rehearse all push validation via task ci | CI-010 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-012 | `holonight-pkg-manager` | Rehearse all push validation via task ci | CI-011 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-013 | `holonight-greeter` | Rehearse all push validation via task ci | CI-012 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-014 | `holonight-shell` | Rehearse all push validation via task ci | CI-013 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-015 | `holonight-settings` | Rehearse all push validation via task ci | CI-014 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-016 | `holonight-viewer` | Rehearse all push validation via task ci | CI-015 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-017 | `holonight-files` | Rehearse all push validation via task ci | CI-016 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-018 | umbrella | Verify published and pinned integration | CI-001–CI-017 | — | Planned | — | Publication and pin changes excluded from this session |

States: Planned, Ready, In Progress, Done, Blocked, Superseded.
Done requires a local commit and completed local verification; it does not mean Integrated.
Record exact acceptance commands, results and verification date before final integration.
