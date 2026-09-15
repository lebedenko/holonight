# Batch 6 — shell geometry and AI VT-return evidence

**Draft: no Batch 6 kit has been generated.** Preparation is deferred to the next
session at the user’s request. Follow [the handoff](BATCH6-HANDOFF.md) first;
`__KIT__` is an unresolved placeholder, not a runnable path.

Use only the new immutable kit identified in the
[Batch 6 findings](FINDINGS.md#batch-6-investigation--2026-09-15).
Earlier kits and accepted batches remain unchanged. These are investigation runs;
no shell rendering repair is claimed. Keep every output at scale **1**.

## Start an isolated session

From a fresh real **tux VT login**, outside any compositor:

```sh
python3 __KIT__/guided-session.py hyprland
```

The terminal opens in an isolated configuration and private session bus. Every
Batch 6 application run gets a fresh profile; AI providers stay disabled and
logged out. Do not enter credentials, send requests, or change provider state.
All clicks, focus changes and VT switching below are performed by the user.

## Shell: four Hyprland comparisons

Run each command in the kit terminal, one at a time:

```sh
python3 __KIT__/guided-app.py shell --style Holonight --scale 1 --index batch6 --session-diagnostics
python3 __KIT__/guided-app.py shell --style Fusion --scale 1 --index batch6 --session-diagnostics
python3 __KIT__/guided-app.py shell --style Holonight --scale 1.25 --index batch6 --session-diagnostics
python3 __KIT__/guided-app.py shell --style Fusion --scale 1.25 --index batch6 --session-diagnostics
```

For each run:

1. Record style/scale, output dimensions, visible/missing status items and service
   availability. Allow startup to settle, then inspect all section edges before
   hovering. Compare status fills with the bell/date sections.
2. Hover network/audio/battery/layout when available, open and close their popups,
   then move away. Record whether frames remain complete and normal transparency
   returns. Do not alter network, volume, battery or layout state between runs.
3. Record shrinking, jitter, sliding, clipping or incorrect hit regions, including
   the exact triggering section/action. Note reserved bar space versus drawn bar
   height; a visual estimate is not a measured exclusive zone.
4. Return to the terminal manually and press Ctrl+C once. Let the helper save the
   exit status and index before starting the next run.

If a defect occurs, repeat that exact style/scale once **without**
`--session-diagnostics` to check whether observation affects it. If no defect
occurs, make one uninstrumented HoloNight/1.25 comparison.

Then exit Hyprland with Super+Shift+E. From the VT, start:

```sh
python3 __KIT__/guided-session.py sway
```

Repeat only the two **scale-1** shell commands for the previously reported frame
problem. Do not expand compositor/scale coverage unless this comparison provides
new evidence. Exit Sway with Super+Shift+E.

## F05: Hyprland at Qt scale 1.25

Start another isolated Hyprland session with the first command above. Run:

```sh
python3 __KIT__/guided-app.py ai --style Holonight --scale 1.25 --index batch6 --session-diagnostics
```

1. Open **Settings → Providers → Ollama**. Confirm it remains disabled. Record the
   actual provider/form name and the starting control; use **Context window's
   numeric editor** if available. If that form/control differs, record what is
   actually present before testing.
2. Click that control once to establish the starting point. Test Tab then
   Shift+Tab without entering text; record the visible focus sequence.
3. Switch manually from the tux VT to the original VT and back. Record the VT
   numbers. On return, **do not click or change focus** before testing Tab and
   Shift+Tab again. Record whether focus/traversal moves.
4. If traversal fails, preserve that observation first. Then click the same
   starting control once and repeat navigation to check the reported recovery.
5. Close AI normally; let the helper finish its evidence. Repeat under Fusion by
   replacing `--style Holonight` with `--style Fusion`.
6. Repeat the same two style runs without `--session-diagnostics`, using the same
   form/control and VT sequence. Stop after this confirming comparison.

The observer records Wayland Tab delivery and keyboard enter/leave when available,
Qt navigation receipt, window activation, active focus identities, actual DPR and
queued focus state after dispatch. Session activation/compositor active-window
metadata are collected separately. No entered text is recorded. Qt event filters
cannot observe final event acceptance: it is explicitly marked unavailable,
never inferred from focus movement. Missing observer records alone do not prove
missing compositor delivery; verify observer coverage before assigning ownership.

## Return the evidence

Report the session/evidence paths printed by the helpers and observations keyed by
style, scale and run. Include the exact F05 form/control and VT numbers. Keep raw
logs/index files for hash verification. Results belong once in
[FINDINGS.md](FINDINGS.md#batch-6-investigation--2026-09-15); link this checklist,
[ledger](TASKS.md) and [shell SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-211.md).

S01/S02 acceptance and F05 ownership remain pending until review. The initiative
stays Accepted and UQC-201 stays In Progress.
