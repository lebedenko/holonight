# Shared thumbnail disk cache — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| THC-001 | holonight-thumbnails | Shared package and cache contract | — | [SDD](../../../holonight-thumbnails/docs/sdd/shared-thumbnail-cache/README.md) | Done | `d27addc044f277686850588147ec825c40c0f252` (published) | 2026-09-29: fresh Release build, cache and installed-package CTest 2/2, REUSE lint; clean working tree and canonical `origin/main` confirmed |
| THC-002 | holonight-files | Shared disk-cache adoption | THC-001 | [SDD](../../../holonight-files/docs/sdd/shared-thumbnail-cache/README.md) | In Progress | — | Baseline: `dfacb4fb07cd68a8c847193599bf208ee21672b8`; provider: `d27addc044f277686850588147ec825c40c0f252` |
| THC-003 | holonight-viewer | Shared disk-cache adoption | THC-001 | [SDD](../../../holonight-viewer/docs/sdd/shared-thumbnail-cache/SPEC.md) | In Progress | — | Baseline: `61a69092cb6ef0db592aff9ffacfba504f0fa9a1`; provider: `d27addc044f277686850588147ec825c40c0f252` |
| THC-004 | umbrella | Publish and verify integrated revisions | THC-001–THC-003 | This initiative | Planned | — | — |

Allowed states: `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`.

Repository work marked `Done` means local verification passed. Only the final umbrella row may change the initiative status to `Integrated` after published pins, exact-revision checks, and manual acceptance.
