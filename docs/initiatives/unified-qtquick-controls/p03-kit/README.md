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
