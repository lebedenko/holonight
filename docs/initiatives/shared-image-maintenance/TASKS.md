# Shared image maintenance — Coordination Ledger

All three packages are Ready after baseline and contract inspection. The coordinator
implements each repository separately; no gitlinks change during local work.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| M-001 | holonight-images | Provide separate off-by-default Clang ASan/UBSan/libFuzzer targets for raw EXIF, container metadata and bounded inspection/decoding. | Existing pinned contracts | [SDD](../../../holonight-images/docs/sdd/shared-image-maintenance/SPEC.md) | Ready | — | Assigned baseline `3633865d2f39e4f163f0159a0f252f88245379f0`; clean HEAD/pin verified 2026-09-23 |
| M-002 | holonight-files | Add versioned measurement metadata and strict five-trial JSON/Markdown comparisons, then run fresh identical-production baseline/candidate datasets. | Existing pinned contracts | [SDD](../../../holonight-files/docs/sdd/shared-image-maintenance/SPEC.md) | Ready | — | Assigned baseline `86e3f4a34a3b190f59d64f1c3e3a5584f98cd646`; clean HEAD/pin verified 2026-09-23 |
| M-003 | holonight-viewer | Add versioned measurement metadata and strict five-trial JSON/Markdown comparisons, then run fresh identical-production baseline/candidate datasets. | Existing pinned contracts | [SDD](../../../holonight-viewer/docs/sdd/shared-image-maintenance/SPEC.md) | Ready | — | Assigned baseline `af57d28416d68ca695c3a2d9bc30bb3b341e7dd0`; clean HEAD/pin verified 2026-09-23 |
| M-004 | umbrella | Final integration | M-001–M-003, publication and authorized pins | — | Planned | — | Await local handoffs and publication authorization |
