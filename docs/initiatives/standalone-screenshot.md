# Standalone HoloNight Screenshot

Screenshot builds against host Qt 6.11+, libwayland-client, and LayerShellQt 6.6+. Its installed CMake package resolves these dependencies before importing `HolonightScreenshot::Capture`. The capture package remains consumable by the opted-in portal, including its direct region overlay path. The standalone build uses the host Wayland scanner and protocol XML files. See the [capture design](../../holonight-screenshot/docs/capture.md) and [change record](../../holonight-screenshot/docs/aidlc/2026-11-24-standalone-wayland-overlay.md).

The Arch source installer selects Screenshot independently. It checks for `layer-shell-qt`, `qt6-wayland`, `grim`, `wl-clipboard`, and `wlr-randr`. Sway and labwc use `wlr-randr` to discover the output layout, and Hyprland uses `hyprctl`. The desktop refresh hook and staged ownership checks apply to the executable, desktop entry, and fallback icon. Build deployable payloads against host dependencies and use container builds for acceptance.

Before release, test the fresh standalone checkout and a separate CLI build consuming the installed capture package. Build and test the opted-in portal against that same prefix. Check ordinary launcher and save-dialog roles, the mixed-scale overlay on Sway, labwc, and Hyprland, and clean failure on a Wayland display without layer-shell. Run focused installer tests and verify Screenshot's files and ownership in a disposable root. Track actual results in the component change record.

Publish Screenshot first after authorization. Update the umbrella pin only after the Screenshot revision is available.
