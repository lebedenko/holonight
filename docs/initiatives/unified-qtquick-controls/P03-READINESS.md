# P03 focused repair readiness — 2026-09-17

## Current manual-session repair — 2026-09-18

Use `/tmp/holonight-uqc201-p03-xtndrklf` for the focused recheck. It derives from
`holonight-uqc201-p03-c_w7vh8n` at umbrella checkpoint `838e931`, with identical
product binaries/libraries and unchanged provider/repository pins and package
inventory. The original release below remains immutable historical evidence.

The manual launcher now binds host `/dev` with device access so GPU, input and
VT nodes are visible under normal user/logind permissions. Offscreen checks keep
the synthetic `/dev`; network isolation, private D-Bus, disposable profiles and
host HoloNight masks remain. Only the launcher path/device mask and preparation
recipe change; no application repair or rebuild is claimed.

Fresh namespace inspection confirms matching host device identities, an isolated
network namespace exposing only loopback, and hidden host modules/config library.
The first network probe incorrectly inspected host-mounted sysfs; its failure is
retained and the corrected socket API probe passes. These checks do not open GPU
or input devices, exercise logind seat acquisition, or prove real-VT startup.
The user must confirm Sway startup before either AI acceptance run.

Fresh offscreen AI workspace/helper checks cover both styles at measured DPR 1.25,
staged executable/library origins, palette transitions and helper refusal cases.
Historical full suites and provider checks remain labeled inherited evidence.
Collector, compositor configuration and terminal checks are retained in the new
kit's `session-repair-verification/` directory with the Python syntax-check script.
Documentation and Ruff outcomes are recorded below.
P03 open, UQC-222 Done, UQC-201 In Progress, initiative Accepted.

Replacement release: **880 verified file hashes**. Archive:
`.cache/holonight-uqc201-p03-xtndrklf/holonight-uqc201-p03-xtndrklf.tar.gz`.
SHA-256 `b3ad9b03d3a7ec0c1060b1617492dfe38cec702c29fb77c834f02d1ad2769b9e`.
Exact-prefix restoration passes; repeated restoration refuses overwrite (exit 2).
The original kit's 838 hashes still match. Collector 14/14, both AI helper styles,
device namespace, Sway configuration, terminal/Python syntax, Ruff and documentation
links/command syntax/whitespace pass. The initial command-sandbox device probe
could not see host GPUs; the host probe was run outside that sandbox. No live
compositor or pointer/focus interaction was automated.

If the replacement path is absent after a reboot, restore from the umbrella root:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc201-p03-xtndrklf/holonight-uqc201-p03-xtndrklf.tar.gz
```

The archive contains the pre-archive readiness snapshot; the final archive hash
and restoration outcomes are recorded here and in its matching `.cache` directory.

## Original release record (historical)

**READY — released and restoration verified on 2026-09-17.** All required
focused automated gates pass. P03 remains open for the two human checks.
Baseline umbrella `6f7af409a38b7a217fec38bf607e43446f86c07f`, published provider
`e94ceddbd3c0e4cb29e21bcdfd6758e3e4639f4f`. All twelve clean submodule HEADs
match authoritative gitlinks and canonical origin/main, confirmed by read-only
`git ls-remote` on 2026-09-17. No product source or pins change.

Fresh kit: `/tmp/holonight-uqc201-p03-c_w7vh8n`.
Build/evidence directory: `.cache/holonight-uqc201-p03-c_w7vh8n/`.
[Retained recipes](p03-kit/README.md) build and install configuration, system
services, shell configuration, provider, adapters, shell, Settings, AI,
package-manager and greeter in dependency order. Commands, exits and timing are
in `results.jsonl` and `focused-results.jsonl`; individual logs retain test counts.

Prior full-suite results are copied under `prior-evidence/`, with exact source
revisions and original package inventory from `/tmp/holonight-uqc201-final-dyxe1nl_`.
They are **prior evidence**, not fresh full-suite passes. All non-provider pins
and all previously listed package versions match. Provider repair verification
is fresh and focused. The complete current `pacman -Q` inventory is additionally
retained and must remain identical through release; drift blocks READY. Earlier
kits and archives remain immutable historical evidence.

All automated runtime checks use disposable HOME/XDG, private D-Bus, offscreen
software rendering and hidden host HoloNight modules/libraries/plugins. AI profiles
disable every provider and title generation. The staged matrix keeps Core-only
isolation separate from Controls-loaded processes. Installed startup checkers
verify staged origins and reject build paths. The new manual session also has a
disposable HOME and masks host HoloNight installations, with network isolation.

The first focused provider attempt failed before tests because the command sandbox
refused the bubblewrap network namespace. Its failed outcome is retained; retry
requires execution outside that command sandbox while keeping kit isolation.
This is harness evidence, not a product failure or passing test.

The actual AI workspace dark/light/dark round trip is recorded separately from
native-control acceptance. Ordinary startup does not instantiate the lazy AI
Settings window. Provider palette/background/pixel assertions and AI component
checks establish automated readiness; [two human Settings palette checks](P03-RECHECK.md)
remain required. No prior interaction/navigation/main-window checklist is repeated.

P03 remains open; UQC-222 Done; UQC-201 In Progress; initiative Accepted. No manual
application run, pointer/focus automation, privileged acceptance procedure or final
integration claim is part of this preparation.


## Focused verification

| Check | Result |
|---|---|
| Fresh configure/build/install, ten components | All pass, in dependency order |
| Provider registered window/Core | 5/5 pass |
| Provider registered palette/composite/Core/import policies | 33/33 pass |
| Provider installed-package acceptance | Pass, including isolated styles, both native-control styles and separate Core process |
| Staged UQC-222 matrix | 18 processes collected; shared-window palette/background/pixel and application-positive assertions pass |
| Retained external boundaries | Plain Window: 32 failures; provider-free Fusion: 8 failures; assertion exit 1 recorded separately from successful collection |
| AI runtime controls/import policy | 4/4 at each DPR 1 and 1.25; styles in separate processes |
| AI relevant QML/component selection | 59/59 in each of four style/DPR processes |
| Settings controls/import policy | 4/4 at each DPR 1 and 1.25; styles in separate processes |
| AI workspace/helper readiness | Both styles pass at measured DPR 1.25; workspace colors round-trip independently of Settings acceptance |
| Helper refusal coverage | Closed run, enabled provider, title generation, missing provider, invalid JSON and wrong profile refused; live invalid cases preserve appearance/transition files |
| Shell build/relocated launch and policy contracts | 7/7 pass; launch checker covers 45 modes and deployment negatives |
| Build Settings/provider startup selectors | Settings 4/4, provider demo/gallery 8/8 pass |
| AI/package-manager/greeter build and installed startup | Six four-selector matrices pass (24 launches); installed checkers reject the build root |
| Installed Settings/provider startup | Settings four selectors and both provider examples × four selectors pass |
| Collector | 14/14 pass |
| Terminal/Python syntax, headless Sway config, installer check, REUSE | Pass; licensing 128/128 files |

The host plugin mask initially overlaid `/dev/null` on plugin files. Qt scans
metadata even when another theme is selected, producing a permission diagnostic
in provider installed-example and Settings acceptance. Both failed attempts are
retained. The corrected mask exposes copies of the other system plugin entries
and omits HoloNight entries; staged plugins remain available from the new prefix.
The provider package and Settings checks pass with that correction. This changed
only the umbrella harness, not provider or consumer behavior.

The earlier immutable full-suite archive remains
`.cache/holonight-uqc201-final-dyxe1nl_/holonight-uqc201-final-dyxe1nl_.tar.gz`,
SHA-256 `b63db86b9821ae6661a4400689adac7f15aa992cbd9ed5b14b24bdb0c85676b8`.
Its exact revisions and listed package inventory accompany the retained results.


All HoloNight CMake package resolutions are checked against the new prefix at
release. Full current package inventory is 1,607 entries; its contents must match
exactly before archiving. Python syntax, Ruff checks/formatting, documentation
links/anchors, shell snippets and whitespace pass. Only diagnostic, helper and
startup checks were run; no full consumer suite or unrelated third-party runtime
matrix was repeated.


## Immutable release

READY kit: `/tmp/holonight-uqc201-p03-c_w7vh8n`, **838 verified file hashes**.
Archive: `.cache/holonight-uqc201-p03-c_w7vh8n/holonight-uqc201-p03-c_w7vh8n.tar.gz`.
SHA-256: `44b4c44a3e19b16c0a3ac59ccbc6716bc49cf46005255025dfea5b59f572b447`.

Exact-prefix restoration passed; repeating restoration refused the existing path
with exit 2. Logs: `.cache/holonight-uqc201-p03-c_w7vh8n/logs/restoration.log` and
`restoration-refusal.log`. The pre-restoration directory is preserved at
`/tmp/holonight-uqc201-p03-c_w7vh8n-before-restore`. Do not modify either release.
The archive contains READY, revisions, inventories, prior evidence, preparation
recipes, detailed launch logs, the matrix and separate workspace/helper evidence.
Restoration outcomes and the archive hash are necessarily recorded outside the
archive itself, here and in the matching work directory.

If the exact kit path is absent, restore from the umbrella root:

```sh
python3 docs/initiatives/unified-qtquick-controls/restore-rendering-kit.py .cache/holonight-uqc201-p03-c_w7vh8n/holonight-uqc201-p03-c_w7vh8n.tar.gz
```

Next: [exactly two sequential human AI Settings palette runs](P03-RECHECK.md).
No human acceptance was performed in this preparation. P03 open, UQC-222 Done,
UQC-201 In Progress, initiative Accepted; all unrelated gates remain unchanged.
