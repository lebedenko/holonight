# Workspace overview snapshot contract

[Shell design and acceptance](../../holonight-shell/docs/sdd/workspace-overview.md)

`holonight-system-services` is the provider. The compositor component publishes opaque window IDs and optional workspace IDs and logical layout rectangles in its existing snapshot. Workspace IDs refer to workspaces in that snapshot, including reported Hyprland special workspaces. Missing membership and geometry stay unknown. The per-window command list advertises exact-ID activation, and the PID/title request stays available to existing callers.

For live previews the Sway provider also publishes the optional `foreign_toplevel_identifier`
from `GET_TREE`. The shell joins it to the Wayland foreign-toplevel identifier and keeps
the numeric container ID for activation. Hyprland uses its full address mapping protocol.
The shell owns capture and preview lifetime and uses integration ABI 5.0 for the changed
snapshot layout. See the [live preview contract and acceptance](../../holonight-shell/docs/sdd/workspace-overview.md#live-previews).

Build and install the provider into a development prefix, then build the shell against that prefix. Run the provider compositor and install-consumer tests, the shell test and QML checks, and session smoke tests on Hyprland, Sway, and Labwc. Make the provider commit available before updating the shell’s standalone CI pin and the umbrella gitlinks. Rebuild shell integration plugins against the same provider headers and library as the shell executable.
