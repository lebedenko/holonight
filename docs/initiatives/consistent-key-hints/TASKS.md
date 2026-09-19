# Consistent HoloNight key hints — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| KH-001 | holonight-qt | Shared semantic renderer, wrapping, typography, accessibility and gallery | — | [SDD](../../../holonight-qt/docs/sdd/consistent-key-hints/SPEC.md) | Done | `8fe24ff` (published) | 2026-09-20: clean build, all 89 CTest entries have passing results after corrections; final affected run 20/20; focused tests in both styles, QML policy/lint, clang-tidy with explicit config, REUSE and font/DPR visual matrix. [Evidence](../../../holonight-qt/docs/sdd/consistent-key-hints/VERIFICATION.md). Published to canonical origin/main; pinned after user authorization. CI at `8fe24ff`: `in_progress`, no conclusion, [run](https://github.com/lebedenko/holonight-qt/actions/runs/35472139078) (checked once). |
| KH-002 | holonight-shell | Launcher, authentication and audio hints | KH-001 published and pinned | [SDD](../../../holonight-shell/docs/sdd/consistent-key-hints/SPEC.md) | Done | `d109fb3` (published) | 2026-09-20: Shell: clean Release build; 1,175/1,175 CTest entries; QML lint/type/package, format and license checks; authentication visual review at 1.25. Published to canonical origin/main and pinned after user authorization. Latest CI at `d109fb3`: CI, `in_progress`, no conclusion; [run](https://github.com/lebedenko/holonight-shell/actions/runs/35475413092) (checked once). |
| KH-003 | holonight-viewer | Footer, shortcut help and menu hints | KH-001 published and pinned | [SDD](../../../holonight-viewer/docs/sdd/consistent-key-hints/SPEC.md) | Done | `746acb2` (published) | 2026-09-20: Viewer: clean Release build; final 20/20 CTest entries; format/tidy/QML/license, staged install and isolated runtime passed; footer/help visual review at fractional scales. Published to canonical origin/main and pinned after user authorization. Latest CI at `746acb2`: Licensing, `queued`, no conclusion; [run](https://github.com/lebedenko/holonight-viewer/actions/runs/35475414932) (checked once). |
| KH-004 | holonight-files | Quick Look and insert guidance | KH-001 published and pinned | [SDD](../../../holonight-files/docs/sdd/consistent-key-hints/SPEC.md) | Done | `550e662` (published) | 2026-09-20: Files: clean Release build; 17 focused tests and all 9 acceptance CTest entries; format/tidy/QML/license, staged install and isolated runtime passed; insert and Quick Look visual review. Published to canonical origin/main and pinned after user authorization. Latest CI at `550e662`: Build and checks, `in_progress`, no conclusion; [run](https://github.com/lebedenko/holonight-files/actions/runs/35475417057) (checked once). |
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

The user authorized provider and consumer publication and pinning on 2026-09-20.
All four implementation commits are available from their canonical origin/main;
the gitlinks pin those revisions and participating working trees are clean.
Consumers use the accepted provider's semantic API without private content or
symbol-geometry overrides. The local acceptance evidence applies to these exact
revisions; no implementation changed during publication.

Consumer CI was checked once after publication; the observed pending statuses
are recorded above, without waiting for completion. The umbrella checkpoint
remains local. Native ecosystem review and final integration remain pending;
the initiative remains Accepted.

## Manual ecosystem review (pending)

After consumer publication/pinning and deployment through the normal umbrella
workflow, the user must review Launcher footer/selection, audio focus-context
hints, authentication buttons, Viewer footer/help/menu and Files Quick Look/insert
validation at native display scale. Confirm visual fit and unchanged keyboard
actions. Offscreen regression tests and captured visual evidence have passed;
no native pointer or focus interaction was automated.
