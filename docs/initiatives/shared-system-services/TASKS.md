# Shared System Services — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SSS-001 | `holonight-system-services` | Exported static package and isolated Audio component | — | `docs/sdd/shared-system-services/` | Done | `0d84adb621dc8a2eaf900cfba9342633ea9eb563` | 2026-08-13: 84 provider tests and install-tree Audio consumer passed |
| SSS-002 | `holonight-shell` | Adopt Audio and preserve `AudioService` QML contract | SSS-001 | `docs/sdd/shared-system-services-adoption/` | Done | `20e505859a6877d9b88aa38cedf18a78c9ec00c2` | 2026-08-13: test-enabled build, architecture check, qmltypes/package checks passed |
| SSS-003 | `holonight-settings` | Adopt Audio and add Settings-owned Audio presentation | SSS-001 | `docs/sdd/shared-system-services-adoption/` | Done | `744c7d0e182365b793ec8ce9e5f194b09d1af4bb` | 2026-08-13: test-enabled build, 43 CTest cases (2 D-Bus skips), and qmllint passed |
| SSS-004 | `holonight-system-services` | Export isolated Network component | SSS-001–SSS-003 | Pending | Planned | — | — |
| SSS-005 | consumers | Adopt shared Network component | SSS-004 | Pending | Planned | — | — |
| SSS-006 | `holonight-system-services` | Export isolated Bluetooth component | SSS-001–SSS-003 | Pending | Planned | — | — |
| SSS-007 | consumers | Adopt shared Bluetooth component | SSS-006 | Pending | Planned | — | — |
| SSS-008 | umbrella | Verify integrated revisions and concurrent clients | SSS-001–SSS-007 | — | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and the verification date in SSS-008 before setting the initiative status to `Integrated`.
