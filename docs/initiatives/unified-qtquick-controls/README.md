# Unified Qt Quick Controls and Third-Party Compatibility

Status: Accepted

## Goal

Make compatible third-party Qt 6 Quick applications use verified HoloNight control implementations in HoloNight
sessions, and unify HoloNight applications around the same runtime style-selection path. Verify control rendering
and behavior rather than treating dark palettes or exported environment variables as proof of successful styling.

This initiative extends the completed [Cross-Toolkit Visual Consistency](../cross-toolkit-visual-consistency/README.md)
initiative. The review in [Automatic Quick Controls Style Selection](../../../holonight-qt/docs/automatic-quick-controls-style-selection.md)
is an input; its broad selection claims and recommendations must be reconciled with the contract below.

## Non-goals

- Reopen GTK or Qt Widgets styling work, or redesign all HoloNight application surfaces.
- Support Qt 5 Quick, static binaries, Flatpak, or AppImage deployment in this initiative.
- Patch third-party source or binaries, inject libraries, or replace application resources.
- Promise replacement of application-painted controls or controls explicitly locked to another style.
- Implement the entire Qt Quick Controls catalog regardless of demonstrated application needs.
- Change the fixed non-QML hyprlock theme or unrelated configuration, daemon, services, and icon repositories.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-qt` | Compatibility audit, shared style coverage, composite migration, policy checks, examples, installed-consumer tests, and documentation | [Discovery SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/SPEC.md) |
| `holonight-shell` | Shell and authentication adoption, session propagation, and selection/loading diagnostics | Pending |
| `holonight-settings` | Application adoption and correction of contradictory import-contract tests | Pending |
| `holonight-ai` | Application adoption and alignment of its import checker | Pending |
| `holonight-pkg-manager` | Application adoption and independent-launch verification | Pending |
| `holonight-greeter` | Application adoption and pre-session verification, preserving scaled ComboBox behavior | Pending |
| Umbrella | Contract acceptance, baseline coordination, real-application matrix, and final integration | This initiative |

Detailed requirements, implementation decisions, file changes, and test tasks belong in each repository's local SDD.

## Cross-repository contracts

### HoloNight applications

- Application QML imports standard controls using `import QtQuick.Controls as Controls` and qualifies control types,
  attached properties, and enums through that namespace. Remove direct `Holonight` style imports and Basic imports
  from application code.
- Every graphical executable embeds `:/qtquickcontrols2.conf` with `[Controls]` and `Style=Holonight`. Production and
  demo startup use this default instead of imperative style selection. Explicit environment and command-line style
  overrides remain supported according to Qt's precedence rules.
- `Holonight.Core` remains the palette, typography, metrics, and primitives API; `Holonight.Controls` remains the
  composite API. Their intentional HoloNight visuals do not become generic when the standard-controls style changes.
- Shared composites consume standard controls through the runtime selection path. Template-based implementations
  remain inside the shared library. Preserve dependency direction and prevent recursive style imports through Core.
- Preserve public composite APIs and interaction behavior. Resolve dependencies on style-specific properties that
  would otherwise break an explicit supported style override.
- Basic remains the declared style fallback and may appear in explicit compatibility-test fixtures. It is not a
  competing application import. Standard style implementations continue to use Qt Quick Templates as appropriate.
- Align usage guides, repository instructions, import checks, and contract tests with this policy. Do not interpret
  namespace qualification or a style-name check alone as proof of the rendered implementation.

### Third-party applications

The supported deployment is native, dynamically linked Qt 6 applications in HoloNight Hyprland and Sway sessions.
Keep the existing session contract:

```text
QT_QPA_PLATFORMTHEME=holonight
QT_QUICK_CONTROLS_STYLE=Holonight
```

Preserve explicit user overrides and propagate the environment through applicable terminal, desktop-launcher,
D-Bus, and systemd activation paths. The platform theme and Quick Controls selector have separate responsibilities;
installing or activating the platform theme alone does not establish Quick Controls selection.

Qt's runtime selector cannot override an application's unconditional `QQuickStyle::setStyle()` call or explicit
competing style imports. Module discovery and ABI-compatible deployment are also required. Classify such boundaries
explicitly rather than reporting every application as successfully themed. See
[Qt style selection](https://doc.qt.io/qt-6/qtquickcontrols-styles.html) and
[Qt Quick Controls deployment](https://doc.qt.io/qt-6/qtquickcontrols-deployment.html).

Add HoloNight implementations for missing standard controls encountered in the target matrix. The current shared
style implements 18 standard control types and declares Basic fallback; selecting the style does not establish full
HoloNight rendering for every control. Record each relevant surface as verified HoloNight, Basic fallback,
application-owned, or blocked by a concrete compatibility issue. A visible standard-control coverage gap in the
accepted matrix must be closed or explicitly resolved at contract acceptance, not silently counted as success.

### Initial real-application matrix

The installed-package survey below was performed on 2026-09-05. These versions are a discovery snapshot, not minimum
supported versions or a completed compatibility claim. Record actual package and Qt versions during integration.

| Application | Surveyed package version | Verification purpose |
|---|---|---|
| Haruna | `1.8.1-2` | Runtime selection, hybrid Qt integration, media controls, and settings |
| NeoChat | `26.08.0-1` | Kirigami composites, forms, navigation, and dialogs |
| Tokodon | `26.08.0-1` | A second Kirigami consumer, scrolling, and account forms |
| hyprpolkitagent | `0.1.3-10` | Service-launched Qt authentication UI, exercised in isolation |

Haruna 1.8.1 and hyprpolkitagent 0.1.3 condition their own style selection on an empty
`QT_QUICK_CONTROLS_STYLE`; see their versioned
[Haruna startup](https://github.com/KDE/haruna/blob/v1.8.1/src/main.cpp) and
[agent initialization](https://github.com/hyprwm/hyprpolkitagent/blob/v0.1.3/src/core/Agent.cpp).
The agent target is specifically the surveyed Qt-based version; do not assume later versions use the same toolkit.
NeoChat and Tokodon were identified as Qt Quick/Kirigami consumers; their effective style selection still requires
verification. Use logged-out surfaces without account credentials. Isolate the third-party authentication agent
from the active desktop authentication service.

## Acceptance and dependency order

1. `UQC-001`: audit provider/composite dependencies and the target matrix; identify concrete control additions,
   override constraints, and repeatable evidence collection. Produce the provider-local SDD.
2. `UQC-002`: resolve the audit findings, settle required coverage and integration checks, link local SDDs as they
   become available, and establish exact published baselines. Only then mark this initiative `Accepted`.
3. `UQC-101`: implement and verify the provider contract in `holonight-qt`; publish and pin its handoff.
4. `UQC-102`–`UQC-106`: adopt the published provider in each consumer repository and verify locally.
5. `UQC-201`: verify the exact integrated revisions and real-application matrix in both supported sessions.

Only Ready work packages may be assigned. Each implementer receives one repository, an exact upstream baseline, and
the work-package ID. Discovery is complete and UQC-002 accepted on 2026-09-07. UQC-101 is In Progress; consumer packages remain Planned
until the verified provider is published and pinned. Gitlinks remain authoritative; this document is not a second
compatibility manifest. Provider revisions must be published and pinned before dependent consumer work starts.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit, a linked local SDD, and passed local verification.
- [ ] Participating submodules are clean and pinned to published commits with compatible shared contracts.
- [ ] Owned graphical executables select HoloNight with style overrides unset; an explicit Fusion override works
      without hidden direct-style bypasses or style-specific property failures.
- [ ] Import-policy checks enforce the agreed boundary, including attached-property usage and test exceptions.
- [ ] Installed-prefix consumers and shared controls load without source-tree QML paths; missing-module and explicit
      competing-style cases are covered by negative fixtures.
- [ ] Foreign fixtures prove actual HoloNight implementations and representative enabled, disabled, focused, hovered,
      and selected states. Unimplemented types have explicit fallback classifications.
- [ ] Required visible standard-control gaps from the accepted real-application matrix have tested implementations.
- [ ] Applicable terminal, desktop-launcher, D-Bus, and systemd activation paths have verified selection and discovery.
- [ ] Focused regressions cover text editing, authentication, scrolling, keyboard navigation, and scaled popups,
      including the existing greeter ComboBox geometry contract.
- [ ] Dependency-order repository builds/tests and umbrella integration checks pass.
- [ ] Human-operated visual and interaction checks pass for the accepted application matrix under Hyprland and Sway.
      Do not automate pointer movement, clicking, or window focus; request manual interaction when required.
- [ ] The final ledger row records commands, results, application/Qt versions, limitations, and verification date;
      only its successful completion permits status `Integrated`.

## Discovery checkpoint — 2026-09-05

Published current checkouts are recorded in [the existing-work baseline handoff](BASELINE.md). The
[provider audit](../../../holonight-qt/docs/sdd/unified-qtquick-controls/DESIGN.md) records source dependencies and
verification design. UQC-001 remains In Progress: desktop probes did not reach QML loading, isolated third-party
authentication evidence is missing, and the exact desktop coverage proposal is not settled. See
[application evidence](../../../holonight-qt/docs/sdd/unified-qtquick-controls/APPLICATIONS.md). The initiative remains
Draft; review findings with the user before UQC-002 acceptance or any implementation.


## Discovery continuation — 2026-09-06

The [updated provider proposal](../../../holonight-qt/docs/sdd/unified-qtquick-controls/APPLICATIONS.md) and
[reproducible evidence](../../../holonight-qt/docs/sdd/unified-qtquick-controls/audit/EVIDENCE.md) supersede the earlier
pre-QML timeout inference: corrected logging establishes staged-module loading in all three desktop applications.
Haruna reaches the event loop in ordinary/private-bus probes; the fixture verifies default, explicit Fusion and
Haruna-style Fusion fallback origins. Application-owned slider painting and the competing fallback are explicit
review boundaries. Nine provisional additions are proposed, pending required manual surface/state observations.

This remains a partial handoff. No separate authentication login is prepared; manual Hyprland checks are pending.
Follow the [collection checklist](../../../holonight-qt/docs/sdd/unified-qtquick-controls/audit/CHECKLIST.md).
UQC-001 remains In Progress and the initiative Draft. Stop for joint review before UQC-002 acceptance.

## Scope-review preparation — 2026-09-07

The provider working tree now contains manual desktop observations, completed isolated authentication discovery,
and a six-case installed-provider layout/palette comparison. These are unpublished continuation artifacts; the
published gitlink still identifies the earlier partial audit. See the [scope review](../../../holonight-qt/docs/sdd/unified-qtquick-controls/REVIEW.md)
and its linked application evidence.

The proposed scope adds indicator-only CheckBox/RadioButton/Switch geometry fixes and application palette support
to the standard-control work, alongside the nine provisional missing controls. The reduced license-popup
composition overflows under all three compared styles; resolve it as an application composition limitation,
preserving legitimate horizontal scrolling. Unreported application surfaces and states remain unverified.

The comparison was rerun successfully on 2026-09-07. Joint coverage and palette-boundary review, publication of the
discovery handoff, and UQC-002 contract acceptance remain prerequisites to product implementation. No acceptance
state or gitlink changes are implied by this working-tree update.

## Accepted scope — 2026-09-07

The user approved the complete [scope review](../../../holonight-qt/docs/sdd/unified-qtquick-controls/REVIEW.md).
This supersedes earlier Draft/review gates in the historical checkpoints above.

- Implement ApplicationWindow, Label, ToolButton, ToolBar, ToolSeparator, MenuSeparator, Popup, MenuBar and
  MenuBarItem in the provider. Retain Basic fallback for other unimplemented controls and honor Haruna's explicit
  Fusion fallback. Application-painted sliders remain application-owned. Dialog/DialogButtonBox/Page/Pane and
  other deferred catalog entries are explicitly outside the required additions.
- Fix indicator-only CheckBox, RadioButton and Switch geometry, including mirrored placement and existing Switch
  size roles. Verify adjacent labels, trailing-card containment and ordinary labeled controls.
- Standard controls respect application/control Qt palette overrides. Session defaults supply HoloNight colors;
  application theme selection must not write shared desktop configuration. Core/composites retain their explicit
  appearance APIs. Provider design must map roles and states and verify default parity and dark/light round trips.
- Preserve composite error, sizing, delegate-corner and scaled-popup APIs through public hooks. Core HnLabel uses
  Templates.Label to avoid a selected-style dependency cycle. Authentication wrappers preserve overrides and
  propagate process-local installed-prefix discovery paths with meaningful missing-module diagnostics.
- The license-popup reduced composition clips under all three compared styles. Accept this application/Kirigami
  composition limitation; do not add blanket popup padding or disable legitimate horizontal scrolling.
- Recorded manual observations and isolated authentication complete discovery with explicit limits. Unobserved
  server/onboarding fields and visual/input states remain required final matrix checks, not inferred passes.
  Existing UQC-201 two-compositor, activation, installed-prefix and negative-fixture gates remain in force.

Canonical remote checks on 2026-09-07 confirmed the existing consumer discovery baselines in BASELINE.md and
provider discovery commit `033d6001fd088a96ac6e4ff936b6bafcf6ab5d4c`. UQC-101's exact assignment baseline is that
published provider revision. Consumer assignments must record their then-current published baselines when Ready.
Execution order is provider → settings → AI → packages → greeter → shell, then umbrella integration. All consumers
require the published, pinned provider; their local SDDs are prepared before their implementation starts.

## Provider implementation checkpoint — 2026-09-07

The published geometry slice fixes indicator-only and mirrored CheckBox/RadioButton/Switch layout and passes the
provider suite. UQC-101 remains In Progress. See the [implementation SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md)
for remaining provider work. Consumer packages remain Planned until the complete provider handoff.
