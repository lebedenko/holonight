# Batch 7 — greeter keyboard and appearance acceptance

Manual acceptance pending. Use only the released kit named in the [handoff](BATCH7-HANDOFF.md).
Replace `__KIT__` below with that path; the released README already resolves it.
No real login/authentication is tested. Use disposable text; inspect power buttons
without activating them. These four runs cover G01–G06 only.

## Start an isolated Sway session

From a fresh real `tux` VT login, outside the existing desktop:

```sh
python3 __KIT__/guided-session.py sway
```

The kit uses compositor output scale 1. In its terminal, capture output geometry:

```sh
swaymsg -t get_outputs > "$UQC_SESSION_RUN/outputs.json"
```

## Four focused demo runs

Run each command separately, complete the checklist, then close the demo with
Super+Q. The collector records its PID, actual DPR, module mappings and exit.

```sh
python3 __KIT__/guided-app.py greeter --style Holonight --scale 1 --render-diagnostics
python3 __KIT__/guided-app.py greeter --style Holonight --scale 1.25 --render-diagnostics
python3 __KIT__/guided-app.py greeter --style Fusion --scale 1 --render-diagnostics
python3 __KIT__/guided-app.py greeter --style Fusion --scale 1.25 --render-diagnostics
```

For each style/scale:

1. **G01:** initial password focus; Tab and Shift+Tab through account → password
   → reveal → login → session → keyboard layout (only if enabled) → reboot →
   poweroff → account. Look for a visible focus border. Do not activate power.
2. **G02:** type disposable text, focus reveal and hold Space beyond key-repeat
   delay. It stays revealed until release. Repeat and Tab away while holding:
   it remasks. Switch away from the demo while holding and confirm it remains
   masked on return. Mouse hold/release should also reveal/remask. Reveal never
   submits. Clear the disposable text afterward.
3. **G03/G04:** inspect disabled keyboard-layout selector, including hover: no
   interactive painting, readable disabled semantic colors. Inspect password
   idle/focus/text-selection states for readable text, background and border.
   The password background is inherited from the selected style.
4. **G05:** retain the large portrait; open centered account selector with keyboard
   and mouse. Check avatar/name rows, chevron, bounded sizing and selected name.
   Select another demo account; its portrait/name update and password focus returns.
5. **G06:** inspect enabled idle reboot/poweroff backgrounds: transparent with
   borders. Reboot glyph retains its size; poweroff is 25% larger in the same hit
   area. Check hover/focus feedback without activating either action.

Use Super+Shift+E after all four runs to leave isolated Sway. Return the session
path and four per-run pass/fail observations with any exact failing sequence.
Record observations once in FINDINGS.md; this checklist is not an acceptance result.
Single-user/manual/compact layouts, missing avatars and long names also have
isolated runtime regression coverage; no extra manual runs are requested.
