# Dropdown and input checkpoint

Use a fresh real **tux VT login**, outside a compositor:

```sh
python3 __KIT__/guided-session.py sway
```

In the test terminal, run and close each app in turn:

```sh
python3 "$UQC_KIT/dropdown-test.py" settings
python3 "$UQC_KIT/dropdown-test.py" settings --style Fusion
python3 "$UQC_KIT/dropdown-test.py" greeter
python3 "$UQC_KIT/dropdown-test.py" greeter --style Fusion
```

Defaults are Qt scale 1.25 and output scale 1. In Settings, enter **Weather**
first and exercise its six selectors, then check **Appearance** font selectors.
In the greeter demo, check the session selector. Leave the pointer over a row
while navigating elsewhere with the keyboard: only the selected row should have
selection feedback. Moving within the hovered row restores pointer feedback;
clicking must work immediately. Compare a representative button and selected row.
Fusion owns its standard-control rendering; HoloNight composites use the shared
input policy under either style.

Repeat only the affected accepted dropdown checks: selected-row visibility on
reopen, first/last selection, scrolling and outside/Escape dismissal. Diagnostics
are saved in `launch.log`; no console warning is expected because output is
redirected. Retain each printed evidence directory and its `isolation.json`.

For the launcher, start the shell in one test terminal:

```sh
python3 "$UQC_KIT/launcher-test.py" run
```

Open another terminal with Super+Return and request the launcher:

```sh
python3 "$UQC_KIT/launcher-test.py" toggle
```

Leave the pointer over another result when opening/reopening, typing a search,
and using Up/Down. Confirm the selected row and intended Enter target stay with
the keyboard. Move within the same row to select it, and check immediate clicking.
Compare browse, search, filters and reopen. Use harmless applications for any
manual launch check. Close test applications afterward; stop only this test shell
with Ctrl+C in its original terminal. Repeat with `run --style Fusion`.

Report observations plus evidence paths. D02, F06 and F07 remain open until the
required manual results support closure. This is a focused checkpoint; broad
integration remains pending. Close apps and exit Sway with Super+Shift+E afterward.

Previous kits and evidence remain unchanged. Rebuild from the umbrella with
`python3 docs/initiatives/unified-qtquick-controls/prepare-dropdown-kit.py`.
The builder prints a persistent `.cache/holonight-uqc206-*/…tar.gz` archive.
Restore that archive after reboot using
`python3 docs/initiatives/unified-qtquick-controls/restore-dropdown-kit.py ARCHIVE`.
Restoration refuses an existing kit and verifies all recorded hashes.
