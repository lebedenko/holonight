# Qt upgrades and desktop recovery

The appearance adapter reloads the UWSM labwc unit only after matching its main
PID to the session PID. The managed unit and its existing SIGHUP action belong to
the session. The adapter retains the generated files when a reload fails.
See the [labwc theme guide](../../holonight-appearance-adapters/docs/labwc-theme.md).

The portal backend sends the Settings dictionary with one variant layer per
entry. The public broker forwards the same typed values. Viewer handles a
chooser response of 2 with an explicit action that marks the Qt Quick file
dialog as non-native. Viewer and the portal backend communicate through the
public protocol and can be installed independently. See the
[Viewer opening guide](../../holonight-viewer/README.md#opening-images).

Shell, the Qt theme, and the portal each install their own metadata under
`share/holonight/qt-build`. Each record contains the exact Qt version and the
absolute Qt Core SONAME path used by the build. Shell's session check resolves
that path against the host installation and compares live mappings by device
and inode when the relevant build versions match. The check can run before
Shell loads Qt. Missing records allow older component installations to coexist.
Build the Qt provider first when a rebuild is required, then build Shell and
the portal against the installed provider and host Qt. Deploy through the
umbrella installer and restart the affected services after portal work finishes.

Managed reload and standalone signalling have isolated adapter coverage. The
[broker test](../../scripts/check-filechooser-broker.py) stages the backend and
checks Settings wire types, live changes, and FileChooser dispatch and close.
Viewer's offscreen mock tests exercise recovery without a second OpenFile call.
Shell's tests cover matching metadata, stale mappings, startup failure without
notifications, notification deduplication, and staged timer installation.
Manual acceptance uses existing labwc windows and the desktop's broker and GTK
client to confirm the visible theme and selection behavior.
