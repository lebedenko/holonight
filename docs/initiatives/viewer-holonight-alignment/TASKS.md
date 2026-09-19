# Viewer HoloNight alignment — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| V-001 | umbrella | Accept contracts and exact baselines | — | This initiative | Done | e75c245 | Canonical main refs verified 2026-09-19 before assignment; accepted user plan |
| V-002 | holonight-viewer | Alignment, checks and publication | V-001 | [SDD](../../../holonight-viewer/docs/sdd/holonight-alignment/README.md) | Ready | — | Assigned baseline c76a3c683ac500a75aab56c68998698cf428aad9 |
| V-003 | umbrella | Register published Viewer and verify integration | V-002 | This initiative | Planned | — | Pending published handoff and integration checks |

Starting review: umbrella e75c245ad04de0f3081573a296213af65435a7f2; Viewer c76a3c683ac500a75aab56c68998698cf428aad9. Provider refs verified against canonical remotes: Qt eadfe482000e64ee7ead83d63f878e3f365686b1; Config fe69a59e6b73167fd5349223a4d265d75386c139. Gitlinks remain authoritative.

Review found direct Basic/style imports, unsafe fixed-path removal, missing umbrella registration, library-owned QML, forced development paths, incomplete check inventories and source-local fixture paths. Existing review smoke: 124 passed, five skipped, three failed (WebP unavailable and navigation fixture assumption). This is an accepted implementation initiative, not integrated acceptance.
