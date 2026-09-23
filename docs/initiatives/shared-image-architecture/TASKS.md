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

## Files orientation follow-up — published and pinned 2026-09-22

With user authorization, published Files commit `f0a5ed66c16cc53b6d059778989d17e822a68367`
(`fix: apply intrinsic image orientation to Files previews`) to canonical `origin/main` and
confirmed the exact remote revision with `git ls-remote` before updating the umbrella gitlink.
The original IMG-003/IMG-004 rows above retain their historical integration evidence.
Provider and Viewer revisions are unchanged.

Files now applies intrinsic EXIF orientation (including mirrors) to originals, publishes oriented
full-resolution dimensions, and lazily regenerates thumbnails lacking `Files::OrientationPolicy=applied-v1`.
Cached PNGs retain Ignore because their pixels are already oriented. Detailed scope and acceptance are in
the [Files orientation SDD](../../../holonight-files/docs/sdd/image-orientation/SPEC.md) and
[verification record](../../../holonight-files/docs/sdd/image-orientation/VERIFICATION.md).
That record's publication-pending statement describes the earlier local handoff; this entry records
the subsequent authorized publication.

Reused completed local acceptance for the unchanged implementation: all 22 test-preset CTest entries,
all 16 clean Release acceptance entries, final orientation/thumbnail regressions 30/30 in both Debug
and Release, quality/install checks, isolated runtime, and user-confirmed manual Files/Viewer comparison.
The recorded unrelated Viewer dialog-lifecycle regression remains a limitation; no Viewer fix or passing
claim is included in this handoff. Publication review checked the committed diff and whitespace;
documentation and pin changes do not require repeating unchanged application builds.

Checked CI once after publication with `gh run list --repo lebedenko/holonight-files --commit
f0a5ed66c16cc53b6d059778989d17e822a68367 --limit 5 --json headSha,status,conclusion,url,name`:

| Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `f0a5ed66c16cc53b6d059778989d17e822a68367` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35758528862) |
| `f0a5ed66c16cc53b6d059778989d17e822a68367` | Licensing | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35758529031) |

These are publication snapshots, not completed CI acceptance. No live waiting or polling was performed.

## Verified follow-ups — published and pinned 2026-09-22

Published the prepared commits to canonical `origin/main` in Images, Viewer, Files order.
`git ls-remote origin refs/heads/main` confirmed each exact revision before staging its umbrella
gitlink. All three product working trees were clean. The initiative remains **Integrated**;
the original integration and orientation records above are preserved as historical evidence.
The repository-local SDDs describe their earlier local-only handoffs; this entry records the
subsequent authorized publication and pin updates.

| Repository | Published revision | Local SDD and acceptance evidence |
|---|---|---|
| holonight-images | `3633865d2f39e4f163f0159a0f252f88245379f0` | [Scope](../../../holonight-images/docs/sdd/deterministic-contract-regressions/SPEC.md), [verification](../../../holonight-images/docs/sdd/deterministic-contract-regressions/VERIFICATION.md): deterministic device failures, cancellation, exact resource boundaries and malformed metadata regressions; clean Release, all 19 provider cases and installed-package consumer (2/2 CTest), formatting and REUSE passed. |
| holonight-viewer | `737d7a99849701f985e927a09f18c475231a6d1d` | [Scope](../../../holonight-viewer/docs/sdd/dialog-lifecycle-evidence/SPEC.md), [verification](../../../holonight-viewer/docs/sdd/dialog-lifecycle-evidence/VERIFICATION.md): corrected private D-Bus/offscreen lifecycle invocation passed 1/1; full smoke passed 182 cases with seven existing opt-in skips, including 13 PortalFileChooser and six PortalViewer cases. |
| holonight-files | `84d4023818978aa3d8dd72a1276d6fcee75cc3eb` | [Scope](../../../holonight-files/docs/sdd/container-verification/SPEC.md), [verification](../../../holonight-files/docs/sdd/container-verification/VERIFICATION.md): exact four-path system Git trust repaired the reproduced container ownership rejection; extracted workflow, unprivileged acceptance under both locales and isolated installed-payload runtime passed. |

### Reused acceptance and corrected evidence

Images changed only tests and documentation; Viewer changed only documentation; Files changed only
the container workflow and documentation. No provider implementation, public contract or consumer
application code changed. Completed acceptance is reused without repeating unchanged builds.
The consumer artifacts tested against Images `efe3e780327fa793fb76c82b18fddde15298120b` remain
applicable because the new Images commit leaves production sources unchanged.

Viewer's earlier `openDialog` failure in the Files orientation handoff came from a direct smoke
invocation without the required private-bus runner: a desktop portal could serve the request instead
of opening the fallback dialog. The corrected isolated invocation and full smoke pass supersede that
failure assessment. No application defect was reproduced, no Viewer code fix was needed, and no new
native manual check is claimed.

Files' exact workflow body passed `task deps`, unprivileged `LC_ALL=C.UTF-8 task check` and
`LC_ALL=en_US.UTF-8 task test` in the existing CI image: clean builds, 16/16 CTest in each locale,
555 smoke cases with two existing native/performance opt-in skips, formatting, all 94 clang-tidy
translation units, QML, licensing and staged installation checks. A separate read-only trust probe
confirmed that root and UID 1001 trust only the four intended source paths; the exit trap restored
build ownership. The isolated runtime image also passed. Container namespace restrictions skipped
16 cross-filesystem and three cross-filesystem window cases; accelerated separator checks remained
disabled, while six software scales passed. These limitations and the historical hosted failures are
retained; local container acceptance is not a claim that the new hosted run has completed.

### Publication CI snapshot

Checked once at approximately 19:59 UTC on 2026-09-22 using `gh run list --repo
lebedenko/<repository> --commit <published-sha> --limit 10 --json headSha,status,conclusion,url,name`.

| Repository | Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|---|
| holonight-images | `3633865d2f39e4f163f0159a0f252f88245379f0` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-images/actions/runs/35777273578) |
| holonight-viewer | `737d7a99849701f985e927a09f18c475231a6d1d` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-viewer/actions/runs/35777291627) |
| holonight-viewer | `737d7a99849701f985e927a09f18c475231a6d1d` | Licensing | `completed` | `success` | [GitHub Actions](https://github.com/lebedenko/holonight-viewer/actions/runs/35777291629) |
| holonight-files | `84d4023818978aa3d8dd72a1276d6fcee75cc3eb` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35777305850) |
| holonight-files | `84d4023818978aa3d8dd72a1276d6fcee75cc3eb` | Licensing | `queued` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35777305980) |

No waiting or polling was performed. Publication review passed committed whitespace checks for
all three follow-ups. Umbrella closure passed `git diff --check`, local Markdown link validation
and exact staged gitlink verification against the confirmed remote revisions. The separate umbrella
closure commit is kept local as requested.

## Viewer performance follow-up — published and pinned 2026-09-23 (Europe/Kyiv)

Published Viewer `06b0061a20ab4175f6f1546c8316132e31271bce`
(`test: measure Viewer image performance and memory`) to canonical `origin/main`.
`git ls-remote origin refs/heads/main` confirmed that exact revision before pinning;
Viewer's working tree was clean. Images and Files pins are unchanged, and the initiative
remains **Integrated**. The [local SDD](../../../holonight-viewer/docs/sdd/image-performance/SPEC.md)
and [verification record](../../../holonight-viewer/docs/sdd/image-performance/VERIFICATION.md)
describe the completed local implementation; their local-only scope notes precede the
user's subsequent authorization to commit, publish and pin recorded here.

Reused completed acceptance: 45 focused cases, five runner regression tests, all 22 Debug
and 22 clean Release CTest entries, 25 initial performance trials and five final navigation
trials passed. Contributor checks passed after selecting Qt 6.11.2 through the existing
`QMLFORMAT` override and correcting/rechecking benchmark-only tidy findings. Formatting,
QML lint/import/type checks, licensing and staged installation passed. Navigation RSS was
flat across pressure-cycle endpoints in every trial; no production correction was justified.
Measurements are offscreen, with synthetic fixtures, and do not establish native rendering
or clipboard-transfer performance. No provider or application implementation changed.

Checked hosted CI once at approximately 21:49 UTC on 2026-09-22 (2026-09-23 locally), using
`gh run list --repo lebedenko/holonight-viewer --commit 06b0061a20ab4175f6f1546c8316132e31271bce
--limit 10 --json headSha,status,conclusion,url,name`. The initial sandbox API connection
failed; the network-permitted retry returned this snapshot. No polling or waiting followed.

| Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `06b0061a20ab4175f6f1546c8316132e31271bce` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-viewer/actions/runs/35788748499) |
| `06b0061a20ab4175f6f1546c8316132e31271bce` | Licensing | `completed` | `success` | [GitHub Actions](https://github.com/lebedenko/holonight-viewer/actions/runs/35788748482) |

Publication review confirmed the staged ten-file Viewer scope and exact instrumentation
hashes from the final measurements. Umbrella whitespace, local Markdown links and the exact
published gitlink were checked. This separate umbrella handoff commit remains local.

## Files preview performance follow-up — published and pinned 2026-09-23 (Europe/Kyiv)

Published Files `06c42f03534cdf57b2fb09f73bbfa69f029d0f9c`
(`fix: avoid repeated preview decoding from rounded bounds`) to canonical `origin/main`.
`git ls-remote origin refs/heads/main` confirmed that exact revision before pinning;
Files' working tree was clean. The [local SDD](../../../holonight-files/docs/sdd/preview-performance/SPEC.md)
and [verification record](../../../holonight-files/docs/sdd/preview-performance/VERIFICATION.md)
record the completed implementation and measurements. Their local-only handoff notes
precede the user's subsequent authorization to commit and pin, recorded here.

The Files-local correction passes original requested bounds to full decoding, avoiding
a second aspect-ratio fit that lost one pixel and caused repeated inadequate decodes.
The synthetic 2300-pixel upgrade changed from 37–39 attempts without adequate pixels
to one attempt and approximately 268 ms median. All 15 candidate performance trials
passed with identical baseline/candidate instrumentation, encoded fixtures, providers
and build configuration. Cache timings overlapped across trials; pressure-cycle RSS
settled without demonstrated sustained growth. No shared provider, public API, QML or
cache-policy change was made, and other gitlinks are unchanged.

Reused completed acceptance: clean Release build with testing enabled, 114 focused
preview/thumbnail/EXIF cases, six runner failure-path tests, all 23 CTest entries in
`task check`, formatting, full C++/QML lint, REUSE, staged installation and QML policy/
metadata checks passed. The network-disabled installed-runtime container passed as an
ordinary user. Initial sandbox socket/OpenGL failures passed on the unrestricted rerun
without disabling checks. Native sharp-preview task T5 remains open; neither synthetic
fixtures nor offscreen measurements qualify native sharpness or compositor behavior.
Historical integration/native acceptance remains unchanged; the initiative remains
**Integrated** and this entry records only the scoped Files follow-up.

Checked hosted CI once at approximately 23:47 UTC on 2026-09-22 (2026-09-23 locally),
using `gh run list --repo lebedenko/holonight-files --commit
06c42f03534cdf57b2fb09f73bbfa69f029d0f9c --limit 10 --json headSha,status,conclusion,url,name`.

| Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `06c42f03534cdf57b2fb09f73bbfa69f029d0f9c` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35799105733) |
| `06c42f03534cdf57b2fb09f73bbfa69f029d0f9c` | Licensing | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35799105817) |

No CI waiting or polling followed. Publication review verified the fifteen-file Files
scope against the measured production/instrumentation hashes. Umbrella whitespace,
local Markdown links and the exact published gitlink were checked. This separate
umbrella checkpoint remains local alongside the existing local checkpoints.

## Files native preview follow-up — published and pinned 2026-09-23

Published Files `8ba2a6bdec2c99ecb7c34ade107328204e2e180f`
(`fix: use window DPR for native previews`) to canonical `origin/main`.
`git ls-remote origin refs/heads/main` confirmed the exact revision before pinning;
the Files working tree is clean. The [native acceptance SDD](../../../holonight-files/docs/sdd/native-preview-acceptance/README.md)
and [verification record](../../../holonight-files/docs/sdd/native-preview-acceptance/VERIFICATION.md)
retain the implementation, evidence and pending rows. Their local/uncommitted
handoff notes precede the user's subsequent authorization to commit and pin.

The passive, non-installed lab demonstrated a fractional screen/window DPR mismatch
on native Wayland at 1.25×. Both Files preview consumers now use their owning window's
DPR, protected by a deterministic regression. The lab, photographic pins, capture
helper and evidence validator remain testing-only. No provider or other gitlink changes.

Reused completed acceptance: clean final Release lab build, focused preview regressions,
all 25 CTest targets, 16 tooling tests, full C++/QML lint, formatting, REUSE, staged
installation, QML policy/metadata and isolated installed-runtime acceptance passed.
The aggregate `task check` invocation stopped at observer lint findings; corrected
lint and the remaining stages passed separately, as recorded in the Files SDD.
At actual 1.25×, five photographic cold/disk/memory pairs and ten startup processes
passed without threshold misses. The user reported no visible issues during the
eight-fixture walkthrough, then requested that remaining native rows stay pending.
Other scales, remaining captures and matched-reference inspection remain open;
sharp-preview T5 is not closed. Original compositor scale remains 1.25×.

Hosted CI snapshot at approximately 09:58 UTC on 2026-09-23, queried with the full
published revision using `gh run list --repo lebedenko/holonight-files --commit
8ba2a6bdec2c99ecb7c34ade107328204e2e180f --limit 10 --json headSha,status,conclusion,url,name`:

| Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `8ba2a6bdec2c99ecb7c34ade107328204e2e180f` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35845987770) |
| `8ba2a6bdec2c99ecb7c34ade107328204e2e180f` | Licensing | `completed` | `success` | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35845987771) |

An initial abbreviated-SHA query returned no runs; the full-SHA sandbox query had
a connection failure and its network-permitted retry produced this snapshot.
No CI waiting or status polling followed. The staged 23-file Files scope and
umbrella whitespace, handoff links and published gitlink were reviewed. Historical
integration status and unrelated pending work remain unchanged. This separate
umbrella checkpoint remains local.

## Viewer information-preview DPR — published and pinned 2026-09-23 (Europe/Kyiv)

Published Viewer `2085b8f1f6d448a4da306d5ee022ef2ac58e5904`
(`fix: use window DPR for information preview`) to canonical `origin/main`.
`git ls-remote origin refs/heads/main` confirmed this exact revision before pinning;
the Viewer working tree is clean. The [local SDD](../../../holonight-viewer/docs/sdd/information-preview-dpr/SPEC.md)
and [verification record](../../../holonight-viewer/docs/sdd/information-preview-dpr/VERIFICATION.md)
record the reproduced screen/window DPR mismatch and the one-line popup binding fix.
The user reported manual checks done and authorized commit and pin on 2026-09-23,
closing this popup's manual visual qualification. Files T5, physical mixed-monitor
acceptance and unrelated deferred gates remain open; other gitlinks are unchanged.

Reused completed acceptance: focused red/green DPR and painted-sampling regression,
19/19 popup/canvas/geometry tests, all 22 CTest entries, clean Release build and
isolated installed runtime passed. All required task-check components passed;
the aggregate command stopped at test identifier-length diagnostics, then the
corrected affected-file tidy check and remaining stages passed individually.
Only acceptance documentation changed during this handoff; no unaffected build or
runtime checks were repeated. Staged scope, whitespace and documentation links
were reviewed. Historical initiative integration status remains unchanged.

Hosted CI snapshot at approximately 10:51 UTC on 2026-09-23, queried once with
`gh run list --repo lebedenko/holonight-viewer --commit
2085b8f1f6d448a4da306d5ee022ef2ac58e5904 --limit 10 --json headSha,status,conclusion,url,name`:

| Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `2085b8f1f6d448a4da306d5ee022ef2ac58e5904` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-viewer/actions/runs/35851155125) |
| `2085b8f1f6d448a4da306d5ee022ef2ac58e5904` | Licensing | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-viewer/actions/runs/35851155018) |

The initial sandboxed push failed on system SSH configuration permissions; the
network-permitted retry succeeded. No CI waiting or polling followed. This separate
umbrella checkpoint remains local.

## Files thumbnail cancellation — published and pinned 2026-09-23

Published Files `67d8dd9710cf13510374d23f68ce3301b8793cf6`
(`fix: propagate preview cancellation through thumbnails`) to canonical `origin/main`.
`git ls-remote origin refs/heads/main` confirmed the exact revision before pinning;
the Files working tree is clean. The [local SDD](../../../holonight-files/docs/sdd/preview-cancellation/README.md)
and [verification record](../../../holonight-files/docs/sdd/preview-cancellation/VERIFICATION.md)
record implementation and automated acceptance. Their local/uncommitted handoff
notes precede the user's subsequent authorization to commit and pin.

Each request's cancellation token now reaches thumbnail inspection, decoding and
cache publication. Cancellation silently stops subsequent work and abandons
uncommitted writes, preserving existing entries. Active codecs/filesystem operations
and a commit already started remain cooperative. Images stays at
`3633865d2f39e4f163f0159a0f252f88245379f0`; no provider API or other gitlink changes.

Reused completed acceptance: eight reproduced failures now pass, 16 new cancellation
cases pass, clean Release build, complete `task check` (25 CTest entries, full lint,
formatting, licensing, staged installation and QML checks), isolated installed runtime,
and 15/15 performance trials on each of baseline and candidate passed. Timing ranges
largely overlap and decode-attempt counts are unchanged; no speedup is claimed.
Publication review matched production and instrumentation hashes to the measured
candidate and checked staged scope, whitespace and local documentation links.
No unchanged expensive acceptance checks were repeated for this handoff.

Hosted CI was checked once on 2026-09-23 with
`gh run list --repo lebedenko/holonight-files --commit
67d8dd9710cf13510374d23f68ce3301b8793cf6 --limit 10 --json headSha,status,conclusion,url,name`:

| Revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `67d8dd9710cf13510374d23f68ce3301b8793cf6` | Build and checks | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35864744176) |
| `67d8dd9710cf13510374d23f68ce3301b8793cf6` | Licensing | `in_progress` | pending (empty API conclusion) | [GitHub Actions](https://github.com/lebedenko/holonight-files/actions/runs/35864744495) |

No CI waiting or polling followed. Native sharp-preview T5, mixed-monitor
qualification and other deferred gates remain open. Historical initiative integration
status is unchanged. This separate umbrella checkpoint remains local alongside the
two existing local checkpoints.
