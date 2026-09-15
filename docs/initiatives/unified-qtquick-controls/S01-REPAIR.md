# S01 fractional shell repair acceptance

**Verified kit: `/tmp/holonight-uqc211-8ptiz_ko`.**
[Release evidence](FINDINGS.md#s01-provider-repair-and-f05-reduced-diagnosis--2026-09-15). Keep previous kits and completed Batch 6 comparisons.
This kit contains the provider coordinate repair; no shell compensation or F05
workaround is included. Output scale stays **1**, Qt scale **1.25**.

From a real fresh tux VT login outside a compositor:

```sh
python3 /tmp/holonight-uqc211-8ptiz_ko/guided-session.py hyprland
```

In the kit terminal, run one at a time:

```sh
python3 /tmp/holonight-uqc211-8ptiz_ko/guided-app.py shell --style Holonight --scale 1.25 --index batch6 --session-diagnostics
python3 /tmp/holonight-uqc211-8ptiz_ko/guided-app.py shell --style Fusion --scale 1.25 --index batch6 --session-diagnostics
```

Check only the repaired behavior:

1. Stable startup and bar height.
2. Hover/tooltip stability, without jumping or resizing.
3. Rightmost sections remain inside the screen.
4. Popups appear at their intended anchors.
5. Clickable controls align with their visible locations.
6. An ordinary application respects the bar's reserved space.

Perform every pointer/focus action yourself. Stop each shell using Ctrl+C and
allow the collector to finish. Record pass/fail for each check and the session
path printed by the helper. Scale-1 comparisons and the completed AI VT matrix
remain accepted evidence and are not requested again. F05 is a separate reduced
fixture diagnosis, not an AI acceptance run in this kit. S01 remains open until
these checks pass. Final ecosystem integration remains open.
