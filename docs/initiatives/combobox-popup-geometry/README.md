# ComboBox Popup Geometry

Status: Integrated

## Goal

Keep scaled shared ComboBox popups aligned with their collapsed controls by expressing popup geometry in the same
window-overlay scene coordinate system, and remove the greeter-only geometry workaround.

## Non-goals

- Add support for rotation, shear, or non-uniform scaling.
- Change popup styling, placement policy, scrolling, delegates, or keyboard behavior.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-qt` | Overlay-relative popup parenting, rendered-coordinate regression coverage, package `0.1.1` | [`docs/sdd/combobox-popup-geometry/`](../../../holonight-qt/docs/sdd/combobox-popup-geometry/) |
| `holonight-greeter` | Remove the footer workaround and require the corrected package | [`docs/sdd/visual-refinement/`](../../../holonight-greeter/docs/sdd/visual-refinement/) |

## Cross-repository contracts

`Holonight.ComboBox` owns popup parenting and geometry. Its `Popup.Item` is parented to `Overlay.overlay`, and its
scene-space position and uniform-scale calculations are refreshed before every open. Consumers do not reparent the
popup or override its margins. The corrected CMake package contract is version `0.1.1`.

Implementation started from `holonight-qt@1858c5e` and `holonight-greeter@39a38da`. The integrated revisions are
`holonight-qt@8b25b72` and `holonight-greeter@e89abc9`, both published on their canonical remotes.

## Dependency order

1. `holonight-qt`: provide and publish the `0.1.1` popup geometry contract.
2. `holonight-greeter`: adopt the published provider revision and remove its local workaround.
3. Umbrella integration review and gitlink updates.

Provider revisions must be published and pinned before dependent consumer integration is accepted.

## Integration acceptance criteria

- [x] Every repository work package has a published commit and passed local verification.
- [x] Participating submodules are clean and pinned to those published commits.
- [x] Cross-repository contracts are compatible at the pinned revisions.
- [x] Integration builds and tests passed in provider-first dependency order.
- [x] User confirmed the installed scaled footer selector popup aligns and behaves correctly on the physical display.
