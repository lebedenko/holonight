# HoloNight Hyprlock Theme — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| HYL-101 | `holonight-hyprlock` | Implement theme, helper, assets, package, docs, and automated tests from `b22cb16` | — | [SDD](../../../holonight-hyprlock/docs/sdd/hyprlock-theme/README.md) | Done | `d9db610` | 2026-09-03: shell syntax, CMake, 2/2 CTest tests, staged install and PNG validation passed with hyprlock v0.9.6; commit published to canonical `origin/main`. |
| HYL-201 | umbrella | Verify published commit, register and pin submodule, and complete final integration | HYL-101 | — | In Progress | — | 2026-09-03: canonical `origin/main` contains `d9db610`; clean gitlink staged at that revision. At the pinned revision, `sh -n scripts/status tests/test-status.sh tests/test-package.sh`, CMake configure/build, and 2/2 CTest tests passed with hyprlock v0.9.6; staged install and asset checks are covered by `package-layout`. Manual lock-screen acceptance remains. |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on HYL-101 is a local checkpoint, not an integrated initiative. HYL-201 may be marked `Done` and the
initiative `Integrated` only after the pinned-revision checks and manual lock-screen acceptance both pass.
