# Viewer HoloNight alignment

Status: Integrated

## Goal

Align Viewer with the unified runtime controls contract, application structure and owned umbrella installation without changing its application identity, formats or interaction design.

## Non-goals

Shared-provider implementation, holonight-files, portal redesign, new features, historical release deferrals and the draft shared CI image initiative.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| holonight-viewer | Runtime controls, private application structure, checks and staging | [Alignment SDD](../../../holonight-viewer/docs/sdd/holonight-alignment/README.md) |
| umbrella | Registration, published pin, installer dependency order and preflight | This initiative |

## Cross-repository contracts

Viewer consumes published Config and Qt providers. Runtime controls use `QtQuick.Controls as Controls`; Core and composite imports remain explicit. Generic CMake honors caller-supplied provider paths. The HolonightViewer URI, hn-viewer executable, CLI and public desktop identity remain stable. System payload ownership and removal belong to the umbrella; existing collisions are rejected and modified files preserved.

## Dependency order

1. Existing published Config and Qt provider pins (no provider changes).
2. Viewer implementation and local verification, then publication.
3. Umbrella registration, published gitlink and integration review.

## Integration acceptance criteria

- [x] Viewer checks and CI pass with declared dependencies; verified commit is published.
- [x] Participating submodules are clean and pinned to published revisions.
- [x] External build, explicit provider selection and staged /usr runtime pass.
- [x] Installer dependency diagnostics, ownership, collisions and modified-file preservation pass.
- [x] Native default/Fusion appearance and interaction checks pass with user participation.
