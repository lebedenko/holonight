# G07 — empty-password caret diagnostic handoff

Released and verified 2026-09-15. G07 remains open; production QML is unchanged.
[Investigation and verification](FINDINGS.md#g07-rendered-investigation-and-diagnostic-handoff--2026-09-15).
UQC-216 is Done for the published diagnostic handoff. UQC-212 stays Done,
Batch 7 closed, UQC-201 In Progress and the initiative Accepted.

## Four short comparisons

From a fresh real `tux` VT login outside the desktop:

```sh
python3 /tmp/holonight-uqc216-e8pceq20/guided-session.py sway
```

In the isolated terminal:

```sh
swaymsg -t get_outputs > "$UQC_SESSION_RUN/outputs.json"
python3 "$UQC_KIT/guided-app.py" greeter --style Holonight --scale 1 --caret-diagnostics
python3 "$UQC_KIT/guided-app.py" greeter --style Holonight --scale 1.25 --caret-diagnostics
python3 "$UQC_KIT/guided-app.py" greeter --style Fusion --scale 1 --caret-diagnostics
python3 "$UQC_KIT/guided-app.py" greeter --style Fusion --scale 1.25 --caret-diagnostics
```

Run them separately using the [G07-only checklist](GREETER-G07.md): initial empty
caret, one disposable character/clearing, focus re-entry and reveal/remasking.
Wait three seconds in each empty focused state so native blink phases are captured.
Close each demo with Super+Q and leave Sway with Super+Shift+E after all four.
Return the session evidence path and four sets of observations. No G01–G06 repeats
or real login are requested. The observer does not change focus or blink timing;
it records geometry and bounded empty-field crops, never entered text.

## Restore after reboot

Only if the original `/tmp` kit is absent, from the umbrella root:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc216-e8pceq20/holonight-uqc216-e8pceq20.tar.gz
```

Archive SHA-256:
`994613367ec844c34b7c19b8e5bcfef85efab15dd7ee28ec120765b59a73d51f`.

All 189 hashes, exact-prefix restoration, existing-path refusal, package versions,
staged source origins, actual DPR and deliberate process exits pass. The four
staged graphics cases pass with host HoloNight modules/libraries masked. Release
verification and raw logs are retained under `.cache/holonight-uqc216-e8pceq20/`.
The previous Batch 7 release is preserved and all its 187 hashes still match.
