# Managed Wayland session coordination

The shell owns the [session lifecycle and environment design](../../holonight-shell/docs/sdd/managed-wayland-sessions.md),
compositor adapters, UWSM hook, portal defaults and read-only session doctor. The
umbrella dependency profile requires UWSM. Compositor installation remains selected
by the user: Hyprland (with start-hyprland), Sway or labwc. Recommended portal packages
are xdg-desktop-portal, xdg-desktop-portal-gtk, and xdg-desktop-portal-hyprland or
xdg-desktop-portal-wlr. HoloNight supplies Settings and FileChooser providers.

Build/install providers before shell consumers using host dependencies. Existing
installer staging, collision checks, ownership manifests and conservative uninstall
remain authoritative. Shell assets use the configured prefix and never embed DESTDIR.
Run shell session/installation tests, umbrella installer tests, and both repositories'
`task check:integration`. Complete real systemd/compositor acceptance in a disposable
VM or dedicated test user. Container binaries are acceptance-only.

`auto` now requires UWSM. Apply on next login; do not migrate personal configuration,
restart the active desktop, or globally enable services during login. Managed
Hyprland loads the native Lua entrypoint with tracked imports. Sway includes the
first personal file in native user-path order. labwc uses the persistent personal
directory when `rc.xml` exists. Each compositor uses installed defaults only when
its personal entrypoint is absent. Existing HoloNight override files block login
until the user explicitly merges desired settings into native configuration.

Shell owns the private structured systemd state protocol, login association and
preflight. UWSM owns activation and teardown; verified managed logout uses `uwsm stop`
for every compositor. Managed Polkit routing uses the login binding and Wayland peer
credentials without requiring compositor environment access.

Appearance owns persistent labwc mutations. Resolution order is explicit
`--labwc-config`, `HOLONIGHT_LABWC_CONFIG_DIR` supplied by Shell, then standalone
native discovery. Ownership tied to a different directory remains a conflict; no
runtime path or automatic ownership migration is introduced. Settings continues to
invoke the adapter normally. Ship Appearance's variable support before Shell's new
configuration routing; umbrella publication pins remain unchanged until authorized.

The native-configuration revision's automated checks and completed three-compositor
VM acceptance are recorded in the Shell design. The supplied hn-arch VM used native
builds and a separate test account for actual authentication, ordered Shell logout,
application survival, native reload and fallback login. Firefox received screen-sharing
frames after accepting each backend's real interactive picker. Focused installed-prefix
checks and the 87-case umbrella installer suite cover the changed packaging contract;
unchanged full ecosystem container acceptance was not repeated.
