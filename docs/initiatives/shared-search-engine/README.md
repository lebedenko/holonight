# Shared HoloNight search engine

Status: Accepted

## Goal

Provide a reusable, fast fuzzy search engine and use it for recursive finding in Files. The existing Files finder remains the UI prototype for this work.

## Non-goals

- Launcher, Packages, clipboard history, persistent indexing, visit-based ranking, typo correction, and fzf operators beyond unordered AND terms.
- Filesystem traversal or product policy in the shared library.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-search` | Installed Qt Core search library, relevance tests, benchmark | [Shared search engine](../../../holonight-search/docs/sdd/shared-search-engine/README.md) |
| `holonight-files` | Source traversal, hidden-path policy, finder adapter and UI acceptance | [Shared search adoption](../../../holonight-files/docs/sdd/shared-search-adoption/README.md) |

## Cross-repository contracts

- Records have source-local stable IDs, named weighted text fields, an explicit source boost, and optional source-owned type metadata.
- Search returns source and record IDs, score, and per-field UTF-16 highlight offsets. Results are capped. Query cancellation is cooperative; a cancelled search publishes no result.
- Source snapshots can be replaced, and immutable batches can be appended while a scan is active. Search sees a coherent snapshot of all batches available when it begins.
- Queries use fuzzy characters within each whitespace-delimited term, unordered AND across terms, smart case, and boundary/consecutive bonuses. A path ranking profile favors filename matches.
- Files owns directory traversal, hidden path policy, result navigation, and worker scheduling. The provider has no filesystem or UI dependencies.

## Dependency order

1. Publish and pin `holonight-search` after provider tests, installed consumer check, and representative benchmark.
2. Adopt that exact provider revision in `holonight-files`; publish Files after local checks and manual native finder acceptance.
3. Pin Files and run umbrella integration checks at published revisions.

## Integration acceptance criteria

- [x] Provider passes relevance, cancellation, snapshot, and synthetic source tests.
- [x] The same two-million-path candidate list is benchmarked against fzf in Release; Files warm-index final-keystroke to stable-result p95 is under 100 ms on the user's machine. Index size, memory, cold progress, and first-result latency are recorded separately.
- [x] Files passes focused tests, required build/checks, and the user-performed native finder check.
- [ ] Every participating repository has a published, verified commit and clean pinned gitlink.
- [ ] Contracts and integration builds pass at those exact revisions.
