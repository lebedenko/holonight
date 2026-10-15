# CMake, one container, proportional design notes

The umbrella and 18 component repositories remain independent. CMake owns dependency
requirements and package discovery; Task provides short aliases. The shared Arch image
owns acceptance tools and external development packages. Product APIs and runtime
behavior are unchanged.

The pilot workflows are documented in [Config](../../../holonight-config/DEVELOPMENT.md)
and [Files](../../../holonight-files/DEVELOPMENT.md). Other components use the same
contract, retaining their own product tests. See [contribution rules](../../../CONTRIBUTING.md)
and the [image recipe](../../../packaging/ci/README.md).

## Shared contracts

- `dev` enables tests and writes `build/dev/compile_commands.json`; `release` stages
  optimized binaries. Native CMake builds never download dependencies. Installed packages
  are discovered normally, with `CMAKE_PREFIX_PATH` for additional prefixes.
- `scripts/ci/image.txt` contains an immutable image digest. Update all references
  together when deliberately adopting a verified replacement image.
- `scripts/ci/providers.json` is an ordered list of source revisions and necessary build
  options. Providers are installed with ordinary CMake into a disposable prefix.
  `source_only` is reserved for the Icons renderer regression against Qt source.
- `task check` runs the repository's `scripts/ci/check.sh` through the container launcher.
  Build, tests, formatting, clang-tidy, applicable QML checks and REUSE must succeed.
  Missing tools and failed commands return nonzero.
- `task check:integration` additionally runs `scripts/ci/integration.sh`: Release staging,
  installed consumers, configuration variants and applicable isolated runtime regressions.
  GitHub invokes this same entry point and stores its logs.
- Sources and images may be reused; acceptance builds and installation prefixes start
  fresh. Logs and generated evidence remain under ignored `build/` or CI artifacts.
  No compatibility fingerprints, dependency profiles, compilation-database merging or
  binary cache qualification are part of acceptance.

## Coordinating provider and consumer work

Use `task check -- --siblings /path/to/umbrella` in a component to test current provider
checkouts, including edits. The umbrella's native `task build` installs current siblings
into `build/integration/prefix`; `task test` also runs their tests.

Umbrella container integration defaults to its exact gitlinks. Explicit
`task check:integration -- --siblings .` selects current working trees instead.
Publish provider revisions before consumers that pin them, then update umbrella pins
once per coherent integration milestone. Source export tests enforce the distinction
between committed gitlinks and working copies.

The installer maintains dependency order in `scripts/install.sh`. It checks a short
maintained Arch package list, then relies on each component's CMake configuration for
versions and capabilities. It builds against host packages, stages every component,
checks ownership and collisions, and preserves modified files during uninstall.
QMarkdown stays separately package-managed and outside umbrella ownership.

## Acceptance

Verify standalone container checks, native builds with installed packages and explicit
prefixes, failing dependency/test/format/static-analysis gates, provider-consumer working
copies, exported-package tests, runtime regressions, and disposable-root installation,
upgrade, collision and uninstall behavior. Installation/runtime changes and umbrella
integration require `task check:integration`.

Historical SDDs remain historical. Substantial future designs need one local note;
cross-project work needs one umbrella contract note. Routine fixes need tests and a
commit explanation. Separate readiness, handoff, publication and closure documents are
not required.
