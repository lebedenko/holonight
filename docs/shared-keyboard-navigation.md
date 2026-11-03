# Shared keyboard navigation

The configuration contract lives in [holonight-config](../holonight-config/docs/input.md).
The interaction provider design lives in [holonight-qt](../holonight-qt/docs/navigation.md).
Files, the standalone portal chooser and Bluetooth retain application action policy.
Neither the input reader nor navigation requires Shell. Launcher, network and audio
adoption, modal text editing and remapping are outside this milestone.

Build/install Config into an isolated native prefix, then Qt, then the browsing provider
and consumers against installed packages. Do not embed provider source in consumers.
Keep installation ownership and conservative uninstall unchanged. Keep deployment and publication separate from local implementation commits.
The umbrella records the coordinated provider and consumer revisions.

Verification starts with parser/interpreter/controller tests, then consumer routing and
installed-package probes. Native acceptance covers focus, keyboard reachability, row
controls, chooser layout and scaling; it must be performed manually under the Files
and portal repository instructions. General chooser visual polish, server-side rendering and metadata corrections are deferred
by user direction; focus visibility remains part of navigation.

Consumer designs: [Files](../holonight-files/docs/sdd/shared-navigation.md),
[browsing provider](../holonight-file-browser/docs/sdd/shared-navigation.md),
[chooser](../xdg-desktop-portal-holonight/docs/sdd/shared-navigation.md), and
[Bluetooth](../holonight-shell/docs/sdd/shared-navigation.md).

## Shared Settings preference

Config owns `[input].navigation` in `holonight/config.toml`; Shell owns its existing
sections. Settings composes the two schemas into one document edit session, so a
single save patches both kinds of edits with the same revision/conflict handling.
Appearance remains separate. Qt consumers use the Config decoder independently of
Shell and retain their semantic navigation API. See the [input contract](../holonight-config/docs/input.md)
and [Settings design](../holonight-settings/docs/sdd/shared-navigation.md).

The prior input.toml contract is replaced before release; manual migration is
documented and no legacy file is removed. Provider order remains Config, Qt, consumers.
