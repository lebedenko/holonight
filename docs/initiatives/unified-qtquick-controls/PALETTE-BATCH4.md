# Batch 4 — palette navigation and pickers, scale 1

These checks are complete. [Manual acceptance](FINDINGS.md#batch-4-manual-visual-acceptance--2026-09-15)
records P02 acceptance and P01 external ownership. Do not repeat these runs; the
commands below preserve the completed procedure.

Results and ownership are recorded once in [FINDINGS.md](FINDINGS.md#batch-4-palette-investigation-and-repair--2026-09-14).
UQC-208 is Done for scoped provider work; UQC-201 remains In Progress and the initiative Accepted. This kit repairs
the provider's missing Light palette role. It does not patch the external default
scheme alternation or reopen accepted rendering, chevron, layout or greeter work.

From a fresh local **tux** VT login, start the prepared session:

```sh
python3 __KIT__/guided-session.py hyprland
```

In its terminal, run each command separately and close the application normally
afterward. Every invocation starts with the same empty application/configuration
profile and default HoloNight appearance; its writes remain in its evidence folder.
The HoloNight/Fusion choice affects Quick Controls, while the platform theme stays
HoloNight in both. Output/Qt scale is 1. No fractional-scale checks are requested.

1. **NeoChat:** while logged out, open Settings → General → Appearance → close
   Settings, three times. Do not select a scheme during these three cycles. Pause
   one second on each page and note whether the main and settings windows change
   together. Afterward select explicit HoloNight Dark → HoloNight Light → HoloNight
   Dark and confirm deliberate selection takes effect. Record the displayed names
   if the available names differ. Close the app.
2. **Tokodon:** Settings opens on Appearance. Open it, pause, open Content font,
   inspect header/footer/list/control colors, cancel, reopen the font picker, cancel
   and close Settings. Repeat three times without choosing a scheme. Then choose
   the same explicit dark/light/dark sequence and reopen/cancel the font picker in
   each state. Inspect whether fills and controls remain coherent.
3. **Haruna:** open/cancel/reopen the file picker before visiting Settings. Then
   inspect/cancel/reopen a subtitle color picker (Settings → Subtitles). In General,
   select explicit dark/light/dark schemes and inspect both pickers in each state.
   Do not open media or apply a subtitle color; cancellation suffices.

Run the sequence for each application in this order:

```sh
python3 __KIT__/palette-test.py neochat --style Holonight --diagnostics
python3 __KIT__/palette-test.py neochat --style Holonight
python3 __KIT__/palette-test.py neochat --style Fusion --diagnostics
python3 __KIT__/palette-test.py tokodon --style Holonight --diagnostics
python3 __KIT__/palette-test.py tokodon --style Holonight
python3 __KIT__/palette-test.py tokodon --style Fusion --diagnostics
python3 __KIT__/palette-test.py haruna --style Holonight --diagnostics
python3 __KIT__/palette-test.py haruna --style Holonight
python3 __KIT__/palette-test.py haruna --style Fusion --diagnostics
```

The middle run for each application disables both observers and broad Qt logging.
Do not diagnose an observer-only symptom as a product failure. The diagnostic runs
record existing objects, palette roles/groups/masks/alpha, palette-change events,
origins and actual window DPR, without executing deferred controls. Qt's dialog
category reports backend creation; control origins and actual object classes must
corroborate it. Palette groups in `HN_PALETTE` records are 0 active, 1 disabled,
2 inactive. Similar-looking buttons are not evidence of a Basic backend.

Report the nine printed evidence paths, navigation color changes, picker consistency
before/after each transition, any difference with diagnostics disabled, and whether
each app closed normally. Keep `batch4-index.jsonl` and the run folders together;
the collector records profile identity, module isolation, log hash and process
outcome. Navigation alternation may persist: the source/reduced reproduction
identifies external ownership, and this kit makes no application repair claim.
All actual application pointer, focus and navigation interactions are user-operated.
