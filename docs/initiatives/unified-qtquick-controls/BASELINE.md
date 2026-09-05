# Existing-work baseline handoff — 2026-09-05

These are existing-work handoffs, not UQC implementation. Current checkouts were retained without history edits.
Canonical `origin` URLs were inspected and `git ls-remote origin refs/heads/main` confirmed publication. Qt's avatar,
shell's authentication sizing/account selection, and greeter's avatar commits were published from `main`. The
pre-existing provider review was preserved unchanged in separate documentation commit
`dd8eef45f92baf77efe6680e4ccaaa40b3c20030`; its claims are reviewed by UQC-001.

| Repository | Previous umbrella pin | Accepted published handoff |
|---|---|---|
| `holonight-qt` | `0b1bf7c3e27d1aafb19abe39cbf29f833f66289c` | `dd8eef45f92baf77efe6680e4ccaaa40b3c20030` |
| `holonight-shell` | `67d19a57392874f6d0e9f1fe93f849fdea3a614c` | `723763e09ff815d344a6cb01529dd8345a43b316` |
| `holonight-settings` | `8b8ccb521a925d18c71e4e0279b3017b77f4d188` | `579515ffb456c59cd1299e5852c392c3064c8262` |
| `holonight-ai` | `008536f319312d319e13bf0c4e681be373cd0eda` | `b600674ce4c86d883d98a27ae783e056a6a2f0e6` |
| `holonight-pkg-manager` | `c962af4f8e5b0a2f21d40beb52d3b41dfc760f8c` | `518bb60232086e9537fb402f91b4b703d260ffcf` |
| `holonight-greeter` | `f378680c39caa523f1c262c8153511495a878afe` | `9130c9ccbf05986ab1843ae322831e7fe9efdac9` |

## Verification and limits

- Provider: `cmake --build build -j 4`; `cmake --install build --prefix /tmp/holonight-qt-prefix`; existing 28 CTest
  entries passed. Focused `QmlAvatar.*`: loading/failure test passed; shader masking skipped under software rendering.
- Shell: `QT_QPA_PLATFORM=offscreen dbus-run-session -- ctest --test-dir build --output-on-failure`: 1,139/1,139 passed.
- Settings: existing CTest suite 45 entries, no failures; two activation checks initially skipped without a session
  bus. Follow-up `QT_QPA_PLATFORM=offscreen dbus-run-session -- ctest --test-dir build -R
  SettingsActivationServiceTest --output-on-failure` passed all 10 activation checks, including those two.
- AI: 711-entry suite had one missing-prefix failure and one credential-service skip. After staging Qt, all three
  `CanonicalQmlModules` tests passed, including the failed installed-artifact check. Real credential testing excluded.
- Packages: 94/94 CTest entries passed.
- Greeter: CTest passed outside the sandbox; the sandbox prevents transport tests from binding local sockets.
- Consumer builds: `cmake --build build -j 3` used existing configured builds against the staged Qt dependency.
- Tests initially used existing build artifacts; these results are baseline evidence, not clean installed-prefix
  UQC acceptance. No UQC product files were changed.

Previous visual/automated results and outstanding manual checks remain in
[the authentication handoff](../../../holonight-shell/docs/sdd/authentication-frontends/AVATAR-DIALOG-VERIFICATION.md).
Accepting these published revisions as the discovery baseline does not close those manual checks or assert final
visual acceptance. UQC's two-compositor application and activation matrix remains outstanding.

The untracked `holonight-pkg-manager/docs/mockups/explore.png` and `history.png` are intentionally untouched.
Temporary command logs are `/tmp/uqc-<repository>-baseline-tests.log` and `/tmp/uqc-<repository>-build.log`;
these are session-local and are not durable evidence artifacts. Results above are the durable summary.
