# First-Class Sway Support — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SWS-101 | `holonight-qt` | Optional shared Wayland layer-surface host | — | `docs/sdd/shared-wayland-surface-host/` | Ready | — | Baseline `8b25b721e7a4`; run `task verify` and package-consumer/lifecycle tests. |
| SWS-102 | `holonight-shell` | Compositor subsystem, shared surface adoption, sessions, and portals | SWS-101 | `docs/sdd/sway-compositor-support/` | Planned | — | Baseline `791ec98e87b1`; run `task test`, `task format-check`, `task tidy`, `task qml-lint`, `task qmltypes-check`, and `task architecture-check`. |
| SWS-103 | `holonight-ai` | Quick-panel adoption of the shared surface host | SWS-101 | `docs/sdd/shared-wayland-surface-host-adoption/` | Planned | — | Baseline `6868ac8775ac`; run tests, formatting, tidy, QML lint, and qmltypes checks. |
| SWS-201 | umbrella | Pin published revisions and verify the integrated ecosystem and unchanged greeter | SWS-101–SWS-103 | — | Planned | — | Verify clean published pins in dependency order, stage the Shell install, run greeter tests, then record commands, results, manual checks, and date. |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in SWS-201 before setting the initiative status to `Integrated`.
