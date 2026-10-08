# HoloNight FileChooser portal — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | holonight-files | Extract installed browsing Core/Quick, adopt in Files, verify independent consumers | — | [SDD](../../../holonight-files/docs/sdd/filechooser-provider/README.md) | Done | cfc130e3cd0b0eb56a94f6b9435d433bc96cb78e | Local verification 2026-10-08: independent Core/Quick and installed C++/QML/plugin consumers; Files regressions, Debug/clean Release, full lint/format/import/metadata/license and staged/isolated runtime pass. Prerequisite lint commit b74ee94. See local verification record. Both commits unpublished; gitlink unchanged. |
| I-002 | xdg-desktop-portal-holonight | Standalone protocol/lifecycle, private chooser and Wayland parenting | I-001 published/pinned | Pending | Planned | — | Provider handoff required before assignment |
| I-003 | holonight-shell | Route FileChooser=holonight-filechooser;gtk in HoloNight/Hyprland/Sway/labwc | I-002 published/pinned | Pending | Planned | — | Baseline 25e1556bc5ffc06015a757d48e468f7c0d9c9ccb; preserve Settings/compositor preferences |
| I-004 | umbrella | Verify exact published ecosystem revisions and manual acceptance | I-001–I-003 | — | Planned | — | No integration or publication claimed |

States: Planned, Ready, In Progress, Done, Blocked, Superseded. Done requires a local commit and passing
local verification; it does not mean integrated. Record final commands, results and date in I-004 before
changing initiative status to Integrated. No implementation revisions have been pinned.
