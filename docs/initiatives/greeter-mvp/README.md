# HoloNight Greeter MVP

Status: Integrated

Accepted: 2026-08-10

Integrated: 2026-08-11

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Deliver the first complete HoloNight login experience as a fullscreen Qt/QML greeter. The MVP discovers configured
users and installed Wayland sessions, drives arbitrary greetd/PAM authentication conversations, starts the selected
session, exposes authorized logind power actions, and provides deterministic demo scenarios for development and
visual review.

The greeter must reproduce the external mockup's responsive clock and login-surface composition using the installed
HoloNight QML modules. The idea document and mockup remain external references and are not copied or changed by this
initiative.

## Accepted baseline

- `holonight-greeter@975e35a` is the exact implementation baseline for HGR-101.
- `holonight-qt@e30ff79` is the exact installed design-system dependency. The greeter consumes the installed
  `Holonight`, `Holonight.Core`, and `Holonight.Controls` QML modules and does not copy their primitives.
- `holonight-shell@c32c7d9` is an inspected, unchanged provider of the existing HoloNight Wayland desktop entry and
  session command. The greeter discovers that entry through the same general desktop-entry mechanism as other
  installed Wayland sessions.
- HGR-101 must be implemented, verified, committed, and published in `holonight-greeter` before the umbrella may pin
  its handoff. Neither provider repository receives an implementation package in this initiative.

## MVP product contract

### Application and presentation

- The production executable is a fullscreen Qt/QML greeter intended to run as greetd's greeter command under Cage.
- The responsive composition preserves the external mockup's clock and login-surface relationship across supported
  window sizes without treating one screenshot size as a fixed canvas.
- Production UI uses installed HoloNight design-system controls, tokens, typography, focus treatment, and surfaces.
  Greeter-specific composition and authentication behavior remain owned by `holonight-greeter`.
- A demo mode runs without greetd, PAM, logind, or a privileged system installation and includes deterministic
  default, wrong-password, OTP, and fingerprint scenarios.
- Every enabled control has a working action. Keyboard-only navigation, visible focus, a Caps Lock warning on secret
  input, and readable contrast are release requirements.

### Authentication and greetd IPC

- C++ owns the Unix-socket transport, native-endian 32-bit length framing, UTF-8 JSON encoding/decoding, protocol
  state machine, and mapping into a narrow QML-facing model. QML never constructs, parses, or frames greetd JSON.
- The implementation follows the
  [official greetd IPC contract](https://github.com/kennylevinsen/greetd/blob/master/man/greetd-ipc-7.scd), using the
  socket named by `GREETD_SOCK` and the `create_session`, `post_auth_message_response`, `cancel_session`, and
  `start_session` exchanges.
- Authentication accepts any number and ordering of `visible`, `secret`, `info`, and `error` messages. It makes no
  password-first, single-prompt, OTP, or fingerprint-specific protocol assumption. Informational messages are
  acknowledged without inventing a response.
- The UI supports an in-progress cancellation path, non-fatal authentication failure and retry, malformed/general
  errors, peer disconnect, and recovery to an actionable state. Starting a session occurs only after greetd reports
  authentication success.
- Authentication responses exist only as briefly as required to submit them. Secret controls and C++ buffers are
  cleared on submission, cancellation, failure, retry, disconnect, and destruction. Responses are never logged,
  serialized, retained in demo history, or persisted.

### User and session discovery

- User discovery is machine-configurable and deterministic. The local SDD must settle the source and explicit
  include/exclude rules, stable ordering, treatment of missing metadata or avatars, and behavior when no eligible
  users remain. It must not read a selected user's pre-login configuration.
- Session discovery enumerates Wayland desktop entries from configured system directories, applies documented
  filtering and ordering, and reports invalid entries without making the remaining list unusable. X11 session
  directories and X11 launch support are excluded.
- Desktop-entry `Exec` values are parsed into an executable and argument vector according to the supported desktop
  entry field-code subset. Unsupported or unsafe entries are rejected. The resulting argument vector is passed
  directly as greetd's `start_session.cmd`; it is never interpreted by a shell.
- The existing HoloNight Shell entry supplied by `holonight-shell@c32c7d9` must be selectable without changing the
  Shell repository or special-casing HoloNight in the generic parser.

### Machine configuration and state

- `/etc/holonight/greeter.toml` is the sole production machine-configuration document. It owns user/session discovery
  policy, display labels and defaults, keyboard-layout label, and other administrator choices accepted by the local
  SDD. Invalid configuration produces actionable diagnostics and a safe documented fallback or startup failure.
- `/var/lib/holonight-greeter/state.json` stores only non-secret last-successful user and session selection. State is
  updated only after a successful session handoff, is written safely, tolerates missing/corrupt data, and never
  becomes a second configuration authority.
- The greeter never reads pre-login user configuration, writes into a user's home directory, or persists
  authentication prompts or responses. Logs and diagnostics redact user-entered responses.

### Keyboard, compositor, and power

- Cage is the tested and documented compositor. Deployment guidance must define the greetd/Cage command, runtime
  environment, permissions, failure behavior, and recovery path without overwriting administrator configuration.
- The administrator-configured keyboard layout is displayed in the greeter. Deployment documents the Cage startup
  variables `XKB_DEFAULT_RULES`, `XKB_DEFAULT_MODEL`, `XKB_DEFAULT_LAYOUT`, `XKB_DEFAULT_VARIANT`, and
  `XKB_DEFAULT_OPTIONS` from Cage's
  [public interface](https://github.com/cage-kiosk/cage/blob/master/cage.1.scd). Interactive layout switching is
  deferred because that interface exposes XKB configuration at compositor startup rather than a runtime switch API.
- Reboot and shutdown use logind over D-Bus with explicit capability/authorization handling, confirmation UI, and
  useful failure feedback. A disabled, denied, unavailable, or failed action must not leave a dead control or imply
  that power state changed.

### Installation and deployment

- The install tree contains the production binary, QML/resources, default
  `/etc/holonight/greeter.toml`, state-directory provisioning for `/var/lib/holonight-greeter`, Cage deployment
  guidance, a greetd configuration example, and any policy files required for the accepted logind authorization
  design.
- Installation never replaces, edits, or removes `/etc/greetd/config.toml`; the supplied greetd fragment is an
  example at a separate documentation path.

## Security and reliability invariants

- No authentication response crosses the C++/QML boundary except for the active submission path, and no response is
  retained after that exchange completes or aborts.
- Protocol lengths are bounded before allocation; fragmented/coalesced reads, invalid lengths, malformed JSON,
  unexpected response types, and disconnects fail safely.
- Session commands are argument vectors, not command strings passed to `/bin/sh`, `sh -c`, a terminal, or equivalent
  evaluation.
- Configuration, state, desktop entries, avatars, and server descriptions are untrusted input. Parse failures are
  bounded, diagnosed without secrets, and cannot silently authorize a session or power operation.
- Authentication and launch states expose only actions valid for the current protocol state, preventing duplicate
  submissions, stale prompt replies, or session start before success.

## Non-goals

- Hyprland greeter deployment; `holonight-shell` remains a selectable post-login session, not the greeter compositor.
- Guaranteed multi-monitor composition beyond Cage's tested MVP behavior.
- Runtime keyboard-layout switching.
- X11 session discovery or launch.
- Battery telemetry.
- An accessibility settings menu. Keyboard operation, focus visibility, Caps Lock warning, and readable contrast are
  still required baseline accessibility behavior.
- Per-repository distribution packaging. Packaging and release engineering for the complete HoloNight ecosystem is
  deferred to a future cross-project initiative.
- Changes to `holonight-qt`, `holonight-shell`, the external idea document, or the external mockup.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-greeter` | Complete greeter MVP: application, demo scenarios, discovery, greetd client, authentication/session state, power actions, machine configuration/state, and deployment documentation | [Local SDD](../../../holonight-greeter/docs/sdd/greeter-mvp/SPEC.md) |
| `holonight-qt` | Inspected unchanged provider of installed HoloNight Qt/QML design-system modules at `e30ff79` | Not required (unchanged provider) |
| `holonight-shell` | Inspected unchanged provider of the installed HoloNight Wayland session entry at `c32c7d9` | Not required (unchanged provider) |
| umbrella | Accepted contract, exact baselines, handoff pin, and final exact-revision integration review | This initiative |

## Dependency order

1. `holonight-qt@e30ff79` and `holonight-shell@c32c7d9` remain published, installed provider contracts.
2. HGR-101 authors its local SDD and implements the complete MVP in `holonight-greeter` from `975e35a` against those
   exact provider revisions.
3. The verified HGR-101 commit is published to the canonical `holonight-greeter` remote.
4. HGR-201 pins that published commit and performs umbrella integration at the exact revisions.

Provider revisions and the greeter handoff must be available from their canonical remotes before the umbrella pin is
updated. A clean, verified greeter worktree is a local handoff, not an integrated initiative.

## Integration acceptance criteria

- [x] HGR-101 has a published implementation commit, linked local SDD, and complete local verification record.
- [x] All participating submodules are clean and pinned to commits available from their canonical remotes.
- [x] The greeter builds and consumes the installed QML modules from `holonight-qt@e30ff79`; it does not rely on a
      source-tree import path or copied provider assets.
- [x] Wayland session discovery accepts the unchanged HoloNight entry from `holonight-shell@c32c7d9`, and its parsed
      command reaches greetd without shell evaluation.
- [x] Fake-server protocol, deterministic domain, offscreen QML/demo, toolchain, and install-tree
      verification all pass at the pinned greeter revision.
- [x] A live Cage/greetd VT test passes successful and failed authentication, cancel/retry, session selection/start,
      configured-layout display, authorized/denied power behavior, and recovery from greeter failure without a login
      loop.
- [x] The final HGR-201 row records exact revisions, commands, results, manual evidence, and verification date before
      this initiative becomes `Integrated`.
