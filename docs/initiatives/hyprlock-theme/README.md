# HoloNight Hyprlock Theme

Status: Accepted

## Goal

Ship a self-contained HoloNight lock screen for hyprlock 0.9.6 and newer, with a system-wide fallback configuration,
bundled visual assets, PAM authentication, and resilient read-only status indicators.

## Non-goals

- Runtime palette synchronization, clickable controls, fingerprint configuration, suspend, shutdown, and other
  locker implementations are deferred.
- The external visual mockup is not distributed.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-hyprlock` | Theme configuration, assets, status helper, packaging, and local verification | [Hyprlock theme SDD](../../../holonight-hyprlock/docs/sdd/hyprlock-theme/README.md) |
| umbrella | Repository registration, published pin, and final integration record | This initiative |

## Cross-repository contracts

The product targets hyprlock 0.9.6 or newer and introduces no Qt, QML, or other HoloNight API dependency. Its only
internal config-to-script interface is `/usr/libexec/holonight-hyprlock/status` with the `user`, `volume`, and
`battery` subcommands. Each is read-only, emits at most one Pango-safe line, and degrades without blocking the locker
when an optional provider is absent. The Wi-Fi indicator and keyboard layout are rendered directly by Hyprlock.

Production installation uses `/etc/xdg/hypr/hyprlock.conf` as a fallback, with assets below
`/usr/share/holonight-hyprlock`. A user's own hyprlock configuration takes precedence.

## Dependency order

1. Implement and publish `holonight-hyprlock` from baseline `b22cb16`.
2. Register and pin the published repository in the umbrella.
3. Perform umbrella integration review and required manual lock-screen acceptance.

## Integration acceptance criteria

- [x] The product work package has a published commit and passed local verification.
- [x] The submodule is clean and pinned to that published commit.
- [x] The three status-helper commands and installed absolute paths match the local SDD.
- [x] CMake, CTest, staged-install, config-safety, and asset checks pass at the pinned revision.
- [ ] Manual checks cover layout fidelity, multiple monitors, avatars, live state, Caps Lock, PAM failure/success, and
  verbose-log resource errors.
