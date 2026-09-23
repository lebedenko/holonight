# Preserve shared image outcomes

Status: Integrated

## Goal

Preserve typed raster failures through Files and Viewer presentation and retain quiet metadata status internally. Cancellation remains silent.

## Non-goals

Provider/API changes, codecs, format coverage, limits, scheduling, cache budgets/formats, logging and performance claims. Consumer publication and pinning are complete, including the qualification tooling and records authorized by the subsequent “publish and pin” request.

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
- [x] Initial clean candidate submodules pinned to published commits.
- [x] Contracts reviewed at exact pinned revisions; the Images provider remains unchanged.
- [x] Umbrella integration builds/tests pass in dependency order.
- [x] Required single-monitor native checks pass: current-build Files sharp-preview T5 and a Files/Viewer outcomes walkthrough. Physical second-monitor qualification is explicitly deferred until hardware arrives and does not block this iteration.

- [x] Publish the runner extension/records and verify clean canonical pins for the final integration checkpoint.

Automated and native acceptance passed. Published Files `05fa9f7` and Viewer
`6f9c048` are clean and canonically available; this umbrella checkpoint closes
I-003. Exact revisions and CI snapshots are recorded in [the ledger](TASKS.md).

## Current qualification iteration — 2026-09-23

The supplied single-monitor closure plan authorizes I-003 against the current published
gitlinks. Use one frozen Release lab for actual compositor scales 1/1.25/1.6/2,
20 cold/disk/memory pairs and 40 separate startup processes, plus separate visual
captures and user comparisons. Preserve prior 1.25× evidence as historical only.
All rows passed, including 72 user comparisons and the Files/Viewer walkthrough;
original 1.25× was restored. See [current acceptance](SINGLE-MONITOR.md) for commands,
evidence, retained failures and the final publication checkpoint.

Second-monitor hardware, clipboard-service acceptance, unrelated release gates and
the unknown-dimension runtime fixture remain explicit deferrals; none is reported
as passed. No public API, provider design, format or cache-policy changes are in scope.

### Approved scale amendment — 2026-09-23

The user approved **“use 1.6”**. The required current matrix is now actual
**1×, 1.25×, 1.6×, 2×**, retaining the same display mode, refresh rate, counts
and thresholds. 1.5× is unavailable at this mode and is not passed. The runner
accepts 1.6× and an explicit report matrix while preserving the historical default.
Use `native-preview.py report --output <candidate>/native --scales 1 1.25 1.6 2`.
The original frozen hash record and original runner are preserved; the separate
`scale-amendment.json` records authorization and the amended runner hash. Binary,
providers, fixtures, observer, timing calculations and capture helper are unchanged.
Focused validator tests pass 17/17, including rejection when a 1.6× matrix is
reported as the original 1.5× matrix. No application/provider rebuild is required.
