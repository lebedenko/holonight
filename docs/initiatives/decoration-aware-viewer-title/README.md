# Decoration-aware Viewer toolbar titles

Status: Abandoned

Presentation policy superseded by [backend-aware external title presentation](../external-window-title-presentation/README.md). Historical scope and verification records below remain unchanged.

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Hide image and grid toolbar headings in decorated normal Viewer windows while retaining fullscreen headings and native titles.

## Non-goals

- X11/XWayland, custom decoration plugins, integrated HoloNight CSD and compositor title-text rules.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| holonight-qt | Observational Core decoration helper | [SDD](../../../holonight-qt/docs/sdd/decoration-aware-viewer-title/README.md) |
| holonight-viewer | Heading visibility policy | [SDD](../../../holonight-viewer/docs/sdd/decoration-aware-viewer-title/README.md) |

## Cross-repository contracts

`HnWindowDecoration` in `Holonight.Core` exposes writable `window`, read-only `mode` (Unknown, ServerSide, ToolkitClientSide, Undecorated), and `externalDecorationPresent`. Decorated modes set the boolean true. Unsupported/pending states retain headings. Qt 6.11 private APIs stay provider-owned.

## Dependency order

1. holonight-qt helper
2. holonight-viewer adoption
3. Umbrella integration review

This session explicitly permits local provider → Viewer verification before publication. Pushes and pin updates are not authorized. Final integration requires published revisions and explicit pin authorization.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Required manual ecosystem checks pass.

Replaced by [Decoration-independent Viewer](../decoration-independent-viewer/README.md). Historical implementation and verification are retained.
