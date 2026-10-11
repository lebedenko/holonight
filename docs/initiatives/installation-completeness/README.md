# Installation completeness

Status: Accepted

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Make AI and Packages discoverable in application menus and install every pinned submodule, including Hyprlock.

## Non-goals

- Package installation, service enablement, user configuration changes, and automatic publication.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| holonight-ai | AI launcher, Qt identity and fallback icon | [SDD](../../../holonight-ai/docs/sdd/installation-completeness/SPEC.md) |
| holonight-pkg-manager | Packages launcher, Qt identity and fallback icon | [SDD](../../../holonight-pkg-manager/docs/sdd/installation-completeness/SPEC.md) |
| umbrella | Installer module coverage, ownership checks and documentation | This initiative |
| holonight-hyprlock | Existing CMake package consumed unchanged | [Existing SDD](../../../holonight-hyprlock/docs/sdd/hyprlock-theme/README.md) |

## Cross-repository contracts

Launchers use direct installed commands and matching Qt desktop-file names. App SVGs use their existing names
in hicolor. Hyprlock uses its existing /etc/xdg fallback and /usr helper/assets contract; the installer
attributes all payloads through its normal staging manifest and preserves unmanaged-file collision protection.

## Dependency order

1. Independently verify AI and Packages against current pinned providers; verify unchanged Hyprlock package.
2. Publish application changes and explicitly update their umbrella pins.
3. Umbrella integration review

Current pinned provider revisions remain unchanged. Integration at updated application pins follows publication.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Required manual ecosystem checks pass.
