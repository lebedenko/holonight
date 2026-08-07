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
| `holonight-pkg-manager` | Package manager | Pinned submodule |
| `holonight-settings` | Settings application | Pinned submodule |
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
