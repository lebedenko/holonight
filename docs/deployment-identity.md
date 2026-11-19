# Verified deployment and package-manager build identity

The umbrella already coordinates native builds, staging, ownership manifests and
systemd daemon-reload. This addition makes final verification and runtime staleness
visible. It does not replace the conservative deployment model with a second
installer or introduce automatic service restarts.

## Contracts

- REQ-F-001: When deployment finishes its refresh hooks, the installer shall verify selected installed ordinary files and links against their recorded inventories before declaring completion.
- REQ-F-002: If installed content differs, then the installer shall retain a pending transaction and report the conflicting path.
- REQ-F-003: When package-manager installation targets the host, the installer shall verify systemd's helper executable path.
- REQ-F-004: If a running helper uses a previous executable inode, then the installer shall report it without stopping the process.
- REQ-F-005: When saved payloads are resumed, the installer shall explain that checkout changes are not rebuilt and print prepared revisions.

The component exposes its build identity through `--build-info` and the helper's
additive D-Bus `BuildId` property. `holonight-packages --diagnostics` compares local
and running helper identities without activating a service. Its local design is
[deployment identity](../holonight-pkg-manager/docs/sdd/deployment-identity/SPEC.md).
The installer verifies bytes and effective activation independently of application
identity; it never executes staged application payloads as root for verification.

## Delivery and verification

The component identity change may ship independently; the installer has no new
D-Bus dependency. Publish component changes before updating the umbrella pin.
No automatic pin updates or publishing are part of this work.

Use disposable-root installer tests for correct/altered files, wrong activation,
inactive helper, stale running inode and host isolation. Component checks cover
build provenance and the D-Bus property. Existing ownership, collision and resume
tests remain mandatory. Container builds remain acceptance only; deployed code
continues to be built against host dependencies.
