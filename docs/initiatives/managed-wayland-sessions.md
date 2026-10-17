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
restart the active desktop, or globally enable services during login. Native
compositor configuration remains available through explicit `direct` mode.
