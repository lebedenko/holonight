# Shared image architecture

Status: Integrated

## Goal

Share image inspection, bounded raster decoding and EXIF mechanics through an independently buildable holonight-images provider. Qt codecs remain the extension point.

## Non-goals

New codecs/guaranteed AVIF, KDE, shared QML, workers, global caches, daemons, SVG vector rendering, animation, and fixing Files orientation.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| holonight-images | Device-only processing and installed package | [SDD](../../../holonight-images/docs/sdd/shared-image-architecture/SPEC.md) |
| holonight-viewer | Raster adoption and metadata formatting | [SDD](../../../holonight-viewer/docs/sdd/shared-image-architecture/SPEC.md) |
| holonight-files | Verified-device adoption and metadata formatting | [SDD](../../../holonight-files/docs/sdd/shared-image-architecture/SPEC.md) |

## Cross-repository contracts

C++23, Qt Core/Gui, caller-owned open seekable QIODevice; no pathname reopening. Explicit caller limits; synchronous calls on application workers; cooperative cancellation between codec calls. Outcomes distinguish unsupported, damaged, resource limit, I/O and cancellation. Default intrinsic orientation applies once; Files explicitly ignores it during migration. Inspection reports raw and policy-oriented sizes; decode bounds are in output coordinates. Metadata values are structured, presentation stays local. Optional malformed tags are absent; oversized metadata is skipped and reported separately from raster success. Applications set Qt's process allocation ceiling at startup. The narrow single-bitstream WebP fallback remains private.

## Dependency order

1. Provider implementation, tests and installed package.
2. Viewer and Files local adoption against that exact provider artifact.
3. Publication/pinning when authorized, followed by final umbrella integration.

Provider and consumer publication, pinning, and final integration are complete. The umbrella gitlinks identify the accepted revisions.

## Integration acceptance criteria

- [x] Every repository package has a published commit and local verification.
- [x] Participating submodules are clean and pinned to published commits.
- [x] Contracts are compatible at those revisions.
- [x] Root builds/tests pass in dependency order.
- [x] Manual Viewer navigation/animation/SVG and Files preview checks pass.

## Published delivery

The provider and both consumer migrations are published and pinned. [TASKS.md](TASKS.md) records the revisions,
local verification, publication CI snapshot, and final integration evidence. The new `holonight-images` submodule is registered at
`git@github.com:lebedenko/holonight-images.git` and precedes its consumers in the installer build order.

Final integration passed on 2026-09-22 using the published pins and compatible existing acceptance builds.
The user confirmed manual native ecosystem checks were completed with no issues observed. Files build CI
retains the recorded container Git ownership failure; local acceptance passed. Provider and Viewer build CI passed.

The subsequent Files-only [orientation correction](../../../holonight-files/docs/sdd/image-orientation/SPEC.md)
was published and pinned on 2026-09-22. Files now applies intrinsic orientation to original images and
reports oriented dimensions; cached thumbnails contain already-oriented pixels and are decoded with Ignore.
This supersedes the migration-time Files Ignore policy above without changing the provider or Viewer.
The ledger records its acceptance evidence and publication CI snapshot.
