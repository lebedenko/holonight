# Batch 8 — Haruna Sway fractional coverage

Tokodon's two runs are [accepted](FINDINGS.md#batch-8-tokodon-sway-acceptance--2026-09-16).
Use the same released kit for two Haruna runs covering remaining Sway fractional
interaction, control origins and palette behavior. This does not reopen the
historical crash or Fusion hover investigation.

Continue in the prepared Sway test session if still open. Otherwise, from a fresh
real tux VT login outside a compositor:

```sh
python3 /tmp/holonight-uqc201-final-yn9_fquf/guided-session.py sway
```

In its test terminal, launch one at a time; close Haruna normally between runs:

```sh
python3 "$UQC_KIT/guided-app.py" haruna --style Holonight --scale 1.25 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" haruna --style Fusion --scale 1.25 --render-diagnostics
```

For each run:

1. Manually open `/tmp/holonight-uqc201-final-yn9_fquf/sample.mp4`. Check local
   playback/pause, seeking, volume and toolbar/menu usability. Do not open URLs.
2. In settings, check text editing, Tab/Shift+Tab, scrolling, selector containment
   and first/last-row reachability at fractional scale. Report inaccessible items.
3. Select HoloNight Cyber D → HoloNight Cyber L → HoloNight Cyber D if available
   (the previously accepted readable scheme pair). Check readability throughout;
   report if the selector/pair is unavailable.

Application-painted controls and Haruna's explicit Fusion fallback are accepted
boundaries, not missing provider implementations. Do not repeat runs or investigate
warnings solely for deferred findings. Report any concrete functional blocker.

Return both printed evidence paths and pass/fail or inaccessible results for the
three items. Stop after the two runs for review. Super+Shift+E exits the test
compositor. No authentication or systemd-manager changes belong to this batch.
