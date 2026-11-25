# Hyprland screenshot and layer focus investigation

Both patches for each Hyprland base are independent. Each was checked against
the exact base with `git apply --check --whitespace=error`. Host-native builds
and changed-file clang-format checks passed. The patches are local investigation
artifacts. [Hyprland BSD 3-Clause notice](../../../LICENSES/BSD-3-Clause.txt)

| Hyprland base | Cursor capture | Keyboard focus |
| --- | --- | --- |
| 0.57.2, `11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947` | [Capture patch](v0.57.2/fix-capture-cursor.patch) | [Focus patch](v0.57.2/fix-layer-click-focus.patch) |
| Upstream main, `423da96907feb3eef7ca4e06dc5cb69e9eec63a8` | [Capture patch](upstream/fix-capture-cursor.patch) | [Focus patch](upstream/fix-layer-click-focus.patch) |

## Reproduction and attribution

Use a private nested Hyprland session on the specified base. Keep one swatch
window active. Use a static high-contrast fixture for capture comparisons.

| Scenario | Result | Procedure and evidence |
| --- | --- | --- |
| Stock Hyprland 0.57.2 cursor in a cursor-excluded export | **known upstream limitation** | Keep the pointer still and take monitor captures with grim with and without `-c`. Repeat at a second pointer location. On stock 0.57.2 the images at each location were pixel-identical and both contained one cursor. Moving the pointer changed the cursor-excluded capture. Wayland traces recorded session flags 0 and 1. The compositor trace showed the software cursor drawn before the mirror framebuffer copy used for capture. This reproduced without either portal backend. |
| Patched monitor and region capture on both bases | **pass** | Repeat the two-position comparison and use a direct wlr-screencopy region request. Excluded PNGs were identical across positions. Included PNGs matched the corresponding stock single-cursor images with no pixels at the previous location. Direct regions matched their full-output crops. The release region check used the standard color path and upstream forced the unmodified color attachment. |
| Stock Hyprland 0.57.2 same-window keyboard handoff | **known upstream limitation** | Set `follow_mouse=0`. Focus the swatch, open a layer with on-demand keyboard interactivity, focus it, then click the still-active swatch outside the layer and type. The swatch received the click while keys still went to the layer. This reproduced independently of portal routing. Dispatch `hl.dsp.focus({window = 'address:<window-address>'})` with the active swatch address to restore key delivery without closing the layer. |
| Patched keyboard handoff on both bases | **pass** | Repeat the outside click and type while the layer remains mapped. The swatch received the key. Clicking the on-demand layer restored key delivery to it. An exclusive layer retained keyboard focus after an outside click. |
| GTK Access with HoloNight Screenshot on patched Hyprland 0.57.2 | **known upstream limitation** | With stock xdg-desktop-portal 1.22.1-2 and GTK backend 1.15.3-2, route `Access=gtk` and `Screenshot=holonight`. Enable layer animations at speed 15, reset the screenshot permission, allow the request, then compare the decoded Flatpak export with the pre-request reference. Routing, export and input passed. A fresh run isolated the pixel mismatch to the fading GTK dialog at raster bounds (1348, 897)–(1732, 1027), with exclusive right and bottom edges. HoloNight Screenshot receives the request after GTK Access replies and has no presentation feedback for the GTK dialog. |
| Stock upstream-main behavior before applying either patch | **unverified** | The paired upstream-main build was tested with the fixes. |

The capture patch copies scene damage before drawing the software cursor. The
capture renderer reads that copy and composites the current cursor on request.
Physical mirrors retain their final output copy. The capture point precedes the
DPMS black overlay and final render hook. The focus patch extends click-refocus
when the clicked window is already active, its surface is under the pointer,
and the keyboard focus belongs to an on-demand layer. It retains the existing
pointer-constraint and seat-grab checks.

## Headless acceptance with the stock broker

The private stock broker was xdg-desktop-portal 1.22.1-2. HoloNight Access and
Screenshot used the same staged backend with SHA-256
`561f837765d47b8f7c2dbd8a749d78ac774c9f15682c01180480cec678daa8ba`.
Mixed-scale outputs were 2560 × 1600 at 1.25 and 3840 × 2160 at 1.5.
The Hyprland requalification used patched 0.57.2 and all four layer animations
at speed 15. Sway 1.12 and labwc 0.20.3 used normal compositor settings.

| Case | Patched Hyprland 0.57.2 | Sway 1.12 and labwc 0.20.3 |
| --- | --- | --- |
| First-use Allow, saved Allow | **pass** | **pass** |
| First-use Deny, saved Deny | **pass** | **pass** |
| Ask every time, Allow and Deny | **pass** | **pass** |
| Escape and client Close | **pass** | **pass** |
| Interactive Desktop and cross-output Area | **pass** | **pass** |
| PickColor on each output | **pass** | **pass** |
| Non-modal same-window handoff | **pass** | **unverified** |
| Overlapping Access calls | **pass** | **unverified** |
| Camera Access and unmatched hold retirement | **pass** | **unverified** |
| GTK Access with HoloNight Screenshot | **known upstream limitation** | **unverified** |
| HoloNight Access with Hyprland Screenshot 1.5.0-1 | **pass** | **unverified** |

Hyprland first-use, patterned ask-every-time, non-modal and overlap exports
matched all 6912 × 2160 RGB pixels. In the overlap run, the second call reached
Access, returned Busy and produced public response 2 with empty results. The
first prompt remained mapped and completed normally. The original run had timed
out before the second backend dispatch. The completed Sway and labwc runs
matched the full-export and Area reference pixels, returned both expected
PickColor values, and restored pointer and keyboard input after first-use Allow.

## Physical-display acceptance

| Test setup | Result | Evidence |
| --- | --- | --- |
| Stock Hyprland 0.57.2-1 with stock broker and both HoloNight routes staged | **known upstream limitation** | eDP-1 at 1.25 and DP-3 at 1.5, sRGB, layer animations at speed 15. First-use Allow and ask-every-time Allow exported readable PNGs. The RGB comparisons differed at 1,378 and 1,372 pixels respectively in pairs of cursor-sized regions. Direct cursor-on and cursor-off captures both showed the cursor. In non-modal Access the swatch received the outside click while keys stayed with the card until it cleared. |
| Stock Hyprland physical overlap with both HoloNight routes staged | **pass** | Two distinct request tokens on one Flatpak connection. The second Access call returned Busy and response 2 with empty results. The first prompt stayed mapped, then completed with a decodable PNG. |
| Full physical matrix using the patched compositor and stock broker, and staged Access on physical Sway and labwc | **unverified** | The matching complete matrix ran headless. |
| Earlier physical frozen-consent implementation, private patched broker | **pass** | Hyprland, Sway and labwc exported real Flatpak Documents PNGs. Fresh and saved decisions, one-shot consent, Escape and Close, explicit and interactive cross-output Area, and layout invalidation and retry were exercised. Fresh full exports matched 6912 × 2160 on Hyprland and 7680 × 2400 on Sway and labwc. Independent pointer traces established exact mixed-scale Area bounds. This earlier broker and backend contract exercised a different consent path. |

## Publication verification

| Scenario | Result | Evidence |
| --- | --- | --- |
| Installed-package integration | **pass** | Screenshot provider `c5ffc7f4dc36f6bd760a59128c5a3854b6b01f2d` passed 7 CTest suites. The CLI rebuilt using the installed capture package and passed 6 suites. The portal built against the same installed provider and host-native HolonightQt. |
| Staged portal activation | **pass** | The stock broker activated the staged backend, selected `holonight-access.portal` for Access and `holonight.portal` for Screenshot in the opt-in configuration, and exposed the public Screenshot interface. Private-bus Screenshot, Access, and Settings tests passed. |
| Full visual matrix for the publication pins | **unverified** | The final provider has a newer Wayland capture and selection implementation. The historical headless and physical results above identify the tested configurations. The final pins were checked with installed-package builds, private-bus tests and broker activation. |

The recorded staging requalification identified no HoloNight regression.
Keep Access opt-in. See the [integration guide](../hyprland-screenshot-portal.md)
for the staged configuration and native release gate.
