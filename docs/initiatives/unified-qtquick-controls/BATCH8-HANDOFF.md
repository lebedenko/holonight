# Batch 8 — first coverage batch (complete)

Accepted on 2026-09-16: [reviewed NeoChat evidence](FINDINGS.md#batch-8-neochat-sway-acceptance--2026-09-16).
Do not repeat these runs. Next: [Tokodon](BATCH8-TOKODON.md).
The commands below are retained as provenance.

Use only the released kit recorded below; preparation must have created READY.
The [final checklist](FINAL-ACCEPTANCE.md) preserves all completed acceptance.
This batch fills NeoChat's Sway fractional-scale/control-origin coverage, in two
styles. It does not reopen Batch 3 diagnostics or repeat accepted repair checks.

From a fresh real `tux` VT login, outside any compositor:

```sh
python3 /tmp/holonight-uqc201-final-yn9_fquf/guided-session.py sway
```

In its test terminal (Super+Return opens another), run one at a time:

```sh
python3 "$UQC_KIT/guided-app.py" neochat --style Holonight --scale 1.25 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" neochat --style Fusion --scale 1.25 --render-diagnostics
```

For each run, remain logged out. Check only the following remaining coverage:

1. On the welcome/server form, type/select/erase `example.invalid` without
   submitting or connecting. Check Tab/Shift+Tab, text selection and visible focus.
2. Open reachable settings and a selector. Check scrolling and first/last-row
   reachability at fractional scale. The observer records created controls and
   effective DPR so their origin can be classified during evidence review.
3. If a palette selector is reachable, select HoloNight Dark → HoloNight Light →
   HoloNight Dark and report whether controls remain readable at each step. The
   existing P01 navigation alternation is documented; do not investigate it.

Close NeoChat normally before the second run. Retain both printed evidence paths
and report pass/fail or the exact inaccessible surface for each item. Include any
functional blocker; deferred warnings alone do not reopen Batch 3. Do not sign in,
start browser authorization, or run additional comparisons.

Return the two evidence paths and observations for review before the next batch.
Exit the test compositor with Super+Shift+E when finished. No authentication,
systemd-manager change or privileged greeter launch belongs to this batch.

Kit hashes, archive and verification are recorded in FINAL-ACCEPTANCE.md after
release. If the kit is absent, restore the recorded archive with the existing
`restore-rendering-kit.py`; never rebuild or modify a released kit in place.
