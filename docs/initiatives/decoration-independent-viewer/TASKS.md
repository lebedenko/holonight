# Decoration-independent Viewer — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | holonight-viewer | Fullscreen-only heading and accurate native titles | — | [SDD](../../../holonight-viewer/docs/sdd/decoration-independent-viewer/README.md) | Done | `e2670ec2359f6b818a811cb8a93466ac1995b4e1` (local) | 2026-10-08: task check and all 27 tests passed; native checks passed by user confirmation. |
| I-002 | holonight-qt | Remove decoration helpers and dependencies | I-001 | [SDD](../../../holonight-qt/docs/sdd/decoration-independent-viewer/README.md) | Done | `6c7ac33004702e166b8c152dcde918296be54286` (local) | 2026-10-08: clean ON/OFF builds; 95/86 checks covered with affected input retests passing; package/QML/format/REUSE and focused lint passed. |
| I-003 | holonight-system-services | Remove decoration contract; preserve compositor behavior | I-002 | [SDD](../../../holonight-system-services/docs/sdd/decoration-independent-viewer/README.md) | Done | `39472e6dcafc93acea218a234213c346be256586` (local) | 2026-10-08: enabled 6/6 and disabled 2/2 suites, install consumers and focused lint/format passed; unrelated AudioBackend global format blocker retained. |
| I-004 | holonight-shell | Compositor adapter and plugin ABI 3 | I-003 | [SDD](../../../holonight-shell/docs/sdd/decoration-independent-viewer/README.md) | Done | `54ce600afd0d0c120e92b8b6e099c059344a0013` (local) | 2026-10-08: clean staged-provider build; 1156-check suite covered with private-bus execution and corrected uqc_launch retest (124.01 s); plugin rejection, architecture, QML/package, focused lint/format and REUSE passed. Unrelated edits preserved. |
| I-005 | umbrella | Verify published integrated revisions and native ecosystem | I-001–I-004 | — | Planned | — | Publication and pinning pending; final umbrella integration review not run |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in the final umbrella row before setting the initiative status to `Integrated`.

Native Viewer checks passed by user confirmation on 2026-10-08. No publication, deployment, CI polling or gitlink changes occurred. Final umbrella integration remains Planned until published and pinned revisions can be reviewed.
