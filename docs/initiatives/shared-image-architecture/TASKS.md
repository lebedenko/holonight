# Shared image architecture — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| IMG-001 | holonight-images | Provider and installed package | — | ../../../holonight-images/docs/sdd/shared-image-architecture/ | Done | efe3e780327fa793fb76c82b18fddde15298120b (published) | Clean Release, 2/2 CTest, installed consumer, format and REUSE passed 2026-09-22 |
| IMG-002 | holonight-viewer | Raster and EXIF migration | IMG-001 | ../../../holonight-viewer/docs/sdd/shared-image-architecture/ | Done | 149b86a908689477d1ba0cb4e7d486d091bf1024 (published; baseline 08d504f7930e6e358f7c24c3d933115452018c44) | Clean Release; CTest 21/21, final smoke 182 passed/7 existing skips; format, tidy rechecks, QML/license/install checks and isolated runtime passed 2026-09-22 |
| IMG-003 | holonight-files | Verified-device migration | IMG-001 | ../../../holonight-files/docs/sdd/shared-image-architecture/ | Done | 152cb98078e973fce74e020fd0e3b63bb4b5f046 (published; baseline dc340ea1767c642844e2ffb4faba875b2056ad38) | Clean Release; all 22 CTest entries verified including repaired provider fixture; final affected 26/26; format, tidy rechecks, QML/license/install checks and isolated runtime passed 2026-09-22 |
| IMG-004 | umbrella | Published/pinned integration review | IMG-001–IMG-003 | — | Done | Umbrella closure commit containing this ledger; implementation pins unchanged | 2026-09-22: published pins and clean submodules confirmed; compatible acceptance builds checked with `cmake --build`; provider CTest 2/2, Viewer 21/21, Files 22/22, installer tests 16/16 passed; manual checks passed per user. Commands and CI caveat below. |

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

At publication, Files retained the pre-existing untracked `tests/provider_revisions_test.sh`; it is not in the published commit.
Detailed local acceptance evidence remains in each repository's SDD (its publication-pending notes describe
the pre-publication handoff).

## Final integration — 2026-09-22

IMG-004 is Done and the initiative is Integrated. The user confirmed the required manual checks were completed
with no issues observed, covering the initiative's Viewer navigation, SVG/animation/clipboard and Files previews.

### Revision and contract review

- `git submodule status holonight-images holonight-viewer holonight-files` matched the published implementation
  revisions above. `git -C <repository> ls-remote origin refs/heads/main` confirmed all three on their canonical
  remotes. `git -C <repository> status --porcelain` was empty for every participating submodule at closure.
- With user authorization, removed the obsolete untracked `holonight-files/tests/provider_revisions_test.sh`.
  It was an unused two-provider fixture, superseded by the tracked `shared_provider_revisions_test.sh` that CMake
  runs and that additionally verifies images-provider refresh. No tracked implementation or gitlink changed.
- Reviewed provider API and consumer calls: caller-owned devices, explicit limits, local workers/caches/formatting,
  startup allocation ceilings, Viewer default orientation and Files explicit Ignore remain compatible.
- Reused the documented clean acceptance builds (GCC 16.2.1, Qt 6.11.2, Release providers, BUILD_WAYLAND=OFF).
  Consumer CMake caches point to their local installed provider prefixes; the Files provider-revision ledger matches
  the umbrella pins for config, Qt and images. SHA-256 comparison of the provider acceptance archive and both
  installed consumer archives was identical. Existing clean/final build logs contained no compiler warnings/errors.

### Local verification

Commands were run from the umbrella root, checking the provider before its consumers. Existing clean builds and
isolated runtime acceptance recorded in the local SDDs remain valid; documentation closure did not repeat them.

| Command | Result |
|---|---|
| `ctest --test-dir holonight-images/build/acceptance --output-on-failure` | 2/2 passed, including installed-package consumer |
| `cmake --build holonight-images/build/acceptance --parallel 2` | Passed; fixture generation only |
| `cmake --build holonight-viewer/build/images-acceptance --parallel 2` | Passed; no work to do |
| `cmake --build holonight-files/build/images-acceptance --parallel 2` | Passed; no work to do |
| `QT_QPA_PLATFORM=offscreen ctest --test-dir holonight-viewer/build/test --output-on-failure` | 9/21 passed in sandbox; 12 blocked by private D-Bus socket restrictions |
| `QT_QPA_PLATFORM=offscreen ctest --test-dir holonight-viewer/build/test --rerun-failed --output-on-failure` (outside sandbox) | Remaining 12/12 passed; all 21 entries verified. Smoke: 182 passed, seven existing opt-in skips |
| `QT_QPA_PLATFORM=offscreen ctest --test-dir holonight-files/build/test --output-on-failure` | 15/22 passed in sandbox; seven failed due to socket/graphics restrictions |
| `QT_QPA_PLATFORM=offscreen ctest --test-dir holonight-files/build/test --rerun-failed --output-on-failure` (outside sandbox) | Remaining 7/7 passed; all 22 entries verified |
| `bash -n scripts/install.sh` | Passed |
| `python3 -m unittest discover -s tests -p 'test_install*.py' -v` | 16/16 passed |
| `git diff --check` and local Markdown link validation for the three changed documents | Passed |

### Final CI snapshot

Checked once during closure on 2026-09-22 using `gh run list --repo lebedenko/<repository> --commit <pinned-sha>
--limit 5 --json headSha,status,conclusion,url,name`; no live waiting or polling.

- Images `efe3e780327fa793fb76c82b18fddde15298120b`: [Build and checks](https://github.com/lebedenko/holonight-images/actions/runs/35744067722) completed/success.
- Viewer `149b86a908689477d1ba0cb4e7d486d091bf1024`: [Build and checks](https://github.com/lebedenko/holonight-viewer/actions/runs/35744065695) and [Licensing](https://github.com/lebedenko/holonight-viewer/actions/runs/35744065714) completed/success.
- Files `152cb98078e973fce74e020fd0e3b63bb4b5f046`: [Licensing](https://github.com/lebedenko/holonight-files/actions/runs/35744069727) completed/success; [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/35744069731) completed/failure.

Files' existing CI failure is the container Git ownership failure documented above, before compilation. It is
retained as a CI infrastructure follow-up, not reported as a passing check. Integration acceptance is supported by
the successful local builds/tests, isolated runtime evidence and user-confirmed manual checks.
