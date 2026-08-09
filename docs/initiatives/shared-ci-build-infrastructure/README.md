# Shared CI Build Infrastructure

Status: Draft

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Make Arch Linux the reproducible, authoritative CI toolchain for HoloNight desktop components while replacing
duplicated repository-specific dependency images with a small umbrella-owned image family. Local container runs and
GitHub Actions must execute the same repository commands from immutable, traceable images.

Ubuntu remains explicit portability coverage where a repository promises it. It is not the authoritative HoloNight
desktop build environment.

## Non-goals

- Moving product implementation or repository-specific build logic into the umbrella repository.
- Publishing a mutable `latest` tag as an authoritative CI baseline.
- Replacing an existing repository image before the replacement passes that repository's complete suite.
- Forcing `holonight-config` onto Arch; it remains Ubuntu-based or gains Arch only as an additional matrix entry.
- Combining source checkouts or prebuilt HoloNight product artifacts into the shared toolchain images.
- Standardizing repository commands beyond the minimum needed to run them identically locally and in CI.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| umbrella | Build definitions, publication workflows, provenance, image validation, rebuild documentation, and image-update policy | This initiative until an umbrella-local infrastructure design is required |
| `holonight-qt` | Pilot the shared images across Qt 6 and Qt 5/private-header compatibility coverage | Pending |
| `holonight-shell` | Migrate shell build, test, QML, architecture, format, and tidy jobs | Pending |
| `holonight-ai` | Migrate application build, test, QML, format, and tidy jobs | Pending |
| `holonight-settings` | Migrate application and dependency-integration jobs | Pending |
| `holonight-pkg-manager` | Migrate application build, test, QML, format, and tidy jobs | Pending |
| `holonight-config` | Preserve portable Ubuntu coverage; optionally add an Arch matrix without changing the portability promise | Pending |

## Shared image contract

The umbrella publishes three layered Arch-based images to GHCR:

1. `ci-base`: compiler, CMake, Ninja, Clang formatting/static-analysis tools, Git, and common test utilities.
2. `ci-qt6`: `ci-base` plus the supported Qt 6 development, QML, and headless runtime packages used by HoloNight
   desktop applications.
3. `ci-qt-compat`: `ci-qt6` plus Qt 5 development and private headers required for explicitly approved
   compatibility work.

Exact package names, Arch snapshot/update strategy, supported architectures, and installed tool versions must be
settled before this initiative becomes `Accepted`. Each image definition must include a smoke test that reports tool
versions and proves a minimal configure/build/test path. `ci-qt6` must additionally prove a minimal headless QML
run; `ci-qt-compat` must prove separate Qt 5 and Qt 6 linkage and private-header compilation.

Images contain toolchain and system dependencies only. Each consumer continues to fetch, build, and install its
exact HoloNight source dependencies in its own workflow or repository-local helper.

## Versioning, provenance, and update contract

- Every publication produces a human-readable version tag and a content digest. Consumer workflows pin the digest;
  a version tag may appear beside it for readability. `latest` may be a convenience alias but is never authoritative.
- The umbrella records the Dockerfile/container definition revision, Arch package source or snapshot, package list,
  build date, supported architecture, digest, and validation results for each published image.
- Publication uses least-privilege GitHub permissions, produces OCI provenance/metadata, and validates the pushed
  digest rather than only the local build result.
- Controlled updates begin with an umbrella change that rebuilds and validates all three layers. Consumer updates
  are explicit repository commits, one repository at a time, and retain the previous digest until the complete local
  and CI suite passes.
- Rollback is a normal commit restoring the previously recorded digest. Published image versions used by pinned
  commits must not be overwritten or deleted under the normal retention policy.

## Consumer workflow contract

Each migrated repository must provide a documented container command that developers can run locally. GitHub
Actions invokes the same repository-owned configure, build, test, format, tidy, QML, and architecture commands; the
workflow must not maintain a second dependency recipe.

Repositories use the narrowest shared layer that satisfies them. Additional packages require a thin
repository-owned image derived from an immutable shared-image digest, with only the extra packages and its own
smoke test documented. Before adding such an image, the repository must show why its need is not common to other
consumers.

Ubuntu jobs, where retained, are named portability jobs and run alongside—not instead of—the authoritative Arch
job. The current Ubuntu 24.04 Qt 5/Qt 6 job in `holonight-qt` remains compatibility evidence until the Arch pilot is
validated and the accepted matrix explicitly decides its long-term role.

## Dependency order

1. Define, build, smoke-test, publish, and document `ci-base`.
2. Build and validate `ci-qt6` and `ci-qt-compat` from the accepted `ci-base` digest.
3. Pilot immutable shared-image pins in `holonight-qt`; require its complete Qt 6 and Qt 5 compatibility suites.
4. Migrate `holonight-shell` after the pilot, including its repository-specific dependency builds and QML checks.
5. Migrate `holonight-ai`, `holonight-settings`, and `holonight-pkg-manager` individually, preserving each existing
   image until its replacement passes.
6. Confirm `holonight-config` Ubuntu coverage and decide whether an additional Arch matrix provides useful evidence.
7. Run umbrella integration review at the exact published consumer revisions and image digests.

Provider image digests and validation records must be published before a consumer work package becomes `Ready`.
Each consumer commit must be available from its canonical remote before its umbrella gitlink is updated.

## Integration acceptance criteria

- [ ] All three shared images pass their layer-specific smoke tests locally and after publication.
- [ ] Published images have immutable digest pins, provenance, package/tool version records, rebuild instructions,
      an update procedure, a retention policy, and a tested rollback path.
- [ ] `holonight-qt`, Shell, AI, Settings, and Package Manager run their complete suites on the shared images.
- [ ] Every migrated repository documents and passes the same commands locally in the pinned container and in CI.
- [ ] Duplicated authoritative dependency definitions are removed; justified repository-specific additions remain
      in thin derived images only.
- [ ] Existing repository images remain available until their replacements pass and are removed only through a
      separately reviewed cleanup.
- [ ] Ubuntu jobs are explicitly labeled as portability coverage; `holonight-config` retains its portable baseline.
- [ ] Participating submodules are clean and pinned to published commits whose workflows use recorded image digests.
- [ ] Umbrella integration records exact commands, image digests, workflow runs, results, and verification date.
