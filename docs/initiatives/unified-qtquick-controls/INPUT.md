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

Defaults are Qt scale 1.25 and output scale 1. This follow-up checks the
stationary-pointer dropdown repair only:

1. In Settings **Appearance**, open a font selector with enough rows to scroll.
   Move the pointer over a visible row, then leave it still. Press Down until the
   list scrolls, then Up through the scroll boundary. The highlight must follow
   each key without jumping to the pointer's row; Enter must commit that highlight.
2. Reopen the selector with the pointer still in the popup area. The committed
   row must remain visible and highlighted. Move the pointer deliberately to
   another row to restore mouse selection. After a keyboard step, click a row
   immediately to confirm clicking still works.
3. Repeat in the greeter demo session selector if it has enough rows to scroll;
   otherwise check keyboard selection, reopen and immediate clicking, and report
   that scrolling could not be exercised.

Run both apps under default HoloNight and Fusion using the commands above.
Fusion owns its standard-control behavior; these checks target the shared icon
selectors used by Settings and greeter. No launcher or broad application rerun is
requested in this follow-up. Existing F07 and D02 manual gates remain pending.

Report the app/style, whether the **highlight** or **committed value** changed,
and the printed evidence paths including `isolation.json`. F06 remains open until
this real-session check passes. Close apps and exit Sway with Super+Shift+E.

Previous kits and evidence remain unchanged. Rebuild from the umbrella with
`python3 docs/initiatives/unified-qtquick-controls/prepare-dropdown-kit.py`.
The builder prints a persistent `.cache/holonight-uqc206-*/…tar.gz` archive.
Restore that archive after reboot using
`python3 docs/initiatives/unified-qtquick-controls/restore-dropdown-kit.py ARCHIVE`.
Restoration refuses an existing kit and verifies all recorded hashes.
