# Shared HoloNight search engine — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| S-001 | `holonight-search` | Installed search engine and performance evidence | — | [SDD](../../../holonight-search/docs/sdd/shared-search-engine/README.md) | Done | `d12e441` | 2026-09-30: Release CTest (6 tests), installed consumer, REUSE, two-million-path benchmark passed; canonical `main` verified at this revision. Latest CI query returned no runs. |
| S-002 | `holonight-files` | Replace prototype ranking, retain finder UI | S-001 | [SDD](../../../holonight-files/docs/sdd/shared-search-adoption/README.md) | Done | `7593bd3` | 2026-09-30: implementation `51cef84` and documentation closure `7593bd3` published on canonical `main`. Twelve focused finder tests, Release build, formatting, and focused tidy passed. User confirmed shortcuts, roots, hidden toggle, both term orders, responsiveness, navigation, and scan reuse. At the single latest CI check, [one run succeeded](https://github.com/lebedenko/holonight-files/actions/runs/36774136288) at `7593bd3` and [another was in progress](https://github.com/lebedenko/holonight-files/actions/runs/36774136325). |
| S-003 | umbrella | Review pinned revisions and integration | S-001, S-002 | — | Done | `d12e441` + `7593bd3` | 2026-09-30: canonical remotes and clean submodule trees verified at both pinned revisions. Provider `ctest --test-dir build/release --output-on-failure` passed 6/6 and installed `search-consumer` ran; Files `files-smoke --gtest_filter='PathFinderModel.*'` passed 12/12 and `bash tests/shared_provider_revisions_test.sh .` passed. The previously verified Release Files build and two-million-path benchmark use unchanged implementation code at these pins. `task license-check` passed for the umbrella and submodules. The user completed the native finder check at the same Files implementation revision. |

## Reopened adjustment cycle — 2026-10-02

The user reported that Shared Search needs adjustments and cannot yet be considered Integrated.
S-001–S-003 retain the historical 2026-09-30 delivery evidence; they do not accept the pending adjustments.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| S-004 | umbrella | Specify reported behavior, expected results, owning repositories, exact baselines and adjustment work packages | Approved exclusion/reload plan | Files exclusion SDD below | Done | This checkpoint | 2026-10-02: approved Files-only exclusion/reload scope; exact Files baseline `2b8da3fccc0829a2b9c33b79e56304e9861f7b97`; provider unchanged |
| S-005 | umbrella | Verify corrected published revisions and native finder behavior | S-004, S-006 | — | Planned | — | Pending baseline lint resolution, authorized publication/pinning and corrected-revision integration |
| S-006 | `holonight-files` | Search indexing exclusions, search config reload, diagnostics and cache invalidation | S-004; unchanged pinned provider | [SDD](../../../holonight-files/docs/sdd/search-index-exclusions/README.md) | In Progress | `823a9216d7e6e7835e5b543b6ca491452a64e3ba` (local) | Baseline `2b8da3fccc0829a2b9c33b79e56304e9861f7b97`; 38 focused tests, 27 CTest entries, changed-file tidy, remaining checks and isolated runtime passed; user native acceptance confirmed 2026-10-02. Full task check blocked by baseline tidy errors; committed locally/unpublished; no pin authorization |

`Done` records a locally verified repository commit. The initiative becomes `Integrated` only after S-005 records integration checks and the required native result for the adjusted delivery.
