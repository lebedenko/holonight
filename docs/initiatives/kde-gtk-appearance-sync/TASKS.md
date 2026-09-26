# KDE and GTK appearance synchronization — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| KGS-001 | `holonight-appearance-adapters` | KDE output and canonical drift status | — | [Adapter SDD](../../../holonight-appearance-adapters/docs/sdd/kde-gtk-appearance-sync/README.md) | Done | `90ea9f3` implementation, `0fcf79c` docs | 2026-09-26: build and 6/6 CTests; KF6 disabled build and unavailable status; format check, tidy, REUSE lint; published and pinned in `7d149d6` |
| KGS-002 | `holonight-settings` | Canonical status path | KGS-001 | [Settings SDD](../../../holonight-settings/docs/sdd/kde-gtk-appearance-sync/README.md) | Done | `dbc7635` implementation, `e603d43` docs | 2026-09-26: focused client/coordinator tests 10/10; `task test` 54/54, `task format-check`, `task tidy`, `task qml-lint`, `task qmltypes-check`, `task qml-import-check`, REUSE lint; published and pinned in `fb0798d` |
| KGS-003 | `holonight-shell` | Bounded login apply | KGS-001 | [Session SDD](../../../holonight-shell/docs/sdd/kde-gtk-appearance-sync/README.md) | Done | `e53e44f` implementation, `d079259` docs | 2026-09-26: focused session script test; `task test` 1170/1170; `bash -n`; REUSE lint; published and pinned in `1d0b2ae` |
| KGS-004 | `holonight-icons` | GTK symbolic verification for installed icon variants | — | [Icon verification](../../../holonight-icons/docs/sdd/icon-theme-compliance/VERIFICATION.md) | Done | `2454966` verification, `23b3cf2` correction | 2026-09-26: 41 Python tests, Qt render check, 400 GTK 3/4 headless Wayland render cases, previews, REUSE lint; exact Xvfb wrapper CI-only; published and pinned in `a93a52d` |
| KGS-005 | umbrella | Verify integrated revisions and native applications | KGS-001–KGS-004 | — | In Progress | — | 2026-09-26: exact published pins confirmed; repository acceptance in rows above, root `task test:installer` 27/27 and REUSE lint passed. Native Dolphin plus GTK 3/4 checks pending |

## CI snapshot on 2026-09-26

| Repository | Revision | Workflow | Status | Conclusion |
|---|---|---|---|---|
| `holonight-appearance-adapters` | `0fcf79c` | [CI](https://github.com/lebedenko/holonight-appearance-adapters/actions/runs/36270535364) | In progress | — |
| `holonight-settings` | `e603d43` | [CI](https://github.com/lebedenko/holonight-settings/actions/runs/36270565996) | In progress | — |
| `holonight-shell` | `d079259` | [CI](https://github.com/lebedenko/holonight-shell/actions/runs/36270566954) | In progress | — |
| `holonight-icons` | `23b3cf2` | [Theme verification](https://github.com/lebedenko/holonight-icons/actions/runs/36270882475) | Queued | — |

The earlier icons [run at `2454966`](https://github.com/lebedenko/holonight-icons/actions/runs/36246978976) failed its new GTK 3 color threshold; `23b3cf2` corrects that assertion. The latest available run above was checked once after publication, without waiting for completion.

Allowed states: `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`.

`Done` on a repository task means its handoff passed local verification. It does not mark the initiative integrated. Record final native commands, results, and verification date in KGS-005 before changing the initiative status.
