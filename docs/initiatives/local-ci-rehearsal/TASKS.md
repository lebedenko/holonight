# Local CI Rehearsal — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| CI-001 | `holonightd` | Rehearse all push validation via task ci | — | [SDD](../../../holonightd/docs/sdd/local-ci/README.md) | Done | `5e7425d`, `78ee744` (local) | 2026-10-02: all container lanes pass; host format-check/tidy-src/test pass after user-requested corrections (111 tests). Fault injection and 245-file isolation pass. No publication or pin update |
| CI-002 | `holonight-config` | Rehearse all push validation via task ci | CI-001 | Pending | Ready | — | Baseline b185c8404368cee6b2729ee17ffbcc671ba41cf3; instructions and workflows reviewed; no providers |
| CI-003 | `holonight-qt` | Rehearse all push validation via task ci | CI-002 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
| CI-004 | `holonight-images` | Rehearse all push validation via task ci | CI-003 | Pending | Planned | — | Awaiting predecessor acceptance and repository review |
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
