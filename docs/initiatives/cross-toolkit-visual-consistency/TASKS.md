# Cross-Toolkit Visual Consistency — Coordination Ledger

The initiative is in discovery. Implementation packages remain `Planned` until the relevant contracts, ownership,
baselines, and repository-local SDDs are settled and the initiative is `Accepted`.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| CTV-001 | umbrella | Inventory representative applications and record toolkit/version, Wayland/XWayland mode, supported mechanisms, current behavior, target tier, and fallback | — | This initiative | Done | Umbrella commit containing this row | 2026-08-07: inspected Hyprland program/keybinding configuration, desktop entries, package ownership/versions, ELF linkage, Electron flags, GNOME interface settings, installed Qt/GTK/portal components, and live `hyprctl clients -j`; documented primary and fixture matrices plus conclusions in README |
| CTV-002 | umbrella | Decide ownership for GTK 3/4 and toolkit-neutral adapter artifacts; revise the ownership map or create a repository proposal | CTV-001 | This initiative | Planned | — | — |
| CTV-003 | `holonight-qt` | Specify the versioned semantic appearance export and compatibility rules for non-Qt consumers | CTV-001–CTV-002 | Pending | Planned | — | — |
| CTV-004 | `holonight-qt` | Complete Qt 5 Widgets feasibility study: reusable code, Qt 5 API differences, private-API/rebuild policy, packaging, and representative application tests | CTV-001 | Pending | Planned | — | — |
| CTV-005 | Toolkit adapter owner (TBD) | Prototype GTK 3 and GTK 4 Tier 1 mechanisms; compare GSettings, XSettings, portal, environment, and generated artifacts | CTV-001–CTV-003 | Pending | Planned | — | — |
| CTV-006 | Toolkit adapter owner (TBD) | Prototype GTK 3/4 Tier 2 palette mappings and record the accept/reject decision for each GTK major | CTV-005 | Pending | Planned | — | — |
| CTV-007 | umbrella | Accept scope, support matrix, contracts, dependency order, phase boundaries, and local SDD links | CTV-002–CTV-006 | This initiative | Planned | — | — |
| CTV-101 | Toolkit adapter owner (TBD) | Implement accepted standards-based appearance outputs and GTK Tier 1 integration | CTV-007 | Pending | Planned | — | — |
| CTV-102 | `holonight-settings` | Implement user-facing apply/revert, validation, status, and reload semantics for accepted outputs | CTV-101 | Pending | Planned | — | — |
| CTV-103 | `holonight-shell` | Implement Hyprland session/portal propagation and diagnostics using the accepted contract | CTV-101 | Pending | Planned | — | — |
| CTV-201 | `holonight-qt` | Implement accepted Qt 5 Widgets palette/style compatibility, separate Qt 5 packaging, and local tests | CTV-004, CTV-007 | Pending | Planned | — | — |
| CTV-202 | `holonight-qt` | Implement Qt 5 platform-theme integration only if accepted by CTV-004; otherwise mark this package `Superseded` with the decision | CTV-201 | Pending | Planned | — | — |
| CTV-301 | Toolkit adapter owner (TBD) | Implement accepted GTK 3 Tier 2 palette adapter, or mark `Superseded` if CTV-006 rejects it | CTV-006–CTV-007 | Pending | Planned | — | — |
| CTV-302 | Toolkit adapter owner (TBD) | Implement accepted GTK 4 Tier 2 palette adapter, or mark `Superseded` if CTV-006 rejects it | CTV-006–CTV-007 | Pending | Planned | — | — |
| CTV-401 | umbrella | Survey remaining Electron/Chromium and Java gaps after baseline integration and propose only evidence-backed follow-up packages | CTV-101–CTV-103 | This initiative | Planned | — | — |
| CTV-501 | umbrella | Verify exact revisions under Hyprland against the accepted application, fallback, accessibility, high-DPI, Wayland/XWayland, and rollback matrix | CTV-102–CTV-103, CTV-201–CTV-302 | — | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands,
results, application versions, and the verification date in CTV-501 before setting the initiative status to
`Integrated`.
