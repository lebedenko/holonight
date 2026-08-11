# Ecosystem Maintainability Standardization — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| EMS-001 | `holonight-config` | Review shared-library maintenance and publish local backlog | — | [SDD](../../../holonight-config/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `d05367d` | Review/backlog published; `git diff --check` passed |
| EMS-002 | `holonight-qt` | Review exported Qt/QML packages and publish local backlog | EMS-001 | [SDD](../../../holonight-qt/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `12f9c51` | Review/backlog published; staged provider build passed |
| EMS-003 | `holonight-appearance-adapters` | Review adapter/probe boundaries and publish local backlog | EMS-001–EMS-002 | [SDD](../../../holonight-appearance-adapters/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `8575582` | Review/backlog published; staged production build passed |
| EMS-004 | `holonight-icons` | Review asset lifecycle and publish local backlog | — | [SDD](../../../holonight-icons/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `859f377` | Review/backlog published; validation and staged asset checks passed |
| EMS-005 | `holonight-shell` | Review QML/system integration and publish local backlog | EMS-001–EMS-002 | [SDD](../../../holonight-shell/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `fff1ae4` | Review/backlog published; staged Release build passed |
| EMS-006 | `holonight-settings` | Review application/package boundaries and publish local backlog | EMS-001–EMS-002 | [SDD](../../../holonight-settings/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `de6abfd` | Review/backlog published; staged Release build passed |
| EMS-007 | `holonight-ai` | Review product structure, fix pinned appearance contract, and publish backlog | EMS-002 | [SDD](../../../holonight-ai/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `6868ac8` | Published; Release build and 703 tests passed (one guarded integration test skipped) |
| EMS-008 | `holonight-pkg-manager` | Review package-manager application and publish pinned revision/backlog | EMS-002 | [SDD](../../../holonight-pkg-manager/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `aca33a6` | Previously unpublished baseline and backlog published; staged Release build passed |
| EMS-009 | `holonight-greeter` | Review Greeter/system integration and publish local backlog | EMS-002 | [SDD](../../../holonight-greeter/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `39a38da` | Review/backlog published; staged Release build/assets passed |
| EMS-010 | `holonightd` | Review daemon/service lifecycle and publish local backlog | — | [SDD](../../../holonightd/docs/sdd/ecosystem-maintainability-standardization/README.md) | Done | `657508a` | Review/backlog published; staged Release build passed; pre-existing untracked doc excluded |
| EMS-011 | umbrella | Implement source installer, uninstaller, preflight, manifest, and docs | — | — | Done | — | 2026-08-12: `task --list`; `bash -n`; `scripts/install.sh --check`; complete alternate-root build/install; manifest hash/mode/symlink checks; modified-file-preserving uninstall |
| EMS-012 | umbrella | Pin published repository handoffs and run final Arch integration | EMS-001–EMS-011 | — | In Progress | — | Published handoffs ready for umbrella checkpoint; real `/usr` verification pending |

CI-image changes in every local backlog refer to the existing Shared CI Build Infrastructure initiative and are not
implemented or duplicated here.

Allowed states are `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`. Repository `Done` means the
local commit passed local verification; only EMS-012 may make this initiative `Integrated`.
