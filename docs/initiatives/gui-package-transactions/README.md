# GUI package transactions integration

The umbrella adopts published `holonight-pkg-manager` commit
`bf752c88e2b453bf65d65124bae4d12680ebc39f`. The authoritative local design,
requirements and task results are in the [package-manager SDD](../../../holonight-pkg-manager/docs/sdd/gui-package-transactions/SPEC.md),
[design](../../../holonight-pkg-manager/docs/sdd/gui-package-transactions/DESIGN.md) and
[manual results](../../../holonight-pkg-manager/apps/packages/README.md).

## Contracts and publication order

Explore requests installation and Installed requests removal of one package at a time.
The GUI uses the existing system D-Bus helper's PreparePlan, Execute and Cancel methods;
polkit authorizes changes in the privileged helper. The GUI and session update service
do not perform package changes themselves. The helper implementation, transaction core,
interface XML and installer ownership of service/policy artifacts are unchanged.

Dependency order is `holonight-config` → `holonight-qt` → `holonight-pkg-manager` → umbrella.
The package-manager commit was published and its remote main revision verified before
creating the umbrella pin commit. Existing umbrella provider pins remain:

| Component | Revision |
|---|---|
| holonight-config | `b115286c67561bcb34c8009da5098e3cb215f874` |
| holonight-qt | `c3c0911615b72104d19cdfe48a7a2f50a0edd81f` |

The umbrella CI image is aligned to the published AppStreamQt-capable digest in
`scripts/ci/image.txt`; the previous image lacked a required GUI build dependency.
This changes acceptance tooling only, with no host deployment.

## Verification

The component's final `task check` and `task check:integration` passed: 918 CTest cases,
zero failures, five namespace-dependent skips, both runtime styles, quality gates and
Release staging/runtime checks. Its standalone Qt pin is
`e9b5f79b9ab69a0d22ba6d326dc04f12055a45ab`; all seven human Arch/Plasma/polkit checks
and Escape dismissal/protection passed on 2026-11-11.

The provider-pin difference is checked using committed source archives for the exact
umbrella config/Qt gitlinks and the published package-manager commit, without sibling
working-tree substitutions. Focused verification covers the production Release build,
transaction and Explore views/models, both compiled runtime styles, policy fixtures and
relocated installed launches. On 2026-11-11, all 83 focused cases passed, along with
the Release build/staging and all four relocated startup selectors (default Holonight,
environment Fusion, command-line Fusion and external-config Fusion). Installed launches
loaded no provider build-prefix libraries. `task test:installer` passed 115 tests with
two skips. Full ecosystem acceptance remains the CI release gate; unrelated components
are not rebuilt locally for this pin update.

Detailed logs and generated evidence remain in ignored build directories.
