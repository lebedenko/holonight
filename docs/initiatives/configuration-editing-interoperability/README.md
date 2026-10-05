# Manual configuration editing and Settings interoperability

Status: Abandoned

Replaced by [configuration architecture](../configuration-architecture/README.md). All work packages are superseded.
The proposed Files search-exclusion page in Settings is explicitly cancelled; Files owns its settings UI.

## Goal

Make manual text editing and Settings UI controls two editors of one canonical configuration file per domain.
This initiative does not block Files search exclusions; their Settings page is deferred here.

## Non-goals

- Choosing a comment/format-preserving editor before the unresolved preservation decision is settled.
- Mixing user preferences with runtime state or disposable caches.
- Accepting implementation packages before discovery and shared contracts are resolved.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-settings` | Settings UI, appearance conflict/revision/rollback precedent and domain editing interoperability | Pending discovery |
| `holonight-files` | Search-exclusion Settings controls and canonical Files config | Pending discovery |
| `holonight-qt` | Appearance consumer and Qt validation contract | Pending discovery |
| `holonight-config` | Existing neutral appearance schema and atomic writing precedent | Pending discovery |
| Other domain owners | Identify canonical files and existing editors during discovery | Unresolved |

## Cross-repository contracts

One canonical configuration file per domain; manual edits and UI controls update that same file.
Preferences, runtime state and caches have separate storage lifecycles, following the
[XDG specification](https://specifications.freedesktop.org/basedir/0.8/).
Merge unrelated changes from manual/UI editors. Concurrent changes to the same key require explicit resolution;
initially treat a whole list as one value. Start from existing appearance conflict detection and atomic writing,
then review save behavior, revision checks, and rollback across domain owners. Initial discovery points to
`holonight-settings/apps/settings/src/AppearanceFileService.cpp` for revision/conflict/stage/commit/rollback,
`holonight-config` for `writeAtomically`, and `holonight-qt` for appearance resolution. These are starting points,
not an accepted general-purpose editing contract.

**Unresolved: comment and formatting preservation.** Settle this when the initiative begins, before choosing
an editing implementation or accepting work packages. No preservation behavior is implied by this draft.

[VS Code](https://code.visualstudio.com/docs/configure/settings) provides a precedent for text and UI settings
editors over the same settings file. [fd](https://github.com/sharkdp/fd#excluding-files-or-directories) provides
precedent for global user exclusions; Files' exclusion semantics remain its own documented contract.

## Dependency order

1. Inventory domain files and existing appearance save/revision/rollback behavior.
2. Settle preservation and merge/conflict contracts, exact baselines and participating owners.
3. Accept repository packages, including the deferred Files search Settings page.
4. Umbrella integration review at published pins.

## Integration acceptance criteria

- [ ] Preservation decision and cross-domain editing contracts are settled.
- [ ] Concurrent unrelated edits merge; same-key/list conflicts require explicit resolution.
- [ ] Save, revision-check, atomic-write and rollback scenarios are verified.
- [ ] Every repository package passes local verification and is published.
- [ ] Submodules are clean at compatible published pins; dependency-order integration and manual checks pass.
