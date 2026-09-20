# Consistent HoloNight key hints — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| KH-001 | holonight-qt | Shared semantic renderer, wrapping, typography, accessibility and gallery | — | [SDD](../../../holonight-qt/docs/sdd/consistent-key-hints/SPEC.md) | Done | `8fe24ff` (published) | 2026-09-20: clean build, all 89 CTest entries have passing results after corrections; final affected run 20/20; focused tests in both styles, QML policy/lint, clang-tidy with explicit config, REUSE and font/DPR visual matrix. [Evidence](../../../holonight-qt/docs/sdd/consistent-key-hints/VERIFICATION.md). Published to canonical origin/main; pinned after user authorization. CI at `8fe24ff`: `in_progress`, no conclusion, [run](https://github.com/lebedenko/holonight-qt/actions/runs/35472139078) (checked once). |
| KH-002 | holonight-shell | Launcher, authentication and audio hints | KH-001 published and pinned | [SDD](../../../holonight-shell/docs/sdd/consistent-key-hints/SPEC.md) | Done | `d109fb3` (published) | 2026-09-20: Shell: clean Release build; 1,175/1,175 CTest entries; QML lint/type/package, format and license checks; authentication visual review at 1.25. Published to canonical origin/main and pinned after user authorization. Latest CI at `d109fb3`: CI, `in_progress`, no conclusion; [run](https://github.com/lebedenko/holonight-shell/actions/runs/35475413092) (checked once). |
| KH-003 | holonight-viewer | Footer, shortcut help and menu hints | KH-001 published and pinned | [SDD](../../../holonight-viewer/docs/sdd/consistent-key-hints/SPEC.md) | Done | `746acb2` (published) | 2026-09-20: Viewer: clean Release build; final 20/20 CTest entries; format/tidy/QML/license, staged install and isolated runtime passed; footer/help visual review at fractional scales. Published to canonical origin/main and pinned after user authorization. Latest CI at `746acb2`: Licensing, `queued`, no conclusion; [run](https://github.com/lebedenko/holonight-viewer/actions/runs/35475414932) (checked once). |
| KH-004 | holonight-files | Quick Look and insert guidance | KH-001 published and pinned | [SDD](../../../holonight-files/docs/sdd/consistent-key-hints/SPEC.md) | Done | `550e662` (published) | 2026-09-20: Files: clean Release build; 17 focused tests and all 9 acceptance CTest entries; format/tidy/QML/license, staged install and isolated runtime passed; insert and Quick Look visual review. Published to canonical origin/main and pinned after user authorization. Latest CI at `550e662`: Build and checks, `in_progress`, no conclusion; [run](https://github.com/lebedenko/holonight-files/actions/runs/35475417057) (checked once). |
| KH-005 | umbrella | Verify integrated revisions and manual ecosystem behavior | KH-001–KH-004, KH-006–KH-008 | — | Planned | — | Pending |
| KH-006 | holonight-qt | Extract frameless HnKeySequenceLabel and refine compact badge geometry; baseline `8fe24ff83f8108631c2b7b0351994f7e513acfcd` | KH-001 | [SDD](../../../holonight-qt/docs/sdd/consistent-key-hints/SPEC.md) | Done | `9723cef7371a4ca5f2967d869b26ee7ff1e3c789` (published) | 2026-09-20: entered Ready before implementation. Clean Debug build, 89/89 CTest entries, seven focused tests under both styles, QML lint/policy, full clang-tidy, format, REUSE and 8/12/18 pt captures at scales 1/1.25/1.5 passed. [Evidence](../../../holonight-qt/docs/sdd/consistent-key-hints/VERIFICATION.md#kh-006-refinement-acceptance--2026-09-20). Published to canonical origin/main and pinned after user authorization. CI at `9723cef`: `in_progress`, no conclusion, [run](https://github.com/lebedenko/holonight-qt/actions/runs/35512774792) (checked once). |
| KH-007 | holonight-viewer | Frameless menu sequences and resolved footer font-size synchronization; baseline `746acb2f00e427eab97743feda7492fbc40c751e` | KH-006 published and pinned | [SDD](../../../holonight-viewer/docs/sdd/consistent-key-hints/SPEC.md) | Ready | — | Corrected provider published and pinned on user authorization; exact Viewer baseline unchanged. |
| KH-008 | holonight-shell, holonight-files | Verify existing consumers against corrected provider | KH-006 published and pinned | [Shell SDD](../../../holonight-shell/docs/sdd/consistent-key-hints/SPEC.md), [Files SDD](../../../holonight-files/docs/sdd/consistent-key-hints/SPEC.md) | Ready | — | Corrected provider published and pinned; regression verification only. Any product fix needs a separate work package. Files has unrelated active edits; verify an isolated checkout of its pinned revision. |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in the final umbrella row before setting the initiative status to `Integrated`.

## Historical KH-001–KH-004 handoff boundary

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

## Refinement handoff — 2026-09-20

KH-001–KH-004 and their evidence remain historical completed work. The initiative
remains Accepted; the new acceptance gate includes KH-006–KH-008. The previous
publication authorization covered the four recorded implementation revisions.
Corrected-provider publication and pinning require a new concrete handoff before
KH-007 or KH-008 starts. Native menu/footer/help and ecosystem interaction remain
manual user checks. Existing untracked Files `docs/sdd/quick-look-text-viewer/`
work is unrelated and must be preserved.

KH-006 is locally complete at `9723cef7371a4ca5f2967d869b26ee7ff1e3c789`.
The provider working tree is clean and main is one commit ahead of origin/main.
This checkpoint updates coordination documentation only; the authoritative provider
gitlink remains `8fe24ff83f8108631c2b7b0351994f7e513acfcd`. No follow-up commit has
been pushed or pinned, and no follow-up CI result is claimed. KH-007 and KH-008
remain Planned until the provider handoff is authorized and completed.

## Authorized provider publication — 2026-09-20

The user authorized publishing KH-006, pinning it, and continuing KH-007/KH-008.
Provider `9723cef7371a4ca5f2967d869b26ee7ff1e3c789` was pushed to canonical
origin/main. Its working tree is clean. The provider gitlink is updated in this
checkpoint, making KH-007 and KH-008 Ready. CI was checked once: in progress,
without a conclusion; no waiting or polling. The earlier local-only handoff above
is historical. Viewer publication remains a subsequent completed-work handoff.
