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

The original [`umbrella-project-idea.md`](umbrella-project-idea.md) is retained as design background. The workflow in
`AGENTS.md` and the initiative templates are the operative contract.

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

For unattended image/VM installation or integration testing, use `--yes` and an absolute alternate root:

```sh
task install -- --yes --root /tmp/holonight-root
task uninstall -- --yes --root /tmp/holonight-root
```

Installed paths, content hashes, and pinned source revisions are recorded in
`/var/lib/holonight/source-install/`. Uninstall removes only files that still match that record, preserves modified
files and non-empty directories, and never removes user data, administrator configuration, logs, databases,
credentials, or service state.
