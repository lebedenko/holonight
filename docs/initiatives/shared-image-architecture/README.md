# Shared image architecture

Status: Accepted

## Goal

Share image inspection, bounded raster decoding and EXIF mechanics through an independently buildable holonight-images provider. Qt codecs remain the extension point.

## Non-goals

New codecs/guaranteed AVIF, KDE, shared QML, workers, global caches, daemons, SVG vector rendering, animation, and fixing Files orientation.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| holonight-images | Device-only processing and installed package | ../../../holonight-images/docs/sdd/shared-image-architecture/ |
| holonight-viewer | Raster adoption and metadata formatting | ../../../holonight-viewer/docs/sdd/shared-image-architecture/ |
| holonight-files | Verified-device adoption and metadata formatting | ../../../holonight-files/docs/sdd/shared-image-architecture/ |

## Cross-repository contracts

C++23, Qt Core/Gui, caller-owned open seekable QIODevice; no pathname reopening. Explicit caller limits; synchronous calls on application workers; cooperative cancellation between codec calls. Outcomes distinguish unsupported, damaged, resource limit, I/O and cancellation. Default intrinsic orientation applies once; Files explicitly ignores it during migration. Inspection reports raw and policy-oriented sizes; decode bounds are in output coordinates. Metadata values are structured, presentation stays local. Optional malformed tags are absent; oversized metadata is skipped and reported separately from raster success. Applications set Qt's process allocation ceiling at startup. The narrow single-bitstream WebP fallback remains private.

## Dependency order

1. Provider implementation, tests and installed package.
2. Viewer and Files local adoption against that exact provider artifact.
3. Publication/pinning when authorized, followed by final umbrella integration.

Local consumer validation is authorized by the implementation request. Publication and pins are separate pending actions; no unpublished local work is an integrated state.

## Integration acceptance criteria

- [ ] Every repository package has a published commit and local verification.
- [ ] Participating submodules are clean and pinned to published commits.
- [ ] Contracts are compatible at those revisions.
- [ ] Root builds/tests pass in dependency order.
- [ ] Manual Viewer navigation/animation/SVG and Files preview checks pass.
