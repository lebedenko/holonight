# Decoration-aware Viewer toolbar titles — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | holonight-qt | Core helper | — | [SDD](../../../holonight-qt/docs/sdd/decoration-aware-viewer-title/README.md) | In Progress | aa26e2e (local) | 2026-10-05: all 98 CTests, normal package install, QML checks and changed-source tidy pass; full OFF build and focused tests pass. task check fails on 12 pre-existing isolated_style_probe.cpp lint errors. Extra OFF install fixture unconditionally requires Wayland and fails. Native checks pending by user request. |
| I-002 | holonight-viewer | Header adoption | I-001 | [SDD](../../../holonight-viewer/docs/sdd/decoration-aware-viewer-title/README.md) | Done | bcfdf7f (local) | 2026-10-05: task check passes, all 27 CTests pass; final strengthened header test passes. Local provider content aa26e2e verified with BUILD_WAYLAND=ON. Hosted CI provider update awaits publication. |
| I-003 | umbrella | Verify integrated revisions | I-001–I-002 | — | Planned | — | Not run: provider acceptance gap, publication/pin authorization and native checks remain pending. Existing gitlinks are preserved. |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in the final umbrella row before setting the initiative status to `Integrated`.

## Session boundary

Implementation commits are local on each repository's main branch. No pushes, hosted CI waits, CI dependency pins or umbrella gitlink updates were authorized or performed. The existing untracked Viewer report was preserved. Initiative status remains Accepted; these working trees and local commits are not an integrated umbrella state.

Before publication, resolve provider acceptance gaps, publish the provider, update Viewer's CI dependency to that available revision and rehearse it. The native SSD/CSD/undecorated/fullscreen/surface-recreation checks remain pending by user request. No umbrella integration checks ran while I-001 remains In Progress.
