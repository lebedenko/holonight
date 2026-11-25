# Screenshot portal integration

Install the host builds of HolonightQt with Wayland support and the
standalone screenshot provider. Build the portal against the
installed packages with `-DHOLONIGHT_PORTAL_SCREENSHOT=ON` and
`-DHOLONIGHT_PORTAL_ACCESS=ON`. The installer keeps its defaults. The stock
distro broker owns consent persistence and document export.
[Capture design](../../holonight-screenshot/docs/capture.md)
[Capture backend design](../../xdg-desktop-portal-holonight/docs/sdd/screenshot.md)
[Access backend design](../../xdg-desktop-portal-holonight/docs/sdd/access.md)

Use a fresh prefix for the capture provider. Build the CLI with
`-DSCREENSHOT_USE_INSTALLED_CAPTURE=ON` and place the same prefix on the portal's
`CMAKE_PREFIX_PATH`. Run the capture-provider and private-bus portal tests.
Stage both default and opt-in portal payloads and check discovery and D-Bus
activation with the distro broker.

In the staged session's active portal config under `XDG_CONFIG_HOME/xdg-desktop-portal`,
retain the other preferences and set these entries under `[preferred]`.

```ini
org.freedesktop.impl.portal.Access=holonight-access
org.freedesktop.impl.portal.Screenshot=holonight
```

Verify in the stock broker's verbose log that it selects the two staged
descriptors. Compare both split-backend configurations with the corresponding
third-party Access or Screenshot implementation. Changing Access routing also
changes other broker prompts that use Access. To roll back, restore the previous
session preference and start a fresh session.
[Portal routing configuration](https://flatpak.github.io/xdg-desktop-portal/docs/portals.conf.html)

## Native release gate

Exercise Hyprland with long animations, then Sway and labwc with normal compositor
settings. Use `grim` and the wlroots layout adapter's `wlr-randr --json` where applicable.
Compare the former card area against solid and patterned references on mixed-scale
outputs, and confirm pointer and keyboard input return when the card clears.

Reset the Flatpak probe's screenshot permission between first-use Allow and Deny.
Repeat after saved decisions and with ask-every-time. Test Escape, request
cancellation, interactive capture, PickColor, and reading the exported PNG from
the Flatpak app. Check an Access prompt unrelated to screenshots. Compare the
interactive Area crop against the expected raster bounds across a mixed-scale seam.

Keep Access staged until all three compositors pass. Record any presentation
failure or capture artifacts with the compositor, scale, and animation settings.
Publish the provider before the consumer when releasing the coordinated change.

[Hyprland investigation and acceptance results](hyprland-screenshot-investigation/README.md)
