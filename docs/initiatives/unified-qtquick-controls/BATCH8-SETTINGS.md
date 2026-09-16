# Batch 8 — Settings Sway scale-1 coverage

Package-manager's fractional runs are [accepted](FINDINGS.md#batch-8-package-manager-sway-acceptance--2026-09-17).
This batch fills Settings' remaining Sway scale-1 interaction/origin coverage in
two styles. Earlier fractional focus and dropdown acceptance stays closed; this
is not another investigation of those repairs or deferred Fusion hover.

Continue in the prepared Sway session, or from a fresh real tux VT login outside
a compositor start:

```sh
python3 /tmp/holonight-uqc201-final-yn9_fquf/guided-session.py sway
```

In its terminal, run one at a time and close Settings normally between runs:

```sh
python3 "$UQC_KIT/guided-app.py" settings --style default --scale 1 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" settings --style Fusion --scale 1 --render-diagnostics
```

For each run:

1. Navigate the sidebar and scroll Appearance/Weather pages. Check scale-1
   readability, clipping and Tab/Shift+Tab focus through reachable controls.
2. In the Weather City field, select/type/erase disposable text without saving
   or triggering a lookup. Check text selection and keyboard navigation.
3. Open reachable Appearance/Weather selectors; check containment and first/last
   row reachability, then dismiss without applying changes. Report inaccessible
   surfaces explicitly.

Do not apply appearance, system or session changes, invoke authentication, or
trigger network actions. Palette transitions remain a separate final gate; this
batch does not claim them. Discard unsaved edits when closing Settings.

Return both printed evidence paths with pass/fail or inaccessible results for
the three items. Stop after these two runs for review. Super+Shift+E exits the
test compositor. Preserve all existing acceptances and historical deferrals.
