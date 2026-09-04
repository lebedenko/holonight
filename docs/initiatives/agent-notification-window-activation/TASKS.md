# Agent Notification Window Activation — Coordination Ledger

| ID | Repository | Baseline | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|---|
| ANWA-101 | `holonight-shell` | `b48574d39a83943cb7c6fa012ed0066bb8120399` | Shell activation provider | — | [`SPEC`](../../../holonight-shell/docs/sdd/agent-window-activation/SPEC.md), [`DESIGN`](../../../holonight-shell/docs/sdd/agent-window-activation/DESIGN.md), [`TASKS`](../../../holonight-shell/docs/sdd/agent-window-activation/TASKS.md) | Done | `c2fa018aabb4dc3c9125d9e956237757d2a6975a` | 2026-09-04: published to canonical `origin/main`; full pre-handoff suite passed 1,094/1,094 tests, and the Hyprland 0.56 Lua compatibility correction passed 42/42 focused activation checks plus format, tidy, architecture, QML metadata, and user-confirmed Hyprland/Sway positive and fail-safe manual checks. |
| ANWA-102 | `holonightd` | `dbb6ecc6205f964c3c4dc4e2467503ee940dc34f` | Daemon session activation and notification action adoption | ANWA-101 | [`SPEC`](../../../holonightd/docs/sdd/agent-notification-window-activation/SPEC.md), [`DESIGN`](../../../holonightd/docs/sdd/agent-notification-window-activation/DESIGN.md), [`TASKS`](../../../holonightd/docs/sdd/agent-notification-window-activation/TASKS.md) | Ready | — | — |
| ANWA-201 | umbrella | Current accepted pins | Pin and verify integrated revisions on Hyprland and Sway | ANWA-101, ANWA-102 | — | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in `ANWA-201` before setting the initiative status to `Integrated`.
