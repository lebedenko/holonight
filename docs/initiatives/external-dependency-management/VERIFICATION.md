# Foundation verification — 2026-10-12

This verifies the canonical umbrella foundation. Repository adoption, publication, pins, Debian environment
qualification and manual ecosystem acceptance remain pending. Image IDs below are local immutable IDs, not
published registry digests.

| Check | Result | Evidence |
|---|---|---|
| Canonical tooling unit/integration regressions | 32 passed locally and in both offline Arch images | verification/local-tooling-tests.log and *-tooling-tests.log |
| Full installer fixture suite | 67 passed | verification/installer-tests.log |
| Changed preflight and QMarkdown ownership fixtures after final edits | 15 + 4 passed | Recorded local commands below |
| Generated production/CI profiles and provider snippets | No drift | generate-install-profile.py --check |
| Shell syntax and final diff whitespace | Passed | bash -n; git diff --check |
| Umbrella REUSE metadata | Passed: 324/324 files | reuse lint (outside sandbox: multiprocessing socket required) |
| Real local provider preparation with spaces, cache reuse and installed consumer | Passed | verification/local-provider-smoke.log |
| Clean accepted-revision QMarkdown Release build/staging | Passed with local Qt 6.12.0 | local build and full production probe under /tmp; Arch package acceptance below |
| Pacman-built pinned QMarkdown package in full Arch image | Passed; installed main package only; licenses/metadata/shared library checked | verification/arch-full-build.log and full-qmarkdown-ownership.txt |
| Full Qt offline prerequisite, Qt5/GTK checks, QMarkdown rendering and tooling | Passed, --network none | verification/full-evidence.json and full-prerequisites.log |
| Minimal daemon offline prerequisite/tooling profile | Passed; no Qt/GTK packages | verification/daemon-evidence.json and daemon-packages.txt |
| Repository application acceptance | Not run: adoption has not started | Local SDDs |
| Debian release environment | Pending package-managed Qt >=6.11 qualification | packaging/ci/README.md |

Commands:

```sh
python3 -m unittest discover -s tooling -p 'test_*.py' -v
python3 -m unittest discover -s tests -p 'test_install*.py' -v
python3 -m unittest discover -s tests -p 'test_install_dependencies.py' -q
python3 -m unittest discover -s tests -p 'test_install_qmarkdown.py' -q
python3 tooling/generate-install-profile.py --check
bash -n scripts/install.sh scripts/install-dependencies.sh scripts/install-profile.sh packaging/qmarkdown/PKGBUILD
git diff --check
docker build --target daemon -f packaging/ci/Dockerfile.arch -t holonight-deps-daemon:external-dependencies .
docker build --target full -f packaging/ci/Dockerfile.arch -t holonight-deps-full:external-dependencies .
python3 scripts/qualify-dependency-images.py --profile daemon --image holonight-deps-daemon:external-dependencies --output .cache/dependency-qualification/final-daemon
python3 scripts/qualify-dependency-images.py --profile full --image holonight-deps-full:external-dependencies --output .cache/dependency-qualification/final-full
```

Full image: `sha256:dc3d1e15907ef1c97c5edc9a00a9dbd1969ba76465e04d6d4e415f509beca1bb`.
Daemon image: `sha256:17f90982a6c56a84d706706f75ebd91b0e123df2fa84d6f0d444f6eedcecd93d`.
The full image uses Qt 6.11.2; the local source/package smoke uses installed Qt 6.12.0. Compiler, CMake, Ninja,
resolved paths/versions, package inventories and inputs are retained under verification/.

Warnings reviewed: Qt emits its standard private-module ABI warning; exact public/private versions are required
by the probe and recorded. Arch's default LTO warned in the pinned cmark bundle; the package now disables optional
LTO to match upstream Release compilation, and the corrected complete package build log has no compiler warnings.
The initial smoke exposed an unnecessary QML_IMPORT_PATH argument on a C++ consumer; it was corrected and the
smoke was rerun successfully. No compiler-warning suppression flags were added.

Historical supplements remain fully preserved: 250 entries, 103 distinct names. Classification describes direct
profile requirements versus transitive package-manager resolution. No hosted CI result or manual ecosystem result
is claimed. All 18 original gitlinks remain unchanged. No packages were installed on the host by this work.

Committed log copies normalize trailing whitespace only; complete raw logs remain in /tmp and .cache.
