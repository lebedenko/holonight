# Contributing

Use `task build` and `task test` for incremental native CMake/CTest work. Native builds
consume installed packages; use `CMAKE_PREFIX_PATH` for an explicit development prefix.
Use `task format` for the pinned formatter and `task check` for container acceptance.
Run `task check:integration` for installation/runtime changes. Container builds use
fresh build/prefix directories, separate from `build/dev` and `build/release`.
clangd reads `build/dev/compile_commands.json` directly.

Umbrella builds, container builds and clang-tidy use all available CPUs by default.
Set `JOBS=4 task build` or `JOBS=4 task check` to override the job count. Container
acceptance detects CPUs inside Docker and logs the selected count. Native component
builds use Ninja defaults; limit them with `CMAKE_BUILD_PARALLEL_LEVEL=4 task build`.
Native ecosystem tests use private D-Bus sessions without host service activation.

Routine changes need tests and a commit explanation; update user documentation when
behavior changes. Substantial designs need one local SDD describing intent, decisions,
interfaces and acceptance. Cross-project changes need one umbrella note linking local
designs and stating contracts, dependency order and integration checks. Historical SDDs
remain historical. No separate planning, readiness, handoff or closure commits are required.
Keep routine logs and generated evidence in ignored build directories or CI artifacts.
Provider and consumer implementation may proceed together; publish providers before
consumer commits that reference them. Update umbrella pins per coherent milestone.

Use Conventional Commits. Preserve component boundaries and installed-package tests.
The umbrella owns coordinated installation and conservative uninstall.
