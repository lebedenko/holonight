# GTK Visual Fidelity — Coordination Ledger

This initiative is a low-priority deferred draft. Every work package remains `Planned`; none may be assigned until
the initiative is explicitly prioritized, its discovery contracts are settled, and its status becomes `Accepted`.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| GVF-001 | umbrella | Inventory GTK 3, GTK 4, and libadwaita versions and representative applications; capture current HoloNight Qt versus GTK accent, surface, typography, contrast, and mixed-DPI differences | Cross-Toolkit Visual Consistency integrated | This initiative | Planned | — | — |
| GVF-002 | umbrella | Decide fidelity tiers, supported versions, semantic mappings, accent approximation gates, theme packaging, visual-test protocol, rollback ownership, and the third-party libadwaita boundary | GVF-001 | This initiative | Planned | — | — |
| GVF-003 | `holonight-config` | Specify and implement a portable document-font role only if GVF-002 accepts the schema extension | GVF-002 | Pending | Planned | — | — |
| GVF-004 | `holonight-qt` | Publish any accepted semantic/reference fixtures needed by GTK generators without adding GTK implementation to Qt | GVF-002, optionally GVF-003 | Pending | Planned | — | — |
| GVF-101 | `holonight-appearance-adapters` | Implement deterministic accent translation and separately versioned generated GTK 3 and conventional GTK 4 themes with atomic apply/revert, diagnostics, parser probes, and contrast tests | GVF-002–GVF-004 | Pending | Planned | — | — |
| GVF-102 | `holonight-appearance-adapters` | Evaluate supported libadwaita preference propagation and HoloNight-owned opt-in CSS; reject global third-party palette overrides unless a stable upstream contract is demonstrated | GVF-002–GVF-004 | Pending | Planned | — | — |
| GVF-103 | `holonight-settings` | Add preview, status, selection, opt-in disclosure, and Restore Native Defaults orchestration for accepted generated artifacts | GVF-101–GVF-102 | Pending | Planned | — | — |
| GVF-201 | umbrella | Verify exact published revisions across GTK/libadwaita versions, representative applications, accent combinations, dialogs, accessibility, typography, mixed-DPI displays, failure recovery, and native fallback | GVF-101–GVF-103 | — | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record commands, exact revisions,
automated results, visual observations, supported-version boundaries, and restoration evidence in GVF-201 before
setting the initiative status to `Integrated`.
