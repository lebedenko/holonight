# Unified HoloNight portal backend

Status: Implementation published and pinned; manual acceptance and full shell acceptance pending

## Goal

Provide one standalone HoloNight portal backend for FileChooser and Settings, usable without the shell running.
This initiative documents the coordinated migration. The component implementation is published and pinned in
the umbrella; deployment remains a separate handoff. See [verification and publication](VERIFICATION.md).

## Non-goals

- AppChooser, Screenshot and Wallpaper implementation. Future interfaces use the same backend identity.
- Changes to existing FileChooser behavior or Settings values, errors and change notifications.
- Permanent compatibility aliases or automatic edits to personal portal configuration files.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `xdg-desktop-portal-holonight` | Shared registration, Settings extraction and appearance watching, activation and payload tests, documentation and repository scope instructions | [Design](../../../xdg-desktop-portal-holonight/docs/sdd/unified-backend/DESIGN.md) (UPB-001) |
| `holonight-shell` | Remove Settings publication and descriptor installation; update routing, diagnostics and regression tests | [Design](../../../holonight-shell/docs/sdd/unified-portal-backend/DESIGN.md) (UPB-002) |
| umbrella | Coordinated staging, descriptor ownership transfer, conservative cleanup, migration documentation and integration acceptance | This contract (UPB-003) |

Each component work package starts with a local SDD and links it from this contract and the
[coordination ledger](TASKS.md). Local implementation checklists remain in their owning repositories.

## Cross-repository contracts

Use backend identifier `holonight`, descriptor `holonight.portal`, and D-Bus name
`org.freedesktop.impl.portal.desktop.holonight`. Keep executable `xdg-desktop-portal-holonight` and object path
`/org/freedesktop/portal/desktop`. The portal repository owns the descriptor and activation service; the shell
must no longer register a competing service or install the descriptor.

Move Settings from the shell into this backend alongside FileChooser. Consume the installed
`Holonight::AppearanceReader` for appearance reads and watching, independently of the shell; do not copy provider
sources. Preserve Settings values, errors and change notifications, including retention of the last valid
appearance after invalid configuration and suppression of notifications for unchanged effective values.
Preserve FileChooser cancellation, concurrency, native Linux path bytes and save behavior.

Advertise only implemented interfaces: FileChooser and Settings for this migration. Ship routing entries
`FileChooser=holonight;gtk` and `Settings=holonight;gtk`, preserving compositor-specific defaults for other
interfaces. Retire `holonight-filechooser` without a permanent alias, including its old descriptor
`holonight-filechooser.portal` and bus name `org.freedesktop.impl.portal.desktop.holonight_filechooser`.

The umbrella installer coordinates descriptor ownership transfer and obsolete-file cleanup. Preserve modified
or unmanaged files, reject collisions, and retain conservative uninstall behavior. Document how users replace
`holonight-filechooser` with `holonight` in personal portal configuration files; never edit them automatically.

## Context and supersession

The [FileChooser portal initiative](../filechooser-portal/README.md) records the original separate FileChooser
identity and shell-owned Settings service. The [configuration architecture initiative](../configuration-architecture/README.md)
records installed appearance readers, shell-independent infrastructure and configuration update semantics.
This initiative supersedes their separate portal identity decision only. Retain historical records and all
outstanding acceptance; this migration does not close those checks or reopen unrelated configuration decisions.

## Dependency order

1. UPB-001 and UPB-002 establish local SDDs against this shared contract. Backend and shell implementation may
   proceed together, consuming installed providers.
2. Publish providers before consumer commits that reference them.
3. UPB-003 stages and deploys compatible backend and shell revisions together, including descriptor ownership
   transfer and routing. Update umbrella pins only for a coherent milestone.
4. Record component and ecosystem acceptance before marking the initiative Integrated.

## Integration acceptance criteria

- [ ] One installed HoloNight descriptor and activation service are owned by the portal repository, with no competing shell registration.
- [ ] Both interfaces activate and work through the real broker without the shell running.
- [ ] Settings appearance updates propagate through the broker; invalid configuration retains valid values and unchanged values emit no redundant notifications.
- [ ] Existing FileChooser cancellation, concurrency, native-path and save behavior remains covered.
- [ ] Upgrade tests cover ownership transfer, obsolete-file cleanup, preservation of modified/unmanaged files, collision rejection and conservative uninstall.
- [ ] Routing uses the unified identifier with GTK fallback and preserves compositor-specific defaults; personal configuration migration is documented.
- [ ] Focused component tests precede clean acceptance and installation/runtime checks at compatible revisions.
- [ ] Required native desktop acceptance is performed manually; never automate pointer or focus interaction.
- [ ] Participating revisions are published, clean and coherently pinned, with dated integration evidence recorded in UPB-003.

## Personal routing migration

Review personal and administrator overrides under
`$XDG_CONFIG_HOME/xdg-desktop-portal` (normally `~/.config/xdg-desktop-portal`)
and `/etc/xdg/xdg-desktop-portal`. Desktop-specific files and `portals.conf` can
supersede shipped routing. Manually replace `holonight-filechooser` with
`holonight`, and select both interfaces explicitly:

```ini
[preferred]
org.freedesktop.impl.portal.FileChooser=holonight;gtk
org.freedesktop.impl.portal.Settings=holonight;gtk
```

Preserve other interface defaults for the compositor. Install compatible backend
and shell payloads together after the publication/pinning handoff, then restart
the session or portal services at a convenient time. Starting the shell does not
repair a missing standalone backend. Personal configuration is never edited by
the installer or this migration.

## Preserved-file remediation

Before any destination copies, staging rejects duplicate component owners,
missing unified executable/service/descriptor, legacy payloads and incompatible
interfaces. An existing `holonight.portal` transfers from shell ownership only
when its contents match the old recorded hash. Modified or unmanaged descriptors
stop the upgrade even with `--adopt-existing`: back up and compare the file,
then move the conflicting copy aside manually before retrying.

The installer removes only unchanged backend-owned
`holonight-filechooser.portal` and
`org.freedesktop.impl.portal.desktop.holonight_filechooser.service` absent from
the new payload. Modified legacy files and paths beneath symlinked parents are
preserved and reported; their original ownership hashes survive repeated upgrades
so later cleanup and uninstall remain conservative. Unmanaged legacy files are
never adopted by cleanup. Review preserved files and move retired descriptors or
activation files outside their search directories manually if they are no longer
needed. Resolve symlinked installation parents manually before retrying a blocked
installation. Do not replace recorded hashes with hashes of modified files.
