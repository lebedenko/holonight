# Licensing and provenance standardization

Status: Accepted

## Goal

Standardize first-party HoloNight work on `GPL-3.0-or-later`, adopt REUSE 3.3 throughout the ecosystem, document
redistributed third-party material, and remove the non-redistributable Shell weather artwork from published history.

## Non-goals

- Removing objects from external forks, existing clones, or third-party caches that are outside repository control.
- Changing the existing PNG forecast compositor or moon-phase presentation.

## Participating repositories

Every initialized repository participates. Repository-local `REUSE.toml`, notices, provenance records, build files,
and tests are the implementation records; this ledger owns integration state and exact pins.

## Cross-repository contracts

- First-party work uses `GPL-3.0-or-later` and `2026 Andrii L <lebeden@gmail.com>`.
- CI runs `reuse==6.2.0`; local checks use `task license-check`.
- Additional license texts exist only where repository files use them.
- CMake packages install license material below `${CMAKE_INSTALL_DATADIR}/licenses/<package>`.
- Shell weather condition resources use the 18 `01/02/03/04/09/10/11/13/50` day/night SVGs.

## Dependency order

1. Repository-local licensing and provenance commits.
2. Shell history rewrite, replacement artwork, and dependent revision updates.
3. Umbrella pin update and aggregate verification.

## Integration acceptance criteria

- [x] Every repository work package has a published commit and passed its focused licensing verification.
- [x] Participating submodules are clean and pinned to published commits, except the preserved untracked Shell SDD.
- [x] Cross-repository licensing and Shell weather contracts are compatible at the pinned revisions.
- [ ] Full repository builds and tests pass in dependency order.
- [ ] Required manual ecosystem checks pass.
