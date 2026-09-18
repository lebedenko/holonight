# Batch 8 — Settings Sway scale-1 coverage

**Accepted — 2026-09-18.** Both requested runs passed; see the
[reviewed human evidence](FINDINGS.md#settings-sway-scale-1-human-acceptance--2026-09-18). No rerun is requested.
UQC-201 remains **In Progress**; the initiative remains **Accepted**.
The handoff and commands below are retained as historical procedure.

Preserve [P03 closure](FINDINGS.md#p03-human-acceptance-after-observer-repair--2026-09-18),
[Settings fractional acceptance](FINDINGS.md#batch-8-settings-fractional-results-and-composition-disposition--2026-09-17)
and [UQC-220 Weather acceptance](FINDINGS.md#uqc-220-fractional-repair-acceptance--2026-09-17).
No repeat fractional, Weather popup/centering/hover, composition comparison or
palette-transition checks. Inaccessible controls must be reported explicitly.

## Fresh kit handoff

**READY:** `/tmp/holonight-uqc201-settings-p1ndqzdz`.
[Reviewed automated readiness and archive identity](FINDINGS.md#settings-scale-1-kit-readiness--2026-09-18).
Use only this released Settings kit. Preparation uses umbrella
`52908523d5347100f59fd1edf3861330f5d09286` and preserves every gitlink, including
provider `eadfe48` and Settings `0eb5028`. The [Settings preparation profile](p03-kit/README.md#settings-scale-1-profile)
freshly builds configuration, system services, shell configuration, provider and
Settings. Prior P03 inventory is comparison evidence only; its binaries and prior
suite results are not reused. The released kit contains inventory.diff, exact
revisions, build/check logs, helper outcomes, hashes and binary provenance.

From a fresh real **tux VT login**, outside a compositor:

```sh
python3 /tmp/holonight-uqc201-settings-p1ndqzdz/guided-session.py sway
```

The disposable Sway session uses output scale 1, isolated HOME/XDG and a private
bus, masks host HoloNight providers, disables network access, and retains normal
GPU/input/VT device bindings. In its terminal, run sequentially, closing Settings
normally and discarding unsaved edits between runs:

```sh
python3 "$UQC_KIT/guided-app.py" settings --style default --scale 1 --render-diagnostics
python3 "$UQC_KIT/guided-app.py" settings --style Fusion --scale 1 --render-diagnostics
```

For each run:

1. Navigate the sidebar. Scroll Appearance and check readability, clipping and
   keyboard focus with Tab/Shift+Tab.
2. Open reachable Appearance selectors; check containment and first/last row
   reachability, then dismiss without applying changes.
3. Use the Weather City field only for unsaved text selection, editing and
   keyboard navigation. Do not invoke lookup or compare Weather popups/hover.

Do not save appearance/system/session changes or invoke authentication. All UI
interaction is manual; no pointer or focus automation. Return both printed
**Evidence** paths and pass/fail/inaccessible observations for each item. Stop
after these two runs for review; no automatic repair or rerun is authorized by
readiness alone.

## Cleanup and evidence

Close Settings normally, then use **Super+Shift+E** to exit this test Sway session.
Keep the evidence directories printed by the helpers under the real tux home;
the disposable HOME/XDG profiles stay there for review. Do not delete the kit or
archive. No host configuration restoration is required because edits are isolated.
If the kit path is absent after reboot, restore from the umbrella root:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc201-settings-p1ndqzdz/holonight-uqc201-settings-p1ndqzdz.tar.gz
```

Restoration checks hashes, restores only the exact prefix and refuses overwrite. Never point a moved kit at a different prefix.

Review kit identity, versions, process exits, isolation, selectors, actual DPR,
staged origins and human observations before closing any Settings scale-1 cell.
Record reviewed results once in FINDINGS and link them from FINAL-ACCEPTANCE and
TASKS. Authentication, service activation, pre-session greeter, broader matrix
coverage and final integration remain separate iterations.
