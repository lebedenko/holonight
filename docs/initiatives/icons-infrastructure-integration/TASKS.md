# Icons infrastructure integration — Coordination ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| III-001 | holonight-icons | Validated system staging and documentation | — | [SDD](../../../holonight-icons/docs/sdd/umbrella-packaging/README.md) | Done | 5eb892baa242e216121f28ff2b68b23ee03e833e | Clean task verify: 39 tests, rendering, previews, four REUSE checks; published origin/main confirmed with ls-remote |
| III-002 | umbrella | Installation lifecycle, tasks and CI adoption | III-001 | — | Ready | — | Provider published and pinned |
| III-003 | umbrella | Verify integrated published revisions | III-001, III-002 | — | Planned | — | — |

Baseline review (2026-09-24): 33 icons tests, 16 installer tests, source/theme validation, source REUSE,
and offscreen rendering passed. Review found obsolete source-copy staging, missing dark-theme/cache/bundle
integration, missing upgrade cleanup, and stale Places documentation. Current Qt renderer baseline is
863af4183bdf09ce05199b37e8f5dfb46a311ba1. These baseline results are not final acceptance evidence.
