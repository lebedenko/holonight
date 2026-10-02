# Verification record

Implementation is local. The initiative is **not complete** while the blockers below remain.
No source warning cleanup, host installation, publication, or umbrella pin updates were performed.

## Passed

- All 17 Taskfiles parse; applicable capabilities and independent Serena configurations are present.
- Ten helper fixtures cover owned/dependency and canonical/legacy database precedence, invalid/stale commands,
  preservation on failed refresh, source overrides, paths with spaces, missing metadata, drift without writes,
  explicit prefixes without builds, and exclusion of vendor/probe sources from formatting.
- Bundle drift check and `git diff --check` pass. Root instantiated clangd and component configurations use the selected database.
- All 16 CMake components configure and build with Debug and Release presets. Test builds and CTest pass for
  15 components after rerunning private-socket fixtures outside the sandbox. Qt test configuration is blocked below.
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

1. **Qt tests:** the existing installed-package test requires `patchelf`, which is absent. Both Debug and Release
   builds pass, but test configuration stops at `tests/CMakeLists.txt`. Make that prerequisite available and run
   `task test`; no acceptance target was disabled or substituted. Doctor reports this prerequisite.
2. **Hyprlock extensionless Bash recognition:** the installed Serena Bash filename matcher supports `.sh` and `.bash`,
   but rejects `scripts/status` with `Cannot extract symbols`. Retrieval from `.sh` files succeeds. This requires
   Serena support for extensionless files or an explicitly approved compatibility change; server startup is not
   counted as successful recognition. No upstream runtime was patched and the installed helper name is preserved.
3. **Existing source formatting/static analysis:** Appearance Adapters, Greeter, System Services and Thumbnails fail
   the common formatting baseline on existing source files. Config tidy finds existing missing braces; daemon tidy
   finds existing trailing-comma and C/systemd macro diagnostics. These are source findings, not missing include/import
   or unsupported compiler flag errors. They remain outside this configuration initiative's cleanup scope.

Hyprlock's original nested graphical acceptance remains available as `task test`/`task test:nested`, with automated
checks as `task test:auto`. No native pointer/focus automation or manual desktop checks were performed.
