# Unified Qt Quick Controls and Third-Party Compatibility — Coordination Ledger

The initiative is Accepted following user scope approval on 2026-09-07. Discovery UQC-001 is complete and
UQC-002 settles the contract. UQC-101 is Done with its verified provider published and pinned.
UQC-103 settings and UQC-104 AI are Done with local acceptance and publication complete.
Supplemental UQC-107/UQC-108/UQC-109, UQC-105 package-manager and UQC-106 greeter are Done.
UQC-102 shell is Done with published local acceptance and green final-revision CI; UQC-201 is In Progress for automated integration and manual-kit work.

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
| UQC-201 | umbrella | Verify published clean pins, dependency-order checks, activation paths, and accepted third-party matrix under Hyprland and Sway | UQC-101–UQC-109; UQC-202/UQC-203 findings | [Evidence](INTEGRATION.md), [commands](COMMANDS.md), [manual kit](MANUAL.md) | In Progress | Assigned from `a26b4e537ea8105a991ec5f48e06e9fe7565dd72`; verification gitlinks at readiness `67a72a6` | 2026-09-09: fresh dependency-order full suites, current installed/relocated launches, static checks and licensing pass. Explicit AI Fusion composer geometry fails reproducibly; installer preflight rejects the current Qt Wayland package ownership. Both findings remain open. Third-party bounded loading verified; all human Hyprland/Sway and authentication gates unchecked. |
| UQC-202 | umbrella | Resolve installer preflight Qt 6 Wayland package-ownership assumptions with a separately verified correction | — (found during UQC-201) | [Design](UQC-202.md) | Ready | Baseline `4c38804f142486b23dc20b81f6a0fa78e5530421` | 2026-09-09: `--check` requires absent `qt6-wayland`, but installed Qt6WaylandClient CMake metadata is owned by `qt6-base 6.11.2-3`. No package transaction or installer change performed. This gate must be resolved before final integration. |
| UQC-203 | `holonight-ai` | Resolve composer geometry acceptance under explicit Fusion against the integrated provider | — (found during UQC-201) | [Supplemental SDD](../../../holonight-ai/docs/sdd/unified-qtquick-controls/UQC-203.md) | Ready | Baseline `b874334b20053f94f84fd9b4b1a0a7e0c7cc867a` | 2026-09-09: `ChatComposerActionsQml.PreservesDesktopAndCompactPresentation` fails in the 59-test Fusion selection and in a focused serial recheck: icon-only attachment implicit height 24 versus labeled context/tools 25. Settle intended native-style geometry before changing the UI or assertion; publish a separately verified handoff before repinning. |

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
