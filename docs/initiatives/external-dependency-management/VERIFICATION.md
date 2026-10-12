# Historical foundation verification — 2026-10-12

This preserves EDM-003 qualification against the earlier recipe. The current EDM-024 evidence follows below.
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
is claimed. At foundation verification time, all 18 original gitlinks were unchanged; subsequent documentation publication/pins are recorded in TASKS.md. No packages were installed on the host by this work.

Committed log copies normalize trailing whitespace only; complete raw logs remain in /tmp and .cache.

## EDM-024 Arch handoff qualification — 2026-10-12

Starting umbrella revision: `9a37a76205d5995253312ca286e953bf478ae02d`.
Current QMarkdown: 1.1.0, source `b71740c7e0f26b0709f5e929a79e8d01dba56071`.
Historical evidence above remains unchanged in `verification/`; current evidence is in `verification/edm024/`.
`edm024/INPUTS.json` records recipe, context, package-list, declaration, probe and tooling SHA-256 inputs.

Full image ID: `sha256:51bb1aed43c0ad4e9336ed49962862ec78293f4380fd05e73b954e88c6c479c7`.
The rebuilt package used Release, shared libraries, tests/examples/benchmarks off, and optional LTO disabled.
The Arch snapshot remains `2026/09/30` with the pinned base recorded in Dockerfile.arch. Compatible base/package
layers were cached; QMarkdown was rebuilt cleanly. The build context transfer was only 1.17 kB.

| Check | Result | Evidence |
|---|---|---|
| Current recipe package build | Passed; main package 1.1.0-1 installed through pacman | edm024/arch-full-build.log |
| Full prerequisites with network disabled | Passed for all 18 declaration profiles, including GTK/Qt5 probes and GTest/GMock targets | edm024/full-probe.cmake, full-prerequisites.log, full-resolved.txt |
| Exact Qt public/private identities | All selected modules 6.11.2 | edm024/full-resolved.txt, full-qt.txt |
| QMarkdown ownership, metadata and offscreen rendering | Passed | edm024/full-qmarkdown-ownership.txt, full-qmarkdown-runtime.log |
| Compiler, CMake, Ninja and package inventory | Retained | edm024/full-compiler.txt, full-cmake.txt, full-ninja.txt, full-packages.txt |
| Canonical tooling tests | 32 passed locally and 32 offline in full image | edm024/local-tooling-tests.log, full-tooling-tests.log |
| Full installer fixture suite | 68 passed | edm024/installer-tests.log |
| Installer dependency/QMarkdown fixtures | 15 + 4 passed | edm024/local-dependency-tests.log, local-qmarkdown-tests.log |
| Generated profiles | No drift | `python3 tooling/generate-install-profile.py --check` |
| Licensing | Passed | edm024/reuse.log |
| Daemon reuse | Identity and complete pacman inventory unchanged; no Qt/GTK packages | edm024/daemon-reuse.json; historical daemon-evidence.json and daemon-packages.txt |

Daemon identity remains `sha256:17f90982a6c56a84d706706f75ebd91b0e123df2fa84d6f0d444f6eedcecd93d`.
Dockerfile.arch, daemon package list and qualification/tooling inputs match the historical baseline. The narrowed
context rules do not change daemon COPY inputs; QMarkdown changes affect only full. Historical offline daemon
qualification is reused without another build or qualification run. A fresh offline `pacman -Q` matched its
historical inventory byte for byte.

Complete build and prerequisite logs reviewed: no compiler warnings; Qt’s standard private ABI warnings remain,
with exact module versions enforced. Optional Vulkan headers are absent; software/offscreen rendering passes.
No warning suppression was added. Registry publication and digest identity checks passed; immutable references follow below.

Commands for this iteration:

```sh
docker build --progress=plain --target full -f packaging/ci/Dockerfile.arch -t holonight-deps-full:arch-handoff .
python3 scripts/qualify-dependency-images.py --profile full --image holonight-deps-full:arch-handoff --output .cache/dependency-qualification/edm024-full
docker image inspect --format '{{.Id}}' holonight-deps-daemon:external-dependencies
docker run --rm --network none holonight-deps-daemon:external-dependencies pacman -Q
cmp /tmp/edm024-daemon-packages.txt docs/initiatives/external-dependency-management/verification/daemon-packages.txt
python3 -m unittest discover -s tooling -p 'test_*.py' -v
python3 tooling/generate-install-profile.py --check
reuse lint
python3 -m unittest discover -s tests -p 'test_install_dependencies.py' -v
python3 -m unittest discover -s tests -p 'test_install_qmarkdown.py' -v
bash -n scripts/install.sh scripts/install-dependencies.sh scripts/install-profile.sh packaging/qmarkdown/PKGBUILD
git diff --check
```

Canonical Config and System Services `origin/main` tips were confirmed by `git ls-remote` on 2026-10-12
at the exact handoff baselines recorded in TASKS.md.

Application acceptance and final integration remain pending. Debian is deferred, not qualified.

### Publication and handoff — 2026-10-12

Recipe/qualification checkpoint: `8f437c03c6b8da4ead2d16d938b6fb1c4f0a9702`.
The first push was rejected as unauthenticated. After the user authenticated Docker, manual publication succeeded
for the exact qualified images with tags `arch-full-8f437c0` and `arch-daemon-8f437c0`.

| Profile | Immutable registry reference | Qualified/pulled image ID |
|---|---|---|
| full | `ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40` | `sha256:51bb1aed43c0ad4e9336ed49962862ec78293f4380fd05e73b954e88c6c479c7` |
| daemon | `ghcr.io/lebedenko/holonight-deps@sha256:cfd5daeb5745c71e72062aa9926b4ca1636599987f93697a1bf79e17693768ec` | `sha256:17f90982a6c56a84d706706f75ebd91b0e123df2fa84d6f0d444f6eedcecd93d` |

Registry digests are manifest identities, distinct from local image IDs. Both digest pulls succeeded and
`docker image inspect --format '{{.Id}}' <digest-reference>` matched each qualified image ID exactly.
Both references also passed anonymous digest pulls using an empty Docker configuration, confirming availability
for standalone CI consumers. `verification/edm024/PUBLICATION.json` records the verification time and identities;
`*-push.log`, `*-pull.log` and `*-anonymous-pull.log` retain the successful registry commands’ output.

```sh
docker push ghcr.io/lebedenko/holonight-deps:arch-full-8f437c0
docker push ghcr.io/lebedenko/holonight-deps:arch-daemon-8f437c0
docker image inspect --format '{{json .RepoDigests}}' ghcr.io/lebedenko/holonight-deps:arch-full-8f437c0 ghcr.io/lebedenko/holonight-deps:arch-daemon-8f437c0
docker pull ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40
docker pull ghcr.io/lebedenko/holonight-deps@sha256:cfd5daeb5745c71e72062aa9926b4ca1636599987f93697a1bf79e17693768ec
docker image inspect --format '{{.Id}}' ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40 ghcr.io/lebedenko/holonight-deps@sha256:cfd5daeb5745c71e72062aa9926b4ca1636599987f93697a1bf79e17693768ec
docker --config /tmp/edm024-anonymous-docker pull ghcr.io/lebedenko/holonight-deps@sha256:37ca051c39d1688d6413c47d94b8c0f221152dac6981ec67d155f2c43ea17b40
docker --config /tmp/edm024-anonymous-docker pull ghcr.io/lebedenko/holonight-deps@sha256:cfd5daeb5745c71e72062aa9926b4ca1636599987f93697a1bf79e17693768ec
```

EDM-024 is Done. EDM-004/005 are Ready at the exact baselines recorded in TASKS.md. The completed umbrella
handoff publishes the qualification checkpoint and this publication record in one Git push to canonical
`origin/main`. Application acceptance remains pending; the initiative remains Accepted. No application workflow,
repository adoption implementation or gitlink changes are included.
