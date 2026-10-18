# Reproducible VM Acceptance

Status: Draft — implementation deferred to a later session

## Goal

Make native builds, installation, graphical interaction and lifecycle verification reproducible across Hyprland,
Sway and labwc. Preserve the demonstrated historical acceptance and its qualifications in the [ledger](TASKS.md),
then replace session-specific setup with reviewable provisioning, orchestration and evidence contracts.

The supplied `hn-arch` is suitable for this work: the session inventory reports KVM, 4 vCPUs, 8 GiB RAM,
accelerated Virtio graphics, SSH and QEMU guest agent. Keep it as a development VM. The proposed acceptance
architecture is a reproducibly provisioned baseline plus a disposable clone for each run, on the existing
Arch distribution. This recommendation is future work, not authorization to reprovision the VM. The existing
VM and user configuration remain intact.

## Non-goals

- Hardware upgrades, another distribution, GPU passthrough or physical-hardware qualification.
- Hosted CI integration in the initial initiative.
- Component implementation designs before investigation establishes the relevant failure and owner.
- Provisioning, component changes, acceptance execution, publication or component pin changes in this draft.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| umbrella | Baseline provisioning, clone lifecycle, orchestration, installer integration and evidence contracts | This initiative; tooling design deferred |
| `holonight-shell` | Managed/unmanaged lifecycle verification, routing and product fixes within Shell | [Managed sessions](../../../holonight-shell/docs/sdd/managed-wayland-sessions.md); follow-up design after investigation |
| `holonight-greeter` | Cold graphical login and return-to-greeter coverage | [Boot/login reliability](../../../holonight-greeter/docs/sdd/boot-login-reliability/); follow-up design deferred |
| `xdg-desktop-portal-holonight` | FileChooser shutdown investigation and component lifecycle fixes | [FileChooser](../../../xdg-desktop-portal-holonight/docs/sdd/filechooser/README.md); follow-up design deferred |
| `holonight-appearance-adapters` | Persistent configuration apply/status/revert and reload verification | [Configuration architecture](../../../holonight-appearance-adapters/docs/sdd/configuration-architecture/README.md) |

Other components retain ownership of any product fixes uncovered by acceptance. Add a scoped handoff when evidence
identifies an owner; do not implement component behavior in the umbrella harness.

## Cross-repository contracts

- **Profiles:** a complete-desktop profile supplies declared build/runtime dependencies, compositor-specific portal
  backends, icons and optional integrations selected for that profile. A minimal-dependency profile deliberately
  omits documented optional dependencies and verifies diagnostics/degradation. Record exact package versions,
  omissions and expected outcomes; accidental missing dependencies must not silently redefine either profile.
- **Build/install:** build deployed binaries natively against guest system dependencies, in dependency order,
  consuming installed provider packages. Container binaries remain acceptance-only. Exercise the normal umbrella
  installer, including staging, manifests, ownership, collisions, upgrade and conservative uninstall. A private
  prefix is useful supplementary coverage but activation links or environment patches cannot substitute for normal
  installation acceptance.
- **Isolation:** use disposable acceptance identities and credentials, never personal credentials. Baseline and clone
  setup must be reproducible without carrying private user configuration or secrets. Cold-login cases disable
  lingering and begin without a pre-existing test user manager; explicit warm/relogin cases remain separate.
- **Evidence:** retain results outside disposable guest state before teardown. Record source revisions, package and
  VM configuration, profile, commands, timestamps, session identity, assertions, skips, workarounds, journals,
  screenshots and capture observations. Redact credentials. Track harness source; keep routine generated artifacts
  in ignored build directories or an agreed artifact store with a stable run identifier and retention policy.
- **Reporting:** distinguish observed success, harness failure, unresolved product findings and untested behavior.
  A passing request or frame callback does not establish clean shutdown or changing captured content.

Existing contracts remain authoritative: [managed sessions](../managed-wayland-sessions.md),
[session lifecycle](../session-lifecycle-reliability/README.md),
[installation completeness](../installation-completeness/README.md),
[dependency management history](../external-dependency-management/README.md) and its replacement
[CMake workflow](../cmake-workflow/README.md), and [FileChooser portal](../filechooser-portal/README.md).
This initiative coordinates their acceptance rather than duplicating their implementation specifications.

## Dependency order

1. Umbrella defines reproducible baseline/profile inputs, evidence schema and tracked orchestration.
2. Repository owners investigate and verify their work packages against that baseline; independent investigations
   may proceed together. Designs and fixes stay in the owning repositories.
3. Umbrella performs integrated acceptance with compatible, recorded revisions and normal installer paths.

Use installed providers in dependency order. Publish providers before consumer commits that reference them, and
update pins per coherent milestone, subject to separate publication authorization. This draft authorizes neither.

## Integration acceptance criteria

- [ ] Baseline provisioning and disposable clone runs can be repeated from recorded inputs for both profiles;
  evidence survives clone destruction and includes all omissions and workarounds.
- [ ] Guest-native builds and installed-package checks pass in dependency order. Normal install, upgrade, collision
  rejection and conservative uninstall preserve unmanaged files and personal configuration.
- [ ] Cold greeter login without lingering reaches each compositor; logout returns to the greeter and repeat login
  succeeds without inherited session state.
- [ ] Managed applications survive Shell restart. Shell UI logout stops applications, Shell and Polkit before the
  compositor, with journal evidence and no unexplained failed units or leftover session processes.
- [ ] Separate genuinely unmanaged-session tests verify compositor-native exit; native exit inside a managed
  session does not satisfy this requirement.
- [ ] Personal native configuration reload and installed fallback startup work on all three compositors; Appearance
  edits persist in the selected labwc directory across reload/relogin, with ownership conflicts and revert checked.
- [ ] Actual Polkit password authentication completes a privileged test action; Settings and FileChooser route to
  the expected providers, and FileChooser request/close/shutdown/relogin leave no unexplained lifecycle failures.
- [ ] Browser permission and each backend's real interactive picker are accepted without bypass. Capture assertions
  prove changing source content reaches the received video, beyond frame counts, readiness and dimensions.
- [ ] Additional resolutions, multiple virtual displays and supported integer/fractional scaling exercise picker
  targeting, placement and capture dimensions; unsupported combinations are explicitly recorded.
- [ ] Repository work packages have local verification and recorded commits; final integration records published,
  clean pinned revisions when publication is authorized, compatible contracts and proportionate integration checks.

Historical acceptance remains valid for the behaviors it demonstrated; none of these unchecked future criteria
retroactively claims broader coverage or invalidates those observations.
