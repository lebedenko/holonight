# Local installation acceptance — 2026-10-11

These checks cover working-tree implementation based on the current umbrella pins. They are not
published-revision ecosystem integration evidence. The subsequent publication/pin handoff is recorded in TASKS.md.

## Application staging

For each of `holonight-ai` and `holonight-pkg-manager`:

```sh
cmake -S <repository> -B /tmp/installation-completeness/<repository>/build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr \
  -DCMAKE_PREFIX_PATH="${PWD}/.source-install/stage/usr" \
  -DBUILD_TESTS=OFF
cmake --build /tmp/installation-completeness/<repository>/build --parallel 4
DESTDIR=/tmp/installation-completeness/<repository>/stage \
  cmake --install /tmp/installation-completeness/<repository>/build
```

Both fresh Release builds and staged installs passed. Complete logs were reviewed; no compiler or
configure warnings occurred. Toolchain: GNU 16.2.1, Qt 6.12.0, Ninja. Reused providers were Release
artifacts built with the same compiler and Qt installation; 225 staged provider paths were checked
against the existing ownership manifest, file hashes and exact pinned revisions:

- Config: `d6a392b41991f70a004d58f7694c7b6115cb7280`
- System services: `39472e6dcafc93acea218a234213c346be256586`
- Qt: `ec6857162f9947f4ad926c62781e4854b52ad2a5`

Staged executable modes, both desktop files, byte-identical application SVGs and existing D-Bus
service files were checked. Packages also retains holonight-packaged, its systemd user unit and
D-Bus introspection XML. `desktop-file-validate` passed for source and staged launchers; Packages
emits only an optional suggestion to add Settings to its requested category set.

Logs: `/tmp/holonight-ai-installation-build.log` and
`/tmp/holonight-pkg-manager-installation-build.log`.

## Hyprlock and ownership

```sh
cmake -S holonight-hyprlock -B /tmp/installation-completeness/holonight-hyprlock/build \
  -G Ninja -DCMAKE_INSTALL_PREFIX=/usr
cmake --build /tmp/installation-completeness/holonight-hyprlock/build
ctest --test-dir /tmp/installation-completeness/holonight-hyprlock/build --output-on-failure
DESTDIR=/tmp/installation-completeness/holonight-hyprlock/stage \
  cmake --install /tmp/installation-completeness/holonight-hyprlock/build
python3 -m unittest discover -s tests -p test_install_ownership.py -v
python3 -m unittest discover -s tests -p test_install_order.py -v
bash -n scripts/install.sh scripts/uninstall.sh scripts/install-dependencies.sh
```

Hyprlock passed both tests and stages the /etc/xdg configuration, executable helper and both assets
with /usr runtime references. All 36 ownership tests and five module coverage/order tests passed.
Ownership tests cover AI and Packages service payloads and the real Hyprlock CMake stage, including
unmanaged configuration rejection, package ownership checks, migration backups and preservation
of modified configuration on uninstall. Shell syntax and diff whitespace checks passed.

The three actual clean component stages were merged and deployed using the production
make_manifest, collision_check and copy_stage functions into `/tmp/installation-completeness/root`.
All deployed file hashes and module owners matched. No host installation or service refresh ran.
This is component deployment acceptance; full ecosystem installation at published application
revisions remains a separate integration step.

`task test:installer` passed: all 63 tests, including dependency, icon installation/upgrade,
module coverage and payload ownership regressions. Log: `/tmp/holonight-installer-acceptance.log`.

## Remaining handoff

- Separate application commits were reviewed and published on 2026-10-11 after user authorization.
- The user authorized application pin updates on 2026-10-11; the umbrella handoff records those published revisions.
- Run final ecosystem alternate-root installation at those exact accepted pins.
- User confirmed HoloNight AI and HoloNight Packages appear in the application menu on 2026-10-11.
- Mark the final integration work package Done and initiative Integrated only after those checks.
