# Shared File UI Controls

Status: Implemented, published and pinned; visual fine-tuning deferred

## Goal

Provide reusable file-oriented presentation components and adopt them across Files,
Viewer, the portal chooser and Settings’ wallpaper picker. Share appearance,
interaction affordances and accessibility while preserving application behavior
and provider ownership. This initiative covers components **and adoption**;
implementation and automated acceptance are tracked in the coordination ledger.

## References and scope

Use all available participating-application mockups as visual references:

- [Files](../../../holonight-files/docs/mockups/moc1.png): breadcrumbs, detailed listing, preview/metadata and Quick Look.
- [Viewer](../../../holonight-viewer/docs/mockups/moc1.png): thumbnails, image information and keyboard hints.
- [Portal chooser](../../../xdg-desktop-portal-holonight/docs/mockups/file-picker.png): location, detailed columns and selected-entry preview.
- [Settings wallpaper picker](../../../holonight-settings/docs/mockups/change-wallpapers.png): thumbnails, preview and configuration controls.

The source plan mentioned five inspected mockups; four files were located in this
checkout, and the user confirmed using all of them. No unidentified fifth reference
is asserted. Mockups guide presentation; they do not expand the scope below.

Related initiatives:

- [Shared File Selection Toolkit](../shared-file-selection-toolkit/README.md)
  supplies the independent File Browser provider and installed-package boundaries.
- [Consistent Key Hints](../consistent-key-hints/README.md) supplies the existing
  semantic key renderer; this initiative adds labeled composition without changing bindings.
- [FileChooser Portal](../filechooser-portal/README.md) owns protocol and lifecycle
  acceptance. **Portal previews are newly included work here**, previously deferred
  by the toolkit and excluded from the original portal scope. This does not claim
  completion of that initiative’s outstanding acceptance.

## Ownership and local designs

| Repository | Ownership | Local SDD |
|---|---|---|
| `holonight-qt` | Five public controls, gallery, usage documentation and installed public-type coverage | [Shared file controls](../../../holonight-qt/docs/sdd/shared-file-ui-controls/README.md) |
| `holonight-file-browser` | Shared detailed-list presentation, path-to-breadcrumb adaptation and reusable file-preview composition | [Shared file controls](../../../holonight-file-browser/docs/sdd/shared-file-ui-controls/README.md) |
| `holonight-files` | Files adoption and preservation of application interaction | [Shared file controls](../../../holonight-files/docs/sdd/shared-file-ui-controls/README.md) |
| `holonight-viewer` | Viewer adoption and preservation of image/document behavior | [Shared file controls](../../../holonight-viewer/docs/sdd/shared-file-ui-controls/README.md) |
| `xdg-desktop-portal-holonight` | Chooser adoption, selected-entry preview/metadata and protocol preservation | [Shared file controls](../../../xdg-desktop-portal-holonight/docs/sdd/shared-file-ui-controls/README.md) |
| `holonight-settings` | Wallpaper picker adoption and configuration behavior | [Shared file controls](../../../holonight-settings/docs/sdd/shared-file-ui-controls/README.md) |
| Umbrella | Installed-package compatibility and ecosystem acceptance | This contract and [coordination ledger](TASKS.md) |

Each repository work package must deliver its local SDD describing intent,
decisions, interfaces and acceptance. Add links when those documents exist.

## New public component contracts

All five `Hn*` types belong to `Holonight.Controls` in `holonight-qt`. Reuse
existing internal selection foundations and semantic tokens. Keep file identities,
path resolution, formatting, decoding, caches and application controllers outside
`holonight-qt`; consumers provide data, rendering and policy.

| Component | Contract |
|---|---|
| `HnThumbnailDelegate` | Thumbnail slot, optional caption and selection marker; shared hover, selection and distinct focus appearance; tooltip, accessibility and activation signals. |
| `HnPreviewFrame` | Stable preview geometry, themed framing and content/loading/empty/error slots. Consumers supply rendering and state. |
| `HnMetadataList` | Generic label/value rows, section headings, aligned label columns, wrapping and accessible reading order. Consumers supply formatted values. |
| `HnLabeledKeyHint` | Existing semantic key-hint renderer combined with description, typography, alignment and unified accessibility. Preserve semantic key input and translated readable names. |
| `HnBreadcrumbBar` | Caller-supplied segments, current-location presentation, overflow handling, segment activation and location-edit requests. No path parsing or navigation controller. |

`holonight-file-browser` owns shared detailed file-list header/row composition for
Files and the portal, including extension points for Files’ gutter and editing UI.
It owns path-to-breadcrumb adaptation and any reusable file-preview composition.
Preserve native path identity independently of display labels. Its presentation
remains passive: consumers handle navigation, selection and editing requests.
Preserve the installed `HolonightFileBrowser` package, optional components and
`Holonight.FileBrowser` import; presentation changes must not add Qt Quick
requirements to Core-only builds.

## Adoption matrix

| Consumer | New/shared presentation adoption | Behavior to preserve |
|---|---|---|
| Files | Breadcrumbs, shared detailed-list header/rows, preview framing, metadata rows and labeled keyboard hints | Vim modes, line numbers, editing, history, preview transitions and Quick Look |
| Viewer | Thumbnail delegates, preview framing in image information, compatible metadata presentation and labeled keyboard hints | No-upscaling, provider cache ownership, image rendering, playback and footer hint priorities |
| Portal | Breadcrumbs with editable location, shared detailed columns and a selected-entry preview/metadata pane | Selection modes, native path identity, filters, choices, cancellation and save validation |
| Settings | Shared thumbnail and preview presentation in the wallpaper picker | Favorites, folder management, pending selection, display assignment and configuration-conflict behavior |

### Existing-control adoption

This is separate from the five new public types:

- Portal adopts existing search, header, action-bar, sidebar and feedback controls.
- Settings uses existing navigation, settings-row, form, action, empty and loading controls.
- Consumers use existing popup controls where compatible, retaining ownership of
  popup sizing, focus and dismissal policies.

## Dependency order

1. UI-001: Qt controls and installed public interfaces.
2. UI-002: File Browser presentation using those controls.
3. UI-003–UI-006: affected application adoption. Files and Portal require both
   providers; Viewer and Settings can adopt Qt controls directly.
4. UI-007: umbrella installed-package compatibility and ecosystem integration.

Under current [CONTRIBUTING.md](../../../CONTRIBUTING.md), local provider and
consumer development may proceed together using staged installed packages and
`CMAKE_PREFIX_PATH`, without source-tree provider includes. This workflow takes
precedence over older initiatives’ publish-before-development wording. Publication
places providers before dependent consumer commits; publication and umbrella pin
updates require separate authorization. The user subsequently authorized both;
publication and pins are recorded in the ledger. System deployment remains separate.

## Acceptance criteria

The ledger records executed automated checks. Native user-operated acceptance,
publication and pin updates remain separate; unchecked criteria are not completion claims.

- [x] Local SDDs, implementation, usage documentation and gallery examples cover the contracts and adoption matrix.
- [x] Installed C++/QML consumers cover the public types and compatible provider/consumer interfaces; File Browser Core-only and optional-component checks pass.
- [x] Keyboard navigation, activation, distinct focus and selection, tooltips and accessibility work across adopted surfaces.
- [x] Long labels, wrapping, breadcrumb overflow and narrow layouts remain usable.
- [x] Loading, empty and image-failure states preserve preview geometry; stale preview results cannot replace the current selection’s content.
- [x] Fractional scaling, live theme changes and Fusion compatibility are verified.
- [x] Application regressions cover every preserved behavior in the adoption matrix, including portal protocol/validation and Settings conflict handling.
- [x] Component checks and clean umbrella container integration passed in dependency order against staged installed packages. Native verification and one unrelated host-only policy exception are recorded in the ledger.
- [x] Installer staging, ownership, collision rejection and conservative uninstall protections remain intact.
- [x] User-operated native functional checks passed using host-built binaries against host dependencies. The user explicitly deferred visual fine-tuning to separate repository work; container binaries serve acceptance only.
- [x] Following explicit authorization, providers preceded dependent consumer publication and coherent umbrella pins identify the compatible verified revisions recorded in the ledger.

Executed builds, installed-package checks and outstanding acceptance are recorded
in the [coordination ledger](TASKS.md).

## Exclusions

Full Open With functionality, chooser grid/filmstrip, wallpaper fit modes,
periodic wallpaper changes and curated categories remain outside this initiative.
Publication and integration completion are claimed only when explicitly recorded in the ledger.
