# Shared thumbnail disk cache — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| THC-001 | holonight-thumbnails | Shared package and cache contract | — | [SDD](../../../holonight-thumbnails/docs/sdd/shared-thumbnail-cache/README.md) | Done | `d27addc044f277686850588147ec825c40c0f252` (published) | 2026-09-29: fresh Release build, cache and installed-package CTest 2/2, REUSE lint; clean working tree and canonical `origin/main` confirmed |
| THC-002 | holonight-files | Shared disk-cache adoption | THC-001 | [SDD](../../../holonight-files/docs/sdd/shared-thumbnail-cache/README.md) | Done | `dd31d10f2e81ab3dd540fd06ce93ed21870cc39d` (published; implementation `f1dd8c696fa4869c76900891a9788a92d77a9ce9`) | 2026-09-29: baseline `dfacb4fb07cd68a8c847193599bf208ee21672b8`, provider `d27addc044f277686850588147ec825c40c0f252`; focused 55 tests, full CTest 27/27, lint/format/REUSE/install/QML and isolated runtime passed. CI-only follow-up aligned all five provider refs and checkout paths; YAML/API/ref checks and `task deps` passed. Canonical `origin/main` and clean checkout confirmed |
| THC-003 | holonight-viewer | Shared disk-cache adoption | THC-001 | [SDD](../../../holonight-viewer/docs/sdd/shared-thumbnail-cache/SPEC.md) | Done | `577aa107ebf0a4a2de5e3eef7987522b342f3941` (published; implementation `5d812e9f7087a4beacaea5a8d2ab4ddc962d35f9`) | 2026-09-29: baseline `61a69092cb6ef0db592aff9ffacfba504f0fa9a1`, provider `d27addc044f277686850588147ec825c40c0f252`; 25/25 CTest, focused 45 thumbnail tests, builds, format/QML/REUSE/tidy, staged install and isolated runtime passed. CI-only follow-up aligned four provider refs/checkouts and measurement provenance; YAML/ref checks, `task deps`, five measurement tests and REUSE passed. Canonical `origin/main` and clean checkout confirmed |
| THC-004 | umbrella | Verify published integrated revisions and native behavior | THC-001–THC-003 | This initiative | In Progress | — | 2026-09-29: exact published pins clean; provider Release build and CTest 2/2, Viewer Release build and CTest 25/25, Files Release build and CTest 27/27, `task test:installer` 28/28, `task license-check`, and `scripts/install.sh --check` passed. User-operated native check pending; hosted build failures under investigation. |

Allowed states: `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`.

Repository work marked `Done` means local verification passed. Only the final umbrella row may change the initiative status to `Integrated` after published pins, exact-revision checks, and manual acceptance.

## Published CI snapshot — 2026-09-29

This is one snapshot of the latest available runs at the pinned revisions; no CI completion is inferred from other revisions.

| Repository | Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|---|
| holonight-thumbnails | `d27addc044f277686850588147ec825c40c0f252` | — | No run available | — | — |
| holonight-viewer | `5d812e9f7087a4beacaea5a8d2ab4ddc962d35f9` | Build and checks | completed | failure | [Run](https://github.com/lebedenko/holonight-viewer/actions/runs/36614565141) |
| holonight-viewer | `5d812e9f7087a4beacaea5a8d2ab4ddc962d35f9` | Licensing | completed | success | [Run](https://github.com/lebedenko/holonight-viewer/actions/runs/36614565506) |
| holonight-files | `f1dd8c696fa4869c76900891a9788a92d77a9ce9` | Build and checks | completed | failure | [Run](https://github.com/lebedenko/holonight-files/actions/runs/36615845295) |
| holonight-files | `f1dd8c696fa4869c76900891a9788a92d77a9ce9` | Licensing | completed | success | [Run](https://github.com/lebedenko/holonight-files/actions/runs/36615845211) |
