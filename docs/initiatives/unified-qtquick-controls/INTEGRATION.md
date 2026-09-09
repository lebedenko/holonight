# UQC-201 automated integration evidence

Verification date: 2026-09-09. Status: **In Progress**. Initiative: **Accepted**.
Manual acceptance remains pending in [the user-operated kit](MANUAL.md).

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
