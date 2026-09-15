# G07 — empty-password caret diagnostic comparison

G07 remains open. Automated production-QML cases pass on software and isolated
Sway/OpenGL; no speculative production repair is included. This fresh kit adds a
passive observer: geometry, focus, DPR, native blink interval and small empty-caret
pixel crops. It never records entered text or changes focus/blinking. Sampling
stops after five minutes; empty-field captures are bounded to 120 per run, in
short bursts on state changes. Use only a disposable character.

From a fresh real `tux` VT login outside the desktop:

```sh
python3 __KIT__/guided-session.py sway
```

In the isolated terminal, record compositor scale 1 and run each demo separately:

```sh
swaymsg -t get_outputs > "$UQC_SESSION_RUN/outputs.json"
python3 __KIT__/guided-app.py greeter --style Holonight --scale 1 --caret-diagnostics
python3 __KIT__/guided-app.py greeter --style Holonight --scale 1.25 --caret-diagnostics
python3 __KIT__/guided-app.py greeter --style Fusion --scale 1 --caret-diagnostics
python3 __KIT__/guided-app.py greeter --style Fusion --scale 1.25 --caret-diagnostics
```

For each run (about 30 seconds):

1. Wait three seconds at initial empty password focus. Is a blinking caret visible?
2. Type one disposable character, then Backspace. Wait three seconds. Is the
   caret visible both populated and cleared?
3. Tab to reveal, then Shift+Tab back. Wait three seconds. Does the empty caret return?
4. Type a disposable character; Tab to reveal, hold Space, release, then Shift+Tab
   to password. Confirm reveal/remasking and caret return; clear the field.

Close each demo with Super+Q. Leave Sway with Super+Shift+E after all four runs.
Return the session evidence path and observations for each style/scale, including
whether initial focus differs from cleared/refocused behavior. The collector
records actual DPR, source origins, mappings, versions and exit outcomes.

G01–G06 are already accepted; do not repeat that checklist. Batch 7 stays closed.
Real pre-session login, F05 and Batch 3 are outside this comparison. Observations
will be recorded once in FINDINGS.md; this procedure does not claim acceptance.
