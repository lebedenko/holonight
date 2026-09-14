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
| C02 — Tokodon Fusion Switch extends past row | **Not fixable within HoloNight: same upstream composition/sizing incompatibility.** Installed FormSwitchDelegate uses a zero-padding, null-content Controls.Switch. A new stock-Fusion offscreen fixture at actual DPR 1 and 1.25 reproduces control width 0, indicator width 40/x=-20. In a 400-wide row, the content starts at 12 and the switch at content x=376: indicator right edge is 408, eight pixels outside the row. No HoloNight QML override is required to reproduce this. |
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

Actual-app visual acceptance remains pending. See
[RENDERING-BATCH3.md](RENDERING-BATCH3.md) for the five scale-1 runs, including the
NeoChat uninstrumented comparison and Fusion reference. UQC-201/UQC-207 remain
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
`post-restoration.json`. Actual-app results for the five README runs remain pending.
