# Installation completeness — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| IC-001 | holonight-ai | Launcher, identity and icon | — | [SPEC](../../../holonight-ai/docs/sdd/installation-completeness/SPEC.md) | Done | `777affc646b44bfb757bd2616f5cd7a218897cba` | Baseline dbf192c39ea11aeaf901c0597a2ad2e3e3a3f96a; clean Release/staged install and desktop-file validation passed on 2026-10-11; published to canonical main; user confirmed menu visibility on 2026-10-11 |
| IC-002 | holonight-pkg-manager | Launcher, identity and icon | — | [SPEC](../../../holonight-pkg-manager/docs/sdd/installation-completeness/SPEC.md) | Done | `68784033fb79e4ad98ce5b7864cc39ec3d7bb375` | Baseline 4a17121406822ca7087f817fa3ab4765d08af714; clean Release/staged install and desktop-file validation passed on 2026-10-11; published to canonical main; user confirmed menu visibility on 2026-10-11 |
| IC-003 | umbrella | Hyprlock sequence, ownership regression and documentation | — | This initiative | Done | `7dec1e3f778e3f5bbb833224a384a0ca5fc251db` | Hyprlock baseline def9618fca833535275e8a8aa9a0e577acda8377; 36 ownership and five module coverage/order tests, two Hyprlock package tests and alternate-root component deployment passed on 2026-10-11; task test:installer passed (63 tests) |
| IC-004 | umbrella | Publish handoff, explicit pin updates and integration review | IC-001–IC-003 | — | In Progress | — | Application commits published and menu visibility confirmed by user on 2026-10-11; pins updated to the verified canonical main revisions. Final ecosystem alternate-root installation remains pending |

States: Planned, Ready, In Progress, Done, Blocked, Superseded. Done requires a local commit and local verification;
only the final integration row permits Integrated status. Publication and pin updates remain explicit handoff steps.

Detailed commands, artifact provenance and handoff limits: [local acceptance](ACCEPTANCE.md).

Latest available CI checked once on 2026-10-11:

- AI revision `777affc646b44bfb757bd2616f5cd7a218897cba`: [Licensing](https://github.com/lebedenko/holonight-ai/actions/runs/38134926864), `in_progress`, no conclusion yet.
- Packages revision `68784033fb79e4ad98ce5b7864cc39ec3d7bb375`: [CI](https://github.com/lebedenko/holonight-pkg-manager/actions/runs/38134929225), `queued`, no conclusion yet.
