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
installed modules pass eight of eight in all four combinations. F01–F03 remain
pending the short real Settings/AI keyboard regression; original observations are
preserved below. No other finding is closed by this handoff.

| ID | Application / context; reproduction | Confirmed facts and suspected cause | Evidence | Acceptance |
|---|---|---|---|---|
| F01 | Settings H/F, 1/1.25; edit Weather City then Tab. AI H/F 1.25; first ComboBox traversal then full cycle | Text editing works; first-cycle indicator absent, later cycle restores it. Provider baseline reproduces lost visualFocus from parameterless wrapper forwarding. Sway Settings equivalence reported with limits above. | [Settings](GUIDED.md#evidence-review), [AI clarification](GUIDED.md#ai-fusion-comparison-and-switch-feedback--2026-09-10); private `.cache/uqc201-focus-probe/` | First and repeated Tab/Backtab entries retain owner, reason and visible indicator under both styles. |
| F02 | AI providers H/F 1.25; Context value → invisible stop → Temperature value → Slider; reverse lacks extra stop | Direction asymmetry reported repeatedly. Labels match Ollama source; user did not confirm provider. HnFormField compound wrapper is a reproduction target. | [AI](GUIDED.md#ai-provider-form-observations--2026-09-10) | Natural child traversal in both directions, no invisible compound stop. |
| F03 | AI H/F 1.25; traverse provider form | Disabled-control traversal is suspected only, not observed focus ownership. UQC-204 guards hidden/disabled/missing/non-tab children without claiming all app symptoms explained. | [AI](GUIDED.md#ai-provider-form-observations--2026-09-10) | Isolated eligibility regressions pass; app-specific attribution remains conditional. |

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
| D04 | Settings H 1.25; reopen selected ComboBox | Selected item not focused on opening; visibility, highlight and actual focus still need separation. | [Settings](GUIDED.md#settings-continuation-observations--2026-09-10) | Current row visible, correctly highlighted and keyboard navigation begins from expected selection. |

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
| A03 | Same run after failure; Cancel prompt | Prompt closes but Python challenge hangs until Ctrl+C. Agent exit 0 verified; challenge.txt absent, no normal completion. Bridge/coordinator completion loss unlocated. | [hang](GUIDED.md#owned-agent-cancellation-completion-failure--2026-09-10) | Deterministic cancellation completes pending request exactly once and parent exits; cover failure-then-cancel and direct cancel with isolated fake backend. Highest next priority. |
| A04 | Askpass F 1.25; inspect unfocused/focused editor then cancel | Left border appears half thickness; focused ring intact, cancel exit 1. Shell supplies Rectangle background; clipping/fractional position suspected only. | [border](GUIDED.md#owned-askpass-fusion-scale-125-border-finding--2026-09-10) | Uniform intended border at fractional scale without breaking cancellation/focus. |

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
- Owned Polkit challenge completion record is absent. No cancellation success is
  inferred from prompt closure or the agent's successful exit.
- Positive package-manager and askpass observations retain their limited tested
  surfaces; no exhaustive pass. Account-dependent third-party surfaces untested.
- Process maps prove native loading, not every created Control origin. Direct
  private-bus, desktop-entry and transient systemd process correlation do not close
  shipped-service/wrapper acceptance. Transient unit cleanup is confirmed; manager
  environment was unchanged. Preserve earlier failures in INTEGRATION.md.
- Remaining compositor/style/scale cases, palette round trips, shipped services,
  owned Polkit completion and real pre-session greeter acceptance remain explicit
  integration gates. No broad acceptance restart or full Sway repetition now.

## Repair order and repository packages

1. **UQC-204**, holonight-qt: F01–F03; baseline and implementation/verification in
   [local SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/UQC-204.md).
2. **UQC-205**, holonight-shell: A03 first, then A01/A02/A04; prepare local lifecycle
   reproduction and fake-backend completion tests before Ready assignment. Only A03
   precedes UQC-206; remaining authentication repairs follow the dropdown checkpoint.
3. **UQC-206**, holonight-qt: D01–D04; separate popup geometry, delegates and dismissal
   reproductions; do not assume the binding loop explains every symptom.
4. **UQC-207**, holonight-qt: R01–R04 and F04 investigation; **UQC-208** palette
   investigation P01/P02; settle origins before accepting implementation scope.
5. **UQC-209**, holonight-settings: L01; **UQC-210**, holonight-ai: L02;
   **UQC-211**, holonight-shell: S01/S02; **UQC-212**, holonight-greeter: G01–G06.

Packages 205–212 are Planned investigation/repair packages, not Ready assignments.
Each needs its own local SDD, exact canonical baseline and reproduction before work
starts. F05 and C01–C06 remain umbrella investigations until ownership is settled.
