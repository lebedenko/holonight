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
F06 provider UQC-213 and F07 shell UQC-214 repairs are published and locally Done.
F06 is accepted for the reported Settings/greeter HoloNight sequence below; F07
awaits both launcher styles. See [current batch order](BATCHES.md).


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
