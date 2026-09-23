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

## Acceptance follow-up — 2026-09-23

Scoped user-approved continuation; existing I-003 and Integrated status remain intact.
Publication and gitlink updates were outside the initial acceptance scope; the
subsequent **“commit, publish, pin”** request authorizes the handoff below.
The accepted scale matrix is not repeated.
The provider API, decoding policy and limits are unchanged. Baselines were clean:
Files `05fa9f74965fc82d98610a4777ce7a527a941075`, Viewer
`6f9c048e2f936bc93e017a89cd18fb032159d603`, Images
`3633865d2f39e4f163f0159a0f252f88245379f0`.
Both follow-ups were Ready after contract inspection, then taken by this implementer.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Verification |
|---|---|---|---|---|---|---|
| I-004 | holonight-files | Synthetic unknown-dimension rejection acceptance | Existing installed Images contract | [SDD](../../../holonight-files/docs/sdd/unknown-dimension-acceptance/SPEC.md) | Done | 2026-09-23: isolated 4/4, focused 98/98, all 26 CTest entries, task-check stages and fresh Release isolated target pass; [evidence](../../../holonight-files/docs/sdd/unknown-dimension-acceptance/VERIFICATION.md). Publication recorded in the follow-up checkpoint below |
| I-005 | holonight-viewer | Personal clipboard-service acceptance and passive measurements | Personal package/autostart, user interaction | [SDD](../../../holonight-viewer/docs/sdd/clipboard-persistence/SPEC.md) | Done | 2026-09-23: singleton desktop autostart, 8/8 orientation/alpha/dimension rows, exact paths, GIMP and five identical trials passed; user accepted costs. [Evidence](../../../holonight-viewer/docs/sdd/clipboard-persistence/VERIFICATION.md). Publication recorded in the follow-up checkpoint below |

Mixed-monitor and unrelated release gates remain deferred and non-blocking for
this scope. These rows close only after their own acceptance passes.

### CI conclusions observed 2026-09-23

Queried once using `gh run list --repo lebedenko/<repository> --commit <full-SHA>
--limit 10 --json headSha,url,status,conclusion,name`; no waiting or polling.
Earlier pending snapshots above remain historical. These conclusions apply only
to the specified published revisions, not the new local follow-up changes.

| Repository | Full revision | Run | Status | Conclusion |
|---|---|---|---|---|
| Images | 3633865d2f39e4f163f0159a0f252f88245379f0 | [Build and checks](https://github.com/lebedenko/holonight-images/actions/runs/35777273578) | completed | success |
| Files | 05fa9f74965fc82d98610a4777ce7a527a941075 | [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/35898447985) | completed | success |
| Files | 05fa9f74965fc82d98610a4777ce7a527a941075 | [Licensing](https://github.com/lebedenko/holonight-files/actions/runs/35898448021) | completed | success |
| Viewer | 6f9c048e2f936bc93e017a89cd18fb032159d603 | [Build and checks](https://github.com/lebedenko/holonight-viewer/actions/runs/35898076747) | completed | success |
| Viewer | 6f9c048e2f936bc93e017a89cd18fb032159d603 | [Licensing](https://github.com/lebedenko/holonight-viewer/actions/runs/35898076730) | completed | success |

### Scoped acceptance closure — 2026-09-23

I-004 and I-005 are Done locally. The unknown-dimension fixture and clipboard-service
deferrals are closed by their linked acceptance records. User explicitly accepted
measured service/receiver costs and reported both GIMP checks passed. Existing
Integrated status and single-monitor evidence remain intact. Physical mixed-monitor
qualification and unrelated release gates remain deferred, not passed. Changes were
initially retained locally for review. The subsequent user request
authorizes publication and pinning; the follow-up checkpoint below records it.

## Acceptance follow-up publication and pin checkpoint — 2026-09-23

The user authorized **“commit, publish, pin”** after both acceptance packages passed.
Files and Viewer were committed separately and pushed once each to canonical
`origin/main`. Successful pushes and `git ls-remote origin refs/heads/main`
confirm the exact revisions below before updating their gitlinks. Both consumer
working trees are clean; Images remains unchanged at
`3633865d2f39e4f163f0159a0f252f88245379f0`.

- Files `86e3f4a34a3b190f59d64f1c3e3a5584f98cd646` — `test: verify unknown-dimension image rejection`.
- Viewer `af57d28416d68ca695c3a2d9bc30bb3b341e7dd0` — `test: qualify desktop clipboard persistence`.

Prior complete local acceptance remains applicable: product and install payload
sources are unchanged, including provider contracts. Final isolated Files CTest
passes all four cases; Viewer validator passes eight cases; documentation links
and whitespace pass. Existing clean-build and isolated-runtime evidence is reused
as recorded in the local SDDs. No native matrix or unchanged application build was
repeated for this publication-only handoff. Personal configuration and generated
raw evidence remain outside the published source payload.

CI was queried once for each new full revision using `gh run list --commit
<revision> --limit 10 --json headSha,url,status,conclusion,name`. This is the
2026-09-23 observation, not a prediction of completion. No waiting or polling.

| Repository | Published and pinned revision | Run | Status | Conclusion |
|---|---|---|---|---|
| Files | 86e3f4a34a3b190f59d64f1c3e3a5584f98cd646 | [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/35911834807) | in_progress | None yet |
| Files | 86e3f4a34a3b190f59d64f1c3e3a5584f98cd646 | [Licensing](https://github.com/lebedenko/holonight-files/actions/runs/35911834851) | completed | success |
| Viewer | af57d28416d68ca695c3a2d9bc30bb3b341e7dd0 | [Licensing](https://github.com/lebedenko/holonight-viewer/actions/runs/35911839836) | completed | success |
| Viewer | af57d28416d68ca695c3a2d9bc30bb3b341e7dd0 | [Build and checks](https://github.com/lebedenko/holonight-viewer/actions/runs/35911839799) | in_progress | None yet |

This umbrella checkpoint publishes the authoritative pins and completed I-004/I-005
records. Existing Integrated status and prior single-monitor acceptance remain
intact. Physical mixed-monitor and unrelated release gates remain deferred.
