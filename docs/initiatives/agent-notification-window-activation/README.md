# Agent Notification Window Activation

Status: Accepted

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Let a user activate the existing terminal window for an agent session from its desktop notification or through the
agent daemon's public D-Bus API, with compositor-specific window management remaining in HoloNight Shell.

## Non-goals

- Supporting Niri, KWin, labwc, or compositor-specific behavior beyond Hyprland and Sway.
- Spawning a terminal or any replacement process when the original window cannot be activated.
- Specializing HoloNight Shell's notification server for agent notifications or adding private notification hints.
- Making `holonight-agentd` or `hn-agent-run` aware of compositor IPC.

## Participating repositories

| Repository | Published baseline | Ownership in this initiative | Local SDD |
|---|---|---|---|
| `holonight-shell` | `dd78e9961ef38770f933a9dad94ce5c47e019ae0` | Window-resolution and activation provider | [`agent-window-activation`](../../../holonight-shell/docs/sdd/agent-window-activation/SPEC.md) |
| `holonightd` | `dbb6ecc6205f964c3c4dc4e2467503ee940dc34f` | Session descriptors, notification action handling, and activation API | [`agent-notification-window-activation`](../../../holonightd/docs/sdd/agent-notification-window-activation/SPEC.md) |

These exact published revisions are the upstream implementation baselines. Implementers work and commit only in their
assigned repository; the umbrella coordinator records accepted handoffs and updates gitlinks later.

## Cross-repository contracts

### Shell activation provider

HoloNight Shell owns the session-bus service interface
`org.holonight.Shell.WindowActivation1` and exposes:

```text
RequestWindowActivation(au processLineage, s titleHint) -> b accepted
```

`processLineage` is ordered from the registered agent process toward its ancestors. The shell matches compositor
windows by PID from that lineage and uses a non-empty `titleHint` only as an exact-title disambiguator. The result is
`true` only when a supported, connected backend resolves exactly one target and accepts its activation command for
delivery. It does not promise that focus has completed before the reply. Missing, closed, ambiguous, unsupported, or
disconnected targets return `false` and never launch a process.

### Agent activation API

`holonight-agentd` retains the existing `org.holonight.AgentActivity1` API and adds:

```text
ActivateSession(s sessionId) -> b accepted
```

There is no activation signal. The daemon resolves the active session descriptor and makes a bounded request to the
shell provider. Its result reflects whether the shell accepted that request.

### Notification action ownership

Notifications continue to use the standard `org.freedesktop.Notifications` contract. The originating daemon sends an
`"open"` action and subscribes to `ActionInvoked(u id, s actionKey)` and `NotificationClosed(u id, u reason)` on its
persistent session-bus connection. It correlates the notification ID to a captured activation descriptor and calls
the shell provider itself; the shell notification server needs no agent-specific behavior.

## Compositor support

| Environment | Resolution and activation | Contract result |
|---|---|---|
| Hyprland | PID/address inventory and address activation | Supported |
| Sway | PID/container inventory and container focus | Supported |
| Generic Wayland | No safe compositor-neutral activation primitive in scope | Clean `false` |

## Dependency order

1. `ANWA-101`: `holonight-shell` publishes the activation provider from baseline
   `dd78e9961ef38770f933a9dad94ce5c47e019ae0`.
2. `ANWA-102`: `holonightd` adopts the provider from baseline
   `dbb6ecc6205f964c3c4dc4e2467503ee940dc34f` after `ANWA-101` is published and pinned.
3. `ANWA-201`: the umbrella coordinator pins both published handoffs and performs integration review.

Provider revisions must be published and pinned before dependent consumer work starts.

## Integration acceptance criteria

- [x] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [x] The two D-Bus interfaces and accepted-result semantics are compatible at the pinned revisions.
- [x] Repository builds and automated tests pass in dependency order.
- [ ] Hyprland and Sway notification-action and direct `ActivateSession` smoke checks pass.
- [ ] Closed-window, ambiguous-target, unavailable-shell, and generic-Wayland checks fail cleanly without a process launch.
