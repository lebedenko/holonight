# Focused P03 kit recipes

Run from the umbrella root at baseline `6f7af409a38b7a217fec38bf607e43446f86c07f`.
Use these retained umbrella recipes (from the preparation checkpoint) against that
baseline. Preparation refuses changed pins, package drift and unpublished heads.
Existing kits and archives must remain untouched.

```sh
python3 docs/initiatives/unified-qtquick-controls/p03-kit/prepare.py --prior /tmp/holonight-uqc201-final-dyxe1nl_
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
