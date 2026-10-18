# Reproducible VM Acceptance — Coordination Ledger

Status: Draft — implementation deferred to a later session

## Findings record — 2026-10-18

This audit combines the supplied session findings with the retained local artifacts and the
[Shell acceptance record](../../../holonight-shell/docs/sdd/managed-wayland-sessions.md#native-configuration-vm-acceptance-2026-10-18).
The VM inventory and discovery/process lessons below are reported session findings, not a new VM inspection.
No VM actions or acceptance tests were performed to create this draft.

### Observed successes

- Guest-native builds used Qt 6.11.2/system libraries and a private prefix, with UWSM 0.26.7, Hyprland 0.56.2,
  Sway 1.12 and labwc 0.20.2. No container binary was deployed.
- The isolated `hnmanaged` account used real PAM/logind sessions on VT3. Actual Polkit authentication produced
  root-owned markers on all three compositors. Sway retained `cap_sys_nice=ep`; its unreadable process environment
  did not prevent managed discovery. Doctor correctly reported that environment check as incomplete.
- Managed applications survived Shell restart. Shell UI logout journals show applications, Shell and Polkit
  stopping before the compositor. Repeat login, native configuration reload and installed fallback startup worked.
- FileChooser request/close and Settings color-scheme routing worked. Firefox permission and real wlr/Hyprland
  interactive pickers delivered 1280×800 video callbacks; the historical record reports minima of 60, 45 and 60
  frames for Sway, labwc and Hyprland respectively.
- labwc Appearance apply/status/revert exercised the selected persistent directory, title font/theme/accent edits,
  ownership conflict handling, atomic `rc.xml` replacement, keybinding reload and menu-edit preservation.
  The original title font was restored. A competing personal Sway `uwsm finalize` was rejected read-only.

These observations remain valid within their tested setup and scope.

### Harness problems and process lessons

- Initial libvirt discovery was incomplete. Future tooling must identify connection URI, domain and access context
  before concluding that a VM or capability is absent; the supplied `hn-arch` was suitable without hardware changes.
- Dependency-order retries and missing dependencies made setup ad hoc. Record package prerequisites and installed
  provider order before builds. KF6Config development files were absent, so the optional Appearance KDE adapter was
  omitted; this does not establish complete-desktop coverage. Journals also report unavailable RealtimeKit.
- Private-prefix FileChooser activation required a user D-Bus service-file link because the user bus predated the
  added data search path. This workaround demonstrates the fixture's behavior, not normal installer activation.
- Pointer coordinates and focus-dependent keyboard input were brittle. Track window/output/focus observations,
  bounded retries and failure evidence; retain actual picker interaction rather than bypassing permission UI.
- Disposable harnesses were left in ignored directories. They are useful local evidence, but are neither versioned
  tooling nor a reproducible provisioning recipe. Capture harness source and setup assumptions in future tooling.
- Completion reporting was broader than the evidence. Report each assertion and qualification explicitly; distinguish
  managed logout, native dispatcher execution, cold login, service cleanup and content freshness.

### Unresolved product findings

- The journal records FileChooser D-Bus activation units exiting with `status=255/EXCEPTION` and failed `exit-code`
  results around session teardown (including 18:10:41, 18:23:12 and 18:32:49). Successful request/close does not
  establish clean backend shutdown. Reproduce activation, close, logout and relogin before proposing a fix.
  A relationship to compositor teardown or service lifetime is a hypothesis, not a confirmed cause.
- Qt host-portal registration warnings include inability to open a process root and missing app information.
  Shell/FileChooser icon-provider warnings also remain in the journal. Missing packages, private-prefix identity,
  activation timing and product defects are possible explanations, not established diagnoses. Classify and route
  each warning after reproduction under the normal installation profile; do not silently declare it harmless.

### Untested behavior and qualifications

- Hyprland's native Lua exit dispatcher was exercised after a fallback login **inside a managed session**. It does
  not prove genuinely unmanaged-session logout. Cover that separately for every supported compositor.
- VT3 sessions with a lingering test user manager do not establish a cold greeter login without lingering.
  Returning the VM to the greeter VT during cleanup is not end-to-end greeter login acceptance.
- `capture-server.py` counts `requestVideoFrameCallback` calls and records metadata. Retained final JSON reports
  975/45/3255 callbacks for Sway/labwc/Hyprland, all with `mediaTime: 0`. These later counters do not contradict the
  earlier minima, but neither proves changing captured pixels. Add a changing source and receiver-side content
  assertions; callback counts, nonzero dimensions and readiness are insufficient freshness evidence.
- Clean provisioning, normal installer activation/upgrade/uninstall in the VM, deliberate minimal-dependency
  degradation, multi-display behavior, other resolutions and scaling remain outside this historical run's proof.
- Automated Appearance persistence tests and live apply/reconfigure/revert observations do not replace a repeatable
  cold-login/relogin persistence matrix. Missing optional KDE coverage must stay explicit.

## Evidence and baseline revisions

Local evidence is under umbrella `build/managed-session-acceptance/`: `hn-managed-journal.log`,
`hn-{sway,labwc,hyprland}-logout.log`, `hn-sway-doctor.log`, `hn-managed-evidence.tar.gz`,
`hn-native-build-logs.tar.gz`, screenshots, disposable Python/shell harnesses and `evidence/` JSON results.
The older Shell record also refers to `build/session-acceptance/`; that directory was absent during this audit.
These ignored artifacts are local evidence, not durable repository attachments. Future runs must retain an
identified evidence bundle outside disposable guest state; this draft does not promise availability of these
local files in another checkout or publish them.

Published baseline references, confirmed against locally available `origin/main` refs on 2026-10-18 (no fetch):

| Repository | Revision | Role |
|---|---|---|
| umbrella | `46648c90079b220b9e38d07b2b4ee78885575129` | Published integration pins; preceding `b6fcabb` records native configuration/VM acceptance |
| `holonight-shell` | `f895874f56e4e11afe61ace13558e6cdba66672c` | Managed-session implementation and historical acceptance record |
| `holonight-appearance-adapters` | `bab3f58217f6c3070c4901d58af53f5d1e11dd12` | Persistent labwc configuration support |

The umbrella revision records the remaining component pins, including Greeter and FileChooser. These are provenance
references, not a claim that the historical guest build archived a complete source/package manifest. The historical
Shell note's “no publication” statement describes that acceptance phase; the later umbrella pin commit records the
published baseline. No revisions are changed or published by this draft.

## Repository work packages

All packages are Planned and deferred; no implementation is authorized by this ledger. Existing local designs are
context, not preselected fixes. Investigate first and let each component own any necessary follow-up design.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification / completion evidence |
|---|---|---|---|---|---|---|---|
| RVA-001 | umbrella | Reproducible provisioning, profiles, tracked orchestration, normal installer coverage and evidence contract | — | [Contract](README.md); tooling design deferred | Planned | — | Repeat baseline/clone creation from recorded inputs; native build/install logs; staging/ownership/collision/upgrade/uninstall results; exported evidence and credential cleanup |
| RVA-002 | `holonight-shell` | Lifecycle and portal-routing verification; investigate owned failures | RVA-001 | [Managed sessions](../../../holonight-shell/docs/sdd/managed-wayland-sessions.md); follow-up after investigation | Planned | — | Three-compositor restart/PID survival, ordered managed logout, separate unmanaged exit, native reload/fallback, real Polkit, routing and changing-content capture evidence; focused local checks for any fixes |
| RVA-003 | `holonight-greeter` | Cold login and return-to-greeter coverage | RVA-001; RVA-002 for integrated logout | [Boot/login reliability](../../../holonight-greeter/docs/sdd/boot-login-reliability/); follow-up deferred | Planned | — | No-linger cold boot/login, all compositor selections, logout/relogin and failure-recovery journals; focused local verification for any fixes |
| RVA-004 | `xdg-desktop-portal-holonight` | Investigate FileChooser activation/shutdown failures and owned warnings | RVA-001; coordinate lifecycle evidence with RVA-002 | [FileChooser](../../../xdg-desktop-portal-holonight/docs/sdd/filechooser/README.md); cause/design unconfirmed | Planned | — | Minimal reproduction under normal install, request/close/logout/relogin logs, activation-unit status and cause classification; fix or justified disposition with focused regression evidence |
| RVA-005 | `holonight-appearance-adapters` | Repeatable labwc persistence checks | RVA-001; RVA-002 for session configuration selection | [Configuration architecture](../../../holonight-appearance-adapters/docs/sdd/configuration-architecture/README.md) | Planned | — | Apply/status/revert across reload/relogin, selected directory and ownership conflicts, preserved menu edits, optional-dependency profile results and focused local checks |
| RVA-006 | umbrella | Integrated acceptance and evidence review | RVA-001–RVA-005 | [Acceptance criteria](README.md#integration-acceptance-criteria) | Planned | — | Record date, commands, profiles, revisions and outcomes for every criterion, display/scaling matrix and warning disposition; verify compatible clean pins after authorized publication and durable evidence retention |

`Done` means a local commit and local verification, not an integrated initiative. Use the template's Planned,
Ready, In Progress, Done, Blocked and Superseded states when work resumes. Record integration commands, results,
verification date and remaining explicit limitations in RVA-006 before changing the initiative to Integrated.
