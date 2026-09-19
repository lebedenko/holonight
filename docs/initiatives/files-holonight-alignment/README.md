# HoloNight Files refactoring and onboarding

Status: Accepted

## Goal

Preserve Files behavior and identity while separating application responsibilities and onboarding coordinated installation.

## Non-goals

- Shared-provider APIs, filesystem algorithm changes, or automatic adoption/removal of unmanaged installations.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| holonight-files | Architecture, QML, build and acceptance | [Alignment](../../../holonight-files/docs/sdd/holonight-alignment/README.md) |
| umbrella | Inventory, installer and final integration | This initiative |

## Cross-repository contracts

Existing Config/Qt providers are unchanged. Files retains hn-files, org.holonight.Files, HolonightFiles,
CLI, resource aliases and local TOML formats. The umbrella owns system installation/removal with collision
refusal and hash-based modified-file preservation. Explicit caller provider/import paths are authoritative.
Detailed requirements and verification belong to the local SDD. Publication/pin updates require separate authorization.

## Dependency order

1. Existing pinned Config and Qt providers (no changes).
2. Files implementation and local acceptance at baseline bb34b9ae224106fa993d0b05fd76f9bae880e32b.
3. Published Files handoff, submodule registration and umbrella installer onboarding.
4. Final exact-revision integration and user-assisted native checks.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Required manual ecosystem checks pass.
