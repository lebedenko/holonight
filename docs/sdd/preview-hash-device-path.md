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
historically sealed debug symbols. It searches supplied local Git caches before
retrieving primary Arch/Qt repositories. The recipe must match `.BUILDINFO`;
the Qt Git archive and packaging patches must match recipe checksums. Recipe
scripts are never executed. Source reconstruction applies retained diffs only to
an isolated source tree. Missing exact provenance limits source conclusions;
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
