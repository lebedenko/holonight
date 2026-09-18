# P03 observer-repair human acceptance

**P03 closed — 2026-09-18.** [Accepted human results](FINDINGS.md#p03-human-acceptance-after-observer-repair--2026-09-18)
cover correct Fusion and replacement default. Do not repeat these completed checks.
The preparation/release instructions and pending-state text below are historical.

Use only this fresh kit: /tmp/holonight-uqc201-p03-95__83sb.
Provider eadfe482000e64ee7ead83d63f878e3f365686b1; unchanged AI
7e25e78cc7fb33aa63ed480bc3f328a65e04ca0c. P03 remains open.

Exactly two sequential human-operated runs follow. From a fresh real **tux** VT
login outside a compositor:

```sh
python3 /tmp/holonight-uqc201-p03-95__83sb/guided-session.py sway
```

In its terminal, record outputs and confirm every active output has **scale 1**:

```sh
swaymsg -t get_outputs -r > "$UQC_SESSION_RUN/outputs.json"
python3 - <<'PY'
import json, os
from pathlib import Path
outputs = json.loads((Path(os.environ['UQC_SESSION_RUN']) / 'outputs.json').read_text())
active = [output for output in outputs if output.get('active')]
assert active and all(output['scale'] == 1 for output in active)
print([(output['name'], output['scale']) for output in active])
PY
```

1. Launch the embedded default run:

   ```sh
   python3 "$UQC_KIT/guided-app.py" ai --style default --scale 1.25 --index batch6 --palette-diagnostics
   ```

2. After completing the inspection below, closing AI normally and waiting for the
   launcher to finish collecting evidence, launch explicit Fusion:

   ```sh
   python3 "$UQC_KIT/guided-app.py" ai --style Fusion --scale 1.25 --index batch6 --palette-diagnostics
   ```

`batch6` uses the retained isolated profile/index format. It does not request old
checklists. All providers and title generation remain disabled. Only palette
diagnostics are enabled; do not enable providers, network access or authorization.

For **each** run, before opening Settings for the first time, manually open another
terminal with **Super+Return**, wait for process evidence collection, and switch
that run's isolated profile to light:

```sh
python3 "$UQC_KIT/ai-palette.py" light
```

Confirm the main window started dark and initially inspect New Chat and prompt buttons.
After the light command, open AI Settings for the **first time in this process**. Inspect native text fields, SpinBoxes and reachable
selectors in light mode: backgrounds, text, disabled states and shared composites.
Closing and reopening Settings retains its Loader instance; only this first open
in light mode tests light-time construction.

Keep **both windows alive** through dark → light → dark. At each unchanged scheme,
manually alternate activation between the main window and Settings, then hover
New Chat/prompt buttons and Settings inputs, numeric controls, selectors, disabled
controls and shared search/combo composites. Watch for persistent color reversals
after activation/deactivation or hover. Do not repeat unrelated navigation checks. Issue each command separately
in the other terminal, returning manually to inspect Settings between commands:

```sh
python3 "$UQC_KIT/ai-palette.py" dark
python3 "$UQC_KIT/ai-palette.py" light
python3 "$UQC_KIT/ai-palette.py" dark
```

Record pass/fail/inaccessible for each required surface in each state, including
main-window New Chat/prompt buttons and Settings native inputs/selectors, disabled
controls and shared composites. Note activation and hover separately. Missing or
inaccessible required evidence keeps P03 open. Name the
field, numeric control, selector or composite; describe background/text/disabled
state inconsistencies. Record empty or inaccessible controls without enabling
providers or creating network content. Observer origins cover instantiated objects,
not unopened pages or all painted pixels. Automated provider diagnostics and isolated AI
startup checks establish readiness; ordinary AI startup does not instantiate
its lazy Settings window, and the workspace round trip is separate evidence.

Close Settings and then AI normally using their close controls, or manually use
**Super+Q** with the intended AI window focused. Do not use Ctrl+C. Wait for the
launcher outcome before starting the next run.

Before archiving, save your per-surface observations in a text file inside the
session directory. Include each scheme, main and Settings controls, activation,
hover, disabled states and any inaccessible required controls.

After both runs, verify **measured** application DPR 1.25 from collector output:

```sh
python3 - <<'PY'
import json, os
from pathlib import Path
session = Path(os.environ['UQC_SESSION_RUN'])
rows = [json.loads(line) for line in (session / 'batch6-index.jsonl').read_text().splitlines()]
finished = [row for row in rows if row['status'] == 'finished']
assert len(finished) == 2, finished
for row in finished:
    dprs = row['palette_window_dpr']
    assert dprs and set(dprs.values()) == {1.25}, (row['run'], dprs)
    assert row['process_exit'] == 0 and row['outcome'] == 'normal', row
    print(row['run'], dprs)
PY
cat "$UQC_SESSION_RUN/batch6-index.jsonl"
UQC_P03_ARCHIVE="/tmp/$(basename "$UQC_SESSION_RUN")-p03-recheck.tar.gz"
if ( set -o noclobber; tar -czf - -C "$(dirname "$UQC_SESSION_RUN")" "$(basename "$UQC_SESSION_RUN")" > "$UQC_P03_ARCHIVE" ); then
    chmod 644 "$UQC_P03_ARCHIVE"
    sha256sum "$UQC_P03_ARCHIVE"
fi
```

Return the session path, both run paths, archive path and SHA-256, plus per-surface
observations for initial light construction and all three transitions. Preserve
original evidence and the archive. After collection, `swaymsg exit` or manually
**Super+Shift+E** closes this disposable compositor/private bus. Review these two
runs before another batch. This handoff does not close P03 or claim integration.
