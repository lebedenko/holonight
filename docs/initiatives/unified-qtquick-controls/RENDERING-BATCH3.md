# Batch 3 focused manual checks

Results and open evidence gaps are recorded once in
[FINDINGS.md](FINDINGS.md#batch-3-focused-repair-iteration--2026-09-14).
This kit is for rendering repair acceptance and investigation. Batch 3 is still open.
Do not repeat accepted authentication, dropdown navigation or F03 traversal checks.
Fusion hover and external visual preferences remain recorded for later classification.

From a fresh local **tux** VT login, start:

```sh
python3 __KIT__/guided-session.py hyprland
```

In its terminal, run one application at a time, close it normally after inspection,
and retain the printed evidence directory. Use each command with `Holonight` and
`Fusion`, at `1` and `1.25`. The compositor output stays at scale 1.

```sh
python3 __KIT__/rendering-test.py haruna --style Holonight --scale 1 --diagnostics
python3 __KIT__/rendering-test.py ai --style Holonight --scale 1 --diagnostics
python3 __KIT__/rendering-test.py settings --style Holonight --scale 1 --diagnostics
python3 __KIT__/rendering-test.py neochat --style Holonight --scale 1 --diagnostics
python3 __KIT__/rendering-test.py tokodon --style Holonight --scale 1 --diagnostics
```

- **Haruna:** compare top-menu and Settings-navigation icons. Menus with no icons
  should omit the icon column; icon-bearing menus align all labels. Check a checked
  entry and submenu. In Shortcuts, the first row must not remain selected merely
  because it is current; explicit navigation selection remains visible. Retain any crash
  and its preceding action; a later successful run does not close the crash finding.
- **AI:** Settings → Ollama, focus “Test connection”, press Space and wait for the
  operation to finish; compare the ring before, during and after, then Tab/Backtab.
  Also activate a button that stays enabled (for example Cancel where available).
  For Enabled and Enable tool calling, inspect a pill-shaped outline around the
  switch track, excluding its label, in both states. No credentials or chat requests
  are needed; do not change non-test configuration.
- **Settings:** inspect the track-only Switch focus outline checked and unchecked.
- **NeoChat/Tokodon:** open the logged-out scheme dropdown and inspect background
  transparency. Leave it open briefly for geometry, palette and pixel observation,
  then close it and the application normally to retain teardown diagnostics.
  Account-dependent views are out of this focused request.

Report application, style, scale and exact action for failures; identify whether
the issue affects appearance, keyboard focus, selection or process survival.
Pointer movement, clicking and focus changes are human-operated only.

The optional `--diagnostics` observer records labeled button state, Space before/after
press and release, active focus owner/reason, visualFocus, row selection state,
actual window DPR, and visible ComboBox background geometry/palette/pixels in
`HN_RENDER` log records. `HN_ICON` compares actual HnIcon names with Qt lookup.
It observes without changing application input or focus. Avoid account-dependent
views; button labels are recorded. Keep diagnostic and uninstrumented comparisons
separate if a crash appears only with instrumentation. Missing observations remain
unknown and are never inferred from requested scale. Report the exact preceding
action for any crash and retain its core and binary identity.
