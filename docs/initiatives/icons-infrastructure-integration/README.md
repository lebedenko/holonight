# Icons infrastructure integration

Status: Accepted

## Goal

Build, validate, install, upgrade and remove the restructured icon themes through the umbrella tooling.

## Non-goals

- Changing consumer defaults, existing user settings, automatic variant selection or artwork.
- Publishing the umbrella commits or installing into the live system.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| holonight-icons | Validated system packaging, documentation and regression tests | [SDD](../../../holonight-icons/docs/sdd/umbrella-packaging/README.md) |
| umbrella | Task wrappers, installation lifecycle, dependency checks, CI and pin | This contract and ledger |

## Cross-repository contracts

`python3 holonight-icons/scripts/stage.py --destdir <root>` builds and validates both themes and the
template bundle before copying into unused `usr/share/icons/HoloNight`, `usr/share/icons/HoloNight-Dark`
and `usr/share/holonight-icons` destinations. It preserves relative aliases and attribution, requires
no host cache tools or privilege, and does not create installation backups. Python 3.10+ is required.
The existing user-local installer and explicit recoloring command retain their contracts.

HoloNight means light; HoloNight-Dark means dark. Papirus, Breeze and hicolor supply inherited icons.
Umbrella rendering verification uses the umbrella-pinned holonight-qt checkout. System installation
owns both themes, their generated caches and the bundle. Upgrades remove only unchanged obsolete
icons-owned artifacts; modified and unowned files are preserved and reported.

## Dependency order

1. Icons packaging from `7342a0947b960191b3e0c32cfd4f4c49ad2e973f`, verified with Qt
   `863af4183bdf09ce05199b37e8f5dfb46a311ba1`.
2. Publish verified icons changes, confirm remote availability, and checkpoint the umbrella pin.
3. Umbrella adoption and final integration review at the published pin.

## Integration acceptance criteria

- [ ] Icons package and documentation pass local verification and are published.
- [ ] Icons and renderer checkouts are clean at the accepted published pins.
- [ ] Disposable-root staging, ownership, collision, upgrade and uninstall tests pass.
- [ ] Theme validation, rendering, preview inspection, licensing and installer checks pass.
- [ ] Final ledger records commands, results, date and latest available CI status.

No pointer/focus automation or live installation is required: artwork and consumer behavior are unchanged.
Icons publication is authorized; umbrella checkpoints remain local. Unrelated checkout changes are excluded.
