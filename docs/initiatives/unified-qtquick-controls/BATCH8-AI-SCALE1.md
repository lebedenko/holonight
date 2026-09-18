# Batch 8 — AI Sway scale-1 coverage

**Preparation pending; no READY kit has been released.**

Kit path: `__KIT__`. Use only after its READY marker exists; do not run placeholders.
The canonical [review record](FINDINGS.md#ai-sway-scale-1-iteration--2026-09-19)
tracks preparation and, later, both human cells. UQC-201 remains **In Progress**;
the initiative remains **Accepted**.

Preserve accepted fractional coverage and P03 closure. Do not repeat palette
transitions or light-time Settings construction. Exactly two sequential human
runs are in scope: embedded default and explicit Fusion, Sway output scale 1,
and **measured application DPR 1**. No product changes or gitlink updates.

## Fresh kit handoff

Planning baseline: `9a33b504dbd1e0a772058cb15bced459ddc2682e`, retaining every pin,
including provider `eadfe482000e64ee7ead83d63f878e3f365686b1` and
AI `7e25e78cc7fb33aa63ed480bc3f328a65e04ca0c`.
The [ai-scale1 profile](p03-kit/README.md#ai-scale-1-profile) freshly builds
configuration → provider → AI. Prior archives supply inventory comparison only.
The release must contain source/tooling revisions, inventory differences,
build/test logs, helper evidence, binary provenance and hashes. Package drift
during preparation blocks release. Prior releases remain untouched.

From a fresh disposable **tux VT login**, outside a compositor:

```sh
python3 __KIT__/guided-session.py sway
```

In its terminal, record the actual output scale. Stop if it is not 1. Run the
second command only after normal closure and completed collection of the first:

```sh
swaymsg -t get_outputs -r > "$UQC_SESSION_RUN/outputs.json"
cat "$UQC_SESSION_RUN/outputs.json"
python3 "$UQC_KIT/guided-app.py" ai --style default --scale 1 --index batch6 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" ai --style Fusion --scale 1 --index batch6 --render-diagnostics
```

`batch6` selects per-run profile isolation and the evidence index; it does not
request VT-return testing. Keep providers and title generation disabled. Do not
send prompts, enter credentials or start authorization. DPR is measured from
observer evidence, not inferred from `--scale`. All pointer and focus interaction
is manual.

For each run:

1. Enter disposable multiline text offline. Select, edit, erase and restore it
   without sending.
2. Check Tab/Shift+Tab, visible focus and keyboard navigation.
3. Inspect reachable local settings, selectors and popups for readability,
   containment, first/last row reachability and keyboard dismissal.
4. Check composer and reachable local scrolling. Report empty, disabled or
   inaccessible selectors, history and other controls explicitly.
5. Close normally using the window close control or manually press Super+Q with
   the AI workspace focused. Do not use Ctrl+C. Wait for the launcher to print
   the exit/outcome before starting the next run.

Report observations separately for standard controls, shared composites and
application-owned surfaces. Created-control origins do not cover unopened pages
or every painted pixel. A failure leaves its cell pending: diagnose ownership
before any repair or rerun.

## Evidence and cleanup

After both runs, collect from the session terminal:

```sh
printf '%s\n' "$UQC_SESSION_RUN"
cat "$UQC_SESSION_RUN/batch6-index.jsonl"
UQC_AI_ARCHIVE="/tmp/$(basename "$UQC_SESSION_RUN")-batch8-ai-scale1.tar.gz"
if ( set -o noclobber; tar -czf - -C "$(dirname "$UQC_SESSION_RUN")" "$(basename "$UQC_SESSION_RUN")" > "$UQC_AI_ARCHIVE" ); then
    chmod 644 "$UQC_AI_ARCHIVE"
    sha256sum "$UQC_AI_ARCHIVE"
fi
```

Return both evidence paths, the session path, archive path/hash and per-style
pass/fail/inaccessible observations. Preserve the archive and evidence. Exit the
disposable session using Super+Shift+E or, after collection:

```sh
swaymsg exit
```

No system service or main-user configuration restoration is needed. Review kit
identity, versions, isolation, selectors, measured DPR, staged executable/module
origins, exits and observations before accepting either cell. Bounded automated
termination is not human normal closure. Stop after this two-run review; success
closes only AI's scoped Sway DPR-1 coverage. Authentication, activation,
pre-session greeter and other matrix gaps remain separate iterations.
