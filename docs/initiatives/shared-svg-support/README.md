# Shared SVG support for Images, Viewer and Files

Status: Accepted

## Goal

Provide explicit shared SVG inspection and bounded rasterization, sharp Files previews and consistent Viewer geometry.
Approved scope: the implementation plan supplied by the user on 2026-09-24.

## Non-goals

- SVGZ, browser rendering, new codec frameworks, linked-resource thumbnail caching or new animation controls.
- Moving persistent renderers, workers, caches, presentation or pathname resolution into Images.
- Publication, pin changes or claiming integration before authorization and verification.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| holonight-images | Synchronous bounded source, facts, resource classification and rasterization | [SDD](../../../holonight-images/docs/sdd/shared-svg-support/SPEC.md) |
| holonight-viewer | Shared mechanics, retained-byte renderer, local-image fallback | [SDD](../../../holonight-viewer/docs/sdd/shared-svg-support/SPEC.md) |
| holonight-files | Explicit SVG dispatch, vector-aware sizes and cache policy | [SDD](../../../holonight-files/docs/sdd/shared-svg-support/SPEC.md) |

## Cross-repository contracts

- Separate public `holonight_images/svg.h`; raster API and its no-upscaling behavior stay unchanged.
- `loadSvg` reads a caller-owned seekable QIODevice from zero, checks reported and actual bytes and returns retained
  bytes with Outcome. Both applications choose a 10 MiB input budget. No provider pathname opening or resolution.
- `inspectSvg` validates XML and resources before renderer loading. Facts retain separate default size, viewBox and
  document size. Prefer positive finite default size; otherwise use a positive finite viewBox. Preserve fractional
  pixel geometry until `svgPixelSize` fits it to an explicit pixel bound, allowing enlargement.
- `rasterizeSvg` revalidates bytes, enforces output-byte limits before QImage allocation and returns a transparent
  premultiplied image. Logical coordinates are not subject to raster source-pixel limits.
- Only fragments and embedded raster images are self-contained. Reject external stylesheets, entity declarations,
  external resources, and unsupported resource-obscuring CSS syntax. Check href, xlink:href and CSS references.
  Image-element fragment hrefs are rejected because Qt treats them as filenames; use/paint fragments are allowed.
  Embedded rasters must decode before SVG loading, preventing Qt's ordinary failed-data filename fallback.
  Policy rejection is Unsupported with SvgResourceReason. An exclusively LocalImageReference rejection lets Viewer
  choose its existing consumer-owned filename-loading path; no other rejection is eligible for that fallback.
- Qt SVG is an explicit library and installed-package dependency. Renderer options retain Qt resource checks;
  Files uses Disabled animation. Viewer can use Enabled without introducing animation controls or new features.
- Files validates before memory/disk cache lookup; uses existing verified descriptor, worker, DPR requests,
  debounce, PNG tiers, revision checks and atomic writes. Mark thumbnails with an SVG policy version. Document
  geometry is separate from rendered pixels; required sizes, adequacy and dispatch upgrades allow enlargement.
  Skip EXIF. Translate unsupported resource explanations; opening in Viewer remains available.
- Viewer retains vector zoom, navigation, clipboard and animation behavior; self-contained renderers load retained
  bytes and previews use the provider. Canvas/information/previews share the default-size-first rule.
- Cancellation is cooperative between Qt calls; byte/output budgets do not bound every renderer intermediate
  allocation and application timeouts do not forcibly terminate Qt rendering.

## Dependency order

1. Images provider SVG-001, baseline `35efad8325f31991deb24149d2e2d8ec388ae8c1`.
2. Viewer SVG-002, baseline `1200adb820c802259af37b583ce076a863036c56`, and Files SVG-003,
   baseline `98936ee55e4e70fdf8236e7c5e8685dda1eac330`.
3. Umbrella integration SVG-004.

Baselines matched clean HEAD, tracked origin/main and umbrella pins during inspection (2026-09-24).
Provider revisions must be published and pinned before dependent consumer implementation starts.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Required manual ecosystem checks pass without pointer/focus automation.
