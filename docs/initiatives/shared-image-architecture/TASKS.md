# Shared image architecture — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| IMG-001 | holonight-images | Provider and installed package | — | ../../../holonight-images/docs/sdd/shared-image-architecture/ | Done | efe3e780327fa793fb76c82b18fddde15298120b (local) | Clean Release, 2/2 CTest, installed consumer, format and REUSE passed 2026-09-22 |
| IMG-002 | holonight-viewer | Raster and EXIF migration | IMG-001 | ../../../holonight-viewer/docs/sdd/shared-image-architecture/ | Done | 149b86a908689477d1ba0cb4e7d486d091bf1024 (local; baseline 08d504f7930e6e358f7c24c3d933115452018c44) | Clean Release; CTest 21/21, final smoke 182 passed/7 existing skips; format, tidy rechecks, QML/license/install checks and isolated runtime passed 2026-09-22 |
| IMG-003 | holonight-files | Verified-device migration | IMG-001 | ../../../holonight-files/docs/sdd/shared-image-architecture/ | Done | 152cb98078e973fce74e020fd0e3b63bb4b5f046 (local; baseline dc340ea1767c642844e2ffb4faba875b2056ad38) | Clean Release; all 22 CTest entries verified including repaired provider fixture; final affected 26/26; format, tidy rechecks, QML/license/install checks and isolated runtime passed 2026-09-22 |
| IMG-004 | umbrella | Published/pinned integration review | IMG-001–IMG-003 | — | Planned | — | Publication, pinning and manual checks pending |

## Handoff notes

All implementation commits remain local. No hosted CI run exists for these revisions. `holonight-images` has no
canonical remote yet and is not pinned; Viewer and Files gitlinks are unchanged. Files retains the pre-existing
untracked `tests/provider_revisions_test.sh`; the implementation commits its expanded fixture under a new name.
Detailed commands and acceptance corrections are recorded in each repository's local SDD.

Final IMG-004 verification has not run: it requires authorized publication/pinning and manual native Viewer
navigation, SVG/animation/clipboard and Files preview checks. The initiative remains Accepted, not Integrated.
