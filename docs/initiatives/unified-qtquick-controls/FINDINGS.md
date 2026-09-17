# UQC acceptance findings — canonical register

Current repair checkpoint (2026-09-17): [UQC-220](UQC-220.md) provider repair
is manually accepted for Settings Weather row centering and Fusion hover.
[Scale-1 and fractional evidence](FINDINGS.md#uqc-220-fractional-repair-acceptance--2026-09-17)
close the focused repair handoff, including the subtle closed-button hover.
Other Batch 3 historical dispositions remain unchanged. Resume the final
checklist with affected integration revalidation; do not repeat accepted checks.

Initiative **Accepted**; UQC-201 **In Progress**. Batch 8 final acceptance preparation is active; the
[reconciled checklist](FINAL-ACCEPTANCE.md) governs remaining work. This register is authoritative for current findings;
[GUIDED.md](GUIDED.md) and [TASKS.md](TASKS.md) retain chronological evidence,
including superseded interpretations. Add new observations here once, and link
from the ledger rather than copying the narrative into both historical documents.
Current scope and dispositions below take precedence over dated historical reports.
Batches 1–3 are closed. Batch 3 diagnostics are deferred, non-blocking historical
findings; Tokodon chevron is deferred. Batch 5 is removed from this
initiative, and Batch 7 is narrowed by the greeter review below.

## Evidence and interpretation

Reports were collected on 2026-09-10–11. In the tables, H/F means requested
HoloNight/Fusion; scale means Qt scale with output scale 1. All original application
reports are Hyprland unless stated otherwise. These are user observations, not
independent measurements of DPR or created-control origins. The
[run correlation inventory](GUIDED.md#hyprland-evidence-correlation--2026-09-10)
records selectors/scales/PIDs for `hyprland-j97jound`; exact action-to-run correlation
is incomplete. Each linked historical section contains the original evidence path
or explicitly pending path. Missing evidence is not a retraction of a finding.
An investigation owner is responsible for classification, not an asserted root cause.

New report carried into this checkpoint: **Sway Settings behaves equivalently to
the earlier Settings run**. This adds a compositor comparison to F01/D01–D03/L01;
no new per-control results, run path, actual selector/scale or process-origin evidence
were supplied with the plan. Do not infer a complete Sway matrix pass.

## Shared focus — UQC-204, holonight-qt

Automated repair accepted on 2026-09-11 at published provider `65c806f` (implementation
`e97b646`). Baseline failed seven of eight cases per style/scale; repaired build and
installed modules pass eight of eight in all four combinations. The short manual
regression passed on 2026-09-11 as recorded below: F01/F02 are closed for the
requested focus repair. F03 eligibility coverage passes automatically, but the
original app-specific disabled-control attribution remains unconfirmed. Original
observations are preserved below; unrelated findings remain open.

| ID | Application / context; reproduction | Confirmed facts and suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| F01 | Settings H/F, 1/1.25; edit Weather City then Tab. AI H/F 1.25; first ComboBox traversal then full cycle | Text editing works; first-cycle indicator absent, later cycle restores it. Provider baseline reproduces lost visualFocus from parameterless wrapper forwarding. Sway Settings equivalence reported with limits above. | [Settings](GUIDED.md#evidence-review), [AI clarification](GUIDED.md#ai-fusion-comparison-and-switch-feedback--2026-09-10); private `.cache/uqc201-focus-probe/` | First and repeated Tab/Backtab entries retain owner, reason and visible indicator under both styles. |
| F02 | AI providers H/F 1.25; Context value → invisible stop → Temperature value → Slider; reverse lacks extra stop | Direction asymmetry reported repeatedly. Labels match Ollama source; user did not confirm provider. HnFormField compound wrapper is a reproduction target. | [AI](GUIDED.md#ai-provider-form-observations--2026-09-10) | Natural child traversal in both directions, no invisible compound stop. |
| F03 | AI H/F 1.25; traverse provider form | Disabled-control traversal is suspected only, not observed focus ownership. UQC-204 guards hidden/disabled/missing/non-tab children without claiming all app symptoms explained. | [AI](GUIDED.md#ai-provider-form-observations--2026-09-10) | Isolated eligibility regressions pass; app-specific attribution remains conditional. |

### Manual focus acceptance — 2026-09-11

The user reports **“No issues observed”** after all four requested runs from kit
`/tmp/holonight-uqc201-focus-5ydxn45l`, in session `sway-950ccu53`. This accepts the
requested Weather City editing and first/repeated forward/reverse focus checks,
AI Context → Temperature → Slider and reverse, and first/repeated ComboBox entry,
under default/Fusion at requested Qt scale 1.25 (prepared Sway output scale 1).
No failing controls were reported. All four returned helper exits are 0.

Evidence paths below are relative to `/home/tux/uqc-guided-evidence/sway-950ccu53/`:

| Application | Requested style / Qt scale | PID | Evidence directory | User result / exit |
|---|---|---|---|---|
| Settings | default / 1.25 | 58347 | `settings-1789118907310613383` | Pass / 0 |
| Settings | Fusion / 1.25 | 58547 | `settings-1789118993555599627` | Pass / 0 |
| AI | default / 1.25 | 59046 | `ai-1789119657507072702` | Pass / 0 |
| AI | Fusion / 1.25 | 59186 | `ai-1789119798617406618` | Pass / 0 |

**F01 and F02 closed:** the requested manual behavior now passes alongside the
previous automated owner/reason/eligibility regressions. **F03:** automated
eligibility protection is verified; this report does not establish that disabled
controls caused the original symptom, so that attribution remains unconfirmed.
This is user-reported interaction and pasted helper evidence, not an independent
review of saved logs/maps or measurement of effective DPR. Direct read access to
the supplied evidence directory was denied; no saved-log claims are made.

Providers remain disabled by the prepared profile; no provider requests were
part of this check. Button activation feedback (F04), VT return (F05), checked
Switch contrast, dropdown interaction and all other unrelated findings remain
open. Broad acceptance stays paused; initiative Accepted and UQC-201 In Progress.

Separate focus investigations (not included in UQC-204):

| ID | Application / context; reproduction | Facts / hypothesis; investigation owner | Evidence | Acceptance |
|---|---|---|---|---|
| F04 | AI H 1.25; focus button, Space, Tab then Shift+Tab | Action works but ring disappears until reentry; exact button/owner unknown. holonight-qt investigates activation reason, AI supplies reproduction. | [AI](GUIDED.md#ai-provider-form-observations--2026-09-10) | Identify button and focus lifecycle; keyboard activation retains appropriate feedback. |
| F05 | AI H 1.25; tux VT3 → VT1 → back | External Qt/Hyprland compatibility defect reproduced in plain Qt/Fusion at DPR 1.25. Keyboard re-enters and navigation reaches the settings window while Qt focus stays null. Exact upstream mechanism unresolved; no HoloNight repair owner. | [Plain-Qt evidence and disposition](#f05-plain-qt-external-reproduction--2026-09-15) | Upstream follow-up remains open; no repair or restored VT navigation claimed. |

## Dropdowns — holonight-qt investigation/repair package

| ID | Application / context; reproduction | Confirmed facts / suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| D01 | Settings Appearance H 1.25; hover rows then click former positions. Greeter session selector H 1/1.25 | Rows disappear and cannot be selected there. Weather and Haruna scrollable font dropdown work; not every scrollable list fails. Fusion comparison works. Shared cause unproven. | [Settings](GUIDED.md#settings-continuation-observations--2026-09-10), [greeter](GUIDED.md#greeter-demo-default-scale-1-findings--2026-09-10) | Rows stay visible and selectable through hover/scroll; first/last selection works. |
| D02 | Settings/NeoChat/Tokodon H logs; open selectors | Provider ComboBox.qml popup implicitHeight binding loops confirmed (12 in Settings); no proof this causes D01. | [log review](GUIDED.md#hyprland-evidence-correlation--2026-09-10) | Reproduce affected geometry; no height loop and bounded usable popup. |
| D03 | Settings H 1.25, Haruna H 1/1.25, NeoChat H 1; open popup then click outside | Outside does not close; item choice/collapsed area/Escape close Settings. Haruna Fusion outside closes; NeoChat Fusion result unspecified. Sway Settings equivalent. | [Settings](GUIDED.md#settings-continuation-observations--2026-09-10), [Haruna](GUIDED.md#haruna-default-scale-1-observations--2026-09-10), [NeoChat](GUIDED.md#neochat-logged-out-settings--palette-transition--2026-09-10) | Outside click dismisses according to popup policy without selecting a row. |
| D04 | Settings H 1.25; reopen selected ComboBox | User clarifies list starts at the beginning; selected row may be onscreen or offscreen and is not highlighted. Strengthened baseline fixture reproduces an invisible selected row owned by the hidden inherited list; scroll reset itself remains unconfirmed automatically. | [Settings](GUIDED.md#settings-continuation-observations--2026-09-10) | Current row visible, correctly highlighted and keyboard navigation begins from expected selection. |

### UQC-206 local dropdown repair checkpoint — 2026-09-12

The [provider SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-206.md)
records isolated D01/D03 failures, the local repair and verification. A replaced
inherited popup was consuming the active popup's delegates; both lists now guard
model ownership. Overlay parenting made outside-parent dismissal ineffective;
explicit outside-popup dismissal with modal, undimmed input fixes that route and
prevents collapsed-click reopening. Ten interaction cases pass in each of four
style/scale processes, and all 69 provider checks including installed consumers pass.

D01/D03 remain open for manual acceptance. D02 binding loop is not reproduced by
these fixtures; D04 isolated visibility/highlight/keyboard checks already pass on
baseline, so app-specific interpretation remains pending. No finding is closed,
no new kit is released and no gitlink changes. Retained source and evidence under
`.cache/uqc206/` survive reboot; accepted focus and cancellation results stand.

### D04 clarification and stronger reproduction — 2026-09-12

User clarifies that reopening starts the list at the beginning, with no selected-row
highlight whether that row is onscreen or offscreen. This supersedes the ambiguous
"not focused" description; it is not a report about arrow-key starting position.

The prior test checked highlight state and list-local coordinates but missed actual
visibility and scene containment. Adding those assertions reproduces an invisible
selected HnIconComboBox row on baseline under both mouse and keyboard opening.
The hidden inherited list owns that delegate, linking this reproduced part of D04
to D01. Mouse opening alone did not expose it. The existing ownership repair passes the stronger coverage: 12 dropdown cases in
each style/scale process, composite/geometry and installed-consumer checks (7/7
CTests). No new product QML change is needed.
Scroll reset and full manual D04 acceptance remain open. See the provider SDD.

### Manual dropdown acceptance and remaining height loop — 2026-09-12

The user completed four runs (two applications × two styles) from candidate kit
`/tmp/holonight-uqc206-wou7oqyf` and reports that dropdowns work well with both mouse
and keyboard. This accepts the requested reopen/selected-row, hover/scroll,
first/last selection and dismissal checks for the tested Settings Appearance and
greeter demo selectors. All four exits are 0. D01, D03 and D04 are **closed for this
owned-application dropdown checkpoint**; third-party and final ecosystem gates are
not closed by it. The new stationary-pointer findings below remain separate.

Paths are relative to `/home/tux/uqc-guided-evidence/sway-7m7cgmn7/`:

| Application | Verified selector / requested Qt scale | PID | Evidence directory | User result / exit |
|---|---|---|---|---|
| Settings | embedded default / 1.25 | 329367 | `settings-1789234977224144508` | Pass / 0 |
| Settings | Fusion / 1.25 | 329571 | `settings-1789235104546994351` | Pass / 0 |
| Greeter demo | embedded default / 1.25 | 329701 | `greeter-1789235475914841486` | Pass / 0 |
| Greeter demo | Fusion / 1.25 | 329776 | `greeter-1789235646987834678` | Pass / 0 |

Read-only review via authorized sudo confirms executable paths, commands, selectors,
scale environment and exits. Maps identify candidate Core/Controls/impl in all
four and candidate HoloNight style in the default runs. This is loading evidence,
not independent observation of interactions or measured DPR. `LD_LIBRARY_PATH` is
absent in all saved process environments and config maps point to
`/usr/lib/libholonight_config.so`; the manual kit did not preserve fully isolated
config-library loading despite the staged paths used by preparation checks. Keep
this deployment limitation explicit; do not claim a fully staged runtime pass.

**D02 remains open:** Settings default has six `QML Popup: Binding loop detected
for property "implicitHeight"` warnings at `qrc:/qt/qml/Holonight/ComboBox.qml:109:12`.
The other three logs have no matches for the bounded binding-loop/type/reference/
assignment/failed-component diagnostic search. User-reported functional success
does not establish absence of warnings. Review summary is retained privately in
`.cache/uqc206/manual-review.jsonl`; original logs remain in the tux evidence directory.
The provider is still an unpublished working-tree candidate. No pin/publication or
full UQC-206 completion follows from this acceptance.

## Pointer and keyboard interaction — new findings, 2026-09-12

| ID | Reproduction / observed result | Owner and evidence | Acceptance |
|---|---|---|---|
| F06 (closed for reported Settings/greeter HoloNight sequence; see manual acceptance below) | Open a dropdown by keyboard with an unknown/stationary pointer over its rows, or switch from mouse to keyboard. Two rows look highlighted: keyboard selection and pointer hover. User reports visual-only impact and similar behavior across HoloNight apps. | holonight-qt investigates shared delegate feedback; broad app scope is user-reported, not independently enumerated. ItemDelegate and icon-composite backgrounds render hover separately from highlight/current state. | Keyboard interaction has one unambiguous active-row indication; a stationary pointer does not introduce a competing active-looking row. Deliberate pointer movement/click still restores normal mouse interaction. |
| F07 | Open launcher with stationary pointer inside its unfiltered results, then Enter expecting the initial first item. Another item under the pointer can launch. | holonight-shell owns functional selection. Source review finds browse and search result `onHoveredChanged` handlers unconditionally calling `LauncherService.setSelectedIndex` on hover. Live event ordering and exact default selection still need isolated reproduction. This is selection change, not proof that keyboard focus moved. | Opening beneath a stationary pointer preserves intended initial selection/Enter target; keyboard navigation remains authoritative until deliberate pointer movement or click. Cover browse/search, filtering, reopen and pointer reentry without launching real applications. |

Proposed shared input policy: keyboard opening/navigation retains control of the
active row until deliberate pointer movement or clicking. Showing/moving content
beneath an unchanged pointer must not count as that movement. Preserve mouse
clicks and ordinary hover after intentional movement; avoid globally disabling
hover or conflating selected/current/checked/keyboard-focus states. Provider visual
feedback and shell selection need separate reproductions and repository-local SDDs
before assignment. These findings do not reopen the accepted D01/D03/D04 repair.

## Shared rendering — holonight-qt investigation/repair package

| ID | Application / context; reproduction | Confirmed facts / suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| R01 | Haruna H/F 1; open top menus and Settings navigation | Fusion shows icons missing in H; exact navigation side/origins pending. | [icons](GUIDED.md#haruna-fusion-comparison--missing-icons--2026-09-10) | Required icons render with actual application icon sources; verify origin before attributing missing navigation icons. |
| R02 | Haruna H 1; open each top-menu dropdown | Excess blank left space. User requests per-menu conditional shared icon column. | [menu requirement](GUIDED.md#haruna-fusion-comparison--missing-icons--2026-09-10) | If any item has icon, align all texts in that menu; otherwise omit icon column/spacing while retaining edge/check/submenu space. |
| R03 | Haruna H 1/1.25; Shortcuts list, select/change other rows | First row permanently looks selected; hover independently works. Fusion has no persistent background. Actual selection failure unproven. | [first row](GUIDED.md#haruna-scale-125--persistent-first-row-background--2026-09-10) | Visual selected/current state matches application state and moves/clears appropriately. |
| R04 | AI H/F 1.25; navigate Switch off then on | H feedback visible off, not on; F visible in both. Focus interpretation provisional, contrast cause unproven, exact Switch unknown. | [Switch](GUIDED.md#ai-fusion-comparison-and-switch-feedback--2026-09-10) | Identify state/Control; visible keyboard indicator in both checked states. |

## Palette investigation — holonight-qt leads classification with umbrella

| ID | Application / context; reproduction | Confirmed facts / suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| P01 | NeoChat H 1/1.25, F 1: open Settings General, Appearance, close/reopen and repeat. Tokodon same requested comparisons, Appearance first | Appearance toggles two schemes repeatedly without explicit selection; both windows change. Other pages do not trigger NeoChat. Not just lazy initialization; ownership unresolved. | [toggle](GUIDED.md#neochat-appearance-palette-toggle-clarification--2026-09-10), [Tokodon](GUIDED.md#tokodon-default-scale-1-findings--2026-09-10) | Measure palette roles/state/origins across sequence; navigation alone preserves intended palette and application overrides. |
| P02 | Haruna file/color pickers H 1/1.25; Tokodon font picker H 1/1.25; compare palette states | Mixed light surfaces/dark controls when H-looking scheme applied; alternate scheme consistent by user correlation. Haruna F dark. Palette state confounds style comparison; backend/roles unknown. Tokodon button resemblance to Basic is unverified. | [Haruna](GUIDED.md#haruna-default-scale-1-observations--2026-09-10), [state clarification](GUIDED.md#tokodon-scale-125--picker-palette-state-clarification--2026-09-10) | Same picker remains coherent before/after palette transitions while honoring app palette; record actual backend/control origins. |

## Application layouts — removed from initiative scope

User correction, 2026-09-14: L01/L02 are caused by incorrect layout implementation
in Settings and AI, not holonight-qt controls unification. Batch 5 is removed;
UQC-209/UQC-210 are Superseded rather than completed repairs. Preserve these reports
for separate follow-up sessions: create/update each application’s local SDD with
reproduction, layout ownership and focused verification before implementing there.
Do not schedule, repair or gate UQC integration on these items. No application
source or local follow-up SDD is created in this documentation-only scope update.

| ID | Application / context; reproduction | Facts / hypothesis; owner | Evidence | Acceptance |
|---|---|---|---|---|
| L01 | Settings H 1.25; press/drag slider (exact page pending); Sway equivalent | Width shrinks and value jumps. Not reported in F comparison. Incorrect Settings-owned layout; separate Settings-local SDD follow-up. | [Settings](GUIDED.md#settings-continuation-observations--2026-09-10) | Stable usable track width through press/drag; no geometry-induced value jump. |
| L02 | AI provider Temperature H/F 1.25 | H knob-only, F track visible but too short; Incorrect AI-owned row layout; separate AI-local SDD follow-up. | [AI](GUIDED.md#ai-fusion-comparison-and-switch-feedback--2026-09-10) | Adequate stable track alongside SpinBox at supported widths/scales under both styles. |

## Shell — holonight-shell

| ID | Application / context; reproduction | Confirmed facts / suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| S01 | Shell H 1.25; start then interact with bar | Missing right items, bar shrinks/jitters, sections slide in/out, unusable clicks; reserved space appears constant, unmeasured. Scale 1 functional; F 1.25 untested. | [fractional](GUIDED.md#shell-default-failure--2026-09-10) | Stable geometry, all sections visible/clickable at 1.25; measure exclusive zone. |
| S02 | Shell H/F 1; inspect topbar including transient systemd launch | Broken right frame edges; network/audio/battery/layout backgrounds cover frame/gradient; bell/date correct. Composition suspected, frame path not proven broken. | [frames](GUIDED.md#shell-default-scale-1-comparison--2026-09-10), [systemd](GUIDED.md#transient-systemd-shell-visual-result--sway-handoff--2026-09-11) | Complete frame edges and intended transparent status backgrounds; preserve functional scale-1 interaction. |

## Authentication — holonight-shell

| ID | Application / context; reproduction | Confirmed facts / suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| A01 | Owned Polkit H; open user selector in isolated run | Two reserved but blank identity rows. Custom avatar/text delegate uses model roles; independent from D01. | [prompt](GUIDED.md#owned-agent-prompt-findings--2026-09-10), private auth run `20260910T192833Z` | **Closed** by the [Batch 2 manual acceptance](#batch-2-authentication-manual-acceptance--2026-09-14), supported by real-model rendering tests. Historical blank rows remain recorded without an inferred cause. |
| A02 | Same run; failed submission shows error | Input disappears, Password label remains. Label/input visibility conditions differ; lifecycle/retry needs reproduction. | [prompt](GUIDED.md#owned-agent-prompt-findings--2026-09-10) | **Closed** by the [Batch 2 synthetic lifecycle/rendered checkpoint](#batch-2-authentication-repair-checkpoint--2026-09-14). Label/editor/helper track supported prompt/error/retry lifecycle. No further failed credential submission. |
| A03 | Same run after failure; Cancel prompt | Prompt closes but Python challenge hangs until Ctrl+C. Agent exit 0 verified; challenge.txt absent, no normal completion. UQC-205 baseline reproduction locates missing listener GError: coordinator completion occurs, but libpolkit cannot reply. Typed cancellation error repairs the automated path. | [hang](GUIDED.md#owned-agent-cancellation-completion-failure--2026-09-10), [repair/verification](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-205.md) | Deterministic cancellation completes pending request exactly once and parent exits; cover failure-then-cancel and direct cancel with isolated fake backend. **Closed**: automated completion checks and [manual cancellation result](#manual-polkit-cancellation-acceptance--2026-09-12) pass. |
| A04 | Askpass F 1.25; inspect unfocused/focused editor then cancel | Left border appears half thickness; focused ring intact, cancel exit 1. Shell supplies Rectangle background; clipping/fractional position suspected only. | [border](GUIDED.md#owned-askpass-fusion-scale-125-border-finding--2026-09-10) | **Closed** by the [Batch 2 manual acceptance](#batch-2-authentication-manual-acceptance--2026-09-14), supported by rendered edge-coverage checks. |

### Manual Polkit cancellation acceptance — 2026-09-12

In response to the requested direct-cancel check from kit
`/tmp/holonight-uqc205-irzzhjcz`, the user returned:

- Challenge: `normal-exit`, exit `126`.
- Evidence: `/home/tux/uqc-auth-evidence/20260912T002338Z/challenge.txt`.
- After challenge completion, Ctrl+C stopped the agent with exit `0`.

This is the returned result for the requested fresh real tux Sway login using
default HoloNight at Qt scale 1.25, without credential entry. The challenge returned
before agent cleanup; neither timeout nor Ctrl+C was needed to complete it.
The supplied excerpt does not separately describe prompt closure or repeat the
registration PASS line. The released helper requires verified live registration
before requesting the challenge. Direct read access to the evidence file was denied;
this records the user's pasted result, not independent saved-log inspection.

**A03 closed:** the returned manual cancellation result, together with the verified
exactly-once direct/failure-then-cancel, D-Bus reply, bounded requester exit, queued
request and shutdown regressions in the [shell SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-205.md),
satisfies the completion gate. No repeat or failed credential submission is requested.
A01/A02/A04 remain open after the dropdown checkpoint. UQC-201 remains In Progress,
the initiative Accepted, and broad acceptance paused.

## Greeter — holonight-greeter (demo evidence only)

All rows refer to H 1/1.25 and general F 1 comparison in
[demo findings](GUIDED.md#greeter-demo-default-scale-1-findings--2026-09-10) and
[Fusion follow-up](GUIDED.md#greeter-demo-fusion-scale-1-comparison--2026-09-10).
The original reports are retained below, with current dispositions from review of
pinned greeter `b082d82` and the subsequent shared-provider acceptance records.
Source: [LoginPanel.qml](../../../holonight-greeter/qml/LoginPanel.qml),
[FooterSelector.qml](../../../holonight-greeter/qml/FooterSelector.qml),
[Main.qml](../../../holonight-greeter/qml/Main.qml), and
[runtime tests](../../../holonight-greeter/tests/runtime/controls_test.cpp).
Real pre-session login remains a separate Batch 8 gate.

**Already implemented/accepted:** session dropdown disappearance, dismissal and
selection (D01/D03/D04) and the reported stationary-pointer feedback sequence (F06).
The avatar display already uses `HnAvatar` in LoginPanel.qml, introduced by greeter
commit `9130c9c` and verified by its runtime-control origin test. Do not assign
these again. G05's requested avatar *selector* is distinct from that existing display.

**Still not established as fixed:** G01's custom user-selector Tab/focus behavior
and G02's keyboard reveal lack specific acceptance. LoginPanel still bypasses the
user selector in password Backtab/power Tab links and gives the selector empty
background/indicator items. Reveal still depends on `reveal.pressed`; generic
Button tests do not prove this greeter lifecycle. FooterSelector still supplies
its own colors/hover background, so G03 is not closed by shared hover fixes. G04
remains a palette question, not a proven defect. Main.qml's SystemActionButton
still paints `HoloniightPalette.surface` normally and uses the same text font size
for both power glyphs, so G06's transparency/larger-poweroff request is not already
implemented merely because its inner Button has an empty background.


| ID | Reproduction | Confirmed facts / suspected cause | Acceptance |
|---|---|---|---|
| G01 | Tab/Backtab through login | User selector absent from cycle; F functional mouse use does not establish Tab reachability | Enabled selector reachable both directions, visible indicator. |
| G02 | Focus password reveal; hold/release Space | Mouse reveal works; keyboard does not; lifecycle unknown | Keyboard hold-to-reveal matches documented behavior and remasks on release/focus loss. |
| G03 | Inspect disabled layout selector without configured choice | Correctly disabled but unexpected colors and hover appearance | Appropriate disabled appearance, no interactive hover feedback. |
| G04 | Inspect password background | User questions palette alignment; no proven color defect | Identify semantic palette source and validate intended contrast/state. |
| G05 | Inspect user selector | Shared HnAvatar display already implemented; user selector remains a separate Controls.ComboBox. Requested selector composition and reported Fusion sizing are unaccepted | Review only remaining selector composition/sizing and keyboard reachability; do not redo shared avatar adoption. |
| G06 | Inspect reboot/poweroff without activating | Requests transparent normal backgrounds, larger poweroff icon; reboot size correct | Requested normal presentation; no power-action execution needed to verify appearance. |

Session-row disappearance belongs only to D01, not a duplicate greeter finding.

## Compatibility observations — umbrella classification, no premature product assignment

| ID | Application / context; reproduction | Facts / hypothesis | Evidence | Acceptance / classification criterion |
|---|---|---|---|---|
| C01 | Settings/Haruna F; menus/ComboBoxes | No hover; small Settings text padding is explicitly a preference. NeoChat scheme popup DOES hover, so not universal. | [Fusion](GUIDED.md#fusion-comparison-follow-up--2026-09-10), [NeoChat](GUIDED.md#neochat-fusion-follow-up--2026-09-10) | Identify implementation/state; preserve Fusion conventions, no forced H spacing. |
| C02 | NeoChat/Tokodon F 1; inspect check/radio labels and scheme ComboBox | No indicator-label gap; popup uses available height, looks H-like despite F collapsed control. No clipping/unreachable rows reported, origins unknown. | [NeoChat](GUIDED.md#neochat-fusion-follow-up--2026-09-10), [Tokodon](GUIDED.md#tokodon-fusion-scale-1-findings--2026-09-10) | Classify owner with origins/geometry and first/last reachability; do not infer mixed style from appearance. |
| C03 | Tokodon F 1; boxed Settings rows | Switch extends beyond right boundary; H equivalence not confirmed | [overflow](GUIDED.md#tokodon-fusion-scale-1-findings--2026-09-10) | Measure containment and assign narrow owner before repair. |
| C04 | Haruna H/F 1, H 1.25; Mouse → Add action | Warning corners imperfect in both styles; less noticeable 1.25. Buttons look different, origin unverified; fallback boundaries accepted | [Haruna](GUIDED.md#haruna-default-scale-1-observations--2026-09-10) | Identify warning geometry/control origins; classify actual rendering defect independently of allowed fallback. |
| C05 | Haruna Settings; open multiple help buttons | Concurrent help popups; exclusivity is user preference, suspected app behavior | [Haruna](GUIDED.md#haruna-default-scale-1-observations--2026-09-10) | Confirm owner and intended exclusivity before accepting a repair requirement. |
| C06 | Initial Haruna launch and NeoChat/Tokodon logs | First Haruna SIGABRT; activeControl/type errors; Kirigami MessageDialog/AboutItem diagnostics also occur with F. No established link to P01 | [logs](GUIDED.md#hyprland-evidence-correlation--2026-09-10) | Bound crash reproduction and classify diagnostics independently; successful later runs do not erase first failure. |

## Evidence gaps and remaining integration gates

- Initial Settings `hyprland-cwas_0je/settings-1788998056392643199` has incomplete
  session/activation evidence. Retain the initial failed observation and subsequent
  City-editing clarification; restored runs do not overwrite it.
- `askpass.log` was overwritten by the later default 1.25 command, as clarified by
  the user. Original default scale-1 interaction/cancel result is user-only;
  `askpass-scale125.log` never existed separately. Fusion logs are separate. See
  [clarification](GUIDED.md#connection-verification--askpass-log-clarification--2026-09-10).
- The original owned Polkit challenge completion record remains absent. A03 is
  closed by the subsequent [manual cancellation result](#manual-polkit-cancellation-acceptance--2026-09-12)
  and automated regression checks; the original failure evidence is preserved.
- Positive package-manager and askpass observations retain their limited tested
  surfaces; no exhaustive pass. Account-dependent third-party surfaces untested.
- Process maps prove native loading, not every created Control origin. Direct
  private-bus, desktop-entry and transient systemd process correlation do not close
  shipped-service/wrapper acceptance. Transient unit cleanup is confirmed; manager
  environment was unchanged. Preserve earlier failures in INTEGRATION.md.
- Remaining compositor/style/scale cases, palette round trips, shipped services,
  other authentication checks and real pre-session greeter acceptance remain explicit
  integration gates. No broad acceptance restart or full Sway repetition now.

## Repair order and repository packages

The [current roadmap](BATCHES.md) controls execution; dated checkpoints below are
historical evidence, not current assignments.

- UQC-204/205/205-B2/206/213/214 are Done for their recorded scopes. Preserve
  accepted focus, authentication, dropdown and launcher behavior.
- UQC-207 remains In Progress for unresolved diagnostics/classification. Its
  icon/menu/selection, Switch and background repairs are accepted; busy-button
  focus is expected Qt behavior and Tokodon chevron is deferred.
- UQC-208 (P01/P02 palette transitions/pickers) is Done for scoped provider work;
  [manual acceptance](#batch-4-manual-visual-acceptance--2026-09-15) preserves the external P01 defect.
- UQC-209/UQC-210 (L01/L02) are Superseded and removed from this initiative.
  Future Settings/AI sessions must address their incorrect layouts in local SDDs.
- UQC-211 (S01/S02 shell) and UQC-212 (remaining greeter-specific checks after the
  review above) remain Planned. F05 remains an umbrella/AI session-delivery
  investigation. Established external compatibility dispositions do not become
  speculative provider repair assignments.
- UQC-201 remains In Progress for final ecosystem integration at clean published
  pins. The initiative remains Accepted, not Integrated.

Planned packages need a local SDD, exact canonical baseline, settled ownership and
Ready state before implementation. See TASKS.md for package states and historical
handoffs; no new implementation assignment is made by this documentation update.


### D02 context correction and provider handoff — 2026-09-12

Reading the surrounding original Settings log identifies all six warning sites
as Weather page ComboBoxes (provider, location source, temperature, wind, pressure,
refresh interval), not Appearance font selectors. The user reports no console
warnings; the app helper redirected diagnostics to launch.log. The kit's verbose
viewport logging exposes the sizing cycle during construction. Provider UQC-206
records a failing reduced regression and the demand/viewport separation repair.
Font model/reset/replacement coverage remains compatibility evidence.

Published provider `4dfa803` includes D02 sizing and separate UQC-213 F06 policy.
73/73 provider tests plus final focused/installed acceptance pass. D02 stays open
until the actual Settings Weather path is warning-free in the fresh isolated kit.
F06 stays open for manual confirmation. D01/D03/D04 remain accepted. F07 shell
implementation and new kit preparation follow; no manual result is inferred.

### Next-iteration automated evidence / manual gate — 2026-09-12

Fresh final kit: `/tmp/holonight-uqc206-qa20p_jh`, published provider `4dfa803` and
shell `f55cb5f`. D02's actual Settings Appearance/Weather lifecycle is warning-free
under the triggering viewport diagnostics in four style/scale cases. Twelve
actual app processes show candidate-prefix HoloNight/config libraries; missing
runtime evidence and host fallback now explicitly fail isolation. This resolves
the previous kit's automated isolation limitation, not its historical evidence.

F06 window policy and F07 deliberate launcher hit-testing have passing provider
and fake-service/Enter-target regressions. Manual confirmation remains pending;
use the fresh kit's README for Settings/greeter both styles and launcher
browse/search, filtering and reopen with a stationary pointer. D01/D03/D04 remain
accepted; repeat only checks affected by sizing/input changes. No unrelated
UQC-207 finding or broad ecosystem gate is closed. The ledger records the exact
archive, restore command, checksums and test logs.

### Manual dropdown failure / next-session handoff — 2026-09-13

The user reports: "doesn't work. in opened dropdown whatever selected what static
mouse pointer points." An opened dropdown still selects the row beneath a
stationary pointer. The input repair therefore does not satisfy this manual
acceptance check; F06 remains open despite the passing automated regressions.
The application/style and whether this changes the highlighted or committed
selection were not specified. No new launcher result or height-warning evidence
is inferred from this report.

The user requested recording the failure and deferring further work until the
next session before powering off. Resume by reproducing stationary-pointer
selection in the actual dropdown and examining its selection handling as well
as hover rendering. Add a failing regression before repairing it. Preserve the
existing D01/D03/D04 evidence and all immutable kits/archives; the ledger contains
the restoration command for the current candidate. No repair or new verification
was performed after this report.

### Stationary-pointer selection repair — 2026-09-13

The provider follow-up reproduces a concrete functional failure: keyboard Down
scrolls the popup beneath a stationary pointer, native delegate hover changes
move the highlight back, and Enter commits the wrong row. Both owned dropdowns
fail in HoloNight; the icon composite also fails in Fusion. This establishes a
selection path independently of the still-unspecified app/style in the manual
report; it does not reinterpret the earlier visual-only observation.

Published provider `2965d8d` gates native delegate hover handling with the existing
keyboard policy and suppresses stale hover when an owned popup opens. The local
[UQC-213 record](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-213.md)
owns baseline failures and repair verification: 8/8 focused CTests, 73/73 full
provider tests including installed coverage, pointer recovery/immediate clicking,
settled-frame reopening, formatting and existing-only QML lint diagnostics.
Canonical origin/main was independently confirmed before accepting its pin.
F06 remains open pending the focused real-session retest; D02/F07 and unrelated
integration gates retain their prior status. Old kits and evidence are preserved.

### Manual sequence clarified — 2026-09-13

The user identifies Settings and greeter under HoloNight. They report that Fusion
has no hover visual feedback in the tested surfaces; this is their observation,
not a general claim about all Fusion controls. The tested sequence is keyboard-only:
Tab to focus, Space to open, stationary pointer steals selection, Space to close;
the collapsed control contains the new value. Both highlight and committed value
change. No Down/scroll step is required in this reported reproduction.

The new provider test exercises Tab → Space → Space with a stationary pointer over
a different future popup row. It passes with the repair but also with baseline
`4dfa803` in the isolated offscreen fixture. Therefore this exact opening-time
failure is not yet independently reproduced. The earlier failing scroll regression
is related automated evidence, not a substitute for the clarified manual sequence.
The released `06_tsrg6` kit remains unchanged; its runtime contains the same current
repair. For its manual retest, first use exactly Tab → Space → Space without arrow
keys and confirm the value is unchanged, then perform the guide's scrolling and
pointer recovery checks. F06 stays open pending this result.

### Manual stationary-pointer acceptance — 2026-09-13

After receiving the exact `/tmp/holonight-uqc206-06_tsrg6` kit and Settings/greeter
commands under default HoloNight, the user reports: "Fixed. Works as expected".
Accept this as confirmation of the requested Tab → Space → Space sequence with
a stationary pointer over another popup row: the intended highlight and committed
value are preserved. F06 is closed for the reported Settings/greeter HoloNight
behavior. The kit contains published implementation `2965d8d`; the pinned provider
`927d9e9` differs only in documentation.

This user confirmation resolves the manual gate despite the direct opening-time
sequence not failing in the offscreen fixture. Preserve that automated evidence
limit and the earlier failed reports. No new evidence paths were supplied and no
runtime logs were inspected for this acceptance. Do not infer fresh Fusion,
launcher F07, Weather D02, or broad ecosystem acceptance. UQC-201 remains In
Progress and the initiative Accepted. Released kit/archive remain unchanged.

### Settings and launcher manual results — 2026-09-13

The user reports testing Settings and launcher under HoloNight and Fusion: everything
works as expected, no visual defects, and the pointer did not steal focus. Accept
the requested interaction/visual checks as user-confirmed; this wording does not
establish a separate keyboard-focus defect or expand ecosystem acceptance.

Recovered session `/home/tux/uqc-guided-evidence/sway-h9vkfryf` from `/tmp/res.txt`
using user-authorized read-only `sudo -A`. Identity records active local tux UID 1001,
seat0, tty3, session 7; command uses the immutable `06_tsrg6` Sway config (output
scale 1). All three PID records show Qt scale 1.25 and staged executables, imports
and libraries; all isolation.json results are verified with no problems.

| Run directory under that session | PID / style | Result |
|---|---|---|
| `settings-1789325822693874587` | 229302 / embedded HoloNight | Exit 0; WeatherPage and selector activity present, 2476 viewport diagnostic lines, zero height binding loops or TypeError/ReferenceError/SyntaxError/assignment/type failures. D02 Settings checkpoint accepted with the user's successful visual result. |
| `shell-1789326143300249901` | 229986 / embedded HoloNight | Verified staged loading; exit -2 matches saved Ctrl+C transcript. F07 interaction accepted for this style. |
| `shell-1789328881496739096` | 240099 / explicit Fusion | Recovered third run; verified staged loading and user-confirmed interaction. exit.txt absent; log ends with broken Wayland connection. The user confirms deliberately ending the session after testing. Classify this as deliberate session shutdown; numeric exit remains unavailable. F07 accepted. |

Settings Fusion is user-reported only; no separate Settings Fusion run is present
in this session. It is not required for the targeted D02 HoloNight diagnostic gate.
Settings retains a host-portal registration diagnostic unrelated to popup sizing.
Shell logs retain missing Hyprland-signature warnings on Sway, one unexpected
wl_keyboard.leave warning in HoloNight, and Fusion's final broken-connection warning.
Compositor tail has DRM atomic/page-flip busy errors and client broken connections;
the user independently confirms deliberately ending the session after testing.
Do not treat these diagnostics as a launcher crash or erase them from later session review. Preserve
these for session investigations without attributing an F07 selection failure.

Log SHA-256 values, in table order:

- `fcf6611f7a80053cabccb70d1b005e4a59a525fd958ad6eff581725f5afd0fe4`
- `ee35328e5d325d994cb18bc49b96c33c8f36503b9b48d5aee8efd3ac127069b4`
- `8b17e6432e2e138a4a27ecb5881aea2e689fb01fa67c3e28e892f64a4b82eb65`

D01/D03/D04 and F06 acceptance is preserved. UQC-206's owned-application checkpoint
is complete; NeoChat/Tokodon diagnostics remain UQC-201 gates. F07 behavior passes
both styles. The user confirms: "I deliberately ended the session after testing".
This resolves the shutdown classification while retaining missing numeric exit
evidence as a limitation. F07 is closed and Batch 1 is complete. No repeated
interaction run is requested. Batch 2 authentication follows; UQC-201 remains In
Progress and the initiative Accepted.


### Batch 2 authentication repair checkpoint — 2026-09-14

Published shell `fffb1715bac5a57127af5e671033ac33335ffc16`, provider `68b7069`.
The [shell follow-up SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-205.md#batch-2-follow-up--a01a02a04--2026-09-14)
records reproduction, bounded shell repairs and verification. Prior manual failures,
accepted A03 and Batch 1 results remain unchanged.

- **A01 pending targeted manual acceptance:** compiled QML with the real prompt and
  identity models renders labels and local/fallback avatar artwork under both styles
  at scales 1/1.25. Profile updates, label fallbacks, stable-ID keyboard commitment,
  constrained scrolling and reopening pass. Blank rows did not reproduce with the
  current provider; no selector repair or historical-cause attribution is asserted.
- **A02 closed:** all four baseline lifecycle regressions reproduced the orphaned
  Password label after a synthetic session failure. A shared AwaitingInput visibility
  condition repairs the whole input group. Rendered failure retains the error and
  Retry/Cancel, retry waits without inputs, and a new prompt restores cleared,
  unrevealed, focused input. Real coordinator/model and test-only sessions pass;
  no PAM credential submission was used or requested.
- **A04 repaired, targeted manual acceptance pending:** the graphics-backed scale
  1.25 reproduction measured left/right coverage of 0.792/1.269 physical pixels
  with the background on the scrolling clip. A shell background inset makes them
  1.281/1.281, preserving palette, rounded appearance and intended border widths.
  Focused/unfocused and constrained scrolling checks pass in both styles/scales.
  Software-only captures had not reproduced this failure; their result is distinct.

Final local suite: 1171/1171; supplemental rendered matrix, static checks and staged
runtime verification pass. The fresh immutable kit and exact verification inventory
are in the [coordination handoff](TASKS.md#batch-2-authentication-handoff-and-fresh-kit--2026-09-14).
The [manual request](AUTHENTICATION-BATCH2.md) is two owned Polkit identity/prompt
inspections with credential-free cancellation, then one Fusion Askpass border check,
in a fresh real tux Hyprland login at output 1 / Qt 1.25. No manual observations
have been returned for this kit. A01/A04 and manual shutdown classifications remain
pending; Batch 2 is not closed and broader acceptance is not implied.


### Batch 2 authentication manual acceptance — 2026-09-14

The user reports: “all tests passed, no issues observed” for the fresh immutable kit
`/tmp/holonight-uqc205-b2_vmvoyd51`. **A01 and A04 are accepted** for the targeted
identity/prompt inspections in HoloNight and Fusion and the Fusion Askpass border/ring
inspection. A02 remains closed by synthetic lifecycle/rendered tests; no additional
failed credential submission is required. Historical A03 and Batch 1 acceptance stand.
A01 acceptance establishes current behavior, without attributing the historical blank
rows to an unproven repair.

Read-only inspection correlates the report with
`/home/tux/uqc-auth-evidence/session-9.jsonl`. All three runs belong to fresh local
tux session 9 (UID 1001, seat0, tty3, Wayland, leader 412438), with eDP-1 output
scale 1 and actual Qt DPR 1.25. Requested and actual styles match. Every required
module is verified from the immutable kit prefix, using PID-tagged loader records.
No ReferenceError, TypeError, binding-loop, assignment or required-property diagnostic
was found in the three process logs.

| Indexed run under `/home/tux/uqc-auth-evidence/` | PID | Registration and bounded result |
|---|---|---|
| `9-001-polkit-Holonight-1.25` | 414942 | Exclusive registration with authority `:1.28`, agent `:1.11191`, serial 9. Challenge timed out after 60.063 seconds, exit 124. Agent supervisor interrupted; child terminated with exit 0. |
| `9-002-polkit-Fusion-1.25` | 416228 | Exclusive registration with authority `:1.28`, agent `:1.11293`, serial 9. Challenge normally exited 126 (Request dismissed) after 25.657 seconds. Agent supervisor interrupted; child terminated with exit 0. |
| `9-003-askpass-Fusion-1.25` | 416707 | Normal exit 1, zero stdout bytes, consistent with cancellation. |

Both Polkit executables match SHA-256
`70155604f039965621511609baf40f80033dd75a56db3a22162d97e452c96b8b`;
Askpass matches `0097e31c38f8196c72dffa39a02467af9068df99602bf6b1e33454e5266aec88`.
Process-log SHA-256 values, in run order:

- `d11e79cab1ddf752bc633be87d48210c7e70aeafb8b748113c691ac4ffe34ea4`
- `a1ff54a46865027e9f32a2d5889b92f9e322dd3d2935e018a28ef37de0cd4cc4`
- `108d6d2348026ce9691baf44e16d99bb553b3b7108d4744e9d8f4898e633c2be`

The HoloNight log contains BeginAuthentication, CancelAuthentication and agent
unregistration. The user clarifies: “Inspection took over 60 seconds.” Its exit 124
is therefore classified as the visual inspection exceeding the harness deadline;
it is not normal requester completion and does not establish a cancellation regression.
Fusion provides normal bounded cancellation evidence, and the accepted A03 automated
and earlier manual completion checks remain intact. Both test agents stopped cleanly;
Askpass cancelled normally. The user reports no shutdown issue; no separate numeric
compositor exit result is asserted.

**Batch 2 is closed:** A01/A02/A04 have supported acceptance, the shell implementation
and umbrella pin are published, and the saved process outcomes are classified. No
repeat visual checks or failed credential submission are needed. Batch 3 follows with
Haruna crash/diagnostic classification. Broader compositor, successful-authentication
and activation gates remain Batch 8; UQC-201 stays In Progress and the initiative Accepted.


### Batch 3 investigation and rendering repair — 2026-09-14

Baseline umbrella `5822417dca1b8735bf4afbdb49ac7604ce283dca`, provider
`68b7069cc10b85cf0ce591b89cf8c1494bf316b3`: both clean and equal to canonical
origin/main before UQC-207 assignment. Local repair requirements and regressions
belong to [UQC-207](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-207.md).
Batches 1–2 remain accepted; UQC-201 remains In Progress and the initiative Accepted.

**C06 original crash recovered, cause still open.** Original run
`/home/tux/uqc-guided-evidence/hyprland-j97jound/haruna-1789046055724363325`,
PID 72625, tux session 5, exited -6. The retained core records SIGABRT at
2026-09-10 13:25:58 UTC, about eleven minutes after the saved PID metadata.
The final log diagnostic is `QQmlEngine: Illegal attempt to connect to QQuickRectangle`
in a different thread from the QML engine. The stack reaches
`QQmlPropertyCapture::captureNonBindableProperty`, AOT scope-property lookup,
and provider ItemDelegate background construction. The retained provider module's
build ID `425b2b87f8a0e9cf8a990581c6fb5edceac5a944` exactly matches the core.
Addresses `0x2c4791` / `0x2c4833` resolve to the generated `anchors.fill: parent`
binding at original ItemDelegate.qml line 84. This identifies the fatal path;
it does not establish the initiating lifetime/threading defect or prove that
R03's selection change repairs it.

Read-only original copies, extracted core, module inventory and crash metadata are
retained privately in `.cache/uqc207/investigation/`. Original launch-log SHA-256:
`c324c2a00b458d4864ce18f53fb34b05818ec575b559a6d190048ee7ec0186fb`.
PID-map SHA-256: `2e958194631d73ad5b5a1a9b844444c595c30c049e2a633b6847cd27ec71ad79`.
The source logs and released kits were not overwritten.

Twelve fresh-profile, private-bus, offscreen/software Haruna launches (three per
style at Qt scale 1 and 1.25) all reached the ten-second deadline; the harness
then terminated each with SIGTERM (-15). These are bounded survivals, not normal
exits or a crash explanation. `.cache/uqc207/launches/` retains per-run logs,
PID maps, outcomes and log hashes; `.cache/uqc207/launch-matrix.py` records the
procedure. HoloNight maps identify the staged provider/config libraries. The
software renderer and lack of the original settings interaction limit this comparison.
No crash stack exists for those non-crashing runs. Scale factors in these launch
records are requested values, not independently measured application DPRs.

Separate diagnostic classification from matching Haruna 1.8.1 release source:

| Diagnostic | Owner and evidence | Status |
|---|---|---|
| ImageAdjustmentSlider.qml:35 `activeControl` | Haruna unconditionally assigns `background.activeControl` on a standard Slider, assuming a style-specific background API. | Application compatibility boundary; no provider property shim added. Independent of the fatal diagnostic. |
| Main.qml:106 QString-to-int | Haruna assigns `"auto"` to `mpv.audioId` when preferredTrack is zero. | Application/backend type contract; not a provider rendering repair. |
| AboutItem.qml:381 null height | Original stack-independent Kirigami AboutItem diagnostic. | Historical evidence retained; current reproduction/acceptance still open. |
| MessageDialog undefined Success/null size | Historical NeoChat/Tokodon diagnostics also reported under Fusion. | Separate Kirigami/consumer investigation remains open; no palette attribution. |

Current package snapshot: Haruna `1.8.1-2`, NeoChat/Tokodon `26.08.1-1`,
Qt base `6.11.2-3`, declarative `6.11.2-1`, Kirigami `6.30.0-1`,
Kirigami Addons `1.13.1-1`. The third-party/Kirigami versions differ from discovery;
do not present new comparisons as identical historical-package reproductions.

**R01/R02/R03:** Haruna SettingsWindow delegates use Action.icon.name and explicit
navigation highlighting. Its ShortcutsSettings reuses ItemDelegates with custom
RowLayout/IconTitleSubtitle/KeySequenceItem content and no explicit selection flag.
Baseline regressions fail for named menu/navigation icons, unconditional menu icon
space, and current-row-only selection. The repaired HoloNight controls render names
and URLs through HnIcon, reserve an icon column per visible menu contents, and render
selection from explicit highlighted/checked states. Mirroring, dynamic item/icon/
visibility changes, checked menu activation, explicit selection and keyboard focus
are covered. Fusion comparisons retain Fusion conventions. Manual actual-app
acceptance remains pending.

**R04 clarified by the user:** any checked Switch demonstrates the concern; the
thumb focus ring blends with the track. The requested ring surrounds the whole
control. The provider moves it to the full-control background, preserving track,
thumb and public sizing APIs. The rendered baseline difference covers only the
thumb; repaired coverage surrounds the control in both states and at both scales.
Manual AI acceptance remains pending.

**F04 clarified:** the user believes any keyboard-activated button is affected,
with “Test connection” as an example. A plain Button's Tab → Space → Tab → Backtab
regression retains actual focus owner, Tab/Backtab reason and visualFocus in both
styles/scales. This does not reproduce the reported problem. AI's Test connection
button disables itself during the asynchronous operation; actual application owner/
reason evidence during that lifecycle is still required. No speculative Button or
AI repair is claimed. F03's suspected disabled stop likewise remains unattributed.

**C05 ownership established:** Haruna ToolTipButton.qml independently binds each
ToolTip.visible to its own checkable button, sets timeout -1 and Popup.NoAutoClose,
and does not use a shared exclusivity group. Concurrent help popups are therefore
application-controlled behavior. No provider exclusivity requirement is introduced;
focused manual classification/acceptance remains pending.

**C01/C02/C04:** installed-source compatibility probes retain their logs in
`.cache/uqc207/compatibility-*.log`; these are reduced fixtures, not actual application
acceptance. Fusion FormCard check/radio delegates replace contentItem with null,
set spacing/padding to zero and add an external label margin. At DPR 1/1.25 the
indicator-only Fusion control measures width 0, indicator width 14 and x=-7, while
the label starts at x=8: the visible gap is only one logical pixel. These are
Kirigami composition plus Fusion sizing conventions, not HoloNight geometry.
Fusion's 30-row popup measures height 468, viewport 466 and contentHeight 1080;
first/last scroll positions are 0/614. Its runtime origin is Fusion ComboBox and
Kirigami's supplied delegate; HoloNight-like appearance does not establish a mixed
style. This is available-height scrolling, with no reduced-fixture unreachable rows.
Haruna's warning is Kirigami.InlineMessage, whose own background composes nested
rectangles and a 60%-radius inset fill. Visual corner acceptance remains open.
The HoloNight fractional-scale reduced probe has inconsistent indicator geometry
and needs isolation review before being used as acceptance evidence.


Provider rendering implementation `fbffc872c31ad8c8c22d499a08c8259e781f0a51` is
published and canonical availability was confirmed before the umbrella pin.
All 77 provider CTests pass, including installed-package acceptance. Formatting,
provider/demo/gallery import policy and licensing pass; QML lint has only existing
unrelated diagnostics. This verifies implementation, not pending manual findings.


Fresh isolated compatibility reruns against the staged published provider resolve
the earlier fractional-scale fixture inconsistency: HoloNight check controls measure
width 16 with label x=24 at both DPRs; Fusion measures width 0, indicator x=-7/width 14
and label x=8 at both DPRs. Logs are `.cache/uqc207/compatibility-isolated-*.log`.
These runs use separate empty configuration/cache/data/runtime directories, explicit
staged libraries and report actual fixture Window.devicePixelRatio (1 or 1.25).
The earlier non-isolated observation remains retained and is not used for acceptance.


Read-only recovery of original AI focus events adds historical owner evidence.
HoloNight run `ai-1789029827393494892` has log SHA-256
`a1929f292c04ce19b62b20c3a92400cc81d1482b15d4a0fcf8a30a27309cd1f0`;
Fusion run `ai-1789039726877575859` has
`53b12319ce105d1464fa43bc1118216612ddc218f7f0c7f7dabaec0057dc5b78`. Selected focus records are privately retained as
`.cache/uqc207/investigation/ai-*-focus.txt` with original line numbers.
HoloNight lines 117762–119011 show Context-window editor → Temperature RowLayout →
Temperature editor, followed by Slider at 120324. This observed intermediate owner
is a layout, not evidence of a disabled Control receiving focus. Both styles also
show an HnFormField Loader stop before the subsequent action button. This is
historical evidence preceding UQC-204, not proof of a present failure.
HoloNight lines 137903–138898 show ProviderActionButton ↔ enclosing Loader changes;
Space-event/reason correlation and exact button label are not established by the
selected records. Do not claim the button kept focus or assign a new consumer repair
from those transitions alone. The fresh actual-app F03/F04 retest remains required.

Final manual kit `/tmp/holonight-uqc207-8jhojhzb` contains published provider `fbffc87`.
Provider, newly built AI and Settings acceptance passes at both styles/scales;
twenty actual staged launches pass module-path/origin checks. The harness sends
SIGTERM after inspection: sixteen children exit -15; all four NeoChat runs handle
termination and exit 0. These are supervised shutdowns, not user-completed sessions. The helper records missing actual application DPR as null;
these launches do not supply the plan's complete per-window DPR/focus-owner evidence.
Seven evidence-helper tests pass, including foreign Fusion module requirements and
preservation of a -6 outcome in the run index. Restoration and file hashes pass.
The initial `i0u2klt7` kit/archive remains preserved; use the replacement above.
[Focused manual instructions](RENDERING-BATCH3.md) follow. No manual Batch 3 result
has been received; no finding is closed by kit preparation alone.


Final bounded startup log review finds NeoChat RoomDrawer.roomDrawerWidth binding
loops under both styles at both scales, at NeoChat Main.qml:153. The remaining
sixteen logs have none of the scanned TypeError/ReferenceError/assignment/binding-loop
markers. The RoomDrawer diagnostics remain C06 compatibility evidence; successful
loading is not a warning-free claim. No new MessageDialog/AboutItem reproduction
was observed on those limited startup paths. The scan is retained in
`.cache/uqc207/final-runtime-diagnostics.json`.


### Batch 3 manual review and external ownership — 2026-09-14

This review supersedes the pending-manual wording in the preceding checkpoint,
without replacing its historical evidence. User notes: `/tmp/res.txt`, SHA-256
`254267165f6c32a2b8ad1d83b2dc5069d476cbc67970b3815b2cf572426df17e`.
Session: `hyprland-fpyxbe1q`, kit `holonight-uqc207-8jhojhzb`, provider `fbffc87`.
The twenty reported runs cover five applications, both styles and requested scales
1/1.25. All exit 0. Read-only verification matched all 21 indexed log hashes,
including an additional Settings run `settings-1789382239077263155`: that run exits
0 but has incomplete isolation and no PID snapshot, so it is excluded from acceptance.
Actual per-window DPR is still not established by the manual run index. Successful
current exits do not explain or erase the original Haruna SIGABRT.

**Disposition terminology:** “Not fixable within HoloNight” means that the demonstrated
fault belongs to external application/library code and needs an upstream change under
the agreed no-third-party-patches scope. It does not mean impossible to fix upstream.
An external preference or stock-style convention is not automatically a bug. Unknown
ownership remains open; occurrence under both styles alone is insufficient evidence.

| Finding | Reviewed disposition and evidence |
|---|---|
| R01 — Haruna menu/navigation icons | **Open; HoloNight repair required.** Both HoloNight runs log failures from `Holonight/Core/HnIcon.qml:54` and `image://hnicons`, including `configure`, `media-seek-forward`, `contrast` and `tools-report-bug`. Fusion displays the application icons. The provider's `IconThemeResolver` searches `.svg` files in a fixed theme list; it does not implement standard theme inheritance or non-SVG fallback. The prior self-contained SVG fixture did not validate real application resolution. Determine the exact failing lookup path before the next repair; this is not an external-bug exemption. |
| R02 — menu icon column | **Open actual-app acceptance.** Haruna supplies icons for most entries, so reserving the shared column is correct even when R01 prevents painting them. Blank space is not proof the new conditional-column logic failed. Preserve its passing insertion/removal/mirroring regressions; retest actual menus after R01. |
| R03 — persistent Shortcuts row | **Open.** “Nothing really changed” does not provide a successful row-selection retest. The prior reduced regression passes, but no actual-app repair acceptance is claimed. |
| R04 — Switch keyboard outline | **Open; HoloNight repair required.** The whole-widget rectangle in `Switch.qml` includes the label and fails the clarified requirement. The focus outline must follow the pill-shaped switch track, exclude its label, and remain visible checked/unchecked. This corrects the earlier interpretation of “whole control”; the existing whole-widget rendered test asserts the wrong acceptance target. |
| F03 — hidden/disabled traversal | **Reported traversal accepted for the tested AI path.** User confirms no hidden stop between Context window and Temperature and the Enabled control remains enabled. No disabled-control owner was ever demonstrated; do not invent an additional disabled-focus repair. This does not close F04. |
| F04 — Space removes button ring | **Open; owner unresolved.** User reproduces it in both styles immediately on Space, with subsequent Tab/Backtab working. That traversal is not sufficient to establish the exact activeFocusItem or focusReason during activation. Plain-button regressions pass; AI Test connection disables while busy. Current log inspection does not establish a Space-correlated owner/reason timeline. Do not mark Qt, Hyprland or the provider unfixable from this evidence. |
| C01 — Settings page differences | **Known composite boundary, not established external bug.** Appearance uses HnIconComboBox with an explicit HoloNight frame; Weather uses ordinary Controls.ComboBox, hence different Fusion appearance. Public composite APIs and accepted fallback boundaries remain preserved. The missing visible Fusion hover remains **open**: installed Fusion ButtonPanel does consume `control.hovered`, so “Fusion never implements hover” would be false. Need actual hovered state/contrast evidence before classifying this symptom. Small text padding remains a preference. Haruna Fusion menu hover also remains unverified. |
| C02 — Fusion check/radio label gap | **Not fixable within HoloNight: Kirigami FormCard/Fusion layout incompatibility.** FormCard replaces the control content with null and removes padding/spacing. Fusion's implicit width then ignores its indicator. Existing isolated measurements at both DPRs show control width 0, indicator width 14/x=-7, external label x=8, leaving only one logical pixel. An upstream composition/sizing fix is needed; do not change Fusion globally. |
| C03 — Tokodon Fusion Switch extends past row | **Not fixable within HoloNight: same upstream composition/sizing incompatibility.** Installed FormSwitchDelegate uses a zero-padding, null-content Controls.Switch. A new stock-Fusion offscreen fixture at actual DPR 1 and 1.25 reproduces control width 0, indicator width 40/x=-20. In a 400-wide row, the content starts at 12 and the switch at content x=376: indicator right edge is 408, eight pixels outside the row. No HoloNight QML override is required to reproduce this. |
| C02 — tall / HoloNight-looking Fusion popups | **Stock/composite behavior, no demonstrated sizing bug.** Installed Fusion owns the popup, Kirigami supplies delegates. Prior 30-row probe reaches first/last rows and uses available-height scrolling. Appearance alone is not mixed-style evidence. Keep actual-app reachability acceptance open where not explicitly reported; do not classify functional tall popups as unfixable defects. |
| C04 — Haruna warning corners | **External visual composition; outside provider repair scope.** Kirigami InlineMessage draws its own nested background rectangles with a reduced-radius inset fill. HoloNight does not own these corners. This establishes the owner, not that the subjective corner mismatch is an upstream defect; visual acceptance remains open. |
| C05 — concurrent Haruna help popups | **External application behavior / preference, not a confirmed bug.** Haruna ToolTipButton intentionally binds each popup to its independent checked state with no timeout or auto-close. Exclusivity would require a Haruna product change. No provider requirement or silent user acceptance is inferred. |
| R05 — transparent HoloNight ComboBox dropdowns in NeoChat/Tokodon (new) | **Open; investigate HoloNight rendering first.** Reported in both applications with HoloNight. Provider ComboBox supplies a Rectangle background using popup ControlPalette.surface; Kirigami FormComboBoxDelegate supplies item delegates. Neither the exact background alpha nor a replacement popup has yet been measured in these applications. Do not mark this external or silently defer a missing background to Batch 4 palette transitions. |

C06 is split by diagnostic rather than given one blanket disposition:

| Diagnostic | Disposition |
|---|---|
| Haruna `ImageAdjustmentSlider.qml:35`, missing `activeControl` | **Not fixable within HoloNight: Haruna style-specific API assumption.** Matching release source writes an undeclared property on a standard Slider background. Reproduces eight times in each current HoloNight run. A provider shim would endorse a non-public contract. |
| Haruna `Main.qml:106`, string assigned to integer audioId | **Not fixable within HoloNight: Haruna/mpv property contract.** Matching release source assigns `"auto"` to the integer property. Historical evidence retained; no new occurrence established in this manual review. |
| Kirigami `AboutItem.qml:381`, null window height | **Not fixable within HoloNight: Kirigami null-window handling.** Current Fusion Haruna run `haruna-1789380199968060819` reproduces it twice. Installed source dereferences `parent.Window.window.height` without a null guard. Associated OverlaySheet binding loops remain separately recorded; no crash causality is claimed. |
| Kirigami Addons `MessageDialog.qml:45` undefined Success; lines 96/97/111 null dimensions; AboutPage null width | **Not fixable within HoloNight: external Kirigami Addons/application lifecycle or type-resolution defects.** Current NeoChat and Tokodon reproduce these under stock Fusion as well as HoloNight. Source owns both the self-type enum lookup and unguarded popup-parent dimensions. The precise upstream enum-resolution trigger remains unresolved; no HoloNight control patch is justified. |
| Kirigami ScrollablePage null flickable, FormDelegateBackground null visibleChildren | **External diagnostics; not fixable within HoloNight under this scope.** Current Fusion runs reproduce the same external-source errors. Exact lifecycle trigger and user-visible consequences remain unestablished; do not equate them with popup transparency. |
| NeoChat RoomDrawer.roomDrawerWidth binding loop | **External application diagnostic; not fixable within HoloNight under this scope.** NeoChat Main.qml:153 owns the binding; retained staged startup evidence reproduces it in both styles. No provider repair or visual consequence is claimed. |
| HoloNight ScrollBar.qml:45 null orientation (new) | **Open; provider-owned diagnostic.** Current HoloNight NeoChat/Tokodon logs dereference a null root in the height Binding. Keep separate from external teardown errors and R05; occurrence near teardown does not exempt the provider. |
| Original Haruna SIGABRT / cross-thread QML connection | **Open; root cause unresolved.** Historical core reaches generated HoloNight ItemDelegate code; initiating thread/lifetime fault is unknown. New Fusion Haruna log also reports an event-filter thread warning, but that is not proof of the same cause. Neither successful retries nor external diagnostics permit marking this crash unfixable upstream. |

Verification for this review: read-only source ownership inspection; all saved
index/log hashes matched; stock Fusion FormSwitchDelegate geometry reproduced at
actual DPR 1/1.25 using offscreen software rendering, without desktop interaction.
Probe and logs: `.cache/uqc207/review-switch.qml` and `review-switch-stderr*.log`.
No product code changed or product suite rerun. Batch 3 and UQC-207 remain open;
UQC-201 remains In Progress, initiative Accepted, and Batches 1–2 remain accepted.


### Batch 3 focused repair iteration — 2026-09-14

Ownership review checkpoint `93d1190` preserves the four pending documentation
changes. Provider started clean at canonical `fbffc872c31ad8c8c22d499a08c8259e781f0a51`.
Verified repair `a7e50b05d38a6dc8ed24151685803c75fb16824c` is published on canonical
origin/main and clean before the umbrella pin update. Initiative stays **Accepted**;
UQC-201 and UQC-207 stay **In Progress**. Batches 1–2 and prior kits remain preserved.

| Finding | This iteration's evidence and acceptance boundary |
|---|---|
| R01 icons | **Repair candidate; human menu/navigation acceptance pending.** Staged Haruna selects HoloNight, fallback Papirus, with /usr/share/icons in its paths. HoloNight inherits missing Papirus variants then installed breeze-dark; the baseline resolver never visits that parent. On the bounded comparison path Qt finds icons that HnIcon cannot read: 29 of 31 unique inputs fail, including contrast, tools-report-bug and media-seek-forward. Repaired lookup resolves all 31 names; logged image failures fall from 100 to zero. Indexed inheritance includes symlinks and cycle protection; caches follow resolved source content and image URLs carry a content revision. Semantic SVG colors and URL inputs remain covered. No non-SVG failure was demonstrated, so this iteration does not claim raster-format support. These bounded launches compare icon resolution, not historical crash causality. |
| R02/R03 menus and Shortcuts | **Actual-app acceptance open.** Inherited-theme named/URL fixture, menu insertion/removal/visibility/mirroring and explicit row selection pass. The optional observer now records actual delegate identity, context origin, highlighted/checked/current/visualFocus when the human visits Shortcuts. No application selection result is inferred from the reduced regression. |
| R04 Switch | **Repair candidate; human AI/Settings acceptance pending.** Replaced the full-widget rectangle with a transparent pill outside the indicator track, with a two-logical-pixel gap and existing focus color/width tokens. Rendered regression measures track-centered feedback while keeping track interior unchanged, across both states, all four size roles and mirroring. Hit area, label, implicit sizing and thumb animation remain preserved. |
| R05 popup transparency | **Open; not reproduced, no palette/geometry edit.** Installed FormComboBoxDelegate settles to a visible opaque background at (12,110), 372x92 logical pixels, opacity 1, color #ff131a24, measured DPR 1; the style/scale matrix verifies background pixels at DPR 1/1.25. The earlier 8-pixel pre-layout height was rejected as incomplete measurement. Explicit translucent owner palette and explicit popup override remain preserved. New observer records actual-app background origin/dimensions/visibility/opacity, palette roles and rendered pixels for the next human session. |
| Provider ScrollBar null orientation | **Open; not reproduced, no source repair claimed.** Repeated popup creation/open/close/destruction during animation and garbage collection, both orientations, plus application-engine teardown pass without the diagnostic. The historical actual-app warning remains valid evidence and needs its exact lifecycle trigger. |
| F04 button focus | **Open; evidence tooling verified, actual AI timeline pending.** Opt-in observer records labeled button identity, enabled/down, focus owner/reason, visualFocus and Space before press/release and after delivery. A headless busy/always-enabled two-button fixture verifies 34 observations per style, including transient disabled/down states. This verifies the observer, not AI ownership. F03's accepted reported traversal is preserved. |
| Original Haruna crash | **Open; evidence preserved.** Core SHA-256 and current executable hash are retained in iteration-crash-identities.sha256. Original core module listing and current executable both identify Haruna build ID `7af55f8ac3daad32fea4225cf4e89f86e1523db6`; this strengthens binary identity but does not identify the initiating thread/lifetime defect. No new crash occurred during the bounded icon comparison. |

Verification (2026-09-14), evidence under `.cache/uqc207/`:

- Failing baselines: `iteration-switch-baseline.log` (both HoloNight scales) and
  `iteration-icon-baseline.log` (inherited lookup/source-cache regression).
- `ctest --test-dir holonight-qt/build -R 'holonight_shared_rendering|^holonight_tests$' --output-on-failure`:
  5/5 pass, `iteration-focused-final.log`. This includes the installed Kirigami
  composition on this host; systems without that optional module skip its fixture.
- Installed-package acceptance passes. `ctest --test-dir holonight-qt/build --output-on-failure`:
  77/77 pass, `iteration-full-provider.log`. An earlier overlapping build prevented
  four test processes from starting; the completed-build rerun above supersedes it.
- AI and Settings acceptance binaries against staged provider: both styles × scales
  1/1.25, all eight pass (`iteration-{ai,settings}-*.log`). The first Settings harness
  invocation lacked its required disposable appearance path; the corrected run passes.
- clang-format dry-run, provider/demo/gallery import policy, `all_qmllint`, and REUSE
  lint pass. QML lint retains pre-existing diagnostics; no new Switch warning.
  Logs: `iteration-qmllint.log`, `iteration-reuse-final.log`.
- Collector tests: 8/8 pass, including rejection of requested scale as measured DPR.
  Diagnostic observer compiles and its two-style behavioral check passes.

No external application/Kirigami or AI/Settings source changed. Unresolved Fusion
hover, external preferences and previously classified external defects retain their
prior dispositions. Actual-app acceptance is still required; none is silently closed.


Fresh immutable kit: `/tmp/holonight-uqc207-5j2ew840` (READY).
Archive: `.cache/holonight-uqc207-5j2ew840/holonight-uqc207-5j2ew840.tar.gz`.
SHA-256: `02e6af10f58a84b815c3b68de8d5dda0171c7116e0e4714bdd73f268b7edff11`.
All 33 preparation steps pass, including fresh AI/Settings builds, twelve staged
provider/consumer style-scale cases, collector tests, and restoration at the exact
configured prefix. Read-only post-restoration verification matches all 200 kit
file hashes. The installed FormCombo fixture actually ran in all four kit cases.
Logs/results: `.cache/holonight-uqc207-5j2ew840/`.

Twenty bounded staged application checks (five apps × both styles × both scales)
verify module isolation and runtime-selected origins; all indexed log hashes match.
Sixteen processes exit -15 after the planned SIGTERM deadline and four exit 0;
none exits prematurely or needs a forced kill. All twenty have measured window DPR
records (1 or 1.25), stored independently of requested scale. No new hnicons image
failure or provider ScrollBar orientation error appears on those limited paths.
This is loading/observation validation, not interactive acceptance or an explanation
of the historical crash. Existing external diagnostics remain outside repair scope.

From a fresh local tux VT, start:

```sh
python3 /tmp/holonight-uqc207-5j2ew840/guided-session.py hyprland
```

Follow the kit's README for human-operated Haruna icons/Shortcuts, AI button/Switch
focus, Settings Switch focus, and NeoChat/Tokodon popup backgrounds under both styles
and scales. Use `--diagnostics` to retain the state timeline. No desktop pointer/focus
was automated. Accepted authentication, dropdown navigation and F03 traversal are
excluded; deferred Fusion hover/external preferences remain recorded. Manual results
are pending, so the initiative and work-package states are unchanged.


### Batch 3 focused repair manual results — 2026-09-14

User notes: `/tmp/res.txt`, SHA-256 `c610779c30b570ce1abca07528d768d3a9ea88d2528b5c486765945e57dd4b27`;
preserved at `.cache/uqc207/manual-latest-notes.txt`. The notes identify session
`hyprland-ma02h33q` and twenty runs covering five applications, both styles and
requested scales 1/1.25. All twenty finished records independently match their log hashes and exit files
(exit 0). Recomputed module-isolation checks pass for all twenty using saved PID
maps/environment; every run identifies kit `holonight-uqc207-5j2ew840`. Actual DPR
was recomputed from window observations and matches the indexed measurements
(1 or 1.25). The initial permissions limitation was resolved by the user copying
the evidence to `/tmp/uqc207-manual-evidence`. Analysis and extracted state/event
records are retained in `.cache/uqc207/manual-analysis/`.


| Finding | Latest manual disposition |
|---|---|
| R01/R02/R03 — Haruna icons, menu layout, Shortcuts selection | **Accepted for the tested paths.** For HoloNight at both scales, the user reports that everything except ComboBox transparency is fixed. This accepts the requested icon/menu/Shortcuts checks within the focused instructions. Fusion has no new issues at either scale. The original crash finding is separate and is not closed by this statement. |
| R04 — Switch outline | **Accepted for the tested paths.** AI explicitly reports the Switch focus ring fixed at both HoloNight scales; Settings reports Switch focus good at both scales. Fusion comparisons are also reported good. |
| R05 — ComboBox transparency | **Open; actual-app measurements point to background sizing.** Every recorded HoloNight popup in Haruna/NeoChat/Tokodon has a visible 120×8 background, opacity 1, alpha 255, and sampled pixels matching its surface color (#ff131a24 or #ff141618). Its origin is provider ComboBox.qml. No later larger background sample is recorded for those popup IDs. NeoChat/Tokodon Fusion backgrounds measure 510×528. This supports a geometry investigation; it does not prove a persistent height binding failure because the observer lacks popup/content/model dimensions and continuous visibility history. Do not repair this by forcing palette alpha. |
| F04 — button activation focus feedback | **Open; the busy-action lifecycle is now established.** In all four AI runs, Test connection and Refresh models retain keyboard visualFocus through Space press and just before release. After release they become disabled, focus moves to a Loader, and the same button regains focus with reason 7 (OtherFocusReason), visualFocus=false, once enabled. Test connection returns in 18–54 ms after the initial press snapshot. The captured always-enabled Reset activation (Fusion, scale 1) retains owner, reason 1 (TabFocusReason), and visualFocus=true. Do not generalize this Reset comparison to unobserved controls/style-scale cases. |
| Provider ScrollBar diagnostic | **Open; reproduced in the new actual-app logs.** ScrollBar.qml:45 null-orientation occurs five times across the four HoloNight NeoChat/Tokodon runs (NeoChat scale 1.25 has two occurrences). There are no matching Fusion occurrences. The exact destruction trigger still needs a failing reduced regression; no source repair is claimed. |
| Historical Haruna crash | **Open; root cause unresolved.** Four reported Haruna exits are 0, but they do not explain the preserved SIGABRT. No new crash is reported. |

Previously accepted checks and external classifications remain preserved. No
product source changes accompany this review; a disposable headless focus fixture
was run to test the observed lifecycle. The
initiative stays Accepted; UQC-201/UQC-207 stay In Progress because R05, F04 and
remaining diagnostic/crash investigations are open. Follow-up should reproduce the measured popup geometry and ScrollBar lifecycle
without repeating accepted icon/Switch checks.

**Focus ownership check:** AI's `ProviderFormActionRow.qml` owns the action Loader;
`OllamaSettingsPanel.qml` explicitly disables Test connection and Refresh models
while their operations run. The affected buttons are not inside the provider's
HnFormField/HnSettingsRow control Loaders. A disposable stock-Fusion Loader/Button
fixture with temporary disabling reproduces re-entry with OtherFocusReason and no
visualFocus; an always-enabled button retains keyboard focus. This establishes an
ordinary disabled/re-enabled focus lifecycle, not a global Space or HoloNight
Button rendering defect. Preserving keyboard feedback across the busy action is
an AI interaction requirement: any repair needs a separate AI-local SDD and Ready
work package, and must avoid stealing focus after the user navigates elsewhere.
Fixture/build/log: `manual-analysis/focus-loader-*` under `.cache/uqc207/`.

**Haruna selection check:** all four runs contain actual delegates originating at
`qrc:/qt/qml/org/kde/haruna/qml/Settings/ShortcutsSettings.qml`. Current rows report
`current=true`, `highlighted=false`, `checked=false`, `visualFocus=false`, supporting
the user's visual acceptance. No hnicons image failure is found in the twenty logs.
Successful process exits still do not close the historical crash investigation.

Verification: saved hashes/exits, recomputed isolation and window DPR for all twenty
runs; actual popup/delegate/Space-state inspection; stock-Fusion focus-lifecycle
probe exits 0; documentation diff check passes. No product suite was rerun because
only the umbrella acceptance record changed. Released kits and provider pins remain
unchanged.

### Batch 3 dropdown background repair — 2026-09-14

Primary reproduction: NeoChat at scale 1. The user confirms that all tested
ComboBoxes in NeoChat, Tokodon and Haruna show the same missing background with
both mouse and keyboard, independently of the preceding action.

The saved NeoChat run `neochat-1789394424258792979` contains additional Qt geometry
records beyond the old observer snapshot: popup item `55ca66581e50` reaches
510x232, content `55ca66582e60` reaches 502x224, but background `55ca66801d60`
remains 120x8. Its opaque color is correct; coverage is not.

A deterministic reduced regression now reproduces that exact 120x8 background
with `QT_LOGGING_RULES=qt.quick.viewport.debug=true`. The original guided session
sets `*.debug=true;*.info=true`, which enables this category. Both an installed
FormComboBoxDelegate and a ComboBox populated/attached after creation fail full
coverage and reopening assertions. With debug logging disabled they pass. Enabling
only QML, control item-management, dirty, effectiveclip, focus, pointer or window
logging does not reproduce the failure. The observer is not needed to trigger it.
This is a deferred-geometry/diagnostic interaction, not palette transparency or
scale conversion. No new fractional-scale acceptance is required.

The provider candidate binds its ComboBox popup background dimensions to the
popup dimensions minus public insets. Coverage remains live under the demonstrated
logging condition; explicit translucent owner palettes, explicit popup palette
precedence and transition policy remain intact. The existing pixel test samples
beyond the old strip and now requires full dimensions. Reopening and nonzero insets
are checked too. No public API or dependency changes.

The observer had a separate reproducible defect: reading every visual control's
`popup` property instantiated an unopened deferred popup. The retained old observer
fails the new check with exit 3. The replacement traverses existing QObject/visual
trees, observes only existing popups, and adds owner, popup, content and background
parent geometry plus open/closed state. Checks with the observer on/off and both
styles pass without instantiating the unopened popup. The collector now records Qt
logging rules and clears inherited observer activation for uninstrumented runs.

ScrollBar remains **open, unreproduced in reduced fixtures**. Popup creation and
destruction during animation, application-engine destruction, ScrollView page
destruction and settled vertical/horizontal scrollbar window destruction do not
reproduce the actual-app null-orientation warning, even with broad debug logging.
No ScrollBar source change or lifecycle repair is claimed. Record the exact
preceding action if the warning recurs in the new kit.

Busy-button focus is **expected Qt disable/re-enable behavior**, as established in
the preceding ownership check; this task makes no focus-restoration change. Accepted
icon, Switch, Haruna menu/selection, authentication and navigation results remain
preserved. The historical Haruna crash remains unresolved.

Evidence under `.cache/uqc207/`:

- `background-logging.log`: failing coverage/reopening baseline; the background is
  120x8 despite larger settled popup/content dimensions.
- `background-category-*.log` and `background-qt.quick.*.log`: logging-category
  isolation; `background-baseline.log` and `background-staged-baseline.log`: ordinary
  logging baseline passes without explaining the actual-app failure.
- `background-observer-baseline.log`: old observer creates the unopened popup.
- `background-focused.log`: six diagnostic/observer CTests pass, including Fusion.
- `background-installed.log`: installed-package acceptance passes.
- `background-full-provider.log`: full provider suite passes, 83/83 CTests.
- `background-static.log`: format-check and all_qmllint pass with existing warnings;
  provider/demo/gallery import policy also passes. `background-reuse.log`: REUSE
  passes after its sandbox-blocked multiprocessing socket check was rerun outside
  the sandbox. Collector tests: 8/8 pass, including logging metadata, inherited
  observer removal, process status and indexed hashes.

Actual-app background acceptance is now recorded in the manual acceptance section
below. [RENDERING-BATCH3.md](RENDERING-BATCH3.md) preserves the completed five
scale-1 runs, including the NeoChat uninstrumented comparison and Fusion reference. UQC-201/UQC-207 remain
In Progress and the initiative remains Accepted.

Provider candidate `33d1d51b2f57b1a18fc8ef42ff077b6d62bc21ce` is published on canonical
`origin/main`; `ls-remote` confirms availability before the umbrella pin update.

Fresh immutable kit: `/tmp/holonight-uqc207-qvyy2hq9` (READY).
Archive: `.cache/holonight-uqc207-qvyy2hq9/holonight-uqc207-qvyy2hq9.tar.gz`.
SHA-256: `41c806053a0ab41937a217de8e305b0d921ef6368b738d9b1712026760668bd7`.
Prepared with `prepare-rendering-kit.py --dropdown-only`; this mode stages the
published config/provider without unrelated consumer rebuilds or fractional-scale
acceptance. All 13 preparation steps pass, including staged coverage and observer
checks in both styles, collector tests, and restoration at the original prefix.
Independent post-restoration verification matches all 169 manifest hashes.

Six bounded native launches cover NeoChat, Tokodon and Haruna under both styles at
scale 1 with the viewport diagnostic trigger enabled. All staged module/origin
checks and saved log hashes pass; measured window DPR is 1 in each run. Four
processes exit -15 at the planned SIGTERM deadline, and both NeoChat processes exit
0 after the termination request. None exits prematurely or requires a forced kill.
These are loading/process observations, not interactive background acceptance.
Records: `.cache/holonight-uqc207-qvyy2hq9/results.jsonl`, `runtime/`, and
`post-restoration.json`. The subsequent manual results are recorded below.

### Batch 3 dropdown background manual acceptance — 2026-09-14

User notes: `/tmp/res.txt`, SHA-256 `624639279b689324cf7f9b5ed6b3439446361cebd4d9f2b69a62c6ad96abeb3b`;
preserved as `.cache/uqc207/background-manual-notes.txt`. Session:
`hyprland-6_c43c5q`, kit `holonight-uqc207-qvyy2hq9`. The five reported runs are
NeoChat HoloNight with diagnostics, NeoChat HoloNight without diagnostics/debug
logging, NeoChat Fusion with diagnostics, Tokodon HoloNight and Haruna HoloNight,
all at requested scale 1. The notes report verified isolation and exit 0 for each.

- **R05 background coverage: accepted for the tested paths.** The user confirms
  that dropdown backgrounds and geometry are correct and the controls work well
  in NeoChat, Tokodon and Haruna. Tokodon's exception concerns its chevron, not
  its background or geometry. Preserve this acceptance without repeating it.
- **Tokodon chevron: deferred.** The screenshot identifies the closed Color theme
  ComboBox on Appearance. The user reports intermittent disappearance and requests
  no further investigation without a concrete actionable defect. Ownership remains
  unresolved; see the detailed review and deferral below.
- **ScrollBar lifecycle: remains open.** Reviewed logs contain eight null-orientation
  warnings, including uninstrumented NeoChat. Successful exits do not close it.


The user supplied a readable copy at `/tmp/uqc207-background-evidence`. All eight
finished index records (the five reported checks plus three additional attempts)
match recomputed log hashes and exit files (exit 0). Recomputed module isolation
passes for all eight. Seven instrumented runs have measured window DPR 1, matching
the index; the uninstrumented NeoChat run has no measured DPR and is not assigned
one from its requested scale. Recorded provider ComboBox backgrounds match popup
width and height. Haruna has no popup observation, so its visual background
acceptance comes from the user's report, not inferred measurements.

**Chevron investigation:** Tokodon's two observed Appearance-page ComboBoxes are
510x32. Their provider Shape indicators settle at (490,10), size 12x12. Shape-sync
logs show the intended (2,4) → (6,8) → (10,4) path triangulated and an opaque stroke
updated to #fcfcfc. This rules out a missing object, zero size and an empty path in
those records; it does not establish visible pixels or rule out clipping, opacity,
scene-graph or driver behavior. The application uses OpenGL on Intel/Mesa.

A new reduced rendered check exercises the installed FormComboBoxDelegate in a
secondary window. It passes HoloNight and Fusion at scale 1 with Qt debug logging
on/off. It also passes HoloNight with broad logging under OpenGL/software Mesa in
a private headless Wayland compositor. The actual Intel rendering failure is not
reproduced, and no indicator source repair is claimed. The initial offscreen
OpenGL attempt could not create QRhi; the Wayland probe supplies the usable OpenGL
comparison. No desktop input/focus was automated.

**ScrollBar:** the null-orientation warning occurs eight times across five
HoloNight NeoChat/Tokodon runs, including one occurrence in uninstrumented NeoChat.
It therefore cannot be dismissed as requiring the observer or broad debug logging.
It remains a separate open lifecycle finding. Known Kirigami null-flickable errors
are also retained without claiming provider ownership.

Evidence: `.cache/uqc207/background-manual-analysis/` contains per-run summaries
and extracted popup/error records; `chevron-baseline-*.log`,
`chevron-final-{Holonight,Fusion}-{off,all}.log`, and `chevron-wayland.log` retain
rendering probe results. Added provider test/SDD only; production QML, public APIs,
published pins and immutable kits are unchanged. Focused rendered checks and
clang-format/diff checks pass. The cause remains unestablished; see the user-directed deferral below.

Accepted icon, Switch, Haruna selection and background results remain preserved.
Busy-button focus remains expected Qt behavior; the historical crash remains open.
The initiative remains Accepted and UQC-201/UQC-207 remain In Progress.

### Tokodon intermittent chevron — investigation deferred, 2026-09-14

The user supplied `/tmp/screenshot-first.png`: Tokodon Appearance → General →
Color theme → Default, with the closed ComboBox chevron absent. The screenshot
confirms the visible symptom, not its cause. The user reports repeated HoloNight
runs sometimes show the chevron and sometimes do not, with no identified trigger.
Fusion was proposed only as a diagnostic comparison; the reported defect is in
HoloNight. No Tokodon Fusion visual result is claimed.

Latest notes identify HoloNight at scale 1, kit `holonight-uqc207-qvyy2hq9`, run
`hyprland-srty6z57/tokodon-1789407284589954509`, PID 177519, reported isolation
verified and exit 0. This run's full log is not in the supplied readable evidence
and its original tux directory remains inaccessible. Its raw diagnostics have
therefore not been independently reviewed. Notes and screenshot are preserved as
`.cache/uqc207/chevron-latest-notes.txt` and `chevron-missing.png`.

**Disposition: deferred intermittent actual-app rendering symptom, ownership
unresolved.** Earlier readable logs establish correct indicator geometry, a
triangulated chevron path and an opaque stroke; the reduced rendered probes pass.
There is no sufficiently established provider defect to justify a repair. This is
not a claim that Tokodon itself is at fault. At the user's explicit request, stop
investigation here: no further comparison runs, evidence-copy requests, new kits
or speculative rendering changes. Revisit only if a concrete reproducible trigger
or independently actionable defect becomes available.

Background coverage remains accepted in NeoChat, Tokodon and Haruna. Other accepted
results and the separate ScrollBar/historical-crash dispositions remain unchanged.
Only findings/coordination records and the provider investigation SDD are updated
in this review; existing exploratory test work is retained. Screenshot inspection,
notes inspection, bounded search for the latest log and documentation diff checks
were performed. No additional product tests or source repair were needed.

### Batch 4 palette investigation and repair — 2026-09-14

UQC-208 was Ready before assignment, then In Progress, with the
[local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-208.md) and
canonical provider baseline `cae1213f8204d58d3da8e6cf6da9494a4c5e4bd9`.
The preceding chevron test/deferral checkpoint was verified, published and confirmed
on canonical main before umbrella `873ab0a` pinned it. No chevron repair is claimed.
Batch 5 stays removed; the reviewed Batch 7 scope and all prior acceptances remain.

**P01: external default-scheme activation reproduced; actual-app timeline pending.**
Versioned NeoChat and Tokodon Appearance components call their scheme manager from
`onCurrentValueChanged`, including construction-time value changes. A reduced
installed FormComboBoxDelegate fixture creates/destroys that selection lifecycle
three times without user selection. It alternates application Window between
`#0c1118` (HoloNight, resolve mask 0) and `#202326` (Breeze Dark, explicit mask
`9222809086632918911`) under both Quick styles. The observer is absent and debug
logging disabled. Its parentless FormCard emits a known `visibleChildren` diagnostic;
this is not evidence about actual-app teardown or a provider palette cause.

A second probe calls only installed KColorSchemeManager default activation under
QApplication/Fusion with the HoloNight platform theme absent and no QML loaded.
It alternates Qt's `#efefef` and Breeze Light `#eff0f1` after initialization. This
confirms the activation mechanism independently of HoloNight. In KDE 6.30,
`automaticColorSchemeId()` returns an empty default when `KDE_COLOR_SCHEME_PATH`
is populated; `activateSchemeInternal()` then clears that property and resets
QPalette. The next activation selects Breeze again and repopulates the property.
Application callbacks make page construction reach that non-idempotent operation.

Owner-specific follow-ups (documented here, **not submitted**): KDE KColorScheme
should distinguish its own last activation from a platform-provided scheme path
and make repeated Default activation idempotent. NeoChat/Tokodon should apply
schemes on deliberate activation rather than construction-time value changes;
Tokodon also persists configuration from this callback. No application patch or
provider workaround is made. Actual NeoChat General → Appearance and Tokodon
Appearance-first three-cycle timelines still require the scoped human check.

Primary source evidence:
[NeoChat ColorScheme.qml](https://github.com/KDE/neochat/blob/v26.08.0/src/settings/ColorScheme.qml),
[NeoChat scheme bridge](https://github.com/KDE/neochat/blob/v26.08.0/src/settings/colorschemer.cpp),
[Tokodon Appearance](https://github.com/KDE/tokodon/blob/v26.08.0/src/qml/Settings/AppearancePage.qml),
[Tokodon scheme bridge](https://github.com/KDE/tokodon/blob/v26.08.0/src/utils/colorschemer.cpp),
[KColorSchemeManager 6.30](https://github.com/KDE/kcolorscheme/blob/v6.30.0/src/kcolorschememanager.cpp).
Downloaded versioned files, probe source/runner and three comparison logs are
preserved in `.cache/uqc208/`; no third-party code is modified or linked into the provider.

**P02: demonstrated provider palette omission repaired; actual-app acceptance pending.**
`buildPalette()` did not assign Light. Qt's default Quick FontDialog, ColorDialog
and FileDialog use `palette.light` for their footer fills and header palette.
The installed fallback implementation fixture opens all three and measures opaque
white footers against a dark provider surface. The failed-before logs are
`light-role-before.log` (all 16 scheme cases fail) and `picker-before.log` (all
three footer assertions fail), following `regression-build.log`.

The smallest repair assigns Light to existing `surfaceRaised` in Active and
Disabled; Inactive is copied from Active. The shared builder supplies both platform
and Quick defaults. Existing application roles still resolve over defaults;
ControlPalette inheritance/update and QStyle reload paths are unchanged. No new
token, public API, dependency or blanket palette replacement is introduced.
This fixes a demonstrated cause; it does not assert that every reported picker
has this backend. Haruna source uses QtQuick.Dialogs for file/subtitle-color
pickers; Tokodon uses it for font selection. The provider supplies no native dialog
helper, and the reduced fixture confirms Qt Quick fallback objects and their
installed implementations. Actual-app backend/origin evidence remains pending.
See [Qt dialog backend selection](https://github.com/qt/qtdeclarative/blob/v6.11.2/src/quickdialogs/quickdialogs/qquickabstractdialog.cpp).

**Verification:** initial focused provider palette checks pass 4/4. After repair,
focused palette/observer checks pass 8/8, then full provider CTest passes **87/87**
(50.41 s), including installed-package acceptance. Tests cover all scheme groups,
three picker footers, dark/light/dark palette changes, translucent local overrides,
reopening and navigation/control creation without application mutation. Existing
application/window/control override, sibling isolation and appearance reload tests
remain passing. Picker teardown initially exposed known FontDialogContent/Basic
GroupBox/ScrollBar warnings when the window was destroyed during closing; settling
the close animation fixes the fixture without filtering diagnostics or changing
those components. This is not closure of the separate ScrollBar finding.

Formatting and three provider Core/style/composite qmllint targets pass; existing
QML warnings remain. Provider/demo/gallery import-policy checks pass. REUSE passes
after permitting its worker socket outside the sandbox. The initial SSH/DNS reads
also required escalation; corrected commands succeeded. Collector tests pass 10/10,
including independent empty comparison profiles, inherited observer removal,
measured DPR/origins, index/log hashes and saved process outcomes. The new opt-in
palette observer passes HoloNight/Fusion on/off checks without deferred popup
creation or changes to palette roles/resolve masks. It captures numeric color groups
0 Active, 1 Disabled, 2 Inactive, preserving ARGB and origins for existing objects.
Logs are in `.cache/uqc208/`; failed preparation attempts are retained there too.

Follow [the Batch 4 instructions](PALETTE-BATCH4.md) only after the immutable kit
handoff below. UQC-208 remains In Progress until scoped manual criteria or explicit
external dispositions are accepted. UQC-201 stays In Progress, initiative Accepted.

Provider repair `5d3f06e895be5b5a93ed07f8fe717a0fa6cc6cbb` is published and
confirmed on canonical origin/main; provider working tree is clean.

**Immutable acceptance kit:** `/tmp/holonight-uqc208-y6y4sz52`, prepared from
published provider/config sources with umbrella harness checkpoint `4dad111`.
Archive: `.cache/holonight-uqc208-y6y4sz52/holonight-uqc208-y6y4sz52.tar.gz`.
SHA-256: `504e12cc6a07d636cef13c49cf16c3fe87a617f79bcb6b68e191023af4731bf6`.
All 172 file hashes pass after restoration at the exact original prefix; READY
exists, and the original pre-restoration directory is preserved. Existing-path
restoration and wrong-user launch refusals pass. Python and terminal syntax pass.
The palette mode extends the existing preparation/restore/collector harness;
earlier released kits are unchanged.

Installed provider palette/picker and observer checks pass under both styles at
scale 1. Six bounded real-app launches and six repeated launches after restoration
verify staged HoloNight libraries, runtime-selected origins, observed palette
records and actual main-window DPR 1. Haruna/Tokodon exit -15 after the deliberate
SIGTERM deadline; NeoChat exits 0 after the request. None exits prematurely or
requires forced killing. These are startup/loading observations; Settings and
pickers were not navigated by automation. Actual-app dialog backend and visual
acceptance remain pending. Diagnostic files contain palette metadata and origins,
not user-entered text. Run evidence is indexed with exact log hashes and process
outcomes; each Batch 4 comparison starts from an independent empty profile.

Preparation results/logs, both six-process matrices and restoration/refusal checks
persist under `.cache/holonight-uqc208-y6y4sz52/`; the preparation transcript is
`.cache/uqc208/kit-preparation.log`. Restore after reboot only if the kit path is absent:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc208-y6y4sz52/holonight-uqc208-y6y4sz52.tar.gz
```

The kit's README substitutes its concrete path into [PALETTE-BATCH4.md](PALETTE-BATCH4.md).
Request only those user-operated scale-1 checks; no unrelated acceptance is reopened.

### Batch 4 manual visual acceptance — 2026-09-15

The user confirms that all nine requested runs displayed consistent colors,
including pickers, throughout the dark/light/dark checks and without diagnostics.
The only observed issue is NeoChat/Tokodon still changing colors on Appearance
navigation without deliberate scheme selection.

- **P02 visual acceptance: passed** for all nine reported runs at scale 1.
  NeoChat/Tokodon used HoloNight Dark / HoloNight Light; Haruna used HoloNight
  Cyber D / HoloNight Cyber L. No mixed dark/light picker surfaces were observed.
- **P01 persists**, consistent with the previously reproduced external activation
  mechanism. No provider navigation repair is claimed. Retain the KDE and
  application-specific follow-ups documented above.
- Haruna's scheme dropdown was too narrow to read full names, prompting the
  alternative scheme pair. This is a separate sizing observation, with ownership
  uninvestigated; it does not invalidate the dark/light palette comparison.

Session: `hyprland-jk9unwh0`, kit `holonight-uqc208-y6y4sz52`. User notes in
`/tmp/res.txt` list the nine requested runs with reported isolation verified and
exit 0. The readable session index additionally contains three Tokodon attempts:
all twelve finished entries report normal exit 0. Instrumented entries record
DPR 1; uninstrumented entries provide no measured DPR. Notes and index are
preserved in `.cache/uqc208/manual-review/`.

After the user corrected ownership recursively, all twelve raw log hashes match
the finished index entries; all twelve raw exit files match exit 0, and recomputed
runtime module isolation passes. Palette sample counts match the index. All eight
instrumented runs measure DPR 1; the four uninstrumented runs remain without a
measured DPR. These include the nine requested runs and three extra Tokodon attempts.

Actual-app observations establish:

- NeoChat and Tokodon under both styles repeatedly alternate application Window
  `#ff202326` / Light `#ff393e43` (Breeze Dark) with Window `#ff0c1118` / Light
  `#ff202b39` (provider default) before explicit selection. Explicit selection
  then produces the recorded dark/light/dark application palette sequence.
- Tokodon's font picker uses `QQuickPlatformFontDialog` and Qt's
  `quickimpl/qml/FontDialog.qml`; the observed picker instances follow the default
  palette states. Its explicit selected-scheme visual acceptance is the user's
  report, not a claim of a complete per-picker measured transition timeline.
- Haruna uses `QQuickPlatformFileDialog` / `QQuickPlatformColorDialog` with Qt's
  `quickimpl/qml/FileDialog.qml` / `ColorDialog.qml` under both styles. Both picker
  implementations record the initial provider default and Cyber D/Cyber L roles.
  Runtime-selected HoloNight/Fusion controls and declared Basic fallback origins
  coexist with these Qt-owned dialog implementations; appearance alone is not
  used to assign ownership.
- Explicit KDE-exported HoloNight schemes supply their own Light role (for example
  Dark `#ffd2dcef`, Cyber D `#ffd5dbef`), whereas the provider default supplies
  `#ff202b39`. Those explicit application palettes are preserved; do not replace
  them with provider defaults. The user accepts their appearance across all nine runs.

Session versions match the kit inventory: NeoChat/Tokodon **26.08.1-1**, Haruna
1.8.1-2, Qt base 6.11.2-3 and declarative 6.11.2-1. The earlier ownership inspection
used 26.08.0 source; the exact 26.08.1
[NeoChat callback](https://github.com/KDE/neochat/blob/v26.08.1/src/settings/ColorScheme.qml)
and [Tokodon Appearance](https://github.com/KDE/tokodon/blob/v26.08.1/src/qml/Settings/AppearancePage.qml)
files were fetched and compare byte-for-byte equal to those inspected earlier.
This resolves that version-attribution gap without changing the external disposition.

The logs retain **12** provider ScrollBar null-orientation warnings across the
HoloNight NeoChat/Tokodon runs, including uninstrumented runs, and **30** Kirigami
null-flickable warnings. Haruna has neither TypeError nor ReferenceError in its
three logs. These findings remain separate UQC-207 diagnostics; successful visual
acceptance does not close them or the historical Haruna crash.

The read-only analysis script and per-run summaries are preserved in
`.cache/uqc208/manual-review/`. Notes SHA-256:
`dc90ed83117987235c2dff87f7719c24941cbf15a82b839380c3b0342b39dc34`;
index SHA-256: `8b0a7742afa09b70aacadb761c5f60c6c32baca3970ec73de081ffdb8cc7d088`.

**UQC-208 / Batch 4: Done for scoped provider work.** P02 is accepted; P01 remains
an external defect with documented owner-specific follow-ups, not a repaired
navigation behavior. No further Batch 4 visual runs or speculative provider fixes
are requested. UQC-201 remains In Progress and the initiative Accepted. Batch 5
stays removed, Batch 7 retains its reviewed scope, and unrelated accepted results
and deferred findings remain unchanged. Only documentation and the published
provider documentation checkpoint/pin change; no product or immutable-kit mutation.
Verification for this closure: raw evidence analysis, exact-version source
comparison, local documentation links and whitespace; no product tests repeated
for documentation-only changes.

Provider documentation closure `638eec25c0934538e747b969b37ab8f63d1722de` was
published and confirmed on canonical origin/main before updating the umbrella pin.
The provider is clean; implementation remains `5d3f06e`.


### Batch 6 investigation — 2026-09-15

**Checkpoint only; no kit generated, no S01/S02/F05 acceptance.** The user stopped
kit work and requested commits plus [a next-session handoff](BATCH6-HANDOFF.md).
[Ledger](TASKS.md), [shell SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-211.md)
and [draft instructions](SHELL-BATCH6.md) retain the scope and remaining gates.

Initial umbrella `eb9b80c` and every submodule were clean. Canonical `ls-remote`
confirmed shell `fffb171`, provider `638eec2` and AI `7e25e78` before work. UQC-211
was recorded Ready → In Progress before test implementation.

**S01 — provider coordinate mismatch demonstrated; historical jitter unresolved.**
A reduced provider `LayerSurfaceHost` client, linked against the installed Batch 4
provider, was run in headless Sway with output 1920×1080 at scale 1, fixed profile,
top/left/right anchors, requested size 0×64 and exclusive zone 64. It uses a plain
Rectangle, with no shell QML, Controls or hover:

| Qt scale / measured DPR | Configure | Qt window/root | Buffer | Surface destination | Exclusive zone |
|---|---|---|---|---|---|
| 1 / 1 | 1920×64 | 1920×64 | 1920×64 | 1920×64 | 64 |
| 1.25 / 1.25 | 1920×64 | 1920×64 | 2400×80 | 2400×80 | 64 |

Provider `WaylandLayerSurfaceBackend::applyConfigureSize` copies protocol width
and height directly into Qt window dimensions. The measured surface destination
is in compositor surface coordinates, not just buffer pixels. Repeated window
samples are stable: this does not reproduce the original Hyprland jitter. The
headless Hyprland attempt exited before creating a display (`CBackend::create()
failed`). No Hyprland reproduction or shell compensation is claimed. Proposed
provider [UQC-215](UQC-215.md) stays Planned; the provider repair branch stops here.

The reduced client exits -11 during shutdown. Explicitly closing its host before
quitting removes the first attempt's surface/role-order protocol error, but the
later crash persists with context destruction after Qt display teardown. This is
retained as a probe limitation, not a proved lifecycle diagnosis or acceptance
pass. No teardown repair was attempted. Sources, runner and protocol logs are in
`.cache/uqc211/host-probe.cpp`, `run-sway-probe.py`, `host-1.log` and `host-1.25.log`;
the failed Hyprland startup log is `hyprland.log` in that directory.

**S02 — no demonstrated shell rendering defect in focused fixtures.** Compiled
HoloNight/Fusion checks at Qt scales 1/1.25 verify stable in-bounds sections,
resting status fills matching the isolated frame, complete right-edge coverage,
and active feedback returning to transparency. Whole-bar and isolated-section
inspection used fixed fake services. No product artwork, overlap, geometry or
popup behavior was changed. This is not real-compositor/manual acceptance.

Initial QtTest `grabImage()` captures were cropped in logical coordinates at DPR
1.25. The test harness now reuses its existing image wrapper with physical-pixel
window crops, and feedback assertions sample a border strip. The final six focused
CTest entries (four compiled comparisons plus both source suites) pass. The shell
also gains the missing popup/tray metadata in its service fakes; fixture-specific
undefined-property diagnostics are resolved.

**Verification:** underlying full shell CMake build succeeds. The isolated full
1171-entry suite passed 1164, failed six NetworkManager cases on service-name
registration, and skipped one portal case. All nine related NetworkManager/portal
entries pass serially, resolving those shared-bus parallel-run failures. Four new
compiled composition entries were then registered, and all six final focused
entries pass. Formatting, QML lint/types, import policy, architecture and REUSE
pass, with existing QML lint warnings. The task wrapper's existing provider
`68b7069` guard blocks `task test`/task formatting; individual dependency and
underlying CMake/check commands used requested provider `638eec2` without changing
pins or dependencies. The first unrestricted-environment/sandbox test attempt
also hit socket restrictions and host import contamination; the private wrapper
resolved those. Logs remain under `.cache/uqc211/`.

**F05 — ownership and reproduction pending.** Draft opt-in observation records
navigation receipt, queued focus metadata, actual DPR, and Wayland keyboard
enter/leave/Tab callbacks. It does not read event text, synthesize input or restore
focus. Eight offscreen observer on/off cases pass for forwarding, measured DPR,
unchanged fixture acceptance behavior, and exclusion of a text sentinel. These
are observer fixtures, not actual AI style/form/VT acceptance. The twelve collector
tests pass, including mocked normal/interrupted/forced outcomes, independent
profiles, inherited-observer removal and hashes. Actual-process interruption and
forced cleanup in a released Batch 6 kit remain unverified.

Qt's protected `QGuiApplication::notify` symbol did not support the attempted
interposition. The implemented event filter observes pre-dispatch acceptance and
queued post-dispatch focus only; **final event acceptance is unavailable** and
explicitly labelled as such. Wayland callback coverage, compositor/session
correlation, and observer-enabled versus uninstrumented real VT behavior remain
to verify. Do not infer missing compositor delivery from missing observer records
or classify delivered-but-unhandled navigation from queued focus alone. AI and
provider product code were not modified.

Shell local commits: `954a721410804b429f43b0cd65df5dc252a387a1` and
`ab780d5d477400cdc70195d37783e9e080ee1d05`. The push request was interrupted;
publication is unconfirmed and local origin/main still reports `fffb171`. The
umbrella pin stays at the published baseline. The shell working tree is clean.
Draft preparation/restore/verification scripts are committed for continuation,
but **no Batch 6 staged installation, immutable kit, archive, restoration or live
manual run was performed**. Do not treat draft instructions as a released kit.

UQC-211 and F05 remain open; UQC-201 stays In Progress and the initiative Accepted.
Batch 4/P02 acceptance, external P01, removed Batch 5, reviewed Batch 7 and deferred
Batch 3 findings remain unchanged.


### Batch 6 verified investigation kit — 2026-09-15

Resumed from umbrella `a34d9db`. Canonical shell main was still `fffb171`;
published preserved test/SDD commits `954a721` and `ab780d5`, confirmed canonical
`ab780d5d477400cdc70195d37783e9e080ee1d05`, and checkpointed its gitlink in
`8b7b9a3`. No product repair was made. The proposed provider coordinate package
is now [UQC-215](UQC-215.md), correcting its collision with completed F06 UQC-213.
Historical shell SDD references to the proposed package retain the old number.

Fresh immutable kit: `/tmp/holonight-uqc211-hhs633yu`.
Archive: `.cache/holonight-uqc211-hhs633yu/holonight-uqc211-hhs633yu.tar.gz`.
SHA-256: `1f15cf407c35644102c45f94731bf70177f8a0307c6b35b67471f051dbb0123b`.
Exact sources are in `revisions.json`; all five source repositories were clean
and matched canonical main at preparation. Gitlinks remain authoritative.

Preparation:

```sh
python3 docs/initiatives/unified-qtquick-controls/prepare-rendering-kit.py --batch6
python3 docs/initiatives/unified-qtquick-controls/prepare-rendering-kit.py --batch6 --resume /tmp/holonight-uqc211-hhs633yu
```

The first sandbox attempt failed at SSH configuration access before building;
the permitted resume passed all 40 preparation commands. Logs, commands/results,
harness snapshots and runtime records remain in `.cache/holonight-uqc211-hhs633yu/`.
No earlier released kit was modified.

- Built/installed provider dependencies, AI and shell at the candidate prefix.
  All 16 provider/AI/shell/compiled-topbar acceptance invocations pass across
  HoloNight/Fusion and Qt scales 1/1.25 with host HoloNight modules/libraries masked.
- All 16 actual shell/AI headless Sway startup comparisons pass runtime mapping
  isolation, covering both styles/scales with observation on/off. All were stopped
  deliberately with SIGTERM and returned -15; no forced cleanup or shutdown crash.
  Observed window DPR matches each requested scale. Unobserved runs emit no session
  observations. These are bounded startup checks, not normal user-close acceptance.
- The runtime verifier now rejects unexpected shutdown codes and retains each
  attempt separately. The observer records listener-installation success explicitly.
  Eight offscreen observer on/off cases pass navigation forwarding, unchanged
  fixture acceptance, measured DPR and exclusion of entered text.
- All 13 collector tests pass. New disposable real-child cases cover normal exit,
  abort, interrupted termination and forced cleanup with completed/hash-verified
  indexes. These exercise process supervision, not manual AI/shell close behavior.
- Exact-path archive restoration and all 225 file hashes pass. Four actual refusal
  checks pass: wrong user for session/app, preparing over READY, and restoring over
  an existing kit. Python/shell syntax, relative documentation links and whitespace
  checks pass. No full product suite was rerun beyond the recorded installed checks.

**Observation limits:** headless Sway produced window/focus/geometry records but
no keyboard-listener records. Actual Wayland listener and Tab callback coverage
remains unverified; missing navigation records cannot prove missing compositor
delivery. Final Qt event acceptance remains explicitly unavailable. User-operated
VT return, form navigation and observer-off comparisons remain necessary for F05.
No input, focus or VT interaction was automated. Private AI profiles retain disabled
providers; no credentials or model requests were used.

From a fresh real tux VT login:

```sh
python3 /tmp/holonight-uqc211-hhs633yu/guided-session.py hyprland
```

Follow the kit README's [focused checklist](SHELL-BATCH6.md). If reboot removed
the kit, restore only when its original path is absent:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc211-hhs633yu/holonight-uqc211-hhs633yu.tar.gz
```

S01/S02/F05 and UQC-211/UQC-201 remain open. UQC-215 stays Planned and initiative
status Accepted. Preserve accepted batches, the removed Batch 5, reviewed Batch 7
scope and deferred Batch 3 findings. This kit prepares the focused human sequence;
it does not establish manual acceptance or final integration.


### Batch 6 shell manual results — 2026-09-15

User notes: `/tmp/res.txt`. Copied raw session: `/tmp/hyprland-adyjrxc6`.
Selected evidence and independently checked summaries persist under
`.cache/uqc211-manual/hyprland-adyjrxc6/`; profile data and cookies were excluded.
The session is a real active local tux login on tty3, running Hyprland with the
released `hhs633yu` kit. Recorded package versions match the kit inventory.

| Run suffix | Style / Qt scale | Observer | User result |
|---|---|---|---|
| `1789458964731044325` | HoloNight / 1 | On | No issues observed. |
| `1789459155885339201` | Fusion / 1 | On | No issues observed. |
| `1789459330961040129` | HoloNight / 1.25 | On | Jitter/jumping, apparent height changes around tooltip interactions, right-side overflow and displaced click regions; popups could not be reliably opened. |
| `1789466878712474502` | HoloNight / 1.25 | Off | Same failure; observation removal does not improve it. |
| `1789467128652116817` | Fusion / 1.25 | On | Same failure. |
| `1789467182313919431` | Fusion / 1.25 | Off | Same failure. |

All six final index records have matching launch/session hashes, PID evidence,
independently rechecked staged mappings, and matching saved exit codes. All exits
are -2 (SIGINT), recorded as interrupted and consistent with deliberate Ctrl+C.
They are not crashes or normal application closes. Unobserved runs have no
session-observer records. Four observed runs verify actual DPR 1 or 1.25 and
successful Wayland keyboard-listener installation. Scale-1 runs also contain
keyboard enter/leave callbacks; this proves those callbacks in these shell runs,
not AI Tab delivery or final Qt event acceptance.

The observed topbar Qt window/root stays 2560×64 at both DPRs; it does not show
sampled root-height oscillation. Active-window section widths do change, including
in passing scale-1 runs, so width changes alone do not establish the reported
failure mechanism. Manual fractional-scale jitter/overflow/hit mismatch is now
reproduced on real Hyprland with both styles and with/without observation. The
prior provider coordinate mismatch remains a concrete lead for UQC-215; these
logs do not independently prove the complete configure/buffer/input-region cause.
No shell compensation or speculative rendering repair is justified by this review.

S01 fails fractional-scale acceptance. Preserve both passing Hyprland scale-1
observations for S02; the requested scale-1 Sway frame comparison has not been
reported here. UQC-211/UQC-201 remain In Progress and initiative Accepted.

**AI/F05 evidence is pending:** the notes list two observed AI scale-1.25 runs
under `sway-wgdjbln0` (`1789467311521572433`, `1789467780332669788`) and report no
issues, both interrupted with Ctrl+C. That session has not been copied to `/tmp`;
its hashes, actual compositor, navigation/VT sequence and runtime evidence have
not been verified. The requested F05 sequence was Hyprland, with both observed
and unobserved comparisons. Do not close F05 from general no-issue observations.
The exact form/control and VT sequence need clarification.

The reported Ctrl+Q behavior is not evidence of an application defect: the kit's
Hyprland window-close binding is **Super+Q**, and its Sway configuration defines
no window-close binding. Ctrl+Q is application-specific, not a session-wide close
shortcut. The recorded Ctrl+C exits remain valid deliberate interruptions.


### Batch 6 Sway AI evidence review — 2026-09-15

The user clarified that Sway was accidental: the scale-1 Sway shell checks were
skipped and AI was tested there instead. The user confirms navigation worked
before and after the VT round trip with no issues. This is a passing observed
Sway comparison, not the requested Hyprland F05 acceptance.

Copied session `/tmp/sway-wgdjbln0` is verified as a real tux Sway session on tty3.
Selected evidence and verification summaries are preserved under
`.cache/uqc211-manual/sway-wgdjbln0/`, excluding profile data/cookies. Both indexed
AI runs match launch/session hashes, independently rechecked staged mappings,
recorded package versions and deliberate Ctrl+C exits (-2, interrupted).
Actual chat/settings window DPR is 1.25 in both styles.

| Run suffix | Style | Wayland Tab callbacks before / after VT return | Qt navigation |
|---|---|---|---|
| `1789467311521572433` | HoloNight | 20 / 60 | Tab and Backtab recorded before and after. |
| `1789467780332669788` | Fusion | 30 / 18 | Tab and Backtab recorded before and after. |

Counts include press/release callbacks, not distinct physical keystrokes. Each
session poll records Active yes → no → yes on VT3. Both runs record successful
Wayland keyboard-listener installation at startup and again after return, plus
enter/leave callbacks. This resolves the prior actual-AI listener/Tab-observation
gap for these runs. Final Qt event acceptance remains unavailable; passing
interaction comes from the user's observation, corroborated by delivery/focus
records. Focus origins include the selected style's SpinBox and the Ollama form;
the exact starting numeric field and destination VT are not independently
established by these metadata and are not inferred.

No repeat of these observed Sway AI runs is needed. Remaining planned manual
coverage is two scale-1 Sway shell comparisons and the Hyprland AI F05 sequence
at Qt scale 1.25 in both styles, with and without observation. Preserve the six
already reviewed Hyprland shell outcomes. S01/UQC-211 and F05/UQC-201 remain open;
initiative status remains Accepted. No product changes or product tests accompany
this evidence review; hashes, mappings, session/navigation correlation, links
and whitespace were checked.


### Batch 6 Sway shell acceptance and Hyprland AI failure — 2026-09-15

Latest user notes `/tmp/res.txt` accompany copied sessions `/tmp/sway-mwtwu9yx`
and `/tmp/hyprland-j_eu8uj6`. Selected evidence and verification summaries persist
under `.cache/uqc211-manual/` in matching directories. All four final records have
verified launch/session hashes, independently checked staged mappings, matching
exit files, expected measured DPR and package versions matching the released kit.
Both sessions are real tux logins on tty3 with their declared compositors.

**S02 scale-1 comparison passes.** Sway shell runs `1789468962405320633` (HoloNight)
and `1789469048777333728` (Fusion) both work as expected with no issues reported.
Actual DPR is 1; both exit -2 on deliberate Ctrl+C. Combined with the accepted
Hyprland scale-1 observations, this completes the requested scale-1 frame check.
No S02 product repair is demonstrated or required for this reported comparison.
S01 fractional jitter/overflow remains a separate failing gate; UQC-211 stays open.

**F05 reproduces under observed Hyprland in both styles.** Both AI runs use actual
DPR 1.25 and exit normally with code 0:

- HoloNight `1789469179039733593`: Tab/Backtab works initially. After VT3 → VT1 →
  VT3, the settings window appears focused but its internal focus disappears and
  navigation has no visible effect. Clicking Context window's numeric editor
  restores visible traversal.
- Fusion `1789469397554349022`: after return, the focus ring appears unchanged
  and the text cursor stops blinking. Tab/Backtab has no visible effect until a
  small pointer movement over empty space makes the ring appear on another
  control. The user suspects traversal continued without visual updates; this
  remains an observation/hypothesis, not a measured rendering diagnosis.

**Correlated evidence:** HoloNight records one inactive/active VT cycle; Fusion
records three. On return, Hyprland's active-window metadata retains the settings
window and AI PID. Wayland keyboard listeners reinstall successfully and receive
enter and Tab callbacks. Qt records the settings window as `active:false`, with
application focusWindow/activeFocusItem null. Nevertheless, Qt key events reach
the settings window and its per-window activeFocusItem subsequently changes among
text inputs, sliders, switches and buttons. After the first return there are 78
HoloNight and 156 Fusion Wayland Tab press/release callbacks. The corresponding
Qt event counts include propagation through multiple receivers and are not
physical-keystroke counts.

This demonstrates disagreement between compositor active-window metadata and
Qt activation, with navigation delivery still occurring. It does not prove a
pure redraw defect, final event acceptance, or that every focus change preceded
the reported click/pointer recovery: pointer actions were not timestamped by this
observer. Do not infer that all Tab events were lost or unhandled, and do not
force focus as a speculative repair. AI/provider/Qt/compositor ownership still
requires investigation at the demonstrated activation boundary.

The two requested **uninstrumented Hyprland AI comparisons are not present** in
the notes/index. Run only those remaining comparisons, preserving the same
Context window numeric editor and VT3 → VT1 → VT3 sequence. No shell or observed
AI repetition is requested. Preserve the passing observed Sway AI comparisons.
F05 and UQC-201 remain open; initiative Accepted. This review changes evidence
and checklist documentation only; hashes/mappings/session correlation, links and
whitespace are checked, with no product tests repeated.


### Batch 6 uninstrumented confirmation and manual sequence complete — 2026-09-15

User notes `/tmp/res.txt` and copied session `/tmp/hyprland-fnpkrlmc` complete the
requested observer-off comparisons. Selected raw evidence and verification
summaries persist in `.cache/uqc211-manual/hyprland-fnpkrlmc/`, excluding profiles
and cookies. The session is verified as real tux Hyprland on tty3 using the
released kit; recorded package versions match its inventory.

| Run suffix | Style / requested Qt scale | User result | Exit |
|---|---|---|---|
| `1789470643682165773` | HoloNight / 1.25 | Same failure after VT return; clicking is required to restore focus behavior. | 0, normal |
| `1789470750460305585` | Fusion / 1.25 | Same failure after VT return; pointer movement is required to restore visible focus behavior. | 0, normal |

Both final records match launch/session hashes and saved exit codes. PID evidence
independently verifies staged mappings, selected styles and configured Qt scale
1.25. LD_PRELOAD and session-observer flags are absent, and no HN_SESSION records
appear. The session poll records inactive/active transitions in both runs. Actual
DPR is unavailable in these uninstrumented runs and is not inferred from the
scale setting; the earlier observed comparisons measured 1.25.

F05 therefore reproduces under Hyprland in both styles with and without the
observer. Observation is not required to trigger the reported behavior. Preserve
the earlier observed evidence of compositor/Qt activation disagreement and
continuing navigation delivery. The uninstrumented logs do not independently
measure focus or rendering state, so the precise repair owner remains unresolved.
Passing observed Sway results remain a separate compositor comparison.

**The planned Batch 6 manual sequence is complete. No repeat runs are requested.**
S02's scale-1 frame comparison is accepted on both compositors. S01 fractional
shell geometry and F05 VT-return behavior remain failures requiring bounded
ownership investigation and repair, not further repetition of this kit sequence.
UQC-215 remains the Planned provider coordinate package; F05 remains an umbrella
ownership gate until the AI/provider/Qt/compositor boundary is established. Do
not compensate for either issue by speculative shell geometry or forced focus.
UQC-211/UQC-201 remain In Progress and the initiative Accepted, not Integrated.

Verification for this documentation review: hashes, mappings, observer absence,
exit codes, package versions and VT session transitions pass; relative links and
whitespace pass. No product implementation changed or product tests were repeated.


### S01 provider repair and F05 reduced diagnosis — 2026-09-15

The completed manual sequence was checkpointed as umbrella `cf0cc80`. Canonical
baselines were revalidated unchanged before assignment: provider `638eec2`,
shell `ab780d5`, AI `7e25e78`. UQC-215's provider-local coordinate contract was
marked Ready before implementation. The [provider SDD](../../../holonight-qt/docs/sdd/layer-surface-logical-coordinates/SPEC.md)
and [verification](../../../holonight-qt/docs/sdd/layer-surface-logical-coordinates/TASKS.md)
record the repair and caller audit.

**Provider repair is published and locally verified.** Commit
`0e0f92efe1517bc07c577299f07b51117f25f05a` was confirmed on canonical main before
umbrella checkpoint `0ee4ef5` updated its pin. All public geometry stays in Qt
logical coordinates; Qt boundary conversion now handles initial/later size,
configure, margins, zones and custom input regions. Anchored zeros and zone
sentinels retain their meaning. Scale refresh uses logical originals. No shell
compensation, consumer source edit, public signature change or system install.

The regression failed before repair at Qt 1.25 with output scale 1 and 2; Qt 1
passed both. The repaired four-case matrix passes, including zero-width bar,
zero-height panel, repeated configure, rounded input boundaries, deterministic
scale refresh/reversal and orderly reopen/teardown. Provider CTest **87/87**,
shell hosting **164/164**, AI panel **11/11**, installed package checks, formatting,
QML policy, syntax, whitespace and licensing pass. Clang-tidy completes with
existing code/header warnings. Raw logs are retained in `.cache/uqc215/`.
The reduced probe orders application/context/window teardown explicitly; the
ordinary stack-application context teardown defect is separately documented,
not repaired or hidden by accepting a crash.

**Fresh immutable repair kit:** `/tmp/holonight-uqc211-8ptiz_ko`.

- Archive: `.cache/holonight-uqc211-8ptiz_ko/holonight-uqc211-8ptiz_ko.tar.gz`.
- SHA-256: `041ff28e0f4f241bcd79450ef3260d09b6f4f45b6893f8e7e7d11d7f1894211f`.
- All **230 file hashes** pass after exact-path restoration. Restoring over the
  existing released kit is refused (exit 2). The prior `hhs633yu` kit is preserved;
  all its **225 hashes** still pass.
- **40 preparation commands** pass, including **16 installed comparisons**
  (provider, AI controls, shell controls/composition × two styles/two Qt scales),
  **16 isolated staged process comparisons**, **8 observer checks**, **13 collector
  tests**, terminal syntax and restoration. Actual staged mappings are verified
  with host provider modules hidden. All 16 bounded runtime processes end by the
  requested SIGTERM (-15), classified **terminated**, with no forced cleanup or
  shutdown crash; these are not normal-close acceptance results.
- Independent staged-shell geometry review verifies all four observed cases:
  TopBar stays **1920×64** Qt units at scale 1 and **1536×64** at 1.25 on the
  1920-wide native output. The latter sends Wayland height/exclusive zone **80**.
  Evidence: `.cache/uqc215/installed-shell-geometry.json` and kit runtime logs.
  This does not establish human hover, click or popup acceptance.
- The new `--s01-repair` preparation mode selects the repair-only guide and stages
  reduced F05 sources. The in-flight candidate received those source files
  before hashing; released kit contents were not edited afterward. Detailed
  logs/results are under `.cache/holonight-uqc211-8ptiz_ko/`.

**F05 remains an ownership diagnosis.** [The reduced fixture and source analysis](f05/README.md)
identify Qt's keyboard-destruction/cached-focus path as consistent with the
retained Hyprland/Sway difference. No HoloNight repair owner is demonstrated.
The exact capability/enter/toplevel/Qt-cache sequence and its presentation effect
remain unresolved. Plain Qt, plain Qt with staged platform theme, and
HnApplicationWindow all pass headless fixture verification under Fusion at DPR
1.25; actual mappings prove the plain run loads no HoloNight libraries. Navigation
forwarding/acceptance and text exclusion pass. These results validate the
reproducer, not real VT behavior or new-observer physical keyboard forwarding.
Final installed-kit evidence is preserved at
`.cache/uqc215/f05-kit-evidence/`. The kit includes sources for a user-operated
**plain-Qt reduced VT check first**, without repeating the completed AI matrix.
No forced focus, synthetic pointer, repaint workaround or external patch.

**Remaining gates:** follow only [S01 repair acceptance](S01-REPAIR.md) for the
fractional Hyprland shell. S02's passing scale-1 comparison stays accepted.
S01/F05 and UQC-211/UQC-201 remain open; UQC-215 is Done locally. Initiative remains
Accepted, not Integrated. Batch 7, deferred Batch 3 issues and final integration
were not reopened.


### S01 repair accepted on Hyprland — 2026-09-15

User results `/tmp/res.txt` report **no issues** for both requested fractional
repair checks in session `/tmp/hyprland-6p_j_ox6`. This completes the
[S01 checklist](S01-REPAIR.md): startup/bar stability, hover/tooltips, right-edge
bounds, popup placement, click alignment and reserved space. These interaction
results come from the user's manual review; logs corroborate identity and
geometry rather than independently measuring every interaction.

| Run | Style | Measured DPR | Topbar Qt geometry | Outcome |
|---|---|---|---|---|
| `1789483471242990444` | HoloNight | 1.25 | 2048×64 | No issues; deliberate Ctrl+C (-2). |
| `1789483615617702032` | Fusion | 1.25 | 2048×64 | No issues; deliberate Ctrl+C (-2). |

Both final records match independently recomputed launch/session hashes and
saved exits. Rechecked PID mappings use the released `8ptiz_ko` kit's staged
provider; style selection and actual DPR are verified. Recorded package versions
match the kit. Identity and launch records establish a real local tux session
on tty3 running Hyprland. All sampled TopBar roots retain the geometry above.
SIGINT exits are intentional interruptions, not crashes or normal-close tests.
Selected evidence and verification summaries are preserved under
`.cache/uqc211-manual/hyprland-6p_j_ox6/`; profiles and cookies were excluded.

**S01 is accepted and UQC-211 is Done.** S02's accepted scale-1 comparison remains
valid; no shell repetition is requested. Provider UQC-215 remains Done, with
published repair `0e0f92e` and unchanged shell pin `ab780d5`. No product code or
submodule pins changed during this review. Hashes, mappings, package versions,
geometry, outcomes, documentation links and whitespace were checked; product
tests were not repeated for documentation-only acceptance.

No reduced F05 evidence was supplied. F05/UQC-201 remain open pending the
[plain-Qt reduced VT check](f05/README.md). The initiative remains Accepted,
not Integrated; no unrelated batches or final integration were reopened.

### F05 activation diagnosis setup — 2026-09-15

**Unresolved; plain-Qt real-keyboard evidence is pending.** This iteration starts
at umbrella `f2fae57` with a clean working tree and all twelve submodule checkouts
matching their pins. The umbrella is four commits ahead of its local tracking
reference; this read-only inspection does not reconfirm remote publication.
No product sources or gitlinks changed.

The released `/tmp/holonight-uqc211-8ptiz_ko` exists: all **230 file hashes** pass,
and its retained archive SHA-256 still equals
`041ff28e0f4f241bcd79450ef3260d09b6f4f45b6893f8e7e7d11d7f1894211f`.
All ten `PROVIDER.txt` package entries match the installed versions, including
Qt base `6.11.2-3`, Qt declarative `6.11.2-2`, Hyprland `0.56.2-3` and Sway
`1:1.12-4`. Restoration was unnecessary; the released kit is unchanged.

All three reduced sources are byte-identical to the released copies. Retained
`.cache/uqc215/f05-kit-evidence/` results were rechecked: Fusion mappings, both
windows at actual DPR 1.25 and exit 0 in all three modes; plain has no HoloNight
library mappings, and theme/hn mappings use the released prefix. Existing
navigation forwarding/acceptance and text-exclusion verification is reused.
No diagnostic source or dependency change required another `f05/run.py --verify`.
These are headless fixture results, not evidence of real VT behavior.

Persistent setup audit: `.cache/uqc-f05-activation/setup-audit.json`, SHA-256
`1f7f4fe8e90bb2b88c210f0f5860313e853d4693d6a0601da8c14f31029ca25a`.
It records pins, all kit file hashes, package comparisons, source identity and
retained per-variant evidence hashes.

**Bounded next experiment:** one user-operated plain/Fusion run in isolated
Hyprland, Qt scale 1.25/output scale 1, numeric editor and Tab/Backtab before and
after VT3 → VT1 → VT3, tested before pointer movement. The
[checklist](f05/README.md#one-focused-manual-check-when-ready) includes session and
output capture. Required missing evidence is the user's observation plus actual
keyboard callbacks, capability/enter/leave/toplevel records, Qt focus/navigation,
frame-swap counts, mappings, session/package identity and exit outcome.

An external reproduction boundary cannot yet be assigned. No upstream report is
ready and no HoloNight repair owner is demonstrated; the Qt private-cache path
remains a hypothesis. Frame-swap signals cannot establish physical presentation,
and observer events cannot establish final key acceptance. Only a passing plain
run calls for theme/hn comparisons. S01/S02 and completed AI comparisons are
preserved; UQC-201 remains In Progress, initiative Accepted. Batch 7, remaining
Batch 3 diagnostics and final integration remain outside this iteration.

### F05 plain-Qt external reproduction — 2026-09-15

**Supported disposition: external Qt/Hyprland compatibility defect.** The reduced
plain Qt fixture reproduces without HoloNight libraries. This resolves the
HoloNight ownership gate for this iteration; it does not prove the precise Qt
cache mechanism or repair F05. The [upstream-report draft](f05/UPSTREAM-REPORT.md)
is prepared and **not submitted**. No HoloNight repair package is warranted by
this evidence.

User transcript `/tmp/res.txt` identifies `/tmp/f05-reduced-6q2p2_fg`, plain mode,
and normal completion. The user subsequently confirms Tab/Shift+Tab worked before
VT3 → VT1 → VT3, stopped visibly updating focus after return before any pointer
movement/click, and recovered after a later click. These are manual observations;
pointer actions are not recorded by the observer.

Session copy `/tmp/hyprland-3evu_xyg` establishes a real local tux seat0/tty3 login
and the released kit's isolated Hyprland configuration. Session packages match
the kit: Qt base `6.11.2-3`, declarative `6.11.2-2`, Hyprland `0.56.2-3`.
The monitor capture is 2560×1600 at output scale **1**. Both fixture windows report
actual DPR **1.25**. Independently inspected PID `194332` mappings contain Fusion,
Qt Wayland and xdg-shell, with **no HoloNight library/QML mappings**. Compositor
log records that fixture PID's session-bus request, corroborating the session
association. Saved `outcome.json` records plain mode and **exit 0**.

The new observer's real-keyboard coverage is established: successful listener
installation, keyboard enter, physical Tab callbacks and corresponding Qt
Tab/Backtab events occur before and after capability loss.

| Time (epoch ms) | Correlated evidence |
|---|---|
| Before `1789490119935` | Tab/Backtab reach the settings window and item receivers, focus items change, and frame counters advance. The settings toplevel's last configure is activated. |
| `1789490119935` | Seat loses keyboard capability. No settings keyboard-leave precedes it; the run's only leave was the earlier workspace-to-settings transition. |
| `1789490119999` | Application focus null/state 2; settings inactive, focus item null, frame counter 60. |
| `1789490127582`–`1789490127583` | Keyboard capability returns, replacement listener installs with reused protocol ID 28, and enter targets the same surface 55. |
| `1789490153538`, `1789490154228`, `1789490159118`–`1789490159119` | Two Tab presses and one Backtab reach Wayland callbacks and the Qt settings-window observer. No item receiver is logged for these presses. |
| Through `1789490170199` | Settings frame counter stays 60; Qt application focus and settings focus item remain null. |
| `1789490170299`–`1789490171499` | Settings frame signals resume and reach 70; an item focus appears at `1789490171399`. Application focus remains null/settings inactive in the final samples. |

No xdg-toplevel configure or keyboard-leave occurs at/after capability loss.
Protocol and Qt IDs have no direct native join in this observer; settings
association uses lifecycle order, dimensions and navigation delivery. The user's
click-recovery report is retained even though the final Qt application samples
remain inactive; there is no recorded post-click navigation sequence establishing
its internal routing. FrameSwapped counts are Qt signals, not physical scanout,
and event-filter observations do not establish final key-event acceptance.

Selected raw files, user confirmation and independent analysis persist in
`.cache/uqc-f05-activation/hyprland-3evu_xyg/`, excluding profiles and cookies.
Its `SHA256SUMS` manifest hash is
`8df5761f3171476cb780290c555fb55430bdf8732d9f00a3577b1c3834bdf94a`.
The report links a [sanitized 196-record trace](f05/evidence/plain-vt-trace.jsonl)
(SHA-256 `ece59a81b739aa6fd4e0f2c0231be284ed353b09b2326bbc3afc9a672938cf5c`):
relative timestamps, aliased Qt addresses, no local paths or entered text, and
unchanged protocol IDs. Repeated identical Qt samples are omitted.

**Bounded follow-up:** upstream Qt Wayland triage can instrument the private
keyboard-focus cache across capability loss/same-surface enter and compare normal
leave/enter. An uninstrumented reduced run would separately confirm observer
independence for this exact fixture; the completed AI observer-off matrix remains
valid. Neither experiment is required to repeat now or claimed completed.
Theme/hn variants are unnecessary because plain already fails. No source changes,
external patches, installation, public API changes or focus/repaint workaround.

Verification: raw/retained hashes, source identity, session/package association,
Fusion and provider isolation, actual DPR, callback/focus/frame correlation,
normal exit, sanitized trace derivation, documentation links and whitespace.
Diagnostic sources and dependencies are unchanged, so retained runner/observer
verification is reused and product suites are not repeated. S01/S02 and completed
AI comparisons remain accepted; UQC-211/UQC-215 Done, UQC-201 In Progress,
initiative Accepted. F05's upstream repair and final integration remain open;
Batch 7 and remaining Batch 3 diagnostics stay outside this iteration.

### Batch 7 greeter implementation and verification — 2026-09-15

UQC-212 local work is **Done**; G01–G06 human acceptance is **pending**. Canonical
clean greeter handoff `abb1ecc86bec382b3cb21b238844e5a5d3207443` includes implementation
`9cd5501` and its publication record. Provider `0e0f92e` and configuration `fe69a59`
remain unchanged. F05 documentation was checkpointed separately as `e264286`.
The [local SDD](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-212.md)
records requirements, failing regressions, source decisions and verification.

Production-QML/fake-service reproduction confirms password Backtab skips the
account selector and auto-repeat Space release remasks while the key remains
held. Basic hold/release and focus-loss behavior passed before the repair; this
does not establish the exact cause of the original physical-keyboard report.
The local fixes add the complete availability-aware bidirectional cycle and an
explicit reveal hold lifecycle. The 132-pixel portrait is retained; account popup
rows compose HnAvatar and runtime ItemDelegate inside HnIconComboBox. Footer colors
are semantic and disabled feedback suppressed. Enabled idle power backgrounds
are transparent; only the poweroff glyph grows by 25%.

The inherited password palette is verified rather than overridden. Under isolated
runtime palettes, HoloNight renders enabled #131a24/#e7edf5 background/text and
Fusion white/black; focus preserves the fill. Disabled states retain selected-style
appearance. These are fixture palette observations, not a claim about all platform
themes. Real Sway visual acceptance remains necessary.

Verification: 8/8 CTest entries pass (43 core tests per style, 18 runtime tests per
style/DPR process and import-policy checks), format/QML lint, generated types,
15-unit clang-tidy, REUSE 81/81 and whitespace. Eight build and eight relocated
installed launches verify selected QML/plugin origins, no build discovery after
relocation, and deliberately terminated/reaped outcomes. Baseline/verification
logs persist in `.cache/uqc212/`. The initial fake-socket and REUSE multiprocessing
failures were sandbox restrictions; unrestricted runs pass. An initial Fusion
render capture preceded layout completion; waiting for geometry fixes the test.

No physical keyboard, desktop pointer or window focus automation was used; test
input targets only disposable offscreen windows with fake services. Follow the
[four Sway demo checks](GREETER-BATCH7.md) after the fresh kit is released. Preserve
accepted dropdown/hover results and F05's external disposition. UQC-201 remains
In Progress, initiative Accepted, and Batch 7 stays open until manual acceptance.


Released immutable kit: `/tmp/holonight-uqc212-nq09g2v1`; [manual handoff](BATCH7-HANDOFF.md).
Archive `.cache/holonight-uqc212-nq09g2v1/holonight-uqc212-nq09g2v1.tar.gz`,
SHA-256 `a2235caa325c1de8366c86a1b05e3c568c55df2938bfe99b4ff734a4762ef44b`.
All **187 restored file hashes** pass; exact-prefix restoration preserves the
original directory, and restoration refuses an existing path. The five recorded
Qt/compositor/auth-agent package versions still match. Canonical sources were
reconfirmed during preparation and are recorded in `revisions.json`.

The staged production-QML matrix passes 4/4 with host HoloNight modules/libraries
masked. Eight installed launch cases pass at scales 1/1.25. Four independently
observed installed demo processes verify staged module origins (including runtime
TextField/Button/ComboBox), required configuration/Core/Controls mappings, selected
style and **actual DPR 1/1.25**, plus deliberate termination/reaping. No real service
or desktop input is automated. Existing guided collector tests pass 13/13; Python
syntax, terminal syntax, documentation links and whitespace pass. Preparation
commands, runtime mapping/DPR/outcome records, restoration and final audit are
retained in `.cache/holonight-uqc212-nq09g2v1/`. Initial sandbox SSH refusal was
resolved by permitted preparation outside the sandbox; all installation writes
were confined to the kit/cache. No prior released kit was modified.

Manual G01–G06 observations have not yet been supplied. Only those four Sway demo
runs can close this Batch 7 acceptance gate; no integration acceptance is inferred.


### Batch 7 manual acceptance — 2026-09-15

**G01–G06 accepted; Batch 7 closed for its scoped checks.** The user reports all
six checks pass in each of the four requested Sway runs. UQC-212 remains Done,
UQC-201 In Progress and the initiative Accepted. No further Batch 7 repeats are
requested. The separately reported empty-password caret issue is tracked as G07
below and is not claimed repaired by this acceptance.

Evidence supplied in `/tmp/res.txt` and `/tmp/sway-whchivd2` verifies a real local
tux seat0/tty3 session (ID 15), isolated Sway from the released kit, and active
2560×1600 output at compositor scale 1. Recorded package versions match the kit.
All 187 released file hashes still pass. Each actual PID uses the released demo
binary and staged HoloNight libraries, including configuration/Core/Controls;
selected TextField, ComboBox, Button and ItemDelegate origins match the style.
Observer records establish the actual window DPR. All four saved exits are 0;
the inspected logs contain no QML type/reference/binding/assignment/load errors.

| Run suffix / PID | Style | Actual DPR | User G01–G06 result | Exit |
|---|---|---|---|---|
| 1789500940545549873 / 227470 | HoloNight | 1 | Pass | 0 |
| 1789501185564285240 / 227703 | HoloNight | 1.25 | Pass | 0 |
| 1789501296292753189 / 227792 | Fusion | 1 | Pass | 0 |
| 1789501557293580325 / 227964 | Fusion | 1.25 | Pass | 0 |

**G07 — empty-password caret visibility, open follow-up.** At scale 1 in both
styles, the user reports that the focused empty password field has no visible
caret; typing at least one character makes it visible. No issue was reported at
scale 1.25. Apparent clipping is the user's hypothesis; these logs do not establish
caret geometry, clipping or the responsible implementation. Greeter owns initial
production-QML reproduction and should establish the boundary before assigning a
provider repair. Acceptance: focused empty password caret is visible at scale 1
in both styles, with populated-field and fractional-scale behavior preserved.
No product repair or additional manual run is assigned in this evidence-review turn.

Selected raw session/run evidence and the user transcript are preserved under
`.cache/uqc212-manual/sway-whchivd2/`, excluding user profiles and shader caches.
`verification.json` records the independent checks; the SHA256SUMS manifest hash is
`d3103ac99ce549e07571fa91dc1b61f416303d7b5b565774f866599136856a14`.
Verification covered mappings, selected origins, actual DPR/output scale, session
identity, versions, exits, released hashes, documentation links and whitespace.
No product source, gitlink or released kit changed; product tests were not repeated
for this documentation-only acceptance record. F05 and other integration gates
retain their existing dispositions.

### G07 rendered investigation and diagnostic handoff — 2026-09-15

**G07 remains open; no production QML repair.** UQC-216 takes the planned bounded
diagnostic path because the focused empty production password caret is visible
in the automated software and private Sway/OpenGL comparisons. Clipping is still
unproven. UQC-212 remains Done, G01–G06 accepted and Batch 7 closed. UQC-201 stays
In Progress and the initiative Accepted; no provider assignment or integration
acceptance follows from this result.

Clean canonical requested baselines were confirmed before Ready/assignment.
Greeter implementation `66228b73789f9f678b68e59d4b45e371c95264ba` and documentation
handoff `b7277a63625e07e74f491839ce5b5f6dd4dfdad6` are published on canonical
origin/main, confirmed with `git ls-remote` before pinning. UQC-216 is Done for
local diagnostic delivery. Provider/configuration revisions remain unchanged.
The [local SDD](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-216.md)
records requirements, owner boundaries, detailed tests and failures.

The extended production fixture compares full-window caret-on/off pixels around
the mapped native cursor, with test-only blink suppression/restoration. Both
styles and actual DPR 1/1.25 pass empty → populated → cleared, focus loss/re-entry,
reveal/remasking and normal/compact transforms. Native masking and the selected
palette remain unchanged. No ancestor clipping is observed. A minimal selected-
style field with equivalent font/padding/transforms also passes the graphics
comparison. A separate unscaled-minimal-field software/DPR-1.25 zero-pixel case
is retained as diagnostic evidence, not classified as the reported scale-1 G07.
No shared-provider repair is justified by it.

Verification: 8/8 greeter CTests (43 core tests per style; 19 runtime tests per
style/DPR); four graphics cases with the staged platform theme; 16 build/relocated
selector/scale launch cases; import policy, formatting, QML lint/types, 15-unit
static analysis and REUSE all pass. Observer compilation with warnings-as-errors
and its passive installed-demo smoke check pass. Umbrella collector tests pass
14/14. Failed environment/harness attempts and successful evidence are retained
under `.cache/uqc216/`; no failed attempt is represented as acceptance. The passive
observer samples at 5 Hz for five minutes at most, retains bounded empty-caret
crops across native blink phases, and never logs entered text or changes input.

The fresh immutable G07 kit is [released](G07-HANDOFF.md) from this published
handoff. Four short human-operated Sway comparisons remain: both styles at Qt scales 1/1.25,
compositor scale 1, using only the [G07 checklist](GREETER-G07.md). Preserve the
released Batch 7 kit and completed checklist. F05, Batch 3 and real pre-session
login remain outside this iteration.

G07 release `/tmp/holonight-uqc216-e8pceq20`: all 17 preparation checks pass,
including the host-masked staged production-QML matrix, four graphics comparisons,
eight installed selector/scale launches and four independently observed demo
processes with matching actual DPR, verified isolation/origins and deliberately
reaped exit -15. Both observers load and the empty-field crops are present. The
native blink smoke captures show pixel variation without changing blink timing.
All 189 restored hashes, package versions, source snapshots, exact-prefix archive
restoration and existing-path refusal pass. Archive SHA-256 is
`994613367ec844c34b7c19b8e5bcfef85efab15dd7ee28ec120765b59a73d51f`.
Versions: Qt base 6.11.2-3, declarative 6.11.2-2, Sway 1:1.12-4,
Hyprland 0.56.2-3, hyprpolkitagent 0.1.3-10. Evidence and release audit are in
`.cache/holonight-uqc216-e8pceq20/`. All 187 original Batch 7 release hashes still
match. No human G07 result has been supplied; the finding is not closed.

### G07 manual diagnostic result — 2026-09-16

**G07 fails at Qt scale 1 in both styles; scale 1.25 passes the user's comparison.**
The four requested runs are complete. No repeat of this diagnostic kit is needed.
UQC-216 remains Done for diagnostic delivery, not repair; UQC-212/Batch 7 remain
accepted and closed. UQC-201 stays In Progress and the initiative Accepted.

`/tmp/res.txt` reports no cursor in the empty focused password input in both
scale-1 runs and “all good” for both scale-1.25 runs. Evidence from
`/tmp/sway-mobt7ro0` independently verifies local tux session 17, seat0/tty3,
isolated Sway with active 2560×1600 output at compositor scale 1, matching package
versions and all 189 released-kit hashes. Each PID uses the released greeter,
staged configuration/Core/Controls/platform theme and both observers. Selected
TextField/Button/ComboBox origins match the requested styles. Actual observer DPR
matches each request and every saved exit is 0.

| PID | Style | Actual DPR | Logical window | Empty crops | Rendered caret pixels per crop | User result |
|---|---|---|---|---|---|---|
| 241445 | HoloNight | 1 | 1276×1571 | 36 | Always 0 | Missing empty caret |
| 241576 | HoloNight | 1.25 | 1021×1257 | 24 | 0 or 23 | All good |
| 241643 | Fusion | 1 | 1276×1571 | 28 | Always 0 | Missing empty caret |
| 241719 | Fusion | 1.25 | 1021×1257 | 22 | 0 or 23 | All good |

**The captures now establish the rendering failure, beyond `cursorVisible`.**
Every scale-1 empty-field crop is uniformly background `#131a24`, including
captures after empty/focus transitions. Fractional-scale crops alternate between
background and 23 foreground `#e7edf5` pixels, consistent with native blinking.
At capture time the field is empty/focused, the window is active, `cursorVisible`
is true, and the recorded blink interval is 1000 ms.

The key coverage gap is the tiled window geometry. All four manual runs use
panel scale **0.78**, whereas the original automated production cases exercised
larger normal/compact transforms. The field remains 420×57 with Inter 14.25-point
font, left/right padding 54 and cursor rectangle `(54,17,1,23)`. At DPR 1 its
mapped cursor is `(771.616,789.111,0.78,17.94)`; at DPR 1.25 it is
`(543.136,633.026,0.78,17.94)` in logical coordinates. The native caret therefore
has a nominal physical width of 0.78 versus 0.975 pixels. All observed ancestors
have `clip=false`; the mapped cursor lies inside their recorded clip rectangles.
These facts motivate investigating subpixel rasterization and geometry, but do
not prove the mechanism or assign responsibility to the provider or Qt.

Next reproduction must use these exact window sizes, mapped positions and panel
scale, retain the failing pixel comparison, and repeat the minimal selected-style
field comparison before repair. No product edit or new owner assignment is made
in this evidence review. The observer never captures populated text; those states
and reveal/remasking cannot be independently pixel-verified here. All sampled echo
modes are Password, so the logs do not independently establish a reveal hold.
Preserve the user's fractional-scale pass without inventing additional observations.

Raw session/run evidence and results are preserved under
`.cache/uqc216-manual/sway-mobt7ro0/`, excluding user profiles and shader caches.
`verification.json` records the audit; SHA256SUMS manifest hash:
`042388b9c116f2384afacebe753bda1997616f109102a54e9c862341798839e2`.
Verification covers identity/output scale, versions, released hashes, mappings,
origins, actual DPR, exits, geometry, and every saved empty-field crop. This is an
evidence/documentation update; product tests are not repeated and no gitlinks or
released kit files change. F05, Batch 3 and real pre-session login stay outside scope.


### G07 exact-geometry reproduction and QtQuick handoff — 2026-09-16

UQC-217 reproduces the recorded failure in both styles and both software/OpenGL
backends with asserted window dimensions, DPR, panel scale and cursor mapping.
The equivalent plain QtQuick TextInput also fails, without a Controls import or
greeter ancestors. This establishes the shared QtQuick rendering boundary;
the precise rasterization mechanism remains for the next owner to diagnose.

The [local handoff](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-217.md)
contains the failing regression, comparison variants, commands, pixel results,
verification and evidence manifest. The test remains explicitly opt-in until a
repair is available; ordinary CI passing does not imply G07 acceptance.
The private Sway harness now waits for initial configuration and prevents tiling
from overriding requested test dimensions. Failed startup/geometry attempts are
retained separately from the verified reproduction.

This completes the planned external-owner reproduction branch. No production QML
or provider change, unchanged diagnostic kit, or new human observation is claimed.
A later proven repair must complete release checks and the four focused human
comparisons. G07 stays open; G01–G06 and Batch 7 remain accepted/closed,
UQC-216 remains Done, UQC-201 In Progress and the initiative Accepted.

Published greeter handoff `501d50cf29e2c3adbf1df3c7048d2637bc9c6924` was confirmed
on canonical origin/main before the umbrella pin update. Its clean checkout,
8/8 standard CTests, 4/4 normal/compact graphics cases, and static/licensing checks
pass. All eight exact cases produce the expected failing/passing scale split;
this is reproduction delivery, not a repair or manual acceptance.

### G07 QtQuick diagnosis and rejected layer candidate — 2026-09-16

UQC-218 takes the plan's rejected-experiment branch. **G07 remains open and
production QML is unchanged.** The response-field layer restores visible native
caret pixels in both styles, software/private-Sway OpenGL and DPR 1/1.25,
including the recorded geometry and a subpixel sweep. Paired direct/layer
captures show softer revealed text at panel scale 0.78, so the candidate does
not meet the required preservation of text sharpness and is not adopted.

The [local handoff](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-218.md)
records exact baselines, scope, checks and limitations. The
[upstream draft](../../../holonight-greeter/docs/sdd/unified-qtquick-controls/UQC-218-UPSTREAM.md)
contains a standalone plain-QtQuick reproduction without Controls, HoloNight
modules or platform theme, a matching Qt 6.11.2 source trace and sanitized pixel
attachments. Both standalone backends reproduce zero pixels at DPR 1 and 23 at
DPR 1.25. The source-supported explanation is non-antialiased subpixel rectangle
coverage; the draft distinguishes measured facts from sampling inference.
No upstream issue has been submitted.

All eight opt-in layer visibility cases pass; these do not constitute visual
acceptance. The original external diagnostic and its failing assertion remain
intact. Normal CI stays enabled without pretending an unrepaired exact-geometry
case is fixed. Native blink/resize acceptance and release checks were not
completed after visual rejection and are not claimed as passes.

No UQC-218 repair kit is released and no human repetition is requested. Existing
released kits are preserved. Kit repair-mode work belongs to a successful repair
branch and was not entered. A broader mitigation requires another plan. Preserve
G01–G06, closed Batch 7, UQC-216/UQC-217 Done, UQC-201 In Progress and initiative
Accepted; F05, Batch 3 and final ecosystem integration are outside this handoff.

Verification: 8/8 standard CTests, 4/4 normal/compact OpenGL cases, formatting,
QML lint/types, 15-translation-unit static analysis, Python compilation and
REUSE 99/99 pass. Full private evidence is retained under `.cache/uqc218/`;
manifest SHA-256 `b398fceec211aba95bbcaa12ece035cd02e2c0f6f94c0ce3717962522194966b`.

### G07 fullscreen acceptance and closure — 2026-09-16

**Closed — not an issue for intended fullscreen greeter use**, at the user's
request. Both HoloNight and Fusion pass the two-test fullscreen comparison at
compositor scale 1 and actual Qt DPR 1. The user observed a clearly visible
blinking caret in the focused empty password field, while populated, and after
Backspace clears all characters. Tab/Shift+Tab hides/restores the caret as the
field loses/regains focus. No issues were observed.

The previous missing-caret reproduction is retained as a specific windowed
geometry observation. Windowed greeter use is outside the intended design and
planned real scenarios; it does not warrant a product repair. Settings and AI
windowed testing has not reproduced this issue. This is a scope disposition based
on the successful intended-use comparison, not a claim that the underlying
exact-geometry QtQuick rendering behavior was repaired or cannot occur elsewhere.
No G07 repair, upstream submission or further manual comparisons are planned.
This closure supersedes earlier G07-open and repair-follow-up statements.

Reviewed `/tmp/res.txt` and `/tmp/sway-pdcyf6x6`, collected with immutable kit
`/tmp/holonight-uqc216-5kx47zdb`. The active local `tux` session was on tty3;
output eDP-1 is 2560×1600 at scale 1. Both logs transition from 1276×1571 windowed
geometry to 2560×1600 fullscreen geometry. Style origins and isolation records
confirm staged runtime use; both exits are 0.

| Run suffix / PID | Style | Fullscreen / DPR | Fullscreen samples / empty focused | User result | Exit |
|---|---|---|---|---|---|
| 1789548197191917992 / 24946 | HoloNight | 2560×1600 / 1 | 161 / 78 | Pass | 0 |
| 1789548252123856083 / 25061 | Fusion | 2560×1600 / 1 | 199 / 103 | Pass | 0 |

Both runs record empty/populated and focused/unfocused fullscreen states. Visual
caret/blink acceptance comes from the user's observations; this review did not
rerun a pixel-analysis test. Selected raw evidence, transcript and independent
`verification.json` are preserved in `.cache/uqc216-fullscreen-manual/`, excluding
session profiles and shader caches. SHA256SUMS manifest SHA-256:
`9be0a7d4280a78f1ac4d05aa9339c915d6fc6ed4f4056c19d8860902c8faa7fb`.

Documentation-only disposition: no product source, gitlink, released kit or
existing opt-in diagnostic changed. UQC-212/UQC-216/UQC-217/UQC-218 remain Done,
Batch 7 closed, UQC-201 In Progress and the initiative Accepted. F05 and remaining
ecosystem integration gates retain their dispositions. Product tests were not
rerun because no implementation changed.


### Batch 3 bounded lifecycle and crash diagnosis — 2026-09-16

[UQC-219 research and evidence](UQC-219.md) records the separate dispositions:

- **ScrollBar remains open.** Retained warning sequences implicate ScrollablePage
  composition, but exact lifecycle timing is unavailable. Added installed FormCard
  teardown coverage passes; no failing regression justifies a binding repair.
- **Historical Haruna crash remains open, with stronger thread evidence.** The
  build-matched core confirms the offending rectangle belongs to the Settings
  render thread while the engine belongs to the GUI thread. Asynchronous creation,
  delegate reuse/cancellation and broad-debug threaded probes pass. The initiating
  trigger and repair remain unproven; successful retries do not resolve SIGABRT.
- **Settings Fusion hover: research-pending. Haruna Fusion hover: research-pending.**
  Documentation and a Qt 5.13.1 menu-bar discussion do not classify these Qt 6.11.2
  observations. No matching currently open Qt bug or supported workaround was
  verified; tracker retrieval failure is not evidence that no issue exists.
  No local hover instrumentation or repeated manual testing is assigned.

Provider test/SDD handoff `c9aacd8` is published and pinned after canonical
confirmation. Verification: 24 narrow style/DPR checks, 5 focused/installed CTests,
87/87 final provider CTests, 8 private threaded Wayland checks, format/whitespace,
focused clang-tidy (nonfatal warnings documented) and REUSE 395/395 pass.
Production QML, public APIs and consumer sources are unchanged. No new immutable
kit is necessary. UQC-219 Done for diagnosis; UQC-207/UQC-201 In Progress and
initiative Accepted. All accepted rendering, G07 closure and unrelated dispositions
are preserved; final Batch 8 integration was not run.

## Batch 3 user-directed closure — 2026-09-16

UQC-207 is **Done** and Batch 3 is **closed by user-directed disposition**.
Accepted icons/menu/selection, Switch focus and dropdown backgrounds remain
accepted. Busy-button focus is expected Qt behavior; Tokodon's existing chevron
deferral is unchanged.

ScrollBar warnings, the historical Haruna crash and Settings/Haruna Fusion hover
are **deferred, non-blocking historical findings**. They are not described as fixed.
[UQC-219](UQC-219.md) and the dated findings retain evidence, unsuccessful
reproductions and ownership uncertainty. This disposition supersedes earlier
open/research-pending instructions without deleting their history.

Reopen only when a concrete recurrence blocks required functionality or final
acceptance. No further investigation, instrumentation or manual comparisons solely
for these findings. F05/P01 external findings remain documented; no upstream
investigation or report submission is requested. UQC-201 stays In Progress and the
initiative Accepted pending the final gates.

## Batch 8 automated acceptance and first handoff — 2026-09-16

Fresh dependency-order and installed checks at the clean published gitlinks pass;
see [results, versions and remaining gates](FINAL-ACCEPTANCE.md). No production
behavior or public API changed. Batch 3 remains closed with its user-directed
deferrals, and completed acceptance from other batches is preserved.

The [first short handoff](BATCH8-HANDOFF.md) covers only NeoChat Sway fractional
control-origin/interaction/palette gaps in two styles. Review both evidence paths
before preparing the next manual batch. Successful authentication, shipped systemd
service/wrapper operation and real pre-session greeter use remain final gates;
no privileged launch or authentication challenge has been performed here.
UQC-201 stays In Progress; initiative Accepted.

## Batch 8 NeoChat Sway acceptance — 2026-09-16

The user reports all three requested checks passed with no observed issues in
both runs: logged-out text editing/Tab traversal, reachable settings/selectors
and fractional scrolling/row reachability, plus the requested palette round trip.
The first [two-run handoff](BATCH8-HANDOFF.md) is complete; no NeoChat repeats
are requested for this scoped Sway/DPR-1.25 coverage.

| Style | Run in `sway-zb64ybrm` | PID | Measured DPR | Exit |
|---|---|---|---|---|
| HoloNight | `neochat-1789576971952072995` | 169955 | 1.25 | 0 |
| Fusion | `neochat-1789577196622721077` | 170255 | 1.25 | 0 |

Reviewed the supplied `/tmp/res.txt` and `/tmp/sway-zb64ybrm` copy of the original
`/home/tux/uqc-guided-evidence/sway-zb64ybrm` session. Identity records active local
tux UID 1001, seat0/tty3, session 7. Session command selects the released Sway
configuration (configured output scale 1); effective output scale is not separately
captured, while both application observers independently measure DPR 1.25.
Recorded package versions match the release inventory, including NeoChat 26.08.1-1,
Qt base 6.11.2-3 / declarative 6.11.2-2 and Sway 1:1.12-4.

All 267 release hashes match. Recomputed saved-map isolation passes in both runs;
PID metadata agrees with the style, scale, staged paths and session. Observer
records identify created popup objects originating from HoloNight ComboBox.qml
and Qt Fusion ComboBox.qml respectively. Other observed controls originate in
NeoChat pages and Kirigami/FormCard composites; those are application/composite
origins, not proof that every inherited standard-control part was replaced.
Keep that boundary explicit; no blanket all-controls claim. Palette readability
and interaction are user acceptance, not inferred from process maps.

Diagnostics are not absent: both runs contain Kirigami ScrollablePage's null
`flickable` TypeError; HoloNight also contains NeoChat RoomDrawer's
`roomDrawerWidth` binding loop and the historical provider ScrollBar null
`orientation` warning. The user reports no functional blocker. Preserve these
lines as observations; do not reopen Batch 3, infer ownership beyond the reported
locations, investigate upstream or describe them as repaired. F05/P01 dispositions
are unchanged; this palette pass does not establish that P01 was fixed.

Selected raw evidence, user notes, computed file hashes and `review.json` are
preserved under `.cache/holonight-uqc201-final-yn9_fquf/manual-neochat-sway/`.
Only logs/metadata/maps/outcomes were copied, not profile credentials or cookies.
These are review-time hashes of supplied evidence, not pre-existing collection
signatures. No source, pin or released-kit change; no product tests repeated.
Next is [Tokodon Sway fractional coverage](BATCH8-TOKODON.md), two runs using the
same verified kit. UQC-201 In Progress; initiative Accepted.

## Batch 8 Tokodon Sway acceptance — 2026-09-16

The user reports all requested logged-out text/focus, selector/scrolling and
palette-round-trip checks passed with no observed issues in both styles.
The [Tokodon handoff](BATCH8-TOKODON.md) is complete for Sway/DPR 1.25; do not
repeat these scoped checks.

| Style | Run in `sway-xt4fjcrj` | PID | Measured DPR | Exit |
|---|---|---|---|---|
| HoloNight | `tokodon-1789579305455355467` | 173768 | 1.25 | 0 |
| Fusion | `tokodon-1789579441846949791` | 174047 | 1.25 | 0 |

Reviewed `/tmp/res.txt` and `/tmp/sway-xt4fjcrj`, supplied copies of the real tux
session evidence. Identity records active local UID 1001, seat0/tty3, session 9;
PID metadata agrees with that session and requested selectors/staged paths.
All 267 released-kit hashes and recorded package versions match. Tokodon is
26.08.1-1, Qt base/declarative 6.11.2-3/6.11.2-2, Sway 1:1.12-4.
Recomputed saved-map isolation passes for both processes; both saved exits are 0.
Observers independently record DPR 1.25; output scale 1 is configured by the kit,
not separately measured in the supplied session evidence.

Created-object origins include HoloNight ComboBox.qml in the HoloNight run and
Qt Fusion ComboBox.qml in the Fusion run. The HoloNight run additionally records
Qt Basic DialogButtonBox.qml: explicit observed fallback, not an all-HoloNight
claim. Other origins belong to Tokodon pages and Kirigami/FormCard composites;
their inherited parts are not exhaustively classified. HoloNight visited more
About/Shortcuts/server surfaces in the trace; the Fusion trace is narrower.
User-reported completion accepts the requested interaction coverage, without
claiming identical object inventories or accepting unvisited account surfaces.

Both logs retain Kirigami ScrollablePage's null `flickable` TypeError. The
HoloNight log also retains MessageDialog `Success`/null size diagnostics,
AboutPage null width, FormDelegateBackground null `visibleChildren`, and the
historical provider ScrollBar null `orientation` warning. No functional blocker
was reported. These locations do not establish repair ownership; no investigation
or repair is assigned. Batch 3 remains closed, chevron deferral unchanged, and
P01 is not claimed fixed by the successful palette comparison.

Selected logs/maps/metadata/exits, user notes, review-time hashes and review.json
are preserved at `.cache/holonight-uqc201-final-yn9_fquf/manual-tokodon-sway/`.
No profile credentials/cookies copied. No product, pin or immutable-kit change;
no product tests repeated. Next: [two Haruna runs](BATCH8-HARUNA.md).
UQC-201 remains In Progress and initiative Accepted.

## Batch 8 Haruna Sway acceptance — 2026-09-16

The user reports all requested local playback/toolbar/menu, settings editing/
navigation/scrolling/selectors and palette-round-trip checks passed in both
styles, with no issues observed. The [Haruna handoff](BATCH8-HARUNA.md) is complete
for its scoped Sway/DPR-1.25 coverage; no repeat runs requested.

| Style | Run in `sway-8vt13f26` | PID | Measured DPR | Exit |
|---|---|---|---|---|
| HoloNight | `haruna-1789583324150016259` | 183573 | 1.25 | 0 |
| Fusion | `haruna-1789583570979632619` | 183973 | 1.25 | 0 |

Reviewed `/tmp/res.txt` and supplied `/tmp/sway-8vt13f26` copy of the tux session.
Identity records active local UID 1001, seat0/tty3, session 9; PID metadata and
session command agree with the released Sway configuration and staged selectors.
All 267 kit hashes and recorded versions match: Haruna 1.8.1-2, Qt base/declarative
6.11.2-3/6.11.2-2, Sway 1:1.12-4. Recomputed saved-map isolation passes and saved
exits are 0. Observers measure DPR 1.25 in both runs; output scale 1 is configured,
not independently measured by the supplied evidence.

The HoloNight run records created origins in HoloNight ComboBox, Menu, MenuBar
and ToolTip. The Fusion comparison records Fusion ComboBox, Menu and MenuBar.
Both also record Fusion DialogButtonBox and Qt Quick Dialogs internals, alongside
Haruna/Kirigami-authored objects. This preserves the explicit fallback and
application-painted boundaries; it does not establish that every inherited
standard-control part is HoloNight. Playback and palette readability are user
acceptance, not inferred from imports or maps.

The targeted scan finds no TypeError, ReferenceError, binding-loop or
QQmlApplicationEngine-failure matches in either log. This is not an assertion of
zero diagnostics of every kind, nor proof that the historical Haruna crash or
Fusion hover finding is fixed. Batch 3 closure and all deferrals remain unchanged.

Selected logs/maps/metadata/exits, user notes, review-time hashes and review.json
are preserved at `.cache/holonight-uqc201-final-yn9_fquf/manual-haruna-sway/`;
no profile credentials/cookies copied. No source, pin or immutable-kit change;
no product tests repeated. Next: [two read-only package-manager runs](BATCH8-PACKAGES.md).
UQC-201 remains In Progress; initiative Accepted.

## Batch 8 package-manager Sway acceptance — 2026-09-17

The user reports all requested read-only search/category/focus, package-details/
scrolling/arrow navigation and reachable popup/disabled-state checks passed in
both runs with no issues observed. The [package-manager handoff](BATCH8-PACKAGES.md)
is complete for Sway/DPR 1.25. No package transactions or repository refresh
acceptance is claimed; no repeats requested for these scoped cells.

| Style | Run in `sway-m49qel6p` | PID | Measured DPR | Exit |
|---|---|---|---|---|
| Embedded default (overrides unset) | `packages-1789594894628909407` | 211000 | 1.25 | 0 |
| Fusion | `packages-1789595100475289015` | 211240 | 1.25 | 0 |

Reviewed `/tmp/res.txt` and `/tmp/sway-m49qel6p`. Identity records active local
tux UID 1001, seat0/tty3, session 9; session command uses the released Sway config.
Process timestamps are 2026-09-16 21:41/21:45 UTC (2026-09-17 locally).
All 267 release hashes and recorded package versions match. Qt base/declarative
are 6.11.2-3/6.11.2-2; Sway is 1:1.12-4. Both executable paths identify the
staged `prefix/bin/holonight-packages`; recomputed saved-map isolation passes,
with the recorded selectors, session and staged paths matching. The default run
has both style and configuration overrides unset; Fusion has only its style
selector set. Both observers independently measure DPR 1.25 and saved exits are
0. Output scale 1 is configured, not separately measured by the supplied evidence.

Observed origins include HoloNight ComboBox/ToolTip and HnSearchField in the
default run, Fusion ComboBox/ToolTip in the override run, and the application's
filter tabs, toolbar, package table/rows/header, details and sidebar in both.
These demonstrate the selected controls and application/composite boundaries,
not exhaustive replacement of every inherited part. The targeted scan finds no
TypeError, ReferenceError, binding-loop or QQmlApplicationEngine-failure matches
in either log; this is not a blanket zero-diagnostics claim.

Selected logs/maps/metadata/exits, notes and review-time hashes are preserved in
`.cache/holonight-uqc201-final-yn9_fquf/manual-packages-sway/`, with review.py and
review.json. No profile credentials/cookies copied. No product, pin or released-kit
change; no product tests repeated. Next: [Settings at scale 1](BATCH8-SETTINGS.md).
Prior accepted focus/dropdown repairs remain accepted. UQC-201 In Progress;
initiative Accepted; all deferred findings and final authentication/service/
pre-session gates unchanged.

## Batch 8 Settings fractional results and composition disposition — 2026-09-17

The submitted commands used **scale 1.25**, although the handoff requested scale
1. Observer measurements independently confirm DPR 1.25 in both runs. Preserve
these successful fractional results; the requested scale-1 cells remain pending.
Do not rerun scale 1.25 or use these results to claim scale-1 acceptance.

| Style | Run in `sway-adk_476k` | PID | Measured DPR | Exit |
|---|---|---|---|---|
| Embedded default | `settings-1789596069053077199` | 214268 | 1.25 | 0 |
| Fusion | `settings-1789596751444043230` | 214776 | 1.25 | 0 |

The user reports all default checks passed. The Fusion report identifies an
Appearance/Weather dropdown visual difference and explicitly disposes it as
non-blocking, requesting only investigation and a separate Settings-local SDD.
No functional blocker is reported for the scoped fractional checks; accept with
that disposition, without claiming the visual difference was repaired.

Reviewed `/tmp/res.txt` and `/tmp/sway-adk_476k`: active local tux UID 1001,
seat0/tty3, session 9, released Sway config. All 267 kit hashes and recorded
package versions match. Both binaries are the staged holonight-settings; saved
map isolation, default-unset/Fusion selectors, session correlation and exits pass.
Qt base/declarative are 6.11.2-3/6.11.2-2, Sway 1:1.12-4. Output scale 1 is
configured, not separately measured. Both logs contain HnIconComboBox and
Appearance/Weather objects, with the expected HoloNight/Fusion ComboBox origins.
The targeted QML error scan has no TypeError, ReferenceError, binding-loop or
engine-load-failure matches. This is not a blanket zero-diagnostics claim.

### Bounded composition investigation

Appearance uses four HnIconComboBox font selectors; Weather uses six ordinary
Controls.ComboBox selectors. The shared composite replaces palette, font/metrics,
content, frame, popup and delegate presentation with HoloNight composition, but
inherits the runtime style's indicator. This explains the Fusion triangle amid
HoloNight composite visuals. Weather leaves those presentation slots to Fusion.
This is the application's control-composition choice, not evidence of failed
runtime style selection or an unauthorized direct-style import.

Detailed source analysis, inspected revisions, ownership and unassigned future
implementation criteria are in the [Settings-local SDD](../../../holonight-settings/docs/sdd/dropdown-composition-consistency/SPEC.md).
The investigation is complete; no production repair, additional comparison solely
for this finding, or provider change is assigned. The user's non-blocking
application-local disposition is retained outside UQC integration gates.

Published documentation-only Settings `0eb5028e206e12791ecbe6c2404bc37c39a4962a`
and confirmed canonical origin/main before pinning. Its diff from kit baseline
`2508635` contains only the new SDD; the immutable kit and automated/runtime
acceptances remain valid for unchanged implementation. No rebuild or product-test
rerun is needed for this documentation change. All other gitlinks unchanged.

Selected evidence and review-time hashes are retained under
`.cache/holonight-uqc201-final-yn9_fquf/manual-settings-sway/`; no profile
credentials/cookies copied. Next: the [two originally requested scale-1 runs](BATCH8-SETTINGS.md).
UQC-201 In Progress; initiative Accepted; prior deferrals and final gates unchanged.

## Settings Weather failures and UQC-220 ownership — 2026-09-17

The user corrects earlier observations and requests repair in this initiative.
HoloNight Weather dropdown labels sit below vertical center at scales 1 and 1.25.
Fusion Weather closed ComboBoxes **and** popup rows lack hover feedback (explicit
clarification). The previous fractional visual acceptance is qualified by this
correction; scale-1 runs are completed evidence, not passing acceptance.

Verified `/tmp/sway-dmn1wyrl`: default run `settings-1789597592751176822`
(PID 216769), Fusion `settings-1789597906201175856` (PID 217126), both measured
DPR 1, staged isolation verified, exit 0. All 267 kit hashes and recorded versions
match. Evidence and review-time hashes preserved in
`.cache/holonight-uqc201-final-yn9_fquf/manual-settings-sway-scale1/`.
Normal exits/loading do not close the reported visual defects.

[UQC-220](UQC-220.md) assigns the demonstrated provider boundaries. A standalone
HoloNight ComboBox reproduces label-center y=16 in a 28-pixel row, caused by
8-pixel padding around a 16-pixel label. Private headless Wayland comparison
shows plain Qt/Fusion hover enabled, but disabled when the HoloNight platform
theme supplies the system hint; explicit Qt hover enable restores control/row
flags. No pointer, clicking or focus automation used. Initial sandbox compositor
socket failure was retried outside the command sandbox; logs in `.cache/uqc220`.

This user-directed reopening applies to owned Settings hover. Third-party
historical findings remain deferred; no upstream investigation or manual
comparison solely for them. The separate Settings composition SDD remains
non-blocking and unimplemented. UQC-201 stays In Progress; initiative Accepted.
Further manual coverage batches pause for a verified focused repair handoff.

### UQC-220 verified provider repair — 2026-09-17

Published `7e101bd23661f21efe95cd11dad092069c68601d`; canonical main confirmed
before pinning. Both regressions fail on baseline and pass after repair. Provider
87/87 CTests (including installed acceptance), fractional composites, import
policy, formatting, QML lint and focused static analysis pass with existing
advisories. Private Wayland confirms restored hover hint/control/row flags and
preserved explicit hover disable. Details/commands in the [local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-220.md).
The geometry fix removes excess vertical padding only; platform theme retains
base effect flags and adds HoverEffect. No Settings composition change.

UQC-220 Done for local delivery; human repair acceptance remains pending.
The old final kit remains unchanged and must not be used to test the repair.
A fresh [focused handoff](WEATHER-REPAIR.md) follows kit verification; no final
integration claim or repeat third-party manual comparisons.

## UQC-220 repair kit release — 2026-09-17

Built with `python3 docs/initiatives/unified-qtquick-controls/prepare-rendering-kit.py --weather-repair`.
Released immutable `/tmp/holonight-uqc207-t9ao_81w`; exact-prefix restoration and
all 201 file hashes pass. Existing-path restoration refusal passes (exit 2).
Archive `.cache/holonight-uqc207-t9ao_81w/holonight-uqc207-t9ao_81w.tar.gz`:
SHA256 `1605cbbf179d16ead1990f4d49c42a2842937e2a1caf63306ba54add35810c91`.
Exact six clean, published source revisions are recorded in kit `revisions.json`;
provider is `7e101bd23661f21efe95cd11dad092069c68601d`.

Dependency-order build/install, provider/AI/Settings compiled acceptance at both
styles and scales 1/1.25 pass, with host provider masked. Twenty staged actual-app
loading/origin/DPR runs pass; collector tests 14/14, Python parse and shell syntax
pass. Commands and exits: `.cache/holonight-uqc207-t9ao_81w/results.jsonl`;
logs and runtime evidence are alongside it. This focused kit does not replace
final ecosystem integration or establish visual acceptance. Full affected final
checks remain recorded in FINAL-ACCEPTANCE.md.

[Human handoff](WEATHER-REPAIR.md) is limited to two Settings scale-1 runs in a
fresh Sway session: default and Fusion, Weather row centering and both closed/row
hover paths. Review returned evidence before requesting fractional coverage.
No pointer, focus or credential automation. UQC-201 stays In Progress and the
initiative Accepted; other historical deferrals and accepted evidence remain.

Read-only package versions at release: qt6-base 6.11.2-3, qt6-declarative
6.11.2-2, Sway 1:1.12-4, Haruna 1.8.1-2, NeoChat/Tokodon 26.08.1-1.

## UQC-220 scale-1 repair review — 2026-09-17

User evidence `/tmp/sway-8tnc_rq7` verifies repaired kit
`/tmp/holonight-uqc207-t9ao_81w`: all 201 hashes, recorded versions,
staged process/maps isolation, default/Fusion control origins and measured DPR 1.
Default run `settings-1789603382991554755` (PID 257497) accepts corrected row
alignment and reports no other issues. Fusion run `settings-1789603542615733478`
(PID 257682) accepts popup hover; closed button has no perceptible hover feedback,
conditionally acceptable to the user if it is Fusion's design. Both exits are
intentional Ctrl+C (`-2`) because Ctrl+Q was not mapped, not normal-close evidence
or a crash. Selected evidence, notes, hashes and `review.py` are preserved under
`.cache/holonight-uqc207-t9ao_81w/manual-settings-scale1/`.

Installed Qt Fusion `ComboBox.qml` uses `impl/ButtonPanel.qml`, which passes
`control.hovered` into its background/gradient color calculation. A bounded
private-bus offscreen evaluation of the installed Fusion color function returns
normal `#2d3743`, hover `#2f3946` with the staged HoloNight palette: only 2–3 RGB
levels of difference. Plain Qt palette comparison returns `#e8e8e8` → `#f1f1f1`.
The repaired theme enables hover. Probe source and output are preserved alongside
the evidence. This establishes very subtle native Fusion color feedback, not
absence of a hover design; it does not prove the hovered state of the user's
closed control from logs. Preserve that perceptual limitation without claiming
visible closed-button acceptance or assigning another speculative repair.
Initial offscreen probe attempts timed out; isolated retry first exposed a
missing Fusion import. Corrected private-bus probes both exit 0; diagnostic
process cleaned up. No live pointer/focus automation or production change.

Next bounded batch: same immutable kit, Settings default and Fusion at scale
1.25. Check row alignment and popup hover, record closed-button perception, and
close using the window close button manually (Ctrl+Q is not required). Preserve
scale-1 row acceptance. UQC-220 local delivery Done; fractional manual coverage
pending. UQC-201 In Progress; initiative Accepted.

## UQC-220 fractional repair acceptance — 2026-09-17

Reviewed `/tmp/sway-dihb0lxm` with user results preserved under
`.cache/holonight-uqc207-t9ao_81w/manual-settings-scale125/`.
Default run `settings-1789606497177582759` (PID 262119) and Fusion run
`settings-1789606584178014743` (PID 262313) both measure DPR 1.25, verify staged
process/maps isolation and expected control origins, and exit normally (0).
Recorded versions match the released kit; no screened QML runtime errors.
User reports no issues in either style and explicitly observes/accepts the
closed Fusion button's nearly imperceptible hover color change. This resolves
the previous conditional acceptance, rather than claiming no hover design.
Scale-1 row centering/popup hover acceptance remains preserved. UQC-220 focused
manual repair acceptance is complete; no further Weather comparison is required.

Integrity qualification: 200 of 201 released hashes match. The sole difference
is `sway.conf` appending exactly `bindsym Mod4+Q kill`; original and observed
configs are preserved in the review directory, and the original matches its
release hash. This compositor close-key addition does not change application,
provider, style, palette or scale artifacts. Accept the evidence with this exact
configuration deviation; do not describe the used directory as byte-identical
to the immutable release. The archive is unchanged and the assistant did not
modify the kit or remove the added binding. Review script and selected logs,
process maps/metadata, results and per-run hashes are preserved alongside it.

Updated roadmap, findings, acceptance checklist and UQC-220 ledger. No product
changes or new repair assignment. Affected full integration revalidation and
remaining final human gates stay open; UQC-201 In Progress, initiative Accepted.
