# Shared image maintenance — Coordination Ledger

All three tooling packages are locally Done. Each has a separate unpublished
repository checkpoint; no gitlinks changed. Publication and pin updates remain
subject to separate authorization. The initiative remains Accepted.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| M-001 | holonight-images | Provide separate off-by-default Clang ASan/UBSan/libFuzzer targets for raw EXIF, container metadata and bounded inspection/decoding. | Existing pinned contracts | [SDD](../../../holonight-images/docs/sdd/shared-image-maintenance/SPEC.md) | Done | `35efad8325f31991deb24149d2e2d8ec388ae8c1` (local only) | Assigned baseline `3633865d2f39e4f163f0159a0f252f88245379f0`; clean HEAD/pin verified 2026-09-23; 2026-09-24: Provider and installed-package CTest passed (2/2). Final seed replays and 60-second EXIF/metadata campaigns passed; decode exited 77 with a retained Qt PDF/PDFium leak (7,776 bytes/60 allocations). Tooling correctly reports the finding; codec repair remains outside scope. REUSE/format/diff checks passed. [Evidence](../../../holonight-images/docs/sdd/shared-image-maintenance/VERIFICATION.md) |
| M-002 | holonight-files | Add versioned measurement metadata and strict five-trial JSON/Markdown comparisons, then run fresh identical-production baseline/candidate datasets. | Existing pinned contracts | [SDD](../../../holonight-files/docs/sdd/shared-image-maintenance/SPEC.md) | Done | `98936ee55e4e70fdf8236e7c5e8685dda1eac330` (local only) | Assigned baseline `86e3f4a34a3b190f59d64f1c3e3a5584f98cd646`; clean HEAD/pin verified 2026-09-23; 2026-09-24: Full task check passed, including 27/27 Debug CTest entries, static analysis and staged installation. Eight comparison regressions and all 30 fresh measurement trials passed; comparison needs no provenance overrides. [Evidence](../../../holonight-files/docs/sdd/shared-image-maintenance/VERIFICATION.md) |
| M-003 | holonight-viewer | Add versioned measurement metadata and strict five-trial JSON/Markdown comparisons, then run fresh identical-production baseline/candidate datasets. | Existing pinned contracts | [SDD](../../../holonight-viewer/docs/sdd/shared-image-maintenance/SPEC.md) | Done | `1200adb820c802259af37b583ce076a863036c56` (local only) | Assigned baseline `af57d28416d68ca695c3a2d9bc30bb3b341e7dd0`; clean HEAD/pin verified 2026-09-23; 2026-09-24: All 24 Debug CTest entries and acceptance components passed; one new braces diagnostic was corrected and its translation unit rechecked. Eight comparison regressions and 20 final fresh trials passed with no provenance overrides. [Evidence](../../../holonight-viewer/docs/sdd/shared-image-maintenance/VERIFICATION.md) |
| M-004 | umbrella | Final integration | M-001–M-003, publication and authorized pins | — | Planned | — | Local handoffs complete; await publication and pin authorization |

## Local handoff — 2026-09-24

The final local evidence includes 50 successful measurement processes, identical
production code within each pair, and strict raw-evidence comparisons. Viewer's
first 20 trials are retained but superseded after a test-helper style correction;
the final 20 were recollected. No timing improvement or native-rendering claim is
made. Production APIs, source files, codec selection and caches remain unchanged.

M-001 completion covers harness delivery, bounded execution, nonzero status on
findings and retained reproduction evidence. It does not mean decode fuzzing is
clean: the Qt PDF/PDFium leak remains an open external-codec follow-up. No
suppression or production workaround was added.

M-004 remains Planned: no publication, authorized pin update or final umbrella
integration was performed. The unrelated Package Manager pending-updates working
tree and pre-existing Icons checkout revision were preserved.
