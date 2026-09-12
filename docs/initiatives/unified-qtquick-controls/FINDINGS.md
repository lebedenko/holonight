# UQC acceptance findings — canonical register

Initiative **Accepted**; UQC-201 **In Progress**. Broad manual acceptance is paused
until repairs are available. This register is authoritative for current findings;
[GUIDED.md](GUIDED.md) and [TASKS.md](TASKS.md) retain chronological evidence,
including superseded interpretations. Add new observations here once, and link
from the ledger rather than copying the narrative into both historical documents.
All findings below remain open unless an explicit repair/acceptance result says otherwise.

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
| F05 | AI H 1.25; tux VT3 → VT1 → back | Tab/Backtab stop until user clicks; event delivery/compositor focus unknown. Umbrella investigates session delivery with AI; do not connect to wrapper or earlier VT freeze. | [AI](GUIDED.md#ai-provider-form-observations--2026-09-10) | Correlate delivered events and active window; keyboard navigation resumes on VT return. |

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
| F06 | Open a dropdown by keyboard with an unknown/stationary pointer over its rows, or switch from mouse to keyboard. Two rows look highlighted: keyboard selection and pointer hover. User reports visual-only impact and similar behavior across HoloNight apps. | holonight-qt investigates shared delegate feedback; broad app scope is user-reported, not independently enumerated. ItemDelegate and icon-composite backgrounds render hover separately from highlight/current state. | Keyboard interaction has one unambiguous active-row indication; a stationary pointer does not introduce a competing active-looking row. Deliberate pointer movement/click still restores normal mouse interaction. |
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

## Application layouts

| ID | Application / context; reproduction | Facts / hypothesis; owner | Evidence | Acceptance |
|---|---|---|---|---|
| L01 | Settings H 1.25; press/drag slider (exact page pending); Sway equivalent | Width shrinks and value jumps. Not reported in F comparison. holonight-settings investigates measured layout/provider interaction. | [Settings](GUIDED.md#settings-continuation-observations--2026-09-10) | Stable usable track width through press/drag; no geometry-induced value jump. |
| L02 | AI provider Temperature H/F 1.25 | H knob-only, F track visible but too short; layout suspected. holonight-ai owns form measurement/repair. | [AI](GUIDED.md#ai-fusion-comparison-and-switch-feedback--2026-09-10) | Adequate stable track alongside SpinBox at supported widths/scales under both styles. |

## Shell — holonight-shell

| ID | Application / context; reproduction | Confirmed facts / suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| S01 | Shell H 1.25; start then interact with bar | Missing right items, bar shrinks/jitters, sections slide in/out, unusable clicks; reserved space appears constant, unmeasured. Scale 1 functional; F 1.25 untested. | [fractional](GUIDED.md#shell-default-failure--2026-09-10) | Stable geometry, all sections visible/clickable at 1.25; measure exclusive zone. |
| S02 | Shell H/F 1; inspect topbar including transient systemd launch | Broken right frame edges; network/audio/battery/layout backgrounds cover frame/gradient; bell/date correct. Composition suspected, frame path not proven broken. | [frames](GUIDED.md#shell-default-scale-1-comparison--2026-09-10), [systemd](GUIDED.md#transient-systemd-shell-visual-result--sway-handoff--2026-09-11) | Complete frame edges and intended transparent status backgrounds; preserve functional scale-1 interaction. |

## Authentication — holonight-shell

| ID | Application / context; reproduction | Confirmed facts / suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| A01 | Owned Polkit H; open user selector in isolated run | Two reserved but blank identity rows. Custom avatar/text delegate uses model roles; independent from D01. | [prompt](GUIDED.md#owned-agent-prompt-findings--2026-09-10), private auth run `20260910T192833Z` | Correct identity labels/avatars and selection from actual model roles. |
| A02 | Same run; failed submission shows error | Input disappears, Password label remains. Label/input visibility conditions differ; lifecycle/retry needs reproduction. | [prompt](GUIDED.md#owned-agent-prompt-findings--2026-09-10) | Label and editor visibility track supported prompt/error/retry lifecycle. Do not solicit another failed credential submission. |
| A03 | Same run after failure; Cancel prompt | Prompt closes but Python challenge hangs until Ctrl+C. Agent exit 0 verified; challenge.txt absent, no normal completion. UQC-205 baseline reproduction locates missing listener GError: coordinator completion occurs, but libpolkit cannot reply. Typed cancellation error repairs the automated path. | [hang](GUIDED.md#owned-agent-cancellation-completion-failure--2026-09-10), [repair/verification](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-205.md) | Deterministic cancellation completes pending request exactly once and parent exits; cover failure-then-cancel and direct cancel with isolated fake backend. **Closed**: automated completion checks and [manual cancellation result](#manual-polkit-cancellation-acceptance--2026-09-12) pass. |
| A04 | Askpass F 1.25; inspect unfocused/focused editor then cancel | Left border appears half thickness; focused ring intact, cancel exit 1. Shell supplies Rectangle background; clipping/fractional position suspected only. | [border](GUIDED.md#owned-askpass-fusion-scale-125-border-finding--2026-09-10) | Uniform intended border at fractional scale without breaking cancellation/focus. |

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
Origins/geometry remain uninstrumented; real pre-session login is a separate gate.

| ID | Reproduction | Confirmed facts / suspected cause | Acceptance |
|---|---|---|---|
| G01 | Tab/Backtab through login | User selector absent from cycle; F functional mouse use does not establish Tab reachability | Enabled selector reachable both directions, visible indicator. |
| G02 | Focus password reveal; hold/release Space | Mouse reveal works; keyboard does not; lifecycle unknown | Keyboard hold-to-reveal matches documented behavior and remasks on release/focus loss. |
| G03 | Inspect disabled layout selector without configured choice | Correctly disabled but unexpected colors and hover appearance | Appropriate disabled appearance, no interactive hover feedback. |
| G04 | Inspect password background | User questions palette alignment; no proven color defect | Identify semantic palette source and validate intended contrast/state. |
| G05 | Inspect user selector | User requests existing avatar selector; component identity/API not yet located. F selector unusually large (collapsed/popup unknown) | Adopt appropriate existing component after contract review; bounded geometry and keyboard reachability. |
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

1. **UQC-204**, holonight-qt: F01–F03; baseline and implementation/verification in
   [local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-204.md).
2. **UQC-205**, holonight-shell: A03 complete; see the manual acceptance above.
   A01/A02/A04 remain pending after the UQC-206 dropdown checkpoint.
3. **UQC-206**, holonight-qt: D01–D04; separate popup geometry, delegates and dismissal
   reproductions; do not assume the binding loop explains every symptom.
4. **UQC-207**, holonight-qt: R01–R04 and F04 investigation; **UQC-208** palette
   investigation P01/P02; settle origins before accepting implementation scope.
5. **UQC-209**, holonight-settings: L01; **UQC-210**, holonight-ai: L02;
   **UQC-211**, holonight-shell: S01/S02; **UQC-212**, holonight-greeter: G01–G06.

UQC-205 is Done for A03 only. UQC-206 is In Progress with its [provider SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-206.md),
canonical baseline and isolated reproductions. Packages 207–212 remain Planned
investigation/repair packages, not Ready assignments. Each needs its own local
SDD, exact canonical baseline and reproduction before work starts. F05 and C01–C06 remain umbrella investigations until ownership is settled.
F06 (provider visual input feedback) and F07 (shell launcher selection) are new
planned investigations; no implementation assignment or baseline is implied.


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
