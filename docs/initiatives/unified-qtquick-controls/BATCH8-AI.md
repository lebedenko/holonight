# Batch 8 — AI Sway fractional coverage

Use `/tmp/holonight-uqc201-final-dyxe1nl_` only after its READY marker is present.
[Release evidence](BATCH8-REVALIDATION.md) records verification and restoration.
Exactly two manual runs are prepared: embedded default and explicit Fusion, with
output scale 1 and application DPR 1.25. Review both before issuing another batch.
UQC-201 remains In Progress and the initiative Accepted.

From a fresh real **tux** VT login outside a compositor:

```sh
python3 /tmp/holonight-uqc201-final-dyxe1nl_/guided-session.py sway
```

In its terminal, record output scale and run the first command. Run the second
only after closing the first application and completing its evidence collection:

```sh
swaymsg -t get_outputs -r > "$UQC_SESSION_RUN/outputs.json"
python3 "$UQC_KIT/guided-app.py" ai --style default --scale 1.25 --index batch6 --palette-diagnostics
python3 "$UQC_KIT/guided-app.py" ai --style Fusion --scale 1.25 --index batch6 --palette-diagnostics
```

`batch6` selects the existing per-run profile isolation and index format; it does
not request Batch 6 VT tests. Each profile copies the session's disabled-provider
configuration and disables title generation. The first launch clears all Controls
style overrides. Only the palette observer is enabled. Do not add rendering or
session observer flags. DPR must be measured from returned observer evidence,
not inferred from the command. Do not repeat VT-return checks.

For each run:

1. Type several lines of disposable text in the offline composer. Select, edit,
   erase and restore text without sending it. Check Tab/Shift+Tab, visible focus,
   keyboard navigation and editing. Do not enable providers, submit prompts,
   enter credentials or start authorization.
2. Inspect reachable local settings/selectors/popups; test keyboard dismissal,
   first/last reachable rows, containment and readability. Check scrolling in the
   composer and any reachable local scroll area. Report disabled/empty provider
   selectors and unavailable conversation history as coverage limits; do not
   create network content to populate them.
3. Perform the isolated dark → light → dark round trip below. Inspect the composer,
   navigation, open local panels and reachable selectors in each state. Report
   visible surface names and any inconsistency, so review can correlate them with
   the palette observer's created-object origins.

Open a second terminal manually with **Super+Return** while AI remains open.
Run each palette command separately, returning to inspect AI between commands:

```sh
python3 "$UQC_KIT/ai-palette.py" dark
python3 "$UQC_KIT/ai-palette.py" light
python3 "$UQC_KIT/ai-palette.py" dark
```

The helper selects the latest live AI evidence directory, verifies its process
and isolated profile, writes only that run's appearance file, and records each
transition. It refuses a closed run or a profile with enabled providers. These
writes do not change the main desktop or released kit.

Close AI using its workspace window close control or manually press **Super+Q
while the AI workspace is focused**. A terminal alternative targets its recorded
PID without changing focus (close local settings dialogs first):

```sh
python3 - <<'PY_CLOSE'
import json, os, subprocess
from pathlib import Path
session = Path(os.environ["UQC_SESSION_RUN"])
run = max(session.glob("ai-*"), key=lambda p: p.stat().st_mtime_ns)
assert not (run / "exit.txt").exists()
record = json.loads(next(run.glob("pid-*.json")).read_text())
assert Path("/proc", str(record["pid"]), "exe").resolve() == Path(os.environ["UQC_PREFIX"]) / "bin/holonight-chat"
subprocess.run(["swaymsg", f"[pid={record['pid']}] kill"], check=True)
PY_CLOSE
```
 Do not use Ctrl+C as the normal close procedure. Wait for the launcher
to print its exit/outcome before starting the second run. The Sway close binding
is part of this kit's original hashes; no configuration patch is needed.

After both runs, collect the session evidence from its terminal:

```sh
printf '%s\n' "$UQC_SESSION_RUN"
cat "$UQC_SESSION_RUN/batch6-index.jsonl"
UQC_AI_ARCHIVE="/tmp/$(basename "$UQC_SESSION_RUN")-batch8-ai.tar.gz"
if ( set -o noclobber; tar -czf - -C "$(dirname "$UQC_SESSION_RUN")" "$(basename "$UQC_SESSION_RUN")" > "$UQC_AI_ARCHIVE" ); then
    chmod 644 "$UQC_AI_ARCHIVE"
    sha256sum "$UQC_AI_ARCHIVE"
fi
```

Return the printed session path, `/tmp` archive path/hash, both AI evidence paths, and your
pass/fail/inaccessible observations for each checklist item. Preserve the archive
and original evidence for review. **Super+Shift+E** exits the disposable Sway
session and its private bus; the isolated files can remain for evidence return.
Alternatively, after the evidence archive is complete, this terminal command
performs the same session cleanup:

```sh
swaymsg exit
```

No system service or main-user configuration restoration is needed.

Observer origins cover instantiated controls, not unopened pages or every painted
pixel. The automated appearance-file check verifies the owned workspace background
round trip; the bootstrap application/window palette roles stay unchanged. Inspect
native Fusion controls separately and report whether they change and remain
readable alongside the owned surfaces. Do not infer a uniform palette transition. Application-owned surfaces, Fusion/Basic fallbacks and inaccessible
provider/account/history controls must be distinguished in review. These two
runs do not establish successful authentication, shipped-service activation,
real pre-session greeter operation, or other unresolved matrix cells.
