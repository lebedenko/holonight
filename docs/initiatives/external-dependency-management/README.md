# Unified external dependency management

Status: Accepted

## Goal

Standardize all 18 standalone repositories on installed external dependencies, explicit local source preparation
and locked CI environments. CMake, normal builds and the umbrella installer must never acquire dependencies.
Prioritize a lightweight qualified Arch environment for pre-release development, deployment and CI.
Debian qualification is deferred; retain portable discovery and Debian package mappings without claiming support.

## Non-goals

- Application behavior refactoring, new dependency-management frameworks, Conan or vcpkg.
- Automatic privileged package installation, implicit source downloads or unmanaged external runtime deployment.

## Audited baseline and inventory

Umbrella revision: `38146d8f474317f3f8d72699f60e6d16a71dd165`. [BASELINE.json](BASELINE.json) records all 18 exact gitlinks and initial
working-tree state. Gitlinks remain authoritative; this is an audit snapshot. The pre-existing uncommitted installer
QMarkdown fetch/staging changes are replaced in the umbrella work package.

[CI-PACKAGE-AUDIT.json](CI-PACKAGE-AUDIT.json) retains all 250 historical supplement entries, including versions,
checksums and URLs (103 distinct names). Direct profile requirements are classified separately from package-manager
resolved transitive dependencies; neither class is discarded from the audit. [Canonical declarations](../../../tooling/modules)
record per-consumer direct build/test/tool/runtime requirements and controlling features. Local SDDs retain detailed
implementation and verification tasks; see the [ledger](TASKS.md) for all 18 links.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| holonight-ai | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-ai/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-appearance-adapters | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-appearance-adapters/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-config | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-config/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-files | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-files/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-greeter | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-greeter/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-hyprlock | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-hyprlock/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-icons | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-icons/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-images | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-images/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-pkg-manager | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-pkg-manager/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-qt | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-qt/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-search | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-search/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-settings | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-settings/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-shell | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-shell/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-system-services | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-system-services/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-thumbnails | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-thumbnails/docs/sdd/external-dependency-management/SPEC.md) |
| holonight-viewer | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonight-viewer/docs/sdd/external-dependency-management/SPEC.md) |
| holonightd | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../holonightd/docs/sdd/external-dependency-management/SPEC.md) |
| xdg-desktop-portal-holonight | Standalone declarations, discovery, workflows and CI adoption | [SPEC](../../../xdg-desktop-portal-holonight/docs/sdd/external-dependency-management/SPEC.md) |

See [INVENTORY.md](INVENTORY.md) for direct requirements and [CMAKE-AUDIT.json](CMAKE-AUDIT.json) for current discovery.

## Cross-repository contracts

- Bundle 2.0.0 extends module.json with stable external IDs, discovery names/mechanisms, existing versions,
  components/targets, scopes and controlling features; Arch/Debian mappings ship with standalone copies.
- Installed GTest >=1.14 CONFIG is required for tests; consumers using GMock require its exported targets.
- Production Qt >=6.11 is required; private components must match the selected public Qt version exactly.
- Retain stronger versions: Files toml++ >=3.4, polkit-qt6 >=0.200.0 and installed shared QMarkdown 1.x.
- Keep pkg-config where it is the existing library interface; holonightd uses installed nlohmann_json and toml++
  imported targets. Enabled systemd, KConfig and syntax-theme features require their packages.
- `task deps` alone prepares supplied local sources. `task configure`/build/test validate installed prerequisites.
  HOLONIGHT_DEPENDENCY_PREFIX restricts internal providers; HOLONIGHT_EXTERNAL_PREFIX adds installed external
  discovery without allowing external/global packages to satisfy internal requirements.
- Compatibility evidence includes source content/revision, compiler/toolchain, Qt, build type/options/features,
  selected paths and versions. Incompatible caches/install trees are preserved for inspection and never reused.
- QMarkdown is a separately owned system package. Its accepted source revision is
  `b71740c7e0f26b0709f5e929a79e8d01dba56071` (version 1.1.0); the installer preflights it and never owns/removes its payload.
- The production installer profile is generated from declarations; test dependencies remain excluded.
- CI images use pinned bases, dated package repositories and package-manager resolution. Build/runtime images
  use compatible Qt/toolchains. Acquire packages/providers explicitly before offline configuration/acceptance.
- Qualified immutable Arch image digests and published tooling/provider handoffs precede repository adoption
  (EDM-024). Debian qualification (EDM-023) is Superseded for this pre-release initiative.
- EDM-012 includes moving Shell’s release build gate to the qualified Arch environment while preserving tests,
  linting and quality checks. No application workflows change in the environment handoff.
- Publication and umbrella pin updates are separate authorized handoffs. No unpublished commit is pinned.

## Dependency order

1. Umbrella canonical tooling, system QMarkdown recipe and qualified CI environments.
2. Config and System Services, then Qt; independent Images, Thumbnails and Search providers.
3. Appearance Adapters/Icons, then Shell and its configuration export; Settings follows Shell.
4. Viewer and Files; portal follows Files; AI, Package Manager and Greeter follow Qt/providers.
5. Daemon and Hyprlock independent adoption; final umbrella integration at published exact revisions.

Only Ready work packages may be assigned. Preserve one repository and its exact recorded upstream baseline per
implementation handoff. Repository-local commits do not alter umbrella pins or integration status.

## Integration acceptance criteria

- [ ] Every repository adoption has a verified local commit published to its canonical remote.
- [ ] Every participating submodule is clean and pinned to the published implementation revision.
- [ ] Declarations, CMake, CI profiles and installer requirements agree; all historical audit entries are retained.
- [ ] Missing dependencies, explicit/system prefixes, spaces, conflicts, incompatible versions and stale caches are tested.
- [ ] holonightd builds without vendored headers; systemd ON/OFF and parsing/serialization/notification tests pass.
- [ ] QMarkdown package contents and Files startup pass; umbrella uninstall preserves package ownership.
- [ ] Qualified full Qt and minimal daemon environments retain image/package/source/feature evidence and offline acceptance.
- [ ] Shell’s release build gate uses the qualified Arch environment with tests, linting and quality checks preserved.
- [ ] Clean repository acceptance passes in dependency order, then umbrella staging/install/uninstall checks pass.
- [ ] Manual session, greeter, portal and compositor checks pass without pointer/focus automation.

Acceptance of these contracts does not imply implementation or environment qualification. Current evidence and
outstanding handoffs are recorded in TASKS.md; the initiative remains Accepted until final integration passes.
