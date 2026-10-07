# Configuration architecture improvement

Status: Integrated

## Goal

Make Appearance and Shell configuration safely editable through text and Settings while preserving application ownership.
Replaces [configuration editing interoperability](../configuration-editing-interoperability/README.md).

## Non-goals

- Other application migrations/settings surfaces, including a Files page in Settings (cancelled).
- AI JSON conversion, CLI tooling, additional layers, a daemon or new parser dependencies.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-config` | Neutral documents, schemas, preserving edits, locked storage and appearance v2 | [holonight-config SDD](../../../holonight-config/docs/sdd/configuration-architecture/README.md) |
| `holonight-qt` | Reusable Qt watching and appearance reads | [holonight-qt SDD](../../../holonight-qt/docs/sdd/configuration-architecture/README.md) |
| `holonight-shell` | Shell-owned schema and validated sparse reads | [holonight-shell SDD](../../../holonight-shell/docs/sdd/configuration-architecture/README.md) |
| `holonight-appearance-adapters` | v1/v2 compatibility and isolated application | [holonight-appearance-adapters SDD](../../../holonight-appearance-adapters/docs/sdd/configuration-architecture/README.md) |
| `holonight-settings` | Pending edits, per-value conflicts, resets and guarded rollback | [holonight-settings SDD](../../../holonight-settings/docs/sdd/configuration-architecture/README.md) |
| `holonight-viewer` | Standalone acceptance fixture corrections only; configuration adoption remains deferred | [Viewer verification SDD](../../../holonight-viewer/docs/sdd/configuration-architecture-verification/README.md) |

## Cross-repository contracts

Each application owns its configuration schema, file, settings UI and behavior. Global appearance is shared;
application preferences are separate. Files and Viewer must remain usable without Shell or Settings. AI and Packages
retain their own configuration. Infrastructure requires neither Shell, Settings nor a running daemon.

Snapshots retain original bytes, parsed typed values, override presence, source spans and content revisions.
Paths are vectors of key segments, including quoted keys containing dots. Schemas declare typed defaults,
constraints, descriptions and reload policy, with domain validators for related values and dynamic collections.
Edit batches carry set/remove operations and baseline values/presence. Save outcomes distinguish success,
per-key conflicts, invalid documents/edits, unsupported patches, pre-replacement storage failures and
post-replacement durability failures.

Use toml++ and a TOML-aware lexical editor; never serialize an existing document wholesale or substitute by regex.
Preserve unrelated bytes, comments, ordering, whitespace and unknown fields. Reset removes an assignment and retains
comments/sections. Arrays and arrays of tables are whole conflict values. Unsupported safe patches fail unchanged.
Reparse and validate every candidate. Establish preservation fixtures before consumer adoption.

Merge baseline, pending and current values: unrelated edits merge, identical edits converge, different changes to the
same value conflict. Lock a stable sibling file for cooperating writers; read/patch under the lock and recheck the
revision immediately before replacement. Arbitrary editors do not participate in the lock: a race remains between
the final check and rename. Follow existing symlinks, abort on retargeting, preserve existing permissions, create new
files as 0600, sync a same-directory temporary file, rename, and sync the directory.

Appearance v2 uses sparse defaults, rejects invalid known fields and warns about preserved unknown fields. Retain the
v1 decoder and explicit v1 serialization APIs. Document version is metadata, separate from the effective appearance
model. First successful Settings save upgrades valid v1 by changing only version and requested values. New editing
documents use v2; unsupported versions are read-only. Enable GUI v2 writes only after readers/adapters pass compatibility.

Shell owns defaults/validation in its exported configuration package. Preserve paths and meanings. Reads never create
files or write defaults. Missing overrides use defaults; reset removes the override. Reject invalid known values.

Settings retains Save/Discard, tracks baseline/pending edits, refreshes untouched controls on external changes and
retains pending edits. Expose baseline/disk/pending values and per-value keep-pending/accept-external resolution;
recheck on save. Show default/override status and diagnostics. Discard loads latest disk. Invalid external documents
block saves and running consumers retain last valid values; startup errors use defaults with diagnostics. Missing
files use defaults without writes. Watch files and nearest existing parents through replacement/deletion/recreation;
publish only differing effective values. Domain saves have independent outcomes. Rollback is conditional on the staged
revision still being current; concurrent changes survive and must not be reported successfully applied.

## Dependency order

1. Config provider.
2. Qt reader/watcher.
3. Shell schema.
4. Appearance adapters compatibility.
5. Settings adoption after all readers pass.
6. Standalone consumer acceptance (including CA-006a Viewer fixture corrections).
7. Umbrella integration.

Providers must be published and pinned before dependent work begins. Each package owns one repository.

## Integration acceptance criteria

- [x] Preservation fixtures cover comments, unknown fields, quoted/dotted keys, inline tables, multiline strings, Unicode, CRLF, arrays/AoT, insertion/reset and rejected patches.
- [x] Merge, convergence, conflicts/reset, cooperating locks and revision-change aborts pass.
- [x] Unreadable files, permissions, interrupted writes, replacement failures, symlink retargeting and durability outcomes pass.
- [x] v1 behavior remains compatible; sparse v2/reset and surgical first-save upgrades pass; unsupported versions cannot be overwritten.
- [x] Runtime invalid/startup/missing/delete/recreate and unchanged-signal scenarios pass.
- [x] Settings Save/Discard, external updates, per-value resolution, partial saves and adapter/rollback concurrency pass.
- [x] Each repository passes required clean acceptance and installed-package checks at accepted provider revisions.
- [x] Files and Viewer pass standalone checks without Shell or Settings installed.
- [x] Every participating submodule is clean and pinned to a canonical published implementation commit.
- [x] Dependency-order integration and user-operated concurrent-edit/appearance checks are recorded with dates and revisions.

Staged saves must additionally return the exact pre-write snapshot captured under the advisory lock. This is the
rollback baseline: a pre-lock read can precede unrelated edits merged during saving. CA-001a adds this additive
contract and corrects appearance storage-error classification before Settings adoption.

Automated and user-operated integration evidence: [verification record](VERIFICATION.md).
