# Integration evidence — 2026-10-09

Status: Automated handoff checks passed; manual ecosystem acceptance pending.
Checkpoint: 0e9aa53. Repository work packages I-001 through I-003 are published,
locally verified and pinned. All initialized submodule working trees are clean.
Exact provider/backend/Shell revisions and latest once-checked CI results are in
[TASKS.md](TASKS.md); local acceptance evidence remains in each repository SDD.
The initiative remains Accepted, and I-004 remains In Progress.

## Automated checks

- Installer regression suite: `task test:installer`, 44 tests passed.
  Ordering includes the backend after Files; ownership, adoption and uninstall
  fixtures cover its executable, activation service and portal descriptor.
- `scripts/install.sh --check`: passed after pinning the published Shell handoff.
- Shell: clean Release and Debug CTest, 1157 tests each, four existing native
  user-manager skips; source/staged routing, installation, QML lint/metadata,
  formatting and REUSE passed. See the Shell SDD for provider artifact verification
  and resolved initial build-environment failures.
- Backend: `ctest --test-dir xdg-desktop-portal-holonight/build/design-acceptance
  --output-on-failure`, both portal-tests and portal-staged-activation passed.
- `reuse lint` at umbrella root and `git diff --check`: passed.

Real broker check, using the installed host xdg-desktop-portal on a private session
bus, temp HOME/XDG directories and disposable staged backend:

```sh
python3 scripts/check-filechooser-broker.py \
  --backend-build xdg-desktop-portal-holonight/build/design-acceptance \
  --shell-stage /tmp/filechooser-shell-stage/usr \
  --imports "$PWD/holonight-shell/build/filechooser-providers/lib/qt6/qml:$PWD/xdg-desktop-portal-holonight/build/providers/lib/qt6/qml" \
  --libraries "$PWD/holonight-shell/build/filechooser-providers/lib:$PWD/xdg-desktop-portal-holonight/build/providers/lib"
```

Passed all five cases: OpenFile (single file, folder, multiple files), SaveFile,
SaveFiles. Broker logs confirm the actual staged HoloNight routing preference and
selection of holonight-filechooser.portal. Each public Request reached the private
backend Request; public Close removed that backend Request. Activation executed the
staged binary. No host service was restarted or live installation changed.

The helper supplies read-only system GSettings schemas and copies the staged route
into the broker override directory, which also controls configuration lookup.
The isolated bus deliberately lacks Documents, system RealtimeKit, and Access
implementations: their corresponding startup diagnostics are expected and are not
sandbox grant evidence. The test does not select files or validate returned URIs,
GTK fallback availability, successful application flows or document access grants.

Logs: /tmp/filechooser-real-broker.log, /tmp/filechooser-installer-tests.log,
/tmp/filechooser-installer-preflight-final.log,
/tmp/filechooser-backend-integration-ctest.log and the local Shell verification logs.
No additional hosted CI polling was performed.

## Remaining acceptance

Use [MANUAL_CHECKS.md](MANUAL_CHECKS.md) for Viewer, Settings, selection/results,
save/overwrite, parent lifecycle, sandbox document access and native compositor
checks. The prior user-reported native chooser pass remains valid for that probe;
it does not cover this real-broker application matrix. Flatpak is not installed on
this host, so no sandbox document grant is claimed. Live deployment and the broker restart were subsequently authorized and completed;
see the deployment evidence below. Do not mark I-004 Done or the
initiative Integrated until every required acceptance case is recorded.

## Authorized live deployment — 2026-10-09

The user explicitly approved live installation and the portal restart. Deployed a
focused 30-file payload: installed Files Core/Quick browsing provider, standalone
backend/activation/descriptor/licenses, and four Shell routing configurations.
Reused the verified Release install artifacts; did not replace Shell or Files
application binaries or unrelated providers. Runtime library paths are relative
to the installed executable. All 30 installed hashes and per-file ownership/revision
records were verified against the staged payload. Existing umbrella ownership
records were preserved and merged, rather than replacing the full ecosystem
revision record with a partial deployment claim.

Preflight rejected neither unmanaged nor package-owned collisions. Previous payload
files and ownership manifest were backed up under
/var/backups/holonight-filechooser-5n71e78l. The user Hyprland routing file previously
forced FileChooser=kde. Backed it up with the suffix
.before-holonight-20261009-165751 and changed only that preference to
holonight-filechooser;gtk, preserving defaults and Settings routing.

Restarted xdg-desktop-portal.service at 16:57:51 EEST. Its broker is active, exposes
FileChooser version 4, and activated the backend from
/usr/libexec/xdg-desktop-portal-holonight (PID 370127 at inspection). Backend
introspection exports OpenFile, SaveFile and SaveFiles at the expected object.
Installed browsing Quick linkage resolves in /usr/lib with no missing library.
GTK and Hyprland portal services remain active. No pointer/focus interaction was
automated.

Backend startup logged a Qt host-portal registration diagnostic: “Could not
register app ID: App info not found for ''”. D-Bus activation and expected methods
remain available; successful chooser presentation and application results still
require the requested manual checks. The implementation does not expose a version
property on its private virtual interface; the public broker version lookup passes.
Viewer file selection, Settings folder selection, cancellation/reopen and keyboard
checks were requested from the user; no result is claimed yet. Full native and
sandbox acceptance remains pending.
