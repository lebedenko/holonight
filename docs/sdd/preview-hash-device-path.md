# Retained Qt device hashing audit

The audit explains the existing SHA-256 diagnostic without changing production
behavior or generating measurements. Its inputs are a completed sealed run and
that run's passing independent verification; its output must be a fresh directory.

`scripts/audit-preview-hash-device-path.py --evidence RUN --verification JSON
--output DIRECTORY` checks consumed bindings, snapshots raw rows, and calculates
five-sweep block means and signed per-ordinal contributions. Exact integer sums
are retained before conversion to milliseconds. No adjacent-sweep pairing or file
exclusion is allowed. The original evidence and historical attempts are immutable.

The auditor compares cached package members with host Qt hashes/build IDs and
historically sealed debug symbols. It uses supplied retained local Git repositories without network fallback. The recipe must match `.BUILDINFO`;
the Qt Git archive and packaging patches must match recipe checksums. Recipe
scripts are never executed. Source reconstruction prepares a disposable repository using the versioned
policy described below. Missing exact provenance limits source conclusions;
consumed-evidence drift blocks the audit. Every failure after destination creation
retains a sealed partial assessment.

Primary source Git objects, revisions, URLs, archive checksums, patches, frozen
harness citations and matched disassembly remain in the evidence directory.
The independent stdlib-only checker imports no auditor code. It replays raw rows,
reconciles each signed file contribution, checks consumed seals and verification
bindings, re-extracts package members, checks ELF/debug identities, reproduces
patch provenance and disassembly, and checks citation hashes and inclusive ranges.
This intentionally duplicates arithmetic with a different traversal to detect
reporter mistakes and tampering after resealing.

Acceptance requires focused fixtures for signed arithmetic, empty files,
missing/duplicate ordinals, identity/source/citation mismatches, collisions and
sealed partial failures; a passing independent check of the retained audit; and
whitespace checks. Native builds, workload recordings and unchanged prior test
results are outside this step. The resulting report distinguishes structural API
expectations from observed durations and makes no production savings estimate or
optimization choice. Resolving an upstream source checksum mismatch remains a
source investigation, not authorization for another benchmark.

## Makepkg archive policy correction

`--prior-audit DIRECTORY --prior-verification JSON` are paired options. The
passing verification must bind the prior sealed audit. Its retained Git repositories
are copied into the fresh destination before changing attributes; automatic selection
of an arbitrary earlier cache is no longer used.

New audits record `makepkg-git-v1`. The cached pacman package must match the
installed pacman version in Qt's `.BUILDINFO`; its identity, Git helper and optional
`etc/makepkg.d/gitconfig` are retained without executing packaging scripts. The
archive uses isolated global/system configuration and the helper's
`* -export-subst -export-ignore` override. The independent checker copies the
retained repository and reproduces this policy; missing policy metadata on historical
audits retains ordinary Git attributes. Unknown policies and policy downgrades fail.

The historical reconstruction policy requires the unchanged archive checksum and applies two packaging
patches followed by four commit diffs in recipe order, with `--fuzz=0`. Additions
and deletions are explicit. A failed patch retains output, partial file hashes and
an explicit source limitation, which the checker independently reproduces. Exact
source citations are selected by function signatures rather than fixed line ranges;
they are emitted only after successful reconstruction. A failed gate does not
authorize accepting approximate sources, changing checksums or retrieving more inputs.


## Recipe preparation policy

New reconstruction records `recipe-prepare-v1` independently of the unchanged
`makepkg-git-v1` archive policy. Historical records without reconstruction policy
retain their original replay rules, including zero-fuzz for makepkg archives.
Unsupported policies and inconsistent preparation metadata fail verification.
Acquisition now requires retained local repositories; no clone or fetch uses the network.

Preparation copies the retained object store into a disposable repository initialized
without templates, hooks or inherited Git configuration. It compares starting archive
contents, executable bits and symlinks before changes. Git/GNU patch executable hashes,
versions and matching `.BUILDINFO` entries are retained. The original two patches run
in recipe order with ordinary GNU patch behavior. Only cflags' reviewed first gcc-base
hunk at line 40 may use fuzz 1. Independent whole-file expectations require unique
preimages and preserve the differing `QMAKE_CFLAGS_APP` context unchanged.

The four retained commits run as ordered `git cherry-pick -n` commands. Preparation
records normalized commands, return codes, stdout/stderr, before/after file hashes
and executable bits, and hashes of staged and working-tree binary diffs. Conflicts
stop preparation without resolution. Retained partial source contents and operation
results are replayed in a separate temporary repository by the checker, which imports
no auditor code. Only passing preparation permits exact-source function citations.
Exactness concerns retained prepared source contents, not reproducible compilation
or observed runtime branch selection. Failed attempts remain sealed and historical.
