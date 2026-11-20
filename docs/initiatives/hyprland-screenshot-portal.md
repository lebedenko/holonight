# Hyprland screenshot portal integration

Install the host build of the screenshot provider first. Build the portal
against that installed package with `-DHOLONIGHT_PORTAL_SCREENSHOT=ON`.
The provider owns capture and selection, and the portal owns broker
authorization, approval, request lifetime, and session PNGs.
[Capture design](../../holonight-screenshot/docs/capture.md)
[Portal design](../../xdg-desktop-portal-holonight/docs/sdd/screenshot.md)

Use a fresh prefix for the capture provider. Build the CLI again with
`-DSCREENSHOT_USE_INSTALLED_CAPTURE=ON` and build the opted-in portal with the
same prefix on `CMAKE_PREFIX_PATH`. Run both test suites, including the
private-bus screenshot tests and staged service activation.

For a staged Hyprland session, make the staged backend service and
`holonight.portal` visible to the private session bus and the broker. In the
staged `xdg-desktop-portal/hyprland-portals.conf` under `XDG_CONFIG_HOME`,
keep the session’s existing preferences and set these entries under
`[preferred]`.

```ini
org.freedesktop.impl.portal.Screenshot=holonight
org.freedesktop.impl.portal.Access=gtk
```

Start the broker with the staged configuration and verify from its verbose
log that it selects HoloNight for Screenshot and GTK for Access. The broker
needs Access for the non-interactive screenshot permission flow.
[Portal routing configuration](https://flatpak.github.io/xdg-desktop-portal/docs/portals.conf.html)

Manually verify a full-desktop capture, annotated area sharing across
differently scaled outputs, and PickColor on each output. Check Escape or
Cancel and verify that a sandboxed app can read the shared PNG through the
broker’s document export. Run these interactively in Hyprland.

Publish the provider before the consumer. The umbrella installer stages
the screenshot provider after HolonightQt. The default source build of the
portal keeps the Screenshot option off. Default Hyprland routing is a
separate release handoff.
