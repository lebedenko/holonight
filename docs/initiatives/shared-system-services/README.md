# Shared System Services

Status: Accepted

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Provide reusable Qt/C++ system-control components that let HoloNight applications share integration logic while
remaining independent clients of PulseAudio/PipeWire, NetworkManager, and BlueZ.

## Non-goals

- Introduce a HoloNight daemon or repurpose `holonightd`.
- Provide ABI-stable shared libraries in the initial release.
- Define the detailed Settings Audio-page filtering, validation, or presentation policy.
- Migrate the Audio backend from libpulse to native PipeWire.
- Implement Network or Bluetooth before the Audio provider and consumers are integrated.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-system-services` | Reusable Audio, Network, and Bluetooth components | `docs/sdd/shared-system-services/` |
| `holonight-shell` | Adopt shared components while preserving Shell QML contracts | `docs/sdd/shared-system-services-adoption/` |
| `holonight-settings` | Instantiate shared components and own Settings-specific UI policy | `docs/sdd/shared-system-services-adoption/` |
| umbrella | Initiative coordination, ownership, and gitlink integration | This initiative |

## Cross-repository contracts

- The package name is `HoloNightSystemServices`; public targets are independently linkable static components
  `HoloNightSystem::Audio`, `HoloNightSystem::Network`, and `HoloNightSystem::Bluetooth`.
- Public C++ APIs use the `HoloNight::System` namespace and domain-specific controllers, value types, and models.
- Backend interfaces are constructor-injected. Concrete backends are implementation details.
- Shared classes do not register QML types or contain translations, navigation, dialog policy, or consumer-specific
  display formatting.
- Each consumer owns controller lifetime and local QML registration. Shell exposes `AudioController` locally as
  `AudioService` to preserve its existing QML API.
- Clients connect independently to upstream services and converge through upstream events. Settings must not depend
  on Shell availability.
- Audio retains libpulse until a separately accepted backend migration.
- Network keeps Shell's `openNetworkSettings()` and display strings outside the provider.
- Settings owns interactive Bluetooth pairing; Shell initially observes state and connects known devices.

Published implementation baselines:

- `holonight-shell`: `2e63d8edfbe1e332266997b41ff80765588d01eb`
- `holonight-settings`: `b480b860424eaf77f5b76f67a9e79f518cdc21f7`

## Dependency order

1. `holonight-system-services`: package foundation and Audio component.
2. `holonight-shell`: Audio adoption without QML behavior changes.
3. `holonight-settings`: Audio adoption and Settings-owned presentation.
4. `holonight-system-services` and consumers: Network component and adoption.
5. `holonight-system-services` and consumers: Bluetooth component and adoption.
6. Umbrella integration review.

Provider revisions must be published and pinned before dependent consumer work starts.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Each component's install-tree consumer links without unrelated backend dependencies.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Concurrent Shell and Settings instances reflect external and cross-client Audio changes.
- [ ] Required manual ecosystem checks pass.
