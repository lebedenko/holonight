# Batch 8 — package-manager Sway fractional coverage (complete)

Accepted: [reviewed evidence](FINDINGS.md#batch-8-package-manager-sway-acceptance--2026-09-17).
Do not repeat these runs. Next: [Settings at scale 1](BATCH8-SETTINGS.md).
Commands below are retained as provenance.

Haruna's two runs are [accepted](FINDINGS.md#batch-8-haruna-sway-acceptance--2026-09-16).
This batch adds two read-only Sway runs for the owned package-manager. Preserve
its earlier Hyprland observations; do not repeat them.

Continue in the prepared Sway test session if still open. Otherwise, from a fresh
real tux VT login outside a compositor:

```sh
python3 /tmp/holonight-uqc201-final-yn9_fquf/guided-session.py sway
```

In its terminal, launch one at a time and close the application normally between
runs. The first run deliberately leaves the owned style selector unset:

```sh
python3 "$UQC_KIT/guided-app.py" packages --style default --scale 1.25 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" packages --style Fusion --scale 1.25 --render-diagnostics
```

For each run:

1. Inspect the installed-package list. Type/select/erase a search term, switch
   category tabs, and check Tab/Shift+Tab and visible focus.
2. Select an installed package and inspect details. Check list/detail scrolling,
   horizontal table scrolling where available, and arrow-key selection.
3. Inspect reachable selectors/popups and disabled states for readability,
   clipping and fractional-scale containment. Report unavailable surfaces.

Use only local, read-only inspection. Do not refresh/download repositories,
install, remove, update or apply transactions; do not invoke authentication or AI
actions. There is no requirement to find or change an application palette here.

Return both printed evidence paths with pass/fail or inaccessible results for
each item. Stop after these two runs for review; Super+Shift+E exits the test
compositor. No systemd-manager changes belong to this batch.
