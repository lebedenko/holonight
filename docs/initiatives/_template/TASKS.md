# <Initiative Name> — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | `<provider>` | `<shared deliverable>` | — | Pending | Ready | — | — |
| I-002 | `<consumer>` | `<adoption deliverable>` | I-001 | Pending | Planned | — | — |
| I-003 | umbrella | Verify integrated revisions | I-001–I-002 | — | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in the final umbrella row before setting the initiative status to `Integrated`.
