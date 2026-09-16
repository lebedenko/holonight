# Unified Qt Quick Controls and Third-Party Compatibility — Coordination Ledger

The initiative is Accepted following user scope approval on 2026-09-07. Discovery UQC-001 is complete and
UQC-002 settles the contract. UQC-101 is Done with its verified provider published and pinned.
UQC-103 settings and UQC-104 AI are Done with local acceptance and publication complete.
Supplemental UQC-107/UQC-108/UQC-109, UQC-105 package-manager and UQC-106 greeter are Done.
UQC-102 shell is Done with published local acceptance and green final-revision CI; UQC-201 is In Progress for automated integration and manual-kit work.

Current execution order and remaining gates: [current batch roadmap](BATCHES.md).
D01/D03/D04, A03 and the reported F06 sequence remain accepted. D02 Settings Weather and F07 both styles are accepted. The user confirms deliberate
Fusion session shutdown; missing numeric exit evidence remains documented. Batch 1
and Batch 2 are complete; A01/A02/A04 are accepted and saved process outcomes are
classified. Batch 3 rendering/background repairs are accepted; remaining diagnostic
and compatibility dispositions are in FINDINGS.md. Batch 5 is removed from scope;
UQC-209/UQC-210 are Superseded application-local follow-ups. Batch 7 preserves
already accepted shared-control work and existing HnAvatar use. Dated entries
below retain historical states; current rows and canonical findings take precedence.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| UQC-001 | `holonight-qt` | Complete provider/consumer audit, application evidence and coverage proposal | — | [SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/SPEC.md) | Done | `033d6001fd088a96ac6e4ff936b6bafcf6ab5d4c` | 2026-09-07: user approved full REVIEW; manual observations and isolated authentication recorded with explicit limits. Audit build, six layout/palette cases, three installed-fixture modes, Python syntax and whitespace pass. Canonical publication confirmed. |
| UQC-002 | umbrella | Accept shared contracts, target-app coverage, dependency order, integration gates, and published assignment baselines | UQC-001 | This initiative | Done | Acceptance checkpoint | 2026-09-07: user approved all nine additions, palette support, indicator geometry and explicit composition limits. Existing source inventory and all six published baselines rechecked; final manual/activation gates retained. |
| UQC-101 | `holonight-qt` | Implement accepted coverage and composite migration; provide policy checks, embedded-config example, installed-consumer tests, and aligned documentation | UQC-002 | [SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | Done | `50c59558bb3817f57a992dd72730dba141db1bc8` | 2026-09-08: full provider contract review complete; ten isolated cases plus Qt-default reference, password/hint/length coverage under both styles, DPR 1.0/1.25 rendering, installed/startup/palette/composite/policy checks and all 61 provider CTest entries pass. Canonical publication confirmed before pinning. Ecosystem-only gates remain UQC-201. |
| UQC-102 | `holonight-shell` | Migrate shell/authentication; verify activation propagation and distinguish configured selection from module loading in diagnostics | UQC-109, UQC-106 | [Record](../../../holonight-shell/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | Done | `1320f37093e2148a224a4e8fbfaf4ac1b536c6a8` | 2026-09-09: 1157/1157 local CTests, 45 build/relocated-install launch modes plus three missing-module cases, dual-style/DPR compiled/source/authentication coverage, wrapper/policy checks, format/tidy/lint/types/architecture/licensing pass with documented existing QML warnings. Final-revision CI 34355350981 passes build/test, static and licensing. Canonical publication confirmed before pinning. |
| UQC-103 | `holonight-settings` | Adopt namespaced runtime controls and embedded default; align instructions and contradictory contract tests | UQC-101 | [SDD](../../../holonight-settings/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | Done | `2508635351e4901e1b03daf62dbb8ef6538ffcc5` | 2026-09-08: 53/53 CTest entries, final 8/8 focused checks, HoloNight/Fusion actual-window acceptance and four build/four installed override modes pass. Formatting, tidy, QML lint/types, package/activation, syntax, links and whitespace pass. Implementation `d45141e`, documentation handoff and adapter-isolation follow-up published; canonical availability confirmed before pinning. |
| UQC-104 | `holonight-ai` | Adopt runtime controls and embedded default; align import checker and verify composite behavior | UQC-101 | [SDD](../../../holonight-ai/docs/sdd/unified-qtquick-controls/SPEC.md) | Done | Implementation `286df4791c651ab8842f0d8f278eac9d4f803b81`; published handoff in gitlink | 2026-09-08: 713 executed CTest passes, one opt-in Secret Service skip; 59/59 QML-related checks in each style; dedicated dual-style application acceptance; four build/four staged-install launch modes with implementation/plugin evidence and private-bus/XDG isolation; format, full tidy, QML lint/types, policy fixtures, activation-prefix, syntax, links and whitespace pass. See [local record](../../../holonight-ai/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md). |
| UQC-105 | `holonight-pkg-manager` | Adopt runtime controls and embedded default; verify independent launch and scrollbar behavior | UQC-107, UQC-108 | [Record](../../../holonight-pkg-manager/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | Done | `3686bd22a2478e174ba033636eb2e268aafbef5c` | 2026-09-09: all 98 CTests, 13 source QML tests per style, 18 compiled acceptance tests per style, eight isolated actual launches, format/tidy/lint/types/policy/syntax/links/whitespace pass. Final-revision CI 34278555864 (build/test and static) and licensing 34278555744 pass; canonical publication confirmed. Mockups unchanged. |
| UQC-106 | `holonight-greeter` | Adopt runtime controls and embedded default; verify pre-session startup and retain scaled ComboBox geometry | UQC-107, UQC-105, UQC-109 | [Record](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | Done | `b082d82636726fa1fc51178215a3e85d5bb8bbec` | 2026-09-09: 8/8 CTests (43 core tests per style, 9 GUI tests per style/DPR, 15 policy fixtures), all 8 build/install launch modes with host provider hidden, format/tidy/lint/types/install/syntax/links/licensing pass. Implementation CI 34292227990 and licensing 34292227948 pass; published final handoff confirmed. Final-revision checks recorded below. |
| UQC-107 | `holonight-qt` | Repair direct configuration linkage and verify a clean Release build with privately staged configuration | UQC-101 | [Record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | Done | `478ef7c40a22c7c3f7ea6f45d9205411b5504834` | Fresh Release with system configuration headers hidden; all 59 enabled CTests, format and focused tidy completed; workflow syntax and whitespace pass. Canonical publication confirmed. |
| UQC-108 | `holonight-ai` | Adopt the corrected published provider and confirm local acceptance and green remote CI/licensing | UQC-107 | [Record](../../../holonight-ai/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | Done | `b874334b20053f94f84fd9b4b1a0a7e0c7cc867a` | Local full suite, 59 QML checks per style with host modules hidden, eight isolated launches and static checks pass. Remote CI 34267789749 (build/test and static) and licensing 34267789698 are green. Canonical publication confirmed. |
| UQC-109 | `holonight-qt` | Fix empty icon-role QVariantList delegates blocking greeter acceptance | UQC-107 | [Record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | Done | `00e6e208b6c9b30d89b66ef3aeb4ef8175050764` | 2026-09-09: regression reproduced before fix; 59 provider CTests, both styles/DPRs, format, zero-warning QML lint and licensing pass. Canonical publication confirmed. Final CI 34288860789 and licensing 34288860847 pass. |
| UQC-201 | umbrella | Verify published clean pins, dependency-order checks, activation paths, and accepted third-party matrix under Hyprland and Sway | UQC-101–UQC-109; UQC-202/UQC-203 findings | [Evidence](INTEGRATION.md), [commands](COMMANDS.md), [manual kit](MANUAL.md) | In Progress | Assigned from `a26b4e537ea8105a991ec5f48e06e9fe7565dd72`; verification gitlinks at readiness `67a72a6` | 2026-09-09: fresh dependency-order full suites, current installed/relocated launches, static checks and licensing pass. Initial AI Fusion geometry and installer package-ownership failures are retained in evidence; UQC-202/UQC-203 repairs are Done. Fresh recheck at published handoff `730be06`: installer --check exits 0 and explicit Fusion selection passes 59/59 (15.37 s). Third-party bounded loading verified; subsequent focused manual acceptances are recorded in FINDINGS.md. Remaining ecosystem gates are retained in BATCHES.md. 2026-09-16: fresh dependency-order and installed acceptance pass at closure checkpoint `3fcbe9c`; [Batch 8 checklist/results](FINAL-ACCEPTANCE.md) and [first manual handoff](BATCH8-HANDOFF.md) govern remaining gates. |
| UQC-202 | umbrella | Verify installer Qt Wayland capabilities independently of package ownership | — (found during UQC-201) | [Design and evidence](UQC-202.md) | Done | `8af91cb173d6268e71ddb1b92afed8915a6ac658` | 2026-09-09: eight fixtures, syntax, licensing, whitespace and real installer --check pass. Installer CI 34380475124 and licensing 34380474984 are green. Canonical publication confirmed; original failure retained in INTEGRATION.md. |
| UQC-203 | `holonight-ai` | Accept native composer geometry under both styles against the integrated provider | UQC-202 (execution order) | [Supplemental SDD](../../../holonight-ai/docs/sdd/unified-qtquick-controls/UQC-203.md) | Done | Implementation `11b021a4bd86d07d283d1c89f6467c44a17628f3`; handoff `7e25e78cc7fb33aa63ed480bc3f328a65e04ca0c` | 2026-09-09: four style/scale composer cases, both 59-test selections, complete local suite/Task, compiled acceptance, eight launches, policies and static/licensing pass. Implementation CI 34390403485 and licensing 34390403390 green. Documentation-only handoff published and verified before pinning. |

| UQC-204 | `holonight-qt` | Shared form keyboard focus in HnSettingsRow and HnFormField | UQC-109; found during UQC-201 | [Local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-204.md) | Done | `65c806fb6a65cae9652dde7a69d595813973c1a9` (repair `e97b646`) | 2026-09-11: final regressions fail on baseline (7/8 per style/scale), pass after repair (8/8 × four); all 65 provider checks pass after correcting stale local patchelf path. Installed four-case matrix, QML/import checks, format, focused tidy and licensing pass. Canonical origin/main revalidated before pinning. Manual focus acceptance completed for F01/F02; see [canonical result](FINDINGS.md#manual-focus-acceptance--2026-09-11). F03 app-specific attribution remains unconfirmed. |
| UQC-205 | `holonight-shell` | A03 only: owned Polkit cancellation completion; A01/A02/A04 deferred after dropdown checkpoint | UQC-204 | [Local SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-205.md) | Done | `9a19a969b9ac7455e4947be40eecfaf1d25307a0` | 2026-09-11: baseline failure reproduced; typed cancellation error repairs actual D-Bus reply/requester exit. Final 1163/1163 tests, four authentication style/scale cases, static/install checks pass. Canonical publication and clean shell confirmed before pinning. 2026-09-12: [manual cancellation accepted](FINDINGS.md#manual-polkit-cancellation-acceptance--2026-09-12); A03 closed, other authentication findings deferred. |
| UQC-205-B2 | `holonight-shell` | A01/A02/A04 follow-up; preserve accepted A03 and Batch 1 | UQC-205, UQC-206, UQC-214 | [Follow-up SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-205.md#batch-2-follow-up--a01a02a04--2026-09-14) | Done | `fffb1715bac5a57127af5e671033ac33335ffc16` | 2026-09-14: real-model A02 failure and graphics-backed A04 clipping reproduced/repaired; A01 does not reproduce on current provider, no selector edit. 1171/1171 tests, four style/scale graphics runs, static/licensing and installed checks pass. Clean canonical publication confirmed. A01/A04 manually accepted; process outcomes classified and Batch 2 closed (see canonical findings). |
| UQC-206 | `holonight-qt` | Dropdown delegate, height-loop, dismissal and selection investigation/repair | UQC-205 A03 acceptance | [Provider SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-206.md) | Done | Repair `975bf09`; published provider handoff `68b7069` | Provider repairs published; D01/D03/D04 manually accepted. D02 Settings Weather manual result and completed diagnostic log accepted 2026-09-13; third-party warnings stay in UQC-201. |
| UQC-207 | `holonight-qt` | Shared rendering acceptance and remaining diagnostic classification | UQC-204 (repair order) | [Local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-207.md) | Done | `33d1d51b2f57b1a18fc8ef42ff077b6d62bc21ce` | Icons/menu/selection, Switch focus and dropdown backgrounds accepted. Busy-button focus is expected Qt behavior. Tokodon chevron deferred; ScrollBar lifecycle, historical Haruna crash and unclassified Fusion hover remain. See [current findings](FINDINGS.md#batch-3-dropdown-background-manual-acceptance--2026-09-14). Closure 2026-09-16: user-directed disposition; deferred historical findings are non-blocking, not fixed. See [canonical closure](FINDINGS.md#batch-3-user-directed-closure--2026-09-16). |
| UQC-208 | `holonight-qt` | Palette transitions and picker-state investigation | UQC-204 (repair order) | [Local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-208.md) | Done | Repair `5d3f06e`; documentation closure `638eec2` | 2026-09-15: P02 visually accepted in nine runs; all twelve raw runs pass hashes/exit/isolation review. P01 remains an external KDE/application defect with follow-ups. [Acceptance and limits](FINDINGS.md#batch-4-manual-visual-acceptance--2026-09-15). |
| UQC-209 | `holonight-settings` | Settings slider geometry investigation | — (removed from initiative) | Future repository-local SDD, outside UQC | Superseded | — | 2026-09-14 user scope correction: incorrect application layout, unrelated to shared-controls unification. Document and implement in a separate app-local follow-up session; not an integration gate. |
| UQC-210 | `holonight-ai` | Temperature row geometry | — (removed from initiative) | Future repository-local SDD, outside UQC | Superseded | — | 2026-09-14 user scope correction: incorrect application layout, unrelated to shared-controls unification. Document and implement in a separate app-local follow-up session; not an integration gate. |
| UQC-211 | `holonight-shell` | Fractional-scale shell stability and topbar rendering | UQC-204 (repair order) | [Local SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-211.md) | Done | `ab780d5d477400cdc70195d37783e9e080ee1d05` | 2026-09-15: S01 repaired-provider Hyprland checks pass in both styles at DPR 1.25; S02 scale-1 comparison already accepted. F05 remains open. |
| UQC-212 | `holonight-greeter` | Remaining greeter-specific keyboard/appearance verification and scoped repairs | UQC-204 (repair order) | [Local SDD](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-212.md) | Done | `b082d82636726fa1fc51178215a3e85d5bb8bbec`; canonical provider/configuration confirmed 2026-09-15 | Published clean handoff `abb1ecc`; [verification](FINDINGS.md#batch-7-greeter-implementation-and-verification--2026-09-15). [G01–G06 accepted](FINDINGS.md#batch-7-manual-acceptance--2026-09-15); G07 closed as not an issue; [fullscreen acceptance and closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16). |
| UQC-216 | `holonight-greeter` | G07 rendered investigation and bounded diagnostic kit; no speculative QML repair | UQC-212 | [Local SDD](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-216.md) | Done | `b7277a63625e07e74f491839ce5b5f6dd4dfdad6` | 2026-09-15: published clean diagnostic handoff; 8/8 CTests, four graphics cases, 16 launch modes and static/licensing checks pass. [Investigation](FINDINGS.md#g07-rendered-investigation-and-diagnostic-handoff--2026-09-15); [Manual diagnostic result](FINDINGS.md#g07-manual-diagnostic-result--2026-09-16): scale 1 fails, fractional passes; no kit repeats. G07 closed as not an issue; [fullscreen acceptance and closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16). Batch 7 closed. |
| UQC-217 | `holonight-greeter` | G07 exact-geometry reproduction and QtQuick ownership handoff | UQC-216 | [Local SDD](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-217.md) | Done | `501d50cf29e2c3adbf1df3c7048d2637bc9c6924` | 2026-09-16: published clean handoff confirmed on canonical main; all eight exact cases match manual scale behavior, including plain QtQuick TextInput. Preserved opt-in failure; 8/8 standard CTests, 4/4 normal graphics and static/licensing pass. [Ownership handoff](FINDINGS.md#g07-exact-geometry-reproduction-and-qtquick-handoff--2026-09-16). G07 closed as not an issue; [fullscreen acceptance and closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16). |
| UQC-218 | `holonight-greeter` | Transformed QtQuick caret diagnosis and bounded response-field layer evaluation | UQC-217 | [Local SDD](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-218.md) | Done | `20f788c4ae86926d8c940ec33229fca2ac3c1a55` | 2026-09-16: clean handoff published and confirmed on canonical main. Standalone source/pixel diagnosis; layer rejected for text softening despite eight visibility passes. 8/8 CTests, 4/4 normal graphics, static/lint/licensing pass. [Rejected experiment](FINDINGS.md#g07-qtquick-diagnosis-and-rejected-layer-candidate--2026-09-16). Production unchanged; G07 closed as not an issue; [fullscreen acceptance and closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16). |
| UQC-219 | `holonight-qt` | Batch 3 ScrollBar lifecycle and historical Haruna crash diagnosis; Fusion research gate owned by umbrella | UQC-207 retained evidence | [Local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-219.md); [research/evidence](UQC-219.md) | Done | `c9aacd8fc5a1c70e161c9df2ba0fadd4d282ecb6` | 2026-09-16: canonical publication and clean provider confirmed before pinning; 87/87 CTests including installed acceptance, 8 threaded style/DPR checks and static/licensing verification. No failing lifecycle regression or production repair; original crash trigger unresolved; both Fusion findings were research-pending at handoff. Superseded by [user-directed Batch 3 closure](FINDINGS.md#batch-3-user-directed-closure--2026-09-16): UQC-207 Done; these historical findings are deferred and non-blocking. |
| UQC-215 | `holonight-qt` | Repair layer-surface Qt logical coordinate conversion | UQC-211 evidence | [Package](UQC-215.md); [SDD](../../../holonight-qt/docs/sdd/layer-surface-logical-coordinates/SPEC.md) | Done | `0e0f92efe1517bc07c577299f07b51117f25f05a` | 2026-09-15: published provider repair; 4 real-backend scale combinations, 87 provider CTests, 164 shell and 11 AI hosting tests pass. S01 human repair acceptance passed in both styles. |
| UQC-213 | `holonight-qt` | F06 shared window input policy and owned hover rendering | UQC-206 sizing | [Provider SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-213.md) | Done | `2965d8dcd7d4f5a1361acfdab66688539e9c5d3e` (follow-up); original `4dfa803` | 2026-09-13: stationary-pointer scroll regression fails before repair; native delegate hover gating passes 8/8 focused and 73/73 full provider tests. Published origin/main revalidated. F06 reported Settings/greeter HoloNight sequence manually accepted 2026-09-13; see canonical findings. 2026-09-12: 73/73 provider CTests and final 11/11 focused/installed checks pass; canonical publication verified. The later reported HoloNight sequence acceptance supersedes the historical pending status. |
| UQC-214 | `holonight-shell` | F07 deliberate pointer selection in launcher | Published UQC-213 | [Shell SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-214.md) | Done | `f55cb5fc3b9ca7fd8f74f2b968836b5f36f9e235` | 2026-09-12: 1167/1167 local CTests, final four compiled input cases, QML lint/types and publication verified. F07 interaction manually passes both styles on 2026-09-13 with staged runtime verified; user confirms deliberate Fusion session shutdown (numeric exit unavailable). F07 accepted. |


Allowed states:

- `Planned`: defined, but dependencies or acceptance are not ready.
- `Ready`: may be assigned with an exact published baseline and repository-local requirements.
- `In Progress`: repository work has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Confirm each implementation commit
is available from the canonical remote before updating its gitlink. Make umbrella checkpoint commits after accepted
handoffs; implementers do not modify umbrella status or pointers.

Record commands, results, application and Qt versions, limitations, and the verification date in `UQC-201` before
marking it Done and setting the initiative status to Integrated. Historical survey observations do not satisfy that
final verification gate.

## Discovery continuation handoff — 2026-09-06

Provider documentation and collection fixture published first; canonical `origin/main` availability confirmed before
this gitlink update. This checkpoint accepts the partial discovery record, not UQC-002 scope or integration.

- Corrected stderr collection and bounded Haruna backtraces replace the earlier inference of pre-QML stalls:
  ordinary/private-bus runs both reach the event loop. All three desktop apps load staged HoloNight/Core modules.
- Separate installed consumer passes three modes and 18 type-origin checks plus library-origin assertions.
  Haruna's programmatic Fusion fallback is effective; its seek/volume painting remains application-owned.
- Matching NeoChat/Tokodon release startup and welcome/server sources are retrieved and referenced with hashes.
- Provider APPLICATIONS/DESIGN contain a provisional exact addition list and compatibility recommendations that
  preserve public composite APIs. No product implementation or public API changes are included.
- Manual Hyprland editing/navigation/scrolling/popups/visual states remain unobserved. Only the active user login
  is available; the existing authentication agent remains untouched. A separately prepared login and confirmed
  exclusive registration are required for the surveyed Qt agent prompt/cancellation evidence.
- Provider fixture build/checks, Python syntax, relative links and whitespace pass. Umbrella links and whitespace
  pass. No unrelated suites or UQC-201 integration checks are appropriate at this discovery checkpoint.

Resume with the [guided checklist](../../../holonight-qt/docs/sdd/unified-qtquick-controls/audit/CHECKLIST.md) and
[durable evidence](../../../holonight-qt/docs/sdd/unified-qtquick-controls/audit/EVIDENCE.md). UQC-001 stays In Progress,
UQC-002 stays Planned, initiative stays Draft. Stop for joint scope review; UQC-201 retains full Hyprland/Sway
activation and integration acceptance. Unrelated package-manager mockups and other checkouts are preserved.

## Scope-review preparation — 2026-09-07 (unpublished)

Reviewed the provider's existing continuation artifacts, including manual desktop observations, isolated agent
registration/prompt/cancellation evidence, and controlled geometry/palette comparisons. Authentication discovery
is complete according to the recorded user observations; the cancelled command's exact numeric exit was not
retained. Earlier missing-authentication statements above describe the published 2026-09-06 checkpoint.

Reconfigured and built the standalone audit in `/tmp/uqc-20260907-discovery-build`; the build passed, with CMake
warnings about unavailable Kirigami plugin link targets. All six `check-layout.py` characterization runs against
`/var/tmp/uqc-auth-test-20260907/prefix` passed, including runtime Kirigami loading. These reproduce existing behavior,
not acceptance of the defects. Current run logs: `/tmp/uqc-layout-itg2jcu2` (temporary).

The [provider scope review](../../../holonight-qt/docs/sdd/unified-qtquick-controls/REVIEW.md) is ready for joint
discussion of indicator geometry, palette authority, nine proposed controls and explicit composition limitations.
UQC-001 remains In Progress, UQC-002 Planned and the initiative Draft. Provider continuation files are still
uncommitted; this note does not accept a published handoff or update its pin.

## Accepted discovery handoff — 2026-09-07

Provider `033d6001fd088a96ac6e4ff936b6bafcf6ab5d4c` is committed, published on canonical `origin/main`, and clean.
The umbrella pin now accepts that discovery handoff. The preceding unpublished notes are historical. User approval
resolves the pending scope review; README's accepted-scope section is authoritative for UQC-002.

All five consumer checkouts still match their published discovery baselines. Package-manager's two unrelated
untracked mockups are retained; they do not change its source baseline or satisfy final clean-tree acceptance.
No UQC-201 checks have been run. Final runtime/manual coverage remains open.

## Provider geometry checkpoint — 2026-09-07

Published provider `22ded7815727ce483fd91e82a9cc04bfe252ec3b` contains the first UQC-101 implementation slice and its
local implementation ledger. Canonical `origin/main` was checked before pinning; the provider working tree is clean.
This checkpoint does not make consumers Ready: palette support, all nine additions, composite/runtime migration,
embedded defaults, policy and final installed/negative/rendering coverage remain provider work.

Verification: full provider build, five focused QML tests, 28/28 CTest entries, and whitespace checks passed.
The new geometry regression failed before the fix. Exact commands and work scope are in the local SDD; no live
application interaction or UQC-201 ecosystem checks were performed for this slice. Resume from the pinned revision.

## Provider palette checkpoint — 2026-09-08

Accepted the published palette slice from baseline `22ded7815727ce483fd91e82a9cc04bfe252ec3b`:

- `68b444b`: Quick style initialization, internal palette resolver and RGBA infrastructure test.
- `c368fd0`: standard-control palette adoption, composite appearance boundaries and acceptance fixtures.
- `bc3ed4a`: QWidget reload mask protection, hybrid fixture and implementation record.

Canonical `origin/main` was checked after publication and resolves to
`bc3ed4a0f8e6b9b0d3a3568b07c8c2905332e955`. The provider is clean; its gitlink is updated to that revision.
The [provider implementation record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
contains the mapping, regression evidence, exact commands and limits.

Verification: full provider build and all 46 CTest entries pass, including sixteen default-scheme fixtures,
black/white/black updates, inheritance/reset/isolation, disabled alpha, nested popup overrides, offscreen state
rendering, actual QWidget-style reloads, and staged-prefix HoloNight/Fusion/Haruna-style fallback and configuration
precedence fixtures. Loaded QML type and plugin origins are checked. Changed C++ formatting and whitespace pass.
The historical discovery characterization runner remains unchanged.

UQC-101 remains In Progress. The nine additions, runtime-import migration and executable defaults remain provider
work; UQC-102–UQC-106 remain Planned. NeoChat named-scheme observations and Hyprland/Sway acceptance remain UQC-201
ecosystem gates. No umbrella integration tests or desktop pointer/focus automation were performed. Unrelated
package-manager mockups are preserved.

## Provider nine-controls checkpoint — 2026-09-08

Accepted the provider slice from published `bc3ed4a0f8e6b9b0d3a3568b07c8c2905332e955` and umbrella checkpoint
`8099678`:

- `675240e`: ApplicationWindow, Label, ToolButton, ToolBar, ToolSeparator and MenuSeparator, with focused acceptance.
- `7d0c988`: Popup, MenuBar, MenuBarItem and effective Shadow overlays, with focused acceptance.
- `24220e9`: installed origins/fallback coverage, layout/state/overlay regressions and implementation documentation.

Canonical `origin/main` was checked after publication and resolves to
`24220e95a4ca612700e2fd2b0395f59a481144b6`. The provider is clean and its gitlink now records that revision.
The [provider implementation record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
contains the role contracts, changed files, commands, test results and limitations.

Verification: full provider build, focused palette/hybrid/staged-prefix checks, source/import policy checks,
all 46 provider CTest entries (7.92 seconds), C++ formatting and whitespace checks passed. All sixteen schemes,
new control type/delegate origins, HoloNight with Basic and Fusion fallback, explicit Fusion and the Haruna fixture
are covered. Dialog remains an unimplemented fallback sentinel. Historical discovery characterization is unchanged.

UQC-101 remains In Progress; composite runtime imports and executable defaults remain provider work. Consumers
UQC-102–UQC-106 remain Planned. NeoChat named-scheme observations and manual Hyprland/Sway acceptance remain
UQC-201 ecosystem gates. No umbrella integration checks, real-application acceptance or desktop pointer/focus
automation were performed. Unrelated package-manager mockups are preserved.


## Provider composite-runtime checkpoint — 2026-09-08

Accepted the provider slice from published `24220e95a4ca612700e2fd2b0395f59a481144b6` and umbrella
`b44340c169dd63073740efd088b76913b1353bd1`:

- `f32f5bb`: Templates-based Core HnLabel and straightforward composite runtime imports.
- `da470c5`: search/text/ComboBox compatibility, shared implementation-only popup geometry and initial regressions.
- `bd5f2f0`: separate-process and installed acceptance, scope-specific policy, typography/frame preservation and record.

Canonical `git ls-remote origin refs/heads/main` returned
`bd5f2f0f6844ec809b3fa80182a61493cf724c0a` after publication. The provider is clean and its gitlink records that revision.
The [provider implementation record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
contains the contracts, file changes, exact commands, results and limits.

Verification: full provider build; focused HoloNight/Fusion composite and Core-only fixtures; staged-prefix runs;
all 49 provider CTest entries (11.65 seconds); C++ formatting; import-policy positive/negative cases and whitespace
checks passed. All 26 public composites load. Runtime base/editor/popup/delegate/progress/scrollbar origins and staged
plugin paths are checked. Core stays independent of selected Controls. Both ComboBox variants retain 0.78/1.0/1.25
geometry near window edges and after ancestor movement, empty/long models, item limits, selection visibility and
unsupported-transform diagnostics. Editing, replacement slots, typography overrides, appearance reload and disabled
states are covered without desktop pointer/focus automation.

UQC-101 remains In Progress. Demo/gallery embedded defaults and import migration, remaining guide/policy alignment
and final provider acceptance are subsequent work. UQC-102–UQC-106 remain Planned, and UQC-201 remains Planned.
No umbrella integration or real-application/manual Hyprland/Sway acceptance checks ran. Unrelated package-manager
working-tree files are preserved.

## Provider executable-defaults checkpoint — 2026-09-08

Accepted published provider `82ccb126c2ad8f364f32e0ae3b1551040a6949cb` from provider baseline
`bd5f2f0f6844ec809b3fa80182a61493cf724c0a` and umbrella `8e3cc74ba44503efd610713dc539934bef55fcad`.
Canonical `git ls-remote origin refs/heads/main` returned that revision after publication. The provider is clean;
its gitlink now records the verified revision.

Both examples use namespaced runtime Controls and embedded, overridable HoloNight defaults. Error-state examples
use public composites, and gallery Switch sizing preserves HoloNight semantics without invalid Fusion properties.
Installed examples discover their own prefix without adding the build-tree QML path. Application policy covers
instances, fallback types, enums and attached properties; guides, local provider instructions and CI are aligned.

Verification: full provider build and all 59 CTest entries passed (43.15 seconds, Qt 6.11.2). Thirteen focused checks
passed again after final checker isolation changes (43.67 seconds). Actual build/installed executable launches
verify default selection, environment Fusion, command-line Fusion over environment HoloNight, external configuration,
resolved Button URLs, plugin paths and absence of QML diagnostics. Python syntax, C++ formatting, shell syntax,
changed guide links and whitespace pass. Exact commands, changed files and startup-check limitations are in the
[provider record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md).

UQC-101 remains In Progress. Resume with isolated missing-module/plugin/dependency and bad-case diagnostics,
competing-style/imperative-precedence/platform-theme-only fixtures and final provider acceptance. Consumers remain
Planned until that complete handoff. No UQC-201 integration or human-operated Hyprland/Sway acceptance ran. Unrelated
package-manager working-tree files are preserved.

## Final provider handoff and settings assignment — 2026-09-08

UQC-101 is Done. Provider `50c59558bb3817f57a992dd72730dba141db1bc8` (`test(qml): complete isolated UQC-101 provider acceptance`)
was published from baseline `82ccb126c2ad8f364f32e0ae3b1551040a6949cb` and the provider worktree is clean.
`git -C holonight-qt ls-remote origin refs/heads/main` returned the new revision after push and before this gitlink
update. The umbrella starts from `a68e524da790314eb55c64ee7b14bfb99ab4e5e5`.

The [final provider record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) contains the
contract review, changed files, exact verification commands, results, isolation guarantees and remaining gates.
Full provider build including both examples passed. The ten isolated cases and separate Qt-default reference passed;
four composite/DPR entries passed (5.40 seconds); nineteen focused installed/startup/palette/composite/policy entries
passed (44.00 seconds); all 61 provider CTest entries passed (43.70 seconds, Qt 6.11.2). C++ formatting, Python/shell
syntax, local documentation links and whitespace checks passed. Provider production behavior is unchanged by this
final acceptance slice. All checks stayed offscreen without desktop pointer/focus automation.

Next Ready assignment: **UQC-103**, repository **holonight-settings**, exact published upstream baseline
`579515ffb456c59cd1299e5852c392c3064c8262`. `git -C holonight-settings ls-remote origin refs/heads/main` returned that
revision on 2026-09-08; its checkout is clean. The provider prerequisite is the authoritative `holonight-qt` gitlink
in this checkpoint, whose publication was confirmed above. Begin the next iteration by creating the settings-local
SDD, reviewing its AGENTS.md and accepted provider contracts, and linking that SDD from this ledger before consumer
implementation. The settings-local design must settle the runtime namespace, embedded executable configuration,
explicit override behavior and contradictory import-contract tests. No settings files were changed in this handoff.

UQC-102 and UQC-104–UQC-106 remain Planned. UQC-201 remains Planned and the initiative remains Accepted. No consumer
implementation, system installation, live authentication challenge or umbrella integration run is included.
Human-operated Hyprland/Sway and real-application/activation acceptance remain later integration gates. Unrelated
package-manager working-tree files are preserved. This is the selected provider-handoff stopping point.

## Settings handoff and AI assignment — 2026-09-08

UQC-103 is Done. Settings implementation `d45141e9b9ee191c64bc334eca0ad505e25cd582` and documentation handoff
`aecd872142b55dc42cb4d1dae675102be799285f`, followed by test-isolation hardening
`2508635351e4901e1b03daf62dbb8ef6538ffcc5`, are published on canonical origin/main. The final revision was returned by
`git -C holonight-settings ls-remote origin refs/heads/main` after publication; the settings checkout is clean.
This checkpoint advances its gitlink from the published SDD checkpoint `0c11035` to the verified handoff.
The preceding umbrella design checkpoint is `8956371`; settings implementation started only after that publication.

The [settings implementation record](../../../holonight-settings/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
records the exact commands, baselines, file changes, evidence and limitations. Settings now uses namespaced runtime
Controls and an embedded overridable HoloNight default, preserves Core/composite visuals and Switch Large sizing
where supported, and discovers installed QML relative to the executable without adding build dependency paths.
No configuration schema, D-Bus interface or provider API changed.

Local verification: dependency/application builds passed; full CTest 53/53 passed (45.53 seconds, Qt 6.11.2); final
runtime/policy 8/8 passed (15.98 seconds), including thirteen import-policy fixtures. Production-window tests visit
five implemented pages and a placeholder under HoloNight/Fusion, checking resolved implementations, loaded plugins,
bindings, deterministic ComboBox overflow/selection, swatch/Core/composite preservation and the conflict dialog.
Actual build and staged-install launches pass embedded default, environment Fusion, command-line Fusion over
HoloNight and external Fusion configuration. Installed traces exclude build dependency discovery. Formatting,
clang-tidy, QML lint/types, package/activation-prefix tests, script syntax, documentation links and whitespace pass.
The existing GCC flag requires the established run-clang-tidy removed-arg workflow; no verification remains blocked.

All runtime checks use private D-Bus sessions, temporary XDG/configuration directories, offscreen software rendering
and an unavailable audio endpoint. The app receives an empty PATH so a regression cannot discover live native
adapters. The final isolation runner passed all eight focused entries and all four installed modes again. No desktop activation, pointer/focus automation, live adapter action, system
installation or ecosystem integration check was performed. Human-operated Hyprland/Sway, real-application and
ecosystem activation acceptance remain UQC-201 gates.

Next Ready assignment: **UQC-104**, repository **holonight-ai**, exact published upstream baseline
`b600674ce4c86d883d98a27ae783e056a6a2f0e6`. `git -C holonight-ai ls-remote origin refs/heads/main` returned that revision
on 2026-09-08, and its checkout is clean. Its AGENTS.md, executable registration and canonical import checker were
rechecked. The provider prerequisite is the authoritative holonight-qt gitlink in this checkpoint;
`git -C holonight-qt ls-remote origin refs/heads/main` still returns `50c59558bb3817f57a992dd72730dba141db1bc8`.
Begin a later iteration by establishing and publishing the AI-local SDD, linking it here, and settling the runtime
namespace, composite behavior, embedded default/discovery, override compatibility and isolated acceptance inventory
before implementation. No AI implementation or local design files were changed in this iteration.

The initiative remains Accepted. UQC-102, UQC-105, UQC-106 and UQC-201 remain Planned. Unrelated package-manager
working-tree files are preserved. This is the selected settings-handoff stopping point.

## AI design checkpoint — 2026-09-08

UQC-104 starts from the assigned AI baseline with its published local design checkpoint.
The [design](../../../holonight-ai/docs/sdd/unified-qtquick-controls/DESIGN.md) and
[acceptance matrix](../../../holonight-ai/docs/sdd/unified-qtquick-controls/SPEC.md)
record runtime migration, exact dependencies and isolated acceptance. Implementation
and verification are pending. Other package states and integration gates are unchanged.

## AI handoff and package-manager assignment — 2026-09-08

UQC-104 is Done. AI implementation `286df4791c651ab8842f0d8f278eac9d4f803b81`
was published and confirmed on canonical origin/main before its repository-local
acceptance handoff and umbrella pin update. The [AI record](../../../holonight-ai/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
contains exact commands, results, resolved implementation/plugin evidence and isolation.

Local checks passed: complete CTest (713 executed passes, one opt-in live credential
skip), both dedicated runtime-style processes, 59/59 existing QML-related checks
under each style, eight actual executable launch modes, staged activation-prefix,
format, full tidy, lint/types, both policies with negative fixtures, syntax, links
and whitespace. Production probes used disabled providers, disposable XDG/SQLite
and a private bus without activation directories. No system installation, desktop
activation, provider request, credential read/write or tool execution was performed.

Next Ready assignment: **UQC-105**, repository **holonight-pkg-manager**, exact
published upstream baseline **`518bb60232086e9537fb402f91b4b703d260ffcf`**.
`git ls-remote origin refs/heads/main` confirmed that baseline on 2026-09-08.
Its provider prerequisite is **`50c59558bb3817f57a992dd72730dba141db1bc8`**,
already published and pinned. Begin the next iteration with the package-manager's
local SDD, control/composite inventory and acceptance matrix. Preserve untracked
`docs/mockups/explore.png` and `docs/mockups/history.png`; both remain outside this handoff.

The initiative stays Accepted. UQC-102, UQC-106 and UQC-201 stay Planned. Live
layer-shell, human-operated Hyprland/Sway, third-party applications and ecosystem
activation remain UQC-201; no umbrella integration acceptance is claimed here.

## Provider/AI repair assignment — 2026-09-08

AI CI run `34251906896` fails in both jobs compiling provider `quickstyleplugin.cpp`:
`holonight/config/config.h` is absent from the target include path. Earlier local acceptance remains historical;
this supplemental correction blocks package-manager implementation until UQC-107 and UQC-108 pass.
UQC-107 is assigned to holonight-qt at the exact baseline above, with configuration
`fe69a59e6b73167fd5349223a4d265d75386c139`. Stage dependencies privately and verify clean Release compilation,
provider tests, example startup, installed consumers and static checks. Publish before advancing the gitlink.
No public API/schema changes, system installation or package transactions are authorized.

## UQC-107 handoff and UQC-108 assignment — 2026-09-08

Provider `f9e4e2eea935055754f41d292320d87f4088c8a4` is published on canonical origin/main,
confirmed by `git ls-remote` before pinning. Local Release acceptance passed with system configuration headers
hidden; exact commands and limitations are in the provider record. UQC-107 is Done.
UQC-108 is Ready and assigned to holonight-ai at `2834665e4c8b9c7681e56a2c8238310f1b6b3157`.
Adopt the corrected provider in Taskfile and both CI jobs, repeat local acceptance, publish and require green
remote build/test, static and licensing checks. UQC-105 stays Blocked until that gate passes.

Provider harness follow-up `cdc44718fcf1fb4a601c38c8fbf9c8b1ded571cd` is published and canonically confirmed.
The first remote run passed compilation but exposed private Qt native-library discovery in isolated acceptance.
The follow-up derives configured Qt library discovery without weakening filtered QML/origin checks; local installed
acceptance passes (39.20 seconds). UQC-108 adopts this provider revision; remote provider confirmation is pending.

Provider `478ef7c40a22c7c3f7ea6f45d9205411b5504834` follows up the CI-only false-positive library classification:
compare basenames instead of parent directories. The isolated matrix passes; publication is canonically confirmed
before pinning. AI's final dependency pins use this revision. Product code is identical to the initial linkage fix.

Provider CI `34264044057` and licensing `34264043952` passed at the pinned revision, including all 61 CI tests.
AI CI `34264138449` passed static checks but exposed an internal composite enum in ProviderListDelegate under
Qt 6.11.1. Published AI follow-up `a8e2aa42359c92be767894bcfdfad3f51a07167a` uses public
HnListDelegate.Outline and adds an independent policy fixture. Local runtime/policy/lint checks pass;
CI `34266081919` must be green before accepting UQC-108 and unblocking package-manager.

AI CI `34266081919` passed its full suite, then exposed missing provider discovery in seven source-only list tests
under explicit Holonight. Published `b874334b20053f94f84fd9b4b1a0a7e0c7cc867a` configures the common test entry
point from the existing provider-path macro. All 59 QML selections pass under each style with host provider modules
hidden. Final remote gate: CI `34267789749`; licensing `34267789698` is green. UQC-105 remains Blocked.

## UQC-108 accepted handoff — 2026-09-08

AI `b874334b20053f94f84fd9b4b1a0a7e0c7cc867a` is published and clean. CI `34267789749` passes build/test,
both existing QML styles, eight actual launches, lint/types, formatting and full tidy; licensing `34267789698`
also passes. UQC-108 is Done. Local 713 executed tests pass (one opt-in credential skip), both 59-test QML
selections pass with host provider modules hidden, and all eight actual launches pass under that same isolation.
No live provider requests, credential interaction or desktop activation were performed.

UQC-105 is Ready at canonically rechecked package-manager baseline `518bb60232086e9537fb402f91b4b703d260ffcf`.
Use pinned provider `478ef7c40a22c7c3f7ea6f45d9205411b5504834` and unchanged configuration baseline.
Publish and link the local SDD before product implementation. Preserve both untracked mockups.

## UQC-105 design checkpoint — 2026-09-08

Package-manager SDD `7e8dc02000779508e5cfc4c26fc54e324732f31c` is published and canonically confirmed from the
assigned baseline. Its SPEC/DESIGN/TASKS define runtime imports, executable discovery, pinned private dependencies,
separate compiled-QML acceptance, four independent scroll surfaces, dual styles and eight isolated launch modes.
UQC-105 is In Progress. Product implementation starts only after publication of this linked umbrella checkpoint.

## UQC-105 accepted handoff and UQC-106 assignment — 2026-09-09

Package-manager implementation `50ee371f3807572806f466f23e7ef40080a8599b` and documentation handoff
`3686bd22a2478e174ba033636eb2e268aafbef5c` are published on canonical origin/main, confirmed before pinning.
The [local record](../../../holonight-pkg-manager/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
contains requirements, design, implementation, exact verification commands and CI follow-ups. UQC-105 is Done.

Verification: full 98-entry CTest suite, both 13-test source-QML selections and both 18-test compiled acceptance
processes pass; independent table horizontal and list/detail/page vertical scrolling, header alignment, responsive
breakpoints, filters, sorting, reconciliation, expansion and popup overflow are covered. All eight actual build/
staged-install launch selectors pass with bounded observation, implementation/plugin evidence and explicit reaping.
Local tests and launches also pass with system provider QML/native discovery hidden. Only existing read-only ALPM
enumeration is permitted; no package operation, system installation, public configuration change or desktop
interaction occurred. Format, full tidy, QML lint/types, independently failing policy fixtures, script/workflow
syntax, documentation links and whitespace pass. CI `34275422302`, licensing `34275422316` and image publication
`34275422324` are green. Final documentation revision CI `34278555864` and licensing `34278555744`
also pass before the umbrella checkpoint. The two unrelated mockups remain untracked with unchanged SHA-256 hashes.

Next Ready assignment: **UQC-106**, one repository `holonight-greeter`, exact clean canonical baseline
`9130c9ccbf05986ab1843ae322831e7fe9efdac9`. Use published, pinned provider
`478ef7c40a22c7c3f7ea6f45d9205411b5504834` and configuration
`fe69a59e6b73167fd5349223a4d265d75386c139`. Rechecked its CMake composition, runtime imports and
FooterSelector's direct-style ComboBox/custom painting. Prepare and publish its local SPEC/DESIGN/TASKS, resolve
scaled delegate geometry through public composite hooks, and link an umbrella In Progress checkpoint before
implementation. Preserve the pre-session launch contract, authentication/session behavior, Core/composites and
scaled ComboBox geometry; verify explicit Fusion overrides and executable-relative installed discovery.
This checkpoint prepares the assignment only and includes no greeter implementation.

The initiative remains Accepted; UQC-102 and UQC-201 stay Planned. Human-operated Hyprland/Sway, activation and
final ecosystem integration remain UQC-201. No final umbrella integration run or clean-ecosystem claim is made.

## UQC-106 design checkpoint — 2026-09-09

Greeter design `7bd4bdfb38c16c18402a6501f645c3b5f5eceea5` is published and confirmed
on canonical origin/main. Its [SDD](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/SPEC.md)
settles runtime imports, public scaled footer composite, embedded selection, exact
build versus installed discovery, private dependencies and isolated GUI/launch
acceptance. Configuration stays unchanged. UQC-106 is In Progress; implementation
starts after this checkpoint is published. UQC-102 and UQC-201 remain Planned;
the initiative remains Accepted. Unrelated package-manager mockups are preserved.

## UQC-109 assignment — 2026-09-09

User approved the provider correction after UQC-106 exposed empty-icon-role
QVariantList diagnostics. Assign only holonight-qt at `478ef7c40a22c7c3f7ea6f45d9205411b5504834`.
Guard the empty role before delegate model lookup, add a reproducing regression,
verify and publish separately. Greeter adopts the corrected published prerequisite
after this handoff. Configuration and other consumers remain unchanged.

## UQC-109 local handoff — 2026-09-09

Provider implementation `7ee28b1` and handoff `00e6e208b6c9b30d89b66ef3aeb4ef8175050764`
are published and canonically confirmed. All 59 provider CTests pass, including
installed acceptance; both runtime styles pass at DPR 1/1.25. Formatting, QML
lint and licensing pass; focused tidy completes with existing fixture advisories.
The [provider record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
documents the reproducer and exact commands. UQC-109 is locally Done; remote
CI/licensing confirmation remains required before the final greeter handoff.

This checkpoint pins the published correction before greeter adopts it. UQC-106
remains In Progress, UQC-102/UQC-201 remain Planned, initiative remains Accepted.
Configuration and other consumer implementations are unchanged.

## UQC-106 accepted handoff and UQC-102 assignment — 2026-09-09

Greeter implementation `dbc86f34b6ad0d6eb75351eedacc08f756b82d97` and completed
acceptance record `b082d82636726fa1fc51178215a3e85d5bb8bbec` are published on
canonical origin/main, confirmed before pinning. UQC-106 is Done. Its
[local record](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
contains requirements, design, changed files, commands, resolved implementation/
plugin evidence and isolation guarantees. Configuration remains unchanged.

All 8 CTest entries pass locally with host provider QML/native libraries hidden
(16.10 seconds): the existing 43 core/CLI tests under both styles, 9 production-QML
GUI tests in each Holonight/Fusion × DPR 1/1.25 process, import policy and 15
independent fixtures. Authentication, selection, masking, OTP, fingerprint,
wrong-password recovery, cancellation, fake session completion, configuration
errors, disabled states, power confirmation, selector IPC and wallpaper engines
are covered. Layout/popup checks include 1672×941, widths 899/900, larger layout,
scales 0.78/1/1.25, edge placement, actual delegate height, overflow, selected-row
visibility and first/last-row reachability. The provider bug found by these tests
was fixed and published separately as UQC-109 before greeter adopted it.

All eight actual build/staged-install selectors pass with bounded observation,
required QML/control/plugin evidence and explicit termination/reaping. Installed
launches exclude build discovery, and both matrices pass with host HoloNight QML
and native configuration libraries hidden. Format, full owned-C++ clang-analyzer,
zero-warning four-file QML lint, generated metadata, policy, staged installation,
syntax, links, licensing and whitespace pass. Implementation CI `34292227990`
and licensing `34292227948` pass. Final handoff CI `34292798013`
passes (6 minutes 37 seconds), and licensing `34292797960` passes.

Next Ready assignment: **UQC-102**, one repository **holonight-shell**, exact
published baseline **`723763e09ff815d344a6cb01529dd8345a43b316`**. Canonical main
and the clean checkout were rechecked; AGENTS.md, executable registration,
authentication entry points and session environment wrappers were reviewed.
The corrected provider prerequisite is **`00e6e208b6c9b30d89b66ef3aeb4ef8175050764`**,
published, pinned, and green in CI/licensing. Configuration remains at the
unchanged authoritative gitlink. Start the next iteration by publishing the
shell-local SPEC/DESIGN/TASKS and linking an In Progress checkpoint before product
implementation. Settle runtime imports, graphical executable defaults/discovery,
authentication override propagation, and diagnostics that distinguish configured
selection from actual loaded implementations. No shell implementation is part
of this handoff.

The initiative remains Accepted; UQC-201 remains Planned. No system installation,
live authentication, session/power operation, desktop pointer/focus automation or
umbrella integration acceptance occurred. Real pre-session/compositor behavior,
human-operated Hyprland/Sway, activation and final ecosystem checks remain UQC-201.
Package-manager's untracked `docs/mockups/explore.png` and `docs/mockups/history.png`
are preserved. No clean-ecosystem claim is made while those files remain untracked.

## UQC-102 design checkpoint — 2026-09-09

Shell design `5324b47fb01501d4fa3e90e7865b23065efce970` is published on canonical
origin/main, confirmed by `git -C holonight-shell ls-remote origin refs/heads/main`
before this gitlink update. It starts from the assigned baseline
`723763e09ff815d344a6cb01529dd8345a43b316`. Provider
`00e6e208b6c9b30d89b66ef3aeb4ef8175050764` and configuration
`fe69a59e6b73167fd5349223a4d265d75386c139` were rechecked on canonical origin/main
and remain unchanged at their authoritative pins.

The shell-local [SPEC](../../../holonight-shell/docs/sdd/unified-qtquick-controls/SPEC.md),
[DESIGN](../../../holonight-shell/docs/sdd/unified-qtquick-controls/DESIGN.md) and
[TASKS](../../../holonight-shell/docs/sdd/unified-qtquick-controls/TASKS.md) settle
shell/authentication/compatibility imports, public identity-selector geometry hooks,
embedded defaults, build/bin/libexec discovery, askpass CLI/protocol preservation,
verified session propagation and selection/discovery/loaded-control diagnostics.
They define dependency order, exact affected files and future isolated acceptance.
No new public provider API or configuration schema is planned; a discovered gap
requires a separate coordinated prerequisite.

Verification: current code and pinned provider contracts reviewed; local Markdown
links, existing file inventory, task ordering, staged scope and `git diff --check`
pass. This checkpoint changes documentation and the shell gitlink only. Product
tests are not required and were not run; implementation and verification remain
pending. UQC-102 is In Progress. Stop after publishing this umbrella checkpoint,
before product implementation. The initiative remains Accepted and UQC-201 Planned.
Live authentication, compositor interaction and ecosystem activation stay UQC-201.
Package-manager mockups `docs/mockups/explore.png` and `docs/mockups/history.png`
remain untracked and unchanged; no clean-ecosystem or integration claim is made.

## UQC-102 accepted shell handoff — 2026-09-09

Shell handoff `1320f37093e2148a224a4e8fbfaf4ac1b536c6a8` is published on canonical
origin/main and was rechecked before this gitlink update. Implementation begins at
`8caee8569541ffd84c28fbfe2667259f3117c4b8`; subsequent commits repair stale CI
package setup and disposable-runner namespace support, then finalize acceptance.
Provider and configuration remain unchanged at their authoritative gitlinks.

The shell-local [implementation record](../../../holonight-shell/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
links the requirements, design, exact file choices and executed commands. Shell,
askpass and polkit embed the overridable Holonight default, preserve Qt selector
precedence, and discover QML/native dependencies from exact build outputs or
relocated bin/libexec installations. Qualified Controls and the public identity
composite preserve authentication, input and session routing. Diagnostic evidence
separates configured selection, module discovery and created implementation origins;
askpass protocol stdout remains reserved for responses.

Local `task test` passes 1157/1157 entries. Acceptance covers both styles, DPR 1/1.25,
popup scales 0.78/1/1.25, fake authentication backends, wrapper propagation and 17
independent policy fixtures. The launch matrix passes 45 entry-point/selector modes
plus three missing-module cases with host provider discovery hidden. All 30 installed
launches reject the exact shell build directory and dependency/source-QML paths.
Formatting, full remote tidy, QML lint/types, architecture, syntax, links, whitespace
and licensing pass. Existing AudioService lint metadata warnings and the unchanged
sidebar Loader height warning are explicitly documented; no zero-warning claim is made.

[Final-revision CI 34355350981](https://github.com/lebedenko/holonight-shell/actions/runs/34355350981)
passes build/test (20m14s), static checks (32m24s) and REUSE licensing (20s). Preceding implementation
[CI 34351602771](https://github.com/lebedenko/holonight-shell/actions/runs/34351602771)
also passes. The auxiliary image build succeeded but GHCR denied image publication
with `permission_denied: write_package`; registry-owner maintenance remains separate.
Required verification uses the existing CI image with explicit job-local packages.
No registry permissions, credentials or release deployments were changed.

Only isolated services and a private headless compositor were used. UQC-102 is Done;
the initiative remains Accepted and UQC-201 Planned. Live authentication,
human-operated Hyprland/Sway, ecosystem activation and final integration are still
reserved for UQC-201. No umbrella integration tests or clean-ecosystem claim are made.
Package-manager's untracked explore/history mockups retain their original hashes.

## UQC-201 readiness and assignment — 2026-09-09

All implementation packages are Done. The umbrella coordinator is assigned UQC-201
from `a26b4e537ea8105a991ec5f48e06e9fe7565dd72`, using this checkpoint's authoritative
gitlinks. Every submodule is clean and its HEAD equals canonical origin/main, verified
with `git submodule foreach --quiet 'git ls-remote origin refs/heads/main'`.

Package-manager `32f989f2949092886c26cea4459945c875746089` publishes only
`docs/mockups/explore.png` and `docs/mockups/history.png` as `chore: additional mockups`.
REUSE passes (122/122); staged scope and unchanged SHA-256 bytes verified:

- explore: `5bef2cd1eaaaab6112d512343e56c8ea11e07921e60e3d8a73d867619582bf27`
- history: `ee0aa045baeb79b24bd075b44c0e30a55935dadd131ba15a4daf48765fb2bcb5`

Canonical publication was confirmed before updating the gitlink. Verification uses
fresh private builds and one staged prefix against current pins, without consumer
Taskfile dependency substitution. No product changes, system installation, package
transactions, live authentication or desktop pointer/focus automation are assigned.
The initiative remains Accepted until user-operated Hyprland and Sway gates pass.

## UQC-201 automated checkpoint — 2026-09-09

UQC-201 is In Progress. Fresh dependency-order results, exact command records,
versions, failed attempts and limitations are in [INTEGRATION.md](INTEGRATION.md).
The [manual matrix](MANUAL.md) and [separate authentication procedure](AUTHENTICATION.md)
are prepared for user operation; no manual acceptance is checked.

Installer preflight exposed the package-ownership mismatch recorded as UQC-202.
That correction is a separate Planned work package, not an unreviewed product
change in this evidence handoff. The initiative remains Accepted; full integration
requires resolution of UQC-202 and the reproducible AI Fusion geometry finding
(UQC-203), plus completed Hyprland/Sway manual evidence. No system installation,
package transaction, live authentication or active-desktop pointer/focus/activation
operation occurred.

## UQC-202/UQC-203 readiness and assignment — 2026-09-09

Both packages are Ready with settled contracts. Canonical origin/main was
rechecked for umbrella `4c38804f142486b23dc20b81f6a0fa78e5530421`, AI
`b874334b20053f94f84fd9b4b1a0a7e0c7cc867a`, provider
`00e6e208b6c9b30d89b66ef3aeb4ef8175050764`, and configuration
`fe69a59e6b73167fd5349223a4d265d75386c139` before assignment.
The coordinator implements UQC-202 first in umbrella, then UQC-203 only in AI,
with separate implementation/publication boundaries. The installer verifies
Qt capabilities independently of package ownership; AI preserves native style
sizing and adds polished geometry acceptance. See [UQC-202 design](UQC-202.md)
and [AI supplemental SDD](../../../holonight-ai/docs/sdd/unified-qtquick-controls/UQC-203.md).
Publish this checkpoint before implementation. Keep UQC-201 In Progress and the
initiative Accepted; all manual Hyprland/Sway/authentication gates stay unchecked.

## UQC-202 acceptance / UQC-203 start — 2026-09-09

UQC-202 local verification passes: eight installer fixtures, shell syntax,
REUSE (48/48), whitespace and real `scripts/install.sh --check` on the host.
See [commands and results](UQC-202.md). This checkpoint publishes the umbrella
implementation independently. UQC-203 starts from published design `b8368ac`,
following Ready assignment at `73e0ca2`. No AI implementation is included.
UQC-201 remains In Progress and the initiative Accepted; manual gates remain open.

## UQC-203 accepted handoff — 2026-09-09

AI handoff `7e25e78cc7fb33aa63ed480bc3f328a65e04ca0c` is available from canonical
origin/main, confirmed before this gitlink update. Final implementation
`11b021a4bd86d07d283d1c89f6467c44a17628f3` has green
[CI 34390403485](https://github.com/lebedenko/holonight-ai/actions/runs/34390403485)
(build/test 14m25s; static checks 19m14s) and
[licensing 34390403390](https://github.com/lebedenko/holonight-ai/actions/runs/34390403390).
The handoff changes documentation only; its links, REUSE (475/475) and whitespace pass.
The [AI-local record](../../../holonight-ai/docs/sdd/unified-qtquick-controls/UQC-203.md)
retains the reproduced Fusion failure, CI font-metrics follow-up, all local commands,
results, isolation details and expected skips. No application QML changed.

UQC-202 implementation `8af91cb173d6268e71ddb1b92afed8915a6ac658` is published;
[installer CI 34380475124](https://github.com/lebedenko/holonight/actions/runs/34380475124)
and [licensing 34380474984](https://github.com/lebedenko/holonight/actions/runs/34380474984)
pass. The umbrella ignores only the regression suite's generated Python bytecode.
Provider and configuration pins are unchanged. Both repair packages are Done;
UQC-201 remains In Progress and the initiative Accepted. Publish this checkpoint,
then append fresh installer/Fusion evidence at its authoritative pins. Every manual
Hyprland/Sway/authentication gate remains unchecked.

## UQC-201 targeted recheck checkpoint — 2026-09-09

At published handoff `730be066e78c4cf5c0d65f3f78fb669f5fcbb229`, real installer
`--check` passes and AI's previously failing explicit Fusion selection passes
59/59 in 15.37 seconds. [Fresh evidence](INTEGRATION.md#uqc-202uqc-203-gate-recheck--2026-09-09)
and [commands](COMMANDS.md#uqc-202uqc-203-targeted-recheck--2026-09-09) retain the
original failures and document the repaired gates. All submodules are clean;
umbrella REUSE (47/47), links and whitespace pass. No manual files/checklists
changed. UQC-202/UQC-203 remain Done, UQC-201 remains In Progress, and the initiative
remains Accepted pending human Hyprland/Sway/authentication acceptance.

## UQC-201 guided preparation checkpoint — 2026-09-09

At baseline `7fcc8bb48a451185b9412950ac7f651ee75975c7`, a fresh installation is
configured directly under `/tmp/holonight-uqc201-8r1jtlln/prefix`, resolving the
old kit's inaccessible activation paths. [Fresh preparation evidence](INTEGRATION.md#uqc-201-accessible-guided-preparation--2026-09-09)
records nine passing dependency-order suites (one expected AI credential skip),
installed selector matrices, repaired Fusion 59/59, metadata/linkage/permission
checks, helper checks and retained sandbox failures. No product files or pins
changed; final canonical publication and clean-submodule checks pass.

[Guided batches](GUIDED.md), [manual matrix](MANUAL.md), and
[authentication instructions](AUTHENTICATION.md) now use the accessible kit.
**Reviewed manual results: none yet.** First handoff is Hyprland Settings default
at scale 1; subsequent batches wait for returned observations. UQC-201 stays
In Progress, repairs stay Done, and the initiative stays Accepted. Real pre-session
greeter acceptance remains a separate pending gate even after demo observations.

## UQC-201 first manual finding — 2026-09-10

The user reports no visible focus or action from Tab/Shift+Tab/Space/Enter in
Settings in the prepared Hyprland login. The [guided observation ledger](GUIDED.md#evidence-review)
records the supplied evidence path and the preceding, subsequently recovered VT
freeze. Keyboard traversal is not accepted. Source inspection finds focus visuals
in the provider controls but no Settings test exercising Tab traversal; this does
not establish runtime focus or a product root cause. Await text-entry/window-focus
clarification and review of the actual process/origin evidence before assigning a
repository-owned repair package. No product files, pins or acceptance states change.

## UQC-204 provider focus-visibility finding — 2026-09-10

User follow-up confirms City text entry and click-focus work. Repeated Tab advances
through controls with intermittent missing focus indicators; exact order remains
user-reported rather than instrumented. Settings is pinned at
`2508635351e4901e1b03daf62dbb8ef6538ffcc5`; provider ownership is narrowed to
`holonight-qt` at `00e6e208b6c9b30d89b66ef3aeb4ef8175050764`.

`qml/controls/HnSettingsRow.qml` forwards active focus with parameterless
`forceActiveFocus()`. An offscreen installed-prefix probe compares keyboard focus
forwarded through the row with a standalone ComboBox. In both Holonight and Fusion:

```text
forwarded: activeFocus=true, focusReason=7 (OtherFocusReason), visualFocus=false
standalone: activeFocus=true, focusReason=1 (TabFocusReason), visualFocus=true
```

Private probe and logs: `.cache/uqc201-focus-probe/forward.qml`, `Holonight.log`,
`Fusion.log`. Both final runs exit 0 with software/offscreen rendering and unavailable
session/system bus endpoints. No live pointer/focus interaction was automated.
The existing provider test `Controls_SettingsRowForwardsSingleFocusAndSkipsCompoundRoot`
checks focus destinations using Basic, but does not assert keyboard focus reason or
visualFocus. This confirms a shared-control defect matching the user's observation;
it does not establish that every invisible stop has the same cause. The Weather
page also clips its scrollable content, so offscreen focus must remain a separate
consideration during follow-up.

UQC-204 is Planned; prepare its repository-local SDD and acceptance scope before
Ready assignment. Product implementation and submodule pins remain unchanged.
UQC-201 keyboard visibility remains failed; no further repetition of the same
manual sequence is needed to establish this finding.

## UQC-201 reboot recovery — 2026-09-10

Regenerated helpers with `prepare-guided-kit.py /tmp/holonight-uqc201-8r1jtlln`
and restored the original configured prefix with `cmake --install` from all ten
surviving component builds in dependency order. No relocation or product change.
Qt packages remain 6.11.2-3/base and 6.11.2-1/declarative; product pins are unchanged.
Recovery logs: `.cache/uqc201-guided-qht3_tjs/reboot-20260910/`.

Python/terminal syntax, launcher wrong-user guards, Hyprland configuration and
headless Sway validation pass. All 239 installed regular files are hashed;
permissions and internal symlinks pass, and all 18 ELF files resolve dependencies
without workspace paths. Installed Settings default and environment/Fusion startup
checks pass with host-provider masking, private buses and forbidden build QML paths.
The initial sandbox attempt could not bind its private bus; an approved retry
omitting LD_LIBRARY_PATH failed against the masked host config library. Both final
checks passed with the prefix library path used by the guided launcher.

READY is restored after these recovery checks. Prior full-suite evidence remains
historical; no full-suite rerun or new manual pass is claimed. Next guided step is
Settings default at Qt/output scale 1.25/1, then review before Fusion. UQC-204 stays
Planned and unresolved; UQC-201 stays In Progress and the initiative Accepted.


## UQC-201 additional Settings findings — 2026-09-10

See [continuation observations](GUIDED.md#settings-continuation-observations--2026-09-10)
for the user's report. Record three separate triage subjects: slider geometry/value
jump on press, disappearing/noninteractive popup rows, and popup selected-item
initialization/outside-click dismissal. No root cause, repair acceptance or manual
pass is inferred. Evidence directory and exact slider identities are pending.

Read-only source review at unchanged pins finds Appearance font selectors use
provider `qml/controls/HnIconComboBox.qml`, while Weather selectors use provider
`qml/ComboBox.qml`. Both popup implementations reparent to the overlay, use a
scrollable ListView over delegateModel, bind currentIndex to highlightedIndex,
and reposition on index changes/opening. Neither explicitly sets closePolicy.
These are investigation points, not proof of the reported causes. Appearance
slider rows combine fill-width sliders and value labels inside RowLayouts loaded
by HnSettingsRow; the provider slider has no explicit pressed-dependent width.
This does not rule out indirect sizing or appearance-update effects.

Compare default/Fusion at the same scale and correlate logs before settling
repository-owned repair scopes and local SDDs. Preserve UQC-204 independently.
Only GUIDED.md and TASKS.md changed; source inspection and `git diff --check`
performed, no product tests or pointer/focus automation. UQC-201 remains In Progress.

### Settings Fusion follow-up — 2026-09-10

User confirms Escape closes expanded HoloNight ComboBoxes. Outside-click failure
is unchanged. Fusion comparison reports substantially better behavior with only
missing popup-row hover feedback and tight ComboBox/button padding. Padding is
explicitly a non-defect visual preference; hover feedback remains a triage
observation. Earlier interaction failures were not reported in Fusion, but exact
controls and process/origin evidence remain pending; no root cause or exhaustive
pass is asserted. See GUIDED.md for the next AI default batch. UQC-204 and other
HoloNight findings remain open; initiative Accepted, UQC-201 In Progress.
Documentation-only update; `git diff --check` passes. No product tests needed.


## UQC-201 AI provider-form findings — 2026-09-10

[User observations](GUIDED.md#ai-provider-form-observations--2026-09-10) record
intermittent ComboBox focus feedback, suspected disabled-control traversal,
button ring loss after successful Space activation, a knob-only slider, a
forward-only invisible focus stop between Context window and Temperature, and
loss of Tab/Shift+Tab after VT return until clicking a control. Preserve these
as separate triage subjects; no root cause or product acceptance is established.

Read-only review at AI `7e25e78cc7fb33aa63ed480bc3f328a65e04ca0c` and provider
`00e6e208b6c9b30d89b66ef3aeb4ef8175050764`:

- Provider HnFormField enables activeFocusOnTab whenever a loaded child exists,
  without checking that child's enabled/visible/activeFocusOnTab state. It forwards
  focus using parameterless forceActiveFocus(). This resembles UQC-204's reason
  loss but is a different composite and needs its own reproduction/scope review.
- AI OllamaSettingsPanel places Context window in an HnFormField with a SpinBox;
  Temperature's HnFormField instead loads a RowLayout with a SpinBox and Slider.
  Forwarding to that layout is a candidate for the invisible forward stop, not
  an instrumented identification of the focused item.
- ProviderFormActionRow reserves an action-column width of 220. Temperature's
  nested row has a fill-width Slider beside a SpinBox. Inspect allocated/minimum
  widths before attributing the knob-only rendering to either repository.
- ProviderActionButton is a thin runtime Button wrapper. Provider Button draws
  its focus border using visualFocus. Some action bindings disable buttons while
  work is in progress; exact action and focus lifecycle must be captured before
  explaining the ring loss. No action was triggered during source inspection.
- VT-return failure requires separate session/application event evidence; visual
  focus appearance alone does not prove compositor keyboard focus or delivery.

No implementation assignment, product edits, pin changes or automated live UI
interaction. GUIDED.md/TASKS.md updated and `git diff --check` passes; product tests
were not run for this documentation-only triage. Await Fusion comparison and run
references before settling repair scopes/local SDDs. UQC-204 remains Planned;
UQC-201 remains In Progress and the initiative Accepted.


### AI Fusion comparison / Switch observation — 2026-09-10

The user reports the same focus traversal failures under Fusion. Missing ComboBox
focus feedback occurs on the first traversal in both styles, then disappears on
later cycles. Preserve this initialization condition in future regression scope.
Fusion's Temperature slider has a track and knob but remains too short; AI layout
is user-suspected, not a measured root cause. No resolution of the button or
VT-return failures is claimed. See GUIDED.md for the complete comparison.

HoloNight Switch feedback is visible off but not on; Fusion shows feedback in both
states. Keyboard focus is the provisional interpretation given the surrounding
report. Read-only provider Switch.qml inspection finds a visualFocus-controlled
ring around the thumb using borderFocus, with a checked track using primary (or
primaryHover). Contrast against that track is an investigation point only: no
runtime colors, focus state or screenshot were measured. Exact Switch/feedback
type and evidence path remain pending. Do not merge this with UQC-204's forwarding
cause without reproduction.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No product changes or tests.
UQC-201 remains In Progress, UQC-204 Planned and the initiative Accepted. Continue
with the package-manager default manual batch while preserving these failed gates.


### Package-manager default feedback — 2026-09-10

User reports no issues observed in the requested default-style package-manager
batch at Qt/output scale 1.25/1. Preserve this positive observation with its scope;
run/origin correlation and Fusion comparison remain pending. No exhaustive manual
or integration pass is inferred. GUIDED.md/TASKS.md updated; `git diff --check`
passes. No product changes or tests. UQC-201 stays In Progress; prior defects open.


### Package-manager Fusion feedback — 2026-09-10

User reports no issues in the Fusion package-manager batch requested at Qt/output
scale 1.25/1. Both tested styles have positive observations; actual run/origin
correlation and remaining matrix gates are pending. Next guided batch is shell
default in the prepared minimal compositor. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product edits or tests. UQC-201 stays In Progress;
existing Settings/AI/provider findings remain open.


## UQC-201 shell rendering/input finding — 2026-09-10

[Shell observation](GUIDED.md#shell-default-failure--2026-09-10): default-style
shell requested at Qt/output scale 1.25/1 renders only left sections initially,
jitters/resizes under pointer interaction, reveals/hides right sections, and
appears unclickable while some tooltips work. Exclusive space appears visually
stable; actual geometry is unmeasured. This blocks this run's shell interaction
acceptance; no product root cause or integration acceptance is established.

Read-only review at shell `1320f37093e2148a224a4e8fbfaf4ac1b536c6a8` finds
LayerShellManager::configureSurface assigns kBarHeight to both requested surface
height and exclusive_zone. TopBar uses a parent-filling RowLayout, a fill-width
active-window section and right-side status/tray/clock sections. This establishes
the requested sizing arrangement, not the runtime result or jitter cause.
The scale-1 comparison keeps style unchanged to narrow the reported failure.

Listing `/home/tux/uqc-guided-evidence` was denied by filesystem permissions;
actual run evidence has not been inspected. Request the user's printed run path
and selected diagnostics when needed. No source edits or live pointer/focus
interaction. GUIDED.md/TASKS.md updated; `git diff --check` passes. No product tests
run for documentation-only triage. UQC-201 In Progress, initiative Accepted;
previous findings remain open.


### Shell scale-1 follow-up — 2026-09-10

User reports functional interaction and correctly working/rendered popups at Qt
scale 1, with no jitter. This comparison implicates scale-dependent behavior in
the earlier failure but does not establish its cause. Remaining frame defects
are detailed in GUIDED.md: broken right edges for logo/workspaces/active window,
status-widget solid backgrounds covering borders, with bell/date-time correct.

Read-only source review identifies shell-local Controls/BarFrame.qml (Canvas) as
the frame used by the inspected topbar sections; do not assign this to a shared
provider HudFrame based only on the visual description. TopBar uses negative
section margins; BarFrame also extends across inherited section padding. Review
path geometry and sibling overpainting separately. Network/audio/battery/keyboard
and notifications are BarSection instances; BarSection declares transparent color,
and the widgets contain their own state-dependent background rectangles. Thus a
solid covering block is not explained merely by a missing transparent root color.
Runtime rendering evidence is still required. No root cause or repair scope settled.

Next manual comparison is Fusion at Qt scale 1. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product changes/tests or pointer automation.
Scale-1.25 shell failure and earlier findings remain open; UQC-201 In Progress.


### Shell Fusion scale-1 feedback — 2026-09-10

User reports identical topbar behavior/rendering under Fusion, including the
existing frame/background defects, with no additional issues. Sidebar Overview's
indeterminate progress bar displays Fusion styling; no new progress malfunction
is asserted. Record positive interaction feedback at scale 1 alongside unresolved
visual defects. Both-selector reproduction does not prove ownership/root cause.
Fusion scale 1.25 and actual evidence/origin correlation remain pending.
Next guided batch is Haruna default at Qt scale 1. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product edits/tests. UQC-201 stays In Progress and
all prior failed gates remain open.


### Haruna default scale-1 findings — 2026-09-10

User reports mostly functional Haruna, persistent ComboBox outside-click failure,
a working long font dropdown, mixed light/dark file/color pickers, imperfect warning
corners in Mouse → Add action, visually different dialog buttons, and concurrent
help popups. See GUIDED.md for precise observations and classification limits.

Accepted scope explicitly preserves Haruna Fusion fallback and defers Dialog/
DialogButtonBox implementations. Do not infer actual button origin from appearance
or classify palette/geometry defects as accepted merely because fallback exists.
Likewise, concurrent help-popups are a user preference/application-logic hypothesis,
not yet a required provider repair. Working font-list scrolling narrows the earlier
Settings report without invalidating it. No runtime/source reproduction of these
new Haruna findings was performed; picker backend and evidence paths are pending.

Next guided comparison is explicit Fusion at scale 1 for the reported surfaces;
Holonight scale 1.25 remains pending. GUIDED.md/TASKS.md updated; `git diff --check`
passes. No product changes/tests. UQC-201 remains In Progress; prior failures open.


### Haruna Fusion results / provider icon gaps — 2026-09-10

Fusion pickers are consistently dark and outside-click closes ComboBoxes. Warning
corners remain defective in both styles; Fusion dropdown hover feedback remains
missing. New user comparison reports icons in Fusion top menus/Settings navigation
but not HoloNight, with excessive empty top-menu icon space. See GUIDED.md for
scope, sidebar-location ambiguity and the requested per-dropdown alignment rule.

Read-only inspection of pinned provider `00e6e208b6c9b30d89b66ef3aeb4ef8175050764`
confirms implementation limitations: MenuItem.qml reads icon.source and hides its
HnIcon when that source is empty, without consuming icon.name; its checkmark and
icon containers always reserve compact-icon widths plus RowLayout spacing.
ItemDelegate.qml's contentItem is Text only and does not render the icon property.
Button/ToolButton use IconLabel with the full icon property, an existing provider
convention to inspect when designing the repair. These code gaps match the report,
but actual Haruna delegate origins/icon properties remain uncorrelated.

Record requested provider repair scope: support menu/delegate icons and allocate
menu icon space per dropdown only when at least one item has an icon, aligning all
labels while retaining necessary independent checkmark/submenu geometry. Prepare
repository-local SDD and reproduction before Ready assignment; no implementation
or acceptance claim. Palette mixing, popup dismissal, hover and both-style warning
corners remain separate triage subjects.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No product files/tests changed
or run. Next is Haruna Holonight at Qt scale 1.25. UQC-201 remains In Progress;
initiative Accepted and previous defects open.


### Haruna persistent first-row highlight — 2026-09-10

User reports no new scale-1.25 failures; existing warning corners are less visible.
New both-scale HoloNight observation: first row in list-based Settings pages
(e.g. Shortcuts) retains a selected-looking background despite interaction with
other rows, independently of functioning hover highlights. Fusion has no such
persistent background and gives brief click feedback but no visible hover effect.

Read-only provider ItemDelegate.qml inspection confirms background isSelected
combines highlighted, checked and ListView.isCurrentItem. This can introduce
selection visuals based on view current-item state even without an explicit
application highlight/check state. It is a concrete reproduction candidate, not
runtime proof of Haruna's delegate type/currentIndex or final repair semantics.
Future regression scope should distinguish current-item, selection, hover, press
and focus, preserving intended selection in real selection-bearing lists.
Keep this separate from the previously recorded missing icons/empty menu columns.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No implementation, product
tests or live UI automation. Evidence/origin correlation remains pending. Next
manual batch is NeoChat Holonight at scale 1; UQC-201 remains In Progress.


### NeoChat navigation-triggered palette finding — 2026-09-10

User inspected logged-out Settings; ComboBox outside-click failure repeats, with
no other interaction issue observed. Initial main/General Settings surfaces are
dark in an application-looking palette; navigating to another Settings page changes
both Settings and main window to the current HoloNight scheme. No explicit palette
selection reported. Exact destination page and process/control/palette evidence
remain pending. Account-dependent surfaces are untested.

Treat this as an unresolved navigation-triggered palette transition, not proof of
missing startup style selection or a successful correction to HoloNight colors.
The accepted contract preserves application palette overrides; examine initial
palette ownership and lazy-page side effects before assigning a repository repair.
Next comparison is Fusion at scale 1, same navigation, noting retained disposable
profile state. Holonight scale 1.25 remains pending. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product edits/tests or live UI automation. UQC-201
remains In Progress; no manual gate closed by inference.


### NeoChat Fusion palette/spacing/dropdown comparison — 2026-09-10

User confirms recoloring under both selectors. New Fusion observations: no
indicator-to-label gap for CheckBox/RadioButton; Appearance color-scheme dropdown
uses all available vertical space, highlights hovered rows, and looks HoloNight-
like despite a Fusion-looking collapsed control. See GUIDED.md for limits.
No actual mixed implementation, overflow or unreachable rows is established.
This popup's working hover feedback narrows earlier Haruna observations; missing
hover is not a universal Fusion failure. Checkbox/radio spacing under HoloNight
and NeoChat Fusion outside-click dismissal remain unconfirmed.

No source/runtime attribution performed this turn. Record spacing as a finding
requiring concrete control/layout inspection; retain palette transition separately.
Next is Holonight scale 1.25 with the same surfaces. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product edits/tests or live UI automation. UQC-201
remains In Progress, initiative Accepted, and prior findings remain open.


### NeoChat repeated Appearance-page palette toggle — 2026-09-10

User's deeper reproduction supersedes the earlier broad navigation/initialization
hypothesis: only opening Appearance changes colors; other Settings pages do not.
Across repeated Settings close/reopen cycles, opening Appearance alternates between
the initial non-HoloNight-looking scheme and the current HoloNight-looking scheme,
also affecting the main window. No explicit color-scheme selection is reported.
Confirmed by user under Holonight Qt scale 1 and 1.25, and Fusion Qt scale 1.
The remaining scale-1.25 result is reported unchanged from scale 1.

Record repeated page-entry palette mutation, not a one-time loading transition or
style-selection success. Exact palette values/origins and configuration writes
remain unmeasured; both-selector reproduction does not settle ownership. Future
reproduction should preserve repeated window/page-entry cycles and distinguish
page initialization from explicit user selection. Do not require the user to
repeat this established sequence again. See GUIDED.md for the exact steps.

Next batch: Tokodon default scale 1. GUIDED.md/TASKS.md updated;
`git diff --check` passes. Documentation-only; no product tests or live automation.
UQC-201 remains In Progress and previous failed gates remain open.


### Tokodon palette-toggle / font-picker findings — 2026-09-10

User reports the same repeated two-scheme toggle as NeoChat; Tokodon opens Settings
on Appearance, triggering it immediately. This adds a second application to the
navigation-triggered palette finding without proving shared root cause/ownership.
Font picker has a light main background and otherwise dark controls. OK/Cancel
look unlike HoloNight/Fusion and resemble Basic to the user; exact dialog/backend
and control origins are unverified. Retain palette mismatch and button-style
classification as separate subjects. Accepted Basic fallback is not proof of
these buttons' origin or a palette-failure waiver.

Next guided comparison is Tokodon Fusion at scale 1; Holonight scale 1.25 remains
pending. GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits,
tests or live UI automation. UQC-201 remains In Progress and prior findings open.


### Tokodon Fusion Switch containment finding — 2026-09-10

User confirms palette toggle and references the same ComboBox/RadioButton/CheckBox
observations as NeoChat Fusion. New failure: right-aligned Switch extends beyond
the right edge of its boxed Settings section, with title/description on the left.
Actual setting/section and geometry/origins remain pending; do not equate this
with a proven provider indicator defect or silently close the earlier accepted
trailing-card containment requirement. Font-picker Fusion palette/button result
was not explicitly supplied.

Next comparison is Tokodon Holonight scale 1.25, including these boxed rows;
HoloNight overflow applicability is not yet established. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product edits/tests or live UI automation. UQC-201
remains In Progress; previous palette, focus, geometry and rendering gates open.


### Picker inconsistency depends on observed palette state — 2026-09-10

Tokodon Holonight scale 1.25 is reported unchanged from scale 1. User clarifies
mixed picker colors seem associated with the HoloNight-looking application palette;
the alternate initial palette produces consistently colored pickers. Preserve as
an observed correlation requiring paired same-picker evidence, not a proven cause
or a retrospective pass for all dialogs. Future comparison must vary/record actual
palette state independently of Controls selector. The repeated Appearance toggle
may affect prior style comparisons; original observations remain retained.

Next manual batch is greeter demo default scale 1; activation/authentication,
remaining palette checks, real pre-session greeter and Sway gates stay pending.
GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
live UI automation. UQC-201 remains In Progress and all unresolved findings open.


## Greeter demo functional/visual findings — 2026-09-10

See GUIDED.md for user-reported disappearing session rows, disabled layout-selector
hover/color mismatch, keyboard password-reveal failure, user-selector Tab omission,
and requested power-button/background/icon/avatar-selector corrections. General
keyboard navigation and popup placement are positive observations with those
exceptions. Password-field palette mismatch remains a suspicion to verify.

Read-only review of greeter pin `b082d82636726fa1fc51178215a3e85d5bb8bbec`
(no repository AGENTS.md present; umbrella instructions apply) finds:

- FooterSelector derives from HnIconComboBox, overrides content with fixed color
  literals and background hover/down colors without explicit enabled-state guards.
  This is a candidate for disabled appearance issues, not a runtime state trace.
- LoginPanel uses a regular Controls.ComboBox for users, enabled only with multiple
  users outside starting/authenticated states. Its background/indicator are empty.
  Password Backtab and power-button Tab link directly to system actions/password,
  respectively. Inspect the complete chain and enabled state for user reachability.
- Password echoMode depends on reveal.pressed; reveal is a Controls.Button labelled
  Hold to reveal password. Keyboard activation/press timing needs reproduction;
  do not change its semantics based solely on a brief Space activation report.
- System actions use text symbols for reboot/poweroff. Actual glyph bounds and
  normal backgrounds require review. The requested avatar selector was not located
  by provider filename search; locate its identity before choosing implementation.

No repository repair assigned or product files changed. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product tests or live input automation. Next is demo
Fusion scale 1; UQC-201 remains In Progress, real pre-session gate pending.


### Greeter demo Fusion selector comparison — 2026-09-10

User reports session selector works with mouse/keyboard under Fusion, but lacks
visible hover feedback. User selector is unusually large and lacks hover feedback,
but works when used; exact affected geometry and Tab-chain inclusion remain
unconfirmed. General "same issues" preserves other greeter findings without
claiming a keyboard password-reveal fix. See GUIDED.md for classification limits.

Next is Holonight demo scale 1.25. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product edits/tests or live UI automation. UQC-201
remains In Progress; real pre-session and other pending gates remain open.


### Greeter demo scale-1.25 / authentication handoff — 2026-09-10

User reports no difference from Holonight scale 1. All existing greeter findings
remain open; no real pre-session pass inferred. Next guided step is read-only
third-party authentication preflight per AUTHENTICATION.md; no agent/challenge
has been started. The restored helper and READY marker are present; helper source
inspection confirms preflight collection precedes separate agent/registration/
challenge steps. Review returned evidence before continuing.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or live
UI automation. UQC-201 remains In Progress; outstanding matrix and evidence gates
are retained, including Sway and remaining style/scale combinations.


### Third-party authentication preflight reviewed — 2026-09-10

Read user-supplied `/home/tux/uqc-auth-evidence/20260910T181636Z` via explicitly
requested `sudo -A` after ordinary filesystem access was denied. Identity records
session 5, UID 1001, seat0/tty3, Type=wayland, Active=yes, Remote=no. Session inventory
shows one tux graphical login plus its user manager. Recorded tux processes and
user services show no known competing Polkit agent. Agent-named processes belong
to UID 1000 and are left untouched. Journal contains startup lines only; journal
silence is not treated as registration-absence proof.

Policy requires auth_admin for all three implicit exec cases. Versions match the
kit (hyprpolkitagent 0.1.3-10, Qt base 6.11.2-3/declarative 6.11.2-1); agent links
Qt6 and recorded linkage has no missing dependencies. Reviewed collection commands
exit 0. These are preflight snapshot results, not registration/prompt acceptance.
Next user step is the guarded agent launch in the same tux login, then registration
verification in a second prepared terminal. No challenge before registration PASS.
No service changes or agent launch performed by the assistant.


### Third-party authentication registration PASS — 2026-09-10

User returns helper output: "PASS: registration reply, current authority, agent
PID and login session match." Run: `/home/tux/uqc-auth-evidence/20260910T181636Z`.
Record the reported live registration verification; prompt appearance, masking,
keyboard behavior and cancellation remain pending. Next user step is `challenge`
in the second prepared tux terminal while the helper's agent remains running.
The challenge repeats registration checks before its REGISTERED confirmation and
runs only `pkexec --disable-internal-agent /usr/bin/true`. Inspect using disposable
text only, erase it and cancel; no credential submission. No prompt or exit 0 is
not a cancellation pass. After recording the result, Ctrl+C in the agent terminal
stops only that helper's child. Owned-agent checks remain separate and pending.

Documentation-only update; `git diff --check` passes. UQC-201 remains In Progress.


### Third-party authentication prompt/cancellation result — 2026-09-10

User reports prompt works as expected with no issue and cancels it; challenge
exits 127, helper agent exits -15 after termination. Read-back via authorized
sudo -A confirms challenge.txt records Not authorized/exit_status=127 and agent.json
records exit_status=-15 (SIGTERM), PID 106726, session 5 and the expected third-party
executable/prefix. registration.json is present following the reported live PASS.
Evidence: `/home/tux/uqc-auth-evidence/20260910T181636Z`. This establishes recorded
cancellation/cleanup alongside positive user prompt feedback, not success based
on exit code alone. Requested scale was 1; detailed created-control origin and
actual scale correlation remain pending. Other scales/compositor gates stay open.

Next user step is a fresh owned-agent preflight using owned-auth/auth-test.py in
the same real tux login, after the third-party helper has exited. Review the new
preflight before launching the owned agent; do not reuse the third-party run path.
GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or live
input automation. UQC-201 remains In Progress.


### Owned-agent preflight reviewed — 2026-09-10

Reviewed `/home/tux/uqc-auth-evidence/20260910T192833Z` using user-authorized sudo -A.
Snapshot confirms active local session 5, UID 1001, seat0/tty3, Type=wayland, with
one tux graphical login. No known competing tux authentication agent appears in
recorded processes/services; the earlier third-party agent is absent. Other users'
agents remain untouched. Policy requires auth_admin; Qt/agent package versions
match. Owned executable linkage resolves libholonight_config from the prepared
prefix, with Qt6 and no missing dependencies. Collection commands reviewed exit 0.
Journal contains prior denied challenge entries; these are historical, not proof
of present registration status or a new preflight failure.

Next step is owned-agent launch at embedded default, Qt scale 1, then registration
verification in a second prepared terminal. No challenge before live registration
PASS. This preflight does not establish prompt/registration acceptance.
GUIDED.md/TASKS.md updated; `git diff --check` passes. No product changes/tests or
agent launch by the assistant. UQC-201 remains In Progress.


### Owned-agent registration PASS — 2026-09-10

User reports registration passed for owned-agent run
`/home/tux/uqc-auth-evidence/20260910T192833Z`, after the reviewed preflight and
requested embedded-default/Qt-scale-1 launch. Record reported live registration
success; prompt behavior/cancellation and control-origin review remain pending.
Next user step is owned-auth/auth-test.py challenge in the second prepared tux
terminal. It rechecks registration before REGISTERED confirmation; inspect with
disposable text only, erase and cancel without credential submission. Report
challenge exit and then stop the helper's agent via Ctrl+C in its own terminal.
No prompt or exit 0 is not cancellation acceptance.

GUIDED.md/TASKS.md updated; `git diff --check` passes. Documentation-only, no product
tests or live input automation. UQC-201 remains In Progress.


### Owned-agent prompt findings — 2026-09-10

For `/home/tux/uqc-auth-evidence/20260910T192833Z`, user reports:

- User dropdown is visually empty while reserving space for two users. Actual
  model roles, delegate creation and geometry remain uninstrumented.
- After entering a wrong password and activating Authenticate, an authentication
  error appears and the password input disappears, but its Password label remains.
- No other functional/rendering issues observed in the exercised prompt.

This run included user-initiated failed authentication, beyond the requested
cancellation-only sequence. Do not request further failed submissions or record
cancellation success without a returned result. Final cancellation/challenge exit
and agent cleanup remain pending. Submitted text is neither requested nor recorded.

Read-only shell QML review finds IdentitySelector derives from HnIconComboBox but
supplies its own avatar/text delegate requiring identity-model roles. Blank rows
must be diagnosed separately from earlier default-delegate hover disappearance.
AuthenticationDialog's promptLabel visibility depends only on nonempty text, while
responseField requires lifecycleState == 2 and textInput. This differing visibility
condition can retain the label after the input is hidden; runtime error-state and
retry expectations need reproduction before repair. No product edit or test run.

Next: cancel the remaining prompt if open, report challenge exit, and stop the
helper's owned agent with Ctrl+C in its original terminal, reporting agent exit.
GUIDED.md/TASKS.md updated; `git diff --check` passes. UQC-201 remains In Progress;
owned-agent prompt acceptance has unresolved findings.


### Owned-agent cancellation completion failure — 2026-09-10

User reports Cancel closes the prompt but the parent Python challenge helper keeps
running and requires Ctrl+C. Stopping the agent reports exit 0. Read-back of run
`/home/tux/uqc-auth-evidence/20260910T192833Z` confirms agent.json exit_status=0,
PID 111916 and expected owned executable; challenge.txt is absent. Therefore no
normal challenge exit/cancellation pass exists. This follows the reported failed
password submission; cancellation without a preceding failure is not separately
established. No further submissions requested.

A current UID/PID/command process listing finds no pkexec or owned Polkit agent
remaining. No process was killed by the assistant. Cancellation completion remains
a separate functional failure from blank identities and orphaned prompt label.
Read-only source review shows coordinator cancellation intends to complete the
active request false and the listener bridge returns a GTask boolean; this does
not establish where runtime completion was lost. The helper writes challenge.txt
only after its blocking subprocess.run returns. No broad authentication log or
submitted text was read/published; diagnosis needs bounded completion evidence.

Next independent guided surface is owned askpass, direct invocation at default
style/Qt scale 1 with stdout discarded, disposable text and cancellation only.
Owned Polkit failure remains open; its other style/scale checks are deferred for
investigation, not passed. GUIDED.md/TASKS.md updated; `git diff --check` passes.
No product edits/tests or live UI automation. UQC-201 remains In Progress.


### Owned askpass default scale-1 cancellation — 2026-09-10

User reports cancellation with `askpass exit=1`, no observed issues, and expected
keyboard/mouse behavior for the requested direct embedded-default/Qt-scale-1 run.
Record positive user-operated cancellation and interaction feedback; actual
control-origin/scale correlation remains pending. This is independent of the
owned Polkit cancellation-completion failure and does not resolve it. No credential
submission is reported; stdout was directed to /dev/null by the guided command.
Log reference: askpass.log under the current UQC_SESSION_RUN (full path pending).

Next comparison: direct askpass at default style/Qt scale 1.25, separate log,
disposable text then cancellation only. Fusion and Sway remain pending.
GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
live UI automation. UQC-201 remains In Progress.


### Owned askpass default scale-1.25 cancellation — 2026-09-10

User reports exit code 1 and no issues for the requested embedded-default askpass
run at Qt scale 1.25. Both tested default-style scales now have positive user
cancellation observations; control-origin/actual-scale correlation remains pending.
Log reference: askpass-scale125.log under current UQC_SESSION_RUN. Owned Polkit
findings remain unresolved independently.

Next is direct askpass Fusion at Qt scale 1 with a separate log and cancellation
only. GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests
or live UI automation. UQC-201 remains In Progress; Sway and other gates pending.


### Owned askpass Fusion scale-1 cancellation — 2026-09-10

User reports exit code 1 and no issues for the requested Fusion askpass run at Qt
scale 1. Record positive cancellation/interaction observation, with control-origin
and actual-scale correlation pending. Log: askpass-fusion-scale1.log under the
current UQC_SESSION_RUN. Next is Fusion at Qt scale 1.25 with a separate log and
cancellation only, completing this session's requested askpass style/scale cases.
This does not complete Sway, activation or other outstanding integration gates.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
live UI automation. UQC-201 remains In Progress; prior failures remain open.


### Owned askpass Fusion scale-1.25 border finding — 2026-09-10

User reports cancellation exit 1, with one rendering failure: unfocused text field
has an apparently clipped/thinner left border, roughly half the thickness of its
other three edges. Focused border/ring is intact. Requested mode is Fusion at Qt
scale 1.25; log is askpass-fusion-scale125.log under current UQC_SESSION_RUN. Record
successful reported cancellation separately from failed border appearance; do not
mark all askpass cases visually passed. Earlier default scale-1/1.25 and Fusion
scale-1 observations remain as reported.

Read-only source review identifies shell-owned AuthenticationPrompt.qml overriding
Controls.TextField.background with a Rectangle, radius 5 and border width 1 when
unfocused/2 when activeFocus. Thus this border is application-supplied, not Fusion's
stock background. AuthenticationDialog has a clipping scroll area; fractional
position/rasterization and ancestor clipping are candidates requiring geometry/
rendering reproduction. Neither clipping nor exclusive Fusion applicability is
proven from the visual report. No product edits/tests or live input automation.

Next step is to obtain the current UQC_SESSION_RUN path and correlate retained
application/askpass evidence before remaining activation/session gates. No user
need to repeat this border failure now. GUIDED.md/TASKS.md updated;
`git diff --check` passes. UQC-201 remains In Progress; all existing failures open.


### Hyprland run correlation checkpoint — 2026-09-10

GUIDED.md now records the complete process selector/scale/exit inventory for
hyprland-j97jound. Saved PID records correlate application runs to session 5 and
prefix discovery; exact per-action origins remain incomplete. Selected logs add
provider ComboBox implicitHeight binding loops, an initial Haruna SIGABRT and
application/Kirigami diagnostics requiring classification. Missing separately named
askpass-scale125.log is an evidence gap, not a retraction of the user's observation.
Private summary: `.cache/uqc201-guided-qht3_tjs/review-20260910/session-summary.json`.
See GUIDED.md for exact references and limits. No raw logs, credentials, product
files or pins changed; read-only sudo -A used as requested. `git diff --check`
passes. No product tests run. UQC-201 remains In Progress, initiative Accepted;
next is connection/environment review before activation.


### Connection verification / askpass log clarification — 2026-09-10

User returns socket-peer helper output: XDG_SESSION_ID=5,
XDG_RUNTIME_DIR=/run/user/1001, WAYLAND_DISPLAY=wayland-1,
QT_QPA_PLATFORM=wayland and QT_QPA_PLATFORMTHEME=holonight. This matches the prepared
login. Treat as returned helper verification, not evidence of activation delivery.

User clarifies the default askpass scale-1.25 command was edited manually from the
scale-1 command without changing the output filename. Thus askpass.log represents
the later default scale-1.25 run by user correlation; shell redirection overwrote
the original scale-1 log. The absent askpass-scale125.log is explained, not a missing
scale-1.25 run. Original scale-1 cancellation/interaction remains user-reported,
without a separately preserved log. Fusion logs remain separate. This supersedes
the preceding filename ambiguity; no actual scale is inferred from log contents.

Reviewed staged Settings D-Bus service: org.holonight.Settings Exec points directly
to the configured /tmp prefix binary. Desktop entry is DBusActivatable=true with
Exec=holonight-settings. Next user step imports the named compositor/discovery/
disposable-profile variables into the private test bus only, keeping owned style
selectors unset, then requests StartServiceByName for Settings after closing any
existing Settings instance. Do not import into a systemd manager in this step.
A returned service start and visible window still need actual PID/origin correlation.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
external activation performed by the assistant. UQC-201 remains In Progress.


### Settings private-bus activation observed — 2026-09-10

User reports Settings opened after StartServiceByName on the prepared private bus;
returned value is `u 1` (service started). This follows the requested named-variable
bus environment update. No systemd manager import was requested. Record successful
user-observed D-Bus launch, not yet complete process/control-origin acceptance.
Next: query GetConnectionUnixProcessID for org.holonight.Settings on that same bus,
then collect the live process using guided-app.py collect and inspect its saved
executable/environment/maps. Leave Settings open until collection completes.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
activation performed by the assistant. UQC-201 remains In Progress.


### Settings D-Bus process correlation — reviewed 2026-09-11

Read user-supplied `hyprland-j97jound/collect-1789074883533653402` via authorized
sudo -A. pid-119183.json records collection at 2026-09-10T21:14:43Z, actual executable
`/tmp/holonight-uqc201-8r1jtlln/prefix/bin/holonight-settings`, session 5, unset
QT_QUICK_CONTROLS_STYLE/QT_QUICK_CONTROLS_CONF and unset QT_SCALE_FACTOR. Platform
theme is holonight; QML/plugin/library and XDG_DATA_DIRS use the prepared prefix.
Unset process scale is not an independent measurement of effective output/DPR.

Saved maps confirm the prefix's Holonight style, Core/Controls/impl plugins,
platform-theme plugin and libholonight_config, alongside system Qt 6.11.2. Basic
library presence alone does not establish a rendered Basic control. Combined with
reported StartServiceByName `u 1` and visible Settings, this verifies staged binary
and native loading/environment for that private-bus launch. Individual created
control-origin review remains pending; no complete activation matrix pass claimed.

Next user step is desktop-entry launch of Settings after closing the current
instance. gtk-launch is installed; staged desktop entry is DBusActivatable and
Settings implements org.freedesktop.Application. Treat this as desktop-entry
activation, not proof of a specific graphical launcher's behavior. Collect the
resulting bus PID separately. No systemd manager environment changes performed.
GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
live UI automation. UQC-201 remains In Progress.


### Settings desktop-entry process correlation — reviewed 2026-09-11

User collected PID 123471 following the requested gtk-launch desktop-entry check.
Read `hyprland-j97jound/collect-1789076121579441076/pid-123471.json` and maps via
sudo -A. Collection timestamp is 2026-09-10T21:35:21Z; executable is the prepared
Settings binary, session 5, style/conf and QT_SCALE_FACTOR unset. QML/plugin/library
and XDG_DATA_DIRS point to the kit; platform theme is holonight. Maps confirm all
four staged style/shared QML plugins, platform-theme plugin and config library.
PID differs from the earlier direct D-Bus launch (119183).

This correlates the new process to the expected staged installation following
the requested desktop-entry action; no separate window-open observation or actual
per-control origin review was supplied in this reply. Do not claim graphical
launcher integration or complete activation acceptance from these maps alone.
Next is owned AI's installed org.holonight.Chat D-Bus service, after closing Settings
and any existing AI instance. Preserve disposable provider-disabled configuration.
GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
activation performed by the assistant. UQC-201 remains In Progress.


### AI private-bus process correlation — reviewed 2026-09-11

Reviewed user-supplied `hyprland-j97jound/collect-1789076363003755155` via sudo -A.
PID 124120 metadata (2026-09-10T21:39:23Z) identifies prepared holonight-chat,
session 5, style/conf and QT_SCALE_FACTOR unset, holonight platform theme and
prefix QML/plugin/library/data discovery. Maps confirm staged Holonight style,
Core/Controls/impl, platform-theme and config libraries. This matches the intended
owned default installation following the requested D-Bus launch. The user did not
separately supply StartServiceByName result or window-open observation; retain
those limits and outstanding created-control-origin correlation.

Next is third-party desktop-entry activation of NeoChat. Installed D-Bus metadata
uses /usr/bin/neochat --dbus-activated. Set QT_QUICK_CONTROLS_STYLE=Holonight in the
test terminal and update that one variable in its private bus for third-party
selection; this deliberately differs from owned embedded-default checks. No systemd
manager import. Inspect resulting process via bus PID and collect helper. This
selector remains set for subsequent third-party checks; restore owned defaults
before any later owned activation checks.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
activation by the assistant. UQC-201 remains In Progress.


### NeoChat desktop-entry process correlation — reviewed 2026-09-11

Reviewed `hyprland-j97jound/collect-1789076721712952633` via authorized sudo -A.
PID 124786 metadata at 2026-09-10T21:45:21Z identifies /usr/bin/neochat, session 5,
QT_QUICK_CONTROLS_STYLE=Holonight, unset conf/scale, holonight platform theme and
prepared prefix discovery. Maps show the staged Quick style/Core/impl, platform
theme, Widgets style and config library. This confirms selector propagation and
native staged loading following the requested desktop-entry launch, not each
rendered control's origin or a complete visual/activation pass. No separate
window-open observation was included with the collection path.

Next is Tokodon desktop-entry activation in the same test bus, retaining the
explicit third-party selector. Close NeoChat and any existing Tokodon first,
then collect Tokodon's bus-owned PID separately. No manager import or product
changes. GUIDED.md/TASKS.md updated; `git diff --check` passes. No product tests;
UQC-201 remains In Progress and outstanding evidence/acceptance gates stay open.


### Tokodon desktop-entry process correlation — reviewed 2026-09-11

Reviewed user-supplied `hyprland-j97jound/collect-1789076912749083724` via sudo -A.
PID 125839 metadata at 2026-09-10T21:48:32Z identifies /usr/bin/tokodon in session 5,
Holonight selector, unset conf/scale, holonight platform theme and prepared prefix
QML/plugin/library/data paths. Maps confirm staged Quick style/Core/impl, platform
theme, Widgets style and config library. This establishes expected process-level
propagation/loading after requested desktop-entry activation; no individual-control
origin or complete visual/activation pass inferred. No separate window-open
observation was included with this collection path.

Next is Haruna's desktop entry, which uses Exec=haruna %U and has no installed
D-Bus activation service per the accepted inventory. Close previous instances,
launch via gtk-launch, identify the tux-owned Haruna PID and collect it. Keep the
explicit third-party selector. No user-manager import or external activation by
the assistant. GUIDED.md/TASKS.md updated; `git diff --check` passes. No product
changes/tests. UQC-201 remains In Progress; unresolved gates stay open.


### Haruna desktop-entry process correlation — reviewed 2026-09-11

Reviewed `hyprland-j97jound/collect-1789077252212066228` via authorized sudo -A.
PID 126562 metadata at 2026-09-10T21:54:12Z identifies /usr/bin/haruna, session 5,
explicit Holonight selector, unset conf/scale, holonight platform theme and prepared
prefix discovery. Maps confirm staged Quick style/Core/impl, platform theme,
Widgets style and config library. This verifies process-level propagation/loading
following requested desktop-entry launch; it does not classify every created
control or close the whole activation gate. No separate visible-window statement
was supplied with this collection path.

Next is read-only review of tux's systemd user-manager environment and shell-unit
state before choosing the systemd test. Inspect selected variables only and retain
exact prior values/absence before any imports. Do not start/restart the normal
shell unit or modify manager state during preflight. Published kit includes shell
and templated Polkit units; authentication failures remain independently open.
GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests,
manager changes or activation by the assistant. UQC-201 remains In Progress.


### Systemd preflight and transient shell preparation — 2026-09-11

User returns loaded/inactive holonight-shell.service from /usr/share/systemd/user,
with ExecStart /usr/bin/holonight-shell-systemd (remaining pager text truncated).
Selected manager environment has runtime /run/user/1001, normal user bus
unix:path=/run/user/1001/bus, DISPLAY=:2, WAYLAND_DISPLAY=wayland-1,
XDG_CURRENT_DESKTOP=Hyprland and QT_QPA_PLATFORMTHEME=holonight. No manager mutation
has occurred. The installed unit is not the staged kit service.

Prepared /tmp/uqc201-systemd-shell.sh, retained privately as
.cache/uqc201-guided-qht3_tjs/review-20260910/systemd-shell.sh. It refuses the wrong
user/session/kit or an existing tux shell, then creates only transient
uqc201-shell-hyprland.service with explicit test-bus/discovery/disposable-profile
variables, unset style overrides, scale 1, no restart, and logs under the evidence
session. It runs the staged shell binary directly. It does not change the manager
environment or installed shell unit; no restoration of those is needed. Cleanup
is stopping this transient unit only. This is a transient systemd route check,
not shipped-unit/wrapper acceptance. The latter remains pending.

Shell syntax and wrong-user refusal pass (expected exit 1); launch was not executed
by the assistant. Next user step runs the helper, reports MainPID/ActiveState and
shell behavior, then collects MainPID. GUIDED.md/TASKS.md updated;
`git diff --check` passes. No product changes/tests. UQC-201 remains In Progress.


### Transient systemd shell process correlation — reviewed 2026-09-11

User reports uqc201-shell-hyprland.service ActiveState=active, MainPID=128370, then
collects `hyprland-j97jound/collect-1789078279550643791`. Read-back via sudo -A confirms
staged holonight-shell, collected 2026-09-10T22:11:19Z, QT_SCALE_FACTOR=1, unset
style/conf, session environment ID 5 and prefix discovery/platform theme. Saved
maps confirm staged style/Core/Controls/impl, platform-theme and config libraries,
plus a QML cache in the disposable session directory. XDG_SESSION_ID is environment
evidence, not proof of logind membership for a user-manager-launched service.

Bounded systemd-shell.log search found no TypeError, ReferenceError, binding-loop
or failed-component markers (rg exit 1 means no matches). This does not establish
correct visual behavior. User has not separately reported shell interaction or
confirmed test-unit cleanup in this reply. Transient launch/process propagation is
verified; shipped service/wrapper and individual created-control origins remain
pending. No manager environment or installed-unit changes were made.

Next: stop only uqc201-shell-hyprland.service if still running, verify it is no
longer active, and obtain the user's visual/interaction result for this route.
GUIDED.md/TASKS.md updated; `git diff --check` passes. No product changes/tests or
live UI automation. UQC-201 remains In Progress and all unresolved gates open.


### Transient systemd shell cleanup confirmed — 2026-09-11

User returns LoadState=not-found and ActiveState=inactive for
uqc201-shell-hyprland.service. Record successful stop/collection of the temporary
unit. Manager environment and installed shell unit were not modified by this
check, so no restoration of those is required. Process propagation/loading passed;
visual/interaction result for this specific systemd run remains unreported.
Do not substitute earlier terminal-launch feedback or close shipped-unit/wrapper
acceptance. Before choosing the next remaining integration batch, obtain this
one outstanding user observation without relaunching solely for repetition.

GUIDED.md/TASKS.md updated; `git diff --check` passes. No product edits/tests or
live UI automation. UQC-201 remains In Progress and known defects remain open.


### Transient systemd shell visual result / Sway handoff — 2026-09-11

User confirms the systemd-launched shell behaved the same as the earlier scale-1
run: functional interaction with known topbar frame/background defects. Combined
with saved PID/environment/maps and confirmed unit cleanup, this completes this
transient-route observation with explicit visual failures retained. It does not
establish shipped-unit/wrapper acceptance or resolve scale-1.25 shell behavior.

Next guided batch is Sway in a fresh real tux VT login. Close remaining test apps,
exit the minimal Hyprland compositor and log tux out before logging in again and
running guided-session.py sway. Start Settings default at Qt/output scale 1/1 and
compare keyboard navigation, text editing, scrolling, selectors and placement.
Record compositor-specific differences rather than requiring repetition of every
known defect. The new session creates separate disposable configuration/evidence.

Keep Hyprland evidence intact. Private test-bus changes end with that bus; the
systemd manager was not modified. Existing repair findings, detailed control-origin
correlation, remaining style/scale and palette checks, shipped-service/wrapper,
owned Polkit completion and real pre-session greeter acceptance remain pending.
No full Hyprland or ecosystem acceptance is claimed. Restored Sway config and READY
marker remain present. GUIDED.md/TASKS.md updated; `git diff --check` passes.
No product edits/tests or live UI automation. UQC-201 In Progress, initiative Accepted.


### Findings consolidation and focus checkpoint — 2026-09-11

[FINDINGS.md](FINDINGS.md) is the canonical register for current repair status,
reproductions, owners, evidence limits and acceptance criteria. Chronological
observations above and in GUIDED.md are retained unchanged as historical evidence;
new observations are recorded once in the register. Broad manual acceptance is
paused. UQC-204 scope includes both shared form wrappers; remaining repair order is
Polkit cancellation completion, dropdown interaction, then the other owned packages.
Sway Settings equivalence is recorded in the register with its evidence limits.
UQC-201 remains In Progress and initiative Accepted; all existing failures and
integration gates remain open. Provider handoff and fresh focus kit follow local
verification and canonical publication.


### Published UQC-204 provider accepted — 2026-09-11

Accepted `65c806fb6a65cae9652dde7a69d595813973c1a9` from canonical holonight-qt
origin/main after successful push and independent `git ls-remote` confirmation.
Provider is clean; implementation is `e97b646`, followed by test naming/static
cleanup. Only the provider gitlink changes; all other product pins are preserved.
Verification and initial tool-path failure are recorded in the local SDD. This
completes repository-local UQC-204, not manual or ecosystem acceptance.

Next: release a fresh, focused Settings/AI kit from this provider. Do not modify
`/tmp/holonight-uqc201-8r1jtlln` or repeat broad Sway/application acceptance.
UQC-205 Polkit cancellation and UQC-206 dropdown interaction are next; all other
findings, shipped-service/compositor gates and real pre-session greeter remain open.


### Fresh focus-only kit released — 2026-09-11

New kit `/tmp/holonight-uqc201-focus-afv1kwth`, provider `65c806f`, configured
Settings/AI at unchanged pins. Build/installation results and exact private scripts
are in `.cache/holonight-uqc201-focus-afv1kwth`. Old released kit/evidence unchanged.

All four installed provider focus style/scale cases pass with host QML/config
masked; Settings and AI each pass all four installed selector/startup modes with
private buses and forbidden build discovery. Settings initially could not create
its private bus socket in the sandbox; rerun with permission passes. Syntax,
configured service paths, provider-source byte comparison and prefix hashes pass.
This is focused kit preparation, not an umbrella integration-suite rerun or a
shipped-service acceptance result. The kit has fresh disposable profile/session
helpers; no services, UI interactions or authentication were triggered on the desktop.

Next manual request is only [FOCUS.md](FOCUS.md): Settings and AI first/repeated
Tab/Backtab, including Context → Temperature → Slider, under default/Fusion at
1.25 in Sway. All unrelated defects remain open. UQC-201 In Progress; Accepted.


### Missing focus kit restored — 2026-09-11

The previous temporary focus directory was absent. Restored as
`/tmp/holonight-uqc201-focus-5ydxn45l` using the retained preparation script, with
its original scripts/logs/evidence preserved. Provider `65c806f`, Settings
`2508635`, AI `7e25e78` and all gitlinks remain unchanged; participating source
working trees are clean. Retained dependency caches referenced deleted prefixes,
so config, system-services, shell-config and Qt were reconfigured/rebuilt before
staging. Settings and AI were freshly configured, built and installed against
the new prefix. No product source or API changes.

Exact restoration scripts, pins, commands and results are retained in
`.cache/holonight-uqc201-focus-5ydxn45l/`: `prepare-focus.py`, `verify-focus.py`,
`finalize-checks.py`, `results.jsonl`, `verification.jsonl`, `final-checks.json`
and `logs/`. The preparation entry command was
`python3 .cache/restore-uqc204-focus.py`; verification and final checks used
`python3 .cache/holonight-uqc201-focus-5ydxn45l/verify-focus.py` and
`python3 .cache/holonight-uqc201-focus-5ydxn45l/finalize-checks.py`.

Installed wrapper regressions pass 8/8 in each HoloNight/Fusion × scale 1/1.25
case with host provider QML/config masked. Settings and AI each pass all four
installed startup/selector modes with private buses, disposable profiles and the
entire repository root forbidden in startup discovery. The first Settings attempt
failed because the sandbox denied its private D-Bus socket; the permitted rerun
passes, and append-only logs/results retain the failure. Helper Python/shell
syntax, Sway output scale 1, disabled AI providers/title generation, configured
activation paths, installed wrapper source parity, runtime linkage and all 189
prefix SHA-256 checks pass. `git diff --check` passes.

Regenerated helpers use disposable configuration; FOCUS.md and the kit's guide
contain only the short focus request. READY is created after these checks. This
is a focused kit restoration, not umbrella integration or manual acceptance.
Next: the four [FOCUS.md](FOCUS.md) commands from a fresh real tux Sway login.
Record returned observations once in FINDINGS.md and close only supported findings.
Broad acceptance remains paused, initiative Accepted, UQC-201 In Progress, and
unrelated repairs remain pending. No live desktop interaction was automated.


### Focus acceptance recorded — 2026-09-11

The returned four-run manual result and evidence inventory are recorded once in
[FINDINGS.md](FINDINGS.md#manual-focus-acceptance--2026-09-11). F01/F02 are closed;
F03 app-specific attribution remains unconfirmed. Broad acceptance stays paused,
initiative Accepted and UQC-201 In Progress. UQC-205 owned Polkit completion is
next in the existing repair order; no new repair package is assigned here.
Documentation-only update; `git diff --check` passes. No product edits or tests,
kit mutation, live UI automation, or submodule changes.


### UQC-205 A03 cancellation checkpoint — 2026-09-11

Shell baseline `1320f37093e2148a224a4e8fbfaf4ac1b536c6a8` was clean and confirmed
on canonical origin/main before Ready → In Progress. Scope is A03 only; A01/A02/A04
remain deferred until after the dropdown checkpoint. Provider `65c806f` and all
other product gitlinks remain unchanged. The shell build/CI references now match
that accepted provider.

The [shell-local SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-205.md)
records baseline reproduction, the missing-GError repair, exactly-once lifecycle
coverage, actual D-Bus reply and bounded requester-exit assertions, four style/scale
authentication checks, full suite and static/install verification. This checkpoint
is a locally verified repair handoff, not A03 manual acceptance or ecosystem integration.

[One manual direct-cancel check](CANCELLATION.md) is requested from the fresh kit
`/tmp/holonight-uqc205-irzzhjcz`, default HoloNight at Qt scale 1.25 in a real tux Sway
login. Installed private-authority cancellation/requester and shutdown checks pass;
all 204 staged prefix file hashes and helper syntax are recorded in
`.cache/holonight-uqc205-irzzhjcz/`. The challenge has a 60-second bound and records
normal exit, timeout, signal exit and interruption distinctly. Only normal denied
completion with prompt observation can support A03 closure. Manual observations
will be recorded once in FINDINGS.md; no result is inferred from releasing the kit.

UQC-201 remains In Progress, initiative Accepted, broad acceptance paused. UQC-206
remains Planned until A03 acceptance; no dropdown assignment was made.

Shell handoff `9a19a969b9ac7455e4947be40eecfaf1d25307a0` was published to canonical
origin/main and revalidated with `git ls-remote`; the shell source tree was clean
before pinning. Final local `task test`: 1163/1163 pass (229.84 s), including the
installed-launch matrix. Remote CI is not asserted by this local handoff. The
pre-existing focus-result documentation edits remain unstaged in this session.


### UQC-205 accepted; UQC-206 preparation — 2026-09-12

The [canonical manual result](FINDINGS.md#manual-polkit-cancellation-acceptance--2026-09-12)
closes A03 and completes UQC-205's A03-only scope. Historical failed observations
remain intact. No product files or gitlinks changed for this documentation update;
shell remains `9a19a96`, provider `65c806f`.

The [UQC-206 investigation preparation](UQC-206.md) separates D01–D04 reproductions
and identifies existing provider ownership and coverage. It remains Planned: a
provider-local SDD, canonical baseline revalidation and reproductions are still
required before Ready assignment. No dropdown repair has started. A01/A02/A04 stay
pending; UQC-201 In Progress, initiative Accepted, broad acceptance paused.

Verification: documentation links and `git diff --check`. No product tests rerun
for this documentation-only acceptance record. Existing focus-result edits remain
unstaged and preserved.


### UQC-206 reboot recovery and local repair — 2026-09-12

Ready after canonical provider `65c806f` confirmation, consumer-model inspection,
local SDD and isolated D01/D03 reproduction; then assigned provider-only and moved
In Progress. The [canonical findings checkpoint](FINDINGS.md#uqc-206-local-dropdown-repair-checkpoint--2026-09-12)
records repair status and limits; the provider SDD owns implementation/verification.
Ten interaction cases pass in each style/scale process, full provider 69/69 including
installed consumer passes. Persistent `.cache/uqc206` replaces wiped development
dependencies and retains logs. Existing focus-result edits are preserved.
D02/D04 and manual acceptance remain pending; no publication or gitlink changes.
UQC-201 In Progress, initiative Accepted, broad manual acceptance still paused.


### D04 user clarification — 2026-09-12

The [canonical clarification](FINDINGS.md#d04-clarification-and-stronger-reproduction--2026-09-12)
records list-start/no-highlight behavior and the stronger visibility reproduction.
Provider tests now cover mouse reopening and actual scene containment for both
opening routes. Baseline icon-composite failures identify hidden-list ownership;
no additional product QML or gitlink change. Full manual D04 acceptance remains open.

Verification: 7/7 focused/composite/installed CTests pass (43.52 seconds), including
12 dropdown cases per style/scale process. Formatting and whitespace checks pass.


### UQC-206 candidate scripts and kit — 2026-09-12

At the user's request, prepared the [focused dropdown scripts](DROPDOWNS.md) and
verified candidate kit `/tmp/holonight-uqc206-wou7oqyf`. It explicitly contains the
unpublished working-tree provider patch; no canonical handoff/gitlink change.
Installed dropdown regressions pass in four style/scale processes; both Settings
and greeter pass four startup modes. Helper refusals/restore smoke and 215 hashes
pass; sandbox socket failure and permitted rerun are retained. Complete archive,
commands and logs persist in `.cache/holonight-uqc206-wou7oqyf` for reboot recovery.
Next is user-operated Settings Appearance and greeter demo dropdown verification
at 1.25 in a fresh tux Sway session. D01–D04 remain open for their outstanding
manual/evidence gates. UQC-206/UQC-201 In Progress; initiative Accepted.


### Dropdown manual checkpoint accepted; new input findings — 2026-09-12

[Canonical acceptance/evidence](FINDINGS.md#manual-dropdown-acceptance-and-remaining-height-loop--2026-09-12)
records four Settings/greeter default/Fusion runs with mouse/keyboard success and
verified selectors/scale environment/PIDs/exits. D01/D03/D04 accepted for the owned
checkpoint. Settings default still logs six D02 height loops; UQC-206 stays In
Progress. Host config-library loading is an explicit manual-kit limitation.

[New F06/F07 findings](FINDINGS.md#pointer-and-keyboard-interaction--new-findings-2026-09-12)
separate shared competing hover feedback from launcher selection overriding Enter.
Source inspection identifies the launcher's unconditional hover selection; isolated
reproduction and local SDDs are prerequisites to assignment. No product edits,
publication, pin change, live UI automation or new manual request. Documentation
whitespace checks pass; no product tests rerun for this record-only change.


### Next iteration provider handoff — 2026-09-12

Accepted published provider `4dfa8030df59b896ee7d8ef6a8d6ff6ab960c040`, including
separate sizing commit `975bf09` and shared F06 policy commit `4dfa803`.
Canonical origin/main availability verified via ls-remote; provider tree clean.
The provider SDDs record failing regressions, 73/73 full local tests, final
11/11 focused/installed checks and lint limitations. Only provider gitlink changes.

Full Settings log context identifies the D02 warnings during Weather ComboBox
construction, with viewport debug logging enabled by the kit. Font attribution
was an earlier inference; preserve font coverage but target Weather for D02 manual
confirmation. D01/D03/D04 acceptance remains valid. F06 repository work is Done;
manual confirmation is pending. UQC-214 waits for its isolated reproduction/Ready
assignment. UQC-201 remains In Progress, initiative Accepted; no broad integration.


### Published launcher handoff — 2026-09-12

Accepted shell `f55cb5fc3b9ca7fd8f74f2b968836b5f36f9e235`, confirmed available on
canonical origin/main with a clean shell tree. Provider remains published/pinned
`4dfa803`. The local SDD records the failed stationary-pointer reproduction,
1167/1167 full CTests, final 9-case compiled checks in both styles/scales, QML
lint/type results and initial sandbox/import-path failures. Only shell gitlink
changes at this checkpoint. F07 manual confirmation remains pending; UQC-201
In Progress, initiative Accepted, broad integration still pending.

### Fresh dropdown/input kit and isolation evidence — 2026-09-12

Released `/tmp/holonight-uqc206-qa20p_jh` from published provider `4dfa803` and
shell `f55cb5f`, with Settings/greeter at unchanged pins. The kit's generated
`README.md` contains the concrete [targeted manual request](INPUT.md). Existing
`wou7oqyf` kit/evidence and the intermediate `iipfhve5` archive are preserved.
No broad integration tests or live desktop pointer/focus automation were run.

Actual Settings acceptance enters Appearance and Weather with viewport debug
logging enabled and passes without the reproduced binding loop in both styles
at Qt scales 1 and 1.25. Twelve Settings/greeter/shell runtime inspections also
pass: selected environment and actual mappings show staged HoloNight libraries,
including config, and no host provider fallback. Shell inspections use a private
headless compositor; no real app launch is used for launcher selection tests.
Installed dropdown/input regressions, four Settings startup modes and four
greeter startup modes pass with host HoloNight QML/libraries masked.

The app-launch helper explicitly restores LD_LIBRARY_PATH for every child and
writes `isolation.json`; missing evidence or host/outside-prefix mappings are
incomplete checks. Five Python regressions cover mapping requirements/fallback
and launcher supervisor termination. The initial wrapper lost evidence on Ctrl+C;
the supervisor regression fails on the intermediate kit and passes with exec-based
handoff. A new kit was built instead of mutating that released intermediate kit.

Persistent archive:
`.cache/holonight-uqc206-qa20p_jh/holonight-uqc206-qa20p_jh.tar.gz`

Archive SHA-256:
`0dca74b803e01bc18ee8f8221ec8cd40ad0a474cf47a926cee389b051f222759`

Reboot restoration from the umbrella, before switching to tux:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-dropdown-kit.py \
  .cache/holonight-uqc206-qa20p_jh/holonight-uqc206-qa20p_jh.tar.gz
```

The restore was exercised at the exact original path; 244 file hashes pass and
its original directory is retained with `-before-restore` suffix. Four refusal
checks protect wrong-session launches and existing released/restored kits.
Preparation scripts, commands, initial sandbox failure, permitted rerun, runtime
logs, final checks and refusal results are retained under that `.cache` directory
and `.cache/uqc206/input-kit-*`. Prior kit checksums remain valid. Source syntax,
Python tests and whitespace checks pass. The released directory is immutable.

D02 has warning-free affected-application automated evidence; the targeted real
session remains the confirmation checkpoint. F06/F07 remain open until returned
manual observations support closure. D01/D03/D04 acceptance is preserved. UQC-201
stays In Progress and initiative Accepted, with broad integration pending.

### Pause for poweroff — 2026-09-13

The user reports that an opened dropdown still selects the row under a stationary
pointer. Record this as a failed manual input acceptance check, not closure of
F06. See [the canonical manual failure and next-session handoff](FINDINGS.md#manual-dropdown-failure--next-session-handoff--2026-09-13).
Investigation and repair are deferred at the user's request. Resume from provider
`4dfa803` / shell `f55cb5f`, preserving working-tree changes and the immutable
`qa20p_jh` kit/archive; use the restoration command above after reboot. F07 and
D02 retain their existing pending manual-confirmation status.

### Stationary-pointer provider handoff — 2026-09-13

Accepted clean published provider `2965d8dcd7d4f5a1361acfdab66688539e9c5d3e` after
canonical origin/main confirmation. UQC-213 was reopened Ready → In Progress after
isolated reproduction at `4dfa803`; its follow-up is repository-locally Done.
[Canonical findings](FINDINGS.md#stationary-pointer-selection-repair--2026-09-13)
retain manual uncertainty and the outstanding F06 gate. Only provider gitlink
changes. Shell stays `f55cb5f`; no consumer implementation or broad integration.

Verification: 8/8 focused input/dropdown CTests, 73/73 provider suite (43.64 s),
installed-consumer test, formatting and whitespace pass. QML lint exits 0 with
existing warnings documented locally. Logs: `.cache/uqc206/stationary-*.log`.
The initial sandbox SSH failures and successful permitted publication/confirmation
are retained in session output. [INPUT.md](INPUT.md) now requests only dropdown
keyboard scrolling, Enter target, settled reopen and pointer/click recovery.
Existing poweroff/failure records are preserved in this checkpoint. UQC-201 remains
In Progress and the initiative Accepted; F06 is not manually closed.

### Fresh stationary-pointer retest kit — 2026-09-13

Released immutable kit `/tmp/holonight-uqc206-06_tsrg6`, built from published
implementation `2965d8d` (empty provider.patch), shell `f55cb5f`, and unchanged
Settings/greeter pins. Final provider pin `927d9e9` only corrects the documented
regression count to 22 cases; canonical publication confirmed and provider clean.
No product changes separate the kit implementation from that documentation pin.

Preparation commands:

```sh
python3 docs/initiatives/unified-qtquick-controls/prepare-dropdown-kit.py
python3 docs/initiatives/unified-qtquick-controls/prepare-dropdown-kit.py --resume /tmp/holonight-uqc206-06_tsrg6
```

The first run failed at the sandbox-denied private D-Bus socket; the permitted
resume passes. Full commands/results and logs persist in
`.cache/holonight-uqc206-06_tsrg6/`; top-level logs are
`.cache/uqc206/stationary-kit-preparation{,-permitted}.log`.
Installed input/dropdown checks pass in both styles/scales with host provider
modules/libraries masked. Settings and greeter each pass all four startup modes;
actual Settings Appearance/Weather lifecycle passes in four styles/scales;
12 Settings/greeter/shell runtime mappings pass staged-library isolation. Shell
inspection uses a private headless compositor. Five evidence-helper regressions,
Python/shell syntax, provider source parity, 244 final file hashes, documentation
links and whitespace checks pass. No live desktop pointer/focus automation.

Persistent archive:
`.cache/holonight-uqc206-06_tsrg6/holonight-uqc206-06_tsrg6.tar.gz`

SHA-256: `05a7fa0cb9afcc451e71db055efcf2ce9ed1f3b03f2cda3b7c47132c1a1cf03e`

Restore after reboot from the umbrella if the original path is absent:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-dropdown-kit.py \
  .cache/holonight-uqc206-06_tsrg6/holonight-uqc206-06_tsrg6.tar.gz
```

From a fresh real tux VT login, start:

```sh
python3 /tmp/holonight-uqc206-06_tsrg6/guided-session.py sway
```

Follow the kit README's focused [INPUT.md](INPUT.md) dropdown check only. F06,
D02/F07 manual gates and broad integration remain open. Prior kits/archives and
manual observations remain unchanged. UQC-201 In Progress; initiative Accepted.

### User clarifies opening/Space commitment — 2026-09-13

[Canonical clarification](FINDINGS.md#manual-sequence-clarified--2026-09-13) identifies
Settings/greeter under HoloNight and Tab → Space → Space committing the stolen row
without a scrolling prerequisite. Provider adds direct keyboard/open/Space-close
coverage; both prior/current implementations pass that isolated sequence, including
an unchanged-position mouse event. Exact opening-time failure remains unconfirmed
offscreen; the earlier scroll regression must not substitute for this manual gate.
INPUT.md adds that exact first step. Released `06_tsrg6` kit/archive stays immutable
and usable; no product QML, publication or gitlink update in this clarification.

Final clarification verification: 5/5 focused dropdown/installed CTests pass
(42.53 s), including both styles at scales 1/1.25. Formatting, documentation
links and whitespace pass. Test/documentation changes remain uncommitted; product
implementation, published pins and released kit remain unchanged.

### F06 reported sequence manually accepted — 2026-09-13

[Canonical acceptance](FINDINGS.md#manual-stationary-pointer-acceptance--2026-09-13)
records the user's successful retest of Settings/greeter under HoloNight in
`06_tsrg6`. Close F06 for the reported stationary-pointer Tab → Space → Space
behavior. UQC-213 repository work remains Done. D02/F07 and unrelated integration
gates retain their existing status; UQC-201 In Progress, initiative Accepted.
Documentation-only acceptance update; links and whitespace checked. No product
tests rerun, publication, gitlink change or released-kit mutation. Existing
uncommitted test/documentation follow-up remains preserved.

### Batch 1 preparation and published provider handoff — 2026-09-13

Accepted provider `68b7069cc10b85cf0ce591b89cf8c1494bf316b3` after canonical
origin/main confirmation. This adds the clarified Tab → Space → Space test and
acceptance documentation only; product behavior matches kit implementation `2965d8d`.
The direct sequence passes both baseline and repaired offscreen implementations;
the failing scroll regression remains separate evidence. The final source/object/log
timestamps and retained `space-settled-verification.log` confirm the existing 5/5
focused/installed results apply; test content and dependencies are unchanged.
Formatting, relative documentation links and whitespace checked for the handoff.

The existing `06_tsrg6` kit has READY and all 244 SHA256SUMS entries pass. Its recorded
Qt base 6.11.2-3, Qt declarative 6.11.2-1, hyprpolkitagent 0.1.3-10, Sway 1:1.12-4
and Hyprland 0.56.2-3 match installed packages. No kit/archive mutation or rebuild.
Shell remains `f55cb5f`. Sandbox SSH access initially failed; permitted publication
and canonical confirmation succeeded. The umbrella checkpoint records clarification,
F06 acceptance and this provider gitlink; earlier pending checkpoints are published
with it. No D02/F07 result is inferred. Follow the three runs in [BATCHES.md](BATCHES.md).

### Batch 1 manual evidence recovered — 2026-09-13

[Canonical results](FINDINGS.md#settings-and-launcher-manual-results--2026-09-13)
record the user observations, all three recovered paths, PID/style/isolation checks,
Settings diagnostic scan, log hashes and remaining Fusion exit-evidence limitation.
UQC-206 owned-app checkpoint is Done; third-party warnings remain in UQC-201.
F07 behavior passes both styles; the user confirms deliberate Fusion session shutdown.
Batch 1 is complete. No
product changes, new tests, kit mutation or broad integration checks. Documentation
links and whitespace checked. Batch 2 authentication follows; all later gates remain open.


### Batch 2 authentication handoff and fresh kit — 2026-09-14

Starting umbrella `f505f0e`, shell `f55cb5f` and provider `68b7069` were clean and
confirmed on canonical main. The shell-local follow-up records Ready → In Progress
and its accepted scope. Accepted shell handoff `fffb1715bac5a57127af5e671033ac33335ffc16`
was published and confirmed with `git ls-remote`; shell is clean. Only its gitlink
changes; provider remains `68b7069`. Local work UQC-205-B2 is Done, not integration.

[Canonical Batch 2 findings](FINDINGS.md#batch-2-authentication-repair-checkpoint--2026-09-14)
close A02 using synthetic lifecycle/rendered evidence and retain A01/A04 manual
gates. Final shell `task test`: 1171/1171 passes (251.65 seconds), including existing
cancellation/queued/stale/shutdown, Askpass process and relocated launch checks.
The supplemental private graphics matrix passes both styles at scales 1/1.25;
formatting, QML lint/types, import/architecture, licensing and changed C++ analysis
pass. Existing unrelated QML warnings and initial sandbox/harness failures are
recorded in the local SDD. Remote CI 34785218986 was still running at kit release;
its licensing job passed. No remote green result is inferred from local tests.

Released `/tmp/holonight-uqc205-b2_vmvoyd51` from published sources. Its 218 hashes
and restoration at the exact original prefix pass; the pre-restoration directory
is preserved. Installed production Polkit cancellation/shutdown and compiled real
model checks pass in four styles/scales. Eight staged production Askpass/Polkit
inspections verify actual style, actual DPR, created QML origins and required
libraries, including configuration, with host HoloNight modules/libraries masked.
The existing build/relocated launch matrix also passes. Initial preparation supplied
the kit prefix to the build-prefix comparison; correcting that invocation resolved
the fixture mismatch. No product repair was inferred from that preparation failure.

The kit reuses the established real-login preflight, registration reply and bounded
challenge machinery. New helpers select style/scale, automatically index every
session run, retain PID-tagged loader module evidence despite non-dumpable processes,
and classify normal/signal/interrupted/timeout/forced cleanup separately. Five helper
regressions pass, including interrupted-agent evidence preservation; four actual
wrong-user/released-kit refusal checks pass. Python/shell syntax and whitespace pass.
Previous kits and historical instructions remain intact. No real credentials or
live desktop input were automated.

Persistent archive:
`.cache/holonight-uqc205-b2_vmvoyd51/holonight-uqc205-b2_vmvoyd51.tar.gz`

SHA-256: `510fc35dff132554841fe4024251405d609945ae7c69b8fba2798c7495ed73a8`

Preparation/verification commands and logs persist in the adjacent `.cache`
directory; reproduction and graphics evidence are in `.cache/uqc205-batch2/`.
Restore after reboot, only if the original kit path is absent:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-authentication-kit.py \
  .cache/holonight-uqc205-b2_vmvoyd51/holonight-uqc205-b2_vmvoyd51.tar.gz
```

Follow the [three targeted manual runs](AUTHENTICATION-BATCH2.md) in one fresh real
tux Hyprland login at output scale 1 / Qt scale 1.25. A02 requires no further failed
submission; A03 remains accepted. Record returned observations once in FINDINGS.md.
Batch 2 remains open for A01/A04 and manual shutdown outcomes. Other compositor,
successful-authentication and activation gates remain in Batch 8; Batch 3 follows
with Haruna crash/diagnostic classification. UQC-201 In Progress, initiative Accepted.


### Batch 2 manual evidence review — 2026-09-14

[Canonical acceptance and saved outcomes](FINDINGS.md#batch-2-authentication-manual-acceptance--2026-09-14)
close A01/A04 alongside already verified A02 and classify the saved process outcomes.
Batch 2 is closed; A03 and Batch 1 stay accepted. Batch 3 follows with Haruna
crash/diagnostic classification. Broader UQC-201 integration gates remain open.

Shell CI [34785218986](https://github.com/lebedenko/holonight-shell/actions/runs/34785218986)
is now completed successfully at the published implementation revision `fffb171`.
This supersedes the running-at-release status in the dated kit handoff above.
No product edits, gitlink changes or kit mutations accompany this acceptance record.
Verification: indexed session/runtime/registration/result evidence inspected read-only;
document links and `git diff --check` checked. Product tests were not repeated for
this documentation-only checkpoint.


### Batch 3 provider checkpoint — 2026-09-14

Accepted the verified rendering implementation handoff from provider
`fbffc872c31ad8c8c22d499a08c8259e781f0a51`, independently confirmed on canonical
origin/main before pinning. The provider is clean. Full local verification is
77/77 CTests, including installed acceptance; narrow regressions and static checks
are recorded in its [SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-207.md).
This is an implementation checkpoint, not manual Batch 3 acceptance. UQC-207 and
UQC-201 remain In Progress, and initiative status remains Accepted. Preserve the
[original-crash and compatibility evidence](FINDINGS.md#batch-3-investigation-and-rendering-repair--2026-09-14).


### Batch 3 focused kit — 2026-09-14

Fresh immutable kit: `/tmp/holonight-uqc207-8jhojhzb`.
Archive: `.cache/holonight-uqc207-8jhojhzb/holonight-uqc207-8jhojhzb.tar.gz`.
SHA-256: `ec3a85f73d2f8ab34e08b288ace245835c88bd92b354a4be8a972278f534a1f7`.
Exact repository revisions are in its `revisions.json`; gitlinks remain authoritative.

Restoration (only if the original kit path is absent):

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc207-8jhojhzb/holonight-uqc207-8jhojhzb.tar.gz
```

Preparation commands/results, twelve provider/AI/Settings acceptance logs, twenty
actual-process mapping/origin/outcome records and archive hashes are retained under
`.cache/holonight-uqc207-8jhojhzb/`. `prepare-rendering-kit.py` owns the procedure.
Seven collector/index tests and exact-path restoration pass. Required actual-app
DPR/focus-owner evidence remains explicitly incomplete, not inferred from configured
scale; see the [canonical record](FINDINGS.md#batch-3-investigation-and-rendering-repair--2026-09-14).
Use [RENDERING-BATCH3.md](RENDERING-BATCH3.md) for human-operated checks. UQC-207 stays
In Progress pending acceptance/investigation; UQC-201 stays In Progress and the
initiative Accepted. UQC-208–UQC-212 retain their original Planned state and scope.


Latest Batch 3 manual review: [results and external ownership](FINDINGS.md#batch-3-manual-review-and-external-ownership--2026-09-14).
This records failed acceptance, external dispositions and remaining unknowns;
Batch 3 and UQC-207 remain open. Earlier implementation checkpoints are historical.

### Batch 3 focused repair checkpoint — 2026-09-14

Canonical publication and clean provider confirmed before pinning `a7e50b0`.
Results and remaining evidence gaps: [canonical findings](FINDINGS.md#batch-3-focused-repair-iteration--2026-09-14).
UQC-201/UQC-207 remain In Progress and the initiative Accepted.

Fresh kit and restoration/measurement results are recorded once in the
[focused iteration findings](FINDINGS.md#batch-3-focused-repair-iteration--2026-09-14).
Use [focused human instructions](RENDERING-BATCH3.md); no Batch 3 closure or Batch 8
integration is claimed by this checkpoint.

Latest verified manual results and diagnostic conclusions: [canonical findings](FINDINGS.md#batch-3-focused-repair-manual-results--2026-09-14).

### Dropdown background repair checkpoint — 2026-09-14

The provider's diagnostic-triggered ComboBox background repair is published and
pinned after local verification and canonical availability confirmation. Its
[local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-207.md)
records scope; [findings](FINDINGS.md#batch-3-dropdown-background-repair--2026-09-14)
record reproduction, verification, remaining lifecycle uncertainty and acceptance
kit evidence once. Follow [the focused instructions](RENDERING-BATCH3.md) for
scale-1 NeoChat/Tokodon/Haruna checks. Actual-app acceptance is pending; UQC-201
and UQC-207 remain In Progress, and the initiative remains Accepted.

### Dropdown background manual handoff — 2026-09-14

The user accepts background coverage and geometry in all three applications at
scale 1. Tokodon's missing chevron is a separate open finding. See the
[acceptance record](FINDINGS.md#batch-3-dropdown-background-manual-acceptance--2026-09-14)
for the notes, verified earlier raw evidence and deferred chevron investigation. Do not
repeat accepted checks.
UQC-201/UQC-207 remain In Progress; the initiative remains Accepted.

The user has stopped the intermittent Tokodon chevron investigation unless a
concrete reproducible defect emerges. See the [deferral record](FINDINGS.md#tokodon-intermittent-chevron--investigation-deferred-2026-09-14).
This deferral neither reopens accepted background coverage nor establishes an
upstream or provider cause. No further manual comparison is requested.

### Batch 4 provider checkpoint — 2026-09-14

Accepted published clean provider `5d3f06e895be5b5a93ed07f8fe717a0fa6cc6cbb`
after canonical `ls-remote` confirmation. [Canonical results](FINDINGS.md#batch-4-palette-investigation-and-repair--2026-09-14)
record P01 external ownership, the scoped P02 repair and verification.
[Manual instructions](PALETTE-BATCH4.md) apply only to the fresh kit handoff.
UQC-208/UQC-201 remain In Progress and the initiative Accepted.

Latest [Batch 4 manual visual acceptance](FINDINGS.md#batch-4-manual-visual-acceptance--2026-09-15):
P02 passes all nine reported runs; P01 navigation alternation persists as an external
defect. All twelve raw runs pass evidence verification. UQC-208 is Done for scoped
provider work; UQC-201 remains In Progress. No repeat runs are requested.


### Batch 6 checkpoint — 2026-09-15

The user requested commits and a next-session note, with **no Batch 6 kit generated
in this session**. See [handoff](BATCH6-HANDOFF.md) for exact local/pinned revisions
and remaining publication, harness, installation and manual work. Canonical
investigation results are recorded once in [findings](FINDINGS.md#batch-6-investigation--2026-09-15).
The shell has two local test commits; publication is unconfirmed after the push
request was interrupted. Its umbrella gitlink remains `fffb171`. UQC-211/UQC-201
remain In Progress, UQC-215 Planned, and the initiative Accepted.


### Batch 6 publication resumed — 2026-09-15

Canonical shell main was still `fffb171` on resume. Published the two preserved
test/SDD commits and confirmed canonical `ab780d5d477400cdc70195d37783e9e080ee1d05`
with `git ls-remote` before updating the shell gitlink. Shell is clean; the prior
local verification remains applicable. No product implementation changed.

Corrected the proposed coordinate investigation to UQC-215: UQC-213 already
identifies the completed F06 package. Historical shell SDD references to the
proposed UQC-213 mean UQC-215; its scope/state remains Planned. Batch 6 harness
review and fresh kit preparation continue; no manual acceptance is implied.


### Batch 6 verified kit handoff — 2026-09-15

[Canonical release evidence](FINDINGS.md#batch-6-verified-investigation-kit--2026-09-15)
records the exact kit/archive/hash, 16 installed checks, 16 staged runtime
comparisons, observer/collector tests, restoration/refusals and remaining keyboard
observation gaps. Follow [SHELL-BATCH6.md](SHELL-BATCH6.md) for the focused manual
sequence. UQC-211/UQC-201 remain In Progress; UQC-215 Planned; initiative Accepted.


### Batch 6 manual shell review — 2026-09-15

[Canonical results](FINDINGS.md#batch-6-shell-manual-results--2026-09-15) verify
six Hyprland shell runs and deliberate SIGINT exits. Both scale-1 styles pass;
both fractional styles fail with and without observation. S01 remains open;
Sway frame confirmation and AI/F05 raw evidence/sequence remain pending.
No product edits or repeated product tests; hashes, mappings, versions,
documentation links and whitespace checked. UQC-211/UQC-201 stay In Progress.


### Batch 6 Sway AI clarification — 2026-09-15

[Verified Sway AI results](FINDINGS.md#batch-6-sway-ai-evidence-review--2026-09-15)
record passing user-observed VT return/navigation in both styles at DPR 1.25,
verified callbacks/hashes/mappings and deliberate interruptions. Sway was
unintentional; preserve these results while retaining the requested Hyprland F05
and skipped scale-1 Sway shell checks. UQC-211/UQC-201 remain In Progress.


### Batch 6 remaining compositor results — 2026-09-15

[Canonical review](FINDINGS.md#batch-6-sway-shell-acceptance-and-hyprland-ai-failure--2026-09-15)
accepts the S02 scale-1 shell comparison and records observed Hyprland F05 failure
in both styles, with compositor/Qt activation disagreement and continuing key
delivery. Two uninstrumented Hyprland AI comparisons remain. S01/UQC-211 and
F05/UQC-201 stay open; no product repair or final integration acceptance.


### Batch 6 manual sequence complete — 2026-09-15

[Uninstrumented confirmation](FINDINGS.md#batch-6-uninstrumented-confirmation-and-manual-sequence-complete--2026-09-15)
verifies both final Hyprland AI runs and reproduces both reported recovery
behaviors without the observer. No manual repetitions remain for this kit.
S02 comparison accepted; S01 and F05 fail. UQC-211/UQC-201 remain In Progress;
UQC-215 Planned, with F05 ownership unresolved. Initiative remains Accepted.


### S01 provider repair and F05 reduced diagnosis — 2026-09-15

[Canonical handoff and release evidence](FINDINGS.md#s01-provider-repair-and-f05-reduced-diagnosis--2026-09-15)
record published/pinned provider `0e0f92e`, completed local UQC-215 verification,
the immutable `8ptiz_ko` repair kit and the unresolved F05 activation boundary.
UQC-215 is Done; S01 human acceptance and F05 ownership remain open. Preserve
S02 and all completed manual comparisons. UQC-211/UQC-201 stay In Progress and
the initiative Accepted; no final integration or unrelated-batch work.


### S01 manual repair acceptance — 2026-09-15

[Verified Hyprland results](FINDINGS.md#s01-repair-accepted-on-hyprland--2026-09-15)
accept both fractional styles from the repaired kit. S01 accepted, S02 acceptance
preserved, UQC-211 Done. UQC-215 remains Done; F05/UQC-201 and final integration
remain open. No product edits, changed pins or repeated product tests.

### F05 activation diagnosis setup — 2026-09-15

[Canonical setup audit and missing evidence](FINDINGS.md#f05-activation-diagnosis-setup--2026-09-15)
record successful released-kit hash/package/source checks and reuse of retained
three-mode Fusion/DPR/mapping/exit verification. The manual checklist now captures
session identity and output scale. Plain-Qt physical-keyboard VT evidence remains
pending; no external disposition, upstream submission or product repair is claimed.
S01/S02 and completed AI comparisons remain accepted. UQC-201 stays In Progress
and the initiative Accepted; Batch 7, remaining Batch 3 diagnostics and integration
are excluded. Documentation links and whitespace checked; no product tests repeated
because the diagnostic sources and recorded dependencies are unchanged.

### F05 external reproduction and report draft — 2026-09-15

[Canonical plain-Qt result](FINDINGS.md#f05-plain-qt-external-reproduction--2026-09-15)
establishes an external Qt/Hyprland compatibility boundary: verified Fusion,
DPR 1.25/output scale 1, no HoloNight mappings, real keyboard callback delivery
after recreation, persistent null Qt focus and exit 0. User confirms failure
before pointer action and click recovery. Raw evidence is preserved and hashed;
the [unsubmitted upstream draft](f05/UPSTREAM-REPORT.md) includes sanitized trace
and explicitly unproven hypotheses. Diagnosis iteration complete; exact upstream
mechanism/repair unresolved. No HoloNight repair package or theme/hn repeats.
Source/kit identity, mappings, event/frame correlation, trace derivation, hashes,
documentation links and whitespace checked. Retained automated verification
reused; no product edits/tests or pins changed. S01/S02 and AI comparisons remain
accepted; UQC-201 In Progress, initiative Accepted. Other batches and final
integration remain outside this iteration.

### Batch 7 published greeter handoff — 2026-09-15

Ready baseline and local SDD established before assignment. Accepted canonical
clean handoff `abb1ecc86bec382b3cb21b238844e5a5d3207443` after local verification
and `git ls-remote` confirmation. UQC-212 Done; only the greeter gitlink changes.
[Canonical results](FINDINGS.md#batch-7-greeter-implementation-and-verification--2026-09-15)
retain failure boundaries and all verification. Fresh kit preparation and four
human-operated isolated-Sway runs remain. Batch 7 is open; UQC-201 In Progress,
initiative Accepted. No final ecosystem integration or unrelated batch work.


### Batch 7 immutable kit release — 2026-09-15

[Canonical kit evidence](FINDINGS.md#batch-7-greeter-implementation-and-verification--2026-09-15)
records 187 hashes, exact-prefix archive restoration/refusal, package consistency,
staged runtime/installed-launch matrices, actual DPR/origins/mappings/exits and
collector verification. Follow the [four-run Sway handoff](BATCH7-HANDOFF.md).
UQC-212 remains Done; Batch 7 manual acceptance is pending. UQC-201 In Progress,
initiative Accepted. No unrelated batch or final integration checks were reopened.


### Batch 7 manual acceptance — 2026-09-15

[Canonical acceptance and evidence audit](FINDINGS.md#batch-7-manual-acceptance--2026-09-15)
record the user's four G01–G06 passes, verified session/output scale, actual DPR,
staged origins/mappings, matching versions/hashes and four exit-0 outcomes.
Batch 7 is closed for its scoped checks; UQC-212 remains Done. G07 is a separate
open caret-visibility finding requiring reproduction before repair assignment.
UQC-201 stays In Progress and initiative Accepted. Documentation-only update;
links/whitespace checked, no product tests repeated or pins/kit changed.


### G07 fullscreen comparison kit — 2026-09-16

User-requested follow-up: exactly two manual comparisons, HoloNight and Fusion at
scale 1, with Ctrl+F toggling fullscreen in the isolated Sway session. The previous
windowed reproduction does not establish a failure in intended fullscreen use.
[Procedure](GREETER-G07-FULLSCREEN.md); both tests passed. See [fullscreen acceptance and closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16).

Released `/tmp/holonight-uqc216-5kx47zdb` using
`prepare-greeter-kit.py --fullscreen`, with clean canonical sources recorded in
`revisions.json`. Preparation checks (staged runtime, installed launches, origins,
DPR, caret graphics, collector tests, terminal syntax and archive restoration)
pass; headless `sway --validate` passes for the generated configuration.
Archive: `.cache/holonight-uqc216-5kx47zdb/holonight-uqc216-5kx47zdb.tar.gz`;
SHA-256 `e1ce240734c0797b832c6fcea2e68ec37d622ae55e1b388e9a1becd7ee753a7f`.
G07 closed as not an issue for intended fullscreen use after the two manual tests;
production unchanged and earlier evidence preserved.

### G07 diagnostic kit release — 2026-09-15

UQC-216's published clean handoff is pinned. The [G07 kit](G07-HANDOFF.md)
passes staged rendering/launch/origin/DPR/outcome checks, 189 restored hashes,
package consistency and exact-prefix restoration/refusal. [Canonical findings](FINDINGS.md#g07-rendered-investigation-and-diagnostic-handoff--2026-09-15)
record the unreproduced production defect and retained diagnostic limits. Four
human-operated comparisons remain; no speculative product repair or manual
acceptance is claimed. UQC-216/UQC-212 Done, Batch 7 closed, G07 open,
UQC-201 In Progress, initiative Accepted. Existing accepted work stays preserved.


### G07 manual diagnostic evidence review — 2026-09-16

[Canonical results](FINDINGS.md#g07-manual-diagnostic-result--2026-09-16) verify
four exit-0 runs, released hashes, staged origins, actual DPR and captured pixels.
Both scale-1 runs fail; both fractional runs pass. Exact tiled geometry/panel scale
0.78 exposes a coverage gap for the next reproduction. Four-run sequence complete;
no repeat requested. UQC-216 remains Done for diagnostic delivery, G07 open,
UQC-212 Done/Batch 7 closed, UQC-201 In Progress and initiative Accepted.
Evidence/documents only; no production edits, product-test repeats or pin changes.


### UQC-217 accepted ownership handoff — 2026-09-16

Started from the planned clean greeter/provider/configuration baselines and
confirmed all three on canonical main before the Ready → In Progress assignment.
The scoped greeter package takes its planned external-owner reproduction branch:
plain QtQuick reproduces the failure. Implementation/handoff `501d50c` was pushed
and `git ls-remote origin refs/heads/main` returned its full revision before
pinning; the greeter checkout is clean. Provider/configuration pins are unchanged.

Local standard verification passes; explicit DPR-1 regressions intentionally
remain failing and opt-in. Detailed results and commands live in the linked local
SDD. No repair kit or repeat human comparison is requested before a proven repair.
No umbrella integration claim or integration test run is made: UQC-201 remains
In Progress, the initiative Accepted, G07 open, UQC-216 Done and Batch 7 closed.

### UQC-218 accepted diagnosis/rejection handoff — 2026-09-16

Greeter `20f788c4ae86926d8c940ec33229fca2ac3c1a55` is clean and confirmed on
canonical main with `git ls-remote` after publication. Pin updated only after
that confirmation. Provider/configuration remain at the assigned baselines.
The [evidence and disposition](FINDINGS.md#g07-qtquick-diagnosis-and-rejected-layer-candidate--2026-09-16)
are recorded once in FINDINGS, with detailed implementation and commands in the
local SDD and upstream report draft. No upstream submission was made.

Verification on 2026-09-16: `ctest --test-dir build --output-on-failure` 8/8;
`check-caret-graphics.py` ordinary normal/compact matrix 4/4; candidate mode
4/4 graphics plus 4/4 isolated software; standalone diagnostic exits 1 at DPR 1
and 0 at DPR 1.25 on both backends. Format/QML lint, static analysis of 15 owned
translation units, Python compilation, REUSE 99/99 and diff checks pass. The
layer fails the text-sharpness requirement, so there is no production repair,
CI repair acceptance, UQC-218 kit release or request for four human comparisons.
Native blink/resize acceptance and launch/relocated-install release checks were
not entered after rejection. Existing released kits remain untouched.

This checkpoint completes the bounded diagnosis/rejection package. UQC-201 stays
In Progress, initiative Accepted, G07 open and Batch 7 closed. No umbrella
integration checks were run; F05 and Batch 3 are excluded.

### G07 fullscreen closure — 2026-09-16

Both fullscreen tests pass at scale 1 (HoloNight and Fusion). User acceptance and
reviewed evidence close G07 as not an issue for intended greeter use; the specific
windowed case is outside the design and planned real scenarios. See [fullscreen acceptance and closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16).
This disposition supersedes earlier dated G07-open and repair-follow-up statements.
No production repair, upstream submission or further comparisons are planned.
UQC-212/UQC-216/UQC-217/UQC-218 remain Done, Batch 7 closed; other integration
findings and gates are unchanged. No final ecosystem integration is claimed.


### UQC-219 bounded Batch 3 diagnosis handoff — 2026-09-16

Ready checkpoint `12ef2c8` preceded provider assignment at canonical baseline
`0e0f92e`. Published provider `c9aacd8fc5a1c70e161c9df2ba0fadd4d282ecb6`
was confirmed with `git ls-remote` and a clean checkout before pinning.
[Research and historical evidence](UQC-219.md) and the linked provider SDD record
the bounded handoff. UQC-219 Done; UQC-207/UQC-201 In Progress; initiative Accepted.
No repair kit, manual repeat or final integration check was required. Existing
G07 closure was checkpointed separately at `4e844dd`.

### Batch 3 closure checkpoint — 2026-09-16

UQC-207 Done; Batch 3 closed by user-directed disposition. [Canonical closure](FINDINGS.md#batch-3-user-directed-closure--2026-09-16)
preserves accepted results and deferred historical findings with ownership uncertainty.
Provider documentation commit `019d22fd20722a9f119953c1d810fcdbc105d5b2` was
published and confirmed on canonical origin/main before updating the gitlink.
Provider checkout clean; documentation diff checks pass. No production change or
repeat product tests for this documentation-only closure. This checkpoint is
separate from Batch 8; UQC-201 remains In Progress and initiative Accepted.

### Batch 8 preparation checkpoint — 2026-09-16

All twelve submodules clean at published pinned revisions; no newer remote
revision adopted. Fresh dependency-order suites, installed consumers, import
policy, missing-module deployment negatives and runtime origin/DPR checks pass.
[Canonical final checklist](FINAL-ACCEPTANCE.md) reconciles accepted evidence,
remaining manual work and limitations; exact commands/results and release hashes
are linked there. [First handoff](BATCH8-HANDOFF.md): two NeoChat Sway runs only.
Restoration helper accepts the final-kit name while retaining existing-path refusal.
No product implementation/API changes, no upstream submission and no privileged
launch. UQC-201 In Progress; initiative Accepted until final human gates pass or
receive explicit disposition. Batch 3 closure remains its separate checkpoint.

### Batch 8 NeoChat manual acceptance — 2026-09-16

[Canonical evidence review](FINDINGS.md#batch-8-neochat-sway-acceptance--2026-09-16)
accepts both Sway DPR-1.25 NeoChat runs, with user-reported interaction/palette
passes, verified kit hashes, versions, staged mappings, created ComboBox origins
and exit 0. Diagnostic limitations remain explicit; Batch 3 stays closed.
Next: [two Tokodon runs](BATCH8-TOKODON.md). Documentation links/whitespace checked;
no product edits, tests, pin changes or released-kit modifications. UQC-201 stays
In Progress and initiative Accepted.

### Batch 8 Tokodon manual acceptance — 2026-09-16

[Canonical review](FINDINGS.md#batch-8-tokodon-sway-acceptance--2026-09-16)
accepts both Sway DPR-1.25 runs: user-reported passes, matching release hashes and
versions, verified staged mappings/origins and exit 0. Basic fallback and trace
coverage limits are explicit; diagnostics do not reopen Batch 3. Next:
[two Haruna runs](BATCH8-HARUNA.md). Documentation links/whitespace/licensing
checked; no product tests, pin or released-kit changes. UQC-201 In Progress,
initiative Accepted.

### Batch 8 Haruna manual acceptance — 2026-09-16

[Canonical review](FINDINGS.md#batch-8-haruna-sway-acceptance--2026-09-16)
accepts both Sway DPR-1.25 Haruna runs: user-reported passes, matching kit hashes
and versions, verified staged mappings/origins and exit 0. Explicit Fusion and
application-owned boundaries retained; historical crash/hover deferrals unchanged.
Next: [two read-only package-manager runs](BATCH8-PACKAGES.md). Documentation
links/whitespace/licensing checked; no product tests, pin or released-kit changes.
UQC-201 In Progress; initiative Accepted.
