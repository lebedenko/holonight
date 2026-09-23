# Shared image outcomes — Coordination Ledger

Both packages were Ready after baseline/contract inspection, then assigned to the current implementer.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | holonight-files | Preserve preview outcomes | Existing Images contract | [SDD](../../../holonight-files/docs/sdd/shared-image-outcomes/SPEC.md) | Done | e8efed169bcea51c1ebdc846525a50331a2e298d | 2026-09-23: focused regressions, clean Release, all task check stages and isolated runtime passed; [evidence](../../../holonight-files/docs/sdd/shared-image-outcomes/VERIFICATION.md) |
| I-002 | holonight-viewer | Preserve document outcomes | Existing Images contract | [SDD](../../../holonight-viewer/docs/sdd/shared-image-outcomes/SPEC.md) | Done | 6ed3a3aa471b5c7c585c40f495b2849d83679f2c | 2026-09-23: focused regressions, clean Release, all task check stages and isolated runtime passed; Qt QMLFORMAT override required; [evidence](../../../holonight-viewer/docs/sdd/shared-image-outcomes/VERIFICATION.md) |
| I-003 | umbrella | Verify integrated revisions | I-001, I-002 | — | Done | This umbrella checkpoint | 2026-09-23: Images 3633865 / Files 05fa9f7 / Viewer 6f9c048 canonical and clean; unchanged product sources preserve measured acceptance. Provider build/CTest 2/2, Files task check and CTest 25/25, Viewer build/CTest 22/22, task test:installer 16/16; 20 pairs, 40 startups, 72 comparisons and user walkthrough passed. Commands, exact revisions, compatible evidence reuse and deferrals: [acceptance](SINGLE-MONITOR.md) |

I-001/I-002 record locally verified, published consumer commits. Final I-003 acceptance and this umbrella checkpoint mark the initiative Integrated.

## Historical publication and pin checkpoint — 2026-09-23

Both commits were pushed once to their canonical origin/main branches; push results and clean tracking state confirmed availability before pinning. Images remains at `3633865d2f39e4f163f0159a0f252f88245379f0`. Consumer code is the locally verified implementation; only documentation was updated for publication authorization. Documentation links and staged diffs pass review.

Latest available CI was checked once after publication; no wait or polling:

| Repository | Revision | Run | Status | Conclusion |
|---|---|---|---|---|
| Files | e8efed169bcea51c1ebdc846525a50331a2e298d | [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/35869945371) | in_progress | None yet |
| Viewer | 6ed3a3aa471b5c7c585c40f495b2849d83679f2c | [Build and checks](https://github.com/lebedenko/holonight-viewer/actions/runs/35869953629) | in_progress | None yet |

At that historical checkpoint, the umbrella checkpoint remained local. Sharp-preview T5, mixed-monitor qualification and other deferred native gates were open then; that checkpoint did not claim umbrella integration acceptance.

## Current qualification continuation — 2026-09-23

The umbrella is now synchronized with canonical main; Viewer subsequently advanced
to `266deb99955286e19cc98f0bb6d11fdd082e0af9` for formatter discovery.
The historical implementation handoff and CI observations above remain unchanged.
The qualification was initially kept local as requested. The subsequent **“publish
and pin”** request authorized the final handoff. Automated integration, the amended
1/1.25/1.6/2 matrix, original-scale restoration and the user walkthrough passed.
Physical second-monitor testing remains deferred, not passed.

## Final integration and pin checkpoint — 2026-09-23

Files and Viewer were committed and pushed separately to canonical `origin/main`.
`git ls-remote origin refs/heads/main` confirms the exact revisions below (and
unchanged Images `3633865d2f39e4f163f0159a0f252f88245379f0`); all participating
submodules are clean. Files changes only qualification tooling/tests and records;
Viewer changes only records. Product/provider source equality preserves the frozen
native matrix and compatible clean-build/isolated-runtime evidence. Files additionally
passed full `CMAKE_BUILD_PARALLEL_LEVEL=4 task check` before publication.
See [commands, results and remaining deferrals](SINGLE-MONITOR.md).

Latest available CI was queried once per new revision with `gh run list --commit
<revision> --limit 1`; these are publication snapshots, not passing CI claims.
No waiting or polling was performed; pending hosted CI does not block authorized pins.

| Repository | Published and pinned revision | Run | Status | Conclusion |
|---|---|---|---|---|
| Files | 05fa9f74965fc82d98610a4777ce7a527a941075 | [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/35898447985) | in_progress | None yet |
| Viewer | 6f9c048e2f936bc93e017a89cd18fb032159d603 | [Build and checks](https://github.com/lebedenko/holonight-viewer/actions/runs/35898076747) | in_progress | None yet |

This checkpoint updates the authoritative gitlinks, marks I-003 Done and the
initiative Integrated. Second-monitor, clipboard-service, unrelated release and
unknown-dimension fixture deferrals remain explicit; they are not passed.
