# Shared UDisks2 storage support

Status: Accepted

## Goal

Share asynchronous storage discovery and safe manual operations between Shell and Files. Each application
connects independently to UDisks2 through HoloNightSystem::Storage; neither requires the other to run.

## Non-goals

Automatic mounting, unlocking encrypted storage, disk administration, network/FUSE discovery, and a HoloNight daemon.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| holonight-system-services | Storage types, models, controller and private UDisks2 backend | [SDD](../../../holonight-system-services/docs/sdd/udisks2-storage/README.md) |
| holonight-shell | Removable-device presentation and status popup | [SDD](../../../holonight-shell/docs/sdd/udisks2-storage/SPEC.md) |
| holonight-files | Devices sidebar, mount-then-open and removal recovery | [SDD](../../../holonight-files/docs/sdd/udisks2-storage/SPEC.md) |

## Cross-repository contracts

Public APIs live in HoloNight::System. Separate drive and volume models expose lifetime-scoped IDs, raw metadata,
capabilities and visibility hints. No presentation policy, translations or QML registration belongs in the provider.
Operations return request IDs and complete asynchronously with upstream errors and mount paths. Drive removal
unmounts all affected volumes, including hidden ones, and stops on failure. Power-off requires confirmation of its
current affected drive/volume scope. No forced unmount or automatic retry is permitted.

Shell shows removable drives with media (including external SSDs). Files additionally shows empty removable drives
and mounted fixed data volumes. Both exclude ignored devices, loop devices, raw containers, swap and OS infrastructure
identified by mount locations and partition purpose, never by HintSystem alone. Locked removable storage is shown
unavailable; unlocked backing devices are not duplicated. Consumers own these C++ presentation filters.

Files must invalidate pending activation on subsequent navigation; removal/unmount cancels scans and previews and
returns Home with an explanation. UI modal guards and keyboard access remain intact.

## Dependency order

1. Provider baseline: 60685b9d9f050bfba42b60191a498bd861744f37.
2. Shell baseline: cdb58290d9f39178d44c7e4e09dcf50f4329bdfa; Files baseline: 672b7193fd5523dd5d52dabe0c666044f81b9ab7.
3. Umbrella dependency checks and integration.

Provider revisions must be published and pinned before dependent consumer work starts. Publication and pinning
remain explicit handoffs under the umbrella rules; local working trees are not accepted integration revisions.

## Runtime dependencies

Install UDisks2 (`udisks2` on Arch Linux), use system D-Bus, and retain the existing polkit agent.
The umbrella installer preflight checks for the runtime package; it does not install packages or trigger authorization.

## Integration acceptance criteria

- [x] Provider fake D-Bus and injected-backend tests cover lifecycle, races and safe operations.
- [x] Storage-only install consumption needs no libpulse; existing Audio consumption passes.
- [x] Consumer filtering, actions, superseded navigation and removal recovery pass focused tests.
- [ ] Each repository passes its required acceptance checks and has a published implementation commit.
- [ ] Participating submodules are clean and pinned to published commits with compatible contracts.
- [ ] Umbrella dependency checks and builds pass in dependency order.
- [ ] Manual USB, optical, polkit and cross-application updates pass.
