# Application icon refresh

Status: Accepted

## Goal

Use the four user-supplied SVGs from `~/Pictures/hn-apps/` in AI, Packages, Settings, and Shell.

## Non-goals

- Redesigning artwork or changing application behavior.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-ai` | Replace its bundled app icon | [Specification](../../../holonight-ai/docs/sdd/application-icon-refresh/SPEC.md) |
| `holonight-pkg-manager` | Replace its bundled app icon | [Specification](../../../holonight-pkg-manager/docs/sdd/application-icon-refresh/SPEC.md) |
| `holonight-settings` | Replace its bundled app icon | [Specification](../../../holonight-settings/docs/sdd/application-icon-refresh/SPEC.md) |
| `holonight-shell` | Replace its bundled app icon | [Specification](../../../holonight-shell/docs/sdd/application-icon-refresh/SPEC.md) |

## Cross-repository contracts

Existing asset names, Qt resource aliases, and installation paths remain stable. Each replacement is independent and has no provider dependency.

## Dependency order

1. Replace and verify the four independent app-owned assets.
2. Publish each app commit and pin it in the umbrella (authorized 2026-10-02).
3. Complete the final integration review, including manual visual checks.

## Integration acceptance criteria

- [x] Every repository work package has a published commit and passed local verification.
- [x] Participating submodules are clean and pinned to those published commits.
- [x] Existing resource consumers resolve the replacement artwork (clean app builds passed).
- [ ] Required integration checks pass at the pinned revisions.
