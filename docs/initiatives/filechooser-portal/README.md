# HoloNight FileChooser portal

Status: Accepted

## Goal

Provide a standalone Wayland FileChooser backend, sharing focused browsing logic and passive listing
presentation with Files. The approved implementation plan in the task authorizes this scope.

## Non-goals

Recursive search, previews, thumbnails, bookmarks, devices, X11 parenting and other portal interfaces.
Keep Files' command handling, operations, restore/persistence and existing search semantics private.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| holonight-files | Installed browsing Core/Quick provider; application adoption | [SDD](../../../holonight-files/docs/sdd/filechooser-provider/README.md) |
| xdg-desktop-portal-holonight | Protocol, lifecycle, chooser, Wayland parenting | [SDD](../../../xdg-desktop-portal-holonight/docs/sdd/filechooser/README.md) |
| holonight-shell | FileChooser routing; preserve Settings identity | [SDD](../../../holonight-shell/docs/sdd/filechooser-routing/SPEC.md) |

## Cross-repository contracts

Files installs HolonightFileBrowser with Core and optional Quick components, and QML module
Holonight.FileBrowser. Core owns asynchronous current-folder enumeration, natural sorting/hidden-file
behavior, Home/XDG places and icon metadata. Quick is passive: consumers supply model, cursor and selected
paths; it emits cursor/activation/selection requests and allows delegate extension. Preserve HolonightFiles.
Provider-only builds must not require Files' unrelated runtime providers.

Backend executable/repository: xdg-desktop-portal-holonight. Descriptor: holonight-filechooser.portal.
Bus: org.freedesktop.impl.portal.desktop.holonight_filechooser. Object: /org/freedesktop/portal/desktop.
Implement OpenFile, SaveFile and SaveFiles with delayed replies and independently cancellable Request objects.
Keep Settings bus org.freedesktop.impl.portal.desktop.holonight in Shell.

Operation, directory and multiple are independent. Preserve filters and choices on the wire, normalize
local URIs preserving path bytes, validate destinations asynchronously without creating files, explicitly
confirm SaveFile overwrites, and number SaveFiles collisions deterministically in input order.
Use holonight-search for current-folder fuzzy matching. Use private xdg-foreign-v2 import following Viewer's
native approach; missing/destroyed parents leave an ordinary usable chooser. Keyboard: j/k/h/l, /,
Ctrl+L, explicit multi-selection toggles; SaveFile initially focuses its filename. Invalid starting locations
fall back to Home with explanation; no persisted location history.

## Dependency order

1. I-001 Files provider and adoption. Baseline: 3806c96c014e1897336c854cfb0ca490cec1d50d (origin/main).
2. I-002 New standalone backend using the published installed provider; no existing baseline.
3. I-003 Shell routing. Baseline: 25e1556bc5ffc06015a757d48e468f7c0d9c9ccb (origin/main).
4. I-004 Umbrella ecosystem acceptance.

Provider revisions must be published and pinned before dependent consumer work starts, as required by the
initiative template. Publication and pin updates require user authorization. No publication is implied by
local implementation. Provider compatibility reference: holonight-qt 6c7ac33004702e166b8c152dcde918296be54286.

## Integration acceptance criteria

- [ ] Repository work packages have published commits and passed local verification.
- [ ] Submodules are clean and pinned to published revisions.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Builds/tests pass in dependency order, including installed provider C++/QML consumers.
- [ ] Isolated D-Bus tests cover signatures, options/results, activation, cancellation, concurrent requests and cleanup.
- [ ] Chooser tests cover selection modes, filters, choices, escaped/native paths, conflicts, removed entries and stale work.
- [ ] Manual native acceptance on Hyprland, Sway and labwc covers parenting, keyboard, modality, cancel and placement.
- [ ] Real broker acceptance with Viewer, Settings folder selection and sandboxed caller confirms document access.

References: [backend contract](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.FileChooser.html),
[Request lifecycle](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Request.html),
[routing](https://flatpak.github.io/xdg-desktop-portal/docs/portals.conf.html).
