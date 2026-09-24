# Shared SVG support — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SVG-001 | holonight-images | Bounded SVG mechanics and package contract | — | [Tasks](../../../holonight-images/docs/sdd/shared-svg-support/TASKS.md) | Done | `3da5f4e51fe2eed9a1bd9f72c0ab523aa57a5ceb` | 2026-09-24: 36 raster/SVG tests, installed package and no-SVG-plugin test passed; clean Release build and affected correction checks passed. [Evidence](../../../holonight-images/docs/sdd/shared-svg-support/VERIFICATION.md). Published to canonical origin/main and pinned with user authorization |
| SVG-002 | holonight-viewer | Adopt provider, retain local-image fallback | SVG-001 published and pinned | [Tasks](../../../holonight-viewer/docs/sdd/shared-svg-support/TASKS.md) | In Progress | `3b25553053602138b8a5064f31f406ed17559dbe` (local) | 2026-09-24: focused regressions, CTest 24/24, full task check, clean Release and isolated installed-runtime checks passed. [Evidence](../../../holonight-viewer/docs/sdd/shared-svg-support/VERIFICATION.md). Native visual report pending |
| SVG-003 | holonight-files | Sharp static SVG previews and policy-aware caching | SVG-001 published and pinned | [Tasks](../../../holonight-files/docs/sdd/shared-svg-support/TASKS.md) | In Progress | `1ec432bc75531bfa0595bba493952c3346229376` (local) | 2026-09-24: focused regressions, CTest 27/27, full task check, clean Release and isolated installed-runtime checks passed. [Evidence](../../../holonight-files/docs/sdd/shared-svg-support/VERIFICATION.md). Native visual report pending |
| SVG-004 | umbrella | Verify integrated exact revisions | SVG-001–SVG-003 | — | Planned | — | Builds/tests, compatibility and manual ecosystem checks pending |

Allowed states: Planned, Ready, In Progress, Done, Blocked, Superseded.
Done is a locally verified commit, not an integrated initiative. Publication and pins require authorization.
Record integration commands, results and date in SVG-004 before setting the initiative Integrated.

## Initial documentation checkpoint, 2026-09-24

- holonight-viewer: `78fc05e862cd0128df03a8536bcad2f64c21a164` contains only the local SDD; implementation remains Planned.
- holonight-files: `0efb2dcb75af4c37321567964798d505e8039e6d` contains only the local SDD; implementation remains Planned.
- Umbrella pin values are unchanged. No commits have been pushed and no hosted CI run is claimed.
- Documentation links, whitespace and REUSE checks passed. Consumer acceptance and manual checks have not run.

## Provider handoff, 2026-09-24

User authorized Images publication and pin. Canonical origin/main confirmed at `3da5f4e51fe2eed9a1bd9f72c0ab523aa57a5ceb`.
Latest CI checked once: revision `3da5f4e51fe2eed9a1bd9f72c0ab523aa57a5ceb`, status `in_progress`, conclusion empty,
[run 35990862274](https://github.com/lebedenko/holonight-images/actions/runs/35990862274). No CI completion claimed.
This handoff made consumer implementation Ready; their publication remains a separate handoff.

## Consumer implementation checkpoint, 2026-09-24

Both consumers are implemented in separate local commits and have clean working trees. Automated acceptance used
the published/pinned Images provider and the current pinned Qt/Config providers. Complete evidence is in each local
SDD. Initial sandbox failures were private-socket/D-Bus/OpenGL restrictions; authorized outside-sandbox acceptance
passed. Clean Release logs contain no compiler warnings; complete task-check logs contain no actionable diagnostics.

The user has agreed to check native Files preview/Quick Look resizing and Viewer zoom/navigation and report results.
That report is pending. SVG-002/SVG-003 remain In Progress until native acceptance is recorded. Consumer publication
and gitlink updates are not yet authorized; current consumer pins are unchanged. No umbrella integration checks
have run and the initiative remains Accepted. Local manual fixtures are under `build/shared-svg-manual/`.
