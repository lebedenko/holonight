# G07 — fullscreen greeter caret comparison

**Current disposition: G07 closed as not an issue for intended fullscreen use.**
Both fullscreen style comparisons passed; see [fullscreen acceptance and closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16).
The procedure and earlier status statements below are historical; no repeats are requested.

Two manual tests, HoloNight and Fusion, at compositor scale 1 and Qt scale 1.
The previous missing-caret observation was windowed; it does not establish a
failure in the greeter's intended fullscreen use. Settings and AI windowed tests
have not reproduced this issue. Production QML is unchanged.

From a fresh real `tux` VT login outside the desktop:

```sh
python3 __KIT__/guided-session.py sway
```

In the isolated terminal, record the output geometry, then run these two tests
separately, closing the first before launching the second:

```sh
swaymsg -t get_outputs > "$UQC_SESSION_RUN/outputs.json"
python3 "$UQC_KIT/guided-app.py" greeter --style Holonight --scale 1 --caret-diagnostics
python3 "$UQC_KIT/guided-app.py" greeter --style Fusion --scale 1 --caret-diagnostics
```

For each style:

1. With the greeter focused, press **Ctrl+F** to enter fullscreen. Confirm it fills
   the output. Ctrl+F toggles fullscreen for the focused window.
2. Wait three seconds with the empty password field focused. Record whether the
   caret blinks visibly.
3. Type one disposable character, then Backspace. Wait three seconds and record
   caret visibility while populated and after clearing.
4. Tab to reveal, then Shift+Tab back. Wait three seconds and record whether the
   empty caret returns.
5. Close the greeter with **Super+Q**. Run the other style using the same steps.

Keep each test under five minutes: the passive observer has a bounded sampling
period and records geometry, DPR, focus, native blink timing and empty-field pixel
crops. It never records entered text or changes focus/blinking. Initial windowed
samples may precede Ctrl+F; distinguish them from fullscreen geometry when reviewing
the evidence.

Leave Sway with **Super+Shift+E**. Return the session evidence path printed at
startup and the three caret observations for each style. Fullscreen reproduction
is pending until those observations are reviewed; this kit does not close G07 or
repeat the accepted G01–G06 checklist.
