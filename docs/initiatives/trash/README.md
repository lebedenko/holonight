# HoloNight Trash

Implementation, installed-package verification and native manual acceptance are
complete. Published component revisions are pinned by the umbrella and recorded
in the integration ledger.

Files supports recoverable deletion on local filesystems and NFS. Settings can opt
into daily retention, and Files can list, restore or permanently remove top-level
Trash entries. Permanent deletion of live files remains deferred.

- [Files Trash design](../../../holonight-files/docs/sdd/trash/README.md)
- [Trash provider and retention design](../../../holonightd/docs/sdd/trash/README.md)
- [Settings Trash design](../../../holonight-settings/docs/sdd/trash/README.md)
- [Integration ledger](TASKS.md)

The Move to Trash fix can ship independently. The remaining components consume
the installed `Holonight::Trash` CMake target from holonightd. Stage holonightd
before both consumers. Install the service, timer and relative
`timers.target.wants` link through the provider's CMake manifest. The umbrella
installer then applies its ordinary collision, ownership and uninstall rules.

The shared policy is `$XDG_CONFIG_HOME/holonight/trash.toml`. Missing or invalid
configuration leaves automatic deletion disabled. The same per-root lock
serializes Files moves, restore and permanent deletion with retention. A queued
mutation revalidates the selected entry before touching the payload.

Acceptance covers isolated NFS and local Trash, retention cutoffs and mount
identity, Settings Save/Discard, Files restore and permanent deletion, and the
user timer with both apps closed. Native desktop acceptance is user-operated.
