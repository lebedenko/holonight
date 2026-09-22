# Shared image architecture — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| IMG-001 | holonight-images | Provider and installed package | — | ../../../holonight-images/docs/sdd/shared-image-architecture/ | Done | efe3e780327fa793fb76c82b18fddde15298120b (published) | Clean Release, 2/2 CTest, installed consumer, format and REUSE passed 2026-09-22 |
| IMG-002 | holonight-viewer | Raster and EXIF migration | IMG-001 | ../../../holonight-viewer/docs/sdd/shared-image-architecture/ | Done | 149b86a908689477d1ba0cb4e7d486d091bf1024 (published; baseline 08d504f7930e6e358f7c24c3d933115452018c44) | Clean Release; CTest 21/21, final smoke 182 passed/7 existing skips; format, tidy rechecks, QML/license/install checks and isolated runtime passed 2026-09-22 |
| IMG-003 | holonight-files | Verified-device migration | IMG-001 | ../../../holonight-files/docs/sdd/shared-image-architecture/ | Done | 152cb98078e973fce74e020fd0e3b63bb4b5f046 (published; baseline dc340ea1767c642844e2ffb4faba875b2056ad38) | Clean Release; all 22 CTest entries verified including repaired provider fixture; final affected 26/26; format, tidy rechecks, QML/license/install checks and isolated runtime passed 2026-09-22 |
| IMG-004 | umbrella | Published/pinned integration review | IMG-001–IMG-003 | — | Planned | — | Published and pinned; final integration review and manual checks pending |

## Publication and pinning — 2026-09-22

All three implementation commits were pushed to their canonical GitHub `origin/main` branches and confirmed
with `git ls-remote`. The umbrella registers `holonight-images` and pins both consumers to the published commits
above. The installer builds the images provider before Viewer and Files. `bash -n scripts/install.sh` and
`python3 -m unittest discover -s tests -p 'test_install*.py' -v` passed (16 tests).

CI was checked once at approximately 15:01 UTC; these are snapshots, not a claim about later status.

| Repository | Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|---|
| holonight-images | `efe3e780327fa793fb76c82b18fddde15298120b` | Build and checks | `completed` | `success` | [GitHub Actions](https://github.com/lebedenko/holonight-images/actions/runs/35744067722) |
| holonight-viewer | `149b86a908689477d1ba0cb4e7d486d091bf1024` | Build and checks | `in_progress` | `pending` | [GitHub Actions](https://github.com/lebedenko/holonight-viewer/actions/runs/35744065695) |
| holonight-viewer | `149b86a908689477d1ba0cb4e7d486d091bf1024` | Licensing | `completed` | `success` | [GitHub Actions](https://github.com/lebedenko/holonight-viewer/actions/runs/35744065714) |
| holonight-files | `152cb98078e973fce74e020fd0e3b63bb4b5f046` | Licensing | `completed` | `success` | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35744069727) |
| holonight-files | `152cb98078e973fce74e020fd0e3b63bb4b5f046` | Build and checks | `completed` | `failure` | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35744069731) |

Files' build workflow failed before building: the container rejected `/work/holonight-config` with Git's
“dubious ownership” check during `task deps`. This was diagnosed from the failed run log; no polling or CI
repair push was performed as part of publication/pinning. Viewer build CI was still running when checked.

Files retains the pre-existing untracked `tests/provider_revisions_test.sh`; it is not in the published commit.
Detailed local acceptance evidence remains in each repository's SDD (its publication-pending notes describe
the pre-publication handoff).

Final IMG-004 verification remains pending: review CI, run pinned-revision ecosystem integration and manual native
Viewer navigation, SVG/animation/clipboard and Files preview checks. The initiative remains Accepted.
