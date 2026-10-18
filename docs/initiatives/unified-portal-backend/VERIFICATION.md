# UPB-003 — Local implementation and verification

Date: 2026-10-19 (Europe/Kyiv; work began 2026-10-18).
Status: component implementation committed, published and pinned; not Integrated.
No host deployment was performed. Manual acceptance and full shell acceptance remain open.

## Tested sources and dependencies

| Repository | Base revision; local changes included |
|---|---|
| umbrella | `065dafb989754af0ce216a0c4a7430058252daa9` |
| xdg-desktop-portal-holonight | `42cc52252acb7af82e1cba6c6fc763f42573f8de` |
| holonight-shell | `d2784e965d283280e2540f048141f92ef9d6cb63` |

These are base revisions, not commits containing this implementation. Ignored
`build/unified-portal-backend/source-snapshots.json` identifies the tracked patches
and new source files by SHA-256; corresponding patches and routine logs remain
under that ignored directory. These pre-commit source snapshots correspond to the
published component commits recorded below.

## Publication and pins

On 2026-10-19, following explicit user authorization to commit, publish and pin:

| Repository | Published `main` revision | Commit |
|---|---|---|
| xdg-desktop-portal-holonight | `73e7cf647610ce84cc360bc08c099c69dc6002dc` | `feat(portal): unify standalone Settings and FileChooser backends` |
| holonight-shell | `b06d5cbce95b36502dbbb1048dc984ddb312706d` | `refactor(portal): delegate Settings publication to standalone backend` |

Remote branches were fetched before publication and matched their local bases.
The backend was pushed before committing and pushing the shell consumer change.
This umbrella commit records both gitlinks together with installer ownership,
legacy cleanup, broker checks and the initiative evidence. Prior automated results
are reused because publishing and pinning did not change component source content.
The unrelated untracked `holonight-grub/` directory was excluded.


Native builds consumed installed packages from
`build/shared-file-ui-controls/native-prefix`, without adding sibling source trees
to component builds. Installed artifact hashes are recorded in
`build/unified-portal-backend/native-provider-artifacts.json`. The existing prefix's
`published-revisions.json` records HolonightQt `fac34119cc2e2356a3437b5f709bb052ac04f9a8`
and FileBrowser `6009e59cdf8d685ee818d92564ce64ea0f838896`; artifact hashes identify
the actual native inputs independently of that provenance record. Native Qt was
6.12.0. Container binaries were used only for acceptance.

Clean component acceptance used the pinned image
`ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40`
(Qt 6.11.2, Clang/clang-format 22.1.8). Installed container provider sources:

| Provider | Backend acceptance | Shell acceptance |
|---|---|---|
| holonight-config | `b76a5c3acb6c6717f51f7e131ce42a687566cee2` | `0ccd25f323662f50a47bb048be636160f2b7c135` |
| holonight-qt | `fac34119cc2e2356a3437b5f709bb052ac04f9a8` | same |
| holonight-system-services | — | `70614eb70329af7014853c2973e5624acf0b251e` |
| holonight-search | `3248a4566e265bdacff83deba9d9432afd980727` | — |
| holonight-images | `2713d62b90f980e36221db00220c854141c598dd` | — |
| holonight-thumbnails | `dde56208d8edc8ec6e2870dbcd44c0a9363f4b19` | — |
| holonight-file-browser | `6009e59cdf8d685ee818d92564ce64ea0f838896` | — |

## Commands and results

Commands below ran from the umbrella root unless a component directory is stated.
Private D-Bus checks required execution outside the filesystem/network sandbox
because its Unix socket bind restriction prevented buses from starting. No host
D-Bus activation was used.

- `CMAKE_PREFIX_PATH=$PWD/build/shared-file-ui-controls/native-prefix task -d xdg-desktop-portal-holonight build`
  and `task -d holonight-shell build`: passed native builds using installed packages.
- `ctest --test-dir xdg-desktop-portal-holonight/build/dev --output-on-failure`:
  all three tests passed. Coverage includes Settings values, unsigned defaults,
  `(ddd)` accent signature, NotFound/InvalidArgs, ReadAll filtering, atomic document
  replacement, invalid startup defaults, invalid-update retention, recovery,
  suppression for unchanged and typography-only changes, registration rollback,
  both activation orders in fresh buses, shared process identity, shutdown with
  pending requests, and existing chooser cancellation/concurrency/path/save cases.
- From `holonight-shell`,
  `python3 scripts/run-isolated-test.py --hide-host --build-dir build/dev build/dev/tests/test_holonight_services '--gtest_filter=Appearance*:Portal*:SystemPortalDBusTest.*:SessionIntegrationServiceTest.*'`:
  final 56 tests passed, including canonical appearance changes and independent
  backend diagnostic assertions.
- `python3 -m unittest discover -s tests -p test_install_ownership.py`:
  final 53 tests passed. Covers descriptor transfer, missing/duplicate/incompatible
  payloads, rejection before writes, modified/unmanaged collisions, unchanged
  legacy cleanup, retained original hashes across repeat upgrades, symlink parents,
  and conservative uninstall.
- `python3 -m unittest discover -s tests -p 'test_install_*.py'`:
  101 tests ran, passed with one root-only boundary test skipped. This broader run
  preceded the last added payload-contract case; the final ownership run above
  includes that addition.
- `python3 holonight-shell/tests/test_portal_routing.py`, repeated with
  `HOLONIGHT_PORTAL_STAGE` pointing to native and container Release stages:
  three tests passed for all seven shipped routing files, retained compositor
  defaults and absence of the shell descriptor.
- `python3 scripts/check-filechooser-broker.py --backend-build xdg-desktop-portal-holonight/build/dev --shell-stage holonight-shell/build/upb-stage/usr --imports $PWD/build/shared-file-ui-controls/native-prefix/lib/qt6/qml --libraries $PWD/build/shared-file-ui-controls/native-prefix/lib`:
  passed through the real installed broker on a private bus with isolated home,
  configuration, data directories and staged backend activation only. Settings
  Read, SettingChanged, typography-only suppression, invalid retention and recovery
  passed without shell activation. OpenFile, directory, multiple, SaveFile and
  SaveFiles dispatch/cancellation passed in the same backend process. The absent
  document portal is expected in this unsandboxed dispatch fixture; grants require
  manual acceptance.
- `python3 build/unified-portal-backend/check-native-upgrade.py`: passed actual
  combined native-stage ownership validation, upgrade from historical shell/backend
  descriptors, a second upgrade, obsolete-file removal and uninstall in a disposable
  target. No host destination writes occurred.
- `task -d xdg-desktop-portal-holonight check:integration` and
  `task -d holonight-shell check:integration`: clean installed-provider builds and
  CTest passed (backend: 3 tests; shell: 1,156). Initial runs stopped at formatting.
  `task -d <component> format` applied pinned formatting. Valid test results were
  reused; remaining checks resumed in the same isolated acceptance builds rather
  than rebuilding providers or repeating unchanged suites.
- `bash build/unified-portal-backend/final-verify.sh` repeated final native tests,
  real-broker verification and backend acceptance after preserving both original
  NotFound error messages and moving protocol dispatch into the private handler.
- Backend resumed acceptance passed format, tidy, QML lint/imports, qmltypes, REUSE,
  clean Release compilation and the exact five-file unified payload check. Final
  log: `build/unified-portal-backend/backend-final-checks.log`.
- Shell resumed acceptance passed format, QML lint/imports, qmltypes, REUSE,
  architecture boundaries, installed product-config consumer checks and clean
  Release staging. Final targeted container regressions passed all 23 diagnostic
  tests and the source/staged routing tests. Managed-session tests ran 21 cases,
  with three existing platform-tool checks skipped because the image lacks Lua,
  the Hyprland verifier and real UWSM environment preloader. Logs:
  `shell-final-checks.log` and `shell-final-regressions.log` in the evidence directory.
- Shell full tidy remains failing in unchanged
  `libs/holonight-integration/src/session/ProcessEnvironment.h:11`
  (`performance-enum-size`) and `ProcessEnvironment.cpp:62–63`
  (`readability-braces-around-statements`). Those files have no migration diff.
  The failure is retained in `shell-remaining.log`; it was not hidden or resolved
  by unrelated edits. Full shell acceptance therefore cannot be reported green.
- Python syntax compilation, shell `bash -n`, and `git diff --check` across all
  three repositories passed. Component CMake/QML registration metadata remained
  covered by the checks above.

## Remaining acceptance and handoffs

- [ ] Human native desktop checks: successful single/multiple file and directory
  selection; transient parenting/modality; parent disappearance; cancel/reopen;
  SaveFile overwrite and SaveFiles collision behavior; sandbox document access.
  The user confirmed these checks have not been performed.
  Never automate pointer or focus interaction. Existing historical native and
  sandbox acceptance obligations remain open.
- [ ] Resolve the pre-existing shell tidy failures through a separate focused change
  before claiming a fully green shell acceptance gate.
- [x] Review and commit component changes, publish authorized revisions in dependency
  order, then coherently update umbrella pins. No compatibility alias is installed.
- [ ] Deploy compatible backend/shell payloads together only after the separate
  handoff; review personal routing and preserved legacy files using the
  [migration instructions](README.md#personal-routing-migration).

Local staged verification does not mark the initiative Integrated or close the
historical FileChooser and configuration-architecture acceptance records.
