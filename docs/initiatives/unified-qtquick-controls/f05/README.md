# F05: reduced activation diagnosis

Status: **external Qt/Hyprland reproduction established; exact mechanism unresolved**.
The [plain-Qt result](../FINDINGS.md#f05-plain-qt-external-reproduction--2026-09-15)
and [upstream-report draft](UPSTREAM-REPORT.md) complete this diagnosis iteration.
The report is not submitted and F05 is not repaired. No HoloNight implementation
owner is demonstrated. No AI/provider workaround or external patch.
The completed AI matrix is preserved; it is not requested again.

## Evidence and source boundary — 2026-09-15

The analysis below predates the reduced manual run. That run now establishes
capability loss without leave, same-surface re-entry and persistent null Qt focus
in plain Qt. The private cache itself is still unmeasured; see the canonical
result above for the supported disposition and frame-signal limitations.

Hyprland's observed runs keep delivering navigation after VT return while Qt's
application focus is null. In the retained HoloNight run, the replacement
keyboard listener installs at `1789469203140`, enter follows at `1789469203155`,
and the focus sample is null at `1789469203199`. There is no keyboard-leave
callback at this VT boundary. In Sway's passing comparison, leave is recorded at
`1789467474497`, the replacement listener at `1789467479204`, enter at
`1789467479206`, and restored settings focus at `1789467479299`.
These are callback/sample timestamps, not measurements of Qt's private cache.
The retained files are under umbrella `.cache/uqc211-manual/`.

The installed Qt is 6.11.2. Inspection of its matching source identifies a
specific candidate:

- [QWaylandInputDevice](https://github.com/qt/qtbase/blob/v6.11.2/src/plugins/platforms/wayland/qwaylandinputdevice.cpp):
  losing seat keyboard capability destroys Keyboard. Its destructor clears Qt
  focus directly when it has a focused surface. Ordinary keyboard leave instead
  calls handleFocusLost, which also notifies QWaylandDisplay. The replacement
  keyboard's enter handler notifies the display.
- [QWaylandDisplay](https://github.com/qt/qtbase/blob/v6.11.2/src/plugins/platforms/wayland/qwaylanddisplay.cpp):
  handleKeyboardFocusChanged returns immediately when the new window equals
  mLastKeyboardFocus. A destructor path that clears Qt focus while retaining this
  cached window can therefore suppress restoration when enter targets the same
  window. Activation normally reaches Qt through a Wayland sync callback.
- [xdg-shell integration](https://github.com/qt/qtbase/blob/v6.11.2/src/plugins/platforms/wayland/plugins/shellintegration/xdg-shell/qwaylandxdgshell.cpp):
  Toplevel::applyConfigure updates display activation from the toplevel state
  only when no keyboard is available. Toplevel activation alone need not restore
  Qt focus after keyboard recreation.

This source path is consistent with the Hyprland/Sway difference. It does not
prove which precise capability/configure ordering occurred in the historical
runs. Those logs lack seat capability and xdg-toplevel state, and do not measure
frame presentation. HnApplicationWindow is a Window/content/header composite;
its implementation and the platform-theme source contain no activation or
keyboard-lifecycle handling. This audit supplies no demonstrated HoloNight
implementation owner.

**Remaining mechanism question:** whether Qt retains mLastKeyboardFocus and its
equality check suppresses activation after same-surface re-entry. Capability
loss without leave and absent frame swaps during failed navigation are now
recorded in plain Qt; causality and physical presentation remain unproven.
No speculative AI repair package is Ready.

## Reduced fixture

`main.cpp` uses the AI workspace's lazy settings Loader and user-triggered
show/raise/requestActivate lifecycle. It has a numeric editor, slider, switch
and close controls. It has no providers, saved form data or network activity.
All variants select **Fusion**, Qt scale **1.25**:

| Mode | Window composite | Platform theme |
|---|---|---|
| `plain` | Qt Window | No HoloNight libraries permitted in mappings |
| `theme` | Qt Window | Staged HoloNight platform theme |
| `hn` | HnApplicationWindow | No HoloNight platform theme |

`observer.cpp` forwards the original protocol callbacks and logs seat keyboard
capability, listener creation, enter/leave, navigation only, xdg-toplevel
activation, Qt application/per-window focus and cumulative frameSwapped counts.
It never records entered text or unrelated keys, requests focus, synthesizes
pointer input or requests a repaint. frameSwapped is Qt's presentation signal;
it is not proof of physical scanout. Toplevel protocol IDs and Qt window IDs are
separate; dimensions/order aid correlation but do not provide a native-ID join.
Final Qt key-event acceptance is not claimed by this observer.

## Automated verification

```sh
python3 docs/initiatives/unified-qtquick-controls/f05/run.py --prefix /tmp/holonight-uqc211-8ptiz_ko/prefix --verify
```

The runner builds Qt-only executable/observer binaries, starts private headless
Sway and smoke-loads both windows without sending input or requesting activation.
It checks actual Fusion/provider mappings, both windows at DPR 1.25, successful
seat/toplevel observation, frameSwapped records and normal exits. A deterministic
navigation receiver checks unchanged delivery/acceptance and text exclusion.

All three variants passed on 2026-09-15 using the repaired provider installed in
the shell's local dependency prefix, and again against the fresh kit prefix.
Final installed-kit evidence: `/tmp/f05-reduced-aqxfh2gw`, preserved under
`.cache/uqc215/f05-kit-evidence/`; summary `.cache/uqc215/f05-kit-verification.log`.
Earlier local-prefix evidence is `/tmp/f05-reduced-pxdzxa_b`. These checks validate the
reproducer and its isolation, **not VT-return behavior**. Headless Sway has no
physical keyboard; the completed plain-Qt manual run separately verifies real
keyboard listener/enter/Tab callbacks and Qt navigation delivery. The initial verification
attempt exposed an incorrect platform-theme filename check in the runner; its
corrected check uses the mapped platformthemes directory.

## One focused manual check, when ready

**Completed: plain Qt fails. Do not repeat this checklist or run theme/hn for
this iteration.** The commands remain here for reproduction provenance.

The released kit and retained verification were
[revalidated for this iteration](../FINDINGS.md#f05-activation-diagnosis-setup--2026-09-15).
From a fresh real tux login on VT3, outside a compositor, start the isolated session:

```sh
python3 /tmp/holonight-uqc211-8ptiz_ko/guided-session.py hyprland
```

Within the isolated Hyprland session, start with **plain only** (output scale 1):

```sh
printf '%s\n' "$UQC_SESSION_RUN"
hyprctl -j monitors > "$UQC_SESSION_RUN/f05-monitors.json"
python3 /tmp/holonight-uqc211-8ptiz_ko/f05/run.py --prefix /tmp/holonight-uqc211-8ptiz_ko/prefix --mode plain
```

Open settings yourself, select the numeric editor, test Tab/Backtab, then perform
VT3 → VT1 → VT3 yourself. Before touching the pointer, test navigation again and
note visible focus/caret behavior. Use Quit fixture when finished and retain the
printed evidence directory. If plain Qt reproduces, that is the first external
compatibility gate; inspect its capability/activation/frame correlation before
requesting another run. Only if plain passes is the theme/Hn split needed. Do not
repeat the original AI matrix or automate pointer, focus or VT actions.

Report both printed directories, navigation before/after the VT switch, whether
the pointer moved or a click occurred after return, and the quit outcome. Retain
the session's `identity.txt`, `versions.txt`, `command.json`, compositor log and
`f05-monitors.json`, and the fixture's `events.log`, `mappings.txt` and
`outcome.json`. Copy selected evidence to persistent umbrella `.cache/` storage
and hash it; exclude profiles and cookies. Sanitize paths and unrelated session
details before attaching any evidence to an upstream-report draft.

### Decision gate

- **Plain fails:** require real keyboard listener/enter/Tab callbacks, correlate
  capability changes, activation, Qt focus and frame-swap counts, then draft an
  external compatibility report. The private Qt focus-cache mechanism remains a
  hypothesis unless directly measured. Do not submit the report in this iteration.
- **Plain passes:** repeat the same sequence with `--mode theme`, then `--mode hn`;
  verify each variant's staged mappings before assigning a HoloNight owner.
- **All pass or evidence is incomplete:** keep F05 unresolved and name the missing
  condition. Missing physical-keyboard evidence cannot be replaced by smoke tests.

Product repair requires a subsequent repository-local SDD and published baseline.
S01/S02 and the completed AI comparisons remain accepted; UQC-201 stays In Progress
and the initiative Accepted. Batch 7, remaining Batch 3 diagnostics and final
integration are outside this iteration.
