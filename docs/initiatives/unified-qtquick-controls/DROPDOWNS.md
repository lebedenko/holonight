# UQC-206 — focused dropdown candidate verification

Manual interaction checkpoint completed on 2026-09-12: both applications/styles
work with mouse and keyboard. See the canonical FINDINGS.md acceptance record.
No repetition is requested. D02 warnings and the new F06/F07 pointer/keyboard
findings remain open. Instructions below are retained for reference.

This kit contains an **unpublished working-tree candidate**, identified by
`revisions.json`, `provider.patch` and `SHA256SUMS`. It does not change integration
pins. D01/D03 and the reproduced invisible-selected-row part of D04 are repaired;
D02 height loops and D04's exact scroll reset still need observation.

Ready kit: `/tmp/holonight-uqc206-wou7oqyf`.

From a fresh real **tux VT login**, outside any compositor:

```sh
python3 /tmp/holonight-uqc206-wou7oqyf/guided-session.py sway
```
This creates a private bus and disposable configuration; Sway output scale is 1.

In the Sway terminal, run separately, closing each app before the next:

```sh
python3 "$UQC_KIT/dropdown-test.py" settings
python3 "$UQC_KIT/dropdown-test.py" greeter
```

Both use the embedded HoloNight default at Qt scale 1.25. Test **Settings →
Appearance → font dropdowns** and the **greeter demo session selector**:

1. Select a middle or last row, close, then reopen by mouse. Is that row visible
   and highlighted, or does the list restart at the beginning? Repeat using Space.
2. Hover several rows and scroll down/up. Confirm rows remain visible and usable;
   select the first and last rows. Note the exact selector if behavior differs.
3. Reopen and click outside, then repeat with Escape and the collapsed control.
   Confirm dismissal without accidental selection or reopening.

For a comparison, repeat an affected application with `--style Fusion`. Use
`--scale 1` only if fractional-scale behavior differs. Report each result and the
printed evidence directories. `launch.log` retains height-loop diagnostics; a
successful launch/exit alone is not a manual pass.

Only interact with the greeter's demo dropdowns; no login, credential entry or
power action is needed. Settings changes stay in the disposable profile. Exit
Sway with Super+Shift+E after closing the apps. No automated desktop interaction.

## Preparation and reboot recovery

From the umbrella root:

```sh
python3 docs/initiatives/unified-qtquick-controls/prepare-dropdown-kit.py
```

Commands/logs and a complete kit archive are retained in `.cache/holonight-uqc206-*`.
Preparation creates READY only after installed dropdown and application startup
checks pass. Resume an interrupted preparation with `--resume /tmp/PRINTED_KIT`;
released kits cannot be modified by the builder. The archive restores the same
absolute prefix after reboot; use the restore helper, then launch the original path.


Restore the current kit after a reboot from the umbrella root, before switching
to tux (the command refuses to overwrite an existing kit):

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-dropdown-kit.py \
  .cache/holonight-uqc206-wou7oqyf/holonight-uqc206-wou7oqyf.tar.gz
```

## Preparation record — 2026-09-12

Prepared the current provider working tree on baseline `65c806f`, Settings
`2508635` and greeter `b082d82`; exact revisions and product-QML patch are saved
in the kit. Config/system-services/shell-config dependencies were reconfigured
against the new prefix. Settings/greeter were freshly configured, built and
installed; no source changes or system installation.

All 12 installed dropdown cases pass under HoloNight/Fusion at Qt scales 1/1.25
with host HoloNight QML/config hidden. Settings and greeter each pass four installed
startup/selector cases with repository discovery forbidden. Settings' first private
bus launch failed because the sandbox denied socket creation; the permitted rerun
passes and append-only logs retain both results. Python/shell syntax, refusal of
wrong-session launches and modification of a released kit, independent restore
smoke, installed QML source parity and 215 kit checksums pass.

Commands, results and helper verification are retained in
`.cache/holonight-uqc206-wou7oqyf/{results.jsonl,helper-checks.json,logs/}`.
The complete archive restores the same absolute paths and verifies checksums before
recreating READY. Package-version validation still runs at session launch. No
manual acceptance or publication is inferred from kit preparation.
