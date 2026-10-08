# Shell wallpaper menu publication — 2026-10-08

The user requested review, commit, publication and pinning of the six remaining Shell files.
Reviewed baseline: 7d82bd5162d52df1fcbcfbb747b6c7654be4df45.
Published Shell revision: 25e1556bc5ffc06015a757d48e468f7c0d9c9ccb.

The desktop menu adds Change Wallpaper, dismisses before dispatch, and forwards the captured monitor
connector through org.freedesktop.Application.ActivateAction("wallpaper", [connector], {}). This matches
Settings' existing contract at the pinned revision 7c7275505c91ee37bdbfa674259daae99ea25da4.
Keyboard wrapping, power submenu index, menu height and submenu anchoring account for the fourth row.
No behavioral defect was found. Review added braces to the asynchronous error handler to match repository style.
All six intended files, including service and QML regression tests, were committed together; Shell is clean.

## Verification

Provider stage: holonight-shell/build/decoration-provider, with the Qt, SystemServices and Config revisions
recorded in its provider-revisions.tsv. Qt 6.12.0, Debug, Wayland enabled.

- cmake --build build/decoration-independent -j8: passed; complete log reviewed, no compiler warnings.
- Private-bus CTest filter ^SettingsNavigationService\.|^test_holonight_qml_harness$: 4/4 passed,
  including the complete offscreen QML harness and wallpaper connector dispatch.
- format-check, qml-lint, generated QML type/interface/package checks: passed; existing unrelated QML warnings retained.
- Focused clang-tidy for SettingsNavigationService.cpp and test_settings_navigation_service.cpp: passed.
- REUSE and git diff --check: passed. Initial REUSE worker IPC was blocked by the sandbox; permitted rerun passed.
- Prior clean build and full-suite acceptance included these exact six pending changes before review;
  its evidence is retained in the decoration-independent Viewer handoff. Only braces changed during review,
  so unaffected expensive checks were not repeated.
- task compositor-smoke-check printed the live checklist. No native pointer/focus interaction was automated;
  a native wallpaper-picker interaction check was not performed in this handoff.

Logs: /tmp/shell-wallpaper-review-{build,focused,tests,static,qmltypes,tidy-service,tidy-test,reuse,smoke-checklist}.log.
The initial attempt to select the QML TestCase by bare name was rejected by QtTest; the successful complete
QML harness run supersedes that diagnostic invocation.

## Publication and pin

Canonical origin/main availability was confirmed with git ls-remote before updating the Shell gitlink.
CI was queried once for revision 25e1556bc5ffc06015a757d48e468f7c0d9c9ccb: no run was available at query time.
No CI success is claimed and no CI polling occurred. This is a separate Shell handoff, not final umbrella
integration of the decoration-independent Viewer initiative. No deployment occurred.
