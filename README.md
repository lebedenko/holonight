# HoloNight

HoloNight is an umbrella repository for coordinating and verifying changes across the independently maintained
HoloNight projects. It contains cross-repository initiative contracts and pins published component revisions; product
implementation stays in the component repositories.

## Repository map

| Repository | Ownership | Umbrella state |
|---|---|---|
| `holonight-qt` | Shared Qt/QML design system and reusable primitives | Pinned submodule |
| `holonight-shell` | Desktop shell and system surfaces | Pinned submodule |
| `holonight-icons` | Shared icon assets | Pinned submodule |
| `holonight-config` | Toolkit-neutral shared configuration contracts | Pinned submodule |
| `holonight-appearance-adapters` | Toolkit-neutral and GTK desktop appearance adapters | Pinned submodule |
| `holonight-ai` | AI desktop application | Pinned submodule |
| `holonight-greeter` | Pre-session login UI, greetd IPC, authentication flow, and session selection | Pinned submodule |
| `holonight-pkg-manager` | Package manager | Pinned submodule |
| `holonight-settings` | Settings application | Pinned submodule |
| `holonight-images` | Shared image inspection, raster decoding and metadata | Pinned submodule |
| `holonight-viewer` | Static image viewer | Pinned submodule |
| `holonight-files` | Keyboard-driven file manager | Pinned submodule |
| `xdg-desktop-portal-holonight` | Standalone Wayland FileChooser portal | Pinned submodule |
| `holonight-system-services` | Shared Qt/C++ system-control integration | Pinned submodule |
| `holonightd` | HoloNight service | Pinned submodule |

## Working with the umbrella

Clone published components with:

```sh
git clone --recurse-submodules <umbrella-url>
```

For a component change, work in that repository. Cross-project changes use one umbrella
note defining shared contracts, dependency order and integration checks. Follow
[CONTRIBUTING.md](CONTRIBUTING.md); historical SDDs remain reference material.

Use `task build` and `task test` in a component for native CMake/CTest iteration,
`task format` for the pinned formatter, and `task check` before committing.
`task check:integration` adds Release staging and runtime checks. Each repository stores
the same immutable development image reference and uses the same launcher in GitHub.
See [the shared image](packaging/ci/README.md) and component `DEVELOPMENT.md` files.

For joint development, `task build` at the umbrella builds the current siblings into
`build/integration/prefix`; `task test` also runs their tests. `task check:integration`
uses exact umbrella gitlinks in a fresh container. During an uncommitted cross-project
change, explicitly use `task check:integration -- --siblings .` to test current checkouts.
Publish providers before consumers that pin them, then update umbrella pins once per milestone.

## Installing from source

The umbrella can build every pinned production component in dependency order and install the completed result under
`/usr`:

```sh
task install -- --check
task install
```

Install shared QMarkdown 1.x separately before running the installer. The pinned Arch recipe is in
[packaging/qmarkdown](packaging/qmarkdown/README.md). The installer checks its library, CMake exports and QML
metadata during component configuration; QMarkdown files remain owned by the package
manager and survive umbrella uninstall. Native builds consume installed dependencies,
using `CMAKE_PREFIX_PATH` for additional prefixes. Container acceptance automatically
obtains pinned provider sources; configure and build never download packages.

The installer supports Arch Linux and Arch-derived distributions. It checks the pinned submodules, compiler, build
tools, system packages, and Greeter account without installing packages. Builds run without privilege and every
component is staged before the installer checks for collisions. Privilege is requested only when the completed stage
is copied to `/usr` and caches are refreshed. The operation does not configure greetd, enable services, or create
user configuration.

Icons require Python 3.10+ and the Arch package `hicolor-icon-theme` for the base fallback.
Papirus and Breeze are optional fallback themes; they can be installed globally or in user icon paths
such as `~/.local/share/icons/`. If neither is available, icon lookup still falls back to hicolor.
Installation generates and validates both variants,
preserves their relative aliases, and installs them into `/usr/share/icons/HoloNight` and
`/usr/share/icons/HoloNight-Dark`. The single immutable template/recoloring bundle goes into
`/usr/share/holonight-icons`. Available GTK cache tooling refreshes both themes in staging and
refreshes owned caches after deployment, recording their final hashes. Alternate-root installation
refreshes only that root's themes, never host caches.

**Naming migration:** `HoloNight` now means light. Select `HoloNight-Dark` explicitly for dark icons.

Installed menu entries include **HoloNight AI** (`holonight-chat`) and **HoloNight Packages**
(`holonight-packages`), with application SVGs in the hicolor fallback theme.

The installer also stages the HoloNight Hyprlock fallback: `/etc/xdg/hypr/hyprlock.conf`,
`/usr/libexec/holonight-hyprlock/status`, and assets in `/usr/share/holonight-hyprlock`.
Runtime requires hyprlock 0.9.6 or newer, PAM, Inter, Rajdhani, and JetBrainsMono Nerd Font;
WirePlumber's `wpctl` is optional for the volume indicator. Install these requirements separately.
An existing `~/.config/hypr/hyprlock.conf` takes precedence. Installation does not change user
configuration, install system packages, or enable services. Unmanaged system Hyprlock configuration
receives the same collision protection and explicit migration backups as other installed files.

After deployment and desktop database refresh, a real installation by a non-root user
extends an existing Viewer selection to newly supported image formats. JPEG, PNG, GIF
and WebP must all explicitly select Viewer in user MIME preferences. Supported formats
come from the installed desktop entry; explicit per-format defaults and removed Viewer
associations are preserved, including desktop-specific and legacy user preferences.
Fresh installations, mixed viewer choices, check-only runs and alternate roots leave
preferences unchanged. Direct root installation reports that it skips this extension.
User preferences remain outside payload ownership and survive uninstall.

The installer otherwise preserves existing settings. A user-local theme
can shadow the system theme; the icons repository's `task install:local` manages user-local copies
separately. The installed recoloring command targets an existing user-local theme only, even when
run from the system bundle. See the [icons documentation](holonight-icons/README.md).

Upgrades remove obsolete icons-owned files and aliases only when they match the previous manifest.
Modified files and nonempty directories containing unowned content are preserved and reported;
retained managed paths keep their original ownership hashes for later uninstall. Files from an
unmanaged legacy installation still trigger collision rejection. No blanket theme-directory removal
is performed.

To migrate existing files from an unmanaged source installation, run
`task install -- --adopt-existing`. The installer rejects package-owned files and
backs up all files being adopted under `/var/backups/holonight-source-migration.*`
before replacing any payload. The new files enter the umbrella ownership manifest,
so subsequent installs need no migration flag. Uninstall does not restore backups.

Older umbrella installations generated an untracked `icon-theme.cache`. Upgrades preserve and report
that unowned cache instead of overwriting it; theme changes invalidate its timestamp. Remove the
reported legacy cache manually before a subsequent install to enable managed cache refresh.

For unattended image/VM installation or integration testing, use `--yes` and an absolute alternate root:

```sh
task install -- --yes --root /tmp/holonight-root
task uninstall -- --yes --root /tmp/holonight-root
```

Installed paths, content hashes, and pinned source revisions are recorded in
`/var/lib/holonight/source-install/`. Uninstall removes only files that still match that record, preserves modified
files and non-empty directories, and never removes user data, administrator configuration, logs, databases,
credentials, or service state.

## Icon development and verification

Run from the umbrella root:

```sh
task icons:build       # both generated themes and the shared template bundle
task icons:validate    # source, aliases, migration inventory and generated themes
task icons:test        # Python validation, packaging and installation regressions
task icons:verify      # full verification, staged rendering, previews and licensing
task icons:preview    # family contact sheets in holonight-icons/build/previews
task test:installer   # disposable-root packaging, upgrades, ownership and removal
```

Rendering tasks explicitly use the sibling umbrella-pinned `holonight-qt` renderer, overriding an
external `HOLONIGHT_QT_SOURCE`. They need CMake, C++17 and Qt Core/Gui/Svg development packages;
full verification also requires REUSE. Builds and tests require no live installation or UI automation.
