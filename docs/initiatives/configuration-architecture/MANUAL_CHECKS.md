# User-operated configuration checks

These checks remain pending until the user reports the results. Automated tests do not substitute for them.
Use the accepted revisions in `TASKS.md`; the Settings binary must be rebuilt from its recorded implementation commit.
Do not automate pointer movement or window focus. All interaction below is performed by the user.

## Prepare an isolated session

From the umbrella root, run this in a dedicated terminal and close it after testing. Keep it open during the checks; its exported variables can also launch a
second Settings instance on a separate private D-Bus session. Native outputs are confined to the disposable home;
the keyfile GSettings backend and empty labwc PID prevent changes to the live desktop's settings and compositor.

```sh
umask 077
export CONFIG_CHECK_ROOT="$PWD"
mkdir -p "$CONFIG_CHECK_ROOT/build"
export CONFIG_CHECK_HOME="$(mktemp -d "$PWD/build/configuration-manual.XXXXXX")"
mkdir -p "$CONFIG_CHECK_HOME/config/holonight" "$CONFIG_CHECK_HOME/state" "$CONFIG_CHECK_HOME/data"
export HOME="$CONFIG_CHECK_HOME"
export XDG_CONFIG_HOME="$CONFIG_CHECK_HOME/config"
export XDG_STATE_HOME="$CONFIG_CHECK_HOME/state"
export XDG_DATA_HOME="$CONFIG_CHECK_HOME/data"
export HOLONIGHT_APPEARANCE_FILE="$XDG_CONFIG_HOME/holonight/appearance.toml"
export GSETTINGS_BACKEND=keyfile
export LABWC_PID=
export LD_LIBRARY_PATH="$CONFIG_CHECK_ROOT/holonight-settings/build/deps/prefix/lib"
export QML_IMPORT_PATH="$CONFIG_CHECK_ROOT/holonight-settings/build/deps/prefix/lib/qt6/qml"
export PATH="$CONFIG_CHECK_ROOT/holonight-appearance-adapters/build/test:$PATH"
cat > "$XDG_CONFIG_HOME/holonight/config.toml" <<'TOML'
# preserve this comment
[bar.workspaces]
count = 5
[bar.systemtray]
max_items = 3
[future]
value = 'untouched'
TOML
cat > "$HOLONIGHT_APPEARANCE_FILE" <<'TOML'
version = 2
# preserve this appearance comment
[theme]
scheme = 'holonight-dark'
accent = 'blue'
TOML
printf 'Disposable configuration: %s\n' "$CONFIG_CHECK_HOME"
dbus-run-session -- "$CONFIG_CHECK_ROOT/holonight-settings/build/test/apps/settings/holonight-settings" &
```

Do not replace `XDG_RUNTIME_DIR`; retain the real session's display/runtime environment for this user-operated window.
To open a second isolated instance against the same documents, repeat only the last `dbus-run-session` command in the
same terminal. Both application windows now have independent baselines and edit batches.

## Concurrent editing and reset

1. In the first window, set workspace count to 7 without saving.
2. In the second window, set tray item count to 4 and save. The first window must update its untouched tray control
   to 4, retain pending workspace count 7, and save both values without losing the original comment or future table.
3. In the first window, change workspace count to 8 without saving. In the second, change it to 9 and save.
   Review the first window's conflict: baseline, external and pending values must be visible. Choose **Keep pending**
   for that preference and save; unrelated values and text must survive.
4. Repeat a same-value conflict, choose **Accept external**, and confirm only that preference's draft is removed.
   Other pending preferences remain editable and dirty.
5. Expand **Defaults and overrides**, reset workspace count, and save. It must return to its default while the `count`
   assignment disappears; comments, surrounding sections and unknown fields remain.
6. Make a pending change, edit the document in a text editor to an invalid known value, and save in Settings.
   Settings must retain the draft, show diagnostics and leave the invalid document unchanged. Correct it externally;
   untouched controls must recover. **Discard Changes** must then load the latest valid document.

## Appearance application

1. Change color scheme, font size and accent in Settings; save. Confirm the Settings preview/window updates and the
   Integrations page reports each native output's outcome. Missing desktop-specific adapters may report limited
   propagation; record that outcome instead of reporting full native application.
2. Inspect the disposable appearance document and native GTK/KDE/labwc output files. The document must retain its
   original comment and only requested preference changes. Record which native outputs were available.
3. Reset a preference and save; confirm its assignment disappears and its effective default is displayed.
4. Use the second Settings instance to edit unrelated appearance preferences and confirm live updates in the first.
   Repeat a same-preference conflict and resolve it per value.

Exact rollback, intervening-writer, retargeted-symlink and changed-revision application failure behavior is covered by
provider, adapter and Settings regressions. If a manual native failure occurs, report its diagnostic and whether an
external edit survived; do not retry by overwriting the entire appearance document.

## Result to report

Report pass/fail for concurrent unrelated edits, same-preference keep/accept resolution, reset, invalid-document
recovery, appearance preview/application, and available native outputs. Include the verification date and any failure
text. The coordinator records these results with the exact revisions before marking the initiative Integrated.
