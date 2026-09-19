# Consistent HoloNight key hints — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| KH-001 | holonight-qt | Shared semantic renderer, wrapping, typography, accessibility and gallery | — | [SDD](../../../holonight-qt/docs/sdd/consistent-key-hints/SPEC.md) | Done | `8fe24ff` (published) | 2026-09-20: clean build, all 89 CTest entries have passing results after corrections; final affected run 20/20; focused tests in both styles, QML policy/lint, clang-tidy with explicit config, REUSE and font/DPR visual matrix. [Evidence](../../../holonight-qt/docs/sdd/consistent-key-hints/VERIFICATION.md). Published to canonical origin/main; pinned after user authorization. CI at `8fe24ff`: `in_progress`, no conclusion, [run](https://github.com/lebedenko/holonight-qt/actions/runs/35472139078) (checked once). |
| KH-002 | holonight-shell | Launcher, authentication and audio hints | KH-001 published and pinned | [SDD](../../../holonight-shell/docs/sdd/consistent-key-hints/SPEC.md) | Ready | — | Baseline `ab780d5d477400cdc70195d37783e9e080ee1d05`; verification pending |
| KH-003 | holonight-viewer | Footer, shortcut help and menu hints | KH-001 published and pinned | [SDD](../../../holonight-viewer/docs/sdd/consistent-key-hints/SPEC.md) | Ready | — | Baseline `01cdd23f7a9ddca7d74fab71ec067d9eead1a394`; verification pending |
| KH-004 | holonight-files | Quick Look and insert guidance | KH-001 published and pinned | [SDD](../../../holonight-files/docs/sdd/consistent-key-hints/SPEC.md) | Ready | — | Baseline `21d1589d28c70cb8a045019badb2a56167268744`; verification pending |
| KH-005 | umbrella | Verify integrated revisions and manual ecosystem behavior | KH-001–KH-004 | — | Planned | — | Pending |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in the final umbrella row before setting the initiative status to `Integrated`.

## Handoff boundary

The user authorized provider publication and pinning on 2026-09-20. `8fe24ff` is published
on canonical origin/main and pinned in this checkpoint. KH-002–KH-004 are Ready at the
listed exact baselines and must use this provider. Native ecosystem review and final
integration remain pending; the initiative remains Accepted.
