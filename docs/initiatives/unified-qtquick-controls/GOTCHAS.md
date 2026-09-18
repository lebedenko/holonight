# Unified Qt Quick Controls — gotchas and practical lessons

This is a reference from the [closed initiative](CLOSURE.md), not a new backlog.
Links point to the versioned investigations; do not generalize their observations
to every Qt, KDE or compositor version.

## Styling and composition

| Gotcha | Practical consequence / disposition | Evidence |
| --- | --- | --- |
| A dark palette or selected style name does not prove which control implementation is drawn. | Platform theme, Quick Controls selection, module discovery and application painting are separate. Inspect an actual implementation when diagnosing a mismatch. | [Shared contract](README.md#cross-repository-contracts) |
| Direct style imports and unconditional application style selection can bypass runtime selection. | Owned apps use `QtQuick.Controls as Controls` and embedded defaults; preserve environment, command-line and configuration overrides. Third-party overrides are a compatibility boundary. | [Contract](README.md#cross-repository-contracts) |
| Switching to Fusion does not redesign the whole application. | Core tokens, HoloNight composites, Kirigami wrappers and application-owned surfaces retain their own layout/painting. Basic fallback is intentional for uncovered types. Classify the visible surface before assigning a defect. | [Composition disposition](FINDINGS.md#batch-8-settings-fractional-results-and-composition-disposition--2026-09-17) |
| Style-specific convenience properties may not exist in Fusion. | Keep common consumer logic on standard control APIs; guard optional extensions rather than assuming every style has them. | [Provider implementation](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) |
| Installed execution can accidentally find source/build or host modules. | When investigating deployment, verify loaded origins and executable-relative QML discovery. A build-tree success alone does not establish an installed result. | [Integration evidence](INTEGRATION.md) |
| Palette roles and explicit application overrides matter. | Missing `Light` produced bright fallback-dialog surfaces; the provider role was repaired. Preserve explicitly supplied application palettes. Shared windows also need live default-palette propagation. | [P02](FINDINGS.md#batch-4-palette-investigation-and-repair--2026-09-14), [P03 repair](FINDINGS.md#p03-shared-window-automated-repair--2026-09-17) |

## Interaction and geometry

| Gotcha | Practical consequence / disposition | Evidence |
| --- | --- | --- |
| Forwarding focus through a wrapper can lose the focus reason or create an invisible stop. | Preserve keyboard focus reason and natural child traversal; check first entry and reverse traversal, including hidden/disabled children. Shared form wrappers were repaired. | [Focus repair](FINDINGS.md#manual-focus-acceptance--2026-09-11) |
| Replacing a ComboBox popup can leave a hidden inherited list consuming delegates. | Delegate ownership and scene visibility matter, not just current-index/highlight values. Overlay parenting also changes outside-click dismissal. The provider repairs are accepted. | [Dropdown diagnosis](FINDINGS.md#uqc-206-local-dropdown-repair-checkpoint--2026-09-12), [stronger reproduction](FINDINGS.md#d04-clarification-and-stronger-reproduction--2026-09-12) |
| Scrolling rows beneath a stationary pointer can change hover/selection unexpectedly. | Mouse hover must not override deliberate keyboard navigation merely because content moved. Shared controls and launcher behavior were repaired. | [Pointer-selection repair](FINDINGS.md#stationary-pointer-selection-repair--2026-09-13) |
| Compositor output scale and application DPR are different measurements. | Fractional Qt scaling can expose logical-coordinate conversion errors even at output scale 1. The provider layer-surface conversion was repaired; avoid compensating independently in each consumer. | [S01 repair](FINDINGS.md#s01-provider-repair-and-f05-reduced-diagnosis--2026-09-15) |
| A diagnostic window geometry can create a failure outside intended use. | The greeter caret reproduced in a particular windowed/transformed case; intended fullscreen use passed. The experimental layer workaround softened text and was rejected. No G07 product repair is pending. | [Fullscreen disposition](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16) |

## Known limits retained at closure

- **F05 — external Qt/Hyprland activation behavior:** after VT return, a plain Qt
  reproduction receives keyboard events while focus/rendering does not recover
  normally until further interaction. No HoloNight fix is claimed; the report
  draft was not submitted. [Diagnosis](FINDINGS.md#f05-plain-qt-external-reproduction--2026-09-15).
- **P01 — external KDE/application scheme activation:** repeated Default-scheme
  activation and construction-time callbacks can alter application palettes.
  Provider-free reproduction separates it from the repaired provider palette
  omission. No upstream repair is claimed. [Investigation](FINDINGS.md#batch-4-palette-investigation-and-repair--2026-09-14).
- **Deferred diagnostics:** historical ScrollBar warnings, Haruna crash/Fusion
  hover and Tokodon chevron observations are not all resolved or proven to share
  an owner. They remain non-blocking history, not asserted fixes. A concrete new
  recurrence can be handled as an ordinary bug. [Disposition](FINDINGS.md#batch-3-user-directed-closure--2026-09-16).
- **Coverage boundaries:** third-party account/network surfaces and AI online
  provider behavior were outside the offline scope; package-manager interaction
  was read-only. Disabled/empty controls and unopened popups are not exercised
  merely because their modules loaded. [Latest scoped review](FINDINGS.md#ai-sway-scale-1-iteration--2026-09-19).
- **Product design work:** Settings slider/Appearance composition and AI Temperature
  layout concerns are separate app-local work, not reasons to reopen unification.
  [Scope dispositions](BATCHES.md), [Settings composition](FINDINGS.md#batch-8-settings-fractional-results-and-composition-disposition--2026-09-17).

## Testing lessons

- **An observer can change the program.** Reading every item's palette allocated
  a palette on Qt's root content item and caused stale colors to propagate after
  activation. The observer was repaired; production was not patched around the
  instrumentation. Use passive diagnostics and compare observer-on/off behavior
  when the diagnosis depends on instrumentation.
  [Root cause](FINDINGS.md#uqc-223-observer-induced-palette-reversals--2026-09-18),
  [repair](FINDINGS.md#uqc-224-observer-repair-and-replacement-release--2026-09-18).
- **A namespace suitable for offscreen checks may break a real session.** A
  synthetic `/dev` hid GPU/input/VT devices from Sway. Real-seat helpers needed
  the appropriate device bind; the failure was in the kit.
  [Device-access repair](FINDINGS.md#p03-manual-device-access-repair--2026-09-18).
- **Warnings, crashes and visual bugs are different evidence.** Keep diagnostics
  and uncertain ownership visible, but do not turn every log message into a
  mandatory investigation. In the final AI runs, ScrollBar notices explicitly
  preserved bindings and portal/Secret Service diagnostics accompanied normal
  exits and a no-issues visual report.
- **Test the changed behavior.** Appearance changes warrant focused appearance
  and directly affected interaction checks. They do not automatically require
  recertifying daily-used authentication, service startup or every matrix cell.
  Existing daily use is relevant practical evidence. Expand checks when a concrete
  failure or meaningful change justifies it.
- **Stop when the user goal is met.** Missing formal coverage is a limitation to
  record, not automatically a defect. Kits, ledgers and hashes support diagnosis;
  they must not create an endless acceptance process for early-stage apps.
