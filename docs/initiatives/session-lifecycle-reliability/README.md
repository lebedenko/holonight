# Session Lifecycle Reliability

Status: Accepted

## Goal

Make isolated greeter verification produce actionable compositor cores and make logout follow the owner of the active
HoloNight session.

## Non-goals

- Vendoring Cage, wlroots, Hyprland, or Aquamarine.
- Treating compositor teardown crashes as greeter or shell application failures.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-greeter` | Isolated VT2 live-test lifecycle and Cage evidence capture | `docs/sdd/boot-login-reliability/` |
| `holonight-shell` | UWSM-aware logout dispatch | `docs/sdd/session-logout-reliability/` |

## Cross-repository contracts

The live greetd harness launches the installed HoloNight session entry without changing the primary greetd service.
When that entry selects UWSM, logout is owned by UWSM; direct Hyprland sessions retain compositor-native logout.

## Dependency order

1. `holonight-greeter` hardens isolated VT2 verification.
2. `holonight-shell` corrects logout dispatch and is exercised through that harness.
3. Umbrella integration review.

## Integration acceptance criteria

- [x] Local repository tests pass.
- [x] VT2 is restored after the live harness exits.
- [ ] Sidebar logout ends a UWSM session and greetd returns to the greeter.
- [x] Cage and Hyprland teardown crashes leave symbolizable evidence.
