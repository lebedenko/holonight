# F05: reduced activation diagnosis

Status: **ownership unresolved**. No AI/provider workaround or external patch.
The completed AI matrix is preserved; it is not requested again.

## Evidence and source boundary — 2026-09-15

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

**Unresolved boundary:** whether real Hyprland removes keyboard capability
without a preceding leave, Qt retains mLastKeyboardFocus, and re-entering that
same settings window suppresses activation; and whether absent frame swaps
explain the visible navigation failure. A plain Qt real-VT reproduction is
needed before assigning an external compatibility disposition. No speculative
AI repair package is Ready.

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
physical keyboard; the new observer's real keyboard-listener forwarding still
needs the reduced manual run. The initial verification
attempt exposed an incorrect platform-theme filename check in the runner; its
corrected check uses the mapped platformthemes directory.

## One focused manual check, when ready

Within the isolated Hyprland session, start with **plain only** (output scale 1):

```sh
python3 /tmp/holonight-uqc211-8ptiz_ko/f05/run.py --prefix /tmp/holonight-uqc211-8ptiz_ko/prefix --mode plain
```

Open settings yourself, select the numeric editor, test Tab/Backtab, then perform
VT3 → VT1 → VT3 yourself. Before touching the pointer, test navigation again and
note visible focus/caret behavior. Use Quit fixture when finished and retain the
printed evidence directory. If plain Qt reproduces, that is the first external
compatibility gate; inspect its capability/activation/frame correlation before
requesting another run. Only if plain passes is the theme/Hn split needed. Do not
repeat the original AI matrix or automate pointer, focus or VT actions.
