# First-Class Sway Support

Status: Integrated

## Goal

Support Sway 1.12 beside Hyprland 0.56.2 with automatic, neutral compositor selection, shared safe layer-surface
lifecycle handling, compositor-aware sessions, and truthful capability-based behavior on unknown Wayland compositors.

## Non-goals

- Prefer Sway or Hyprland when compositor identity is ambiguous.
- Add Sway scratchpad integration or compositor-specific settings UI.
- Change Config, Settings, icons, package manager, appearance adapters, system services, daemons, or greeter product code.
- Preserve internal Hyprland-only C++, QML, script, or desktop-entry compatibility contracts.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-qt` | Optional `HolonightQt::Wayland` layer-surface lifecycle component | `docs/sdd/shared-wayland-surface-host/` |
| `holonight-shell` | Compositor subsystem, all surface adoption, session delivery, and portal integration | `docs/sdd/sway-compositor-support/` |
| `holonight-ai` | Quick-panel adoption of the shared surface host | `docs/sdd/shared-wayland-surface-host-adoption/` |
| `holonight-greeter` | Unchanged generic discovery verified against both installed session entries | Not required (verification only) |

## Exact baselines

- `holonight-qt@8b25b721e7a4`
- `holonight-shell@791ec98e87b1`
- `holonight-ai@6868ac8775ac`
- `holonight-greeter@e89abc949b0c` (inspection and integration verification only)

## Cross-repository contracts

`holonight-qt` exports an optional `Wayland` package component as `HolonightQt::Wayland`. Existing theme and style
consumers must not acquire Wayland dependencies unless they request that component. The component owns the
`wlr-layer-shell` protocol binding and the complete layer-role/window lifecycle through `LayerShellContext`,
`LayerSurfaceSpec`, and `LayerSurfaceHost`. Consumers never hide or destroy a Qt window while its layer role is live.

Shell publishes one atomic, compositor-neutral snapshot through `CompositorService`. Workspace identifiers are opaque
strings; numeric slots, names, ordering, kind, output membership, and active/focused/urgent/occupied state remain
independent. Capabilities determine UI visibility and allowed operations. Backend selection happens once at startup
from an unambiguous declared desktop, then an unambiguous runtime marker, otherwise generic Wayland. A declared known
backend remains selected while its socket is unavailable.

Hyprland and Sway retain private protocol details inside their backend directories. Sway IPC uses native-endian
`i3-ipc` framing with bounded payloads, separate request/subscription connections, coherent full refreshes, and
reconnect diagnostics. Generic Wayland publishes only state backed by advertised standard protocols.

Session ownership is independent from compositor identity. Separate installed Hyprland and Sway descriptors invoke
the descriptor-driven `holonight-session`; UWSM-owned sessions stop through UWSM, while direct sessions request native
backend exit. Environment import removes stale variables belonging to the other compositor.

## Dependency order

1. `holonight-qt` publishes the optional shared Wayland surface host (`SWS-101`).
2. At that exact provider revision, `holonight-shell` adopts the host and delivers compositor/session support
   (`SWS-102`), while `holonight-ai` independently adopts the host (`SWS-103`).
3. The umbrella pins published commits and verifies both installed session entries with the unchanged greeter.

Provider revisions must be published and pinned before dependent consumer work starts.

## Integration acceptance criteria

- [x] Every repository work package has a published commit and passed its local verification.
- [x] Participating submodules are clean and pinned to those published commits.
- [x] The optional Wayland package contract works for both Wayland and non-Wayland consumers.
- [x] Hyprland, Sway, and generic backends expose only truthful capabilities at the pinned revisions.
- [x] Root integration builds and tests pass in provider-first dependency order.
- [x] The unchanged greeter discovers, parses, and starts both installed HoloNight session entries.
- [x] User-performed Hyprland, raw/installed Sway, generic compositor, and layer-surface lifecycle checks pass.
