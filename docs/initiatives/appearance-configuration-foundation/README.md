# Appearance Configuration Foundation

Status: Draft

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Establish one clean, versioned source of truth for global HoloNight appearance and a strict separation between color,
metric, shape, and product configuration before cross-toolkit appearance export begins.

This is a prerequisite for the Cross-Toolkit Visual Consistency initiative. The project is pre-stable, so the goal is
to correct weak boundaries now instead of turning the current three-file layout into a permanent compatibility
contract. The final integration must remove superseded readers, writers, environment aliases, and duplicated
defaults. Existing developer files remain untouched but inert; ongoing dual-read or dual-write behavior is not an
acceptable end state.

## Problem statement

Global appearance is currently distributed across three files under `$XDG_CONFIG_HOME/holonight`:

| File | Format | Current content | Schema/code owner | Writers | Consumers |
|---|---|---|---|---|---|
| `theme.conf` | QSettings INI | Scheme, derived mode, accent, UI/fixed fonts and sizes; parser also accepts icons, header/display fonts, scale, and effects | `holonight-qt` `ThemeConfig` and catalog | HoloNight Settings through `ThemeConfig::save()` | Qt palette/QML/style/platform theme; Shell `ThemeService` and Settings portal backend; Settings |
| `appearance.json` | JSON v1 | Corner style, shape scale, optional base radius and chamfer | `holonight-qt` `AppearanceConfig` | HoloNight Settings through `AppearanceConfig::save()` | HoloNight Qt/QML and Settings |
| `config.toml` | TOML | Shell behavior plus an `[appearance]` section containing fonts, sizes, transparency, and blur | `holonight-settings` public `HolonightConfig::Config` package | Settings; Shell writes a full default file when absent | Shell and Settings |

The live file also demonstrates that `config.toml` can contain credentials and private URLs alongside appearance and
ordinary shell settings. Values are intentionally omitted from this initiative. This is both a security boundary and
an ownership problem: appearance updates must not parse and rewrite a secret-bearing product configuration file.

The current layout has these defects:

- Three serialization formats and three write operations are required for one Settings save.
- Font defaults and values overlap between `theme.conf` and `config.toml` and already disagree in family spelling,
  sizes, and specialized font roles.
- Transparency exists in both the Qt theme model and the Shell TOML model with different units and defaults.
- `appearance/mode` is derived from the selected scheme but is persisted beside it, allowing contradictory state.
- Schema ownership follows historical implementation location rather than domain ownership: a reusable configuration
  package lives under Settings, while Shell and Qt contain independent path, watch, default, and parse logic.
- Saving is sequential across three files, so failure can leave a partially applied global appearance.
- Readers support environment, KDE, missing-file, invalid-field, and legacy-mode fallbacks that are not expressed as
  one ordered resolution contract.
- Shell portal behavior parses `theme.conf` separately from the Qt configuration implementation.

The token model has a related responsibility defect. `holonight-qt/palette/holonight/palette.h` declares
`ColorTokens`, but that structure also owns `borderWidth`, `focusBorderWidth`, `separatorWidth`, `controlHeight`, and
`controlPadding`. These values are not colors. Control height and spacing also overlap the separate
`HnControlMetrics` singleton, while shape dimensions already have a dedicated `ShapeTokens` structure.

## Target architecture

ACF-002 settles the target architecture below. The initiative remains `Draft` until the new shared repository exists,
all repository-local SDDs link the same contract, and implementation baselines are recorded.

### Canonical document and schema owner

- The canonical file is `$XDG_CONFIG_HOME/holonight/appearance.toml`.
- The document uses TOML with a required integer `version = 1`. TOML is selected because the configuration is
  user-inspectable, comments are useful, and the existing C++ ecosystem already builds and tests toml++.
- A new independently buildable `holonight-config` repository owns the neutral C++ schema package: field types,
  defaults, validation, path resolution, TOML parsing, deterministic serialization, atomic replacement, diagnostics,
  and test helpers.
- `holonight-config` uses standard C++ value types and filesystem APIs plus a TOML parser. Its public schema target has
  no Qt Core, Qt GUI/QML, compositor, Settings, Shell, or adapter dependency.
- `holonight-qt`, `holonight-settings`, and `holonight-shell` consume the published package. Qt-specific conversion
  from neutral strings/numbers to `QString`, `QColor`, `QFont`, watchers, and resolved palette types stays in the
  consuming repository.
- `holonight-appearance-adapters` does not own or write the user's selection. It will consume a later resolved semantic
  export after this initiative is integrated.

The conceptual v1 shape is:

```toml
version = 1

[theme]
scheme = "holonight-dark"
accent = "blue"

[typography]
ui_family = "Inter"
ui_size = 12
monospace_family = "JetBrains Mono"
monospace_size = 12
title_family = "Audiowide"
title_size = 10
display_family = "Rajdhani"
display_size = 24

[icons]
theme = "HoloNight"
fallback = "Papirus"
cursor = "default"

[layout]
scale = 1.0

[shape]
style = "inherit"
scale = 1.0
# base_radius and base_chamfer are omitted when no override is selected
```

Repository-local SDDs may refine spelling only if all consumers agree before this initiative becomes `Accepted`.
They may not add a second persisted appearance authority.

### One canonical appearance document

- One versioned document stores user-selected global appearance.
- It contains only global appearance state: scheme, accent, typography, icon/cursor choices, layout scale, and
  shape/profile choices accepted by the final schema.
- Derived values such as dark/light mode are computed from canonical state and are not persisted independently unless
  a documented mode is itself the user's canonical selection.
- Shell behavior, widget layout, tray rules, notifications, weather, calendar, credentials, private URLs, and other
  product configuration remain outside the global appearance document.
- A save is atomic at the document level and exposes actionable read/write/validation errors.
- One component owns schema definitions, defaults, validation, path resolution, parsing, serialization, and legacy
  disposition rules.
  Settings is the user-facing writer, not a second schema implementation.
- Consumers use the shared API or a generated contract; they do not independently parse selected fields.

### Field classification

| Current field/group | Target classification | Canonical target / owner | Decision |
|---|---|---|---|
| `appearance/scheme` | Global user selection | `theme.scheme` / `holonight-config` schema | Retain as the only theme selector. `holonight-qt` validates IDs against its theme catalog until catalog ownership is revisited. |
| `appearance/accent` | Global user selection | `theme.accent` | Retain; resolve through the canonical theme catalog. |
| `appearance/mode` | Derived output | None | Remove. Derive dark/light from the selected scheme; portal values are projections, not stored state. |
| UI font family/size | Global typography | `typography.ui_family`, `typography.ui_size` | Merge the conflicting INI/TOML authorities and defaults. |
| Fixed/monospace family/size | Global typography | `typography.monospace_family`, `typography.monospace_size` | Normalize the role name and family spelling. |
| Header/title family and size | Global typography | `typography.title_family`, `typography.title_size` | Merge Qt `header_font` and Shell `title_font`. |
| Display/clock family and size | Global typography | `typography.display_family`, `typography.display_size` | Merge Qt `display_font` and Shell `clock_font`. |
| Icon theme and fallback | Global appearance | `icons.theme`, `icons.fallback` | Retain and expose consistently to Qt, Shell, portals/settings, and later adapters. |
| Cursor theme | Global appearance | `icons.cursor` | Add to the canonical contract; applying it is consumer-specific. |
| `scaleFactor` | Global layout preference | `layout.scale` | Retain one normalized scalar. It does not replace compositor/display scale. |
| Qt `effects/transparency` | Unimplemented/deprecated | None | Remove; it has no production rendering consumer. |
| TOML `appearance.transparency` | Unimplemented/deprecated | None | Remove from schema, Settings, parser, writer, and tests; do not preserve incompatible percentage semantics. |
| TOML `appearance.blur_strength` | Unimplemented/deprecated | None | Remove until a compositor/surface effect design defines ownership and units. |
| Corner style | Global shape preference | `shape.style` | Retain. |
| Shape scale | Global shape preference | `shape.scale` | Retain with one validation range. |
| Base radius/chamfer | Optional global shape overrides | `shape.base_radius`, `shape.base_chamfer` | Retain as omitted optional values rather than JSON null sentinels. |
| Workspace/tray/background/widget/notification/calendar/OSD fields | Shell product configuration | Shell `config.toml` / Shell-owned schema | Keep outside global appearance. Rename or relocate only in the Shell local SDD where needed. |
| Weather and calendar credentials/private URLs | Secret or private integration state | Secret store or separately owned Shell configuration | Never enter `appearance.toml`; appearance writes must not touch their storage. |

The HoloNight theme catalog remains in `holonight-qt` for this initiative because it defines available palettes, not
generic serialization. `holonight-config` validates structural constraints and non-empty identifiers; Qt/Settings use
the catalog to validate supported scheme/accent combinations. A later catalog-neutrality initiative may move it only
with evidence that non-Qt producers require ownership.

### Writer and reload contract

- HoloNight Settings is the only production writer of `appearance.toml` in this initiative.
- `holonight-config` provides the write operation; Settings owns UI validation, dirty state, explicit Save/Discard,
  and user-visible errors.
- The writer creates a same-directory temporary file, flushes it, and atomically replaces the canonical path. Failure
  leaves the previous document intact.
- Qt applications/plugins and Shell are read-only consumers. Each owns a thin native watcher because the neutral
  schema package must not impose an event loop. Watchers observe both the parent directory and file so atomic rename
  cannot permanently disarm reload.
- A consumer parses and validates the complete replacement before publishing change signals. Invalid replacements
  keep the last known-good in-memory state and emit diagnostics; they do not silently switch to defaults mid-session.
- Missing configuration at startup resolves to shared defaults without creating a file. Only an explicit successful
  Settings save creates it.
- Shell projects canonical scheme/accent into the Settings portal. The portal backend consumes Shell's validated
  in-memory appearance state and never parses the file independently.
- Future adapters consume the resolved export defined by CTV, not `appearance.toml` directly.

### Clean-break policy

- There is no automatic legacy migration code. This is a pre-stable developer system, and preserving three parsers
  would undermine the purpose of the initiative.
- Existing `theme.conf`, `appearance.json`, and `[appearance]` values in Shell `config.toml` are ignored once the new
  consumers land. HoloNight does not delete or rewrite those files automatically; developers may archive or remove
  them manually after validating the new configuration.
- Settings initializes the editor from new-schema defaults when `appearance.toml` is absent. The first explicit save
  creates the canonical file.
- Old readers, writers, tests, environment aliases, and watchers are removed in the same repository handoff that
  adopts the new schema. Temporary dual-read or dual-write commits must not be pinned by the umbrella.
- The only supported override is `HOLONIGHT_APPEARANCE_FILE`, used for tests and explicit deployment. Field-by-field
  environment overrides and KDE-as-selection fallback are removed; desktop projections occur after canonical
  resolution and never override the saved choice.

### Configuration security boundary

- Appearance changes never rewrite files containing credentials, access tokens, authenticated feed URLs, or other
  private service configuration.
- Secrets move to an appropriate secret store or a separately owned product configuration as determined by the
  repository-local design; secret migration itself may be split into a security follow-up if it exceeds this
  initiative, but appearance must cease sharing its transaction boundary with them.
- Tests and documentation use redacted fixtures only.

### Token taxonomy

- `ColorTokens` contains `QColor` semantic roles only.
- `MetricTokens` becomes the C++ authority for shared stroke, separator, spacing, icon, header, and control-size
  metrics. It owns compact/normal/large/hero values rather than storing only the normal control height.
- `HnMetrics` is the single QML facade over `MetricTokens`. The current metric properties on `HoloniightPalette` and
  the separate hardcoded `HnControlMetrics` singleton are removed, not retained as forwarding aliases.
- Shape radii and chamfers remain in a dedicated shape model; configuration selects or scales that model without
  moving shapes into the color palette.
- Typography family/size choices are appearance configuration. Derived typography role sizes are a separate
  typography model, not color or general layout metrics.
- A numeric constant stays component-local unless at least two independent components share the same semantic role;
  visual coincidence alone is not sufficient to promote it to `MetricTokens`.
- ANSI values remain color tokens, but terminal export is not automatically in scope.
- Removing metrics from `ColorTokens` includes updating QML properties, controls, tests, examples, documentation, and
  equality/variant invariants. No forwarding aliases remain after integration unless an explicit external API
  compatibility requirement is accepted.

### Clean-break completion

- The final code reads and writes only the accepted canonical appearance document.
- `theme.conf` and `appearance.json`, or whichever current files are superseded, are no longer watched or parsed.
- Appearance fields are removed from `config.toml`; unrelated shell configuration is preserved.
- No automatic migration or permanent fallback is implemented; old files remain untouched and inert.
- Environment overrides are reduced to a documented minimal test/deployment surface and do not silently compete with
  the saved user choice.

## Remaining acceptance work

1. Create and publish the `holonight-config` repository and add it to the umbrella at an exact baseline.
2. Create one local SDD per participating repository, link each here and in `TASKS.md`, and verify that all use the
   field names, defaults, dependency direction, and clean-break rules above.
3. Settle exact default values and numeric ranges in the `holonight-config` SDD, using the HoloNight design system as
   evidence rather than inheriting whichever current file happens to differ.
4. Decide whether secret-storage remediation is fully inside the Shell work package or a linked prerequisite security
   initiative. Appearance/config separation itself remains mandatory here.
5. Record published baselines and change repository packages from `Planned` to `Ready` only after the contracts agree.

## Non-goals

- Cross-toolkit GTK, Electron, Java, or Qt 5 appearance adapters; those resume after this foundation is integrated.
- A general settings daemon or configuration framework for every HoloNight product.
- Combining all HoloNight configuration into one file.
- Persisting generated semantic palettes in the user-selection document.
- Preserving accidental current formats as public stable APIs.
- Moving shell-only behavior into the global appearance schema merely because it currently sits under an
  `[appearance]` TOML table.
- Solving every credential-storage concern in the ecosystem; this initiative enforces separation from appearance and
  records any remaining security work explicitly.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-qt` | Theme/shape model cleanup; color-versus-metric token separation; adoption of the canonical appearance reader contract | Pending |
| `holonight-config` (repository to create) | Canonical appearance schema, defaults, validation, path, TOML serialization, atomic write, diagnostics, and test helpers | Pending repository and local SDD |
| `holonight-settings` | Remove duplicate schema/writer logic; adopt the canonical API; keep shell-product configuration separate and preserve unrelated values | Pending |
| `holonight-shell` | Adopt canonical appearance notifications; remove independent theme parsing/path logic; keep shell-only configuration and portal projection correctly separated | Pending |
| umbrella | Field/owner ledger, cross-repository contract, dependency order, pins, and final clean-break verification | This initiative |

`holonight-config` must be created, published, and pinned before repository-local implementation begins.
`holonight-appearance-adapters` translates resolved appearance into external toolkit outputs and must not become the
source of the user's selection.

## Cross-repository contracts to settle

### Field classification ledger

Before acceptance, every currently supported field must have exactly one classification and owner. The ledger must
cover at least:

- scheme, accent, dark/light/system semantics;
- UI, fixed, header/title, display/clock font families and sizes;
- icon and fallback icon themes, cursor theme, and scale factor;
- transparency and blur semantics, units, and applicability;
- corner style, shape scale, base radius, and base chamfer;
- shell workspace/tray/background/widget/notification/calendar/OSD settings;
- weather/calendar credentials and private URLs without recording their values.

### Read, write, and notification contract

The accepted contract must name:

- the only authoritative on-disk document and schema version;
- the only schema API and default catalog;
- the user-facing writer and atomic commit behavior;
- validation/failure behavior and rollback;
- live reload ordering and whether each consumer reloads live or on restart;
- the projection from canonical selection to resolved semantic appearance;
- test-only overrides and their precedence;
- deletion or inert-file behavior for every superseded path.

### Dependency direction

The shared schema layer must be lower-level than Qt rendering, Settings UI, Shell services, and appearance adapters.
It must not require Qt GUI/QML or application-owned targets. Qt-specific conversion from neutral values belongs in
`holonight-qt`; portal and compositor projections belong in their owning consumers.

## Dependency order

1. Umbrella field/owner audit and target-architecture decision.
2. `holonight-config` implements the canonical neutral schema, validation, serialization, and diagnostics contract
   and publishes it.
3. `holonight-qt` separates token responsibilities and adopts the canonical appearance input.
4. `holonight-settings` adopts the canonical writer and removes appearance from shell-product TOML writes.
5. `holonight-shell` adopts the canonical reader/notification contract and removes independent theme parsing.
6. Umbrella pins published revisions and verifies the clean break at the exact revisions.

Provider revisions must be published and pinned before dependent consumer work starts.

## Integration acceptance criteria

- [ ] Every current field is classified and has one schema owner, writer, and documented consumer set.
- [ ] One versioned canonical appearance document replaces the current appearance state spread across three files.
- [ ] No canonical appearance field has a second persisted authority or contradictory derived copy.
- [ ] Appearance saving is atomic and cannot partially update multiple appearance files.
- [ ] Appearance changes do not parse or rewrite secret-bearing product configuration.
- [ ] Superseded readers, writers, watchers, path helpers, environment aliases, and duplicated defaults are removed.
- [ ] `ColorTokens` contains colors only; metrics and shapes have separate, non-duplicated authorities.
- [ ] Qt/QML, Settings, Shell, portal, and adapter-facing tests cover valid, missing, invalid, update, and rollback behavior.
- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Manual dark/light, accent, typography, shape, Shell, and Settings checks pass under Hyprland.
- [ ] Commands, results, versions, cleanup observations, and verification date are recorded in the final integration row.
