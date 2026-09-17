# Batch 8 post-repair revalidation — 2026-09-17

Baseline: umbrella `c16b164d0cb01fd36ae391415e0350d36c234922`; provider
`7e101bd23661f21efe95cd11dad092069c68601d`. No product changes or gitlink updates.
UQC-220 focused manual repair acceptance is complete. This iteration refreshes
affected automated integration and prepares [exactly two AI runs](BATCH8-AI.md).
UQC-201 remains In Progress; initiative Accepted. No manual application runs or
privileged acceptance procedures belong to this iteration.

## Source and build provenance

All twelve checkouts were clean, matched the baseline's gitlinks and matched
canonical `origin/main` before building. `git submodule foreach --quiet
'git status --porcelain; git remote get-url origin; git ls-remote origin
refs/heads/main'` verified publication. The sandbox's SSH configuration access
failed initially; the elevated retry succeeded. No newer revision was adopted.
Full revisions are in kit `revisions.json`; the umbrella revision is in
`BASELINE.txt`.

Fresh candidate: `/tmp/holonight-uqc201-final-dyxe1nl_`.
Fresh build/evidence root: `.cache/holonight-uqc201-final-dyxe1nl_/`.
The retained Batch 8 `run.py`, `extra.py` and `release.py` recipes were adapted to
these new paths. The successful-command cache was removed. No old build,
installation or released-kit contents were reused. Existing preparation,
collection and restoration helpers remain the basis of the kit.

Commands, options, exits and timings are recorded in `results.jsonl`,
`repair-results.jsonl`, `extra-results.jsonl`, `checks-results.jsonl` and their
named `logs/` files. `run.py` configures Debug/Ninja builds with tests and provider
examples/gallery, builds with six jobs, and installs into the fresh prefix.
Test processes run with disposable HOME/XDG/private D-Bus and host HoloNight
QML/shared libraries hidden through bubblewrap. Shell and Settings run serially.
`resolved-packages.txt` verifies every resolved HoloNight CMake package belongs
to that prefix. Runtime mappings verify actual loaded origins.

The dependency order is configuration → system services → standalone shell
configuration → provider → appearance adapters → shell → Settings → AI →
package-manager → greeter. Unchanged earlier prerequisite results remain valid
only with their revisions and package inventory in the previous
`holonight-uqc201-final-yn9_fquf` archive; this run also rebuilds and retests those
prerequisites, so current results do not depend on the previous success cache.

## Failures and retries

- Initial configuration test launch failed to bind the private D-Bus socket in
  the command sandbox. `logs/config-full-sandbox-failure.log` and the first exit-1
  result are retained. Elevated execution preserved the same isolation and passed.
- The first custom Controls matrix accidentally ran the entire composite binary,
  including Core-only isolation after loading Controls. Its assertion correctly
  detected loaded style modules. The retained
  `logs/controls-Holonight-1-unfiltered-failure.log` records 184/185 passes.
  The corrected matrix uses the repository's `composite_filter`; Core isolation
  runs in its separately registered process in the full suite. This was a harness
  invocation error, not a new product blocker.
- Initial observer population assumed a standalone rendering module build target.
  That target does not exist; the retained helper's `g++ -std=c++23 -shared -fPIC`
  recipe builds it from the pinned observer source instead. The palette observer
  is copied from the fresh provider build. No released kit was changed.
- The first AI palette assertion assumed that changing the appearance file updates
  `QGuiApplication::palette()`. Pinned platform-theme code initializes that palette
  once; the scene's appearance reader updates owned colors independently. The
  retained `ai-palette-default-global-assumption/` trace proves workspace background
  `#ff0c1118` → `#ffe7eef5` → `#ff0c1118`, while the global/window palette roles
  remain unchanged. The corrected helper check measures this scene transition.
  This is a verification-scope correction, not evidence that every native control
  switches palettes. Manual review must distinguish owned surfaces from native
  Fusion controls; no speculative product repair or renewed visual acceptance.

## Verification and release

All dependency-order builds and installations pass. Focused repair checks ran
before the provider full suite: popup label centering, desktop hover policy,
the registered composite filter under both styles at DPR 1/1.25, and six private
Wayland theme/hover combinations. Explicit hover disable remains effective.
The full suite runs Core isolation separately and passes.

| Component | Fresh full result |
|---|---|
| Configuration | 2/2 |
| System services | 2/2 |
| Standalone shell configuration | Build/install pass |
| Provider with examples/gallery/Wayland | 85/85; Qt 5 probes disabled, outside scope |
| Appearance adapters | 6/6 |
| Shell | 1175/1175, including 45 build/relocated launch cases and deployment negatives |
| Settings | 53/53 |
| AI | 713 executed passes; one opt-in real-credential test skipped |
| Package-manager | 98/98 |
| Greeter | 8/8 |

Provider package acceptance covers explicit competing styles and Basic fallback;
consumer import-policy checks/fixtures pass in their suites. Shell missing style
qmldir/Core/Controls fixtures retain deployment diagnostics and empty authentication
protocol output. The unchanged contracts remain compatible: runtime-selected
namespaced Controls, overridable embedded defaults, Core/composite APIs and
executable-relative installed discovery.

Collector tests pass 14/14; installer fixtures pass 8/8 and installer `--check`
passes. All 24 additional command groups in `extra-results.jsonl` pass:
AI/package-manager/greeter build and installed four-selector matrices, four
installed Settings selectors, eight installed provider example/gallery selectors,
both AI 59-test selections, both package-manager 13-test selections, and provider
fractional composites under both styles. Installed consumer checks reject the
integration build root.

Both bounded runtime matrices pass 20/20: Haruna, NeoChat, Tokodon, Settings and
AI × HoloNight/Fusion × DPR 1/1.25, first with rendering observation and separately
with palette observation. Actual DPR, staged mappings/control-origin markers,
log/executable hashes and process outcomes are verified. Processes are terminated
after bounded inspection (SIGTERM or handled exit 0), not recorded as normal
manual closes. No forced kill or premature exit occurred. AI runtime profiles
have all providers and title generation disabled. These checks establish loading
and observer readiness, not unopened-page or visual acceptance.

The AI palette helper passes for embedded default and explicit Fusion at measured
DPR 1.25. Both workspace backgrounds change `#ff0c1118` → `#ffe7eef5` → `#ff0c1118`;
32/33 created-object origins are recorded respectively. Default records 612 palette
events; Fusion records none, despite the scene color transition. Bootstrap
application/window palette roles remain static. Closed-run refusal passes in both
cases. These are explicit palette-scope limits for manual review, not uniform
native-control transition acceptance. Both bounded processes terminate with -15.
Terminal syntax, Python parsing and headless `sway --validate` pass.
Umbrella documentation links/anchors, handoff shell syntax, `git diff --check`
and `reuse --no-multiprocessing lint` (112/112 files) pass.

Released **READY**: `/tmp/holonight-uqc201-final-dyxe1nl_`, **287 file hashes**.
Exact-prefix restoration verifies every hash; restoring again refuses the existing
path with exit 2. Logs: `logs/restoration.log`, `logs/restoration-refusal.log`.
The original tree is preserved beside the restored kit with `-before-restore`.
All submodules remain clean at the recorded pins and package inventory was checked
again immediately before hashing. Neither released tree may be modified.

Archive: `.cache/holonight-uqc201-final-dyxe1nl_/holonight-uqc201-final-dyxe1nl_.tar.gz`.
SHA-256: `b63db86b9821ae6661a4400689adac7f15aa992cbd9ed5b14b24bdb0c85676b8`.
If the kit is absent, restore it from the umbrella root:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc201-final-dyxe1nl_/holonight-uqc201-final-dyxe1nl_.tar.gz
```

The generic restoration helper prints a historical Hyprland suggestion for this
kit name family; use the explicit **Sway** launch in [the AI handoff](BATCH8-AI.md).
Do not launch a manual application in this preparation iteration.

Package inventory (unchanged from the prior kit for the twelve shared entries):
Haruna 1.8.1-2; NeoChat/Tokodon 26.08.1-1; hyprpolkitagent 0.1.3-10;
qt6-base 6.11.2-3; qt6-declarative 6.11.2-2; Kirigami 6.30.0-1;
kirigami-addons 1.13.1-1; Hyprland 0.56.2-3; Sway 1:1.12-4;
greetd 0.10.3-2; Cage 0.3.1-1. Toolchain: CMake 4.4.3-2,
GCC 16.2.1+r23+gd564253eb6c8-1. Full inventory: kit `PROVIDER.txt`;
prior-package comparison: `retained-package-provenance.json`.

## Preserved boundaries

Weather row centering and popup hover are accepted at scales 1 and 1.25;
fractional review also accepted native Fusion's subtle closed-button hover.
Broader Settings scale-1 coverage is still pending. Earlier NeoChat, Tokodon,
Haruna and package-manager acceptances and external/deferred findings stand.

The repair kit `holonight-uqc207-t9ao_81w` had the explicitly accepted single-file
`bindsym Mod4+Q kill` deviation during fractional manual review. Its original
archive and qualification remain unchanged. This fresh kit includes the existing
Sway close binding from `prepare-guided-kit.py` before hashing.

The two AI runs use only the palette observer and isolated offline profiles.
Automated loading/origin checks establish readiness, not renewed human acceptance.
Successful authentication, shipped-service activation, real pre-session greeter
operation and all other unresolved matrix cells remain pending. Review the two
returned AI runs before issuing another manual batch.
