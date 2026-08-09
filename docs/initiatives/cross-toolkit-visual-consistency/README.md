# Cross-Toolkit Visual Consistency

Status: Accepted

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Deliver a coherent HoloNight desktop experience in which applications follow the selected HoloNight color scheme,
light/dark mode, accent, typography, icons, cursor, and other practical appearance defaults regardless of whether
they use Qt 6, Qt 5, GTK 4, or GTK 3.

The initiative should make common third-party applications feel at home in a HoloNight session without promising
pixel-identical controls across unrelated toolkits. It should prefer stable toolkit and desktop standards over
application-specific patches, preserve application functionality, and degrade cleanly when an application does not
support a HoloNight appearance signal.

This initiative supports the wider HoloNight objective of providing a complete, dependable desktop experience for
tiling window managers. Hyprland is the first integration target. The contracts should avoid unnecessary Hyprland
coupling so that Sway, niri, and other Wayland compositors can be added later.

## Experience principles

1. **Correctness before resemblance.** Theming must not prevent an application from starting or break native
   controls, dialogs, accessibility, or toolkit platform integration.
2. **One user choice.** HoloNight Settings owns the user-facing scheme and accent selection; adapters translate that
   choice into supported toolkit mechanisms.
3. **Semantic consistency.** Adapters consume a versioned set of semantic appearance values rather than copying
   unrelated colors between toolkit configuration files.
4. **Progressive fidelity.** A supported toolkit may begin with light/dark and accent propagation, then add palette
   integration, and only later receive custom control styling where evidence justifies its maintenance cost.
5. **Native fallback.** Unsupported applications retain their native appearance. HoloNight must not inject private
   libraries, replace application resources, or maintain per-application binary patches.
6. **Observable and reversible integration.** Generated files and environment changes must have clear ownership,
   diagnostics, and a way to return to toolkit defaults.

## Support model

Support is defined in tiers so that “supported” does not imply an unrealistic identical rendering across toolkits.

| Tier | Promise |
|---|---|
| Tier 0 — Compatible | Applications start and function correctly in the HoloNight Wayland session. |
| Tier 1 — Appearance hints | Applications receive supported light/dark, accent, icon, cursor, and font preferences where the toolkit exposes them. |
| Tier 2 — Palette integration | Application surfaces, text, selection, borders, and status colors are derived from HoloNight semantic tokens through a maintained toolkit adapter. |
| Tier 3 — Native control styling | HoloNight supplies and tests toolkit-specific widget/control rendering. This tier is adopted only for toolkits where its benefit exceeds its compatibility and maintenance cost. |

Initial target policy:

| Application family | Initial target | Direction |
|---|---|---|
| HoloNight Qt 6 applications | Tier 3 | Existing first-class design system; retain as the visual reference implementation. |
| Third-party Qt 6 Widgets | Tier 2/3 | Retain the existing palette, style, and platform-theme integration with compatibility testing. |
| Qt 5 Widgets | Tier 2, with a focused Tier 3 style where practical | Add a narrow compatibility implementation for applications such as KeePassXC; do not port the Qt Quick design system. |
| GTK 4 | Tier 1 first, assess Tier 2 | Prefer supported settings and portal mechanisms; evaluate a generated color adapter before custom widget CSS. |
| GTK 3 | Tier 1 first, assess Tier 2 | Support while important applications remain in use; keep any theme adapter separate from GTK 4 assumptions. |
| GTK 2 | Tier 0 only | No HoloNight theme implementation is planned. |
| Electron/Chromium | Tier 1 where upstream honors system preferences | Propagate standards-based dark/light and portal settings; do not patch individual Electron applications. |
| Java desktop applications | Tier 0 initially | Perform an application/toolkit survey before promising appearance integration; avoid global JVM injection. |
| Other or bespoke toolkits | Tier 0 | Evaluate only when a high-value application and a stable integration mechanism justify it. |

These targets are planning hypotheses until the discovery work packages are complete and the initiative is
`Accepted`.

## Representative application inventory

CTV-001 records a deliberately bounded matrix rather than promising support for every installed desktop entry. The
primary set comes from the applications assigned to HoloNight/Hyprland keybindings on the reference system; coverage
fixtures fill toolkit gaps. Package and toolkit versions are a discovery snapshot from 2026-08-07 and are not minimum
supported versions.

Display paths marked **observed** came from Hyprland's live client inventory. Paths marked **expected** follow the
installed toolkit backend and session configuration but still require launch-time confirmation in the integration
matrix. “Candidate mechanism” identifies what later feasibility packages must validate; it is not yet an accepted
cross-repository contract.

### Primary daily-use matrix

| Application | Snapshot / evidence | Toolkit family | Display path | Candidate appearance mechanism | Current baseline | Target / fallback |
|---|---|---|---|---|---|---|
| HoloNight Settings and shell surfaces | Locally built Qt 6/QML applications | Qt 6 Quick | Native Wayland by design | Canonical HoloNight configuration and QML semantic tokens | First-class HoloNight controls | Tier 3; failure is an integration defect |
| Dolphin | 26.04.3; default file manager keybinding; links Qt 6 Widgets/QuickWidgets | Qt 6/KDE Widgets | Expected native Wayland | Qt platform theme, widget style, palette, KDE color scheme, icons and fonts | Existing HoloNight Qt/KDE outputs are available | Tier 2/3; native KDE/Qt style fallback |
| FreeCAD | 1.1.3; direct keybinding; links Qt 6 Widgets | Qt 6 Widgets with application-specific UI | Expected native Wayland | Qt platform theme, widget style, palette, icons and fonts | Qt integration is available; application-owned surfaces may differ | Tier 2; preserve application-owned rendering |
| KeePassXC | 2.7.12; direct keybinding; links Qt 5 Widgets | Qt 5 Widgets | Native Wayland observed | Separate Qt 5 palette/style and optional platform-theme adapter | Starts natively after installing `qt5-wayland`; no HoloNight Qt 5 adapter | Tier 2 plus focused Tier 3 where safe; native Qt style fallback |
| Ghostty | 1.3.1; default terminal; links GTK 4 and libadwaita | GTK 4/libadwaita with application-owned terminal palette | Native Wayland observed | Portal/GSettings appearance hints for chrome; application-native theme configuration for terminal colors | GNOME settings prefer dark, use `Tokyonight-Dark`, HoloNight icons, and Inter 12 | Tier 1 for chrome; terminal palette is a separate future decision |
| pwvucontrol | 0.5.3; direct keybinding; links GTK 4 and libadwaita | GTK 4/libadwaita | Expected native Wayland | Settings portal, GSettings, libadwaita color-scheme/accent facilities where supported | Same GNOME appearance settings as Ghostty | Tier 1 first, assess Tier 2; native libadwaita fallback |
| Inkscape | 1.4.4; direct keybinding; links GTK 3 | GTK 3 with application-specific UI | Expected native Wayland | GTK settings/GSettings, GTK theme, icons, cursor and fonts | `Tokyonight-Dark` GTK theme currently selected | Tier 1 first, assess Tier 2; native/application theme fallback |
| GIMP | 3.2.4; direct keybinding; links GTK 3 | GTK 3 with application-owned theme behavior | Expected native Wayland | GTK settings where honored; preserve GIMP's explicit application theme | Desktop GTK theme exists, but application preferences may override it | Tier 1 where honored; application theme fallback |
| Google Chrome | 151.0.7922.71; direct keybinding | Chromium/Aura with GTK integration at system edges | Native Wayland observed | Portal/system color-scheme preference, GTK integration for native dialogs/chrome where honored, application/web theme controls | Runs native Wayland; web and browser themes remain independently configurable | Tier 1; Chromium/application theme fallback |
| Teams for Linux | 2.13.0; direct keybinding; Electron binary links GTK 3 | Electron/Chromium | Native Wayland observed | Electron/Chromium system color preference and GTK/portal integration where honored | Global Electron flags request Wayland | Tier 1; application theme fallback |
| Postman | 12.21.9; direct keybinding | Electron/Chromium | Expected native Wayland from global Electron flags | Electron/Chromium system color preference where honored | Application maintains its own UI theme | Tier 1 where honored; application theme fallback |
| DataGrip | 2026.2.2; direct keybinding; bundled JetBrains Runtime | JVM/Swing/JetBrains UI | Expected XWayland until observed otherwise | Application Look-and-Feel and JetBrains theme APIs; no global JVM injection | Application-owned appearance | Tier 0 initially; native JetBrains theme fallback |
| Blender | 5.2.0; direct keybinding; custom application UI | Bespoke/custom toolkit | Expected XWayland until observed otherwise | Application theme only | Not governed by Qt or GTK widget theming | Tier 0; Blender-owned theme |

### Coverage fixtures

| Fixture | Purpose | Target / fallback |
|---|---|---|
| Kate or qView | Second Qt 6 Widgets implementation, separating generic Qt behavior from Dolphin/KDE specifics | Tier 2/3; native Qt style fallback |
| Seahorse 47.0.1 | Conventional GTK 3 application independent of Inkscape/GIMP custom UI | Tier 1 first, assess Tier 2; native GTK fallback |
| pavucontrol 6.2 | Conventional GTK 4 application without making libadwaita the only GTK 4 test | Tier 1 first, assess Tier 2; native GTK fallback |
| GTK 4 Widget Factory | Broad GTK 4 widget/state coverage and visual-regression fixture | Test fixture only |
| Slack, Obsidian, or Code - OSS | Second Electron implementation when behavior differs from Teams/Postman | Tier 1; application theme fallback |

### Inventory conclusions

- Qt 5 is a real daily-use requirement, represented by KeePassXC running natively on Wayland. Its absence from the
  current HoloNight adapter set is a product gap, while the separately packaged `qt5-wayland` platform plugin remains
  a system dependency rather than a HoloNight deliverable.
- Both GTK 3 and GTK 4 remain relevant. GTK 4 must be tested both with and without libadwaita; GTK 3 must include at
  least one conventional application because Inkscape and GIMP have substantial application-owned UI behavior.
- Electron/Chromium applications already run natively on Wayland on the reference setup, but their content themes are
  often application-owned. The initiative should promise system preference propagation, not forced recoloring.
- Java and bespoke applications do not expose one dependable desktop-wide theme contract. DataGrip and Blender are
  explicit Tier 0 fallback tests rather than omissions from the inventory.
- Native Wayland is the primary path. XWayland remains a required fallback/compatibility path for applications that
  cannot use Wayland reliably, not a second visual implementation target.
- Terminal, editor, browser-content, and application-owned themes are adjacent to toolkit chrome integration. They
  require separate ownership and value decisions before HoloNight writes their configuration.

## Non-goals

- Pixel-identical widgets, spacing, or animations across Qt, GTK, Electron, Java, and bespoke toolkits.
- A Qt 5 port of `Holonight.Core`, `Holonight.Controls`, Qt Quick Shapes, or HoloNight application composites.
- A GTK 2 theme or support for unmaintained toolkit versions.
- Per-application binary patching, `LD_PRELOAD` injection, resource replacement, or undocumented private hooks.
- Overriding application-specific themes when the application intentionally does not follow desktop preferences.
- Making compositor-specific IPC the canonical appearance contract.
- Supporting Sway, niri, or other compositors in the first implementation milestone; the shared contract must merely
  avoid preventing their later adoption.
- Folding application launcher, network, Bluetooth, audio, or tray functionality into this appearance initiative.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-qt` | Canonical semantic color mapping for Qt; Qt 6 compatibility; scoped Qt 5 Widgets style/platform-theme feasibility and implementation | [Semantic export SDD](../../../holonight-qt/docs/sdd/cross-toolkit-semantic-export/SPEC.md) |
| `holonight-appearance-adapters` | Toolkit-neutral appearance export tooling; GTK 3/4 adapters; standards-based portal, GSettings, XSettings, and generated appearance outputs | [CTV-005 consumer and Tier 1 SDD](../../../holonight-appearance-adapters/docs/sdd/ctv-005-semantic-consumer/SPEC.md); [CTV-006 GTK palette evaluation](../../../holonight-appearance-adapters/docs/sdd/ctv-006-gtk-palette/SPEC.md) |
| `holonight-settings` | User-facing appearance controls, validation, preview semantics, and apply/revert behavior | Pending |
| `holonight-shell` | Hyprland session environment and desktop integration; startup-time propagation and diagnostics | [CTV-103 session and portal SDD](../../../holonight-shell/docs/sdd/ctv-103-session-portal/SPEC.md) |
| umbrella | Support matrix, cross-repository contracts, exact revision integration, and manual application matrix | This initiative |

The ownership boundary is intentionally split:

- `holonight-qt` owns the canonical semantic token meanings, scheme/accent resolution, and the producer side of the
  versioned semantic appearance contract because it currently owns the source palette.
- `holonight-appearance-adapters` owns the toolkit-neutral serialization/export tooling, contract validation on the
  consumer side, translation into GTK 3/4 and standards-based desktop outputs, and adapter diagnostics. It does not
  own the user's selected appearance state.
- `holonight-settings` owns user-facing selection, validation, preview, apply/revert orchestration, and presentation
  of adapter status. It does not contain toolkit-specific generators.
- `holonight-shell` owns Hyprland session propagation and startup integration. It does not derive colors or generate
  toolkit themes.
- The umbrella owns the cross-repository schema/version contract and exact integration pins, but no product code.

This keeps GTK and other desktop adapters out of `holonight-qt` without duplicating the source token catalog. Future
terminal, editor, or application-specific adapters belong in `holonight-appearance-adapters` only after a separate
scope decision accepts them; repository ownership does not make those integrations automatic goals.

## Cross-repository contracts

### Canonical appearance state

The existing HoloNight configuration remains the source of the user's selected scheme, accent, and appearance
profile. Semantic appearance contract version 1, produced through the existing HoloNight Config and Qt provider
APIs, is the accepted adapter input. The participating repositories document:

- the exact supported fields and values;
- which component validates and writes them;
- how consumers detect changes;
- fallback behavior for missing, invalid, or newer configuration versions;
- whether toolkit adapters consume the current configuration directly or a generated, toolkit-neutral export.

There must be one canonical selection state. GTK settings, Qt settings, portal values, and generated theme files are
outputs, not competing sources of truth.

### Accepted Tier 1 outputs

- The production adapter applies available GNOME GSettings interface keys and updates only its owned keys in the
  GTK 3 and GTK 4 `settings.ini` files. Missing schemas or keys are supported native fallbacks.
- The existing Shell Settings portal backend remains the only portal publisher. The adapter reports portal
  propagation as delegated and does not start another backend.
- `XCURSOR_THEME` is resolved from canonical appearance at session startup. No session-wide `GTK_THEME` is exported.
- XSettings is reported through its existing session owner when present. HoloNight does not start a competing
  XSettings manager.
- GSettings changes are live where consumers observe them, `settings.ini` changes require application relaunch,
  and cursor environment propagation requires a session restart.

Qt 5 styling and platform-theme prototypes are not shipped: the semantic style failed the accepted all-combination
contrast gate, while the private platform theme did not provide native-dialog integration. Qt 5 applications retain
their native toolkit fallback. GTK 3 and GTK 4 palette fragments are also not shipped because stable global
application coverage cannot be guaranteed, and libadwaita or application-owned palettes remain native. These
decisions preserve Tier 1 support without claiming rejected Tier 2 or Tier 3 behavior.

### Semantic export

The initiative must define a versioned semantic export sufficient for adapters. At minimum it must settle mappings
for:

- dark or light color scheme;
- primary accent and contrasting foreground;
- window, view, elevated, selected, hover, and disabled surfaces;
- primary, secondary, disabled, inverse, and selected text;
- passive, active, focus, and destructive borders;
- success, warning, and error roles;
- UI and monospace font families where supported;
- icon and cursor theme identifiers.

The contract defines meanings and fallbacks, not toolkit widget implementation. Unsupported roles may be omitted by
an adapter only when the omission and native fallback are documented.

### Application and reload behavior

Each adapter must declare whether a change applies live, on new application launch, or only after session restart.
The apply path must be idempotent and must not leave partially written configuration. Where HoloNight modifies or
generates user configuration, it must own only a clearly delimited artifact and preserve unrelated user settings.

### Session and portal behavior

The shell owns Hyprland-session propagation, but not palette derivation. Discovery must compare environment
variables, XSettings/GSettings, the Settings portal, and toolkit-native configuration, then choose the smallest set
needed for reliable applications. The contract must distinguish variables safe to export session-wide from those
that are appropriate only for a specific application or test.

### Compatibility policy

- Toolkit adapters are versioned independently in implementation, even when they share generated semantic input.
- Private Qt platform-theme APIs require an explicit rebuild/compatibility policy for each supported Qt major.
- A missing adapter must fall back to native toolkit behavior rather than blocking application startup.
- The integration matrix must include native Wayland applications and XWayland applications where applicable.
- Accessibility, high-DPI behavior, file dialogs, input methods, and application startup are compatibility gates,
  not optional visual polish.

## Roadmap and decision gates

### Prerequisite — Appearance Configuration Foundation

The [Appearance Configuration Foundation](../appearance-configuration-foundation/README.md) initiative must be
`Integrated` before CTV-003 begins. CTV must consume the clean canonical appearance contract and separated token
taxonomy; it must not add compatibility layers for the current `theme.conf`, `appearance.json`, and appearance fields
inside `config.toml`.

### Phase 0 — Inventory and contract

Inventory representative daily-use applications and identify their actual toolkit/version, Wayland or XWayland
mode, supported appearance mechanisms, and current behavior. Settle adapter ownership, the semantic export, update
behavior, support lifetime, and test matrix. This phase ends when the initiative can be marked `Accepted`.

### Phase 1 — Standards-based baseline

Implement Tier 1 propagation for supported desktops/toolkits using stable settings and portals. Add shell diagnostics
and Settings apply/revert behavior. Validate GTK 3, GTK 4, Electron, Qt 5, and Qt 6 applications without custom GTK
control styling.

### Phase 2 — Qt 5 compatibility

Implement the scoped Qt 5 Widgets palette/style integration and, if the feasibility review accepts its private-API
cost, a Qt 5 platform-theme plugin. Package Qt 5 and Qt 6 plugins in separate plugin directories and verify that a
missing optional plugin cannot prevent applications from starting.

### Phase 3 — GTK palette evaluation

Prototype separate GTK 3 and GTK 4 mappings from the semantic export. Measure coverage, visual benefit,
accessibility, upstream compatibility, and maintenance burden on representative applications. Adopt Tier 2 only if
the prototype passes the documented decision gate; otherwise retain Tier 1 and native widget styling.

### Phase 4 — Long-tail applications

Survey Electron/Chromium and Java applications that remain inconsistent after the baseline. Add only stable,
standards-based adapters with meaningful application coverage. Treat application-specific launch flags as documented
compatibility guidance rather than the primary system contract.

### Phase 5 — Additional compositors

Adopt the settled appearance/session contract in Sway, niri, or other compositor sessions without changing the
canonical appearance state or toolkit adapter formats.

Each implementation phase may become a follow-up initiative if Phase 0 shows that it has independent ownership,
release, or integration boundaries. This initiative remains the parent roadmap and records those links.

## Dependency order

1. Umbrella application inventory, support matrix, and ownership decision.
2. Integrate the Appearance Configuration Foundation prerequisite.
3. `holonight-qt` semantic producer export and Qt 5 feasibility contracts.
4. `holonight-appearance-adapters` validates the consumer contract and prototypes GTK 3/4 integration mechanisms.
5. `holonight-settings` adopts the settled apply/revert and status contract.
6. `holonight-shell` adopts the settled session and portal propagation contract for Hyprland.
7. Repository-local implementation proceeds in the phase order above, using published provider revisions.
8. Umbrella integration review validates the exact pinned revisions and representative applications.

Provider revisions must be published and pinned before dependent consumer work starts.

## Integration acceptance criteria

- [ ] The support matrix names representative applications, toolkit versions, display path, target tier, and expected fallback.
- [ ] Toolkit adapter ownership and lifecycle are explicit; no implementation is placed in the umbrella repository.
- [ ] The canonical appearance and semantic export contracts are versioned and documented.
- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Changing scheme and accent produces the documented live/relaunch/restart behavior for every target tier.
- [ ] Representative Qt 6, Qt 5, GTK 4, GTK 3, and Electron applications pass startup and visual checks under Hyprland.
- [ ] Missing optional adapters and deliberately unsupported toolkits fall back safely.
- [ ] Accessibility, high-DPI, native Wayland/XWayland, file-dialog, input-method, and rollback checks pass where applicable.
- [ ] Commands, results, application versions, screenshots or visual notes, and verification date are recorded in the final integration row.
