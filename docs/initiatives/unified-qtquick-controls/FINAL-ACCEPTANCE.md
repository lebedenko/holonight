# Batch 8 final acceptance

Status: In Progress, updated 2026-09-18. Initiative Accepted; UQC-201 In Progress.
This is the current acceptance checklist. Historical unchecked lists in README,
MANUAL, GUIDED and earlier batches are provenance, not requests to repeat work.
Preserve completed manual acceptance unless a subsequent implementation affects it.
Gitlinks are authoritative. Current preparation baseline is umbrella
`6f7af409a38b7a217fec38bf607e43446f86c07f`, including published provider
`e94ceddbd3c0e4cb29e21bcdfd6758e3e4639f4f`. The focused P03 kit and release
verification are recorded in [P03 readiness](P03-READINESS.md); use the
[two-run focused handoff](P03-RECHECK.md). Current READY kit:
`/tmp/holonight-uqc201-p03-xtndrklf` (device-access repair; see the current readiness record).

UQC-220 local and focused Settings manual acceptance remain accepted. UQC-222
remains Done. The [P03 review](FINDINGS.md#p03-human-evidence-review--2026-09-18)
verifies both processes and preserves successful immediate transitions/default
light-time construction. P03 remains open: palette roles revert during interaction,
and Fusion Settings was first constructed dark. [UQC-223](UQC-223.md) is Done as a
diagnosis: an allocating observer exposes a stale Qt root palette on activation.
Instrumentation repair remains separate. No next batch or repeated navigation checklist.

The earlier kit `/tmp/holonight-uqc201-final-dyxe1nl_` and its
[revalidation](BATCH8-REVALIDATION.md) remain historical evidence. Its submitted
[AI runs](BATCH8-AI.md) accepted interaction/main-window coverage and exposed P03;
they must not be used to validate the repaired provider. Earlier baseline
`c16b164` and Settings documentation follow-up `0eb5028` remain provenance.

## Reconciled requirements

| Requirement | Classification | Evidence / remaining coverage |
|---|---|---|
| Repository implementation handoffs and local SDDs | Accepted with evidence | Delivered repository packages Done in [TASKS](TASKS.md); UQC-223 diagnosis Done; UQC-209/210 Superseded. UQC-207 closed by [user disposition](FINDINGS.md#batch-3-user-directed-closure--2026-09-16). |
| Clean, published compatible pins | Accepted with evidence | Fresh canonical audit and shared-contract review at the pinned revisions; do not adopt newer remote revisions automatically. |
| Embedded default, Fusion override and explicit competing styles | Accepted with automated evidence | Post-repair build and installed launch matrices pass for provider examples, shell/authentication, Settings, AI, packages and greeter; see [focused current results](P03-READINESS.md). |
| Namespaced imports, attached properties and exceptions | Accepted with evidence | Provider and consumer policy checks and negative fixtures. |
| Installed consumers and missing-module deployment failures | Accepted with automated evidence | Fresh isolated installation passes with host HoloNight hidden, staged origins verified and build paths rejected; see [focused current results](P03-READINESS.md). |
| Foreign control origins and explicit fallbacks | Manual verification required | Loading is already demonstrated, but maps are not per-control evidence. Correlate remaining reachable surfaces with created origins and actual DPR; classify HoloNight, Basic/Fusion, application-owned or inaccessible with reason. |
| Shared focus, dropdowns, launcher and rendering repairs | Accepted with evidence | [Batches 1–3](BATCHES.md), F01/F02, D01–D04/F06/F07 and accepted icon/menu/selection/Switch/background results in FINDINGS. F03 original attribution remains uncertain; eligibility fixtures pass. No repeat repair comparisons. |
| Authentication cancellation and repaired presentation | Accepted with evidence | [Batch 2](FINDINGS.md#batch-2-authentication-manual-acceptance--2026-09-14), A03 cancellation and A02 synthetic lifecycle/rendered acceptance. Original missing/overwritten logs remain documented. |
| Successful authentication | Manual verification required | Real disposable login; guarded registration preflight and harmless `/usr/bin/true` challenge; human credential entry only. Cancellation does not close this gate. Existing cancellation-only helpers must not be represented as successful-authentication acceptance. |
| AI palette P03 | Open: observer-induced stability failure and incomplete construction coverage | [Two-run review](FINDINGS.md#p03-human-evidence-review--2026-09-18): immediate transitions pass, but palettes later revert; Fusion light-time construction missing. [UQC-223](UQC-223.md) Done: allocating-observer/Qt root-palette boundary reproduced; passive checks pass. Separately verify instrumentation repair before affected stability and fresh Fusion light-time checks. Prior interaction coverage preserved. |
| Palette rendering P02 | Accepted with evidence | [Nine accepted runs](FINDINGS.md#batch-4-manual-visual-acceptance--2026-09-15), scale 1; preserve those observations. Remaining owned/compositor/fractional transition coverage stays manual. |
| Shell compositor/popup S01/S02 | Accepted with evidence | [S01 repair acceptance](FINDINGS.md#s01-repair-accepted-on-hyprland--2026-09-15), Sway comparison and completed Batch 6 runs. |
| Greeter G01–G06 and fullscreen G07 | Accepted with evidence | [Batch 7](FINDINGS.md#batch-7-manual-acceptance--2026-09-15), [fullscreen closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16). Windowed G07 outside intended use; no repeat demo comparisons. |
| Terminal/desktop/D-Bus activation | Manual verification required | Preserve [Settings bus](GUIDED.md#settings-d-bus-process-correlation--reviewed-2026-09-11), [desktop](GUIDED.md#settings-desktop-entry-process-correlation--reviewed-2026-09-11), AI bus and third-party desktop PID correlations. Fill only missing control-origin, outcome and applicable compositor coverage. |
| Shipped systemd unit and wrapper | Manual verification required | Prior [transient shell](GUIDED.md#transient-systemd-shell-process-correlation--reviewed-2026-09-11) proves only transient execution. Exercise installed `holonight-shell.service` → `holonight-shell-systemd` in disposable login; record unit fragment/drop-ins, environment, actual PID and loaded origins, and restore prior manager state. |
| Real pre-session greeter | Manual verification required | Use [isolated VT procedure](../../../holonight-greeter/docs/CAGE.md), staged launcher/provider and disposable login. Record successful login/session start, geometry and cleanup. Demo/fake backend tests do not substitute. |
| Dependency-order builds/tests | Accepted with automated evidence | Configuration, system services, shell configuration, provider, adapters, shell, Settings, AI, packages, greeter; [fresh builds and focused results](P03-READINESS.md) pass; unchanged full-suite results remain labeled prior evidence. |
| Remaining app/compositor/style/scale matrix | Manual verification required | Haruna local clip; NeoChat/Tokodon logged-out surfaces; Qt hyprpolkitagent; owned Settings/AI/packages. Fill unresolved coverage in small reviewed batches, including scale 1/1.25 and HoloNight/Fusion. Preserve existing narrower observations and accepted scope. |
| Final evidence ledger and integration decision | Manual verification required | Record revisions, commands/results, versions, evidence and limitations. Do not mark Integrated before all gates pass or receive explicit disposition. |

## Recorded limitations

- F05 is an external Qt/Hyprland activation defect with a plain-Qt reproduction;
  P01 is an external palette activation defect. Neither is fixed. Keep their
  evidence and owner-specific boundaries; no upstream investigation or submission.
- ScrollBar warnings, historical Haruna crash and Haruna Fusion hover
  are deferred, non-blocking historical findings with unresolved ownership.
  Owned Settings Weather hover was separately repaired and accepted under UQC-220.
  Reopen only for a concrete recurrence blocking required functionality or final
  acceptance. Tokodon chevron deferral remains unchanged.
- Haruna painted controls/explicit Fusion fallback, Kirigami composition and
  application-owned surfaces are explicit compatibility boundaries. C02–C05
  external/preference dispositions remain in the dated Batch 3 findings.
- Third-party scope is logged out; account/network-dependent surfaces are outside
  accepted coverage. Package-manager interaction is read-only. AI providers and
  title generation remain disabled; no requests or authorization flows.
- Settings/AI layout follow-ups L01/L02 are outside this initiative. G07 windowed
  reproduction is historical, outside the intended fullscreen greeter scenario.

## Previous execution and evidence — 2026-09-16

Previous released kit: `/tmp/holonight-uqc201-final-yn9_fquf` (historical).
Private build/log root: `.cache/holonight-uqc201-final-yn9_fquf/`.
Installed checks, collector verification, 267 hashes and exact-prefix archive
restoration passed; READY was included in the archive. Existing-path restoration refusal also passes.
Preparation uses the existing guided-session/application and authentication
helpers. The [original short handoff](BATCH8-HANDOFF.md) is retained as completed provenance.
The fresh-kit [AI runs](BATCH8-AI.md) are reviewed: scoped interaction/main-window
checks accepted, Fusion Settings palette P03 open.

All twelve submodule HEADs were clean, matched gitlinks and matched canonical
origin/main on 2026-09-16. The full revisions are retained in `revisions.json`.
The provider documentation closure was published before its pin changed.

Observed packages: Haruna 1.8.1-2; NeoChat/Tokodon 26.08.1-1;
hyprpolkitagent 0.1.3-10; qt6-base 6.11.2-3; qt6-declarative 6.11.2-2;
Kirigami 6.30.0-1; kirigami-addons 1.13.1-1; Hyprland 0.56.2-3;
Sway 1:1.12-4; greetd 0.10.3-2; Cage 0.3.1-1.

Initial configuration test attempt could not bind its private D-Bus socket in the
command sandbox. The retry runs outside that command sandbox while preserving
the disposable HOME/XDG/private-bus and host-provider mount isolation. Retain the
failed attempt; it is not a product failure or a passing test.

## Later human-operated batches

Review each batch's evidence before giving the next. Never automate pointer,
focus or credential entry. Successful authentication and real pre-session checks
remain required; no privileged launch has been requested or performed yet.

Before the shipped-service batch, inspect the disposable user's existing manager
environment and unit state, then prepare exact activation and restoration commands
for that state. Do not replace this with a transient unit or change the main user.

Before the pre-session batch, check VT2 availability and the separate socket,
generate a temporary greetd configuration pointing at this kit's installed
`holonight-greeter-session`, and isolate greeter state/configuration. Preserve the
primary greetd configuration/service. Use the existing stop/restore-getty trap
procedure and prepare exact cleanup before requesting the privileged launch.
The repository `task live:test` defaults to the host-installed launcher; invoking
it unchanged would not prove this kit's pinned implementation.

## Fresh automated results — 2026-09-16

All configured builds and installs pass. Focused checks preceded full suites.
`run.py` in the private evidence directory records exact configure/build/install
and isolated CTest commands; `results.jsonl` records exits and elapsed seconds.
The initial sandbox socket failure is recorded as exit 1 before the passing retry.

| Component | Full result |
|---|---|
| Configuration | 2/2 |
| System services | 2/2 |
| Standalone shell configuration | Build/install pass |
| Provider, with examples/gallery/Wayland | 85/85; Qt 5 discovery probes disabled (outside scope) |
| Appearance adapters | 6/6 |
| Shell | 1175/1175, serial; includes launch/deployment negatives |
| Settings | 53/53, serial |
| AI | 713 executed passes; one opt-in real-credential test skipped |
| Package-manager | 98/98 |
| Greeter | 8/8 |

Provider installed-package acceptance includes the explicit competing-style and
Basic fallback contracts; shell launch acceptance checks 45 build/relocated modes
and missing style qmldir/Core/Controls diagnostics with empty authentication
protocol output. Provider and all participating application import-policy checks
and fixtures pass in their suites. The shared contracts remain compatible at the
pins: runtime-selected namespaced Controls, overridable embedded defaults,
Core/composite APIs and executable-relative installed discovery.

`verify-rendering-kit.py KIT --logs WORK/runtime --diagnostics` passed all twenty
bounded offscreen processes (Haruna, NeoChat, Tokodon, Settings, AI × both styles
× DPR 1/1.25), inside the private-bus/host-provider mask. Results retain executable
and log hashes, staged mappings, created origin markers, measured DPR and exits.
These checks establish loading/measurement readiness, not human interaction or
unopened-page acceptance. No deferred diagnostic investigation was performed.

`python3 tests/test_guided_app.py`: 14/14; `bash scripts/install.sh --check`: pass;
`reuse --no-multiprocessing lint`: 104/104; new documentation links/anchors,
restoration-helper Python syntax and `git diff --check`: pass.


All 24 `extra.py` command groups pass (`extra-results.jsonl`): AI/package-manager/
greeter build and installed four-selector matrices (24 launches), four installed
Settings selectors, eight installed provider demo/gallery selectors, both AI
59-test selections, both package-manager 13-test selections and fractional
provider composites under both styles. Installed consumer checkers reject the
integration build root. CMake cache inspection confirms every resolved HoloNight
package directory belongs to the fresh prefix. Installer fixtures pass 8/8.


## Previous immutable kit release — 2026-09-16

Released `/tmp/holonight-uqc201-final-yn9_fquf` with 267 verified file hashes.
Archive: `.cache/holonight-uqc201-final-yn9_fquf/holonight-uqc201-final-yn9_fquf.tar.gz`.
SHA-256: `06596692118f1bccba18f1932c711dcfe4b7bd602f0bd3f25712060145d4dfb9`.
The original pre-restoration directory is preserved beside it with suffix
`-before-restore`. Both are immutable release evidence; do not edit either.

Exact-prefix restoration and repeat-existing-path refusal (exit 2) passed;
logs are `logs/restoration.log` and `logs/restoration-refusal.log`. The existing
helper's accepted name pattern now includes `uqc201-final`; extraction/hash and
no-overwrite behavior are unchanged. Sources remained clean at the recorded pins,
and package versions matched again immediately before release.

If the kit path is absent, from the umbrella root:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc201-final-yn9_fquf/holonight-uqc201-final-yn9_fquf.tar.gz
```

The first two-run handoff is [accepted](FINDINGS.md#batch-8-neochat-sway-acceptance--2026-09-16).
Tokodon is also [accepted](FINDINGS.md#batch-8-tokodon-sway-acceptance--2026-09-16).
Haruna is also [accepted](FINDINGS.md#batch-8-haruna-sway-acceptance--2026-09-16).
Package-manager is [accepted](FINDINGS.md#batch-8-package-manager-sway-acceptance--2026-09-17).
Submitted Settings runs measured 1.25; [accepted fractional results and local follow-up](FINDINGS.md#batch-8-settings-fractional-results-and-composition-disposition--2026-09-17)
did not fill scale 1. The subsequent scale-1 runs reported [Weather defects](FINDINGS.md#settings-weather-failures-and-uqc-220-ownership--2026-09-17).
The subsequent [UQC-220 acceptance](FINDINGS.md#uqc-220-fractional-repair-acceptance--2026-09-17)
closes the Weather repair at scale 1 and 1.25. Broader Settings scale-1 coverage
beyond the focused Weather checks remains pending. UQC-201 remains In Progress and the
initiative Accepted; successful authentication and real pre-session operation are
not waived or claimed by this release.


## Manual coverage accepted after release

| Application / coverage | Compositor | Style / measured DPR | Status and evidence |
|---|---|---|---|
| NeoChat logged-out text/focus, settings selectors/scrolling and palette round trip | Sway | HoloNight and Fusion / 1.25 | Accepted; [two reviewed runs](FINDINGS.md#batch-8-neochat-sway-acceptance--2026-09-16). Created ComboBox origins and application/composite boundaries recorded; diagnostics retained without a functional blocker. |
| Tokodon logged-out text/focus, settings selectors/scrolling and palette round trip | Sway | HoloNight and Fusion / 1.25 | Accepted; [two reviewed runs](FINDINGS.md#batch-8-tokodon-sway-acceptance--2026-09-16). ComboBox origins, observed Basic fallback and narrower Fusion trace recorded; no functional blocker. |
| Haruna local playback/menus, settings editing/navigation/selectors and palette round trip | Sway | HoloNight and Fusion / 1.25 | Accepted; [two reviewed runs](FINDINGS.md#batch-8-haruna-sway-acceptance--2026-09-16). Provider/Fusion origins and application/fallback boundaries recorded. |
| Package-manager read-only search/category/focus, details/scrolling/navigation and popups | Sway | Embedded default and Fusion / 1.25 | Accepted; [two reviewed runs](FINDINGS.md#batch-8-package-manager-sway-acceptance--2026-09-17). Unset default selectors, staged executable and standard/application/composite origins verified. |
| Settings navigation/editing/selectors, with non-blocking Appearance/Weather composition difference | Sway | Embedded default and Fusion / 1.25 | [Reviewed results and user disposition](FINDINGS.md#batch-8-settings-fractional-results-and-composition-disposition--2026-09-17); broader scale-1 coverage remains pending beyond accepted UQC-220 Weather checks. Separate Settings-local composition SDD; no composition repair. |
| Settings Weather row centering and Fusion hover (including accepted subtle closed-button feedback) | Sway | Embedded default and Fusion / 1 and 1.25 | Accepted; [UQC-220 review](FINDINGS.md#uqc-220-fractional-repair-acceptance--2026-09-17). Focused repair scope only; broader scale-1 coverage stays pending. |
| AI offline editing/navigation, reachable selectors/popups, scrolling and main-window palette round trip | Sway | Embedded default and Fusion / 1.25 | [Accepted scoped results](FINDINGS.md#batch-8-ai-sway-evidence-review--2026-09-17); Fusion Settings TextField/numeric/ComboBox backgrounds fail palette changes (P03), with [repair Done; reviewed recheck retains instability and construction gap](FINDINGS.md#p03-human-evidence-review--2026-09-18). |

This closes those scoped cells only. Other application/compositor/activation,
successful authentication and real pre-session gates remain pending.


Settings status correction, 2026-09-17: [completed UQC-220 acceptance](FINDINGS.md#uqc-220-fractional-repair-acceptance--2026-09-17)
supersedes the Weather repair-pending claims. Row centering and popup hover are
accepted at both scales; fractional review also resolves the conditional closed
Fusion hover acceptance. Broader Settings coverage gaps, composition disposition,
other accepted application cells and historical deferrals stand. The repair kit
close-binding deviation remains documented in that evidence.
