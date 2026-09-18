# Focused P03 kit recipes

For UQC-224, use the bounded observer-repair profile against an explicit published
umbrella commit. Preparation and release reject dirty checkouts, mismatched
HEAD/gitlinks, unpublished pins and package drift. Only configuration, provider,
observer and unchanged AI are freshly built; no other products or consumer suites.
Prior full suites remain recorded under their original revisions.

```sh
UQC_BASELINE=$(git rev-parse HEAD)
python3 docs/initiatives/unified-qtquick-controls/p03-kit/prepare.py --baseline "$UQC_BASELINE" --profile observer-repair --prior /tmp/holonight-uqc201-p03-xtndrklf
```

Use the printed new path as `KIT`. Run build.py, populate.py, verify.py, checks.py
and release.py as below. Before release, put the exact-path human handoff in the
kit README. The installed observer is exercised by 98 matrix processes, 49 on/off
equivalence pairs and the allocation/deferred-control regression. Isolated AI
startup/helper checks cover embedded default and Fusion at measured DPR 1.25.
Device bindings are inspected without opening devices or automating a compositor.
Named gates, source/binary provenance, hashes, exact-prefix restoration and
existing-path refusal are mandatory. Automated readiness does not close P03.

## Original full preparation profile (historical)


Run from the umbrella root at baseline `6f7af409a38b7a217fec38bf607e43446f86c07f`.
Use these retained umbrella recipes (from the preparation checkpoint) against that
baseline. Preparation refuses changed pins, package drift and unpublished heads.
Existing kits and archives must remain untouched.

```sh
python3 docs/initiatives/unified-qtquick-controls/p03-kit/prepare.py --baseline 6f7af409a38b7a217fec38bf607e43446f86c07f --profile full --prior /tmp/holonight-uqc201-final-dyxe1nl_
```

Use the printed `/tmp/holonight-uqc201-p03-*` path as `KIT` below. Its matching
`.cache` directory contains builds, command logs and outcomes. Supply an existing
`patchelf` executable via PATH or `HOLONIGHT_PATCHELF_EXECUTABLE`.

```sh
python3 docs/initiatives/unified-qtquick-controls/p03-kit/build.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/populate.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/verify.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/checks.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/release.py "$KIT"
```

Before release, populate the kit README from the focused handoff using its exact
new path and run documentation validation. `release.py` requires every named
check, fresh builds/installs, clean authoritative pins and unchanged inventories.
Prior full suites are explicitly labeled with their original revisions; package
drift blocks release. Plain Window and provider-free failures are separately
expected boundary evidence, never a passing shared-window assertion.

The actual workspace palette round trip does not prove AI Settings rendering.
The first light-time Settings construction and native controls remain human gates.
No full consumer suite or unrelated third-party runtime matrix is repeated.

## Settings scale-1 profile

This profile shares build, masking, device and restoration infrastructure, but
reuses no P03 binaries or suite results. Run from a clean umbrella checkpoint
that preserves every gitlink from planning baseline `52908523d5347100f59fd1edf3861330f5d09286`.
The baseline must be published; the preparation-tooling checkpoint may be local.
The prior archive supplies authenticated package inventory comparison only.

```sh
python3 docs/initiatives/unified-qtquick-controls/p03-kit/settings-prepare.py --baseline 52908523d5347100f59fd1edf3861330f5d09286 --prior-archive .cache/holonight-uqc201-p03-95__83sb/holonight-uqc201-p03-95__83sb.tar.gz
KIT=$(cat .cache/uqc201-settings-kit)
python3 docs/initiatives/unified-qtquick-controls/p03-kit/build.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/populate.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/settings-verify.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/settings-release.py "$KIT"
```

Supply an existing patchelf via HOLONIGHT_PATCHELF_EXECUTABLE if needed. Fresh
builds/installations run configuration → system services → shell configuration →
provider → Settings. Focused controls/import/installed checks precede full
provider and Settings suites. Both actual guided helpers run offscreen at measured
DPR 1, with bounded termination explicitly distinct from human normal closure.
Release rejects changed inventory, missing/failed gates, dirty sources or changed
pins, and checks exact-prefix restoration plus overwrite refusal. The
[two-run handoff](../BATCH8-SETTINGS.md) becomes the kit README with its exact path.
P03, fractional and Weather acceptance remain closed.

## AI scale-1 profile

Use the shared scale-1 entry points with explicit `--profile ai-scale1`. The
planning baseline must be canonically published before preparation; a clean local
tooling checkpoint may follow it without changing any gitlinks. Preparation
refuses dirty checkouts and changed pins. Build only configuration → provider →
AI, with provider and AI tests enabled. No palette-transition check is requested.

```sh
python3 docs/initiatives/unified-qtquick-controls/p03-kit/settings-prepare.py --profile ai-scale1 --baseline 9a33b504dbd1e0a772058cb15bced459ddc2682e --prior-archive .cache/holonight-uqc201-settings-p1ndqzdz/holonight-uqc201-settings-p1ndqzdz.tar.gz
KIT=$(cat .cache/uqc201-ai-kit)
python3 docs/initiatives/unified-qtquick-controls/p03-kit/build.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/populate.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/settings-verify.py "$KIT"
python3 docs/initiatives/unified-qtquick-controls/p03-kit/settings-release.py "$KIT"
```

Focused controls/composer/import/installed checks precede full provider and AI
suites. Record intentional credential-test skips. Installed selectors cover
embedded default, environment, command line and external configuration, with
source/build roots forbidden. Both actual guided helpers run offscreen at measured
DPR 1 with cleared inherited selectors, isolated offline profiles and collected
origins/outcomes. Automated SIGTERM is distinct from human normal closure.
Release requires every named gate, unchanged inventory, exact-prefix restoration
and overwrite refusal. The [two-run handoff](../BATCH8-AI-SCALE1.md) must identify
the exact released path before human use; previous kits remain immutable.
