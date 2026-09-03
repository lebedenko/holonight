# HoloNight Hyprlock Theme — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| HYL-101 | `holonight-hyprlock` | Implement theme, helper, assets, package, docs, automated tests, and nested-session workflow from `b22cb16` | — | [SDD](../../../holonight-hyprlock/docs/sdd/hyprlock-theme/README.md) | Done | `29b22d1` | 2026-09-03: shell syntax, CMake, 2/2 CTest tests, and staged install passed with hyprlock v0.9.6; the status panel uses font glyphs without generated status PNGs, and its Wi-Fi glyph spacing was visually confirmed; commits through `29b22d1` published to canonical `origin/main`. |
| HYL-201 | umbrella | Verify published commit, register and pin submodule, and complete final integration | HYL-101 | — | In Progress | — | 2026-09-03: canonical `origin/main` contains `29b22d1`; clean gitlink pinned at that revision. At the pinned revision, shell syntax, CMake configure/build, 2/2 CTest tests, staged install, and config checks passed. Full interactive `task test` lock-screen acceptance remains. |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on HYL-101 is a local checkpoint, not an integrated initiative. HYL-201 may be marked `Done` and the
initiative `Integrated` only after the pinned-revision checks and manual lock-screen acceptance both pass.
