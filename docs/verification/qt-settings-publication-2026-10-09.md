# Qt and Settings publication — 2026-10-09

Published the completed separator scrolling fix and Settings regression coverage to their canonical
`origin/main` branches, then confirmed both remote heads with `git ls-remote` before pinning.

| Repository | Published revision | Change |
| --- | --- | --- |
| holonight-qt | `918d14dd7c739569233a16fd469e0063b9316971` | Stabilize separator geometry during scrolling |
| holonight-settings | `6ec7a402ebc319f9a925fdf97d8e0382e0c1ef42` | Cover expanded Appearance scrolling and navigation |

Both repository working trees were clean before and after publication. Each repository received one
normal push containing its existing implementation commit. No implementation changes were made during
publication, and this record does not mark a broader initiative Integrated.

## Local acceptance

Clean native builds used GNU C++ 16.2.1 and Qt 6.12.0. Qt was configured in
`/tmp/holonight-publish-qt-20261009` with Debug, tests, demo and controls gallery enabled, then built with
`cmake --build ... -j 4` and installed into `/tmp/holonight-publish-prefix-20261009`.
The configuration provider was the clean `holonight-config` revision
`d6a392b41991f70a004d58f7694c7b6115cb7280` from Qt's existing dependency prefix.

Settings was configured in `/tmp/holonight-publish-settings-20261009` with Debug and tests enabled,
using the newly installed Qt prefix first in `CMAKE_PREFIX_PATH`, followed by its existing dependency
prefix. Reused providers were clean: configuration `d6a392b41991f70a004d58f7694c7b6115cb7280`,
shell configuration `d5c5e8d50f6cd4d3ccabb6b8d242ff56914977de` and system services
`39472e6dcafc93acea218a234213c346be256586`. Settings used the same native Qt/toolchain as its providers.

| Check | Result |
| --- | --- |
| Clean Qt build and install | Passed; compiler build log contains no warnings or errors |
| `QT_QPA_PLATFORM=offscreen ctest --test-dir /tmp/holonight-publish-qt-20261009 --output-on-failure -j 4` | 95/95 passed, including package installation, separator tests and example startup |
| Clean Settings build against published Qt sources | Passed; compiler build log contains no warnings or errors |
| `dbus-run-session -- env QT_QPA_PLATFORM=offscreen ctest --test-dir /tmp/holonight-publish-settings-20261009 --output-on-failure -j 4` | 81/86 passed initially; five D-Bus tests failed under parallel execution |
| Same Settings CTest command with `-R '^PortalFolderChooser' -j 1` on a fresh bus | 6/6 passed; concurrent tests had competed for the same service name |
| Same Settings CTest command with `-R '^SettingsActivationServiceTest' -j 1` on a fresh bus | 11/11 passed, including the remaining failed activation test |
| Additional isolated arbitration test with desktop theme overrides cleared | 1/1 passed |
| `task format-check` in each repository | Passed |
| Qt `python3 tooling/qml_policy.py`; Settings `task qml-import-check` | Passed |
| Qt `cmake --build ... --target all_qmllint`; Settings `cmake --build ... --target qml-lint` | Passed with existing warnings in unchanged QML |
| Settings `bash scripts/check-qmltypes.sh /tmp/holonight-publish-settings-20261009` | Passed |
| `reuse lint` in each repository | Passed |
| `git diff HEAD^ HEAD --check` in each repository | Passed |

All 86 Settings tests passed across the full run and serial retries; the parallel run itself did not
pass. Final existing development clang-tidy logs were reviewed for Qt's geometry source, changed Qt
test lines and Settings acceptance source; they contained only suppressed diagnostics. Full build logs
were reviewed. Qt configuration emitted existing private-module and QTP0004/QTP0006 policy warnings;
QML lint diagnostics concerned unchanged files. No physical desktop pointer/focus automation was used.

Logs for the clean builds and acceptance commands are local `/tmp/holonight-publish-*.log` artifacts.
Licensing needed execution outside the sandbox for multiprocessing sockets, and Settings D-Bus tests
needed execution outside the sandbox to create an isolated session bus.

## Hosted checks at publication

Checked the latest available runs once after both pushes. Pending runs were not awaited; older passing
runs are not evidence for these pins.

| Repository/revision | Workflow | Status | Conclusion | Run |
| --- | --- | --- | --- | --- |
| Qt `918d14d` | CI | in_progress | Pending | [37970766942](https://github.com/lebedenko/holonight-qt/actions/runs/37970766942) |
| Qt `918d14d` | Licensing | completed | success | [37970766978](https://github.com/lebedenko/holonight-qt/actions/runs/37970766978) |
| Settings `6ec7a40` | CI | queued | Pending | [37970825921](https://github.com/lebedenko/holonight-settings/actions/runs/37970825921) |
| Settings `6ec7a40` | Licensing | in_progress | Pending | [37970825737](https://github.com/lebedenko/holonight-settings/actions/runs/37970825737) |
