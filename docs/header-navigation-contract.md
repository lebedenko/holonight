# Header navigation contract

Shared API: Holonight.Controls.HnHeaderCloseButton is a runtime Button; applications
supply action or onClicked. HnIconButton forwards icon.name when no source is set.
Actions owns window-close and window-close-symbolic; navigation uses go-previous
and go-next. Publish Icons and Qt before consumers; no pins change in this work.

Local designs: [Qt](../holonight-qt/docs/header-navigation.md),
[Icons](../holonight-icons/docs/header-navigation.md),
[Viewer](../holonight-viewer/docs/header-navigation.md),
[Files](../holonight-files/docs/header-navigation.md).

Acceptance: isolated provider prefix, consumer history/geometry/close regressions,
repository checks and staged runtime checks. Physical mouse, split dragging and
light/dark fractional-scale visual parity are manual native checks.
