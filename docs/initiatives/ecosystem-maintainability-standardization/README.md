# Ecosystem Maintainability Standardization

Status: Integrated

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Give every HoloNight repository a consistent, capability-based maintenance contract and provide one safe umbrella
interface for building and installing the exact pinned ecosystem from source.

## Non-goals

- Implement every repository backlog item in this coordination pass.
- Install packages, enable services, replace `/etc/greetd/config.toml`, or manage user configuration.
- Make per-user installation universal; only asset repositories with a useful user-scoped contract retain it.
- Duplicate the Shared CI Build Infrastructure initiative.

## Universal baseline

Every repository must document target ownership and dependency direction, use CMake install metadata that supports
`DESTDIR` staging with `/usr` as the configured prefix, expose only applicable Task capabilities, and keep CI checks
reproducible locally. Production targets use the repository's declared C++ standard, warnings and static analysis are
actionable, tests validate observable behavior, and release/install documentation names all system integration side
effects. Generated files, credentials, user state, and package-manager operations stay outside source installation.

Application-owned QML belongs under `apps/<app>/qml`, grouped by feature. Each product exposes one product module URI,
assigns stable resource aliases, and uses relative imports only within a tightly coupled feature. Applications consume
`Holonight`, `Holonight.Core`, and `Holonight.Controls` according to their published roles; duplicated local controls,
raw controls that bypass the design system, inconsistent imports or aliases, and missing qmltypes/qmllint checks are
tracked in the repository backlog.

## Repository profiles

| Profile | Additional standard |
|---|---|
| Qt application | One executable-owned QML module; feature directories; qmllint and qmltypes metadata checks; desktop/D-Bus/systemd metadata installed explicitly. |
| Shared library | Exported namespaced CMake package, install-tree consumer test, public-header compatibility, and no application policy. |
| Non-Qt daemon | No Qt dependency; explicit service/config sample paths; unit lifecycle remains administrator-controlled. |
| Adapter | Mutation boundaries and toolkit dependencies are explicit; probes remain test-only; production adapter installs independently. |
| Asset repository | Deterministic asset validation and owned-path install/uninstall pairing; no recursive deletion of user data. |

## Installation contract

The root `task install` configures Release builds with prefix `/usr`, stages providers before consumers, and makes the
completed staged prefix discoverable through `CMAKE_PREFIX_PATH`. It performs distribution, dependency, compiler,
account, checkout, and collision checks; it never invokes pacman. Only after every component installs into the stage
does it copy files, refresh caches, reload systemd metadata, and apply the Greeter tmpfiles definition without
enabling or starting anything. The source-install manifest records module revisions and hashes. Root uninstall walks
that manifest in reverse, removes only unmodified files and empty recorded directories, and reports modifications.

Repository-local per-user installs are omitted unless they are genuinely useful. `holonight-icons` retains
`install:local` and must gain a matching owned-file `uninstall:local`; system-integrated applications, Shell/session
services, Greeter, and daemons must remove misleading local-install commands. Modules do not add
`uninstall:system`; umbrella removal owns the coordinated system transaction. Development uses temporary staged
prefixes rather than globally installed builds.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-config` | Shared configuration package | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-config/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonight-qt` | Qt/QML design system and exported packages | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-qt/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonight-appearance-adapters` | Appearance adapter and toolkit probes | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-appearance-adapters/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonight-icons` | Icon assets and local asset lifecycle | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-icons/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonight-shell` | Shell UI and system/session integration | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-shell/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonight-settings` | Settings UI and product configuration | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-settings/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonight-ai` | Chat application | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-ai/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonight-pkg-manager` | Package-manager application (pinned unpublished commit) | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-pkg-manager/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonight-greeter` | Greeter UI and greetd integration assets | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonight-greeter/docs/sdd/ecosystem-maintainability-standardization/README.md) |
| `holonightd` | Non-Qt daemons and system units | [`docs/sdd/ecosystem-maintainability-standardization/`](../../../holonightd/docs/sdd/ecosystem-maintainability-standardization/README.md) |

## Dependency order

1. `holonight-config`
2. `holonight-qt`
3. `holonight-appearance-adapters` and `holonight-icons`
4. `holonight-shell`, `holonight-settings`, `holonight-ai`, `holonight-pkg-manager`, and `holonight-greeter`
5. `holonightd`
6. Umbrella integration review

## Integration acceptance criteria

- [x] Every repository work package has a published commit and passed local verification.
- [x] Participating submodules are pinned to published commits; pre-existing untracked user documents remain excluded.
- [x] Exported CMake packages and QML modules resolve from one temporary staged prefix.
- [x] Root install/uninstall integration checks cover collision rejection, upgrade ownership, hashes, symlinks, permissions, and modified-file preservation.
- [x] Real Arch installation validates binaries, QML modules, desktop/D-Bus metadata, units, caches, and Greeter assets.
- [x] The final umbrella integration row records commands, results, and verification date.
