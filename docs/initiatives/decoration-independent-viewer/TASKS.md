# Decoration-independent Viewer — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | holonight-viewer | Fullscreen-only heading and accurate native titles | — | [SDD](../../../holonight-viewer/docs/sdd/decoration-independent-viewer/README.md) | Ready | — | Baseline `c79bb8eff4199b6d7504adb4526672a3274d5652` |
| I-002 | holonight-qt | Remove decoration helpers and dependencies | I-001 | [SDD](../../../holonight-qt/docs/sdd/decoration-independent-viewer/README.md) | Ready | — | Baseline `8eadfa36396315da56d734a83b2145b6d71d51cc` |
| I-003 | holonight-system-services | Remove decoration contract; preserve compositor behavior | I-002 | [SDD](../../../holonight-system-services/docs/sdd/decoration-independent-viewer/README.md) | Ready | — | Baseline `398804a7cce5a57f9f6870c4e7ec99e9b1f3ddaa` |
| I-004 | holonight-shell | Compositor adapter and plugin ABI 3 | I-003 | [SDD](../../../holonight-shell/docs/sdd/decoration-independent-viewer/README.md) | Ready | — | Baseline `e490ff73f3da4b3a671aaf0496c8dbdc94a53ff8` |
| I-005 | umbrella | Verify published integrated revisions and native ecosystem | I-001–I-004 | — | Planned | — | Publication, pinning and manual checks pending |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in the final umbrella row before setting the initiative status to `Integrated`.
