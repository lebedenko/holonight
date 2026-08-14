# First-Class Sway Support — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SWS-101 | `holonight-qt` | Optional shared Wayland layer-surface host | — | `docs/sdd/shared-wayland-surface-host/` | Done | `a45f7552054abbc6cbd66609e802b43b9b8ee894` | 2026-08-13: <code>QT_QPA_PLATFORM=offscreen ctest --test-dir build -R 'holonight_(wayland&#124;package_install)_test' --output-on-failure</code> passed 2/2; `cmake --build build --target format-check` passed; `task verify` passed build/tidy and 26/26 tests. Commit confirmed at canonical `origin/main`. |
| SWS-102 | `holonight-shell` | Compositor subsystem, shared surface adoption, sessions, and portals | SWS-101 | `docs/sdd/sway-compositor-support/` | Done | `984ef384a618812a1de7ac138181130374353c59` | 2026-08-14: final handoff record over implementation completion `248a61d9f947b56e6fddeb60d8e3c06a0228a13f`. Focused compositor (18), surface (164), and session (44) tests passed; `task test` passed 1059 tests with 2 existing no-session-D-Bus skips; build, format, tidy, QML types, architecture, session-script, temporary-install, and out-of-sandbox Sway runtime smoke checks passed. QML lint retained existing unresolved `AudioService` warnings. Canonical CI [31757317259](https://github.com/lebedenko/holonight-shell/actions/runs/31757317259) passed both jobs at the exact implementation commit and accepted dependency revisions. Final handoff confirmed at canonical `origin/main`. |
| SWS-103 | `holonight-ai` | Quick-panel adoption of the shared surface host | SWS-101 | `docs/sdd/shared-wayland-surface-host-adoption/` | Done | `20c40fe3b66b53912e738cdc5da49ac3550891f7` | 2026-08-14: final documentation handoff over implementation handoff `5e96acc06a6a5b9ae342cfd677e9350d6ba01784`. `task test` passed 711 tests with the existing environment-gated Secret Service integration skip; release build, format, tidy, QML lint, and QML types passed. QML lint retained existing missing-property warnings. Canonical CI [31800288242](https://github.com/lebedenko/holonight-ai/actions/runs/31800288242) passed both jobs at the implementation handoff; final handoff confirmed at canonical `origin/main` and intentionally skipped CI because it changes documentation only. |
| SWS-201 | umbrella | Pin published revisions and verify the integrated ecosystem and unchanged greeter | SWS-101–SWS-103 | — | Ready | — | Published Qt, Shell, AI, and unchanged Greeter revisions confirmed. Run clean provider-first integration, alternate-root install, descriptor dispatch harness, and user-performed compositor acceptance before marking this task Done. |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in SWS-201 before setting the initiative status to `Integrated`.
