# P03 — focused AI Settings palette recheck

Prepared baseline: umbrella `6f7af409a38b7a217fec38bf607e43446f86c07f`, provider
`e94ceddbd3c0e4cb29e21bcdfd6758e3e4639f4f`. Use only the new READY kit
`/tmp/holonight-uqc201-p03-c_w7vh8n`; [readiness evidence](P03-READINESS.md).
P03 is open, UQC-222 Done, UQC-201 In Progress, initiative Accepted.
Earlier interaction, navigation and main-window checks remain accepted.

Exactly two sequential human-operated runs follow. From a fresh real **tux** VT
login outside a compositor:

```sh
python3 /tmp/holonight-uqc201-p03-c_w7vh8n/guided-session.py sway
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

Now manually open AI Settings. Inspect native text fields, SpinBoxes and reachable
selectors in light mode: backgrounds, text, disabled states and shared composites.
Closing and reopening Settings retains its Loader instance; only this first open
in light mode tests light-time construction.

Keep Settings **open** through dark → light → dark. Issue each command separately
in the other terminal, returning manually to inspect Settings between commands:

```sh
python3 "$UQC_KIT/ai-palette.py" dark
python3 "$UQC_KIT/ai-palette.py" light
python3 "$UQC_KIT/ai-palette.py" dark
```

Record pass/fail/inaccessible for each visible surface in each state. Name the
field, numeric control, selector or composite; describe background/text/disabled
state inconsistencies. Record empty or inaccessible controls without enabling
providers or creating network content. Observer origins cover instantiated objects,
not unopened pages or all painted pixels. Automated provider diagnostics and AI
component tests establish readiness; ordinary AI startup does not instantiate
its lazy Settings window, and the workspace round trip is separate evidence.

Close Settings and then AI normally using their close controls, or manually use
**Super+Q** with the intended AI window focused. Do not use Ctrl+C. Wait for the
launcher outcome before starting the next run.

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
