# Draft: Qt Quick loses application focus after keyboard recreation on Hyprland

**Draft only; not submitted.** Suggested initial triage: Qt Wayland client
activation, with Hyprland capability/enter ordering included for comparison.
The supported boundary is plain Qt on Hyprland; the exact faulty implementation
and private-cache mechanism are not proven. F05 remains an external compatibility
follow-up, not a repaired behavior.

## Environment

Observed on 2026-09-15 in a real local seat0/tty3 session:

| Component | Observed version/configuration |
|---|---|
| Qt base package | 6.11.2-3 |
| Qt declarative package | 6.11.2-2 |
| Hyprland package | 0.56.2-3 |
| Platform / shell | Qt Wayland / xdg-shell, confirmed in process mappings |
| Controls | Fusion, confirmed in process mappings |
| Qt scale / actual DPR | 1.25 / 1.25 in both windows |
| Output | 2560×1600, scale 1, approximately 240 Hz |
| Launch | dbus-run-session -- Hyprland --config <isolated-config> |

The isolated compositor configuration selects `monitor = , preferred, auto, 1`
and terminal/exit bindings. The fixture process maps no HoloNight libraries or
QML plugins. The recorded package inventory matches the retained test kit.
Graphics mappings include both Mesa and NVIDIA EGL libraries; they do not alone
identify the renderer in use. Kernel/active GPU attribution is not established
by this evidence and is not used to assign ownership.

## Reproducer

Source: [main.cpp](main.cpp). Its default mode uses only Qt Quick and Qt Quick
Controls. A workspace button lazily creates a settings Window, shows it and
calls raise/requestActivate from that user-triggered action. The settings window
contains an editable SpinBox, Slider, Switch and buttons. No application data or
network provider is involved. The optional Hn mode is not used in this report.

Standalone build and launch, from a terminal inside the isolated session:

```sh
g++ -std=c++23 -fPIC main.cpp -o fixture $(pkg-config --cflags --libs Qt6Quick Qt6Qml)
env -u LD_PRELOAD -u QT_PLUGIN_PATH -u QML_IMPORT_PATH -u QML2_IMPORT_PATH \
    -u QT_QUICK_CONTROLS_CONF -u QT_SCREEN_SCALE_FACTORS -u LD_LIBRARY_PATH \
    QT_QPA_PLATFORM=wayland QT_QPA_PLATFORMTHEME= \
    QT_QUICK_CONTROLS_STYLE=Fusion QT_SCALE_FACTOR=1.25 ./fixture
```

These commands describe the uninstrumented standalone reproduction to try
upstream; this exact standalone launch has not been manually VT-tested. The
recorded reduced run uses [run.py](run.py) in `--mode plain` with
[observer.cpp](observer.cpp) preloaded. The runner checks mappings and saves
events and process outcome. Its `--prefix` selects the staged search locations;
plain mode rejects any mapped HoloNight library.

Manual sequence:

1. Start the isolated compositor from a real VT3 login.
2. Open settings, select the numeric editor, check Tab and Shift+Tab, then return
   to the numeric editor.
3. Switch VT3 → VT1 → VT3 using the real keyboard.
4. Before moving/clicking the pointer, check Tab and Shift+Tab again.
5. Use Quit fixture and retain the logs.

## Expected and actual behavior

Expected: after keyboard enter returns to the settings surface, Qt application
focus is restored and keyboard traversal works without a pointer action.

Actual: the user reports the same behavior as the earlier Fusion failure. The
reduced log directly establishes capability loss, replacement keyboard enter,
null Qt application focus and Tab/Backtab delivery to the settings window after
return. The user explicitly confirms navigation worked before switching, stopped
visibly updating after return before any pointer movement/click, and recovered
after a later click. This interaction evidence comes from the user; the observer
does not record pointer actions. Process exit is 0.

## Sanitized evidence

[Relative-time trace](evidence/plain-vt-trace.jsonl), with
[SHA-256 manifest](evidence/SHA256SUMS). The trace includes protocol callbacks,
navigation metadata and changed Qt samples. Repeated identical samples were
removed; times are relative to keyboard-capability loss, and Qt pointer values
are replaced with workspace/settings/item aliases. Protocol IDs remain separate
from Qt aliases. It includes no paths, entered text or unrelated key values.

| Relative time (ms) | Observation |
|---|---|
| Before 0 | Tab and Backtab reach settings and item receivers; focus items change and frames advance. Settings toplevel 60's last configure is activated; keyboard surface is 55. |
| 0 | Seat callback reports keyboard unavailable, without a preceding settings keyboard-leave callback. |
| +64 | Qt application focus is null, application state 2; settings inactive, focus item null, frame counter 60. |
| +7647 | Keyboard capability returns. |
| +7648 | Replacement keyboard listener installs successfully (protocol ID 28 reused); enter targets surface 55 again. |
| +33603, +34293 | Two Tab presses reach both Wayland callback and Qt settings-window observer. |
| +39183/+39184 | Shift+Tab reaches the Wayland callback / Qt Backtab observer. |
| Through +50264 | Settings frame counter remains 60; application focus and settings focus item remain null. |
| +50364 onward | Settings frame signals resume, reaching 70. At +51464 an item focus appears, but application focus is still null and settings inactive. |

No toplevel configure or keyboard leave is recorded at or after the capability
loss. The only leave in the run occurred earlier when focus moved from workspace
to settings. Protocol surface/settings association is based on lifecycle order,
dimensions and delivery; the observer does not implement a native-ID join.

Frame counters count Qt frameSwapped signals, not physical presentation. The
observer sees key events before final handling and cannot establish their final
acceptance. Later frame/focus-item changes do not establish click recovery.

## Hypothesis and bounded follow-up

The previously retained Qt 6.11.2 source audit identifies an asymmetric path:
Keyboard destruction clears Qt focus directly, whereas ordinary leave also
updates QWaylandDisplay's keyboard-focus state. Re-entering the same window could
then be suppressed by the cached-window equality check. See the source references
and audit in [the diagnosis README](README.md#evidence-and-source-boundary--2026-09-15).
This run measures the surrounding protocol/Qt behavior, **not mLastKeyboardFocus
or the execution of that early return**.

A bounded upstream experiment would trace that private cache through capability
loss and same-surface re-entry, then verify a candidate fix with the same real-VT
sequence and normal leave/enter regression coverage. An uninstrumented reduced
run would additionally remove the observer from this exact fixture comparison;
the previously completed AI comparison already reproduced with observation off.
No such patch, repeat run or upstream submission is performed in this iteration.
