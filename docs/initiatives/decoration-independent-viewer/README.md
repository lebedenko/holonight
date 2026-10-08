# Decoration-independent Viewer

Status: Accepted

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Show content headings only in fullscreen; preserve native content titles in every mode. Remove decoration detection without adding preferences or heuristics.

## Non-goals

- Publication, deployment, submodule pin updates, and unrelated Shell edits.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| holonight-viewer | Fullscreen-only heading and accurate native titles | [SDD](../../../holonight-viewer/docs/sdd/decoration-independent-viewer/README.md) |
| holonight-qt | Remove decoration helpers and dependencies | [SDD](../../../holonight-qt/docs/sdd/decoration-independent-viewer/README.md) |
| holonight-system-services | Remove decoration contract; preserve compositor behavior | [SDD](../../../holonight-system-services/docs/sdd/decoration-independent-viewer/README.md) |
| holonight-shell | Compositor adapter and plugin ABI 3 | [SDD](../../../holonight-shell/docs/sdd/decoration-independent-viewer/README.md) |

## Cross-repository contracts

Remove the decoration QML helpers and compositor title-bar observations and explicit refresh API. Preserve inventory/PID/fullscreen, activation and event refresh. Shell plugins use IID /3.0 with matching metadata IID. Viewer reuses its heading computation for grid native titles.

## Dependency order

1. Viewer decoupling
2. Qt cleanup
3. SystemServices cleanup
4. Shell compatibility
5. Umbrella integration review

Local handoffs use explicit staged provider prefixes. Publication and pinning are separate, as authorized in this task. Native Hyprland/Sway checks with decorations enabled/disabled require manual interaction.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [x] Required native Viewer title/toolbar/fullscreen checks passed by user confirmation on 2026-10-08.

Native Viewer title/toolbar/fullscreen checks passed by user confirmation on 2026-10-08. This local acceptance is separate from final review at published, pinned revisions.
