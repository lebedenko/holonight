# Shared HoloNight search engine — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| S-001 | `holonight-search` | Installed search engine and performance evidence | — | [SDD](../../../holonight-search/docs/sdd/shared-search-engine/README.md) | Done | `d12e441` | 2026-09-30: Release CTest (6 tests), installed consumer, REUSE, two-million-path benchmark passed; canonical `main` verified at this revision. Latest CI query returned no runs. |
| S-002 | `holonight-files` | Replace prototype ranking, retain finder UI | S-001 | [SDD](../../../holonight-files/docs/sdd/shared-search-adoption/README.md) | Ready | — | Provider published and pinned; Files implementation may start after this checkpoint. |
| S-003 | umbrella | Review pinned revisions and integration | S-001, S-002 | — | Planned | — | Pending |

`Done` records a locally verified repository commit. The initiative becomes `Integrated` only after the final umbrella row records integration checks and the required native result.
