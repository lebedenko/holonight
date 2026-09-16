# UQC-220 — Settings Weather repair check

Use only the fresh verified kit below. The old Batch 8 kit remains immutable
and contains the reported defects. Scope: HoloNight popup label centering and
Fusion hover on both the closed control and popup rows. Appearance/Weather
composition consistency is a separate non-blocking Settings follow-up.

From a fresh real tux VT login outside any compositor:

```sh
python3 __KIT__/guided-session.py sway
```

In its terminal, run one at a time, closing Settings normally between runs:

```sh
python3 "$UQC_KIT/guided-app.py" settings --style default --scale 1 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" settings --style Fusion --scale 1 --render-diagnostics
```

In each run, open Weather. Inspect two selectors, including one with short rows
(provider) and one with more choices (refresh interval):

1. Open the popup and check that labels are vertically centered in their rows.
2. Move the pointer yourself over the closed ComboBox, then over popup rows.
   Check visible hover feedback, especially in Fusion. Distinguish pointer
   movement from a popup appearing under a stationary pointer.
3. Check keyboard navigation and dismissal remain usable; do not save changes,
   trigger network requests or apply configuration. Discard edits on close.

Return both evidence paths and each result. Stop after these two scale-1 runs;
review precedes any fractional-scale handoff. Do not repeat third-party
comparisons or investigate deferred diagnostics. Super+Shift+E exits the session.
