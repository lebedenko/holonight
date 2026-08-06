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
| `holonight-ai` | AI desktop application | Local checkout; pending canonical publication |
| `holonight-pkg-manager` | Package manager | Local checkout; pending canonical publication |
| `holonight-settings` | Settings application | Local checkout; pending canonical publication |
| `holonightd` | HoloNight service | Local checkout; pending canonical publication |

Local-only repositories are deliberately not pinned: an umbrella integration state must never depend on an
unpublished commit. Add each one as a submodule after its canonical remote contains the revision to pin.

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
