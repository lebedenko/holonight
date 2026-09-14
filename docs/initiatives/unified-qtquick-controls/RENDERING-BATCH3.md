# Batch 3 dropdown background checks

The user has completed these checks and accepted dropdown backgrounds and geometry
in all three apps. See the [manual acceptance record](FINDINGS.md#batch-3-dropdown-background-manual-acceptance--2026-09-14).
Do not repeat these accepted checks. Tokodon’s intermittent missing chevron is deferred at the user’s request; no further
comparison is requested. The commands below describe the completed session.

Results are recorded once in [FINDINGS.md](FINDINGS.md#batch-3-dropdown-background-repair--2026-09-14).
The initiative remains Accepted and UQC-201/UQC-207 remain In Progress.
Check dropdown backgrounds only, at scale 1. Preserve accepted icon, Switch,
Haruna selection, authentication and navigation results. Busy-button disable/re-enable
focus is expected Qt behavior and has no repair in this kit.

From a fresh local **tux** VT login:

```sh
python3 __KIT__/guided-session.py hyprland
```

In its terminal, run each command separately and close the app normally afterward.
Start with NeoChat's logged-out settings/scheme dropdown. Open it, leave it open
for two seconds, close and reopen it, then close the settings window and app.
Inspect whether the background covers the entire list. Use either keyboard or mouse;
there is no need to repeat accepted navigation checks.

```sh
python3 __KIT__/rendering-test.py neochat --style Holonight --scale 1 --diagnostics
QT_LOGGING_RULES='*.debug=false;*.info=true' python3 __KIT__/rendering-test.py neochat --style Holonight --scale 1
python3 __KIT__/rendering-test.py neochat --style Fusion --scale 1 --diagnostics
python3 __KIT__/rendering-test.py tokodon --style Holonight --scale 1 --diagnostics
python3 __KIT__/rendering-test.py haruna --style Holonight --scale 1 --diagnostics
```

For Tokodon and Haruna, use a settings dropdown and repeat open/close/reopen, then
close the settings window and app. Keep the logs if a ScrollBar warning occurs and
report the exact preceding action. Its reduced lifecycle trigger is still unresolved;
this kit makes no ScrollBar repair claim. The historical Haruna crash remains open.

The first NeoChat run retains the original Qt debug logging trigger; the second
turns off debug logging and the optional observer. The Fusion run is the reference.
No fractional-scale check is requested because this failure involves deferred
background sizing during Qt diagnostics, not scale conversion.

Report the five printed evidence directories, whether each dropdown has complete
background coverage after opening and reopening, and any teardown warning/crash.
The observer records existing popup/control/content/background geometry and actual
window DPR. Unopened deferred popups remain uninstantiated. Logging configuration,
module isolation, process outcome and log hash are retained in the run evidence.
All pointer and focus interaction is human-operated.
