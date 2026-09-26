# KDE and GTK appearance synchronization — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| KGS-001 | `holonight-appearance-adapters` | KDE output and canonical drift status | — | [Adapter SDD](../../../holonight-appearance-adapters/docs/sdd/kde-gtk-appearance-sync/README.md) | Done | `90ea9f3` implementation, `0fcf79c` docs (local) | 2026-09-26: build and 6/6 CTests; KF6 disabled build and unavailable status; format check, tidy, REUSE lint |
| KGS-002 | `holonight-settings` | Canonical status path | KGS-001 | [Settings SDD](../../../holonight-settings/docs/sdd/kde-gtk-appearance-sync/README.md) | Done | `dbc7635` implementation, `e603d43` docs (local) | 2026-09-26: focused client/coordinator tests 10/10; `task test` 54/54, `task format-check`, `task tidy`, `task qml-lint`, `task qmltypes-check`, `task qml-import-check`, REUSE lint |
| KGS-003 | `holonight-shell` | Bounded login apply | KGS-001 | [Session SDD](../../../holonight-shell/docs/sdd/kde-gtk-appearance-sync/README.md) | Done | `e53e44f` implementation, `d079259` docs (local) | 2026-09-26: focused session script test; `task test` 1170/1170; `bash -n`; REUSE lint |
| KGS-004 | umbrella | Verify and pin integrated revisions | KGS-001–KGS-003 | — | Planned | — | Commits remain unpublished; pin and native Dolphin plus GTK 3/4 checks pending |

Allowed states: `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`.

`Done` on a repository task means a local handoff passed verification. It does not mark the initiative integrated. Record commands, results, and verification date in KGS-004 before changing the initiative status.
