# UQC-201 guided acceptance

Preparation baseline: `7fcc8bb48a451185b9412950ac7f651ee75975c7`.
Initiative **Accepted**; UQC-201 **In Progress**. Every manual result is pending.
The real pre-session greeter gate remains separate from demo observations.

## Accessible kit

Current kit: `/tmp/holonight-uqc201-8r1jtlln`, configured directly with installation
prefix `/tmp/holonight-uqc201-8r1jtlln/prefix`. Build records are in
`.cache/uqc201-guided-qht3_tjs`. The older relocated kit and its evidence remain
historical. This temporary kit must be rebuilt if removed or installed Qt changes.
The `READY` marker is written only after preparation checks pass.

The kit contains [the session launcher](guided-session.py),
[application/evidence helper](guided-app.py), minimal compositor configurations,
guarded authentication helpers, package/revision inventory, and prefix hashes.
The [kit preparation script](prepare-guided-kit.py) copies the pinned provider
helpers and applies the reviewed [owned-agent adaptation](owned-auth.patch).
The launcher verifies its own real logind ownership before starting a compositor.
It creates disposable XDG directories under `~/uqc-guided-evidence`, disables all
configured AI providers/title generation, and selects a disposable appearance
file. It sets prefix discovery before `dbus-run-session` creates the test bus.
It does not import anything into a systemd manager. No agent autostarts.

## Batch 1: Hyprland login and Settings default

Save work and use a spare VT to log in directly as **tux**. Do not use sudo, su,
SSH or a nested compositor. From that VT:

```sh
python3 /tmp/holonight-uqc201-8r1jtlln/guided-session.py hyprland
```

In the terminal opened by the minimal compositor:

```sh
printf '%s\n' "$UQC_SESSION_RUN"
python3 "$UQC_KIT/guided-app.py" settings
```

At scale 1, inspect the initial page, traverse with Tab/Shift+Tab, edit and erase
disposable text in an available field, scroll a page, and open/close a selector.
Do not change system settings. Report which controls/pages were exercised,
visible focus, clipping or popup issues, and the printed evidence directory.
Close Settings yourself. Review these observations before starting batch 2.

Super+Enter opens another test terminal; Super+Q closes the focused window;
Super+Shift+E exits the compositor. All keyboard, pointer and focus interactions
are user-operated. Log tux out after each compositor run.

## Subsequent batches (issue individually after review)

1. Settings Fusion and scale 1.25; owned AI/package-manager defaults and Fusion,
   editing/navigation/scrolling/popups. Use `guided-app.py ai`, `packages`, or
   `settings`, with `--style Fusion` and/or `--scale 1.25`. Never send AI requests
   or apply package transactions. For shell use `guided-app.py shell` in the
   minimal compositor; inspect menus/sidebar/launcher without power/session actions.
2. Haruna, NeoChat, Tokodon: `guided-app.py haruna`, `neochat`, or `tokodon`.
   Third-party default explicitly selects Holonight; owned default leaves overrides
   unset. Exercise the logged-out [manual matrix](MANUAL.md), repeating at scale
   1.25. Open the kit's `sample.mp4` manually in Haruna; no sign-in or browser authorization.
3. Available application palette selectors: dark → light → dark, reopen controls.
   Settings' appearance selection targets the disposable `HOLONIGHT_APPEARANCE_FILE`.
   Preserve HoloNight, named fallback, application-owned and blocked classifications;
   Haruna painted sliders/Fusion and accepted Kirigami composition limitations remain
   explicit. Absence of a selector is recorded with its scope, not a visual pass.
4. Activation: terminal, desktop launcher, D-Bus and systemd where supported.
   Close each previous instance manually. Inspect installed desktop/service metadata
   first, then correlate the actual PID using `guided-app.py collect --pid PID`.
   Retain launch/journal control-origin lines; library loading alone does not prove
   a particular created control. Haruna has desktop metadata but no installed D-Bus
   service. NeoChat and Tokodon each have a service under `/usr/share/dbus-1/services`.
   An ad hoc `systemd-run` is a transient execution route, not a product-shipped unit.
5. Authentication: follow [AUTHENTICATION.md](AUTHENTICATION.md), separate agent
   runs, registration PASS before cancellation-only challenge. Third-party and
   owned agents never run together. Owned askpass is independent of Polkit.
6. Greeter: `guided-app.py greeter`, repeated at scale 1.25 and Fusion. Only demo
   mode is launched. Inspect selector geometry near edges and selected/first/last
   row reachability. Record **demo**; leave real pre-session acceptance unchecked.
7. Exit and log out tux. Start a fresh tux VT login and repeat batches in Sway:
   `python3 /tmp/holonight-uqc201-8r1jtlln/guided-session.py sway`.

The scale option changes Qt's process scale, with compositor output scale 1.
Record both values. If compositor output scaling is also required, the user
changes it manually and records the resulting pair; do not multiply both silently.

## Activation environment review

The test bus starts with the prefix in `XDG_DATA_DIRS`. After compositor startup,
review the verified socket-peer environment:

```sh
"$UQC_PREFIX/libexec/holonight-wayland-session-environment" \
  "$XDG_SESSION_ID" "$XDG_RUNTIME_DIR" | tr '\0' '\n'
```

In the **tux test login only**, after reviewing identity and ensuring no other tux
graphical login uses its user manager, propagate the actual compositor connection
to the test bus. Keep default selectors unset for owned default checks:

```sh
dbus-update-activation-environment WAYLAND_DISPLAY DISPLAY XDG_SESSION_ID \
  XDG_RUNTIME_DIR PATH XDG_DATA_DIRS XDG_CONFIG_HOME XDG_DATA_HOME XDG_CACHE_HOME \
  XDG_STATE_HOME XDG_CONFIG_DIRS HOLONIGHT_APPEARANCE_FILE QML_IMPORT_PATH \
  QT_PLUGIN_PATH LD_LIBRARY_PATH QT_QPA_PLATFORM QT_QPA_PLATFORMTHEME \
  QML_IMPORT_TRACE QT_DEBUG_PLUGINS QT_FORCE_STDERR_LOGGING QT_LOGGING_RULES
```

Import those same named variables plus `DBUS_SESSION_BUS_ADDRESS` into tux's
systemd user manager only for the systemd batch, after reviewing its existing
selected environment. This is a separate explicit guided step; no session helper
does it automatically. Never import test paths into the normal desktop's manager.
Record effective unit environment and actual PID; inspect selected journal lines.
Before leaving that batch, restore the selected manager variables to their
recorded values (unset only variables absent before the batch). Do not dump or
publish unrelated environment values. Authentication always runs from the test
terminal, where actual logind session membership is preserved.

## Evidence review

For each result record date, compositor/package/Qt versions, compositor and Qt
scale, executable/entry point, selector environment, surface/state, user action,
outcome, created implementation origin, loaded native libraries and local evidence
reference. Recollect the PID after opening lazily loaded pages. Authentication
frontends may intentionally deny `/proc` inspection through `PR_SET_DUMPABLE=0`;
record that limitation and use direct-child/session/registration and origin logs.

Raw evidence stays in the tux home. Review personal data before sharing selected
diagnostics; do not publish complete authentication logs. No manual result is
inferred from an automated fixture. Newly found product defects require separate
repository-owned work packages and local SDDs at these exact pins.

| Reviewed batch | Compositor / scale | Outcome / classification | Evidence |
|---|---|---|---|
| None yet | — | Pending user operation | — |
