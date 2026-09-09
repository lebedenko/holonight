# UQC-201 user-operated acceptance

Status: **Pending**. Follow [guided batches](GUIDED.md) using the new accessible
kit, Hyprland first and then Sway in a fresh tux login. Run each gate in both.
Automated origin,
selector and geometry fixtures complement these observations; they do not establish
visual acceptance. See [fresh automated evidence](INTEGRATION.md). Historical
[provider collection instructions](../../../holonight-qt/docs/sdd/unified-qtquick-controls/audit/CHECKLIST.md)
remain useful for interpreting traces, but their old prefixes are not this build.

## Prefix and evidence

In the prepared test compositor (start with [GUIDED.md](GUIDED.md)):

```sh
UQC_KIT=/tmp/holonight-uqc201-8r1jtlln
UQC_PREFIX="$UQC_KIT/prefix"
UQC_AUDIT="$UQC_KIT"
test -f "$UQC_PREFIX/lib/qt6/qml/Holonight/qmldir"
pacman -Q haruna neochat tokodon hyprpolkitagent qt6-base qt6-declarative
```

Use the exact prefix verified in INTEGRATION.md. Rebuild if installed Qt changes.
The private prefix is not a system installation. Keep evidence locally and publish
selected diagnostic lines and observations, after checking for personal data.
For every row record date, compositor/version, package/Qt versions, entry point,
selector environment, observed page/control/state, resolved QML URL, loaded native
library path, scale, action/outcome and screenshot reference. A selector name or
module import alone is insufficient evidence of a created control implementation.

## Third-party desktop matrix

Close existing instances yourself before each launch. These commands create empty
application profiles and retain the compositor connection. They do not change the
session activation environment. The helper prints the evidence directory.

```sh
LD_LIBRARY_PATH="$UQC_PREFIX/lib" QT_QPA_PLATFORMTHEME=holonight \
  python3 "$UQC_AUDIT/launch.py" --prefix "$UQC_PREFIX" --mode manual -- /usr/bin/haruna
LD_LIBRARY_PATH="$UQC_PREFIX/lib" QT_QPA_PLATFORMTHEME=holonight \
  python3 "$UQC_AUDIT/launch.py" --prefix "$UQC_PREFIX" --mode manual -- /usr/bin/neochat
LD_LIBRARY_PATH="$UQC_PREFIX/lib" QT_QPA_PLATFORMTHEME=holonight \
  python3 "$UQC_AUDIT/launch.py" --prefix "$UQC_PREFIX" --mode manual -- /usr/bin/tokodon
```

| Surface and user action | Hyprland | Sway |
|---|---|---|
| Haruna: disposable local clip; seek, volume, toolbar, menus, disabled actions, settings editing and scrolling | [ ] | [ ] |
| NeoChat: logged-out welcome/server form, type/select/delete `example.invalid`, validation, back navigation, Tab/Shift+Tab, reachable dialogs | [ ] | [ ] |
| Tokodon: logged-out onboarding/server/search fields, text selection, navigation, reachable scrolling and popups | [ ] | [ ] |
| Each reachable application palette selector: dark → light → dark; inspect controls and reopen page without changing desktop configuration | [ ] | [ ] |
| Enabled/disabled, hover/focus/selection, popup placement and clipping at scale 1 and 1.25 | [ ] | [ ] |

Do not sign in or begin browser authorization. Mark account/network-dependent
surfaces blocked with their prerequisite. Classify each observed surface as
**HoloNight**, **fallback (name Basic or Fusion)**, **application-owned**, or
**blocked (specific reason)**. Haruna's painted sliders and explicit Fusion
fallback, and the accepted Kirigami license-popup composition limitation, remain
explicit boundaries. Do not turn a trace of a lazy import into a visible-state claim.

## Owned applications and session activation

Use a disposable graphical login for activation and configuration-changing checks.
Do not import these paths into the active desktop's D-Bus or systemd manager.
Capture the real login's identity (`loginctl session-status`) before proceeding.
For terminal checks in that test login:

```sh
export PATH="$UQC_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$UQC_PREFIX/lib"
export QML_IMPORT_PATH="$UQC_PREFIX/lib/qt6/qml"
export QT_PLUGIN_PATH="$UQC_PREFIX/lib/qt6/plugins"
export QT_QPA_PLATFORMTHEME=holonight
export QML_IMPORT_TRACE=1 QT_DEBUG_PLUGINS=1 QT_FORCE_STDERR_LOGGING=1
export QT_LOGGING_RULES='*.debug=true;*.info=true'
unset QT_QUICK_CONTROLS_STYLE QT_QUICK_CONTROLS_CONF QT_QUICK_CONTROLS_FALLBACK_STYLE QML2_IMPORT_PATH
"$UQC_PREFIX/bin/holonight-settings" 2>settings-default.log
QT_QUICK_CONTROLS_STYLE=Fusion "$UQC_PREFIX/bin/holonight-settings" 2>settings-fusion.log
```

Repeat for `holonight-chat` and `holonight-packages` after closing each previous
process. Disable AI providers and use an empty test profile; do not send requests.
Package-manager inspection is read-only; do not apply transactions. Use the
[AI launch fixture](../../../holonight-ai/scripts/check-runtime-launches.py) and
[package launch fixture](../../../holonight-pkg-manager/scripts/check-runtime-launches.py)
for their exact disposable configuration. For shell, use a test compositor with
no other panel and the staged `holonight-shell`; inspect menus, sidebar, launcher,
notifications, text inputs and popups without invoking power/session actions.
Greeter live acceptance requires a dedicated test login/seat; the
[greeter fake-backend fixture](../../../holonight-greeter/tests)
provides automated authentication and scaled ComboBox evidence without real login.

| Gate, repeated per owned surface where applicable | Hyprland | Sway |
|---|---|---|
| Embedded default with selector overrides unset; actual loaded HoloNight controls | [ ] | [ ] |
| Explicit Fusion, normal text editing, Tab traversal, list/table/page scrolling | [ ] | [ ] |
| Palette dark/light round trip in disposable configuration; reopen controls | [ ] | [ ] |
| Shell popups, launcher, notification/sidebar routing and keyboard navigation | [ ] | [ ] |
| Greeter pre-session scale/edge popup placement, selected and first/last-row visibility | [ ] | [ ] |
| Terminal launch: selection, QML discovery and loaded library origins | [ ] | [ ] |
| Desktop launcher: same evidence from actual launched PID | [ ] | [ ] |
| D-Bus activation: staged service Exec and actual implementation origins | [ ] | [ ] |
| systemd activation: effective environment, staged executable, actual implementation origins | [ ] | [ ] |

For activation, start the disposable session with the staged prefix in `PATH`,
`XDG_DATA_DIRS`, `QML_IMPORT_PATH`, `QT_PLUGIN_PATH` and `LD_LIBRARY_PATH`.
Set `QT_QUICK_CONTROLS_STYLE=Holonight` for third-party session selection.
Use the staged shell's `holonight-wayland-session-environment` contract and review
its diagnostics before starting applications. The
[session environment tests](../../../holonight-shell/tests/test_wayland_session_environment.py)
and [session script checks](../../../holonight-shell/tests/test_session_scripts.sh)
show the supported propagation paths; passing those fixtures does not check the
current compositor's activation manager.

In the **disposable login only**, after the separate bus and manager environment
review in [GUIDED.md](GUIDED.md#activation-environment-review):

```sh
dbus-update-activation-environment PATH XDG_DATA_DIRS QML_IMPORT_PATH \
  QT_PLUGIN_PATH LD_LIBRARY_PATH QT_QPA_PLATFORMTHEME \
  QML_IMPORT_TRACE QT_DEBUG_PLUGINS QT_FORCE_STDERR_LOGGING QT_LOGGING_RULES
systemctl --user show-environment | rg '^(PATH|XDG_DATA_DIRS|QML_IMPORT_PATH|QT_PLUGIN_PATH|LD_LIBRARY_PATH|QT_QPA_PLATFORMTHEME|QT_QUICK_CONTROLS_STYLE)='
cat "$UQC_PREFIX/share/dbus-1/services/org.holonight.Settings.service"
gdbus call --session --dest org.freedesktop.DBus --object-path /org/freedesktop/DBus \
  --method org.freedesktop.DBus.StartServiceByName org.holonight.Settings 0
systemd-run --user --unit=uqc201-settings --collect \
  "$UQC_PREFIX/bin/holonight-settings"
journalctl --user -u uqc201-settings --no-pager
```

Close Settings between activation paths. The test session bus must have started
with staged `XDG_DATA_DIRS`; an already running bus may not discover new service
files. If it resolves a system service instead, record blocked and start a fresh
test login with correct discovery. Inspect `/proc/<observed-pid>/exe`, `environ`
and `maps` for that exact process, retaining only relevant environment and
HoloNight/Qt paths. Launcher metadata must resolve to this prefix. For third-party
apps, use their installed desktop/service metadata, record applicable routes and
mark nonexistent activation interfaces N/A with file-level evidence. Do not claim
all four activation mechanisms exist for every application.

## Authentication: a separate real login

Do not launch either authentication agent or a challenge in the active desktop.
A private session bus or nested compositor does not isolate system Polkit session
ownership. Use the existing **tux** login and a minimal compositor that starts no
agent. Do not change passwords, Polkit rules, or the normal desktop agent.

The reusable [guarded authentication procedure](../../../holonight-qt/docs/sdd/unified-qtquick-controls/audit/auth-test/README.md)
checks the surveyed Qt version, actual logind identity and successful registration
reply before allowing a challenge. Use a newly prepared kit with this run's prefix;
do not use its historical `/var/tmp/uqc-auth-test-20260907` build. The kit path and
preparation result are recorded in INTEGRATION.md. From a real tux VT login, use
the [guided session launcher](GUIDED.md#batch-1-hyprland-login-and-settings-default)
so prefix discovery precedes the session bus. Follow the self-contained
[authentication instructions](AUTHENTICATION.md). The new prefix is configured
directly at its accessible location; installed service paths are not patched.
In the separate compositor:

```sh
UQC_KIT=/tmp/holonight-uqc201-8r1jtlln
/usr/bin/python3 "$UQC_KIT/auth-test.py" preflight
# Set UQC_RUN to the exact evidence directory printed above, in both terminals.
LD_LIBRARY_PATH="$UQC_KIT/prefix/lib" /usr/bin/python3 "$UQC_KIT/auth-test.py" agent --run "$UQC_RUN"
# Second terminal, same login:
/usr/bin/python3 "$UQC_KIT/auth-test.py" registration --run "$UQC_RUN"
/usr/bin/python3 "$UQC_KIT/auth-test.py" challenge --run "$UQC_RUN"
```

The agent command invokes `/usr/lib/hyprpolkitagent/hyprpolkitagent` with the kit's
staged QML/plugin paths and process-local Holonight selector. Continue only after
the helper's registration PASS. Manually inspect masking with disposable text,
erase it, traverse focus, hover buttons and cancel; never enter a password or
submit. The challenge is `pkexec --disable-internal-agent /usr/bin/true`.
Stop only the directly launched test agent with Ctrl+C. Repeat in a separate Sway
login. HoloNight's own polkit/askpass live cancellation checks require their own
separate test session and ownership review; the shell's fake authentication suite
does not substitute for this manual gate.

| Authentication evidence | Hyprland | Sway |
|---|---|---|
| Separate login, no competing test-session agent, registration reply and PID/session ownership | [ ] | [ ] |
| Compatible Qt hyprpolkitagent: actual HoloNight origins, masking, navigation, geometry, cancellation | [ ] | [ ] |
| Owned authentication: isolated cancellation and scale behavior; no credential submission | [ ] | [ ] |

Return observations and evidence paths. Leave UQC-201 In Progress and the initiative
Accepted until every applicable manual gate is reviewed and final integration is
recorded. A blocked surface needs an explicit resolution, not a checked box.
