# GTK Visual Fidelity

Status: Draft

Priority: Low

Scheduling: Deferred until explicitly prioritized.

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Bring conventional GTK 3 and GTK 4 applications visually closer to the semantic colors and typography of
`holonight-qt`, while preserving the standards-based dark-mode, accent, portal, and native-fallback behavior
integrated by Cross-Toolkit Visual Consistency.

The initiative should evaluate a generated HoloNight GTK theme for conventional GTK applications, improve the
mapping from arbitrary HoloNight accents to toolkit-supported accent mechanisms, and define portable UI, document,
and monospace font roles. Libadwaita applications should receive the closest supported system preferences by
default. Exact HoloNight surface styling for libadwaita is limited to HoloNight-owned or explicitly opt-in
applications unless upstream adds a stable desktop-wide palette contract.

## Motivation and fidelity targets

### Accent

- Continue publishing the exact HoloNight sRGB accent through the Settings portal.
- Define deterministic mappings to toolkit-native named accents where exact RGB consumption is unavailable.
- Measure perceptual color distance and foreground/background contrast for every supported scheme and accent.
- Allow HoloNight-owned GTK/libadwaita applications to consume exact semantic accent, foreground, focus, and
  selection tokens through supported application CSS variables.

### Surfaces

- Evaluate generated, versioned GTK 3 and conventional GTK 4 themes derived from the canonical HoloNight semantic
  export.
- Cover window, view, header, elevated/card, popover, dialog, selection, border, focus, disabled, and semantic status
  surfaces without copying Qt widget implementation details.
- Preserve native libadwaita surface hierarchy for unmodified third-party applications.
- Require parser, contrast, widget-state, application-startup, and rollback gates before enabling a generated theme
  by default.

### Typography

- Retain the canonical UI and monospace preferences and evaluate a distinct document-font role.
- Map portable roles to GTK settings and supported libadwaita document, body, heading, caption, and monospace
  semantics.
- Keep display/branding typography application-owned where GTK exposes no stable desktop-wide role.
- Verify mixed-DPI metrics, fallback fonts, weight availability, truncation, and accessibility scaling.

## Non-goals

- Pixel-identical Qt and GTK controls, layout, metrics, animations, or widget structure.
- Replacing libadwaita, patching third-party applications, injecting libraries, or overriding application resources.
- Making a global libadwaita user stylesheet part of the supported default experience.
- Overriding application-owned themes in GIMP, browsers, Electron applications, IDEs, terminals, or other bespoke
  surfaces.
- Expanding the canonical schema before discovery proves that a new portable semantic field is required.
- Starting repository implementation while this initiative remains deferred and `Draft`.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| umbrella | Support boundaries, GTK/libadwaita version matrix, visual comparison protocol, exact-pin integration, and acceptance decisions | This initiative |
| `holonight-qt` | Existing semantic token source and reference-rendering fixtures; no GTK implementation | Pending |
| `holonight-config` | Canonical typography schema changes only if discovery accepts a portable document-font role | Pending |
| `holonight-appearance-adapters` | Accent translation, generated GTK theme artifacts, installation, apply/revert ownership, diagnostics, and compatibility tests | Pending |
| `holonight-settings` | User-facing selection, preview/status, explicit opt-in boundaries, and reversible orchestration | Pending |

## Proposed cross-repository contracts

These are discovery hypotheses, not accepted interfaces:

- Semantic colors remain sourced from the versioned HoloNight export; GTK artifacts are generated outputs rather
  than a second palette source.
- The exact portal accent remains authoritative where a consumer supports arbitrary RGB. Named toolkit accents use
  a documented deterministic approximation with contrast validation.
- GTK 3 and GTK 4 outputs are separately generated and version-tested. A successful parser probe for one GTK major
  does not imply compatibility with the other.
- Adapter-owned theme files and settings use compare-and-swap rollback and preserve unrelated user CSS, settings,
  and application preferences.
- Libadwaita receives supported system color-scheme, accent, UI font, document font, and monospace preferences.
  Third-party libadwaita surface palettes remain native unless a stable upstream contract is discovered.
- HoloNight-owned applications may opt into exact semantic CSS variables without changing the promise for
  third-party applications.

## Dependency order

1. Inventory installed/supported GTK 3, GTK 4, and libadwaita versions and representative applications; measure the
   current accent, surface, and typography differences from HoloNight Qt.
2. Settle supported fidelity tiers, semantic mappings, version lifetime, installation paths, rollback ownership,
   visual-test methodology, and the libadwaita boundary.
3. Extend the canonical typography contract only if the document-font discovery gate accepts it.
4. Implement and validate generated GTK 3 and conventional GTK 4 artifacts in Appearance Adapters.
5. Add Settings orchestration only after artifact ownership and rollback behavior are stable.
6. Run umbrella exact-pin automated and user-operated integration across representative applications and displays.

Provider revisions must be published and pinned before dependent consumer work starts. No work package becomes
`Ready` until the initiative is prioritized and its contracts are accepted.

## Integration acceptance criteria

- [ ] Supported GTK/libadwaita versions, applications, fidelity tiers, and native fallbacks are explicit.
- [ ] Accent mappings pass documented perceptual-distance and contrast gates for every canonical combination.
- [ ] Generated GTK 3/4 themes pass version-specific parser, widget-state, startup, dialog, accessibility, and
      mixed-DPI checks without modifying unrelated user configuration.
- [ ] Typography roles have documented GTK/libadwaita mappings, fallbacks, and accessibility behavior.
- [ ] Third-party libadwaita applications retain native surfaces and remain fully functional.
- [ ] Apply, upgrade, partial-failure, and Restore Native Defaults flows are atomic and reversible.
- [ ] Every repository work package has a published commit and passed local and canonical CI verification.
- [ ] Participating submodules are clean and pinned to published commits with compatible contracts.
- [ ] Exact-pin integration records automated results, representative visual observations, version boundaries, and
      final restoration evidence.
