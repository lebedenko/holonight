# Shared image outcomes — Coordination Ledger

Both packages were Ready after baseline/contract inspection, then assigned to the current implementer.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | holonight-files | Preserve preview outcomes | Existing Images contract | [SDD](../../../holonight-files/docs/sdd/shared-image-outcomes/SPEC.md) | Done | e8efed169bcea51c1ebdc846525a50331a2e298d | 2026-09-23: focused regressions, clean Release, all task check stages and isolated runtime passed; [evidence](../../../holonight-files/docs/sdd/shared-image-outcomes/VERIFICATION.md) |
| I-002 | holonight-viewer | Preserve document outcomes | Existing Images contract | [SDD](../../../holonight-viewer/docs/sdd/shared-image-outcomes/SPEC.md) | Done | 6ed3a3aa471b5c7c585c40f495b2849d83679f2c | 2026-09-23: focused regressions, clean Release, all task check stages and isolated runtime passed; Qt QMLFORMAT override required; [evidence](../../../holonight-viewer/docs/sdd/shared-image-outcomes/VERIFICATION.md) |
| I-003 | umbrella | Verify integrated revisions | I-001, I-002 | — | Planned | — | Deferred; consumer publication and pinning completed, umbrella integration and native qualification remain open |

Done records locally verified, published consumer commits; it does not mark the initiative Integrated.

## Publication and pin checkpoint — 2026-09-23

Both commits were pushed once to their canonical origin/main branches; push results and clean tracking state confirmed availability before pinning. Images remains at `3633865d2f39e4f163f0159a0f252f88245379f0`. Consumer code is the locally verified implementation; only documentation was updated for publication authorization. Documentation links and staged diffs pass review.

Latest available CI was checked once after publication; no wait or polling:

| Repository | Revision | Run | Status | Conclusion |
|---|---|---|---|---|
| Files | e8efed169bcea51c1ebdc846525a50331a2e298d | [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/35869945371) | in_progress | None yet |
| Viewer | 6ed3a3aa471b5c7c585c40f495b2849d83679f2c | [Build and checks](https://github.com/lebedenko/holonight-viewer/actions/runs/35869953629) | in_progress | None yet |

The umbrella checkpoint remains local. Sharp-preview T5, mixed-monitor qualification and other deferred native gates remain open; no umbrella integration acceptance is claimed.
