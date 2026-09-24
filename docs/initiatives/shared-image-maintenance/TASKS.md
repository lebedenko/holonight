# Shared image maintenance — Coordination Ledger

All three tooling packages are Done, published to canonical origin/main and pinned
after user authorization on 2026-09-24. The initiative remains Accepted; final
umbrella integration is Ready.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| M-001 | holonight-images | Provide separate off-by-default Clang ASan/UBSan/libFuzzer targets for raw EXIF, container metadata and bounded inspection/decoding. | Existing pinned contracts | [SDD](../../../holonight-images/docs/sdd/shared-image-maintenance/SPEC.md) | Done | `35efad8325f31991deb24149d2e2d8ec388ae8c1` (published) | Assigned baseline `3633865d2f39e4f163f0159a0f252f88245379f0`; clean HEAD/pin verified 2026-09-23; 2026-09-24: Provider and installed-package CTest passed (2/2). Final seed replays and 60-second EXIF/metadata campaigns passed; decode exited 77 with a retained Qt PDF/PDFium leak (7,776 bytes/60 allocations). Tooling correctly reports the finding; codec repair remains outside scope. REUSE/format/diff checks passed. [Evidence](../../../holonight-images/docs/sdd/shared-image-maintenance/VERIFICATION.md) |
| M-002 | holonight-files | Add versioned measurement metadata and strict five-trial JSON/Markdown comparisons, then run fresh identical-production baseline/candidate datasets. | Existing pinned contracts | [SDD](../../../holonight-files/docs/sdd/shared-image-maintenance/SPEC.md) | Done | `98936ee55e4e70fdf8236e7c5e8685dda1eac330` (published) | Assigned baseline `86e3f4a34a3b190f59d64f1c3e3a5584f98cd646`; clean HEAD/pin verified 2026-09-23; 2026-09-24: Full task check passed, including 27/27 Debug CTest entries, static analysis and staged installation. Eight comparison regressions and all 30 fresh measurement trials passed; comparison needs no provenance overrides. [Evidence](../../../holonight-files/docs/sdd/shared-image-maintenance/VERIFICATION.md) |
| M-003 | holonight-viewer | Add versioned measurement metadata and strict five-trial JSON/Markdown comparisons, then run fresh identical-production baseline/candidate datasets. | Existing pinned contracts | [SDD](../../../holonight-viewer/docs/sdd/shared-image-maintenance/SPEC.md) | Done | `1200adb820c802259af37b583ce076a863036c56` (published) | Assigned baseline `af57d28416d68ca695c3a2d9bc30bb3b341e7dd0`; clean HEAD/pin verified 2026-09-23; 2026-09-24: All 24 Debug CTest entries and acceptance components passed; one new braces diagnostic was corrected and its translation unit rechecked. Eight comparison regressions and 20 final fresh trials passed with no provenance overrides. [Evidence](../../../holonight-viewer/docs/sdd/shared-image-maintenance/VERIFICATION.md) |
| M-004 | umbrella | Final integration | M-001–M-003, publication and authorized pins | — | Ready | — | Published handoffs pinned on 2026-09-24; final umbrella integration remains |

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

At the local handoff, M-004 remained Planned: publication, pins and final umbrella
integration had not yet been performed. The unrelated Package Manager pending-updates working
tree and pre-existing Icons checkout revision were preserved.

## Publication and pins — 2026-09-24

The user authorized commit, publication and pinning. Published the three reviewed
implementation commits in one push per repository to canonical `origin/main`;
`git ls-remote origin refs/heads/main` verified each exact revision in the rows
above. Participating repositories are clean. The umbrella gitlinks now select
those published revisions. The unrelated Icons checkout and Package Manager
working tree remain unchanged.

Before the first implementation push, performed clean Release acceptance in each
repository's new `build/publication-acceptance-20260924` directory:

- Images: `cmake -S . -B build/publication-acceptance-20260924 -G Ninja
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON`, then
  `cmake --build build/publication-acceptance-20260924 -j 2` and
  `ctest --test-dir build/publication-acceptance-20260924 --output-on-failure`:
  passed 2/2, including the installed-package consumer.
- Files and Viewer: same clean Release configure/build with testing enabled,
  `/usr` install prefix, `lib` install directory, each repository's existing
  `build/deps/prefix` and its QML import directory. Explicitly selected
  `HolonightImages_DIR` from Images' new
  `build/publication-acceptance-20260924/tests/package-test/prefix/lib/cmake/HolonightImages`.
  This validates both consumers against the newly built provider at `35efad8`.
  `ctest --test-dir build/publication-acceptance-20260924 --output-on-failure`
  passed Files 21/21 and Viewer 24/24 outside the socket-restricted sandbox.

Complete configure/build logs were reviewed with no actionable warnings or
errors: each repository's `build/publication-acceptance-20260924.log`; consumer
CTest logs are `build/publication-ctest-20260924.log`. Prior full checks, the 50
measurement trials and the disclosed decode-fuzz finding remain valid; no source
correction or measurement rerun was needed for publication.

CI was queried once per exact implementation revision, without waiting or polling:

| Repository / revision | Workflow | Observed status | Conclusion | Run |
|---|---|---|---|---|
| Images `35efad8325f31991deb24149d2e2d8ec388ae8c1` | Build and checks | in_progress | none yet | [35975922267](https://github.com/lebedenko/holonight-images/actions/runs/35975922267) |
| Files `98936ee55e4e70fdf8236e7c5e8685dda1eac330` | Build and checks | in_progress | none yet | [35975956277](https://github.com/lebedenko/holonight-files/actions/runs/35975956277) |
| Files `98936ee55e4e70fdf8236e7c5e8685dda1eac330` | Licensing | completed | success | [35975956313](https://github.com/lebedenko/holonight-files/actions/runs/35975956313) |
| Viewer `1200adb820c802259af37b583ce076a863036c56` | Build and checks | in_progress | none yet | [35975974646](https://github.com/lebedenko/holonight-viewer/actions/runs/35975974646) |
| Viewer `1200adb820c802259af37b583ce076a863036c56` | Licensing | in_progress | none yet | [35975974674](https://github.com/lebedenko/holonight-viewer/actions/runs/35975974674) |

Pinning does not assert CI success or final ecosystem integration. M-004 is Ready;
its root checks and final integration record remain outstanding. Initiative status
stays Accepted. The Qt PDF/PDFium leak remains an explicitly retained finding.
