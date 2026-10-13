# Unified external dependency management — Coordination ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| EDM-001 | umbrella | Baseline, audit, contracts and repository SDDs | — | README.md | Done | `523cb8b` + documentation checkpoints below | Exact baseline, 250 supplement entries/103 names and contracts reviewed; all 18 local SDDs committed separately and validated |
| EDM-002 | umbrella | Versioned declarations, prefix/validation/cache tooling and installer profile | EDM-001 | tooling/README.md | Done | `523cb8b` | 32 tooling and 67 installer fixtures passed; generated profiles, installed-provider smoke and final diff review passed |
| EDM-003 | umbrella | System QMarkdown package and Arch CI prerequisite qualification | EDM-002 | packaging/ci/README.md | Done | `523cb8b` | Clean pinned QMarkdown package and offline full/minimal Arch prerequisite qualification passed; historical qualification retained; current publication/handoff is EDM-024 |
| EDM-004 | holonight-config | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-config/docs/sdd/external-dependency-management/SPEC.md) | Done | `0ccd25f323662f50a47bb048be636160f2b7c135` | Audit baseline `d6a392b41991f70a004d58f7694c7b6115cb7280`; next implementation baseline `854784a32f16c231ada49db9b6188e79c5903900`; 2026-10-12: bundle 2.0.0, pkg-config declaration and qualified offline Arch CI adopted; 4 launcher + 3 discovery/cache regressions, both CTest entries, release, format/tidy and REUSE pass; full evidence in local SPEC; published to canonical origin/main and pinned; latest CI Licensing in_progress (pending), run 38279431526 |
| EDM-005 | holonight-system-services | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-system-services/docs/sdd/external-dependency-management/SPEC.md) | Done | `70614eb70329af7014853c2973e5624acf0b251e` | Audit baseline `39472e6dcafc93acea218a234213c346be256586`; implementation baseline `3bd6ebca0c0e5f51768105fa1970007e3e83da65`; 2026-10-12: bundle 2.0.0, Qt >=6.11 and installed GTest/GMock adopted; all eight offline acceptance lanes pass, including 195 backend tests, installed consumers, Release/Core builds, full format/tidy and REUSE; published to canonical origin/main and pinned; latest CI Licensing in_progress (pending), run 38289139967; full evidence in local SPEC and handoff below |
| EDM-006 | holonight-qt | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004 | [SPEC](../../../holonight-qt/docs/sdd/external-dependency-management/SPEC.md) | Done | `7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68` | Audit baseline `680d709de4d1d8e8697d6a69a99f15ef891ef7b2`; implementation baseline `2a6fcb0ef29d20e3413f425914ec1cf171b82306`; Config provider `0ccd25f323662f50a47bb048be636160f2b7c135`; 2026-10-12: bundle 2.0.0, explicit preparation and five qualified offline lanes pass; Full 97/97, Minimal 86/86, Release install, strict tidy across 76 units, QML checks and REUSE; 5 launcher + 12 dependency regressions; published to canonical origin/main and pinned after approval; latest CI Licensing in_progress (pending), run 38309160449; full evidence in local SPEC and handoff below |
| EDM-007 | holonight-appearance-adapters | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-005, EDM-004, EDM-006 | [SPEC](../../../holonight-appearance-adapters/docs/sdd/external-dependency-management/SPEC.md) | Done | `810a61dad372f5b9c1abfe9fd56a7b72ea81c28e` | 2026-10-13: bundle 2.0.0 and explicit providers adopted; Full 11/11, Minimal 8/8, Release install, strict format/tidy across 15 units, REUSE, 6 launcher + 16 dependency regressions pass locally; published once to canonical origin/main and pinned locally; CI rerun attempt 2 completed/success at this revision, run 38318125058 (original GHCR authorization failure preserved below); full evidence in local SPEC and handoff below |
| EDM-008 | holonight-icons | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-icons/docs/sdd/external-dependency-management/SPEC.md) | Done | `b1ee3e7b9e804542e22c8eebd3946eb9c04138bb` | 2026-10-13: bundle 2.0.0, explicit hash-validated renderer fixture, Qt >=6.11 and offline five-lane acceptance adopted; 47 Python tests, 19 launcher/dependency regressions, 282 Qt masters, GTK3/GTK4 symbolic checks, previews, Release staging, canonical format/strict tidy and four REUSE roots pass locally; two separate cleanup/adoption commits published in one push and pinned locally; latest CI run 38369393516 attempt 1 in_progress, conclusion null, at this revision; full evidence in local SPEC and handoff below |
| EDM-009 | holonight-images | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-images/docs/sdd/external-dependency-management/SPEC.md) | Done | `ae827d78db9cc21f9537c27f50f49baf879324da` | 2026-10-13: bundle 2.0.0, installed GTest CONFIG and qualified offline four-lane CI adopted; 3/3 CTest registrations, 36 provider cases, release/external-prefix consumers, optional Clang fuzz builds, format/strict tidy across 10 units, REUSE and 19 launcher/dependency regressions pass locally; cleanup/adoption commits separate; published to canonical origin/main and pinned locally; latest CI Build and checks in_progress (pending), run 38385319992; full evidence in local SPEC |
| EDM-010 | holonight-thumbnails | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-thumbnails/docs/sdd/external-dependency-management/SPEC.md) | Done | `c9ae0ad9a64e8ce28ee669b5463ef1bec74bc16d` | 2026-10-13: bundle 2.0.0, installed GTest CONFIG and qualified offline four-lane CI adopted; both CTest registrations, all 11 cache cases, Release/external-prefix consumer, format/strict tidy across 3 units, REUSE and 19 launcher/dependency regressions pass locally; separate cleanup/adoption commits published together to canonical origin/main and pinned locally; latest CI Build and checks in_progress (pending), run 38398351495; full evidence in local SPEC and handoff below |
| EDM-011 | holonight-search | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-search/docs/sdd/external-dependency-management/SPEC.md) | Ready | — | Audit baseline `26067775e2eac3d9a779b3114dfbddc96834c7de`; implementation baseline `993929cc717f3beaf99c60e01441dc3e86dfe7cf`, confirmed on canonical origin/main with a clean checkout on 2026-10-13; next-iteration handoff below; no implementation or acceptance result claimed |
| EDM-012 | holonight-shell | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-005, EDM-006 | [SPEC](../../../holonight-shell/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `d5c5e8d50f6cd4d3ccabb6b8d242ff56914977de`; implementation awaits handoff |
| EDM-013 | holonight-settings | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-005, EDM-004, EDM-006, EDM-012 | [SPEC](../../../holonight-settings/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `6ec7a402ebc319f9a925fdf97d8e0382e0c1ef42`; implementation awaits handoff |
| EDM-014 | holonight-viewer | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-006, EDM-009, EDM-010 | [SPEC](../../../holonight-viewer/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `2b696a328ec109bd11fe6e1b67e37ea727c8bff5`; implementation awaits handoff |
| EDM-015 | holonight-files | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-005, EDM-006, EDM-009, EDM-010, EDM-011 | [SPEC](../../../holonight-files/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `e8af0a8312133609f2ddd30e87d084be78971a8c`; implementation awaits handoff |
| EDM-016 | xdg-desktop-portal-holonight | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-015, EDM-011, EDM-006 | [SPEC](../../../xdg-desktop-portal-holonight/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `7f09d6bcef64086bf3c7eb8c4eee05017a6f2dae`; implementation awaits handoff |
| EDM-017 | holonight-ai | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-006 | [SPEC](../../../holonight-ai/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `777affc646b44bfb757bd2616f5cd7a218897cba`; implementation awaits handoff |
| EDM-018 | holonight-pkg-manager | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-006 | [SPEC](../../../holonight-pkg-manager/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `879bea1f4b71a2ddf185f45fc2d3e153edc46ac5`; implementation awaits handoff |
| EDM-019 | holonight-greeter | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-006 | [SPEC](../../../holonight-greeter/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `d99e0a17f95af977a42785957e9311597e38bab0`; implementation awaits handoff |
| EDM-020 | holonightd | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonightd/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `c6a9f9e1a353322bf7a3430cdab8392890348ccb`; implementation awaits handoff |
| EDM-021 | holonight-hyprlock | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-hyprlock/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `def9618fca833535275e8a8aa9a0e577acda8377`; implementation awaits handoff |
| EDM-023 | umbrella | Debian release environment qualification | EDM-002 | packaging/ci/README.md | Superseded | — | Deferred for pre-release Arch priorities; mappings retained without qualified support |
| EDM-024 | umbrella | Qualify, manually publish and hand off current Arch environments | EDM-002, EDM-003 | packaging/ci/README.md | Done | `8f437c0` + publication checkpoint | Offline full qualification and daemon reuse passed; both registry digest pulls preserve qualified IDs; anonymous availability verified; see [VERIFICATION](VERIFICATION.md) |
| EDM-022 | umbrella | Verify and integrate exact published revisions | EDM-004–EDM-021, EDM-024 | — | Planned | — | Automated and manual ecosystem acceptance pending; published Config and System Services adoption pins recorded in handoffs below |

Allowed states: Planned, Ready, In Progress, Done, Blocked, Superseded. Done requires a local commit and passed
local verification; it does not make this initiative Integrated. Provider handoffs must be available on canonical
remotes before dependent implementation and pin updates. Record final commands/results/date in EDM-022 before closure.


All 18 local SDDs are committed in their owning repositories. These are documentation checkpoints, not adoption
implementation commits. These checkpoints did not start adoption; all 18 submodule pins select these published
SDD documentation revisions. The original audit baselines remain recorded in BASELINE.json.

Foundation checkpoints `523cb8b` and `1019c4e` were published to `origin/main` on 2026-10-12. The qualified Arch images
remained local at that checkpoint; their immutable IDs and evidence are in [VERIFICATION.md](VERIFICATION.md). At that checkpoint, repository adoption
remained Planned until the qualified environment and canonical tooling handoff are available. The full initiative
is not implemented or integrated. No application CMake, vendored headers, active CI launchers or gitlinks have
been migrated by the foundation checkpoint.

## Repository-local SDD documentation checkpoints — 2026-10-12

Each commit contains only `docs/sdd/external-dependency-management/SPEC.md`, with message
`docs(deps): record external dependency adoption specification`. All were published to canonical `origin/main`
and verified with `git ls-remote` before pinning on 2026-10-12.
Baselines, work-package IDs, canonical metadata references and whitespace were checked;
all 18 repository working trees are clean. No application acceptance result is claimed.

| Repository | SDD documentation commit |
|---|---|
| holonight-ai | `0d8c54e166fb4e34ee1e496421c4bd98339a95c1` |
| holonight-appearance-adapters | `37508f71ed37a16b824329c303083a08cf88aa2f` |
| holonight-config | `854784a32f16c231ada49db9b6188e79c5903900` |
| holonight-files | `2a71f3a9b7faf4542ddad1f7e6c7a686d869a80e` |
| holonight-greeter | `31e8f8ece6d4bb4e90d11433a253150726535916` |
| holonight-hyprlock | `a366a31eaf1b6836a84882a47fe74c34469f7be0` |
| holonight-icons | `7684b021a5b74c7d4e34b7dd05bb3bdd02456473` |
| holonight-images | `ce9bf6957f6efa51a3f5dbf9f51d95fb9b48cd6f` |
| holonight-pkg-manager | `8042ed3890fc3bf226dc7d4c991459cd5c5599a2` |
| holonight-qt | `2a6fcb0ef29d20e3413f425914ec1cf171b82306` |
| holonight-search | `993929cc717f3beaf99c60e01441dc3e86dfe7cf` |
| holonight-settings | `b99c2fcc97a2d7e7c6f6f48f087cdb9fd1536452` |
| holonight-shell | `27567a918aae67ad43dba0e813b3f40ed14e539b` |
| holonight-system-services | `3bd6ebca0c0e5f51768105fa1970007e3e83da65` |
| holonight-thumbnails | `59fb2e92e8794e06db2ff8a1a6ec5cc1ebc66c03` |
| holonight-viewer | `74eee36c7484b37dcece55b5cdf71d84f21c93bb` |
| holonightd | `569905495a8ec0089a62c86c1b39ca68953ae01e` |
| xdg-desktop-portal-holonight | `926de7ccff8146235a014c52a8da890dcc3b0919` |

## Publication and pin verification — 2026-10-12

All submodules are clean. Canonical remote branch tips match the exact pinned documentation commits.
`git show --check` and baseline-parent/specification-only checks passed in each repository.
Latest CI was queried once after publication; pending/missing runs are not acceptance evidence.
No implementation or manual integration acceptance is claimed, and the initiative remains Accepted.

| Repository | CI revision | Status | Conclusion | Latest run |
|---|---|---|---|---|
| holonight-ai | `0d8c54e166fb4e34ee1e496421c4bd98339a95c1` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-ai/actions/runs/38180145072) |
| holonight-appearance-adapters | `37508f71ed37a16b824329c303083a08cf88aa2f` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-appearance-adapters/actions/runs/38180149067) |
| holonight-config | `854784a32f16c231ada49db9b6188e79c5903900` | completed | success | [run](https://github.com/lebedenko/holonight-config/actions/runs/38180153878) |
| holonight-files | `2a71f3a9b7faf4542ddad1f7e6c7a686d869a80e` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-files/actions/runs/38180157745) |
| holonight-greeter | `31e8f8ece6d4bb4e90d11433a253150726535916` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-greeter/actions/runs/38180162106) |
| holonight-hyprlock | `a366a31eaf1b6836a84882a47fe74c34469f7be0` | completed | success | [run](https://github.com/lebedenko/holonight-hyprlock/actions/runs/38180166382) |
| holonight-icons | `7684b021a5b74c7d4e34b7dd05bb3bdd02456473` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-icons/actions/runs/38180171276) |
| holonight-images | `ce9bf6957f6efa51a3f5dbf9f51d95fb9b48cd6f` | completed | success | [run](https://github.com/lebedenko/holonight-images/actions/runs/38180176031) |
| holonight-pkg-manager | `8042ed3890fc3bf226dc7d4c991459cd5c5599a2` | completed | success | [run](https://github.com/lebedenko/holonight-pkg-manager/actions/runs/38180180070) |
| holonight-qt | `2a6fcb0ef29d20e3413f425914ec1cf171b82306` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-qt/actions/runs/38180183755) |
| holonight-search | `993929cc717f3beaf99c60e01441dc3e86dfe7cf` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-search/actions/runs/38180187439) |
| holonight-settings | `b99c2fcc97a2d7e7c6f6f48f087cdb9fd1536452` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-settings/actions/runs/38180191572) |
| holonight-shell | `27567a918aae67ad43dba0e813b3f40ed14e539b` | queued | Pending | [run](https://github.com/lebedenko/holonight-shell/actions/runs/38180196167) |
| holonight-system-services | `3bd6ebca0c0e5f51768105fa1970007e3e83da65` | completed | success | [run](https://github.com/lebedenko/holonight-system-services/actions/runs/38180199580) |
| holonight-thumbnails | `59fb2e92e8794e06db2ff8a1a6ec5cc1ebc66c03` | in_progress | Pending | [run](https://github.com/lebedenko/holonight-thumbnails/actions/runs/38180203410) |
| holonight-viewer | `74eee36c7484b37dcece55b5cdf71d84f21c93bb` | queued | Pending | [run](https://github.com/lebedenko/holonight-viewer/actions/runs/38180207239) |
| holonightd | `569905495a8ec0089a62c86c1b39ca68953ae01e` | queued | Pending | [run](https://github.com/lebedenko/holonightd/actions/runs/38180211785) |
| xdg-desktop-portal-holonight | `—` | Missing | — | No run returned |

CI snapshot times (UTC): 2026-10-11T22:23:46.765764+00:00 through 2026-10-11T22:23:48.212561+00:00.

## EDM-024 next implementation handoffs

| Work package | Assigned repository | Exact next upstream baseline |
|---|---|---|
| EDM-004 | holonight-config | `854784a32f16c231ada49db9b6188e79c5903900` |
| EDM-005 | holonight-system-services | `3bd6ebca0c0e5f51768105fa1970007e3e83da65` |

Each implementer changes only the assigned repository and refreshes its local SPEC during adoption to reflect
this Arch contract and the current QMarkdown source. Original audit baselines remain in BASELINE.json and local
SPEC history. Adopt canonical bundle 2.0.0, portable installed dependency discovery and explicit source preparation;
use published qualified digest references for offline CI acceptance. No submodule pins change in this handoff.
EDM-012 includes Shell’s release build gate migration to Arch while preserving tests, linting and quality checks.

EDM-024 is complete: both qualified Arch images are available by the immutable registry references in
[VERIFICATION.md](VERIFICATION.md) and `verification/edm024/PUBLICATION.json`. Canonical tooling is unchanged from
qualification checkpoint `8f437c03c6b8da4ead2d16d938b6fb1c4f0a9702`; the completed handoff publishes that checkpoint
and its publication evidence together. EDM-004 and EDM-005 are Ready; adoption and application acceptance have
not started. The initiative remains Accepted. The original audit and all historical qualification evidence are retained.

## EDM-004 local acceptance handoff — 2026-10-12

Config implementation `0ccd25f323662f50a47bb048be636160f2b7c135` is locally committed and verified;
its working tree is clean. Canonical `origin/main` was confirmed at the exact assigned baseline before adoption.
Publication and the umbrella pin update await approval. No dependent implementation may use this unpublished revision.
EDM-004 Done records local acceptance only; initiative integration and hosted CI are not claimed.

Config preserves its pkg-config toml++ interface and custom test framework. Its canonical declaration now overrides
the catalog discovery mechanism to pkg-config, matching CMake and the copied standalone declaration. The generated
production installer probe is refreshed; package requirements are unchanged. Bundle drift and declaration equality
checks pass, and all 32 shared tooling fixtures pass. Three clean offline CI lanes pass, including test/release builds,
the installed-package consumer, full format/tidy and separate REUSE licensing. Complete logs were reviewed and
toolchain, warnings and commands recorded in the local SPEC. No gitlinks change in this local handoff preparation.

## EDM-004 approved publication and pin — 2026-10-12

User approved publication of Config `0ccd25f323662f50a47bb048be636160f2b7c135` and its umbrella pin update.
`git push origin main` completed once; `git ls-remote origin refs/heads/main` then confirmed the same full revision
on canonical `git@github.com:lebedenko/holonight-config.git`. Config's working tree is clean and its upstream is synchronized.
The gitlink now selects that published implementation revision. The preceding local handoff and the pinned local SPEC
retain their pre-publication evidence; this section supersedes their pending publication status.

Latest CI was queried once with
`gh run list --repo lebedenko/holonight-config --branch main --limit 1 --json headSha,status,conclusion,url,workflowName,createdAt`.
The returned Licensing run was created at `2026-10-12T16:43:50Z` and reports:

| CI revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `0ccd25f323662f50a47bb048be636160f2b7c135` | Licensing | in_progress | Pending (empty API conclusion) | [run](https://github.com/lebedenko/holonight-config/actions/runs/38279431526) |

No CI completion is claimed, and no polling or waiting was performed. The earlier documentation CI snapshot is historical.
Local acceptance remains the reviewed offline three-lane evidence in Config's SPEC. Shared tooling fixtures (32)
and installer fixtures (68) passed during adoption; generated installer profile drift and commit whitespace checks passed.
This handoff changes only Config's gitlink and this ledger. The umbrella checkpoint remains local; the initiative
remains Accepted and EDM-022 integration acceptance is still pending.

## EDM-005 approved publication and pin — 2026-10-12

User approved publication of the three verified System Services commits and its umbrella pin update:
`616501a` (formatting), `5a3a07f` (API-preserving static-analysis cleanup), and
`70614eb70329af7014853c2973e5624acf0b251e` (EDM-005 adoption).
`git push origin main` completed once; `git ls-remote origin refs/heads/main` confirmed the full adoption revision
on canonical `git@github.com:lebedenko/holonight-system-services.git`. Its working tree is clean and its upstream
is synchronized. The gitlink selects this published revision. This section supersedes the pinned local SPEC's
pre-publication pending status; its complete local acceptance evidence is retained without a documentation-only push.

All eight clean offline acceptance lanes passed: Full Debug with 195 backend tests and all three installed
consumers followed by Release without tests; Audio-only; Storage-only with a private D-Bus session; Compositor
with and without Wayland; Core-only without CTest; full format/strict tidy across 37 owned translation units;
and separate REUSE licensing. Launcher (4), dependency (5), and canonical external-tooling (21) regressions passed.
The final documentation licensing check also passed. Exact commands, package identities, feature switches,
complete-log review and documented informational/suppressed diagnostics are in the local SPEC.

Latest CI was queried once with
`gh run list --repo lebedenko/holonight-system-services --branch main --limit 1 --json headSha,status,conclusion,url,workflowName,createdAt`.
The returned Licensing run was created at `2026-10-12T18:10:35Z` and reports:

| CI revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `70614eb70329af7014853c2973e5624acf0b251e` | Licensing | in_progress | Pending (empty API conclusion) | [run](https://github.com/lebedenko/holonight-system-services/actions/runs/38289139967) |

No CI completion is claimed, and no polling or waiting was performed. Historical documentation CI results do
not verify this implementation. The checkpoint changes only System Services' gitlink and this coordination ledger;
existing untracked artifacts are untouched. The umbrella checkpoint stays local, the initiative remains Accepted,
and final ecosystem integration remains pending EDM-022. Bundle drift and commit whitespace checks pass.

## EDM-006 approved publication and pin — 2026-10-13

User approved publication of the three verified Qt commits and its local umbrella pin/handoff checkpoint:
`a173dc97317891a07ede5d5f6fcf4c7f0b42812e` (test lint cleanup),
`158476f01a6db5d7cea3c2b9fa76ddb113ccedbe` (QML binding cleanup), and
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68` (EDM-006 adoption).
`git push origin main` completed once; `git ls-remote origin refs/heads/main` confirmed the full adoption revision
on canonical `git@github.com:lebedenko/holonight-qt.git`. Qt's working tree is clean and its upstream synchronized.
The gitlink selects this published revision. This handoff supersedes the pinned local SPEC's pending publication
status while retaining its implementation and verification record without a documentation-only Qt push.

Local acceptance on 2026-10-12 passed all five qualified offline lanes: Full Debug (97/97 CTest entries), Minimal
(86/86), production Release build/install, canonical formatting and strict tidy across 76 owned translation units
with QML lint/import/qmltypes policies, and REUSE in its separate image. Applicable installed-package consumers,
syntax-enabled themes and syntax-disabled absence, unavailable Wayland requests, example startup tests and Qt5
probes passed. Launcher (5), dependency/cache (12) and umbrella tooling (32) regressions passed. Final review's
test variable-name correction passed focused tidy/build/smoke and formatting checks; final documentation REUSE
and diff checks passed. Complete logs, exact image/provider compatibility identities and hashes are recorded in
Qt's local SPEC and VERIFICATION.json. Existing shader/software, optional Kirigami Addons and explicit Fusion
GTest skips remain documented; no skip policy was added or broadened.

Latest CI was queried once with
`gh run list --repo lebedenko/holonight-qt --branch main --limit 1 --json headSha,status,conclusion,url,workflowName,createdAt`.
The returned Licensing run was created at `2026-10-12T21:12:26Z` and reports:

| CI revision | Workflow | Status | Conclusion | Run |
|---|---|---|---|---|
| `7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68` | Licensing | in_progress | Pending (empty API conclusion) | [run](https://github.com/lebedenko/holonight-qt/actions/runs/38309160449) |

No CI completion is claimed; no polling or waiting was performed. This checkpoint changes only Qt's gitlink and
this ledger, leaves every other work-package state unchanged and preserves existing untracked artifacts.
The umbrella checkpoint remains local, the initiative remains Accepted, and EDM-022 manual/final ecosystem
acceptance and Debian qualification remain deferred. Canonical bundle/declaration/profile and whitespace checks
pass; documentation-only handoff does not require repeating the unchanged application acceptance builds.

## EDM-007 accepted handoff — 2026-10-13

Adapters' audit baseline remains `95a9078e8d4f0b2d9c5a69ee6040388558eb9251`;
implementation started at confirmed canonical `37508f71ed37a16b824329c303083a08cf88aa2f`.
The local Ready checkpoint is `80e17e4`. Published providers used for acceptance:
Config `0ccd25f323662f50a47bb048be636160f2b7c135`, System Services
`70614eb70329af7014853c2973e5624acf0b251e`, and Qt
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68`.

Fixture cleanup `0b8efad` and adoption `810a61dad372f5b9c1abfe9fd56a7b72ea81c28e`
were published together in one push to canonical
`git@github.com:lebedenko/holonight-appearance-adapters.git` `main`.
`git ls-remote origin refs/heads/main` confirmed the exact published adoption revision;
the Adapters working tree is clean and synchronized with origin/main. The gitlink
selects this published revision. This umbrella checkpoint remains local.

Local acceptance used the qualified EDM-024 full Arch image
`ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`
and the retained separate REUSE image. Explicit preparation exported the exact provider
revisions from local checkouts and installed them through `task deps PRESET=test` with
canonical options and Debug preparation. Provider source/toolchain/package/option
identities were recorded and checked; incompatible preparation was archived.
All acceptance containers used `--pull=never --network=none`, read-only prepared
inputs, host UID/GID and isolated runtime directories.

`python3 scripts/ci/run.py` performed clean acceptance. After fixture/static-only
corrections, `python3 scripts/ci/run.py --lane static --lane full --lane minimal --lane licensing`
reran affected lanes; the unaffected Release result was retained. Full passed 11/11
CTest entries, Minimal passed 8/8, and both retained all 14 GTest cases, CLI contracts,
GTK/labwc behavior, rollback/recovery and canonical-document mutation checks.
Release build/install, staged install/uninstall and non-installed probes, isolated
GTK majors/linkage, canonical formatting, strict tidy across all 15 owned units and
included fragment, REUSE, 6 launcher and 16 dependency regressions passed.
Complete log locations, toolchain/package identities, expected private-Qt/Xvfb notices
and preparation corrections are recorded in the local SPEC. Canonical declaration
comparison, `python3 tooling/sync.py --check --module holonight-appearance-adapters`,
`python3 tooling/generate-install-profile.py --check`, shell syntax and final diffs passed.

Latest available CI was queried once using `gh run list --branch main --limit 1`:
[CI run 38318125058](https://github.com/lebedenko/holonight-appearance-adapters/actions/runs/38318125058),
revision `810a61dad372f5b9c1abfe9fd56a7b72ea81c28e`, created `2026-10-12T22:41:53Z`,
status `completed`, conclusion `failure`. Its failure log shows the preparation pull
of the qualified GHCR image was rejected as `unauthorized`; no hosted provider or
Adapters build ran. This is recorded as a failed hosted check, not acceptance success.
No polling or CI completion wait was performed, and no additional implementation
push was made.

Registry follow-up on 2026-10-13: after the owner changed package visibility, a fresh
anonymous GHCR manifest request returned HTTP 200 and the exact qualified digest
`sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`.
The failed job was rerun with `gh run rerun 38318125058 --failed`. A single subsequent
status query recorded attempt 2 at the same implementation revision as `in_progress`,
with no conclusion yet. Hosted acceptance remains pending; no completion wait,
implementation change or additional publication push was performed.

CI closure: attempt 2 of run `38318125058` completed with `success` at
`810a61dad372f5b9c1abfe9fd56a7b72ea81c28e`. The original failure and pending
query above remain historical evidence.

EDM-008 is Ready at canonical Icons baseline
`7684b021a5b74c7d4e34b7dd05bb3bdd02456473`. Only EDM-007 changes to Done. The initiative remains Accepted; Debian qualification,
manual ecosystem acceptance and final integration remain deferred. Other work-package
states and existing untracked umbrella artifacts are unchanged. The umbrella checkpoint
must not be published as part of this handoff.

## EDM-008 accepted handoff — 2026-10-13

Icons adopted external dependency management from canonical implementation baseline
`7684b021a5b74c7d4e34b7dd05bb3bdd02456473`. Its local SDD preserves audit baseline
`a8debec1399b59c218b2faa8f54047e5d3bc7984` and records the complete contract, file
changes, environment identities and acceptance:
[SPEC](../../../holonight-icons/docs/sdd/external-dependency-management/SPEC.md) and
[structured evidence](../../../holonight-icons/docs/sdd/external-dependency-management/verification/acceptance.json).

Separate Icons commits, published together in one completed push to canonical origin/main:

- `647fbe5`: behavior-preserving canonical formatting and tidy cleanup for the two C++ tools.
- `b1ee3e7b9e804542e22c8eebd3946eb9c04138bb`: explicit dependency/fixture preparation,
  installed-prerequisite validation, offline CI lanes, regressions and contributor/SDD evidence.

`git -C holonight-icons ls-remote origin refs/heads/main` confirmed the exact published
implementation revision before pinning. The Icons checkout is clean. Canonical module
JSON/CMake declarations and bundle 2.0.0 are byte-identical locally; production installer
profiles exclude Qt/GTK/rendering/font/Xvfb/KDE test prerequisites. No GTest is required.
Generation, staging, artwork, metadata, aliases, payload, recovery and assertions are preserved.

The prepared fixture is the actual Qt renderer cpp/header from
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68`, with exact hashes in the local SDD evidence.
Local `task deps` requires explicit `HOLONIGHT_QT_SOURCE`; ordinary rendering consumes
only the validated prepared fixture. CI `--prepare` acquires images/that exact revision
explicitly and invokes `task deps`. Acceptance starts no containers without compatible
preparation, uses `--pull=never --network=none`, read-only inputs, the caller account and
private runtime directories. Incompatible artifacts are archived; supplementary package
downloads, root bootstrap and acceptance-time provider acquisition are retired.

The accepted build image is
`ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`;
licensing retains its separate pinned REUSE image. Qualified versions: GCC 16.2.1,
CMake 4.4.3, Clang 22.1.8, Python 3.14.7, Qt Core/Gui/Svg 6.11.2,
GTK3 3.24.52, GTK4 4.22.5 and REUSE 6.2.0.

Local verification:

- `python3 scripts/ci/run.py --prepare --qt-source ../holonight-qt`: pass.
- Clean `python3 scripts/ci/run.py`: verification, licensing, minimal, release and static pass
  at `build/ci/20261013T081036Z-qqve3cdb`; complete logs inspected.
- Verification/minimal each pass all 47 existing Python tests. Actual Qt rendering passes
  282 masters at 12 sizes/scales and four palettes; temporary inherited Places/Actions
  checks pass all 11 sizes at 1x/2x. GTK3/GTK4 each pass 174 symbolic lookups/two-color
  renders per theme. Preview generation passes.
- Canonical format passes for both owned C++ tools; strict tidy passes for the enabled Qt
  tool. Release staging validates both themes/template bundle and excludes compiled tests.
  Four REUSE roots pass. Existing rollback, recoloring, staging and installed-command
  recovery coverage remains intact; 56 assertion diagnostic texts preserve their order.
- Eight launcher and initially ten dependency regressions pass in clean acceptance.
  Explicit missing-GTK-package coverage was then added; all eleven dependency tests pass
  both locally and in the same offline immutable image. Unchanged application acceptance
  was not repeated. Total final focused regressions: 19.
- Documentation/artifact-upload closure: workflow YAML validated; four-root licensing rerun
  passes at `build/ci/20261013T081504Z-5_8m0v4t`. Declaration equality, bundle/profile drift,
  staged diffs and whitespace checks pass. Environmental notices and the preserved GTK4
  deprecated symbolic assertion are explained in the local SDD; owned compiler/tidy
  warnings are resolved.

A single latest-run query after publication recorded
[CI run 38369393516](https://github.com/lebedenko/holonight-icons/actions/runs/38369393516),
at revision `b1ee3e7b9e804542e22c8eebd3946eb9c04138bb`, attempt 1, status
`in_progress`, conclusion `null`. Hosted acceptance remains pending at the recorded query;
no live wait, polling, rerun or additional implementation push was performed.

Only EDM-008 changes to Done. The initiative remains Accepted. Debian qualification,
explicit native KDE execution (Qt >=6.11 and `KF6::IconThemes`, `VERIFY_KDE=OFF` by default),
manual ecosystem acceptance and final integration remain deferred. Other work-package
states and existing untracked umbrella artifacts are unchanged. This umbrella pin checkpoint
remains local and must not be published as part of this handoff.

## EDM-009 local completion — 2026-10-13

Images started from canonical origin/main `ce9bf6957f6efa51a3f5dbf9f51d95fb9b48cd6f`,
confirmed with `git ls-remote` and a clean checkout. Audit baseline `d834984dc413dc9e56f7f3157fa605d6a8667088`
remains historical. The local Ready checkpoint is `318ce54`.

Two verified Conventional Commits are local on Images main:

- `d84903464e6e9143c60444949a5c1f3e0acbd768`: API-preserving canonical static-analysis cleanup.
- `ae827d78db9cc21f9537c27f50f49baf879324da`: EDM-009 dependency tooling and qualified offline CI adoption.

Complete requirements, changed files, environment/package identities, commands, reviewed warnings and
acceptance are in the Images [SPEC](../../../holonight-images/docs/sdd/external-dependency-management/SPEC.md),
[acceptance reports/log hashes](../../../holonight-images/docs/sdd/external-dependency-management/verification/acceptance.json)
and [environment inventory](../../../holonight-images/docs/sdd/external-dependency-management/verification/environment.json).
Images has no internal providers or reduced-feature profile. Public declarations, package version 0.1.0,
`HolonightImages::Images`, exported Qt/EXIF/WebP interfaces, existing test assertions and fuzzing interfaces
are preserved. Supplemental downloads/extraction are retired; historical package evidence is retained.

`python3 scripts/ci/run.py --prepare` acquires the qualified EDM-024 full Arch and pinned REUSE images.
Compatible preparation is mandatory before every acceptance lane. All acceptance containers use
`--pull=never --network=none`, read-only source/preparation, caller UID/GID, rootless Podman mapping and
private runtime directories, with parallelism two. Actual Docker acceptance passed; real Podman execution
is not claimed.

Clean `python3 scripts/ci/run.py` passed all four lanes at
`build/ci/20261013T102018Z-x17x6m1i`: Release provider tests (all three CTest registrations and all 36
GTest cases, with no skips), installed-package consumer, SVG without image plugins, optional Clang fuzz
builds, Release staging/external-prefix consumer, canonical format/strict tidy over all ten owned units,
and REUSE. Eight launcher and eleven dependency regressions passed within acceptance.
Log review identified an inherited unused QML preset variable; after removing it and refreshing preparation,
affected release/static lanes passed at `build/ci/20261013T102409Z-3aqh6u2h`. Eleven dependency regressions
also passed with the final presets. Unaffected provider/fuzz acceptance was retained. Exact Release staging
contains nine expected files. Final documentation REUSE passes at `build/ci/20261013T102830Z-6y7cryqe`
(76/76 files). Complete logs were inspected; owned compiler/tidy warnings are resolved, with expected
malformed-input diagnostics, optional Vulkan discovery and targeted ABI/API/complexity annotations documented.
Canonical tooling's 32 fixtures, declaration equality, bundle/installer-profile drift, workflow YAML,
shell/Python syntax and whitespace checks pass.

Only EDM-009 changes to Done. Images is clean with two unpublished local commits; the umbrella gitlink
remains the published implementation baseline. Publication and pinning remain separate authorized handoffs;
no CI query, push or pin update is performed here. This ledger checkpoint remains local, unrelated untracked
artifacts are preserved, and the initiative remains Accepted. Thumbnails/downstream consumers, Debian
qualification, new fuzz campaigns and final manual ecosystem integration remain later work packages.

## EDM-009 publication and pin — 2026-10-13

User requested the Images pin. Its verified cleanup `d84903464e6e9143c60444949a5c1f3e0acbd768`
and adoption `ae827d78db9cc21f9537c27f50f49baf879324da` were published together in one push to
canonical `git@github.com:lebedenko/holonight-images.git` main, as the prerequisite for selecting a
published revision. `git ls-remote origin refs/heads/main` confirmed the exact adoption commit.
Images is clean and synchronized with origin/main. The umbrella gitlink now selects that revision.
This supersedes the local completion record and pinned SPEC's pending publication/pin status;
their complete local acceptance evidence is retained without a documentation-only Images push.

Latest CI was queried once with
`gh run list --repo lebedenko/holonight-images --branch main --limit 1 --json headSha,status,conclusion,url,workflowName,createdAt`.
The Build and checks run, created at `2026-10-13T10:43:31Z`, reports revision
`ae827d78db9cc21f9537c27f50f49baf879324da`, status `in_progress`, and an empty conclusion
(pending): [run 38385319992](https://github.com/lebedenko/holonight-images/actions/runs/38385319992).
No CI completion is claimed; no polling or waiting was performed.

Local verification remains the four-lane offline acceptance, affected release/static reruns,
3/3 CTest registrations and 36 provider cases, installed/external-prefix consumers, Clang fuzz
builds, format/strict tidy across ten units, REUSE, 19 module regressions and 32 canonical tooling
fixtures documented above. Canonical bundle/installer-profile drift and whitespace checks pass.
This checkpoint changes only Images' gitlink and this ledger, preserves unrelated untracked
artifacts and remains local. The initiative remains Accepted; later work-package states and
final ecosystem integration are unchanged.

## EDM-010 local completion — 2026-10-13

Ready checkpoint `91e3429` assigned only Thumbnails at canonical implementation baseline
`59fb2e92e8794e06db2ff8a1a6ec5cc1ebc66c03`, confirmed by a clean checkout and
`git ls-remote origin refs/heads/main`. Audit baseline
`2284b1822b0f8f856677e14d21d91e8fa10bd98c` remains historical.

Repository-local commits on main:

- `c6f40b441b83560fbd67d81aa9a6a22b786d7f4a`: behavior-preserving canonical C++ quality cleanup.
- `c9ae0ad9a64e8ce28ee669b5463ef1bec74bc16d`: EDM-010 installed dependencies and offline CI adoption.

The [local SPEC](../../../holonight-thumbnails/docs/sdd/external-dependency-management/SPEC.md)
records changed files, decisions, complete log review, initial failures and verification limits.
[Environment evidence](../../../holonight-thumbnails/docs/sdd/external-dependency-management/verification/environment.json)
and [acceptance evidence](../../../holonight-thumbnails/docs/sdd/external-dependency-management/verification/acceptance.json)
retain preparation identities, installed package/tool versions, log hashes and implementation hashes.
Qt >=6.11 Core/Gui, synchronous cache semantics, package 0.1.0, headers and
`HolonightThumbnails::Thumbnails` remain unchanged. GTest >=1.14 CONFIG is testing-only.

Explicit preparation passed at `build/ci/20261013T111731Z-czf2hazj` in Thumbnails.
Focused corrections were verified locally before one clean four-lane acceptance:
`python3 scripts/ci/run.py` passed at `build/ci/20261013T122552Z-hkum50st`.
All lanes run with --pull=never --network=none, read-only snapshot/preparation inputs,
caller UID/GID, private runtime/HOME/XDG directories and default parallelism two.
Qualified Arch digest is `sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`;
REUSE digest is `sha256:85462a75c0f8efda09ddd190b92816b70e7662577c8427429e11e1b9f25a992e`.

- Both Debug provider CTest registrations and all 11 cache cases pass without skips, retaining permission,
  corruption, cancellation, concurrency and cache-miss behavior.
- Eight launcher and eleven real dependency/cache regressions pass. These cover missing/stale/tampered
  preparation, incompatible evidence archival, snapshots, offline/rootless mappings, failure propagation,
  unavailable/incompatible Qt/GTest, explicit prefixes/spaces, cache reuse/invalidation, testing disabled
  without GTest and ordinary commands without acquisition/preparation.
- Release stages exactly eight expected files, installs a prefix containing spaces, and builds/runs the
  independent consumer in a build directory containing spaces.
- Canonical format and strict tidy pass across all three owned translation units. Public declarations
  match the baseline after stripping comments/whitespace; all 54 existing test/assertion macros remain.
- REUSE 6.2.0 passes. Final documentation/evidence licensing passed separately at
  `build/ci/20261013T122903Z-1zvzwa10` (46/46 covered files).
- Canonical tooling's 32 fixtures, declaration JSON/CMake equality, bundle 2.0.0 drift,
  installer-profile consistency, Python/shell syntax, workflow YAML and whitespace checks pass.

Full logs were reviewed; no unresolved owned compiler/tidy diagnostics remain. Optional Qt Vulkan-header
notices are harmless for these CPU checks. Failed fake-runtime lanes are intentional launcher scenarios.
Real Docker acceptance is verified; real Podman execution and Debian qualification are deferred.

Only EDM-010 changes to Done. Thumbnails is clean with two unpublished local commits; the umbrella
pin remains `59fb2e92e8794e06db2ff8a1a6ec5cc1ebc66c03`. Publication and pinning require separate
handoffs, so no hosted CI result is claimed for these commits. The initiative remains Accepted.
Viewer, Files, final ecosystem integration and unrelated untracked umbrella artifacts remain outside this step.

## EDM-010 publication and pin — 2026-10-13

After user authorization, both verified Thumbnails commits were published together in one push to
canonical `git@github.com:lebedenko/holonight-thumbnails.git` origin/main. `git ls-remote origin
refs/heads/main` confirms `c9ae0ad9a64e8ce28ee669b5463ef1bec74bc16d`; the earlier separate cleanup
commit `c6f40b441b83560fbd67d81aa9a6a22b786d7f4a` is its parent. Thumbnails is clean and synchronized
with origin/main. The umbrella gitlink now selects the published adoption revision.

The latest available CI run was checked once at the pinned revision:
[Build and checks, run 38398351495](https://github.com/lebedenko/holonight-thumbnails/actions/runs/38398351495),
head `c9ae0ad9a64e8ce28ee669b5463ef1bec74bc16d`, status `in_progress`, conclusion empty (pending).
No hosted success is claimed and no CI wait/poll was performed. This publication section supersedes
publication/pinning-pending statements in the historical local completion and pinned local SPEC.

Local acceptance remains the clean four-lane offline run recorded above: both CTest registrations,
all 11 cache cases, Release installation/external-prefix consumer, canonical format/strict tidy across
three units, REUSE, 19 module regressions and 32 canonical tooling fixtures. Canonical bundle drift,
installer-profile consistency and whitespace checks pass at the published implementation.
This checkpoint changes only Thumbnails' gitlink and this ledger and remains local. The initiative
remains Accepted; Viewer, Files, final integration and unrelated untracked artifacts are unchanged.

## Next iteration: EDM-011 Search — Ready, 2026-10-13

The next iteration completes the remaining reusable provider adoption before Files (EDM-015).
Assign only `holonight-search`, work package EDM-011, from exact canonical origin/main
`993929cc717f3beaf99c60e01441dc3e86dfe7cf`. On 2026-10-13, `git -C holonight-search
ls-remote origin refs/heads/main` confirmed that revision and the checkout was clean at it.
Planning inspected Search's AGENTS.md, local SPEC, CMake/presets, Task commands,
launcher/workflow, dependency declarations, provider/consumer tests and benchmark comparison.
EDM-002 and EDM-024 are Done; Search has no internal source providers to prepare.
The initiative remains Accepted. Detailed implementation decisions, changed files and evidence
belong in Search's [local SPEC](../../../holonight-search/docs/sdd/external-dependency-management/SPEC.md).

Implementation sequence:

1. Update the local SPEC with this implementation baseline while preserving its historical audit
   baseline. Synchronize canonical bundle 2.0.0 and Search declarations. Preserve C++23,
   Qt Core >=6.11, package 0.1.0 and `HolonightSearch::Search`; require installed GTest >=1.14
   CONFIG for tests. Verify the declared Qt Test requirement against actual usage before
   settling declarations, and keep fzf exclusively in the test/benchmark profile.
2. Make `task deps` explicit prerequisite preparation/validation. Ordinary configure/build/test
   commands must not acquire packages or prepare sources. Support installed external prefixes,
   paths containing spaces and compatibility evidence; archive incompatible artifacts.
3. Adopt the qualified EDM-024 full image
   `ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`
   and the accepted separate REUSE image. Add explicit launcher preparation before acceptance;
   retain build-test and benchmark gates and add Release installation, canonical static checks
   and licensing. Acceptance uses `--pull=never --network=none`, read-only inputs, caller UID/GID
   and private runtime directories. Retire benchmark-time fzf download/extraction; use the
   qualified image's installed fzf and retain historical package evidence.
4. Verify focused launcher/discovery/cache regressions, then run one clean acceptance and review
   complete logs. Record preparation identities, versions, options, commands and limitations in
   the local SPEC and structured evidence. If canonical formatting/tidy requires broad cleanup,
   keep behavior-preserving cleanup separate from dependency adoption.
5. Commit only verified Search work using Conventional Commits. Publication and umbrella pinning
   remain separate authorized handoffs. After publication, confirm the canonical revision and
   query latest CI once, recording its exact revision/status/conclusion/link without polling.

Acceptance must retain all provider CTest cases, an installed-package consumer and the representative
Release benchmark: two million records, the same complete candidate list for fzf, four existing
queries returning 80 hits, and all 20 fzf samples per query. Preserve the distinction between
provider warm-query timings and fzf ingestion/filter timings; record environment/version changes
without inventing a performance threshold. Test missing/incompatible Qt and GTest, testing OFF
without GTest, unavailable fzf in the benchmark profile, external prefixes/spaces, compatible cache
reuse and stale/tampered preparation rejection. Release staging must exclude tests/benchmark tools.
Canonical declaration/bundle/installer-profile checks, format, strict tidy and REUSE must pass.

Iteration completion means a clean, locally verified Search commit and reviewable handoff evidence;
it does not mean ecosystem integration. Files remains Planned until Search is published and pinned
and its own handoff is prepared. Viewer and Shell are eligible for separate future planning, but
are outside this iteration. Debian qualification, new ranking behavior, new fuzz campaigns and
manual ecosystem integration remain outside EDM-011.

This planning change marks only EDM-011 Ready. It performs no implementation, publication,
submodule pin update or CI query. Before an implementer starts, create the required local umbrella
checkpoint and provide its exact revision together with the Search baseline above.
