# Live appearance propagation

Scheme, accent, icon and typography edits must reach existing windows without directory reloads or selection changes. No schema migration or artwork changes are required.

## Contracts and dependency order

1. [Qt](../../../holonight-qt/docs/sdd/live-appearance/DESIGN.md) exports `HolonightQt::Icons` and `holonight/icons/hniconengine.h`. The shared engine resolves current icon themes and semantic SVG roles while retaining authored shading and fixed paints. Platform hints update on appearance changes, including icon-only changes, without replacing explicit application primary-theme overrides.
2. [File Browser](../../../holonight-file-browser/docs/sdd/live-appearance/DESIGN.md) Quick consumes the installed Qt engine. `image://icon/<candidate-chain>?revision=<appearance-revision>` separates metadata from names. Unversioned requests remain supported. The bounded physical-pixel cache invalidates hits and misses on revision, primary/fallback theme or search path changes. Core retains its dependency boundary. At cache invalidation, Quick synchronously refreshes the engine appearance reader so independent watcher delivery cannot cache old colors under a new revision.
3. [Settings](../../../holonight-settings/docs/sdd/live-appearance/DESIGN.md) coordinates recognized HoloNight/Papirus variants in the existing appearance transaction. Custom themes and cursors remain explicit. Scheme cards and mode toggles share the setter.
4. [Files](../../../holonight-files/docs/sdd/live-appearance/DESIGN.md) binds all themed icon URLs to `HnAppearance.revision`; shared listings/previews do likewise only for the default provider. New URLs bypass Qt Quick's image cache as well as provider caches.
5. [Adapters](../../../holonight-appearance-adapters/docs/sdd/live-appearance/DESIGN.md) retain last-write ownership and all-or-nothing labwc updates. Diagnostics identify field, path, recorded and actual values. Missing/invalid compositor PID reports unavailable reload after asset changes. Settings surfaces these details with Integrations guidance.

Build and stage Qt, then File Browser before native Settings/Files consumers. Use installed-package tests, including Core-only consumers, focused cache/rendering, transaction and adapter tests. Broader container acceptance is reserved for remaining concrete risks. Native desktop interaction is manual. Do not publish, change umbrella pins, or modify host appearance/configuration.

## Native visual acceptance

With Files open, switch dark to dark, light to dark, dark to light, and accents repeatedly. Check Places, Devices, list/grid, information panel and Quick Look; folder fronts must retain shading and emblems. Selection and directory state must survive. Change interface family/size repeatedly and check labwc decorations, Alt+Tab and workspace OSD. This requires a user-run native session check, after explicitly reconciling any ownership conflict.
