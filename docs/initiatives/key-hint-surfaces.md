# Transparent key hints on host surfaces

## Shared contract

HnKeyHint always has transparent fill. Its new borderColor and foregroundColor
properties default to borderPassive and enabled textSecondary / disabled
textDisabled. Explicit bindings remain authoritative when disabled. Both text and
vector glyphs use foregroundColor. HnSelectableDelegate exposes readonly
outlineColor, shared by its painted outline and embedded hints. Geometry,
shortcuts, accessibility and frameless menu sequence labels are unchanged.

## Ownership

- [Provider design](../../holonight-qt/docs/sdd/key-hint-surfaces.md): transparent
  badges, color API, delegate outline API, gallery and regression checks.
- [Shell design](../../holonight-shell/docs/sdd/key-hint-surfaces.md): launcher
  selected-row hint follows delegate outline; authentication hints follow button
  borders. Launcher and audio footers inherit the provider change.
- [Viewer footer](../../holonight-viewer/apps/viewer/qml/footer/FooterKeyHints.qml)
  and shortcut help inherit transparency through shared controls; no source edit
  or local styling override is needed.
- [Files guidance](../../holonight-files/apps/files/qml/status/ModeStatusBar.qml)
  and Quick Look inherit transparency through shared controls; no source edit is
  needed.

## Delivery and acceptance

Provider and Shell source changes can be prepared together. Verify Shell against
an installed development provider. Publish the provider before consumer commits
reference its revision, then update umbrella component pins as one coherent
milestone. Existing historical consistent-key-hints notes remain historical.

Run focused provider smoke/rendering checks, Shell launcher/authentication checks,
QML lint/policy, demo/gallery startup tests and installed-package verification.
Check launcher footer/selection, authentication buttons and Viewer footer visually;
neutral footer borders stay unchanged and embedded hint border/glyph colors match
the enclosing border as focus changes. Viewer/Files need the updated installed
provider to display the new default.
