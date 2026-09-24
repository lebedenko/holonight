# Shared SVG support — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| SVG-001 | holonight-images | Bounded SVG mechanics and package contract | — | [Tasks](../../../holonight-images/docs/sdd/shared-svg-support/TASKS.md) | Done | `3da5f4e51fe2eed9a1bd9f72c0ab523aa57a5ceb` | 2026-09-24: 36 raster/SVG tests, installed package and no-SVG-plugin test passed; clean Release build and affected correction checks passed. [Evidence](../../../holonight-images/docs/sdd/shared-svg-support/VERIFICATION.md). Published to canonical origin/main and pinned with user authorization |
| SVG-002 | holonight-viewer | Adopt provider, retain local-image fallback | SVG-001 published and pinned | [Tasks](../../../holonight-viewer/docs/sdd/shared-svg-support/TASKS.md) | Ready | — | Provider published and pinned; baseline and local SDD unchanged |
| SVG-003 | holonight-files | Sharp static SVG previews and policy-aware caching | SVG-001 published and pinned | [Tasks](../../../holonight-files/docs/sdd/shared-svg-support/TASKS.md) | Ready | — | Provider published and pinned; baseline and local SDD unchanged |
| SVG-004 | umbrella | Verify integrated exact revisions | SVG-001–SVG-003 | — | Planned | — | Builds/tests, compatibility and manual ecosystem checks pending |

Allowed states: Planned, Ready, In Progress, Done, Blocked, Superseded.
Done is a locally verified commit, not an integrated initiative. Publication and pins require authorization.
Record integration commands, results and date in SVG-004 before setting the initiative Integrated.

## Local checkpoint, 2026-09-24

- holonight-viewer: `78fc05e862cd0128df03a8536bcad2f64c21a164` contains only the local SDD; implementation remains Planned.
- holonight-files: `0efb2dcb75af4c37321567964798d505e8039e6d` contains only the local SDD; implementation remains Planned.
- Umbrella pin values are unchanged. No commits have been pushed and no hosted CI run is claimed.
- Documentation links, whitespace and REUSE checks passed. Consumer acceptance and manual checks have not run.

## Provider handoff, 2026-09-24

User authorized Images publication and pin. Canonical origin/main confirmed at `3da5f4e51fe2eed9a1bd9f72c0ab523aa57a5ceb`.
Latest CI checked once: revision `3da5f4e51fe2eed9a1bd9f72c0ab523aa57a5ceb`, status `in_progress`, conclusion empty,
[run 35990862274](https://github.com/lebedenko/holonight-images/actions/runs/35990862274). No CI completion claimed.
Consumer implementation is now Ready; their publication remains a separate handoff.
