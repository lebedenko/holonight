# Local CI Rehearsal

Status: Accepted

## Goal

Provide `task ci` in each module to rehearse every validation job triggered by a push
to main, using the same scripts, container environments and provider revisions as
GitHub CI. Start with holonightd, then adopt module by module after local acceptance.

## Non-goals

- Registry publication, releases and artifact uploads.
- Releases and changes to dependency revisions without compatibility evidence.

The user authorized publication and umbrella pin changes on 2026-10-04; see
[the publication handoff](PUBLICATION.md) for exact revisions and hosted CI evidence.

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
| `holonight-greeter` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-greeter/docs/sdd/local-ci/README.md) |
| `holonight-shell` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-shell/docs/sdd/local-ci/README.md) |
| `holonight-settings` | Repository-owned CI scripts, task and workflow parity | [Local SDD](../../../holonight-settings/docs/sdd/local-ci/README.md) |
| `holonight-viewer` | Repository-owned CI scripts, task and workflow parity | [SDD](../../../holonight-viewer/docs/sdd/local-ci/README.md) |
| `holonight-files` | Repository-owned CI scripts, task and workflow parity | [SDD](../../../holonight-files/docs/sdd/local-ci/README.md) |

## Cross-repository contracts

Each module owns its launcher and validation scripts and keeps its existing development
tasks. Current tracked edits and non-ignored new files enter disposable snapshots;
untracked inputs are reported before pushing. Every required job and matrix lane must
run with a fresh application build, immutable image identity and matching commands,
compiler options, environment and provider revisions. Failures are never skipped.
Complete logs, source state, tool versions and lane results live in ignored build/ci.
Host source is mounted read-only. Container layers may be cached.

All participating repositories and their existing validation workflows have been
inspected. Settings retains its private D-Bus, import-policy and installed-startup
checks. Viewer retains standard and sanitizer lanes plus a second installed-runtime
container without workspace mounts or networking. Files retains both locale runs,
installed-runtime fixtures and required filesystem-isolation coverage. Provider
revisions belong in each module's shared lane scripts and local SDD; correct an
incompatible published provider only with concrete API or verification evidence.

The common immutable build image and checksum-pinned supplements establish matching
environments; REUSE uses its pinned 6.2.0 environment. Disposable runner prerequisites
for required namespaces remain infrastructure setup, without modifying local host
AppArmor profiles or sysctls. This ledger records decisions and evidence; pinned
gitlinks remain authoritative integration state. All 17 module implementations have
passed local acceptance and are committed locally; TASKS.md records their evidence.
The initiative remains Accepted pending final ecosystem integration. Publication
and pin changes are authorized and recorded separately in the handoff.

## Dependency order

1. holonightd pilot, baseline 281e824bbe107dfe1a1825bd34bf1d78a98f09b8.
2. Config and Qt.
3. Images, Thumbnails, Search and System Services.
4. Icons, Hyprlock and Appearance Adapters.
5. AI, Package Manager, Greeter and Shell.
6. Settings, Viewer and Files.
7. Umbrella integration review after publication and pin updates are authorized.

## Integration acceptance criteria

- [x] Every module passes all local validation lanes and preserves specialized checks.
- [x] Every work package has a published implementation commit.
- [x] Participating submodules are clean and pinned to published commits.
- [ ] Provider revisions and contracts match at the exact pinned revisions.
- [ ] Required ecosystem integration checks pass in dependency order.
