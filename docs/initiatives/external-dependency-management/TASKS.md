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
| EDM-011 | holonight-search | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024 | [SPEC](../../../holonight-search/docs/sdd/external-dependency-management/SPEC.md) | Done | `5e71fd7c6494084b4fcc1b5b7a8df9bb2e690bdc` | 2026-10-13: bundle 2.0.0, installed GTest CONFIG, explicit preparation and qualified five-lane offline CI adopted; all six provider tests, Debug/Release installed consumers, full two-million-record benchmark, Release staging, format/strict tidy across four units and REUSE pass locally; 20 module + 32 canonical tooling regressions pass; separate cleanup/adoption commits published together to canonical origin/main and pinned locally; latest CI Build and checks attempt 1 in_progress, no conclusion, run 38409565751 at this revision; full evidence in local SPEC and handoff below |
| EDM-012 | holonight-shell | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-005, EDM-006 | [SPEC](../../../holonight-shell/docs/sdd/external-dependency-management/SPEC.md) | Done | `5d02583a59ed1bf9bff494c667ad6896d5fdce6e` | 2026-10-14: local bundle 2.0.0 and qualified offline Arch adoption verified; baseline `27567a918aae67ad43dba0e813b3f40ed14e539b`; clean Debug 1,157 CTest registrations with zero failures, Controls/runtime, standalone config package, Release staging, strict format/tidy across 244 owned units plus consumer, QML/architecture/REUSE and focused regressions pass; separate cleanup `19b1640`; published to canonical origin/main and pinned; latest CI in_progress, conclusion empty (pending), run 38546762318; publication handoff below |
| EDM-013 | holonight-settings | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-005, EDM-004, EDM-006, EDM-012 | [SPEC](../../../holonight-settings/docs/sdd/external-dependency-management/SPEC.md) | Done | `efc27a753b3e9de37b76aacf56617002ec7a1bda` | Audit baseline `6ec7a402ebc319f9a925fdf97d8e0382e0c1ef42`; implementation baseline `b99c2fcc97a2d7e7c6f6f48f087cdb9fd1536452`; bundle 2.0.0, ordered explicit providers and four qualified offline lanes pass; 86 CTest registrations with no skips, strict tidy across 28 owned units including consumer, Release/startup/QML/REUSE and focused regressions pass; cleanup/adoption plus verified Licensing acquisition correction published to canonical origin/main and pinned; latest Licensing CI in_progress, conclusion empty (pending), run 38565331629; evidence in local SDD and handoff below |
| EDM-014 | holonight-viewer | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-006, EDM-009, EDM-010 | [SPEC](../../../holonight-viewer/docs/sdd/external-dependency-management/SPEC.md) | Done | `90ca5b0f007e76aaf0caa12628ab079811c905f9` | 2026-10-14: bundle 2.0.0, explicit ordered providers and all three qualified offline lanes pass; standard and sanitizer CTest 27/27, strict tidy across 64 owned units, isolated installed runtime, metadata/GIO/QML/REUSE and focused regressions pass; separate compatibility cleanup `b2aaa5f`; published to canonical origin/main and pinned; latest Build and checks CI in_progress, conclusion empty (pending), run 38580865404; full evidence in local SDD and handoff below |
| EDM-015 | holonight-files | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-005, EDM-006, EDM-009, EDM-010, EDM-011 | [SPEC](../../../holonight-files/docs/sdd/external-dependency-management/SPEC.md) | Done | `7de2d9961a0feea28e41f80c4e834542faf1fefa` | 2026-10-13: bundle 2.0.0, component-scoped installed dependencies and explicit qualified offline CI adopted; Core 2/2, Quick 4/4, full CTest 25/25 in both locales, mandatory namespace 16+3 without skips, strict tidy across 121 units, QML/REUSE/install and 13 runtime fixtures pass; separate cleanup d94aa52; published to canonical origin/main and pinned locally; latest CI Build and checks in_progress (pending), run 38457731671; complete evidence and retained limitations in local SDD |
| EDM-016 | xdg-desktop-portal-holonight | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-015, EDM-011, EDM-006 | [SPEC](../../../xdg-desktop-portal-holonight/docs/sdd/external-dependency-management/SPEC.md) | Done | `99b0eea555837932073b488d2a1ae9f66bb037ea` | Audit baseline `7f09d6bcef64086bf3c7eb8c4eee05017a6f2dae`; implementation baseline `926de7ccff8146235a014c52a8da890dcc3b0919`; 2026-10-14: bundle 2.0.0, ordered Config/Qt/Search/Files Core/Quick preparation and qualified offline CI adopted; CTest 2/2 (49 main passes + staged real activation), Release five-file staging, canonical format/strict tidy across 9 units, QML and REUSE pass; 15 dependency + 11 launcher + 32 canonical fixtures pass; separate cleanup `61d4ddf`; published to canonical origin/main and pinned locally; latest CI Build and checks queued (pending), run 38476779407; full evidence in local SDD |
| EDM-017 | holonight-ai | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-006 | [SPEC](../../../holonight-ai/docs/sdd/external-dependency-management/SPEC.md) | Done | `dab860496323d321709a675141d553958bddf968` | 2026-10-14: bundle 2.0.0, installed Qt/GTest/GMock and explicit Config/Qt preparation adopted; four qualified offline lanes pass, CTest 714/714, both style QML subsets 59/59, composer scales 1 and 1.25, build/installed startup, Release staging, strict tidy across 127 units, QML/REUSE and 27 focused regressions pass; separate compatibility fix `549ab34`; published to canonical origin/main and pinned locally; CI and Licensing in_progress, conclusion empty (pending), runs 38595038940 and 38595038661 at this revision; local SDD/evidence and publication handoff below |
| EDM-018 | holonight-pkg-manager | Adopt installed dependencies, explicit preparation and qualified CI | EDM-002, EDM-024, EDM-004, EDM-006 | [SPEC](../../../holonight-pkg-manager/docs/sdd/external-dependency-management/SPEC.md) | Ready | — | Implementation baseline `8042ed3890fc3bf226dc7d4c991459cd5c5599a2`; exact handoff below |
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

## EDM-011 Search publication and pin handoff — 2026-10-13

User authorized publication and pinning after local acceptance. Search's clean `main`
published both completed commits in one push: `56fa411` (behavior-preserving static-check
cleanup) and `5e71fd7c6494084b4fcc1b5b7a8df9bb2e690bdc` (dependency adoption).
`git -C holonight-search ls-remote origin refs/heads/main` confirmed the latter exact
canonical revision before pinning. The submodule working tree is clean.

Local verification: explicit preparation and all five clean offline acceptance lanes passed
at `build/ci/20261013T134825Z-tnsa2kj6`; all six provider tests, Debug/Release installed
consumers, complete two-million-record/four-query benchmark with 80 hits and 20 samples per
query, eight-file Release staging, canonical format/strict tidy across four owned units,
REUSE, 20 module regressions and 32 canonical tooling fixtures passed. Documentation closure
licensing also passed. Commands, versions, benchmark measurements, implementation/log hashes
and limits remain in Search's [local SPEC](../../../holonight-search/docs/sdd/external-dependency-management/SPEC.md)
and its verification JSON files. Declaration equality, bundle drift, installer-profile,
workflow syntax and whitespace checks passed; final committed implementation matches the
acceptance hashes. No application rebuild is required for this umbrella-only checkpoint.

One latest CI query after publication returned [Build and checks, run 38409565751](https://github.com/lebedenko/holonight-search/actions/runs/38409565751),
at exact revision `5e71fd7c6494084b4fcc1b5b7a8df9bb2e690bdc`, attempt 1,
status `in_progress`, conclusion empty (pending). No completion or success is claimed;
no polling or waiting was performed. Pinning proceeds as authorized independently of CI completion.

This local umbrella checkpoint changes only Search's gitlink and this ledger. EDM-011 is Done;
the initiative remains Accepted. Files still requires its own Ready handoff; downstream adoption,
Debian qualification and final ecosystem integration remain deferred. Unrelated untracked
umbrella files are preserved. The umbrella checkpoint is not published.

## EDM-015 implementation handoff — 2026-10-13

Assigned repository: `holonight-files`; exact confirmed `origin/main` baseline:
`b1022c9297712878114ba3d827f970d7b16f3ce6` (clean). Adopt bundle 2.0.0 and qualified
full Arch digest `sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`.
Use the published umbrella-pinned Config, System Services, Qt, Images, Thumbnails and Search revisions.
Preserve standalone Core/Quick, shared QMarkdown >=1.1, Storage enabled/Audio disabled,
all existing application/isolation/runtime gates and explicit preparation with offline acceptance.
Completion is locally verified and committed; publication and gitlink updates remain separate.
Only EDM-015 is made Ready. The initiative remains Accepted.

## EDM-015 local completion handoff — 2026-10-13

Files is clean on local `main` at `7de2d9961a0feea28e41f80c4e834542faf1fefa`, following
separate behavior-preserving consumer cleanup `d94aa5298d46394c1168c8568096be88279e81c5`.
Implementation starts from confirmed canonical `origin/main` baseline
`b1022c9297712878114ba3d827f970d7b16f3ce6`; Ready handoff checkpoint is
`5438cecea111cd54de33b6bdb1bf477555707811`. Original audit baseline remains in the local SDD.

Local acceptance covers installed dependencies, Core/Quick/full builds and consumers,
Debug/Release, both locale suites (25/25 registrations each), mandatory filesystem isolation
(16 worker + 3 window cases, no skips), canonical format/strict tidy across 121 owned units,
QML lint/import/metadata, REUSE, staged installation and installed desktop/runtime acceptance
with 13 healthy/fault fixtures. Twenty dependency, thirteen launcher, four tidy adapter,
one real-CMake provider preparation and thirty-two canonical tooling regressions pass.
Initial clean-run failures are preserved and corrected with focused incremental verification;
compatible compiler and provider artifacts are reused. Full log hashes, package/toolchain
versions, exact provider identities/options, runtime image ID, changed files and existing
native/performance/reserved-block probe skips are recorded in the Files-local
[SPEC](../../../holonight-files/docs/sdd/external-dependency-management/SPEC.md) and
[VERIFICATION](../../../holonight-files/docs/sdd/external-dependency-management/VERIFICATION.json).
No host isolation policy was installed and no new native/performance campaign was added.

EDM-015 is Done locally. The initiative remains Accepted; no downstream work package is
made Ready and no umbrella integration check is claimed. The Files gitlink remains
`b1022c9297712878114ba3d827f970d7b16f3ce6`. Neither Files commit nor this handoff is published;
canonical remote confirmation, one latest CI query and pinning remain later authorized steps.

## EDM-015 Files publication and pin — 2026-10-13

After user authorization, both verified Files commits were published together in one push
to canonical `origin/main`: cleanup `d94aa5298d46394c1168c8568096be88279e81c5` and adoption
`7de2d9961a0feea28e41f80c4e834542faf1fefa`.
`git -C holonight-files ls-remote origin refs/heads/main` confirmed the exact adoption revision.
The umbrella gitlink now selects this published revision; Files is clean and synchronized
with origin/main. This section supersedes the historical local completion and pinned local
SDD's pending publication/pin status, preserving their complete local acceptance evidence.

One latest CI query returned [Build and checks, run 38457731671](https://github.com/lebedenko/holonight-files/actions/runs/38457731671),
created `2026-10-13T19:48:09Z`, at `7de2d9961a0feea28e41f80c4e834542faf1fefa`:
status `in_progress`, conclusion empty (pending). No hosted success is claimed;
no CI wait or repeat query was performed.

EDM-015 remains Done and the initiative remains Accepted. No downstream package is made
Ready and no ecosystem integration is claimed. This umbrella checkpoint remains local;
unrelated untracked artifacts are preserved. Publication introduces no implementation
changes and does not invalidate the recorded local acceptance.

## EDM-016 Portal implementation handoff — 2026-10-13

Only EDM-016 is Ready. Assign Portal from clean, remotely confirmed canonical
`origin/main` baseline `926de7ccff8146235a014c52a8da890dcc3b0919`. Preserve its original
audit baseline. Use Config, Qt, Search and Files pins from umbrella checkpoint
`888ab1d758b7599b5870524c1dab890e5df0f7a0`. Adopt bundle 2.0.0, explicit ordered
provider preparation and qualified offline Arch acceptance. Preserve both CTest
registrations and real staged D-Bus activation. Record details in Portal's local SDD.
Completion requires local acceptance and repository-local commits. Publication and
pinning remain separate; the initiative stays Accepted. Fresh manual Wayland review,
broker/compositor integration, routing, Debian and native-probe shutdown follow-up
remain deferred.

## EDM-016 Portal local completion handoff — 2026-10-14

Portal is clean on local `main` at `99b0eea555837932073b488d2a1ae9f66bb037ea`,
following separate getter-annotation cleanup `61d4ddf`. Both commits remain local.
Canonical implementation baseline was remotely confirmed as
`926de7ccff8146235a014c52a8da890dcc3b0919`; original audit baseline is preserved.
Ready checkpoint: `26856ee`. Provider revisions are those pinned by
`888ab1d758b7599b5870524c1dab890e5df0f7a0`: Config, Qt, Search and Files.

Local acceptance: explicit final preparation reused all four compatible providers;
clean offline Debug, static/QML and licensing lanes passed at
`build/ci/20261013T215358Z-z4iaztex`. Release was rerun cleanly at
`build/ci/20261013T215653Z-h4k16c54` after correcting only the payload checker to
parse the existing quoted D-Bus Exec value. All four lane results pass; the original
Release failure and the exact between-snapshot hash difference remain recorded.
Documentation-only REUSE closure passed at `build/ci/20261013T220010Z-_84poim4`.
UTC log timestamps correspond to the local verification date above.

Both CTest registrations pass: main suite 49 passed/zero failed with the preserved
activation-only skip, staged real D-Bus activation three passed/zero failed/skipped.
Fifteen real-CMake discovery/cache regressions, eleven launcher regressions and
thirty-two canonical tooling fixtures pass. Release installs exactly five production
files. Canonical format/strict tidy across all nine owned units, QML format/imports/
metadata/lint, REUSE, declaration equality, bundle drift, installer-profile consistency,
Python/shell/YAML syntax and whitespace checks pass. Provider identities/options,
image/tool versions, implementation/log hashes, warnings and limitations are in
Portal's [SPEC](../../../xdg-desktop-portal-holonight/docs/sdd/external-dependency-management/SPEC.md)
and [VERIFICATION](../../../xdg-desktop-portal-holonight/docs/sdd/external-dependency-management/VERIFICATION.json).
The canonical Portal declaration now explicitly enables Files Quick and disables
Files tests/application; its repository-owned copy matches exactly.

EDM-016 is Done locally; the initiative remains Accepted. The umbrella gitlink stays
at `926de7ccff8146235a014c52a8da890dcc3b0919`. Publication, canonical remote confirmation,
one latest CI query and pinning remain separate authorized handoffs. Fresh native
Wayland/compositor/broker review, routing, Debian qualification and the existing
native-probe shutdown follow-up remain pending/outside this iteration. No integration
check or hosted CI success is claimed; unrelated untracked artifacts are preserved.

## EDM-016 Portal publication and pin — 2026-10-14

After user authorization, both verified Portal commits were published together in
one push to canonical `origin/main`: getter cleanup `61d4ddf` and dependency adoption
`99b0eea555837932073b488d2a1ae9f66bb037ea`.
`git -C xdg-desktop-portal-holonight ls-remote origin refs/heads/main` confirmed the
exact adoption revision before pinning. Portal is clean and synchronized with
origin/main. The umbrella gitlink now selects that published revision.

One latest CI query returned [Build and checks, run 38476779407](https://github.com/lebedenko/xdg-desktop-portal-holonight/actions/runs/38476779407),
created `2026-10-13T22:17:32Z`, at
`99b0eea555837932073b488d2a1ae9f66bb037ea`, attempt 1, event `push`:
status `queued`, conclusion empty (pending). No hosted success is claimed;
no polling or waiting was performed. Pinning proceeds independently of CI completion
as authorized. UTC publication timestamps correspond to the local date above.

Recorded local acceptance remains valid: both CTest registrations and real staged
activation, Debug/Release, exact five-file production staging, 15 dependency + 11
launcher + 32 canonical regressions, canonical format/strict tidy across nine owned
units, QML/REUSE and declaration/bundle/profile/syntax/whitespace checks pass.
Detailed log and implementation hashes remain in Portal's local SDD/evidence.
Publication changes no implementation and requires no application rebuild.

This section supersedes publication/pinning-pending statements in the historical
local handoff and pinned SDD. EDM-016 remains Done and the initiative remains
Accepted. Fresh manual Wayland/compositor/broker review and ecosystem integration
remain pending. This checkpoint changes only the Portal gitlink and this ledger
and remains local; unrelated untracked artifacts are preserved.

## EDM-012 Shell implementation handoff — 2026-10-14

Accepted from umbrella `37dd9fe`. Assign Shell only at clean canonical baseline
`27567a918aae67ad43dba0e813b3f40ed14e539b`, using the published gitlinks for Config
`0ccd25f323662f50a47bb048be636160f2b7c135`, System Services
`70614eb70329af7014853c2973e5624acf0b251e` and Qt
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68`.

Only EDM-012 becomes Ready. The canonical Shell test declaration now includes QuickTest alongside Test,
as required by its existing QML harness. Adopt bundle 2.0.0 and the qualified full Arch image
`ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`.
Local automated acceptance is the gate; fresh user-operated desktop review remains for final integration.
No publication, system installation, Shell restart or gitlink update is authorized by this handoff.
Settings stays Planned, and the initiative stays Accepted. Implementation evidence belongs in Shell's local SDD.

Canonical follow-up: preserve Shell's existing explicit tidy compiler-database selection, scoped coverage validation,
single invocation per source and owned-header filter in bundle 2.0.0 before adoption. Existing Shell tidy
regressions cover the retained contract; this corrects a synchronization regression without changing application behavior.

Canonical template follow-up: retain Shell's already accepted Clang 23 trailing-comma policy for empty
argument braces when synchronizing the Qt tidy template. Other tidy checks remain strict; this preserves
the existing workaround instead of reversing it during dependency adoption.

## EDM-012 verified local Shell handoff — 2026-10-14

Shell completed at local `main` commit `5d02583a59ed1bf9bff494c667ad6896d5fdce6e`
(`build(deps): adopt qualified offline Arch acceptance`), following separate behavior-preserving
metadata cleanup `19b16401d337903d99e2afa3dc782ce9023a2a6e`
(`fix(qml): export complete model metadata`). Implementation baseline remains
`27567a918aae67ad43dba0e813b3f40ed14e539b`; Ready checkpoint `8f6ff94`, with canonical
corrections `d7c8104` and `a704462` recorded above. Shell is clean and its verified implementation
hashes match the committed files.

The final local command `JOBS=8 python3 scripts/ci/run.py` passed all four lanes in
`build/ci/20261014T085921Z-205uwj2o`: clean Debug/runtime tests, Release staging, strict static
checks and licensing. The 1,157 CTest registrations have zero failures; four duplicate standalone
private-bus skips remain, with those same four cases passing in the dedicated disposable-bus suite.
Controls acceptance passes 45 real frontend/style combinations plus three missing-module cases.
Standalone configuration-library build/install/consumption succeeds with provider sources hidden;
`HoloNightShellConfig::Config`, public headers and package layout are preserved. All 244 owned
translation units and the separate package consumer pass strict tidy; format, QML lint/policy/types,
architecture and REUSE pass. Focused checks: 12 launcher, 16 dependency, 2 tidy-context and 32 canonical
fixtures pass. Complete logs were reviewed; only expected Qt private compatibility notices,
negative-fixture diagnostics and existing suppressed external/NOLINT counts remain.

Exact image/toolchain identities, provider revisions/options, log hashes and retained skips are in
[Shell's local SDD](../../../holonight-shell/docs/sdd/external-dependency-management/SPEC.md) and
[verification record](../../../holonight-shell/docs/sdd/external-dependency-management/VERIFICATION.json).
Documentation closure passed REUSE, bundle/declaration/profile drift and whitespace checks.

EDM-012 is Done locally. This checkpoint publishes nothing and changes no gitlinks. Settings remains
Planned until Shell is published and pinned through a separately authorized handoff. The initiative
remains Accepted; fresh user-operated desktop review belongs to final integration. Unrelated untracked
initiative and packaging artifacts are preserved.

## EDM-012 Shell publication and pin — 2026-10-14

After user authorization, both verified Shell commits were published together in one push to
canonical `origin/main`: metadata cleanup `19b16401d337903d99e2afa3dc782ce9023a2a6e` and
adoption `5d02583a59ed1bf9bff494c667ad6896d5fdce6e`. `git -C holonight-shell ls-remote origin refs/heads/main`
confirmed the exact adoption revision before pinning. Shell is clean and synchronized with origin/main.
The umbrella gitlink now selects that published revision. This publication record supersedes the
historical pending-publication statements in the local acceptance SDD and preceding handoff.

One latest CI query returned [CI run 38546762318](https://github.com/lebedenko/holonight-shell/actions/runs/38546762318) at
`5d02583a59ed1bf9bff494c667ad6896d5fdce6e`: status `in_progress`, conclusion empty (pending).
No hosted success is claimed; no polling or waiting was performed. Pinning proceeds independently
of CI completion as authorized. The full recorded local acceptance remains valid; publication and
documentation closure do not require another unchanged application build.

EDM-012 remains Done, Settings remains Planned pending its own accepted implementation handoff,
and the initiative remains Accepted. Fresh user-operated desktop review remains part of final
integration. Only the Shell gitlink and this umbrella ledger are updated; unrelated untracked
initiative and packaging artifacts are preserved.

## EDM-013 Settings implementation handoff — 2026-10-14

Accepted from umbrella `e3eae422d2744c13fb9ed84c7542060ecd859452`. Only EDM-013 becomes Ready.
Settings implementation baseline is `b99c2fcc97a2d7e7c6f6f48f087cdb9fd1536452` on canonical origin/main;
the original audit baseline remains unchanged. Prepare published providers in order: Config
`0ccd25f323662f50a47bb048be636160f2b7c135`, System Services
`70614eb70329af7014853c2973e5624acf0b251e`, Qt
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68`, then Shell's standalone config export at
`5d02583a59ed1bf9bff494c667ad6896d5fdce6e`. Preserve Audio and Qt Wayland features.

Adopt bundle 2.0.0 and qualified full Arch image
`ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`.
Canonical declarations include all test Qt components even with BUILD_APP=OFF and installed libpulse/toml++
requirements exposed by provider exports. Require Qt >=6.11 and installed GTest >=1.14 CONFIG with GMock.
Preserve existing presets, CTest/runtime/startup coverage, installation and strict static checks.
Four offline automated lanes gate local completion; user-operated desktop review belongs to EDM-022.
Implementation and evidence belong only in Settings. Publication and pinning require separate handoffs;
the initiative remains Accepted. Unrelated umbrella artifacts are preserved.

## EDM-013 Settings publication and pin — 2026-10-14

Settings completed local implementation from `b99c2fcc97a2d7e7c6f6f48f087cdb9fd1536452` using
Ready checkpoint `ca8f7b829f85ca65f76c6061aadb3a362cbefaeb`. After user authorization, cleanup
`b82b14f` and adoption `49728a88c34b1edb211dbfb2c31d64c51f5d4118` were published together to
canonical origin/main. Four qualified offline lanes pass locally: all 86 CTest registrations with no
skips, installed configuration-package consumers with provider sources unavailable, Release staging
and all four installed startup modes rejecting preparation-QML fallback, strict tidy across 28 owned
sources including the separate consumer, format, QML lint/import/metadata and REUSE. Final Debug
also verifies Audio page selection, BUILD_APP OFF tests ON/OFF builds and coverage configuration.
Focused verification passes 12 launcher, 16 real-CMake, 2 tidy-context and 32 canonical fixtures.
Complete logs, exact identities/options/hashes, diagnostic review and verification reuse are recorded
in [Settings SPEC](../../../holonight-settings/docs/sdd/external-dependency-management/SPEC.md) and
[VERIFICATION](../../../holonight-settings/docs/sdd/external-dependency-management/VERIFICATION.json).

One latest CI query at the initial publication returned completed/failure
[Licensing run 38565122031](https://github.com/lebedenko/holonight-settings/actions/runs/38565122031).
The failure log identified a missing pinned REUSE image on the fresh runner; the offline launcher
correctly refused an implicit pull. A separate correction adds explicit pinned-image acquisition before
the offline Licensing lane. The exact acquisition/offline-lane sequence passed locally, with YAML,
image equality and whitespace checks. This concrete post-publication failure justified one additional
implementation push; unchanged application builds were not repeated.

Correction `efc27a753b3e9de37b76aacf56617002ec7a1bda` is published to canonical origin/main.
`git -C holonight-settings ls-remote origin refs/heads/main` confirmed this exact revision before pinning;
Settings is clean and synchronized with origin/main. The umbrella gitlink now selects it.
One latest query at this corrected revision returned
[Licensing run 38565331629](https://github.com/lebedenko/holonight-settings/actions/runs/38565331629),
status `in_progress`, conclusion empty (pending). No hosted success is claimed, and no polling or
waiting for CI was performed. Pinning proceeds independently of CI completion as authorized.

EDM-013 is Done; the initiative remains Accepted. Fresh user-operated desktop review remains EDM-022.
This umbrella checkpoint changes only the Settings gitlink and this ledger and remains local.
Unrelated untracked initiative and packaging artifacts are preserved.

## EDM-014 Viewer implementation handoff — 2026-10-14

Accepted from umbrella `9aa9460751a05a27e662a8591c1fa3f10fbd9b99`. Only EDM-014 becomes Ready.
Viewer's clean canonical origin/main baseline is `74eee36c7484b37dcece55b5cdf71d84f21c93bb`;
the original audit baseline is preserved. Canonical remotes confirmed all revisions on this date.
Prepare Config `0ccd25f323662f50a47bb048be636160f2b7c135`, Qt
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68` with BUILD_WAYLAND=ON, Images
`ae827d78db9cc21f9537c27f50f49baf879324da`, then Thumbnails
`c9ae0ad9a64e8ce28ee669b5463ef1bec74bc16d`.

Canonical declaration corrections add directly exercised WebP encoding, GIO, metadata validators,
Task, format/tidy, REUSE and runtime image plugins. Codec implementation remains Images-owned.
The canonical Qt tool resolver preserves Viewer's library-tool precedence regression contract.
Adopt bundle 2.0.0 and the qualified full Arch digest `37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`.
Preserve all three lanes, presets, explicit tidy context and installed-runtime acceptance.
Local details/evidence belong to Viewer's SDD. Publication and gitlink updates are separate handoffs.
The initiative stays Accepted; other unfinished repository packages stay Planned; fresh native review is EDM-022.

## EDM-014 verified local Viewer handoff — 2026-10-14

Viewer is clean on local `main` at adoption commit `90ca5b0f007e76aaf0caa12628ab079811c905f9`
(`build(deps): adopt qualified offline Viewer acceptance`), following separate compatibility cleanup
`b2aaa5f5b019c59ce88ccb36f2c03532e6835f1a`
(`fix(build): preserve compatibility with qualified Qt and Clang`). Both commits remain local.
Implementation baseline was clean canonical `74eee36c7484b37dcece55b5cdf71d84f21c93bb`;
audit baseline remains `2b696a328ec109bd11fe6e1b67e37ea727c8bff5`.
Exact Ready checkpoint: `741e7e9ce6d180c89671b3111dc4be10832020ce`, following requested umbrella baseline
`9aa9460751a05a27e662a8591c1fa3f10fbd9b99`. Published Config, Qt (Wayland ON), Images and Thumbnails
revisions are the handoff revisions recorded above and in Viewer's evidence.

Final `JOBS=8 python3 scripts/ci/run.py` passes standard, sanitizer and licensing at
`build/ci/20261014T135150Z-mc5g60en`. Standard includes clean Debug/Release, all 27 CTest registrations,
private-bus portal tests, ten fractional-scale/theme separator combinations, Fusion controls, strict format/tidy
across all 64 owned sources, QML contracts, REUSE and staged installation. ASan/UBSan CTest passes 27/27;
complete test logs contain no sanitizer/leak reports, including expected-failure startup cases.
Main smoke runs 379 cases with 371 passing and eight retained opt-in/native-only skips, fully recorded locally.
The isolated installed-runtime image builds/runs offline without workspace mounts or development search paths;
format fixtures, qualification probe, CLI paths/recovery, GIO launch for seven formats and metadata validation pass.
The production executable and qualification-only probe staging boundaries are preserved.

Focused checks pass: 13 launcher, 3 tidy-context, 12 real-CMake dependency and 32 canonical tooling fixtures,
plus both corrected drag/drop cases. Declaration equality, bundle drift, generated installer-profile consistency,
Python/shell/YAML syntax and whitespace pass. All 68 umbrella installer fixtures pass in the qualified offline
container after correcting one stale fixture expectation: the canonical starting profile already required
QMarkdown 1.1, while the fixture still expected the old 1.0 range. No package contract is changed by that fix.
Documentation-only REUSE closure passes at `build/ci/20261014T141446Z-ma3xhh2f`; no unchanged application
acceptance is repeated. Complete logs, exact image/package/toolchain identities, provider options/source hashes,
389 accepted source hashes, artifact hashes, diagnostic review and retained skips are recorded in
[Viewer SPEC](../../../holonight-viewer/docs/sdd/external-dependency-management/SPEC.md) and
[VERIFICATION](../../../holonight-viewer/docs/sdd/external-dependency-management/VERIFICATION.json).
All accepted implementation files match the committed content; only SDD/evidence metadata changes after acceptance.

EDM-014 is Done locally. The initiative remains Accepted; other unfinished repository packages remain Planned.
The Viewer gitlink remains `74eee36c7484b37dcece55b5cdf71d84f21c93bb`. No publication, hosted CI query,
pin update or ecosystem integration is claimed. Publication of both Viewer commits together, canonical remote
confirmation, one current CI query and pinning remain separate authorized handoffs. Fresh user-operated desktop
review remains EDM-022. No host installation, restart, pointer/focus automation, Debian qualification or new native
performance campaign occurred. Unrelated untracked initiative/packaging artifacts are preserved.

## EDM-014 Viewer publication and pin — 2026-10-14

After user authorization, both verified Viewer commits were published together in one push to canonical
`origin/main`: compatibility cleanup `b2aaa5f5b019c59ce88ccb36f2c03532e6835f1a` and dependency adoption
`90ca5b0f007e76aaf0caa12628ab079811c905f9`.
`git -C holonight-viewer ls-remote origin refs/heads/main` confirmed the exact adoption revision before pinning.
Viewer is clean and synchronized with origin/main. The umbrella gitlink now selects this published revision.

One latest CI query at that revision returned
[Build and checks, run 38580865404](https://github.com/lebedenko/holonight-viewer/actions/runs/38580865404),
created `2026-10-14T14:28:45Z`, attempt 1, event `push`:
status `in_progress`, conclusion empty (pending). No hosted success is claimed; no polling or waiting
was performed. Pinning proceeds independently of CI completion as authorized.

Recorded local acceptance remains valid: standard and sanitizer CTest 27/27 each, isolated installed runtime,
strict tidy across 64 owned sources, QML/format/REUSE/staging, 13 launcher + 3 tidy-context + 12 dependency +
32 canonical regressions and 68 installer fixtures pass. Full identities, hashes, diagnostic review and retained
skips remain in Viewer's local SDD/evidence. Publication changes no implementation and does not require another
application build. This section supersedes pending-publication/pinning statements in the historical local handoff
and pinned SDD.

EDM-014 remains Done and the initiative remains Accepted. Other unfinished repository packages remain Planned;
fresh native desktop review and ecosystem integration remain EDM-022. This umbrella checkpoint changes only
the Viewer gitlink and this ledger and remains local. Unrelated untracked initiative/packaging artifacts are preserved.

## Planning handoff: EDM-017 AI — Ready, 2026-10-14 (historical)

Plan prepared from umbrella `16424f4e5e5936d39e6355cbcd39439375453c06` after Viewer's published
handoff. Assign only `holonight-ai`, work package EDM-017, at clean canonical origin/main
`0d8c54e166fb4e34ee1e496421c4bd98339a95c1`. Preserve the original audit baseline in the local
SDD. Canonical `git ls-remote origin refs/heads/main` confirmed AI and both providers on this date.
EDM-002, EDM-024, EDM-004 and EDM-006 are Done. Planning inspected AI's AGENTS.md, local SPEC,
CMake/test inventory, presets, Task commands, CI launcher/lanes/workflows and canonical declarations.
Detailed implementation decisions and evidence belong in AI's
[local SPEC](../../../holonight-ai/docs/sdd/external-dependency-management/SPEC.md).

Prepare providers in order: Config `0ccd25f323662f50a47bb048be636160f2b7c135`, then Qt
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68`. Qt must retain Controls and BUILD_WAYLAND=ON;
disable provider tests/demo/gallery for application preparation. Use bundle 2.0.0 and the qualified
full Arch image
`ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`,
plus the accepted separate pinned REUSE image. Record source revisions/content, compiler/Qt versions,
features, paths and preparation signatures; reuse provider artifacts only when those identities match.

Implementation sequence:

1. Update the local SDD with this handoff and implementation baseline. Audit direct declarations
   against actual build/test/tool/runtime use, including Task, format/tidy, REUSE, coverage-only gcovr,
   and helpers exercised by the CI lanes. Correct canonical declarations in a separate umbrella
   coordinator handoff if needed, then synchronize the standalone declarations and bundle.
   Preserve required libsecret-1 and md4c pkg-config discovery and KF6SyntaxHighlighting discovery.
   Require production Qt >=6.11 and installed GTest >=1.14 CONFIG with GTest::gtest/GTest::gmock;
   remove FetchContent and the network-required BUILD_TESTS description. Qt Test remains required
   when tests are enabled; the inspected C++ QML harness does not require adding QuickTest.
2. Make `task deps` the explicit preparation path. Normal configure/build/test/static commands
   validate installed prerequisites without source preparation or acquisition. Preserve all presets,
   C++23, coverage instrumentation and scoped tidy behavior. Refresh stale provider revision variables,
   the mutable-image tidy helper and contributor guidance, including AGENTS.md's outdated automatic
   preparation description. Keep internal-prefix isolation separate from external-prefix discovery.
3. Replace acceptance-time provider fetches and package bootstrap with explicit preparation before
   offline lanes. Preserve build-test, static-checks and licensing, adding clean Release staging to
   acceptance. Acquire both pinned build and licensing images explicitly on fresh hosted runners;
   run acceptance with --pull=never and --network=none, read-only inputs, caller UID/GID and private
   runtime directories. Retire or redirect obsolete project-image publishing/build entrypoints so
   active workflows and developer helpers use the same qualified contract.
4. Run focused launcher and real-CMake discovery/cache regressions first, then one clean acceptance
   and review complete logs. Record exact identities, commands, log/content hashes, warning review
   and limitations in the local SDD and structured verification evidence. Keep any broad
   behavior-preserving Qt/Clang compatibility cleanup separate from dependency adoption.
5. Finish with a clean, locally verified repository commit using Conventional Commits and a
   reviewable handoff. Publication and umbrella pinning remain separate authorized steps; after
   publication confirm canonical availability and query current CI once without polling.

Acceptance preserves all existing CTest registrations, domain/provider/persistence/credential tests,
canonical import/styling policy and fixtures, and isolated runtime Controls acceptance for Holonight
and Fusion. Retain composer checks at scales 1 and 1.25 and the existing style-specific QML subset.
Preserve application/rendering metatype extraction, merged metadata and singleton registration;
the test-double acceptance executable and generated module remain isolated from production resources.
Build-tree and installed startup must pass default, environment, command-line and external-config
style modes. Installed checks must reject preparation/build QML paths, retain relative installed
QML discovery and verify the configured D-Bus activation Exec path. Stage Release production payload
without tests or fixtures. Strict format/tidy, QML lint/types/policies and REUSE must pass.

Dependency regressions cover missing/old Qt and GTest, missing GMock, tests OFF without GTest,
missing libsecret/md4c/syntax packages, missing internal Controls/Wayland providers, internal/global
prefix leakage, external prefixes and paths with spaces, stale/tampered preparation rejection,
compatible reuse and feature/toolchain changes. Verify coverage configuration/instrumentation remains
usable without imposing a new coverage threshold. Declaration equality, bundle drift, generated
installer-profile consistency and Python/shell/YAML/whitespace checks gate closure.

Only EDM-017 is Ready. Package Manager, Greeter, Daemon and Hyprlock remain Planned for subsequent
individual handoffs; their dependencies are already adopted. EDM-022 remains Planned until all
repository adoptions are Done and published/pinned. Debian qualification, AI product changes,
live model-service calls and fresh user-operated desktop review are outside this iteration.
The initiative remains Accepted. This planning change modifies only the umbrella ledger and claims
no application build, hosted CI result, implementation, publication or gitlink update. Before assigning
implementation, commit a local umbrella planning checkpoint and supply its exact revision with the
AI baseline and work-package ID above.

## EDM-017 AI — published and pinned, 2026-10-14

Published the completed AI change to canonical `git@github.com:lebedenko/holonight-ai.git`,
`main` -> `origin/main`, in one push containing separate compatibility and adoption commits:

- `549ab344cac6f989e56b2404e49a69a1b4fede52`: align the square composer action with native text metrics while retaining
  all existing equality, geometry, accessibility and compact-mode assertions.
- `dab860496323d321709a675141d553958bddf968`: installed dependencies, bundle 2.0.0, explicit
  preparation, qualified offline CI and verification evidence.

Canonical `git ls-remote origin refs/heads/main` confirms
`dab860496323d321709a675141d553958bddf968`; AI is clean and the umbrella gitlink selects that
published revision. Declaration checkpoint `f6621567ddef06e14403a387c4bf99a5a6b679d6` remains
separate from AI implementation. Detailed decisions and commands are in the pinned
[local SPEC](../../../holonight-ai/docs/sdd/external-dependency-management/SPEC.md) and
[structured verification](../../../holonight-ai/docs/sdd/external-dependency-management/verification.json).
The local evidence's publication fields describe its pre-publication acceptance checkpoint;
this umbrella handoff records subsequent publication and pinning.

Local acceptance: clean four-lane run `20261014T151030Z-0d98xrcy`, `JOBS=8`, all lanes pass.
CTest 714/714; composer 4/4 for Holonight/Fusion at scales 1 and 1.25; each style QML subset
59/59; all four build-tree and installed startup selectors; separate Release/tests-OFF staging,
fixture exclusion, build/preparation path isolation and configured D-Bus activation pass.
Strict format/tidy (existing 127-unit target), QML lint/types/policies and REUSE pass, as do
12 launcher, 15 real-CMake, 21 canonical dependency and 11 canonical tooling regressions.
Coverage configuration and instrumented compilation pass without introducing a threshold.
Complete logs and hashes are recorded in AI's evidence; warning review retains provider Qt private
API notices, optional Vulkan absence and source-only QML fixture image diagnostics. Application
build/static logs contain no compiler/CMake warnings; production startup checks pass.
Final documentation-only REUSE checks pass for 508/508 files.

Current CI lookup at the exact published SHA (one corrected full-SHA lookup after the initial
short-SHA filter returned no matches; no completion polling):

| Workflow | Revision | Status | Conclusion | Run |
|---|---|---|---|---|
| CI | `dab860496323d321709a675141d553958bddf968` | in_progress | Empty (pending) | [38595038940](https://github.com/lebedenko/holonight-ai/actions/runs/38595038940) |
| Licensing | `dab860496323d321709a675141d553958bddf968` | in_progress | Empty (pending) | [38595038661](https://github.com/lebedenko/holonight-ai/actions/runs/38595038661) |

These pending runs are not claimed as passing verification. Pinning does not wait for CI.
EDM-017 is Done; the initiative remains Accepted. Package Manager, Greeter, Daemon and Hyprlock
remain Planned, and ecosystem/manual integration remains EDM-022. No host installation, application
restart, live model-service calls, Debian qualification or desktop automation was performed.
This umbrella checkpoint changes only the AI gitlink and this ledger and remains local.
Unrelated untracked initiative/packaging artifacts are preserved.

## Planning handoff: EDM-018 Package Manager — Ready, 2026-10-14

Assign only holonight-pkg-manager, EDM-018, at clean canonical origin/main
`8042ed3890fc3bf226dc7d4c991459cd5c5599a2`; retain audit baseline `879bea1f4b71a2ddf185f45fc2d3e153edc46ac5`.
Planning baseline is umbrella `37887fbd6dc182b39b9413b88e42fa94cd4a308b`. Canonical remote checks confirm
Package Manager and Config `0ccd25f323662f50a47bb048be636160f2b7c135`, then Qt
`7c3ce074a8c2e02e4ee8cad8cd19eb8627aa4f68`. EDM-002, EDM-024, EDM-004 and EDM-006 are Done.
Use bundle 2.0.0, qualified full Arch digest `sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`
and pinned REUSE. Keep Controls and Wayland ON; provider tests/demo/gallery OFF. Canonical declarations now
include Task, format/tidy, REUSE, ripgrep, private-bus/ldd helpers and coverage-only gcovr; package-manager
transitives remain separate. No qualified image change is needed: these packages are already in the accepted image.

Detailed implementation and evidence belong in the [local SPEC](../../../holonight-pkg-manager/docs/sdd/external-dependency-management/SPEC.md).
Adopt explicit task deps, installed Qt >=6.11/GTest >=1.14 with GMock, exact private Qt, and separate internal/external
prefixes; remove FetchContent. Preserve libalpm and ICU discovery, C++23, all presets, coverage and static checks.
Replace acceptance-time downloads with explicit preparation, then offline build-test/release/static/licensing lanes.
Retire obsolete project-image publication. Preserve all CTest, fixture-only file:// sync, private-bus service,
libalpm-free checks, layering/import policies, compiled Holonight/Fusion controls and view acceptance, all four
build/installed startup selectors and installed path isolation. Add clean Release/tests-OFF staging and verify
activation paths. No package transactions, host install, pointer/focus automation or Debian qualification.

Run focused launcher/discovery/cache regressions, then clean acceptance once; review complete logs and record
identities, source/artifact hashes, options, warnings and limitations locally. Separate broad compatibility cleanup
from adoption. Finish with a clean local Conventional Commit and coordinator handoff; publication and pinning remain
separate authorized steps. Other unfinished packages and EDM-022 remain Planned; the initiative remains Accepted.
This checkpoint changes only coordination/declarations/generated profiles; it claims no application verification.
