# Batch 7 — released greeter acceptance kit

UQC-212 is Done for local implementation/publication. Batch 7 remains open for
four human-operated G01–G06 checks. UQC-201 stays In Progress; initiative Accepted.
[Canonical verification and kit evidence](FINDINGS.md#batch-7-greeter-implementation-and-verification--2026-09-15).

## Released kit

`/tmp/holonight-uqc212-nq09g2v1`

From a fresh real `tux` VT login outside the desktop:

```sh
python3 /tmp/holonight-uqc212-nq09g2v1/guided-session.py sway
```

In the isolated terminal, capture output scale and run these separately:

```sh
swaymsg -t get_outputs > "$UQC_SESSION_RUN/outputs.json"
python3 "$UQC_KIT/guided-app.py" greeter --style Holonight --scale 1 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" greeter --style Holonight --scale 1.25 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" greeter --style Fusion --scale 1 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" greeter --style Fusion --scale 1.25 --render-diagnostics
```

Use the [G01–G06 checklist](GREETER-BATCH7.md) in each run; the kit's README has
resolved paths. Use disposable text, hold Space past key-repeat delay, and inspect
power controls without activating them. Close each demo with Super+Q; leave Sway
with Super+Shift+E after all four. Return the session evidence path and per-run
pass/fail observations, including the exact sequence for any failure.

No additional manual single-user/compact runs or repeats of earlier batches are
requested. Real pre-session login remains outside this iteration.

## Restore after reboot

Only if the original `/tmp` kit is absent, from the umbrella root:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc212-nq09g2v1/holonight-uqc212-nq09g2v1.tar.gz
```

Archive SHA-256:
`a2235caa325c1de8366c86a1b05e3c568c55df2938bfe99b4ff734a4762ef44b`.
Restoration at the exact prefix, all 187 file hashes, package versions and
existing-path refusal have been verified. Preserve this released kit.
