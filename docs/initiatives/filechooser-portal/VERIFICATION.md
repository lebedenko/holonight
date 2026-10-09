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
this host, so no sandbox document grant is claimed. Live deployment and service
restarts await separate explicit authorization. Do not mark I-004 Done or the
initiative Integrated until every required acceptance case is recorded.
