# Local CI Rehearsal

Status: Draft

## Goal

Provide `task ci` in each module to rehearse every validation job triggered by a push
to main, using the same scripts, container environments and provider revisions as
GitHub CI. Start with holonightd, then adopt module by module after local acceptance.

## Non-goals

- Registry publication, releases and artifact uploads.
- Pushes and umbrella submodule-pin changes in this session.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonightd` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonightd/docs/sdd/local-ci/README.md) |
| `holonight-config` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-config/docs/sdd/local-ci/README.md) |
| `holonight-qt` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-qt/docs/sdd/local-ci/README.md) |
| `holonight-images` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-images/docs/sdd/local-ci/README.md) |
| `holonight-thumbnails` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-thumbnails/docs/sdd/local-ci/README.md) |
| `holonight-search` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-search/docs/sdd/local-ci/README.md) |
| `holonight-system-services` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-system-services/docs/sdd/local-ci/README.md) |
| `holonight-icons` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-icons/docs/sdd/local-ci/README.md) |
| `holonight-hyprlock` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-hyprlock/docs/sdd/local-ci/README.md) |
| `holonight-appearance-adapters` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-appearance-adapters/docs/sdd/local-ci/README.md) |
| `holonight-ai` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-ai/docs/sdd/local-ci/README.md) |
| `holonight-pkg-manager` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-pkg-manager/docs/sdd/local-ci/README.md) |
| `holonight-greeter` | Repository-owned CI scripts, task and workflow parity | Pending |
| `holonight-shell` | Repository-owned CI scripts, task and workflow parity | Pending |
| `holonight-settings` | Repository-owned CI scripts, task and workflow parity | Pending |
| `holonight-viewer` | Repository-owned CI scripts, task and workflow parity | Pending |
| `holonight-files` | Repository-owned CI scripts, task and workflow parity | Pending |

## Cross-repository contracts

Each module owns its launcher and validation scripts and keeps its existing development
tasks. Current tracked edits and non-ignored new files enter disposable snapshots;
untracked inputs are reported before pushing. Every required job and matrix lane must
run with a fresh application build, immutable image identity and matching commands,
compiler options, environment and provider revisions. Failures are never skipped.
Complete logs, source state, tool versions and lane results live in ignored build/ci.
Host source is mounted read-only. Container layers may be cached.

The holonightd pilot has no provider dependency. Remaining contracts and specialized
acceptance lanes must be inspected before accepting the full initiative. This ledger
records decisions and evidence; pinned gitlinks remain authoritative integration state.

## Dependency order

1. holonightd pilot, baseline 281e824bbe107dfe1a1825bd34bf1d78a98f09b8.
2. Config and Qt.
3. Images, Thumbnails, Search and System Services.
4. Icons, Hyprlock and Appearance Adapters.
5. AI, Package Manager, Greeter and Shell.
6. Settings, Viewer and Files.
7. Umbrella integration review after publication and pin updates are authorized.

## Integration acceptance criteria

- [ ] Every module passes all local validation lanes and preserves specialized checks.
- [ ] Every work package has a published implementation commit.
- [ ] Participating submodules are clean and pinned to published commits.
- [ ] Provider revisions and contracts match at the exact pinned revisions.
- [ ] Required ecosystem integration checks pass in dependency order.
