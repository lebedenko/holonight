# Real application acceptance — I-004

Status: Published/pinned backend and Shell routing are ready. Automated isolated
broker checks passed. On 2026-10-09 the user reported the requested live Viewer
file selection, Settings folder selection, cancellation/reopen and keyboard checks
passed on Hyprland. Other matrix cases remain pending. See [evidence](VERIFICATION.md).
The prior native probe pass validates the chooser follow-up, not these real-broker
and sandbox document-access checks.

## Prerequisites

Record the exact umbrella, Files provider, backend and Shell revisions. Confirm
clean published gitlinks. Build/install into a disposable staging root in provider
order and run applicable integration checks before any live deployment.
Inspect staged executable, D-Bus activation service and portal descriptor, plus
HoloNight/Hyprland/Sway/labwc routing. GTK remains configured as fallback.
Live installation and portal service restarts require separate explicit approval.
Use manual application actions only; never automate pointer/focus interaction.

## Required cases

| Case | Manual action | Pass condition |
|---|---|---|
| Viewer file | Open a known local image through Viewer | HoloNight chooser appears via the broker; selected image opens; no fallback dialog or console error |
| Settings folder | Use the wallpaper folder picker | Folder-specific heading; selected folder reaches Settings correctly; cancellation preserves the previous setting |
| Cancel and reopen | Cancel each application request, then open again | No stale request or duplicate chooser; application stays usable |
| Multiple files | Use a broker caller requesting multiple files | Explicit selection count; returned set matches checked files |
| Save and overwrite | Use a broker caller requesting SaveFile, choose an existing destination | Replacement confirmation is required; cancellation does not alter the file; caller receives the confirmed URI |
| Parent disappearance | Close the requesting parent with the chooser open | No crash or unusable orphan; resulting lifecycle behavior is recorded |
| Sandboxed document access | Select an external test file from a sandboxed application lacking direct access | Application can read the selected file through the document grant; opening the chooser alone is insufficient evidence |

Viewer exports a Wayland parent for its portal flow. Settings currently sends an
empty parent identifier, so its folder test is intentionally unparented and cannot
prove native parenting. Confirm the broker actually selected holonight-filechooser;
the application's generic portal support alone does not establish routing.

Repeat native parenting, modality, placement and keyboard checks on Hyprland,
Sway and labwc, recording compositor/version, scale and selected modes. Preserve
the user's existing Hyprland probe acceptance; identify any additional uncovered
cells rather than claiming an exhaustive matrix from that report.

## Evidence

Record date, exact revisions, commands, application/caller identities, selected
backend, per-case results and relevant log paths. Check latest hosted CI once per
published revision and record its status/conclusion/link; do not poll or use older
passing runs as acceptance of a newer commit.

Mark I-004 Done and the initiative Integrated only after all required cases and
exact-revision integration checks pass. Missing environments or sandbox callers
remain explicit acceptance gaps.
