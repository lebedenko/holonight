# Preserve shared image outcomes

Status: Accepted

## Goal

Preserve typed raster failures through Files and Viewer presentation and retain quiet metadata status internally. Cancellation remains silent.

## Non-goals

Provider/API changes, codecs, format coverage, limits, scheduling, cache budgets/formats, logging and performance claims. The subsequent user request authorizes consumer publication and umbrella pinning.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| holonight-files | Preview adapters and presentation | [SDD](../../../holonight-files/docs/sdd/shared-image-outcomes/SPEC.md) |
| holonight-viewer | Document adapters and presentation | [SDD](../../../holonight-viewer/docs/sdd/shared-image-outcomes/SPEC.md) |

## Cross-repository contracts

Unchanged Images Outcome contract at `3633865d2f39e4f163f0159a0f252f88245379f0`. Exact raster and metadata outcomes remain separate; no metadata failure may fail successful pixels. No outcome denotes metadata not attempted.

## Dependency order

1. Existing pinned Images contract.
2. Independent Files and Viewer adoption.
3. Publish the verified consumers and pin their revisions.
4. Later umbrella integration review and native qualification.

## Integration acceptance criteria

- [x] Consumer packages locally verified and published.
- [x] Clean submodules pinned to published commits.
- [x] Contracts reviewed at exact pinned revisions; the Images provider remains unchanged.
- [ ] Umbrella integration builds/tests pass in dependency order.
- [ ] Required native checks pass; sharp-preview T5 and mixed-monitor qualification remain open.

Automated implementation acceptance is complete. Consumers are committed and published; this umbrella checkpoint pins them. The initiative remains Accepted until umbrella integration and required native gates pass.
