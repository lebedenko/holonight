# Recoverable native appearance

Settings Save and Reapply express an explicit appearance choice. Session startup and
background synchronization preserve native customizations. This supersedes the
whole-labwc conflict rule in the historical live-appearance design.

## Contract and dependency order

The adapter provides protocol version 1 with additive `capabilities` and
`backup_location` metadata. `capabilities --json` advertises `replace-policy`.
`apply --policy preserve|replace` defaults to preserve. Settings first requires the
capability, then invokes replace; older adapters produce an update requirement and
Settings rolls back its staged appearance document. Publish the adapter before
Settings; no source-tree linkage or new package dependency is introduced.

[Adapter design](../../../holonight-appearance-adapters/docs/sdd/recoverable-appearance/DESIGN.md)
and [Settings design](../../../holonight-settings/docs/sdd/recoverable-appearance/DESIGN.md)
own implementation details.

## Acceptance

Focused CLI coverage exercises missing font sizes, stale ownership, edited/deleted
assets, repeated saves, independent fonts/colors, custom theme selection, override
rules, backup failure, interrupted transactions and restore/reapply. Settings tests
cover capability negotiation, replacement arguments, backups and older providers.
Run adapter package staging tests, Settings installed-provider tests and existing
session startup regressions. The isolated labwc 0.20.2 visual smoke verifies exact
and wildcard override precedence and decoration changes after reload. No ecosystem
rebuild or host deployment is needed for this change.
