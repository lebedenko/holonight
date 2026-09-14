# Batch 3 focused manual checks

Results and open evidence gaps are recorded once in
[FINDINGS.md](FINDINGS.md#batch-3-manual-review-and-external-ownership--2026-09-14).
This kit is for rendering repair acceptance and investigation. Batch 3 is still open.
Do not repeat accepted authentication or dropdown checks.

From a fresh local **tux** VT login, start:

```sh
python3 __KIT__/guided-session.py hyprland
```

In its terminal, run one application at a time, close it normally after inspection,
and retain the printed evidence directory. Use each command with `Holonight` and
`Fusion`, at `1` and `1.25`. The compositor output stays at scale 1.

```sh
python3 __KIT__/rendering-test.py haruna --style Holonight --scale 1
python3 __KIT__/rendering-test.py ai --style Holonight --scale 1
python3 __KIT__/rendering-test.py settings --style Holonight --scale 1
python3 __KIT__/rendering-test.py neochat --style Holonight --scale 1
python3 __KIT__/rendering-test.py tokodon --style Holonight --scale 1
```

- **Haruna:** compare top-menu and Settings-navigation icons. Menus with no icons
  should omit the icon column; icon-bearing menus align all labels. Check a checked
  entry and submenu. In Shortcuts, the first row must not remain selected merely
  because it is current; explicit navigation selection remains visible. Visit
  Mouse → Add action and inspect warning corners. Open two help buttons and confirm
  the application-owned independent-popup behavior is acceptable. Retain any crash
  and its preceding action; a later successful run does not close the crash finding.
- **AI:** Settings → Ollama, focus “Test connection”, press Space and wait for the
  operation to finish; compare the ring before, during and after, then Tab/Backtab.
  Also activate a button that stays enabled. For Enabled and Enable tool calling,
  inspect a pill-shaped outline around the switch track, excluding its label, in both states. Record the precise next
  control at any invisible focus stop near Context window/Temperature. No credentials
  or chat requests are needed; do not change non-test configuration.
- **Settings:** inspect the reported Fusion hover/spacing surfaces. Preserve Fusion's
  visual conventions; this is classification, not a request for HoloNight styling.
- **NeoChat/Tokodon:** use logged-out settings to inspect check/radio label spacing
  and scheme popup geometry. Verify first/last rows remain reachable. Report clipping
  separately from a preference for smaller popups. Account-dependent views are out
  of this focused request.

Report application, style, scale and exact action for failures; identify whether
the issue affects appearance, keyboard focus, selection or process survival.
Pointer movement, clicking and focus changes are human-operated only.

The helper indexes process outcomes and hashes; the existing collector records
actual mappings and configured selection. Missing actual per-window DPR/focus-owner
evidence remains an explicit investigation gap and is not inferred from environment
variables or from a successful visual report. Automated provider fixtures measure
their own actual DPR, not the third-party application's DPR.
