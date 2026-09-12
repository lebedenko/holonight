# UQC-204 — short Settings/AI keyboard regression

Completed: user reported no issues in all four runs on 2026-09-11. See the
[canonical result](FINDINGS.md#manual-focus-acceptance--2026-09-11) for scope and
evidence limits. The instructions below are retained for reference; no repeat
is requested.

Fresh kit: `/tmp/holonight-uqc201-focus-5ydxn45l`.
Provider: `65c806fb6a65cae9652dde7a69d595813973c1a9`; all other product pins unchanged.
This is a Settings/AI focus kit, not a replacement full ecosystem acceptance kit.
The previous temporary kit is missing; retained logs and evidence are preserved. Initiative Accepted; UQC-201 In Progress.

From a fresh real **tux** VT login outside the current compositor, start the new
Sway test session (log out of the previous test session first):

```sh
python3 /tmp/holonight-uqc201-focus-5ydxn45l/guided-session.py sway
```

In its terminal, run each command separately, closing the app before the next:

```sh
python3 "$UQC_KIT/guided-app.py" settings --scale 1.25
python3 "$UQC_KIT/guided-app.py" settings --style Fusion --scale 1.25
python3 "$UQC_KIT/guided-app.py" ai --scale 1.25
python3 "$UQC_KIT/guided-app.py" ai --style Fusion --scale 1.25
```

- **Settings:** visit Weather City and edit/erase disposable text. On the first
  Tab traversal, check that eligible controls show focus. Complete one cycle and
  reverse with Shift+Tab; confirm indicators remain visible and there are no
  invisible wrapper stops.
- **AI:** open the provider form with Context window and Temperature. Check
  Context value → Temperature value → Slider, then reverse. Confirm no intermediate
  invisible stop. Check the first ComboBox entry and one repeated cycle.

Keep providers disabled and do not use refresh/test-connection or send requests.
Do not repeat slider dragging, dropdown mouse failures, authentication, other forms,
VT switching, or unrelated known defects. Button activation ring loss and checked
Switch contrast remain separate findings. Both styles/scales already have automated
provider coverage; this short real-app check uses the reported fractional scale.

Report **pass/fail for first and repeated forward/reverse focus**, any exact control
where it fails, and the printed evidence directories. Close apps and exit the test
compositor when finished. All UI interaction is manual. No other acceptance gate
is closed by this check.

## Preparation evidence — 2026-09-11

Retained dependency caches referenced removed temporary prefixes. Dependencies
were reconfigured and rebuilt against the new prefix before installation. Settings
and AI were freshly configured/built/installed at that prefix, preserving their
pinned source revisions and generating activation paths for the new installation.
Source files were not changed. Existing session/app helpers were regenerated into
the fresh kit; the copied guide is this focused request rather than the historical
broad batch list. Disposable profile creation disables AI providers/title generation.

Private build/verification records:
`.cache/holonight-uqc201-focus-5ydxn45l/{results,verification}.jsonl` and `logs/`.
Exact preparation/verification scripts are retained there. Provider focus fixtures
run under both styles at scales 1/1.25 with host provider QML/config masked. Settings
and AI installed startup checks cover all four selection modes with private buses,
disposable profiles and forbidden build discovery. No live desktop input automation.
Restoration checks passed: 8/8 wrapper regressions in each of four style/scale
cases, four installed startup modes per application, helper syntax, activation
paths, wrapper source parity, runtime linkage, and 189 prefix hashes. Host provider
QML/config was masked and the entire repository root forbidden in installed
startup discovery. The sandbox initially denied the private D-Bus socket; the
permitted rerun passed, with the failed attempt preserved in the logs.
The kit is released with READY and SHA256SUMS (check from the prefix directory). Manual observations remain pending and will be recorded once in
FINDINGS.md; only findings supported by those observations may be closed.
