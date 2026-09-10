> Current checkpoint: broad manual acceptance is paused for repairs. Use the
> [canonical findings register](FINDINGS.md) for current status. The batch requests
> below are historical; the next request is limited to repaired Settings/AI focus
> using a fresh kit after the published UQC-204 handoff.

# UQC-201 guided acceptance

Preparation baseline: `7fcc8bb48a451185b9412950ac7f651ee75975c7`.
Initiative **Accepted**; UQC-201 **In Progress**. Settings focus visibility failed
(UQC-204); remaining manual acceptance is pending.
The real pre-session greeter gate remains separate from demo observations.

## Accessible kit

Current kit: `/tmp/holonight-uqc201-8r1jtlln`, configured directly with installation
prefix `/tmp/holonight-uqc201-8r1jtlln/prefix`. Build records are in
`.cache/uqc201-guided-qht3_tjs`. The older relocated kit and its evidence remain
historical. This temporary kit must be rebuilt if removed or installed Qt changes.
The `READY` marker is written only after preparation checks pass.

Reboot recovery on 2026-09-10 restored this same configured path from the surviving
verified build outputs and regenerated helpers. Qt package versions and product
pins are unchanged. Recovery checks are recorded in TASKS.md; this is not a new
full integration run. Resume with Settings default at Qt scale 1.25, inspecting
layout, text editing, scrolling and selectors, then review observations before
the Fusion run. UQC-204 remains open; do not repeat its sequence to establish it again.

The kit contains [the session launcher](guided-session.py),
[application/evidence helper](guided-app.py), minimal compositor configurations,
guarded authentication helpers, package/revision inventory, and prefix hashes.
The [kit preparation script](prepare-guided-kit.py) copies the pinned provider
helpers and applies the reviewed [owned-agent adaptation](owned-auth.patch).
The launcher verifies its own real logind ownership before starting a compositor.
It creates disposable XDG directories under `~/uqc-guided-evidence`, disables all
configured AI providers/title generation, and selects a disposable appearance
file. It sets prefix discovery before `dbus-run-session` creates the test bus.
It does not import anything into a systemd manager. No agent autostarts.

## Batch 1: Hyprland login and Settings default

Save work and use a spare VT to log in directly as **tux**. Do not use sudo, su,
SSH or a nested compositor. From that VT:

```sh
python3 /tmp/holonight-uqc201-8r1jtlln/guided-session.py hyprland
```

In the terminal opened by the minimal compositor:

```sh
printf '%s\n' "$UQC_SESSION_RUN"
python3 "$UQC_KIT/guided-app.py" settings
```

At scale 1, inspect the initial page, traverse with Tab/Shift+Tab, edit and erase
disposable text in an available field, scroll a page, and open/close a selector.
Do not change system settings. Report which controls/pages were exercised,
visible focus, clipping or popup issues, and the printed evidence directory.
Close Settings yourself. Review these observations before starting batch 2.

Super+Enter opens another test terminal; Super+Q closes the focused window;
Super+Shift+E exits the compositor. All keyboard, pointer and focus interactions
are user-operated. Log tux out after each compositor run.

## Subsequent batches (issue individually after review)

1. Settings Fusion and scale 1.25; owned AI/package-manager defaults and Fusion,
   editing/navigation/scrolling/popups. Use `guided-app.py ai`, `packages`, or
   `settings`, with `--style Fusion` and/or `--scale 1.25`. Never send AI requests
   or apply package transactions. For shell use `guided-app.py shell` in the
   minimal compositor; inspect menus/sidebar/launcher without power/session actions.
2. Haruna, NeoChat, Tokodon: `guided-app.py haruna`, `neochat`, or `tokodon`.
   Third-party default explicitly selects Holonight; owned default leaves overrides
   unset. Exercise the logged-out [manual matrix](MANUAL.md), repeating at scale
   1.25. Open the kit's `sample.mp4` manually in Haruna; no sign-in or browser authorization.
3. Available application palette selectors: dark → light → dark, reopen controls.
   Settings' appearance selection targets the disposable `HOLONIGHT_APPEARANCE_FILE`.
   Preserve HoloNight, named fallback, application-owned and blocked classifications;
   Haruna painted sliders/Fusion and accepted Kirigami composition limitations remain
   explicit. Absence of a selector is recorded with its scope, not a visual pass.
4. Activation: terminal, desktop launcher, D-Bus and systemd where supported.
   Close each previous instance manually. Inspect installed desktop/service metadata
   first, then correlate the actual PID using `guided-app.py collect --pid PID`.
   Retain launch/journal control-origin lines; library loading alone does not prove
   a particular created control. Haruna has desktop metadata but no installed D-Bus
   service. NeoChat and Tokodon each have a service under `/usr/share/dbus-1/services`.
   An ad hoc `systemd-run` is a transient execution route, not a product-shipped unit.
5. Authentication: follow [AUTHENTICATION.md](AUTHENTICATION.md), separate agent
   runs, registration PASS before cancellation-only challenge. Third-party and
   owned agents never run together. Owned askpass is independent of Polkit.
6. Greeter: `guided-app.py greeter`, repeated at scale 1.25 and Fusion. Only demo
   mode is launched. Inspect selector geometry near edges and selected/first/last
   row reachability. Record **demo**; leave real pre-session acceptance unchecked.
7. Exit and log out tux. Start a fresh tux VT login and repeat batches in Sway:
   `python3 /tmp/holonight-uqc201-8r1jtlln/guided-session.py sway`.

The scale option changes Qt's process scale, with compositor output scale 1.
Record both values. If compositor output scaling is also required, the user
changes it manually and records the resulting pair; do not multiply both silently.

## Activation environment review

The test bus starts with the prefix in `XDG_DATA_DIRS`. After compositor startup,
review the verified socket-peer environment:

```sh
"$UQC_PREFIX/libexec/holonight-wayland-session-environment" \
  "$XDG_SESSION_ID" "$XDG_RUNTIME_DIR" | tr '\0' '\n'
```

In the **tux test login only**, after reviewing identity and ensuring no other tux
graphical login uses its user manager, propagate the actual compositor connection
to the test bus. Keep default selectors unset for owned default checks:

```sh
dbus-update-activation-environment WAYLAND_DISPLAY DISPLAY XDG_SESSION_ID \
  XDG_RUNTIME_DIR PATH XDG_DATA_DIRS XDG_CONFIG_HOME XDG_DATA_HOME XDG_CACHE_HOME \
  XDG_STATE_HOME XDG_CONFIG_DIRS HOLONIGHT_APPEARANCE_FILE QML_IMPORT_PATH \
  QT_PLUGIN_PATH LD_LIBRARY_PATH QT_QPA_PLATFORM QT_QPA_PLATFORMTHEME \
  QML_IMPORT_TRACE QT_DEBUG_PLUGINS QT_FORCE_STDERR_LOGGING QT_LOGGING_RULES
```

Import those same named variables plus `DBUS_SESSION_BUS_ADDRESS` into tux's
systemd user manager only for the systemd batch, after reviewing its existing
selected environment. This is a separate explicit guided step; no session helper
does it automatically. Never import test paths into the normal desktop's manager.
Record effective unit environment and actual PID; inspect selected journal lines.
Before leaving that batch, restore the selected manager variables to their
recorded values (unset only variables absent before the batch). Do not dump or
publish unrelated environment values. Authentication always runs from the test
terminal, where actual logind session membership is preserved.

## Evidence review

For each result record date, compositor/package/Qt versions, compositor and Qt
scale, executable/entry point, selector environment, surface/state, user action,
outcome, created implementation origin, loaded native libraries and local evidence
reference. Recollect the PID after opening lazily loaded pages. Authentication
frontends may intentionally deny `/proc` inspection through `PR_SET_DUMPABLE=0`;
record that limitation and use direct-child/session/registration and origin logs.

Raw evidence stays in the tux home. Review personal data before sharing selected
diagnostics; do not publish complete authentication logs. No manual result is
inferred from an automated fixture. Newly found product defects require separate
repository-owned work packages and local SDDs at these exact pins.

| Reviewed batch | Compositor / scale | Outcome / classification | Evidence |
|---|---|---|---|
| Settings initial keyboard traversal, reported 2026-09-10 | Hyprland; requested Qt/output scale 1/1, embedded default | Failed observation: Tab/Shift+Tab show no focus; Space/Enter have no observed effect. Page, window focus and text-entry behavior await clarification; implementation origin/logs not yet reviewed. | User-reported `hyprland-cwas_0je/settings-1788998056392643199` under `/home/tux/uqc-guided-evidence/` |

Before this application run, the user reported a frozen VT3 after switching away
and back; the session subsequently recovered. Supplied log excerpts show DRM VT
restoration and a later seat deactivation, but do not establish the freeze's cause
or a causal connection to the Settings keyboard result. The test session's private
bus also reports failed systemd activation attempts. These are unresolved session
observations, not accepted activation evidence. Keep raw logs private and preserve
both observations when diagnosing the application result.

Follow-up on the same Settings run: clicking Weather's City field gives visible
focus; typing and erasing work. Tab removes the visible indicator; repeated Tab
eventually restores it, with intermittent gaps. The user tentatively observes
correct traversal order. Text entry works, while keyboard focus visibility fails;
traversal order is not independently verified. An offscreen provider probe
reproduces loss of `visualFocus` when `HnSettingsRow` forwards keyboard focus to a
ComboBox, in both Holonight and Fusion. See the UQC-204 finding in TASKS.md.


### Settings continuation observations — 2026-09-10

User reports the following after the requested restored-kit Hyprland default run
at Qt/output scale 1.25/1. Actual run path, selector/scale and origin logs await
correlation; the requested launch context is not independently verified.

- Slider handle press/drag shrinks the slider width and immediately changes its
  value. The control remains operable but is difficult to use. The user suspects
  the containing layout; exact slider/page and root cause remain unconfirmed.
- Appearance dropdown rows disappear as the pointer crosses them; clicking the
  now-empty positions does nothing. Weather dropdowns work in this respect.
  The user suspects dropdowns requiring scrolling; this boundary is not yet
  independently established. This is an interaction failure, not an accepted
  text-color-only explanation.
- Across tested ComboBoxes, opening does not focus the selected item. Choosing
  an item or clicking the collapsed-control area closes the popup, but clicking
  outside does not. Selected-row visibility, highlighting and keyboard focus
  need separate checks. Follow-up confirms Escape closes the HoloNight popup.

These are failed observations, not new manual passes. UQC-204 remains open.
Next comparison: Settings Fusion at scale 1.25, same affected surfaces, after
closing the default instance. Retain both evidence directories and name the
specific sliders/dropdowns. Do not change the kit during this comparison.

### Fusion comparison follow-up — 2026-09-10

The user reports Fusion controls work much better, with only two remaining
observations: expanded ComboBox rows have no visible hover effect, and ComboBox/
button text has small padding. The user explicitly classifies padding as an
appearance preference, not a defect. Record missing hover feedback for triage;
do not infer its cause or require Fusion to reproduce HoloNight spacing.

The earlier slider/popup interaction failures were not reported in this Fusion
comparison. This is comparative user evidence, not an instrumented per-control
pass or proof of provider ownership. Exact sliders and both evidence directories
remain pending. Escape dismissal under HoloNight is confirmed by the user;
outside-click dismissal remains failed. UQC-204 remains unresolved.

Next guided surface: AI default at Qt scale 1.25 in the same prepared session.
Exercise unsent composer editing, navigation, scrolling and available selectors;
do not send requests or enter credentials. Review before its Fusion comparison.


### AI provider-form observations — 2026-09-10

User tested AI Settings → providers after the requested default-style launch at
Qt/output scale 1.25/1. Evidence directory and actual selector/origin/scale
correlation remain pending. Context window/Temperature labels match the Ollama
form in source; provider identity has not been explicitly confirmed by the user.

1. Tab/Shift+Tab move in the expected directions, but focus feedback intermittently
   disappears, including focused ComboBoxes. The user suspects traversal through
   disabled controls; this is unconfirmed, not an established disabled-control stop.
2. A keyboard-focused button has a ring; Space successfully activates its action,
   but the ring disappears while focus appears retained. Tab then Shift+Tab restores
   the ring. Exact button/action and actual focus owner are not yet recorded.
3. A slider appears as only a knob with no track, apparently reduced to knob width.
   The user suspects layout; measured geometry and root cause remain pending.
4. Forward sequence: Context window value → invisible focus stop → Temperature
   value → Temperature slider. Reverse: Temperature slider → Temperature value →
   Context window value. Repeating forward reproduces the invisible stop. A hidden
   element is suspected, not identified; retain the direction asymmetry explicitly.
5. After switching from the tux VT3 to VT1 and back, the settings window/control
   appears to retain focus, but Tab/Shift+Tab do nothing until a mouse click on a
   control restores traversal. Track separately as a VT-return/input observation;
   compositor keyboard focus, application focus and event delivery are unverified.
   Do not equate this with the earlier VT freeze or infer a common cause.

No AI provider-form acceptance pass is recorded. Next comparison is AI Fusion at
Qt scale 1.25 in the same prepared session, after closing the default AI instance.
Compare the same form's traversal, slider and ComboBox states. VT switching need
not be repeated to establish the report. Keep providers disabled, enter no
credentials, and do not trigger refresh/test-connection or send requests.


### AI Fusion comparison and Switch feedback — 2026-09-10

User confirms identical Tab/Shift+Tab behavior in Fusion, including disappearing
focus feedback and the asymmetric Context window/Temperature traversal sequence.
ComboBox clarification applies to BOTH styles: the first traversal reaches the
ComboBox without visible focus feedback, the next full Tab cycle highlights it,
and subsequent forward/reverse traversal no longer reproduces the missing ring.
Preserve this first-cycle condition for reproduction; do not describe that specific
ComboBox symptom as indefinitely intermittent. Other focus findings remain open.

Fusion renders the Temperature slider with both track and knob, but the track is
still too short. The user attributes the short track to AI layout. This narrows
the comparison without establishing measured widths or the cause of HoloNight's
knob-only rendering. Overall user assessment: Fusion UI/UX feels better.
The button-after-Space and VT-return findings were not separately resolved by
this comparison. Disabled-control traversal remains unconfirmed.

New Switch observation: Fusion provides visible feedback in both off/on states;
HoloNight provides it when off but not visibly when on. In the keyboard-navigation
context, provisionally interpret this as focus feedback, pending clarification
if the user meant hover or another state. The user suspects an existing indicator
is obscured by the design, rather than absent. Do not record a functional toggle
failure or a proven contrast cause. Exact Switch and evidence reference are pending.

Next batch: close AI and launch package-manager default at Qt scale 1.25. Inspect
search editing, keyboard navigation, scrolling and available menus/selectors;
do not install, remove or update packages. Review before the Fusion comparison.


### Package-manager default observation — 2026-09-10

User reports no issues observed after the requested package-manager default batch
at Qt/output scale 1.25/1 in the prepared Hyprland session. Record a positive user
observation for the exercised surfaces, not exhaustive application acceptance.
Exact exercised controls and the run's evidence directory/origin correlation are
pending. No package transaction result is claimed.

Next: close package-manager and compare Fusion at Qt scale 1.25, inspecting the
same search editing, keyboard navigation, scrolling and available menus. Do not
install, remove or update packages. Review before continuing to shell surfaces.


### Package-manager Fusion observation — 2026-09-10

User reports no issues in the requested Fusion comparison at Qt/output scale
1.25/1. Both package-manager styles now have positive user observations for the
exercised surfaces; evidence-directory/origin correlation remains pending. This
does not complete other scales, compositor, activation or integration gates.

Next: close package-manager, then launch shell default at Qt scale 1.25 in the
prepared minimal Hyprland session. Inspect panel menus/popups, sidebar, launcher
search editing, keyboard navigation and scrolling. Do not invoke power/session
actions. Review before the shell Fusion comparison.


### Shell default failure — 2026-09-10

User reports shell is largely unusable after the requested default-style launch
at Qt/output scale 1.25/1 in the minimal Hyprland session:

- Initially only logo, workspaces and active window render; statuses and date/time
  are absent.
- Hover/click makes the bar shrink slightly in height and missing right-side
  sections appear to slide in from the screen's right edge.
- Mouse interaction produces continual jitter and right-side sections sliding
  in/out; nothing appears clickable.
- Some tooltips still appear for logo, workspaces and active window.
- Reserved/exclusive space appears constant. The initially taller bar overlaps
  the console slightly; after shrinking, the gap above the console appears
  consistent with its other three margins. These are visual observations, not
  measured surface dimensions or exclusive-zone state.

Treat this run as a failed shell usability observation; menu/sidebar/launcher
acceptance could not proceed. Actual run directory, logs and process/scale/origin
correlation are pending. Next diagnostic comparison changes only Qt scale to 1,
retaining default style and the same compositor. Stop the current helper with
Ctrl+C in its launching terminal before starting the comparison; do not run two
shell instances. No need to keep interacting with the unstable bar.


### Shell default scale-1 comparison — 2026-09-10

At requested Qt/output scale 1/1, user reports a fully functional shell: no jitter
or incorrect interaction, with all exercised popups functioning/rendering properly.
This is positive interaction evidence at scale 1, not resolution of the failed
scale-1.25 run or an exhaustive shell acceptance pass. Remaining topbar visuals:

- Logo, workspaces and active-window frames have correct top/bottom/left edges
  but missing/broken right edges.
- Status-frame left/right end regions, approximately the content-padding width,
  appear correct. Network/audio/battery appear as a solid block covering the
  frame's top/bottom borders; keyboard layout also has a solid background covering
  the frame and bar background. Preserve the user's described three gaps without
  inferring an exact pixel grouping.
- Notification bell appears correct: transparent widget background, visible bar
  gradient and top/bottom frame edges. Date/time is also correct.
- User is uncertain whether the underlying entire status frame is correct;
  distinguish overpainting from a proven missing frame path.

Run/evidence correlation remains pending. Next comparison: stop the default shell
with Ctrl+C in its launching terminal, then run Fusion at Qt scale 1. Compare the
same frame edges and status backgrounds, plus popup usability. Do not run two
shell instances. The scale-1.25 failure remains open independently.


### Shell Fusion scale-1 comparison — 2026-09-10

User observes no topbar rendering or functional difference from HoloNight at scale
1: the same frame/background defects persist, with no additional issues. Sidebar
Overview's indeterminate ("infinite") progress bar has Fusion styling. Record that
appearance difference without inferring a new stuck-loading or progress failure.
The unchanged topbar defects under both selectors strengthen the case for reviewing
shell composition, but do not establish a root cause. Fusion at scale 1.25 remains
untested; the HoloNight scale-1.25 failure remains open. Evidence paths/origins are
still pending, and this does not close the full shell acceptance gate.

Next batch: stop shell using Ctrl+C in its launching terminal, then run Haruna with
helper default selection (Holonight) at Qt scale 1. Open the kit's sample.mp4 and
inspect playback/seek/volume, menus, settings controls, keyboard focus and scrolling.
Haruna's application-painted sliders and explicit Fusion fallback remain accepted
classification boundaries; visual difference alone does not establish a defect.
Review before the scale-1.25 comparison.


### Haruna default scale-1 observations — 2026-09-10

User reports Haruna is almost fine in the requested Holonight run at Qt/output
scale 1/1, with these scoped observations:

- ComboBox outside-click dismissal still fails. The long scrollable font selector
  works without the disappearing/noninteractive rows seen in Settings. This is
  evidence against treating every scrollable ComboBox as broken; it does not
  resolve the Settings-specific observation or establish the cause.
- File and color pickers mix light surfaces with mostly dark controls; file-picker
  path breadcrumbs appear as dark badges on a light background. User calls these
  Qt pickers; actual dialog implementation/backend and palette origins are pending.
- Settings → Mouse → Add action opens a popup with two orange/yellow rounded
  warning boxes whose small-radius corners look imperfect/broken. Select action
  looks HoloNight-styled; bottom OK/Cancel look different, possibly Fusion. These
  are visual impressions, not verified control origins. The user suspects Haruna
  ownership; retain warning geometry separately from the mixed-style observation.
- Settings help/info buttons can leave several help popups open at once. The user
  prefers opening one to close others, but suspects application logic. Record as
  a behavior/preference observation pending classification, not a proven provider
  failure or an accepted exclusivity requirement.

Haruna's explicit Fusion fallback and deferred Dialog/DialogButtonBox coverage
are accepted boundaries. They make mixed implementations plausible, but do not
prove the origins of these buttons or excuse the mixed light/dark palette finding.
Exact run/origin references remain pending; no complete Haruna pass is recorded.

Next comparison: close Haruna, then launch explicit Fusion at Qt scale 1. Revisit
file/color pickers and Mouse → Add action, comparing palette consistency, warning
corners and outside-click dismissal. Cancel dialogs without saving a new action.
Review before the still-pending Holonight scale-1.25 batch.


### Haruna Fusion comparison / missing icons — 2026-09-10

User reports file/color pickers consistently dark under Fusion and ComboBox
outside-click dismissal working. Mouse → Add action warning-box corners have the
same defect as HoloNight. Fusion menus/ComboBox dropdowns still lack visible hover
feedback; retain the earlier observation. No other new Fusion issues reported.
This leaves HoloNight picker palette mixing and outside-click dismissal unresolved;
warning corners are a both-style issue, not a proven Haruna-owned cause.

New comparison: Fusion shows icons in player top-menu items and Settings navigation,
where HoloNight does not. HoloNight top-menu dropdowns reserve excessively large
empty left space; Settings navigation has neither icons nor corresponding space.
The report calls Settings navigation left sidebar first and right sidebar later;
record it as Settings navigation pending exact surface/evidence correlation.

User-requested menu layout requirement: each dropdown independently reserves a
shared icon column if at least one of its items has an icon, aligning all item
texts whether or not individual items have icons. With no icons in that dropdown,
omit the icon column and its extra spacing. Preserve ordinary edge padding and
necessary checkmark/submenu affordances; do not conflate those with empty icon space.
This is a recorded repair requirement, not an implemented change or closed gate.

Next: close Haruna and return to helper default Holonight at Qt scale 1.25. Check
whether font-list scrolling, popup placement, playback/settings interaction or
clipping develops any additional scale-specific issues. Known defects need not be
repeated to establish them. Review before moving to NeoChat.


### Haruna scale-1.25 / persistent first-row background — 2026-09-10

Following the requested scale-1.25 run, user reports otherwise unchanged behavior,
with Mouse → Add action warning corners still defective but less noticeable at
1.25. Interpret the repeated scale wording as comparison with the prior scale-1
run, based on the explicit 1.25 distinction; actual run/scale correlation remains
pending. No additional scale-specific failure is reported.

New HoloNight finding applies at both tested scales: list-based Settings pages,
explicitly Shortcuts, permanently paint the first row like a selected item.
Clicking other rows or changing their settings does not move that background.
Hover highlights the row under the pointer independently. User found no action
that moves the persistent first-row background. This is an unexplained selection
visual, not proof that interaction or the underlying application selection fails.
Fusion has no persistent first-row background; rows briefly highlight on click,
with no visible hover feedback, consistent with previous Fusion observations.

Next batch: close Haruna, then launch NeoChat default Holonight at Qt scale 1.
Inspect logged-out welcome/server forms, type/select/erase example.invalid where
available, Tab/Shift+Tab, back navigation and reachable popups/scrolling. Do not
sign in or submit an account/server connection. Review before scale comparison.


### NeoChat logged-out Settings / palette transition — 2026-09-10

User has no account and inspected Settings in the requested Holonight scale-1
run. Only the already recorded ComboBox outside-click dismissal failure was
observed in those interactions. Account-dependent surfaces were not tested;
no full NeoChat acceptance is claimed.

Additional appearance sequence: main window initially renders dark, but in colors
the user describes as NeoChat's own rather than any HoloNight scheme. Settings
opens on General with the same initial colors. Clicking another Settings page
recolors the application into the current HoloNight scheme; after closing Settings,
the main window is also recolored. No explicit theme-selection action was reported.
Exact destination page, before/after palette values and lazy control origins are
pending. Record the navigation-triggered transition without assuming that the
initial application palette was invalid or the final palette necessarily correct:
the contract must preserve application/control palette overrides.

Next comparison: fully close NeoChat, then launch Fusion at Qt scale 1. Observe
initial main/General colors and switch to the same Settings page, noting whether
the palette transition recurs and which page triggers it. Compare ComboBox outside
click. No account is needed. The helper retains the session's disposable profile;
this is a restart/style comparison, not a guaranteed fresh-profile reproduction.
Review before the pending Holonight scale-1.25 batch.


### NeoChat Fusion follow-up — 2026-09-10

User confirms the same navigation-triggered recoloring under Fusion. This rules
out treating the observation as exclusive to the selected Holonight style, but
does not establish application, platform-theme or shared-component ownership.

Additional observations in this Fusion comparison:

- CheckBox/RadioButton indicators have no gap before their labels/titles. Exact
  pages/controls and whether the same spacing occurs under HoloNight are pending.
- Appearance → color scheme ComboBox expands to occupy all available vertical
  space. User did not report clipping, unreachable rows or inability to scroll;
  record its extent as an observation, not a confirmed overflow failure.
- This dropdown highlights rows on hover, unlike the earlier Haruna Fusion
  dropdown observations. Do not generalize missing hover feedback to all Fusion
  ComboBoxes.
- The collapsed control clearly looks Fusion to the user, while the popup looks
  similar to HoloNight. This is a visual comparison, not verified mixed-style
  origins. Application-owned delegates/palette and shared components remain
  possible explanations requiring actual control-origin evidence.

Outside-click dismissal for this NeoChat Fusion run was not explicitly reported;
keep that comparison pending. Next: fully close NeoChat, launch default Holonight
at Qt scale 1.25, and inspect the same checkbox/radio spacing and color-scheme
popup, including first/last row reachability, scrolling and placement/clipping.
No need to repeat the palette transition. Review before Tokodon.


### NeoChat Appearance palette toggle clarification — 2026-09-10

User reports the same observed result at Holonight scale 1.25 as at scale 1.
Further investigation, also rechecked under Holonight scale 1 and Fusion scale 1,
identifies a repeatable two-scheme toggle. This supersedes the earlier unspecified
"other Settings page" trigger and one-time-initialization interpretation:

1. Launch app: initial non-HoloNight-looking scheme, described by user as wrong.
2. Open Settings: same initial scheme. Visit any page other than Appearance:
   no palette change.
3. Open Appearance: changes to the current HoloNight-looking scheme. Close Settings:
   main window retains the changed scheme.
4. Reopen Settings and visit other pages: no change. Open Appearance: changes back
   to the initial non-HoloNight-looking scheme.
5. Repeating the close/reopen/page sequence toggles between these two schemes each
   time Appearance is opened, without a reported explicit scheme-selection action.

This is not merely delayed initial styling: record a repeated navigation-triggered
palette mutation affecting both windows. Reproduction is user-operated in the three
specified style/scale combinations; exact palette values, settings persistence,
control origins and cause remain uninstrumented. The description does not establish
whether leaving/reentering Appearance without closing Settings also toggles it.
Other observations from the preceding scale comparison remain unchanged; no new
scale-specific failure is reported. The account-dependent matrix remains untested.

Next batch: close NeoChat, then launch Tokodon default Holonight at Qt scale 1.
Inspect logged-out Settings if available, welcome/server form editing, keyboard
navigation, reachable menus/popups and scrolling. Do not sign in or submit a server
connection. Report unavailable account-dependent surfaces rather than creating an
account. Review before the scale comparison.


### Tokodon default scale-1 findings — 2026-09-10

User reports the following in the requested Holonight scale-1 run:

- Exactly the same repeated palette-toggle behavior as NeoChat, but Tokodon's
  first Settings page is Appearance, so opening Settings immediately triggers
  recoloring. NeoChat initially opens General and toggles on visiting Appearance.
  Preserve this as a cross-application reproduction; common ownership/cause is
  not yet established.
- Font picker mixes a light main background with otherwise dark content/controls.
  Record a palette-consistency failure separately from button style differences.
- Font-picker controls look HoloNight-styled, while OK/Cancel look neither
  HoloNight nor Fusion. The user recognizes a resemblance to controls seen when
  importing QtQuick.Controls.Basic in other applications. This is a visual
  hypothesis, not verified Basic imports, fallback selection or actual origins.

Actual dialog backend, palette roles, button implementation origins and evidence
path remain pending. Basic fallback exists in the accepted provider contract, but
its presence does not establish this dialog's implementation or excuse mixed
light/dark surfaces. No full Tokodon acceptance pass is recorded.

Next: fully close Tokodon, then launch Fusion at Qt scale 1. Compare repeated
Settings opening/recoloring and the font-picker background and OK/Cancel buttons.
Cancel font selection without applying a change. The disposable application profile
is retained across helper launches. Review before Holonight scale 1.25.


### Tokodon Fusion scale-1 findings — 2026-09-10

User confirms the same recoloring toggle under Fusion and reports the same
ComboBox/RadioButton/CheckBox issues as in the NeoChat Fusion comparison. Link this
to the prior report (indicator-to-label spacing and color-scheme popup observations)
without inventing new per-control details or treating dropdown appearance as proof
of an implementation origin. Font-picker palette/button comparison was not
separately resolved in this reply.

Additional concrete layout failure: Settings sections are enclosed in boxes with
one row per setting; title/description are left-aligned and the Switch is aligned
right. The Switch extends partially past the section's right boundary. Record
right-side containment failure, not measured indicator clipping or a proven
control-width/root-layout cause. Exact setting/section, overflow amount and whether
this occurs under HoloNight remain pending. No full Tokodon pass is recorded.

Next: fully close Tokodon, then run default Holonight at Qt scale 1.25. Inspect the
same boxed Switch rows and checkbox/radio spacing, font picker and dropdown
placement/scrolling. Report additional scale effects and whether Switch overflow
also occurs in HoloNight; no need to repeat the established recoloring sequence.


### Tokodon scale-1.25 / picker palette-state clarification — 2026-09-10

User reports no difference from the Holonight scale-1 run. This does not separately
confirm that Fusion's Switch overflow occurs under HoloNight; preserve the
style-specific report until clarified or measured.

User further narrows mixed light/dark picker rendering: it appears when the
HoloNight-looking color scheme is currently applied. When the initial alternate
scheme (described by the user as wrong) is applied, pickers look consistent with
that application scheme. Treat this as a user-observed correlation/hypothesis,
not a measured causal conclusion or an exhaustive recheck of every earlier picker.

Keep selected Controls style separate from the application palette state in future
reproductions. Compare the same picker before/after Appearance-triggered toggles,
recording actual palette roles and control origins. Earlier style comparisons
alone do not isolate the picker problem if palette state also changed. This
clarification refines rather than erases the original light-background reports.

Next guided batch moves to greeter demo at default style/Qt scale 1 in this test
session. Close Tokodon first. Inspect selectors, keyboard navigation, popup edge
placement and selected/first/last item reachability. Demo checks do not exercise
real login. Activation, palette round-trip, isolated authentication, real pre-session
greeter and Sway checks remain pending; none is bypassed by this batch ordering.


### Greeter demo default scale-1 findings — 2026-09-10

User reports generally working keyboard navigation and correct popup placement,
with the specific exceptions below. This is demo evidence only, not real login.

- Session dropdown rows disappear on hover; clicking their former positions does
  not select them. Up/Down on the collapsed selector can select sessions. Symptom
  matches prior Settings dropdown observations, but shared cause is unverified.
- Keyboard-layout selector is correctly disabled because no choice is configured,
  but its color looks unlike the disabled palette and it exposes a hover state.
- Password reveal works with mouse, but Space does not activate it, preventing
  equivalent keyboard-only use. Exact focus/press lifecycle remains uninstrumented.
- Password-field background seems outside the theme palette; user explicitly asks
  for clarification. Record as an unverified palette concern, not a proven color bug.
- Reboot/poweroff buttons should have transparent backgrounds in their normal state.
  Reboot icon size looks correct; poweroff looks too small. Record requested visual
  corrections, not a failure of the power actions, which need not be activated.
- User selector is a small regular dropdown; user requests the existing avatar-based
  user-selector component. Component identity/API must be located before adoption.
- User selector is absent from the Tab/Shift+Tab cycle. Retain this exception to
  the general positive keyboard observation.

Next: close demo and compare Fusion at Qt scale 1. Inspect session-dropdown hover/
selection, disabled layout-selector appearance, user-selector reachability and
password reveal with keyboard focus and Space held/released (hold-to-reveal label).
Use only disposable text. Inspect power buttons without triggering their actions.
Review before the still-pending demo scale-1.25 batch.


### Greeter demo Fusion scale-1 comparison — 2026-09-10

User reports the same issues except selector behavior differs:

- Session selector works with mouse and keyboard under Fusion, without visible
  hover feedback. The disappearing/noninteractive rows from HoloNight are not
  reported in this comparison.
- User selector is unusually large, has no visible hover feedback, but works
  properly when used. "Large" is user-described; whether this concerns the popup,
  collapsed control or both and exact geometry remain pending. Functional use does
  not explicitly establish inclusion in the Tab cycle, so the earlier reachability
  finding remains unresolved.
- Other previously reported greeter concerns persist by the user's general
  comparison. No separate successful password-reveal keyboard result was supplied.
  Disabled layout-selector and visual requests remain open; exact differences
  beyond the enumerated selectors are not inferred.

Next: close demo, then launch default Holonight at Qt scale 1.25. Check popup edge
placement, selected/first/last-item reachability and additional clipping or sizing
changes. Do not repeat broken mouse selection merely to establish the defect;
use keyboard selection where it works. Demo evidence does not close real-login
acceptance. Review before proceeding to the remaining integration gates.


### Greeter demo scale-1.25 follow-up — 2026-09-10

User reports the same behavior as Holonight scale 1; no additional scale-related
difference observed. Existing selector, keyboard and appearance findings remain
open. This does not establish missing first/last-row evidence or real-login
acceptance. Fusion scale 1.25 has not been reported.

Next guided step: close greeter demo and run the third-party authentication helper
preflight in the same prepared tux compositor terminal. This collects identity,
process/service/registration/policy/version/linkage evidence only; it starts no
agent or challenge. Review that evidence before any agent launch, following
AUTHENTICATION.md. Application evidence/origin correlation, remaining scale/style
combinations, activation, palette round trips, authentication, real pre-session
greeter and Sway gates remain pending. The application round is not integration.


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


### Hyprland evidence correlation — 2026-09-10

Reviewed `/home/tux/uqc-guided-evidence/hyprland-j97jound` using authorized sudo -A.
Session-start identity records active local tux UID 1001 on seat0/tty3, session 5,
Type=tty before compositor launch (later auth preflights correctly record wayland).
Package versions match preparation. All 35 application run directories have saved
PID metadata identifying session 5 and the configured prefix QML discovery path.
Below are observed process selectors/scales and exits, not inferred visual passes.
Repeated same-mode launches are retained; exact action-to-run mapping may need
user clarification. Extra launches do not imply unreported manual coverage.

| Run directory | Process selector | Qt scale | Exit |
|---|---|---|---|
| `ai-1789029827393494892` | unset (owned default) | 1.25 | -2 |
| `ai-1789039726877575859` | Fusion | 1.25 | 0 |
| `greeter-1789058727907759472` | unset (owned default) | 1 | 0 |
| `greeter-1789058812830401738` | unset (owned default) | 1 | 0 |
| `greeter-1789058971398081985` | unset (owned default) | 1.25 | 0 |
| `greeter-1789059113141965834` | unset (owned default) | 1 | 0 |
| `greeter-1789063481495648502` | Fusion | 1 | 0 |
| `greeter-1789063870457038871` | Fusion | 1 | 0 |
| `greeter-1789064051717081618` | unset (owned default) | 1.25 | 0 |
| `haruna-1789046055724363325` | Holonight | 1 | -6 |
| `haruna-1789046765881014589` | Holonight | 1 | 0 |
| `haruna-1789047213269150559` | Fusion | 1 | 0 |
| `haruna-1789047421225401860` | Holonight | 1 | 0 |
| `haruna-1789048160079561569` | Holonight | 1.25 | 0 |
| `haruna-1789048345874786675` | Holonight | 1.25 | 0 |
| `haruna-1789048416038048394` | Fusion | 1.25 | 0 |
| `haruna-1789048637456615845` | Holonight | 1.25 | 0 |
| `neochat-1789049416816987086` | Holonight | 1 | 0 |
| `neochat-1789049563189437097` | Holonight | 1 | 0 |
| `neochat-1789049590074525770` | Holonight | 1 | 0 |
| `neochat-1789050011917160574` | Fusion | 1 | 0 |
| `neochat-1789051163949026488` | Holonight | 1.25 | 0 |
| `neochat-1789051301383353425` | Holonight | 1 | 0 |
| `neochat-1789051364309116433` | Fusion | 1 | 0 |
| `packages-1789042398011866057` | unset (owned default) | 1.25 | 0 |
| `packages-1789043178488902086` | Fusion | 1.25 | 0 |
| `settings-1789028516227886243` | unset (owned default) | 1.25 | 0 |
| `settings-1789029437210147970` | Fusion | 1.25 | 0 |
| `shell-1789043332736844309` | unset (owned default) | 1.25 | -2 |
| `shell-1789043358759673832` | unset (owned default) | 1.25 | -2 |
| `shell-1789044030016687898` | unset (owned default) | 1 | -2 |
| `shell-1789045734425254874` | Fusion | 1 | -2 |
| `tokodon-1789051831779114065` | Holonight | 1 | 0 |
| `tokodon-1789052797977773434` | Fusion | 1 | 0 |
| `tokodon-1789058003039539682` | Holonight | 1.25 | 0 |

Private derived summary and extraction script:
`.cache/uqc201-guided-qht3_tjs/review-20260910/session-summary.json` and
`/tmp/uqc-review-j97jound.py`. The summary contains selected launch metadata,
file-based import/plugin paths and counts of selected QML error markers, not raw
logs or application data. It does not yet correlate every qrc-created control or
review saved process maps. Shell launch logs yielded no matching origin paths;
no visual origin pass is inferred from environment alone.

Selected source-location diagnostics directly reviewed:

- Settings default has 12 popup implicitHeight binding-loop reports at
  `qrc:/qt/qml/Holonight/ComboBox.qml:109:12`; its Fusion run has none of the scanned
  error markers. NeoChat and Tokodon default logs also report that provider popup
  height loop. This is runtime evidence, not proof it causes disappearing rows.
- First Haruna run exits -6 (SIGABRT), while later runs exit 0. Its log includes
  ImageAdjustmentSlider.qml assigning nonexistent activeControl, Main.qml type
  assignment errors and Kirigami AboutItem issues. Crash cause is not established.
- NeoChat/Tokodon logs include Kirigami Addons MessageDialog undefined Success/null
  size errors; other runs contain errors under Fusion too. These require separate
  classification rather than attribution to the palette toggle without evidence.
- Absence of selected QML error markers in owned AI/greeter/package/askpass logs
  does not negate user-reported behavioral/rendering defects.

Askpass directory contains askpass.log, askpass-fusion-scale1.log and
askpass-fusion-scale125.log, each with staged provider/shared-plugin loading.
The separately requested askpass-scale125.log is absent. Default scale-1.25 remains
user-reported without a separately matched log; do not infer which default run
askpass.log represents or reconstruct exit codes from filenames. Fusion-looking
logs load shared Core/Controls/impl as expected but plugin loading alone does not
prove an individual standard-control implementation. No raw auth logs published.

Next guided step is read-only compositor connection/environment verification in
the tux terminal before activation tests. No bus/manager environment import has
been performed. Existing defects and remaining matrix gates stay open.


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
