# Unified Qt Quick Controls and Third-Party Compatibility — Coordination Ledger

The initiative is Draft. `UQC-001` is discovery only; no product implementation is authorized by its Ready state.
Before assignment, record the exact published upstream baseline in the repository-local SDD and handoff. All product
implementation packages remain Planned until the acceptance gate and their dependencies are complete.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| UQC-001 | `holonight-qt` | Audit runtime selection, composite dependencies, style-specific properties, and third-party control coverage; specify required additions and verification | — | Pending | Ready | — | Initial installed-app survey is recorded in README; rendering and compatibility remain unverified |
| UQC-002 | umbrella | Accept shared contracts, target-app coverage, dependency order, integration gates, and published assignment baselines | UQC-001 | This initiative | Planned | — | — |
| UQC-101 | `holonight-qt` | Implement accepted coverage and composite migration; provide policy checks, embedded-config example, installed-consumer tests, and aligned documentation | UQC-002 | Pending | Planned | — | — |
| UQC-102 | `holonight-shell` | Migrate shell/authentication; verify activation propagation and distinguish configured selection from module loading in diagnostics | UQC-101 | Pending | Planned | — | — |
| UQC-103 | `holonight-settings` | Adopt namespaced runtime controls and embedded default; align instructions and contradictory contract tests | UQC-101 | Pending | Planned | — | — |
| UQC-104 | `holonight-ai` | Adopt runtime controls and embedded default; align import checker and verify composite behavior | UQC-101 | Pending | Planned | — | — |
| UQC-105 | `holonight-pkg-manager` | Adopt runtime controls and embedded default; verify independent launch and scrollbar behavior | UQC-101 | Pending | Planned | — | — |
| UQC-106 | `holonight-greeter` | Adopt runtime controls and embedded default; verify pre-session startup and retain scaled ComboBox geometry | UQC-101 | Pending | Planned | — | — |
| UQC-201 | umbrella | Verify published clean pins, dependency-order checks, activation paths, and accepted third-party matrix under Hyprland and Sway | UQC-101–UQC-106 | This initiative | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies or acceptance are not ready.
- `Ready`: may be assigned with an exact published baseline and repository-local requirements.
- `In Progress`: repository work has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Confirm each implementation commit
is available from the canonical remote before updating its gitlink. Make umbrella checkpoint commits after accepted
handoffs; implementers do not modify umbrella status or pointers.

Record commands, results, application and Qt versions, limitations, and the verification date in `UQC-201` before
marking it Done and setting the initiative status to Integrated. Historical survey observations do not satisfy that
final verification gate.
