# Single-monitor integration acceptance — 2026-09-23

Status: **Integrated.** Files T5 and all required single-monitor/native checks
are complete. The subsequent **“publish and pin”** request authorized publication
of the qualification tooling and records and this final umbrella checkpoint.

## Candidate and provenance

Started with clean umbrella and participating repositories. Canonical `main`
references were checked with `git ls-remote origin refs/heads/main` in each
repository (outside the sandbox after SSH configuration access was denied):

| Repository | Initial measured candidate revision |
| --- | --- |
| Umbrella | cd2e4fcd8fbf2ba7037163d988b5019990db545b |
| Images | 3633865d2f39e4f163f0159a0f252f88245379f0 |
| Files | e8efed169bcea51c1ebdc846525a50331a2e298d |
| Viewer | 266deb99955286e19cc98f0bb6d11fdd082e0af9 |

These record the inspected candidate, not an alternative to the authoritative
gitlinks. No product implementation changes have been made. Qt provider
`863af4183bdf09ce05199b37e8f5dfb46a311ba1` and Config provider
`fe69a59e6b73167fd5349223a4d265d75386c139` are clean and match prior acceptance.
GCC 16.2.1, Qt 6.11.2 and Ninja match existing clean-build/runtime evidence.
Provider CMake caches use Release, tests disabled and Qt Wayland provider disabled.
Files' provider revision ledger is current. Both installed Images static archives
match their build artifacts and each other (SHA-256
`96f69b2c4570763c22ae39f060d3cc118273f8a586c26924c5a56a1ac607b11e`).

## Automated integration

Logs are preserved under Files `build/shared-images-single-monitor-20260923/automation/`.
They were collected at umbrella `build/verification/shared-image-outcomes-single-monitor/`
and moved intact into the ignored candidate evidence directory during cleanup.

| Check | Command and evidence | Result |
| --- | --- | --- |
| Images build | `cmake --build holonight-images/build/hardening-acceptance --parallel 4`; `provider-build.log` | Pass |
| Provider and installed package | `ctest --test-dir holonight-images/build/hardening-acceptance --output-on-failure`; `provider-ctest.log` | 2/2 pass |
| Files integration build | From Files: `cmake --build build/test --parallel 4`; `files-build.log` | Pass; current artifacts, no rebuild required |
| Files CTest | `ctest --test-dir holonight-files/build/test --output-on-failure`; `files-ctest.log`, `files-ctest-retry.log` | 18/25 pass in sandbox; seven socket/GPU failures retained, all seven pass on `--rerun-failed` outside sandbox; 25/25 passing coverage |
| Viewer integration build | From Viewer: `cmake --build build/test --parallel 4`; `viewer-build.log` | Pass |
| Viewer CTest | `ctest --test-dir holonight-viewer/build/test --output-on-failure` outside sandbox; `viewer-ctest.log` | 22/22 pass |
| Umbrella installer | `task test:installer`; `installer-final.log` | 16/16 pass after consumer verification |
| Final documentation/license checks | Changed Markdown links and `git diff --check` in all three repositories; `reuse lint` logs | Pass; REUSE 159/159 umbrella, 348/348 Files, 250/250 Viewer. Initial sandbox worker-socket denials retained in session output; rerun outside sandbox passed |
| Files prepublication acceptance | From Files: `CMAKE_BUILD_PARALLEL_LEVEL=4 task check`; `publication-task-check.log` | Pass: Debug/Release/test builds, 25/25 CTest, format, tidy, QML lint, REUSE and staged package checks; complete log reviewed |
| Fresh Release native lab | Files current-candidate `configure.log`, `build.log` | Pass; complete logs reviewed, no compiler warnings |
| Runner amendment | `python3 holonight-files/scripts/check-native-preview.py`; `scale-matrix-before.log`, `scale-matrix-after.log`; focused CTest in `runner-ctest-final.log` | Regression failed before change; 17/17 pass afterward; focused CTest pass |
| Frozen lab observer | `scripts/check-native-observer.py` against the fresh lab and copied prefix | Pass, 34 events; offscreen deliberately rejected as native |

Source contract review at these revisions confirms six typed Images outcomes,
separate optional metadata outcomes, translated consumer raster presentation,
silent cancellation and generation/request-ID rejection of stale results.
Files retains metadata alongside successful pixels; Viewer carries metadata
through `ImageInformation` in its decoded-image cache. Existing orientation,
cache, cancellation, bounds and outcome regressions remain in the passing suites.
No public API, format, scheduling or cache-policy changes are proposed.

Reuse the clean Release, complete quality checks and isolated installed-runtime
results in [Files verification](../../../holonight-files/docs/sdd/shared-image-outcomes/VERIFICATION.md)
and [Viewer verification](../../../holonight-viewer/docs/sdd/shared-image-outcomes/VERIFICATION.md).
Their complete runtime logs are retained in each consumer's
`build/verification/shared-image-outcomes/`; installed desktop launches passed.
Viewer's subsequent change only adjusts formatter tooling; its full acceptance is
recorded in [formatter verification](../../../holonight-viewer/docs/sdd/formatter-discovery/VERIFICATION.md).
No application/provider changes invalidate that evidence. Historical failed
attempts and CI observations remain in their original records; no CI polling was used.

## Completed native acceptance

The [Files report](../../../holonight-files/docs/sdd/native-preview-acceptance/SINGLE-MONITOR.md)
records the current frozen binary, provider/fixture hashes, commands, distributions,
visual judgments and retained failures. The user approved **actual 1/1.25/1.6/2**:
Hyprland rejects 1.5× at preserved 2560×1600/240Hz, so 1.5× is unavailable and
is not reported as passed. No artificial Qt scaling was used.

- [x] All 20 timing pairs and 40 startup processes pass, with no threshold misses.
- [x] Four visual logs validate; all 72 captures and matched physical-size reference
  comparisons pass by explicit user report. All eight fixtures were inspected per scale.
- [x] All 101 Quick Look openings meet the retained-pixel usability target; adequate
  upgrades are separately recorded, not subject to the 200ms usability deadline.
- [x] User restored actual 1.25×; read-only monitor records confirm unchanged mode/refresh.
- [x] Files sharp-preview T5, native N5/N6 completed locally.
- [x] Current-build Files/Viewer outcomes walkthrough passed by user report.
- [x] Final audit verifies frozen hashes, all accepted timing groups, four completed
  visual logs, 72 capture/reference hashes and corresponding user reports.
- [x] Publish the runner extension/records, verify canonical availability and clean
  exact pins, and record the final integration checkpoint in this umbrella commit.

The strict report command from Files is:

```sh
python3 scripts/native-preview.py report \
  --output build/shared-images-single-monitor-20260923/native --scales 1 1.25 1.6 2
```

It passes with 32 groups of five samples, one binary/provider combination,
no missing samples and no failures in the accepted matrix. A rejected 1× cold
attempt with no photo selections is retained under `attempts`, with the user's
explanation and the passing replacement. Historical 1.25× measurements and failed
attempts remain separate and are never relabeled as current-binary results.

## Corrections and walkthrough

No application/provider correction was required. Files' Python runner now accepts
actual 1.6× and an explicit four-scale report matrix while preserving the original
1/1.25/1.5/2 default. A regression proves 1.6× cannot satisfy a 1.5× report. The
original runner and frozen record are preserved; `scale-amendment.json` records
user authorization and the new runner hash. Binary, providers, fixtures, observer,
timing calculations, thresholds and capture helper did not change.

The first walkthrough used an incorrect fixture assumption: full-resolution
Fronalpstock exceeds Viewer's existing 32M-pixel/128MiB limit, and a 90000×90000
BMP header was rejected as damaged before reaching the resource-limit check.
Those logs and the correction record remain under `outcomes-walkthrough`.
This was a fixture mistake, not a product defect or a native matrix correction.

The corrected walkthrough used valid Colosseum and the existing 24M-pixel PNG
control, a damaged PNG, and the exact 9000×9000 BMP header from the passing
resource-limit regression. Fronalpstock's Viewer size-limit error is expected.
Evidence is in `outcomes-walkthrough-corrected`: both current Release binaries
exited 0; Viewer logs distinguish damaged and size-limit failures. The user
reported **“walkthrough passed”** for both apps' valid display, error recovery,
rapid navigation, correct final identity and absence of cancellation popups.
Manifests retain binary hashes, exact revisions, commands and monitor settings;
the dated user report is separate from raw manifests. Release build checks
reported no work to do before launch, confirming current artifacts.

## Final publication and remaining boundaries

The user subsequently authorized **“publish and pin”**. Canonical remote checks
and clean working-tree checks confirm Files
`05fa9f74965fc82d98610a4777ce7a527a941075`, Viewer
`6f9c048e2f936bc93e017a89cd18fb032159d603` and unchanged Images
`3633865d2f39e4f163f0159a0f252f88245379f0`. These are the final integration
pins; the initial table above preserves the actual measured candidate revisions.
`git diff e8efed1 05fa9f7 -- apps CMakeLists.txt CMakePresets.json` in Files
and `git diff 266deb9 6f9c048 -- apps scripts CMakeLists.txt CMakePresets.json`
in Viewer are empty. Full commit review confirms only Files qualification tooling,
its regressions and records changed; Viewer changed records only. Thus the exact
published revisions preserve the accepted application/provider contracts, native
binary and isolated-runtime evidence. No repeated native qualification is needed.

I-003 is Done and the initiative is Integrated in this umbrella checkpoint.
The [ledger](TASKS.md) records exact publication revisions and the once-only CI
snapshots; both new consumer runs were in progress with no conclusion at inspection.
No CI waiting or polling was performed, and no pending run is claimed to have passed.

Physical second-monitor testing awaits hardware and does not block this iteration;
it is not passed. Clipboard-service qualification, unrelated release gates and the
unknown-dimension runtime fixture remain explicitly deferred. Historical failed
attempts, measured revisions and CI observations are preserved separately.
