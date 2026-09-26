# Size roles and icon resolution — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SRI-001 | `holonight-qt` | Xs, header size role, icon resolution | — | [SDD](../../../holonight-qt/docs/sdd/size-roles-icon-resolution/README.md) | Done | `61d0c16` (published) | Clean Release build and 87/87 CTests passed; focused metrics/QML/icon tests, clang-tidy, formatting and REUSE passed; installed theme rendered HoloNight `#131e2c`, 2026-09-26 |
| SRI-002 | `holonight-files` | 42 px header and Xs navigation | SRI-001 | [SDD](../../../holonight-files/docs/sdd/size-roles-icon-resolution/README.md) | Done | `1a46a54` (published; implementation `b058f67`) | `task check`: 27/27 CTests, formatting, lint, REUSE, staged install, import and QML metadata checks passed; isolated Docker runtime check passed; focused history/icon/provider-revision tests passed against `61d0c16`, 2026-09-26 |
| SRI-003 | umbrella | Verify published pins and integration | SRI-001–SRI-002 | — | Ready | — | Published pins verified; final root integration and manual desktop check pending, 2026-09-26 |

Allowed states: `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`. A local `Done` is not integration. Record final integration commands, results, and date in SRI-003 before setting the initiative to `Integrated`.

The umbrella gitlinks pin the published revisions above. The Files pin also includes its pre-existing published baseline `c85e0e0` (badge and breadcrumb corner change), which was ahead of the previous umbrella pin. SRI-003 remains open for the manual desktop check and final integration review.

## Published CI snapshot — 2026-09-26

This records the latest available runs after publication. Pending runs were not polled to completion.

| Repository | Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|---|
| `holonight-qt` | `61d0c16` | CI | in_progress | — | [36245860205](https://github.com/lebedenko/holonight-qt/actions/runs/36245860205) |
| `holonight-files` | `1a46a54` | Build and checks | in_progress | — | [36245874664](https://github.com/lebedenko/holonight-files/actions/runs/36245874664) |
| `holonight-files` | `1a46a54` | Licensing | completed | success | [36245874650](https://github.com/lebedenko/holonight-files/actions/runs/36245874650) |
