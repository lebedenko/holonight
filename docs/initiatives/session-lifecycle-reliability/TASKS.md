# Session Lifecycle Reliability — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SLR-001 | `holonight-greeter` | Safe VT2 live harness and core capture | — | `docs/sdd/boot-login-reliability/` | Done | `6edd3b5` | Published to canonical `origin/main`. Thirty-two tests, formatting, qmllint, Hyprland Lua parsing, temporary install, and the physical `eDP-1`/`DP-5` isolated-VT check passed on 2026-08-11. |
| SLR-002 | `holonight-shell` | UWSM-aware logout | SLR-001 | `docs/sdd/session-logout-reliability/` | Done | `757d26a` | Published to canonical `origin/main`. `task test` passed 1,142/1,142 tests on 2026-08-11, with three declared environment skips. |
| SLR-003 | umbrella | Verify integrated revisions | SLR-001–SLR-002 | — | In Progress | — | Pinned handoffs are ready; production migration, sidebar logout, reboot, and final journal review remain. |
