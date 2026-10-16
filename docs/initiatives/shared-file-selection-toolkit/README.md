# Shared File Selection Toolkit

Status: implemented, published and pinned; Files accepted natively; Portal and Viewer
walkthroughs pending. The recursive traversal performance repair is published and pinned.
The previous External Dependency Management deferral is replaced by the current
installed CMake package workflow.

The independent `holonight-file-browser` repository serves Files, the portal chooser
and Viewer. Preserve the installed `HolonightFileBrowser` package, Core/Quick target
names and `Holonight.FileBrowser` import. Shared scope includes browsing, selection,
passive views, folder/recursive search, places/devices, thumbnails and image/text/Markdown
inspection. Each application constructs its own sessions and supplies configuration.

The [provider design](../../../holonight-file-browser/docs/sdd/shared-file-selection/DESIGN.md)
defines interfaces and ownership. The original [Files provider design](../../../holonight-files/docs/sdd/filechooser-provider/DESIGN.md)
is historical context. Files owns editing and operations, the portal owns protocol and
destination validation, and Viewer owns its image document and portal-based Open.
Initial adoption must retain existing features; new portal preview/device/grid UI is deferred.

Dependency order: Config/System Services → Qt; Images → Thumbnails; Search;
then File Browser → Files, Viewer and portal. Build native deployment binaries against
host dependencies. Container binaries are acceptance artifacts only. Consumers use
staged installed packages, never source-tree provider includes.

Only File Browser installs browsing headers, libraries, QML modules and CMake exports.
The umbrella transfers prior Files-owned paths through its existing ownership manifest,
rejects duplicate staged owners and unowned collisions, and preserves modified files
on uninstall. No installer protection is bypassed for this extraction.

Acceptance requires installed-package consumers, Core-only and optional-component
checks, existing application regressions, disposable-root upgrade/collision/uninstall
tests, component acceptance and `task check:integration`. Manual native checks cover
Files editing/finder/devices/previews, portal Open/Save/multiple selection and Viewer
grid/thumbnails/playback. Publication must place providers before consumers.

See the [delivery and verification record](TASKS.md) for completed checks and the
remaining manual acceptance.
