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
| `holonight-system-services` | Shared Qt/C++ system-control integration | Pinned submodule |
| `holonightd` | HoloNight service | Pinned submodule |

## Working with the umbrella

Clone published components with:

```sh
git clone --recurse-submodules <umbrella-url>
```

For a change confined to one component, work directly in that repository. For a cross-project change, start at this
root, create an initiative under [`docs/initiatives/`](docs/initiatives/), and follow [`AGENTS.md`](AGENTS.md). The
initiative README is the stable contract; its `TASKS.md` is the restartable cross-repository ledger. Detailed
requirements and implementation tasks belong in local repository SDDs.

The workflow in [`AGENTS.md`](AGENTS.md) and the initiative templates is the operative contract.

## Installing from source

The umbrella can build every pinned production component in dependency order and install the completed result under
`/usr`:

```sh
task install -- --check
task install
```

The installer supports Arch Linux and Arch-derived distributions. It checks the pinned submodules, compiler, build
tools, system packages, and Greeter account without installing packages. Builds run without privilege and every
component is staged before the installer checks for collisions. Privilege is requested only when the completed stage
is copied to `/usr` and caches are refreshed. The operation does not configure greetd, enable services, or create
user configuration.

Icons require Python 3.10+ and the Arch packages `papirus-icon-theme`, `breeze-icons`, and
`hicolor-icon-theme` for declared fallback themes. Installation generates and validates both variants,
preserves their relative aliases, and installs them into `/usr/share/icons/HoloNight` and
`/usr/share/icons/HoloNight-Dark`. The single immutable template/recoloring bundle goes into
`/usr/share/holonight-icons`. Available GTK cache tooling refreshes both themes in staging and
refreshes owned caches after deployment, recording their final hashes. Alternate-root installation
refreshes only that root's themes, never host caches.

**Naming migration:** `HoloNight` now means light. Select `HoloNight-Dark` explicitly for dark icons.
The installer does not rewrite existing settings or change application defaults. A user-local theme
can shadow the system theme; the icons repository's `task install:local` manages user-local copies
separately. The installed recoloring command targets an existing user-local theme only, even when
run from the system bundle. See the [icons documentation](holonight-icons/README.md).

Upgrades remove obsolete icons-owned files and aliases only when they match the previous manifest.
Modified files and nonempty directories containing unowned content are preserved and reported;
retained managed paths keep their original ownership hashes for later uninstall. Files from an
unmanaged legacy installation still trigger collision rejection. No blanket theme-directory removal
is performed.

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
