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
| EDM-008 | holonight-icons | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-icons/docs/sdd/external-dependency-management/SPEC.md) | Ready | — | Canonical implementation baseline `7684b021a5b74c7d4e34b7dd05bb3bdd02456473`; audit baseline retained in local SPEC; bundle 2.0.0 and qualified image accepted |
| EDM-009 | holonight-images | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-images/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `d834984dc413dc9e56f7f3157fa605d6a8667088`; implementation awaits handoff |
| EDM-010 | holonight-thumbnails | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-thumbnails/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `2284b1822b0f8f856677e14d21d91e8fa10bd98c`; implementation awaits handoff |
| EDM-011 | holonight-search | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-search/docs/sdd/external-dependency-management/SPEC.md) | Planned | — | Baseline `26067775e2eac3d9a779b3114dfbddc96834c7de`; implementation awaits handoff |
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
