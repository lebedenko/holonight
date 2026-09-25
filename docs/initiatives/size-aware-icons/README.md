# Size-aware icons and shared Qt recoloring

Status: Accepted

## Goal

Give applications using the HoloNight platform theme size-aware icon lookup and palette-aware semantic rendering, with an explicit QML icon contract. Document the icon-theme artwork required for Dolphin's Places and Devices views.

## Non-goals

- Replacing the current colorful 24 px Places and Devices artwork in this initiative.
- Changing Files' sidebar or file-view icon choices.
- Claiming Dolphin's visible result before replacement artwork is installed and manually checked.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-icons` | Small and large icon-theme contract | [Icon contract](../../../holonight-icons/docs/sdd/size-aware-icons/README.md) |
| `holonight-qt` | Size-aware engine and explicit QML rendering API | [Shared renderer](../../../holonight-qt/docs/sdd/size-aware-icons/README.md) |
| `holonight-shell` | Shell icon caller migration | [Shell migration](../../../holonight-shell/docs/sdd/size-aware-icons/README.md) |
| `holonight-files` | Preserve Files provider and fallback choices with explicit rendering | [Files migration](../../../holonight-files/docs/sdd/size-aware-icons/README.md) |
| `holonight-ai` | Provider asset caller migration | [AI migration](../../../holonight-ai/docs/sdd/size-aware-icons/README.md) |
| `holonight-settings` | Navigation asset caller migration | [Settings migration](../../../holonight-settings/docs/sdd/size-aware-icons/README.md) |
| `holonight-pkg-manager` | Package asset caller migration | [Packages migration](../../../holonight-pkg-manager/docs/sdd/size-aware-icons/README.md) |
| `holonight-viewer` | Empty-state asset caller migration | [Viewer migration](../../../holonight-viewer/docs/sdd/size-aware-icons/README.md) |

## Cross-repository contracts

Ordinary Places and Devices names resolve to monochrome semantic artwork at 16–24 px and colorful artwork at 32 px and above. Explicit `-symbolic` names remain monochrome at all sizes. Theme metadata and aliases determine lookup; a separate artwork replacement must satisfy this contract.

`HnIcon` accepts either `name` for a theme icon or `source` for an asset or provider URL, plus `rendering: HnIcon.Original` or `HnIcon.Semantic`. Semantic provider URLs are unsupported and report `hasError`. Original provider URLs remain displayable. `QIcon` uses the application palette; QML supplies component colors.

## Dependency order

1. `holonight-icons` contract and `holonight-qt` engine/API, independently.
2. Migrate Shell, Files, AI, Settings, Packages, and Viewer against the verified local `holonight-qt` revision.
3. Publish the completed repository commits and pin those revisions before umbrella integration.
4. Run umbrella integration after all repository work packages are done and their exact commits are published.

All repository implementation is committed locally. No commit in this initiative has been pushed or pinned. The current umbrella gitlinks remain authoritative until publication and integration.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] GTK 3 recoloring and GTK 4 symbolic recognition pass against generated theme fixtures.
- [ ] Manual Dolphin check after separate artwork replacement: small Places, large file-view icons, and selected-row contrast.
