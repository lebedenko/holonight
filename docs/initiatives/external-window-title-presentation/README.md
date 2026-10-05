# Backend-aware external title presentation

Status: Accepted

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Viewer hides its heading only when a supported toolkit or compositor interface reports an external title-bar area. Unknown evidence preserves the heading.

## Non-goals

- No custom plugin detection, user override, window controls, movement or resize handling.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-system-services` | Shared compositor core | [SDD](../../../holonight-system-services/docs/sdd/external-window-title-presentation/README.md) |
| `holonight-shell` | Plugin factories and shell adapters | [SDD](../../../holonight-shell/docs/sdd/external-window-title-presentation/README.md) |
| `holonight-qt` | Window presentation bridge | [SDD](../../../holonight-qt/docs/sdd/external-window-title-presentation/README.md) |
| `holonight-viewer` | Conservative heading binding | [SDD](../../../holonight-viewer/docs/sdd/external-window-title-presentation/README.md) |

## Cross-repository contracts

HoloNightSystem::Compositor owns backend factories, snapshots, activation and workspace contracts. ExternalTitleBarState is separate from capabilities and requires exactly one PID/app ID match. Holonight.Core exposes HnWindowPresentation; HnWindowDecoration remains the raw Qt API.

This supersedes the original SSD-implies-external-title policy; prior verification records remain unchanged. Present denotes a reported title-bar area, not theme text visibility. Hyprland, labwc and generic Wayland remain Unknown.

Native checks pending: Hyprland heading visibility, Sway decoration changes, Qt CSD, fullscreen transitions and surface recreation. Offscreen tests do not establish native correctness.

## Dependency order

1. system-services extraction
2. shell adoption
3. Qt bridge
4. Viewer adoption
5. Umbrella integration review

This authorized local implementation uses staged provider install trees before publication. No pushes or gitlink changes are authorized; integration remains pending.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Required manual ecosystem checks pass.
