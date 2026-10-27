# Bluetooth core initiative

Delivery order: install the provider into a private native development prefix, then
build shell and Settings against that installed package. Preserve repository and
package-test boundaries; no additional daemon or host service changes.

- [Provider contract](../../holonight-system-services/docs/sdd/bluetooth/README.md)
- [Shell contract](../../holonight-shell/docs/sdd/bluetooth/README.md)
- [Settings contract](../../holonight-settings/docs/sdd/bluetooth/README.md)
- [Popup mockup](../../holonight-shell/docs/mockups/bluetooth-popup.png)
- [Settings mockup](../../holonight-shell/docs/mockups/bluetooth-settings.png)

The supplied plan refers to idea.md, which is absent from this checkout. The plan
and copied mockups define v1 scope. Deferred: history, reconnect policy, Find Device,
per-device bar visibility, notifications and automatic audio switching.

Runtime requires a running BlueZ service on the system bus, usable adapters and bus
policy permitting the user's operations. Missing BlueZ yields unavailable/empty
models, never an automatic host-service modification. Default-agent conflicts are
diagnostics; application-initiated pairing uses each registered agent. Blueman may
remain installed and running: discovery is shared and clients release only their
own sessions. Do not uninstall Blueman or alter host services during implementation.

Acceptance: deterministic provider tests, isolated install-consumer, native consumer
builds, QML checks and targeted integration acceptance. Live checks require headphones,
a keyboard and multiple monitors: pairing, trust/connect, reconnect, battery, rename,
forget, visibility, simultaneous scanning and Settings without shell.

## Implementation and acceptance

The provider exports Bluetooth independently. Shell owns its BluetoothService
singleton, widget and inline workflow; Settings owns its BluetoothController QML
adapter, immediate page and modal workflow. Both consume a private native install
of the provider. The provider and consumers are published in dependency order.
Shell and Settings pin the published Bluetooth provider; Settings also pins the
published shell configuration source. The umbrella gitlinks pin all three commits.

Automated acceptance covers fake-backend conflicts and partial pairing failures,
BlueZ lifetime/restart/adapter removal and snapshot reconciliation, discovery
ownership, every agent interaction, input validation, timeout/cancellation, sender
validation and agents in separate processes. Consumer checks cover selection, scan
visibility, pairing dismissal, sections, pending/error states and Settings details.
Native install-tree consumption, builds, lint, metadata, Settings imports and
offscreen page activation are checked. Container integration now resolves the
published Bluetooth revisions through the updated provider manifests; it has not
been run locally for this milestone.

Live headphone/keyboard and multi-monitor acceptance is outstanding. It requires
physical pairing input and real-device validation; automated tests use a private
D-Bus service and do not manipulate host Bluetooth or other clients.
