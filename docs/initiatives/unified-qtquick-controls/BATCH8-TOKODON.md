# Batch 8 — Tokodon Sway fractional coverage

NeoChat's two runs are [accepted](FINDINGS.md#batch-8-neochat-sway-acceptance--2026-09-16).
Use the same immutable kit. This next batch contains only two Tokodon runs for
remaining Sway fractional-scale, control-origin and palette coverage.

If the prepared Sway test session is still open, continue there. Otherwise, from
a fresh real tux VT login outside a compositor:

```sh
python3 /tmp/holonight-uqc201-final-yn9_fquf/guided-session.py sway
```

In the test terminal, run one at a time and close Tokodon normally between them:

```sh
python3 "$UQC_KIT/guided-app.py" tokodon --style Holonight --scale 1.25 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" tokodon --style Fusion --scale 1.25 --render-diagnostics
```

For each run:

1. Remain logged out. In a reachable onboarding/server field, type/select/erase
   `example.invalid` without submitting. Check Tab/Shift+Tab and visible focus.
2. Open reachable settings/selectors; check scrolling, popup containment and
   first/last-row reachability. Report inaccessible surfaces explicitly.
3. If the palette selector is reachable, select HoloNight Dark → HoloNight Light
   → HoloNight Dark and check readability throughout.

Do not sign in, authorize a browser or submit network requests. Preserve the
existing chevron and P01 deferrals; do not investigate or repeat runs solely for
them. Report any concrete functional blocker separately.

Return both printed evidence directories and pass/fail or inaccessible results
for the three items. Stop after these two runs for review; Super+Shift+E exits
the test compositor. No authentication or systemd-manager changes in this batch.
