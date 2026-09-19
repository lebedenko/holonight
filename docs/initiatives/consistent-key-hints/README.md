# Consistent HoloNight key hints

Status: Accepted

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Use one theme-controlled, font-scaled keyboard hint renderer throughout Shell, Viewer and Files.

## Non-goals

- Key binding changes, new fonts and icon-theme dependencies are out of scope.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-qt` | Shared semantic renderer, wrapping, typography, accessibility and gallery | [holonight-qt SDD](../../../holonight-qt/docs/sdd/consistent-key-hints/SPEC.md) |
| `holonight-shell` | Launcher, authentication and audio hints | [holonight-shell SDD](../../../holonight-shell/docs/sdd/consistent-key-hints/SPEC.md) |
| `holonight-viewer` | Footer, shortcut help and menu hints | [holonight-viewer SDD](../../../holonight-viewer/docs/sdd/consistent-key-hints/SPEC.md) |
| `holonight-files` | Quick Look and insert guidance | [holonight-files SDD](../../../holonight-files/docs/sdd/consistent-key-hints/SPEC.md) |

## Cross-repository contracts

`HnKeyHint.keyGroups` is an ordered array of arrays of `Qt.Key_*` integers. Keys are joined with `+`, alternatives with ` / `. Nonempty semantic groups take precedence over literal `text`. `wrap` defaults to false; when enabled it prefers alternative boundaries before key boundaries. One badge encloses all content. Symbol geometry and resolved-font metrics belong to the provider. Consumers supply semantic keys and action labels, never parse translated strings or override content/geometry. Accessibility exposes translated readable key names. Existing shortcuts remain authoritative.

## Dependency order

1. `holonight-qt`: implement and verify the provider, then obtain publication and pin authorization.
2. Shell, Viewer and Files: adopt the published and pinned provider and verify locally.
3. Umbrella integration review

Provider revisions must be published and pinned before dependent consumer work starts.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Required manual ecosystem checks pass.
