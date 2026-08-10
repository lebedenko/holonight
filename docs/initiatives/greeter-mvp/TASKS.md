# HoloNight Greeter MVP — Coordination Ledger

The initiative was accepted on 2026-08-10 against `holonight-greeter@975e35a`, `holonight-qt@e30ff79`, and
`holonight-shell@c32c7d9`. Qt and Shell are inspected, unchanged providers; only HGR-101 may be assigned for product
implementation.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| HGR-101 | `holonight-greeter` | From exact baseline `975e35a`, author the local SDD; implement and publish the complete fullscreen Qt/QML greeter MVP, deterministic demos, user/Wayland-session discovery, C++ greetd client and arbitrary PAM conversation flow, safe session launch, logind power actions, machine configuration/state, Cage guidance, and Arch packaging against `holonight-qt@e30ff79` and the unchanged `holonight-shell@c32c7d9` session contract | Published providers `holonight-qt@e30ff79`, `holonight-shell@c32c7d9`; this accepted initiative | Pending | Ready | — | Required before `Done`: fake Unix-socket greetd protocol suite; deterministic domain/security tests; offscreen QML/demo suite; build, format, static analysis, QML lint/type, install-tree and package-content checks; live Cage/greetd VT matrix; publish the verified commit to the canonical remote |
| HGR-201 | umbrella | Confirm the HGR-101 handoff is published; pin it; verify provider compatibility and the complete MVP at exact revisions; record final commands/results/date; mark the initiative `Integrated` only after successful integration | HGR-101 | — | Planned | — | — |

## Required HGR-101 verification

### Fake greetd server

Unit tests must use a fake Unix-socket greetd server and cover:

- fragmented length headers and payloads, coalesced frames, and bounded frame handling;
- each `visible`, `secret`, `info`, and `error` authentication message type;
- repeated prompts and mixed prompt sequences without fixed ordering assumptions;
- authentication failure followed by retry;
- cancellation while a conversation is active;
- malformed lengths, malformed JSON, unexpected replies, and general errors;
- disconnects during connection, prompting, response submission, and authenticated state;
- successful authentication and `start_session` with the exact selected argument vector.

### Deterministic domain and security tests

Tests must cover:

- configurable user filtering, ordering, missing metadata, and empty results;
- Wayland-only session search, filtering, ordering, invalid entries, and duplicates;
- desktop-entry `Exec` parsing, supported field codes, rejection of unsafe/unsupported input, and proof that no shell
  evaluation occurs;
- default, valid, missing, and malformed `/etc/holonight/greeter.toml` behavior through injectable test paths;
- missing/corrupt state, last-successful selection updates, safe replacement, and rejection of secret state fields;
- clearing active secret input and C++ storage after submission, cancellation, failure, retry, disconnect, and
  destruction, with logs verified not to contain responses;
- mocked logind capability, authorization, denial, unavailable-service, and operation-failure paths for reboot and
  shutdown.

### Offscreen QML and demo tests

Headless tests must cover:

- default, wrong-password, OTP, and fingerprint demo scenarios;
- keyboard-only traversal and activation across all enabled actions;
- visible and correct focus transitions as prompts and errors change;
- Caps Lock warning behavior on secret input;
- responsive clock/login-surface composition at the accepted compact, standard, and wide size matrix;
- user/session empty and error states, disconnect/retry presentation, and power confirmation/failure feedback;
- an assertion that every visible enabled control is connected to a valid action and no placeholder/dead controls
  ship.

### Toolchain, installation, packaging, and live system

Before HGR-101 is `Done`, record successful:

- configure/build and the complete automated test suite;
- format check, project static analysis, and QML lint/type checks;
- install-tree smoke test using installed HoloNight QML modules rather than source-tree imports;
- Arch package build and content/ownership verification for the binary, configuration, resources, state-directory
  provisioning, documentation/example, and policy files;
- upgrade/install checks proving `/etc/greetd/config.toml` is never packaged, created, edited, replaced, or removed;
- live Cage/greetd testing on a VT for successful and failed authentication, arbitrary prompt handling as available,
  cancel/retry, Wayland session selection/start, administrator-configured keyboard-layout display, reboot/shutdown
  authorization and denial/failure, and recovery after forced greeter failure without a login loop.

The local SDD may name concrete commands and fixtures, but it may not weaken or omit this observable verification
matrix.

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on HGR-101 is a local checkpoint, not an integrated initiative. Record exact pins, commands, results, manual
evidence, and the verification date in HGR-201 before changing the initiative status to `Integrated`.
