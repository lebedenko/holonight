# Shared thumbnail disk cache

Status: Accepted

## Goal

Files and Viewer reuse the same freedesktop thumbnail files through an independently buildable `holonight-thumbnails` library.

## Non-goals

- Shared image decoders, worker pools, memory caches, UI behavior, new formats, a thumbnail daemon, or automatic cache pruning.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| holonight-thumbnails | Cache paths, validation, bounded PNG reads, atomic writes, installed CMake package | [SDD](../../../holonight-thumbnails/docs/sdd/shared-thumbnail-cache/README.md) |
| holonight-files | Replace private disk cache, retain verified source descriptor and preview behavior | [SDD](../../../holonight-files/docs/sdd/shared-thumbnail-cache/README.md) |
| holonight-viewer | Use shared disk cache on worker misses, preserve logical size and memory LRU | [SDD](../../../holonight-viewer/docs/sdd/shared-thumbnail-cache/SPEC.md) |

## Cross-repository contracts

The provider exposes synchronous `lookup` and `store` using a local source URI, modification time, byte size, required pixel dimensions, raster/SVG kind, optional revision and cancellation flag. It owns freedesktop URI hashing, XDG paths and 128/256/512/1024 tiers. Lookup validates PNG dimensions and source metadata before returning pixels. Standard external raster entries are reusable when valid; HoloNight metadata is checked when present. SVG requires HoloNight's rendering-policy marker, and each consumer validates the SVG resource before lookup. A cache failure is a miss and never prevents source decoding. Requests above 1024 pixels remain memory-only. Consumers own image inspection and decoding, workers, in-memory caches, and presentation.

The provider uses C++23 and Qt Core/Gui and exports `HolonightThumbnails::Thumbnails`. Its public header is `<holonight_thumbnails/cache.h>`.

## Dependency order

1. Build, verify, and publish holonight-thumbnails.
2. Verify Files and Viewer against that exact provider revision, then publish them.
3. Update umbrella installer order and published pins, then run integration checks.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to published commits.
- [ ] Cache contracts are compatible at the pinned revisions.
- [ ] Provider and consumer builds/tests and root installer checks pass in dependency order.
- [ ] Required manual Files and Viewer ecosystem checks pass.
