# Unified Qt Quick Controls and Third-Party Compatibility — Coordination Ledger

The initiative is Accepted following user scope approval on 2026-09-07. Discovery UQC-001 is complete and
UQC-002 settles the contract. UQC-101 is In Progress from published provider assignment baseline
`033d6001fd088a96ac6e4ff936b6bafcf6ab5d4c`; consumers remain Planned until the complete provider handoff is published and pinned.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| UQC-001 | `holonight-qt` | Complete provider/consumer audit, application evidence and coverage proposal | — | [SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/SPEC.md) | Done | `033d6001fd088a96ac6e4ff936b6bafcf6ab5d4c` | 2026-09-07: user approved full REVIEW; manual observations and isolated authentication recorded with explicit limits. Audit build, six layout/palette cases, three installed-fixture modes, Python syntax and whitespace pass. Canonical publication confirmed. |
| UQC-002 | umbrella | Accept shared contracts, target-app coverage, dependency order, integration gates, and published assignment baselines | UQC-001 | This initiative | Done | Acceptance checkpoint | 2026-09-07: user approved all nine additions, palette support, indicator geometry and explicit composition limits. Existing source inventory and all six published baselines rechecked; final manual/activation gates retained. |
| UQC-101 | `holonight-qt` | Implement accepted coverage and composite migration; provide policy checks, embedded-config example, installed-consumer tests, and aligned documentation | UQC-002 | [SDD](../../../holonight-qt/docs/sdd/unified-qtquick-controls/IMPLEMENTATION.md) | In Progress | `22ded7815727ce483fd91e82a9cc04bfe252ec3b` (geometry slice) | 2026-09-07: indicator-only and mirrored geometry fixed; original code fails new behavioral regression, fix passes five focused tests and all 28 provider CTest entries including installed consumer. Published checkpoint; remaining UQC-101 slices stay open. |
| UQC-102 | `holonight-shell` | Migrate shell/authentication; verify activation propagation and distinguish configured selection from module loading in diagnostics | UQC-101 | Pending | Planned | — | — |
| UQC-103 | `holonight-settings` | Adopt namespaced runtime controls and embedded default; align instructions and contradictory contract tests | UQC-101 | Pending | Planned | — | — |
| UQC-104 | `holonight-ai` | Adopt runtime controls and embedded default; align import checker and verify composite behavior | UQC-101 | Pending | Planned | — | — |
| UQC-105 | `holonight-pkg-manager` | Adopt runtime controls and embedded default; verify independent launch and scrollbar behavior | UQC-101 | Pending | Planned | — | — |
| UQC-106 | `holonight-greeter` | Adopt runtime controls and embedded default; verify pre-session startup and retain scaled ComboBox geometry | UQC-101 | Pending | Planned | — | — |
| UQC-201 | umbrella | Verify published clean pins, dependency-order checks, activation paths, and accepted third-party matrix under Hyprland and Sway | UQC-101–UQC-106 | This initiative | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies or acceptance are not ready.
- `Ready`: may be assigned with an exact published baseline and repository-local requirements.
- `In Progress`: repository work has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Confirm each implementation commit
is available from the canonical remote before updating its gitlink. Make umbrella checkpoint commits after accepted
handoffs; implementers do not modify umbrella status or pointers.

Record commands, results, application and Qt versions, limitations, and the verification date in `UQC-201` before
marking it Done and setting the initiative status to Integrated. Historical survey observations do not satisfy that
final verification gate.

## Discovery continuation handoff — 2026-09-06

Provider documentation and collection fixture published first; canonical `origin/main` availability confirmed before
this gitlink update. This checkpoint accepts the partial discovery record, not UQC-002 scope or integration.

- Corrected stderr collection and bounded Haruna backtraces replace the earlier inference of pre-QML stalls:
  ordinary/private-bus runs both reach the event loop. All three desktop apps load staged HoloNight/Core modules.
- Separate installed consumer passes three modes and 18 type-origin checks plus library-origin assertions.
  Haruna's programmatic Fusion fallback is effective; its seek/volume painting remains application-owned.
- Matching NeoChat/Tokodon release startup and welcome/server sources are retrieved and referenced with hashes.
- Provider APPLICATIONS/DESIGN contain a provisional exact addition list and compatibility recommendations that
  preserve public composite APIs. No product implementation or public API changes are included.
- Manual Hyprland editing/navigation/scrolling/popups/visual states remain unobserved. Only the active user login
  is available; the existing authentication agent remains untouched. A separately prepared login and confirmed
  exclusive registration are required for the surveyed Qt agent prompt/cancellation evidence.
- Provider fixture build/checks, Python syntax, relative links and whitespace pass. Umbrella links and whitespace
  pass. No unrelated suites or UQC-201 integration checks are appropriate at this discovery checkpoint.

Resume with the [guided checklist](../../../holonight-qt/docs/sdd/unified-qtquick-controls/audit/CHECKLIST.md) and
[durable evidence](../../../holonight-qt/docs/sdd/unified-qtquick-controls/audit/EVIDENCE.md). UQC-001 stays In Progress,
UQC-002 stays Planned, initiative stays Draft. Stop for joint scope review; UQC-201 retains full Hyprland/Sway
activation and integration acceptance. Unrelated package-manager mockups and other checkouts are preserved.

## Scope-review preparation — 2026-09-07 (unpublished)

Reviewed the provider's existing continuation artifacts, including manual desktop observations, isolated agent
registration/prompt/cancellation evidence, and controlled geometry/palette comparisons. Authentication discovery
is complete according to the recorded user observations; the cancelled command's exact numeric exit was not
retained. Earlier missing-authentication statements above describe the published 2026-09-06 checkpoint.

Reconfigured and built the standalone audit in `/tmp/uqc-20260907-discovery-build`; the build passed, with CMake
warnings about unavailable Kirigami plugin link targets. All six `check-layout.py` characterization runs against
`/var/tmp/uqc-auth-test-20260907/prefix` passed, including runtime Kirigami loading. These reproduce existing behavior,
not acceptance of the defects. Current run logs: `/tmp/uqc-layout-itg2jcu2` (temporary).

The [provider scope review](../../../holonight-qt/docs/sdd/unified-qtquick-controls/REVIEW.md) is ready for joint
discussion of indicator geometry, palette authority, nine proposed controls and explicit composition limitations.
UQC-001 remains In Progress, UQC-002 Planned and the initiative Draft. Provider continuation files are still
uncommitted; this note does not accept a published handoff or update its pin.

## Accepted discovery handoff — 2026-09-07

Provider `033d6001fd088a96ac6e4ff936b6bafcf6ab5d4c` is committed, published on canonical `origin/main`, and clean.
The umbrella pin now accepts that discovery handoff. The preceding unpublished notes are historical. User approval
resolves the pending scope review; README's accepted-scope section is authoritative for UQC-002.

All five consumer checkouts still match their published discovery baselines. Package-manager's two unrelated
untracked mockups are retained; they do not change its source baseline or satisfy final clean-tree acceptance.
No UQC-201 checks have been run. Final runtime/manual coverage remains open.

## Provider geometry checkpoint — 2026-09-07

Published provider `22ded7815727ce483fd91e82a9cc04bfe252ec3b` contains the first UQC-101 implementation slice and its
local implementation ledger. Canonical `origin/main` was checked before pinning; the provider working tree is clean.
This checkpoint does not make consumers Ready: palette support, all nine additions, composite/runtime migration,
embedded defaults, policy and final installed/negative/rendering coverage remain provider work.

Verification: full provider build, five focused QML tests, 28/28 CTest entries, and whitespace checks passed.
The new geometry regression failed before the fix. Exact commands and work scope are in the local SDD; no live
application interaction or UQC-201 ecosystem checks were performed for this slice. Resume from the pinned revision.
