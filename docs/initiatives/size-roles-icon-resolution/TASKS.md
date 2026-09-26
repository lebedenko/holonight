# Size roles and icon resolution — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SRI-001 | `holonight-qt` | Xs, header size role, icon resolution | — | [SDD](../../../holonight-qt/docs/sdd/size-roles-icon-resolution/README.md) | Done | `61d0c16` (local) | Focused metrics, QML, icon and bootstrap tests passed; 97 non-OpenGL CTests passed in sandbox, six OpenGL checks passed outside it; lint, formatting and REUSE passed; installed theme probe rendered HoloNight `#131e2c`, 2026-09-26 |
| SRI-002 | `holonight-files` | 42 px header and Xs navigation | SRI-001 | [SDD](../../../holonight-files/docs/sdd/size-roles-icon-resolution/README.md) | In Progress | `b058f67` (local) | Focused 14 history tests, icon tests and provider-revision check passed against installed `61d0c16`; six OpenGL checks and quality/staged-install gates passed. Full non-OpenGL suite: 20/21 CTest entries passed; `files-smoke` has two unchanged badge-radius and Places-spacing assertion failures, 2026-09-26 |
| SRI-003 | umbrella | Verify published pins and integration | SRI-001–SRI-002 | — | Planned | — | Pending publication and manual check |

Allowed states: `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`. A local `Done` is not integration. Record final integration commands, results, and date in SRI-003 before setting the initiative to `Integrated`.

The repository commits are local and the umbrella gitlinks remain at their previous published revisions. SRI-002 stays open until its full local acceptance gate is resolved. SRI-003 requires publication, pinning, and a manual desktop check.
