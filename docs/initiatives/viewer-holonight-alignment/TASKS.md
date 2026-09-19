# Viewer HoloNight alignment — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| V-001 | umbrella | Accept contracts and exact baselines | — | This initiative | Done | 3e7156e | Canonical main refs verified 2026-09-19 before assignment; accepted user plan |
| V-002 | holonight-viewer | Alignment, checks and publication | V-001 | [SDD](../../../holonight-viewer/docs/sdd/holonight-alignment/README.md) | Done | a37af1c2d3088b1139e1de63b445e10783e2b76d | Published and canonical main verified 2026-09-19; 20/20 CTest, tidy, formatting, QML lint/import/metadata, REUSE, Debug/Release staged runtime, stale-prefix exclusion and native HoloNight/Fusion passed. [Details](../../../holonight-viewer/docs/sdd/holonight-alignment/VERIFICATION.md). Hosted CI pending. |
| V-003 | umbrella | Register published Viewer and verify integration | V-002 | This initiative | Ready | — | Published Viewer handoff accepted; installer registration and integration checks ready |

Starting review: umbrella e75c245ad04de0f3081573a296213af65435a7f2; Viewer c76a3c683ac500a75aab56c68998698cf428aad9. Provider refs verified against canonical remotes: Qt eadfe482000e64ee7ead83d63f878e3f365686b1; Config fe69a59e6b73167fd5349223a4d265d75386c139. Gitlinks remain authoritative.

Review found direct Basic/style imports, unsafe fixed-path removal, missing umbrella registration, library-owned QML, forced development paths, incomplete check inventories and source-local fixture paths. Existing review smoke: 124 passed, five skipped, three failed (WebP unavailable and navigation fixture assumption). This is an accepted implementation initiative, not integrated acceptance.

Provider validation: Config fresh build, 2/2 CTest passed. Qt fresh build: 79/80 passed with Wayland disabled; package-consumer check requires Wayland. After enabling the existing component, Wayland and package-install checks passed (2/2). No provider source changes. Native Viewer appearance/interaction checks passed by user report on 2026-09-19.
