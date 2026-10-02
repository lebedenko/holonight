# Verification record

Implementation is local. The initiative is **not complete** while the blockers below remain.
No source warning cleanup, host installation, publication, or umbrella pin updates were performed.

## Passed

- All 17 Taskfiles parse; applicable capabilities and independent Serena configurations are present.
- Eleven helper fixtures cover owned/dependency and canonical/legacy database precedence, invalid/stale commands,
  preservation on failed refresh, source overrides, paths with spaces, missing metadata, drift without writes,
  explicit prefixes without builds, and exclusion of vendor/probe sources from formatting.
- Bundle drift check and `git diff --check` pass. Root instantiated clangd and component configurations use the selected database.
- All 16 CMake components configure and build with Debug and Release presets. Test builds and CTest pass for
  15 components after rerunning private-socket fixtures outside the sandbox. Qt now also passes its full 95-test workflow, as recorded below.
- Every CMake component configures in an exported standalone checkout under a path containing spaces, using an
  explicit dependency prefix. Standalone Config and Hyprlock build/test; standalone Qt builds Config from an
  arbitrary source override into its own prefix. These checks do not use an umbrella parent.
- All eight QML modules pass import policy, lint, and production metadata checks. Pure-QML `Module {}` metadata
  is valid; component-specific registration checks remain in place. Shell's 37-singleton, resource and authentication
  metadata/package checks pass. Viewer formatter fixtures verify configured Qt selection, rejection of stale PATH
  tools, explicit override validation, spaces and failure propagation.
- Search: representative Release benchmark runs with two million records.
- Files provider-revision fixtures retain unchanged-provider skip behavior and rebuild changed providers; missing
  installed package artifacts invalidate cached state. Shell retains its existing isolated test-command prefix.
- Icons: 44 unit/packaging tests, asset validation, actual Qt renderer at all advertised sizes/scales and palettes,
  GTK 3/4 symbolic checks, preview generation, and source/generated-theme/template REUSE checks pass.
- Serena activation and representative retrieval succeed for every configured language in every component.
  QML retrieval uses object-level symbols. See SERENA-RESULTS.json. Extensionless recognition fails below.
- Sampled real-command C++ and QML diagnostics for Files, Greeter, AI and Settings have no error diagnostics.
  Config diagnostics are existing source style findings. See DIAGNOSTICS.json.
- Umbrella compilation merging succeeds, records origins/coverage and rejects stale entries; cross-component
  retrieval from `holonight-config/src/path.cpp` succeeds. The active umbrella process retains its existing local
  language overrides; restart to load changes to server configuration.

Detailed build, standalone, QML and formatting results are checked in alongside this file. Raw logs and generated
compilation coverage remain ignored under `build/tooling-verification` and `.cache/tooling`.

## Open acceptance blockers

1. **Hyprlock extensionless Bash recognition:** the installed Serena Bash filename matcher supports `.sh` and `.bash`,
   but rejects `scripts/status` with `Cannot extract symbols`. Retrieval from `.sh` files succeeds. This requires
   Serena support for extensionless files or an explicitly approved compatibility change; server startup is not
   counted as successful recognition. No upstream runtime was patched and the installed helper name is preserved.
2. **Existing source formatting/static analysis:** Appearance Adapters, Greeter, System Services and Thumbnails fail
   the common formatting baseline on existing source files. Config tidy finds existing missing braces; daemon tidy
   finds existing trailing-comma and C/systemd macro diagnostics. These are source findings, not missing include/import
   or unsupported compiler flag errors. They remain outside this configuration initiative's cleanup scope.

Hyprlock's original nested graphical acceptance remains available as `task test`/`task test:nested`, with automated
checks as `task test:auto`. No native pointer/focus automation or manual desktop checks were performed.

## Qt tool discovery follow-up — 2026-10-02

- `task -d holonight-qt test` passes all 95 tests, including installed-package and example startup checks.
  `patchelf` is available in the existing environment; its discovery remains unchanged.
- A fresh ignored `build/tool-discovery-fresh` configuration succeeds without `/usr/lib/qt6/bin` on PATH,
  with an unrelated qmllint first on PATH. It selects `/usr/lib/qt6/bin/qmllint` and its sibling qml,
  substitutes absolute paths into the installed-package script, and does not cache automatic tool paths.
- Eight focused resolver fixtures pass: imported/default/configuration-specific locations, configuration
  precedence, sibling precedence, relative/absolute install bins, explicit overrides, missing/invalid tools,
  paths containing spaces, and reconfiguration against a different installation.
- Valid direct overrides containing spaces reach the real installed-package script with quoting intact;
  an invalid direct override fails with the variable name and missing executable path.
- All eleven shared helper fixtures pass, including QML/QMLLINT environment forwarding and compatibility
  with other modules. Bundle 1.0.1 is synchronized across all 17 modules; drift and diff whitespace checks pass.
- Qt editor metadata and the umbrella compilation database were refreshed after verification.
- Required daemon checks also pass formatting and all 111 tests. `task -d holonightd tidy-src` still fails on
  existing C99 compound literals and a missing enum trailing comma, covered by the source-analysis blocker above.
- Changes are committed locally using Conventional Commits. Publication and umbrella submodule pins are unchanged.
