# Icons infrastructure integration — Coordination ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| III-001 | holonight-icons | Validated system staging and documentation | — | [SDD](../../../holonight-icons/docs/sdd/umbrella-packaging/README.md) | Ready | — | Baseline 7342a0947b960191b3e0c32cfd4f4c49ad2e973f |
| III-002 | umbrella | Installation lifecycle, tasks and CI adoption | III-001 | — | Planned | — | Awaiting published provider |
| III-003 | umbrella | Verify integrated published revisions | III-001, III-002 | — | Planned | — | — |

Baseline review (2026-09-24): 33 icons tests, 16 installer tests, source/theme validation, source REUSE,
and offscreen rendering passed. Review found obsolete source-copy staging, missing dark-theme/cache/bundle
integration, missing upgrade cleanup, and stale Places documentation. Current Qt renderer baseline is
863af4183bdf09ce05199b37e8f5dfb46a311ba1. These baseline results are not final acceptance evidence.
