# Shared window color precision and labwc selection colors

The Qt [shared window contract](../holonight-qt/docs/shared-controls-usage-guide.md)
and [labwc theme projection](../holonight-appearance-adapters/docs/labwc-theme.md)
keep application canvas and titlebar on `background` / `QPalette::Window`; content
panels remain `surface` / `QPalette::Base`. Per-window RGB8 minimum requests prevent
RGB565 rounding without changing renderer selection or public palette APIs.

The adapter projects subtle selection (including alpha) and accent to both snapping
overlays and both switcher styles. Existing staging, ownership, rollback, override
handling and conservative revert stay responsible for these generated files.
Fixed translucent-black shadows remain intentional.

Both components build against host-installed dependencies. Qt is verified before its
installed-package consumer; the adapter consumes installed Qt packages independently,
with no new public dependency contract or required publication order. Focused window
format/palette tests, semantic generator tests and CLI regeneration/override regressions
cover the changes. Private-prefix installed-package and isolated headless compositor
checks provide integration validation; routine evidence belongs in ignored build trees.

Validation used native component builds and the focused Qt dark/light palette,
window format, software canvas, semantic resolver, adapter generator, CLI and
installation tests. The Qt package consumer uses its own staged prefix rather than
host installation writes. Isolated labwc screenshots verified exact titlebar/canvas
pixels for both window types in dark (`#0c1118`) and light (`#e7eef5`) schemes with
OpenGL and software clients. Both snapping overlays and classic/thumbnail switchers
were inspected in both schemes using private virtual input. Overlay background and
border enablement was explicitly set in that disposable visual fixture; the generated
theme leaves it untouched. Evidence is under `build/window-colors/` and the component
`build/dev/window-*.log` files.
