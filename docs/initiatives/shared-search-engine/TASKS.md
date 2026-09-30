# Shared HoloNight search engine — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| S-001 | `holonight-search` | Installed search engine and performance evidence | — | [SDD](../../../holonight-search/docs/sdd/shared-search-engine/README.md) | Done | `d12e441` | 2026-09-30: Release CTest (6 tests), installed consumer, REUSE, two-million-path benchmark passed; canonical `main` verified at this revision. Latest CI query returned no runs. |
| S-002 | `holonight-files` | Replace prototype ranking, retain finder UI | S-001 | [SDD](../../../holonight-files/docs/sdd/shared-search-adoption/README.md) | Done | `51cef84` | 2026-09-30: published on canonical `main` and pinned; 12 focused finder tests, Release build, formatting and focused tidy passed. User confirmed shortcuts, roots, hidden toggle, both term orders, responsiveness, navigation, and scan reuse. [Files CI success](https://github.com/lebedenko/holonight-files/actions/runs/36772717041) at this revision; a [second run](https://github.com/lebedenko/holonight-files/actions/runs/36772716867) was still in progress at the single check. |
| S-003 | umbrella | Review pinned revisions and integration | S-001, S-002 | — | In Progress | — | 2026-09-30: provider Release CTest 6/6, installed consumer, Files focused tests 12/12, provider revision check, and umbrella REUSE passed. Final publication and pin review pending. |

`Done` records a locally verified repository commit. The initiative becomes `Integrated` only after the final umbrella row records integration checks and the required native result.
