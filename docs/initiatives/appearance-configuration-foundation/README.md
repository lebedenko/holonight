# Appearance Configuration Foundation

Status: Draft

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Establish one clean, versioned source of truth for global HoloNight appearance and a strict separation between color,
metric, shape, and product configuration before cross-toolkit appearance export begins.

This is a prerequisite for the Cross-Toolkit Visual Consistency initiative. The project is pre-stable, so the goal is
to correct weak boundaries now instead of turning the current three-file layout into a permanent compatibility
contract. The final integration must remove superseded readers, writers, files, environment aliases, and duplicated
defaults. A narrowly bounded one-time migration may be accepted for existing developer installations, but ongoing
dual-read or dual-write behavior is not an acceptable end state.

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

## Target architecture constraints

The exact shared-schema repository and serialization format remain acceptance decisions, but every acceptable design
must satisfy the following constraints.

### One canonical appearance document

- One versioned document stores user-selected global appearance.
- It contains only global appearance state: scheme, accent, typography, icon/cursor choices, scale/effects when truly
  global, and shape/profile choices accepted by the final schema.
- Derived values such as dark/light mode are computed from canonical state and are not persisted independently unless
  a documented mode is itself the user's canonical selection.
- Shell behavior, widget layout, tray rules, notifications, weather, calendar, credentials, private URLs, and other
  product configuration remain outside the global appearance document.
- A save is atomic at the document level and exposes actionable read/write/validation errors.
- One component owns schema definitions, defaults, validation, path resolution, parsing, serialization, and migration.
  Settings is the user-facing writer, not a second schema implementation.
- Consumers use the shared API or a generated contract; they do not independently parse selected fields.

### Configuration security boundary

- Appearance changes never rewrite files containing credentials, access tokens, authenticated feed URLs, or other
  private service configuration.
- Secrets move to an appropriate secret store or a separately owned product configuration as determined by the
  repository-local design; secret migration itself may be split into a security follow-up if it exceeds this
  initiative, but appearance must cease sharing its transaction boundary with them.
- Tests and documentation use redacted fixtures only.

### Token taxonomy

- `ColorTokens` contains `QColor` semantic roles only.
- Layout, stroke, spacing, sizing, and typography metrics have a separately named metric model with one authority per
  role and a deliberate C++/QML exposure contract.
- Shape radii and chamfers remain in a dedicated shape model; configuration selects or scales that model without
  moving shapes into the color palette.
- ANSI values remain color tokens, but terminal export is not automatically in scope.
- Removing metrics from `ColorTokens` includes updating QML properties, controls, tests, examples, documentation, and
  equality/variant invariants. No forwarding aliases remain after integration unless an explicit external API
  compatibility requirement is accepted.

### Clean-break completion

- The final code reads and writes only the accepted canonical appearance document.
- `theme.conf` and `appearance.json`, or whichever current files are superseded, are no longer watched or parsed.
- Appearance fields are removed from `config.toml`; unrelated shell configuration is preserved.
- A one-time migration, if accepted, is deterministic, idempotent, backed up or recoverable, and deleted after a
  documented pre-stable transition window. Permanent fallback is prohibited.
- Environment overrides are reduced to a documented minimal test/deployment surface and do not silently compete with
  the saved user choice.

## Decisions required before acceptance

1. Select the canonical document format and path. Evaluate expanding versioned JSON, extracting a dedicated TOML
   appearance document, and any shared-schema packaging consequences; do not select a format only because one current
   implementation already uses it.
2. Assign the shared appearance schema/API to a repository that can be consumed without inverted dependencies. In
   particular, `holonight-qt` must not depend on an application repository merely to read global state, and non-Qt
   consumers must not depend on Qt GUI types.
3. Classify every current field as global appearance, shell-only product configuration, derived output, deprecated,
   or secret/private integration state.
4. Define the single writer and the notification/reload contract for Qt, Shell, Settings, portals, and future
   adapters.
5. Decide whether a one-time developer migration is worth implementing. There is no requirement to preserve the
   current pre-stable formats indefinitely.
6. Define the metric-token structure and the boundary among general design metrics, control-size metrics, shape
   tokens, and component-local constants.

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
| Shared configuration owner (TBD) | Canonical appearance schema, defaults, validation, path, serialization, atomic write, and optional one-time migration | Pending ownership decision |
| `holonight-settings` | Remove duplicate schema/writer logic; adopt the canonical API; keep shell-product configuration separate and preserve unrelated values | Pending |
| `holonight-shell` | Adopt canonical appearance notifications; remove independent theme parsing/path logic; keep shell-only configuration and portal projection correctly separated | Pending |
| umbrella | Field/owner ledger, cross-repository contract, dependency order, pins, and final clean-break verification | This initiative |

If the shared configuration owner is a new repository, it must be created and pinned before repository-local
implementation begins. `holonight-appearance-adapters` is not automatically that owner: adapters translate resolved
appearance into external toolkit outputs and must not become the source of the user's selection by accident.

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
- deletion and migration behavior for every superseded path.

### Dependency direction

The shared schema layer must be lower-level than Qt rendering, Settings UI, Shell services, and appearance adapters.
It must not require Qt GUI/QML or application-owned targets. Qt-specific conversion from neutral values belongs in
`holonight-qt`; portal and compositor projections belong in their owning consumers.

## Dependency order

1. Umbrella field/owner audit and target-architecture decision.
2. Shared configuration owner implements the canonical neutral schema, validation, serialization, and migration
   contract and publishes it.
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
- [ ] Commands, results, versions, migration/cleanup observations, and verification date are recorded in the final integration row.
