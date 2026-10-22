# Preview presentation correction

`HnPreviewFrame` is a transparent, zero-padding state host with stable default
240 × 180 geometry. Its enum, component slots and `previewItem` API are unchanged.
Surrounding panes own spacing and surfaces; image renderers own corner treatment.
The current component contract is in
[shared file UI controls](../holonight-qt/docs/sdd/shared-file-ui-controls/README.md).
Historical acceptance records remain unchanged.

An empty selection leaves the preview blank. Pending work without usable content
shows a centered standard BusyIndicator with an accessible name. Available images
remain visible during progressive decoding. Failures without usable content show
an entry icon and muted “No preview available” caption; the reason is available
through a tooltip and accessible description. A bundled generic file icon covers
missing themed icons. Folders and ordinary icon-only entries are normal content.
Selection, metadata, navigation and acceptance do not depend on preview success.

The portal inherits this behavior from FilePreview in holonight-file-browser.
Files keeps its thumbnail transitions and local icon fallbacks in the sidebar and
Quick Look; Quick Look retains metadata on failure. Settings keeps its source
Image outside the state Loader so loading transitions cannot destroy it. Viewer’s
information thumbnail uses the transparent default. The gallery demonstrates all
four states without instructions or loading captions. HnLoadingState is unchanged.

Dependency order: stage holonight-qt (including the generic-file SVG), then
holonight-file-browser, then Files, Settings, Viewer and the portal. No decoder or
public interface changes are required. Validate provider geometry/state tests,
installed package consumption, example startup and QML policies, then focused
consumer preview regressions against the staged packages. Native narrow-layout,
fractional-scale and theme visual comparisons require manual interaction; no
mockup image was included with this implementation request.
