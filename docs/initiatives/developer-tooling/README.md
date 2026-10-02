# Developer tooling and standalone Serena

Status: Accepted; implementation delivered locally, full acceptance blocked. See [verification](VERIFICATION.md).

This initiative extends [Ecosystem Maintainability Standardization](../ecosystem-maintainability-standardization/README.md).
The user-approved implementation plan authorizes configuration and workflow changes across all 17 components.
Broad source-warning cleanup, CI redesign, host installation, publication and umbrella pin updates are excluded.

The contract is documented in the canonical [tooling bundle](../../../tooling/README.md). Checked-in component copies
must remain independently usable. Presets, dependency sources/prefixes, compilation databases and QML tooling
must resolve without relying on an umbrella checkout or stale global HoloNight installations.

Completion requires real builds, existing acceptance checks and symbol retrieval for every configured language,
including explicit extensionless Hyprlock status-helper recognition. Verification blockers remain open in TASKS.md.
See BASELINE.json for initial revisions and Taskfile.before.yml for the preserved umbrella edit.
