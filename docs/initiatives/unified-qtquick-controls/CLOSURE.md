# Unified Qt Quick Controls — closure summary

Status: **Integrated**. UQC-201: **Done**. Closed on **2026-09-19** by the user's
explicit scope decision. This is completion of the unified-look initiative for
early-stage HoloNight applications, with documented compatibility limits.

## Why we started

HoloNight applications mixed direct style imports, standard Qt controls and
fallbacks. Third-party applications could have a dark palette without actually
using HoloNight controls. We wanted consistent appearance and everyday control
behavior, a common selection path, and an honest account of what can be themed.

## What was delivered

- Provider coverage expanded for the standard controls needed by the surveyed
  applications. Palette roles, icons, menu/selection states and popup backgrounds
  were corrected where concrete defects were found.
- Shell/authentication, Settings, AI, package-manager and greeter adopted
  namespaced runtime Qt Quick Controls and embedded HoloNight defaults. Explicit
  Fusion overrides remain supported. Core primitives and shared composites keep
  their public APIs and intentional HoloNight appearance.
- Shared keyboard focus, dropdown delegate ownership/dismissal, stationary-pointer
  hover/selection, Weather row geometry and fractional layer-surface coordinates
  received focused repairs. Authentication UI/cancellation issues found during
  the work were also repaired; this did not establish a need to recertify login.
- Installed module discovery, import boundaries and style overrides have
  regression coverage. Native Qt 6 Haruna, NeoChat and Tokodon were examined and
  exercised with explicit application-owned, Kirigami and fallback boundaries.
- AI's shared-window palette problem was repaired. A later apparent palette
  regression was traced to the diagnostic observer and corrected there. P03 is
  closed. The intended fullscreen greeter scenario passed; its windowed caret
  experiment did not require a product repair.

Implementation ownership, commits and local SDDs remain in [TASKS.md](TASKS.md).
The [gotchas](GOTCHAS.md) collect the practical lessons and unresolved limitations.

## Evidence we retain

We accept the existing repository verification, recorded dependency-order builds,
installed-launch checks and reviewed human interaction results. The
[final checklist](FINAL-ACCEPTANCE.md) and [canonical findings](FINDINGS.md) retain
their exact dates, versions, scopes, failures, fixes and limitations. Recent
provider/AI verification passed 89 provider tests and 713 AI tests, with one
intentional real-credential-service skip. Settings and AI Sway DPR-1 and accepted
fractional runs remain accepted; none needs repetition to close this initiative.

The user reports that the installed greeter and askpass are used every day without
authentication problems. This is practical usage evidence, not a fabricated new
instrumented authentication test. It is sufficient context to stop demanding
unrelated authentication acceptance for an appearance-focused initiative.

Closure uses the unchanged gitlinks at umbrella `e78d134`. Their published
handoffs and clean-pin checks are already recorded. No product source, dependency,
public API, installed service, kit or submodule pin changes accompany closure.
There is no new claim of a complete release-validation matrix at one revision.

## Scope correction and removed gates

The work expanded into a release-style acceptance exercise beyond the original
goal and the maturity of these applications. The user explicitly ended that
exercise. The following are **removed requirements**, not passing test results:

| Former outstanding gate | Final disposition |
| --- | --- |
| Fresh successful-authentication challenges for greeter/askpass/Polkit | Removed from this styling initiative; preserve existing everyday usage and prior scoped UI results. |
| Exhaustive terminal, desktop, D-Bus and shipped-systemd activation coverage | Removed as a closure gate; retain completed selection/discovery checks and actual known defects. |
| Another real pre-session greeter login/session/cleanup acceptance run | Removed; the installed greeter is in everyday use and its scoped appearance work is accepted. |
| Every remaining app × compositor × style × scale combination, including unopened controls and palette variants | Removed; retain demonstrated coverage and explicitly documented limits. |
| Another fresh kit, broad rebuild, publication audit or final manual certification cycle solely to finish the ledger | Removed; close using the existing evidence and this explicit disposition. |

These decisions supersede pending/open instructions in earlier checklists,
handoffs, kits and dated findings. Historical documents and immutable artifacts
remain available for diagnosis, **not an execution queue**. There is no next batch.

## Future work

F05/P01 external behavior and deferred historical diagnostics remain documented;
closure does not mean they were fixed. Settings/AI layout and composition wishes
belong to ordinary product development. None is an automatic dependency of this
closed initiative. Start new work only for an explicitly requested improvement or
a concrete bug in actual use; choose checks proportional to the affected behavior.

For this documentation-only closure, verification consists of local Markdown
links/anchors, shell-example syntax, REUSE licensing and whitespace checks.
Product suites, authentication challenges and UI runs are deliberately not repeated.
