# UQC-201 automated integration evidence

Verification date: 2026-09-09. Status: **In Progress**. Initiative: **Accepted**.
Manual acceptance remains pending in [the user-operated kit](MANUAL.md).
UQC-202/UQC-203 repairs and fresh passing gate rechecks are appended below;
the original failures remain as historical evidence.

## Baseline and isolation

Start baseline: `a26b4e537ea8105a991ec5f48e06e9fe7565dd72`.
Readiness checkpoint: `67a72a65cd253b73f96c8b5a8e1226b9c6c1d106`.
The checkpoint's gitlinks are authoritative. All submodules were clean and their
HEADs matched canonical origin/main (`git ls-remote`) before verification.
The final read-only recheck on 2026-09-09 confirms all twelve submodule HEADs
still match canonical main and the authoritative gitlinks; every submodule is
clean. Final document links, umbrella REUSE (43/43) and `git diff --check` pass.
Only package-manager's two byte-preserved mockups changed its pin; see the
[ledger](TASKS.md#uqc-201-readiness-and-assignment--2026-09-09).

Builds use `.cache/uqc201/build/<component>` and shared prefix
`.cache/uqc201/prefix`, configured directly from the pinned source trees. No
consumer Taskfile dependency preparation runs. Configuration and system services
are verified first, followed by standalone shell configuration, provider,
appearance adapters, shell, settings, AI, package-manager and greeter.

Tests run through the shell's disposable HOME/XDG/private-bus helper, inside a
mount namespace hiding `/usr/lib/qt6/qml/Holonight` and host native HoloNight
configuration libraries. No live desktop activation, authentication, system
installation or package transaction runs. CMake installs target only private
prefixes. Test fixture directories are disposable, never user configuration.

The initial `.source-install/uqc201` provider run passed focused checks and 58/59
full entries. `holonight_package_install_test` failed because the probe's maps
filter checks `.so` anywhere in a path and includes the executable under
`.source-install`; Python then rejects it as a host/build library. Fresh builds
under `.cache/uqc201` avoid that harness path limitation without editing product
or test source. The initial logs remain in `.source-install/uqc201/logs`.
The fresh-path installed-example check initially lacked `LD_LIBRARY_PATH` for
the staged configuration library while host libraries were hidden (exit 127).
The verification environment now includes `.cache/uqc201/prefix/lib`; QML
discovery remains fixture-controlled. Its first log is retained as
`qt-full-before-native-path.log`.
A sandbox attempt also failed to create a private D-Bus socket; the same isolated
checks were rerun outside the command sandbox. REUSE required the same adjustment
for its worker-process socket. These are recorded failures, not test passes.

The first parallel shell full-suite run passed 1150/1157 entries. Seven
NetworkManager cases competed for the same fake service name on the private
session bus. All eight backend cases pass serially; the complete suite is rerun
serially to match the repository acceptance workflow. Parallel-run logs are
retained as `shell-full-parallel.log` and `shell-focused-parallel.log`.

The historical discovery `audit/check-fixture.py` was also attempted against the
new provider. It expects Basic ApplicationWindow/Label/ToolButton from discovery
and rejects the now-required HoloNight ApplicationWindow. It is not a current
acceptance gate. Use the current provider installed-package and example-startup
fixtures for this kit; the historical script was left unchanged. Its attempted
output is `audit-fixture.log`. Full provider acceptance already covers the new
control origins and fallback contract.

Shell static analysis initially lacked `compile_commands.json` because direct
CMake configuration had not enabled its export (normally supplied by Taskfile).
Reconfiguration with `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` supplies the database;
static analysis uses four workers and the repository's GCC-flag filtering.

## Versions observed locally

| Package | Version |
|---|---|
| Haruna | 1.8.1-2 |
| NeoChat | 26.08.0-1 |
| Tokodon | 26.08.0-1 |
| hyprpolkitagent (Qt) | 0.1.3-10 |
| qt6-base | 6.11.2-3 |
| qt6-declarative | 6.11.2-1 |
| CMake | 4.4.3-2 |
| GCC | 16.2.1+r23+gd564253eb6c8-1 |
| clang | 22.1.8-1 |
| REUSE | 6.2.0-2 |

Collected with `pacman -Q` for those package names. This is local package evidence,
not a claim about current upstream releases. Private patchelf is obtained with
`UV_CACHE_DIR=/tmp/uqc201-uv-cache uv run --with patchelf --no-project`; no system
package is installed.

## Fresh results

| Component | Fresh full suite | Notes |
|---|---|---|
| Configuration | 2/2 pass, 0.65 s | Includes installed consumer |
| System services | 2/2 pass, 9.62 s | Includes installed consumer |
| Standalone shell configuration | Build/install pass | Shared prerequisite |
| Qt provider | 59/59 pass, 44.59 s | 15 focused entries pass; ten isolated cases, installed palettes/composites/examples; Qt 5 probes outside scope |
| Appearance adapters | 6/6 pass, 0.05 s | Shared staged provider/configuration |
| Shell | 1157/1157 pass, 226.88 s | Serial full suite; 45 launch modes and three missing-module cases; both styles/DPR and fake authentication |
| Settings | 53/53 pass, 43.38 s | Includes controls, activation and startup fixtures |
| AI | 713 executed passes, one opt-in real-credential skip | Full 714-entry suite; no credential interaction |
| Package-manager | 98/98 pass, 9.50 s | Both compiled runtime styles and import-policy fixtures |
| Greeter | 8/8 pass, 6.39 s | Both styles, DPR 1/1.25, fake authentication and scaled popup geometry |

Build and installed selector matrices pass for AI, package-manager and greeter
(four selectors each per location, 24 launches total), as do all four installed
Settings selectors. Installed checks reject the integration build root while
requiring staged implementation/plugin origins. Both package-manager 13-test
source selections pass. Provider composite checks pass under both styles with
`QT_SCALE_FACTOR=1.25`. The copied manual kit's actual demo and gallery each pass
all four current startup modes (eight relocated launches) with host provider
modules hidden.

AI's 59-test Holonight selection passes. Its Fusion selection passes 58/59:
`ChatComposerActionsQml.PreservesDesktopAndCompactPresentation` fails at
`tests/qml/test_chat_composer_actions.cpp:69–70`: attachment implicit height is
24, context/tools are 25. A fresh, serial focused recheck fails identically.
The QML uses an icon-only standard Button next to labeled standard Buttons;
no loading or style-property error is reported. This is reproducible acceptance
failure, not a claimed transient or a reason to silently weaken the assertion.
UQC-203 must settle the geometry contract and provide a separate published
correction before final integration. No AI source or tests changed in this run.

All participating static checks pass: format, QML lint, provider/shell/Settings/AI/
package-manager full clang-tidy (four workers), greeter owned-C++ analysis and
metadata, consumer qmltypes, and shell architecture boundaries. QML lint emits
existing advisories (including provider unqualified access/semanticRadius and
shell AudioService metadata); successful exit is not a zero-warning claim.
Shell tidy's first retry from the umbrella directory reported “No checks enabled”;
running from the shell repository selects its intended configuration and passes
234 translation units. This working-directory correction and the earlier missing
compile database are retained in the private logs.

REUSE passes with `--no-multiprocessing lint` in the umbrella, configuration,
system-services, provider, appearance-adapters, shell, Settings, AI,
package-manager and greeter. No license metadata or mockup bytes changed.
See [exact commands and outcomes](COMMANDS.md).
Third-party probes used the pinned provider with host QML/native HoloNight
modules hidden, empty HOME/XDG, unavailable system/audio endpoints, private
session buses without activation services, offscreen/software rendering and a
12-second bound. All three exited 124 at the bound after loading the staged
Quick Controls style, Core and impl plugins. A second pass explicitly enabled
`QT_QPA_PLATFORMTHEME=holonight` and confirmed the staged platform-theme plugin
as well. Haruna also loaded Fusion. These establish bounded loading, not visible
surface or interaction acceptance. No authentication process was launched.

| Application | Style-only raw evidence | Platform-theme raw evidence |
|---|---|---|
| Haruna | `/tmp/uqc-audit-d3ftreus` | `/tmp/uqc-audit-o7_ap6fu` |
| NeoChat | `/tmp/uqc-audit-p0ur_8ps` | `/tmp/uqc-audit-nqt51_ni` |
| Tokodon | `/tmp/uqc-audit-yp29b23m` | `/tmp/uqc-audit-ibreaq84` |

Each directory contains executable hash, command, timestamp, selected environment
and exit status in `metadata.json`, plus `launch.log`. Selected component/plugin
lines are retained as `<app>-selected-evidence.log` below the integration logs.
No QQmlApplicationEngine failure, TypeError, ReferenceError or assignment failure
was found in the first-pass logs; other private-service/platform diagnostics are
not a zero-warning claim. Human classification remains pending.

Raw private logs are under `.cache/uqc201/logs`, with commands, exit codes and
elapsed seconds in `.cache/uqc201/results.jsonl`. Historical repository acceptance
records are references only; they do not fill unexecuted rows here.

## Installer gate and manual kit

`bash scripts/install.sh --check` exits 1: `Missing required Arch packages:
qt6-wayland`. `pacman -Q qt6-wayland` confirms that package is absent, while
`pacman -Qo /usr/lib/cmake/Qt6WaylandClient/Qt6WaylandClientConfig.cmake` reports
`qt6-base 6.11.2-3` owns the required installed metadata. All builds already
resolved Qt Wayland successfully. This is an installer package-assumption failure,
not evidence that Qt Wayland libraries are unavailable. No package is installed
and no installer code is changed. UQC-202 records the separate correction; the
preflight gate remains failed. Checks after its early package failure (including
its account check) are not claimed to have passed.

The self-contained manual kit is `/tmp/holonight-uqc201-manual` (409 MiB at
preparation), containing the staged prefix, unchanged guarded authentication
helpers, standalone Hyprland/Sway configs, README, manual matrix, revision/version
record and SHA-256 inventory. All 239 copied regular prefix files match their
source bytes. It is user-readable outside the private workspace and temporary;
regenerate after cleanup or a Qt update. Python syntax and terminal shell syntax
pass. `Hyprland --verify-config --config .../hyprland.conf` passes;
`WLR_BACKENDS=headless WLR_RENDERER=pixman sway --validate --config .../sway.conf`
passes without starting a session. The initial Sway validation attempted the
inherited Wayland backend and failed to connect inside the sandbox; the final
headless validation avoids the active desktop. `auth-test.py preflight` refuses
the current user with the expected tux-only message, before any authentication
operation. User login, registration and cancellation remain unchecked.

The private workspace's `/home/andrii` parent is mode 0700. The copied prefix
supports relocated terminal execution, but its D-Bus service Exec paths retain
the original configured workspace prefix. A tux activation test therefore needs
a separately configured accessible prefix; this is an explicit manual prerequisite,
not a claimed activation pass. Do not weaken home permissions or alter existing
activation managers. The current shell launch matrix independently verifies
relocated bin/libexec discovery in a private test environment.

## UQC-202/UQC-203 gate recheck — 2026-09-09

Published handoff checkpoint: `730be066e78c4cf5c0d65f3f78fb669f5fcbb229`.
The authoritative gitlinks at that checkpoint are AI
`7e25e78cc7fb33aa63ed480bc3f328a65e04ca0c`, provider
`00e6e208b6c9b30d89b66ef3aeb4ef8175050764`, and configuration
`fe69a59e6b73167fd5349223a4d265d75386c139`. Other pins are unchanged.
The AI handoff is documentation-only above green implementation `11b021a`;
canonical publication was confirmed before pinning. UQC-202's implementation
`8af91cb` is published and green in installer CI/licensing. AI implementation
CI 34390403485 and licensing 34390403390 pass; details and failed intermediate
attempts are in the [local SDD](../../../holonight-ai/docs/sdd/unified-qtquick-controls/UQC-203.md).

| Rechecked gate | Fresh result |
|---|---|
| `bash scripts/install.sh --check` | Exit 0, Preflight passed; includes real Qt 6.11.2 WaylandClient/scanner configure probe and unchanged distribution/compiler/account/gitlink checks |
| Explicit Fusion QML selection | Exit 0, 59/59 pass, 15.37 s; includes formerly failing composer geometry |
| Submodule working trees | `git submodule foreach --quiet 'git status --porcelain'` produces no output; every submodule clean |
| Umbrella REUSE and whitespace | 47/47 source/document files licensed; `git diff --check` passes |

The Fusion check uses the same private integration build/prefix, disposable
HOME/XDG/private bus, offscreen rendering and hidden host HoloNight discovery.
Commands are appended to [COMMANDS.md](COMMANDS.md); raw local outputs are in
ignored `.cache/uqc203/logs/uqc201-installer-final.log` and
`.cache/uqc203/logs/uqc201-fusion-final.log`. No system installation, package
transaction, live authentication or active-desktop automation occurred.

These fresh passes resolve the two automated findings above without erasing the
original failures. UQC-202 and UQC-203 are Done. UQC-201 stays **In Progress** and
the initiative stays **Accepted**. This is a targeted gate recheck, not final
ecosystem integration. MANUAL.md, AUTHENTICATION.md and the initiative's manual
checklists are unchanged; all human Hyprland/Sway/authentication gates remain open.

## UQC-201 accessible guided preparation — 2026-09-09

Baseline: `7fcc8bb48a451185b9412950ac7f651ee75975c7`. All twelve submodules
remain clean and match that baseline's gitlinks and canonical `origin/main`,
rechecked with `git ls-remote` before and after preparation. No pins or product
files changed. Installer `bash scripts/install.sh --check` passes. Installed
versions remain those above; compositor packages are Hyprland `0.56.2-2` and
Sway `1:1.12-4` (package epoch included).

The new kit is `/tmp/holonight-uqc201-8r1jtlln` (410 MiB), configured directly at
`/tmp/holonight-uqc201-8r1jtlln/prefix`; no service paths were patched after install.
Fresh private build directories and raw results are under
`.cache/uqc201-guided-qht3_tjs`. The old kits, build directories and evidence remain.
Dependency order/options match the recorded integration recipe, including the
pinned AI repair; no consumer Taskfile dependency preparation ran. The installed
prefix is populated before each component's focused/full checks. Shell and
Settings tests run serially, inside disposable HOME/XDG/private-bus fixtures with
host HoloNight QML/configuration libraries hidden. No live authentication,
active-desktop activation, AI requests or package transactions ran.

| Component | Fresh full result | Harness seconds |
|---|---|---|
| config | 2/2 pass | 0.77 |
| system-services | 2/2 pass | 9.63 |
| qt | 59/59 pass | 42.17 |
| appearance-adapters | 6/6 pass | 0.11 |
| shell | 1157/1157 pass | 228.60 |
| settings | 53/53 pass | 42.91 |
| ai | 713 pass; one opt-in real-credential skip | 23.79 |
| pkg-manager | 98/98 pass | 8.40 |
| greeter | 8/8 pass | 5.44 |

Standalone shell configuration builds/installs successfully. Focused selections
pass. Build and installed AI/package-manager/greeter selector matrices pass all
24 launches, as do four installed Settings modes and eight installed provider
example modes. AI's explicit Holonight and Fusion selections each pass 59/59;
Fusion CTest time is 15.37 seconds. Both package-manager source selections and
provider composites at scale 1.25 pass. Earlier source static-analysis evidence
remains applicable to the unchanged pins; this preparation reruns runtime suites,
not all clang-tidy jobs.

All 18 unique installed ELF files resolve dependencies without missing libraries
or workspace paths. All seven installed desktop/D-Bus/systemd/session metadata
files resolve executable paths; Settings desktop-file validation passes. Prefix
permissions permit other-user read/traversal and its symlinks remain inside the
prefix. `SHA256SUMS` records 239 regular installed files. The service `Exec` paths
now point directly to the accessible prefix, resolving the earlier relocated-kit
prerequisite; actual activation in tux remains a manual gate.

Haruna, NeoChat and Tokodon each reach the expected 12-second probe limit (exit
124), loading staged provider/platform-theme plugins. Selected load-line counts
are 5, 10 and 5 respectively; no TypeError, ReferenceError or failed-component
marker was found. This is bounded loading evidence, not visible acceptance.
Raw runs are `/tmp/uqc-audit-g4ot_2h3`, `/tmp/uqc-audit-6alompu5` and
`/tmp/uqc-audit-yffp0qd1`; selected plugin lines stay in the private build logs.

Hyprland configuration verification passes; Sway headless validation passes.
Python syntax, terminal shell syntax and the helpers' current-user refusals pass
(expected refusal exits: session/auth 1, application helper 2). A freshly generated
helper kit reproduces all five authentication/terminal files byte for byte.
The owned-agent adaptation retains session/registration/cancellation guards and
uses recorded child start ticks because the frontend is intentionally
non-dumpable. A harmless non-authentication child confirms start ticks remain
readable/stable while executable inspection is denied. Live registration remains
unverified. No agent or challenge was launched by these preparation helpers.

Retained failed attempts: SSH inside the sandbox exits 128 on its system SSH
configuration access; private test-bus startup fails for initial config/example
checks (exit 1); initial Sway validation cannot create its socket and exits 134.
Approved retries outside the command sandbox pass, with headless/offscreen/private
bus isolation retained. Failed config/example logs have `-sandbox-failure`
suffixes; result records preserve both attempts. These are environment failures,
not silent test passes or product work packages.

[GUIDED.md](GUIDED.md) defines one reviewed batch at a time, Hyprland before a
fresh Sway login. The real test login owns the compositor; discovery is set before
the new test bus starts. Disposable application configuration and a generated
Haruna clip are included. Owned defaults, explicit Fusion and Qt scale 1/1.25
are selectable. Systemd environment imports require the separately guided tux-only
review; no launcher modifies a manager automatically. AI has a shipped D-Bus
service but no desktop entry; package-manager has neither. Haruna has no D-Bus
service; NeoChat and Tokodon do. These unavailable routes are N/A with metadata
and CMake install-rule evidence, not missing visual results.

Umbrella REUSE (52/52), local documentation links, Python syntax and whitespace
pass. The preparation checkpoint retains initiative **Accepted** and UQC-201
**In Progress**. Every user-operated observation remains pending; greeter demo
checks do not resolve real pre-session acceptance. The next action is the small
[Hyprland/Settings batch](GUIDED.md#batch-1-hyprland-login-and-settings-default).
