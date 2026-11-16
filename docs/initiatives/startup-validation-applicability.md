# Qualification C startup-validation applicability — 2026-11-16

**Evidence insufficient.** The offline audit connects qualification **C** to
accepted reconciliation **03**, validation **04**, CPU profile **03**, and the
completed hashing investigations. All three optimization proposals remain deferred.
No experiment, workload, recording, build, installation or qualification is prepared
or run. Native/package verification is reused because production inputs are unchanged.

The [auditor](../../scripts/audit-preview-startup-applicability.py),
[independent verifier](../../scripts/verify-preview-startup-applicability.py), and
[read-only retained-input boundary](../../scripts/startup-applicability-evidence.py)
keep this audit separate from historical reports. The verifier never imports the
auditor or executes historical preparation recipes. Audit-time pins checkpoint
retained historical records before analysis; only identities recorded inside those
records attest their children. A newly computed hash is not historical proof.

## C source path and execution provenance

The earlier source-equivalence report proves A/A-fixed equivalence. This audit
explicitly binds qualification C's complete source inventory and binary/runtime
inventory. It compares C through CU, CT, delivery v3-C/v4-C and validation
baseline-C/validation-C, including runtime verification, generation construction
and refresh, session-pool and service callers, declarations, and the startup harness.

Recorded C tracing hunks and C-specific delivery/validation replacements are replayed
in memory. Only exact generated include paths are relocated. Every file retains
paths, exact hashes, anchors, differences and residuals in `sources.json`. The
independent verifier reconstructs the complete recorded C tracing diff and reverses
the ordered literal replacements. Unexplained edits block acceptance. Qualification
to CU harness differences are retained as differences, without adding them to the
instrumentation allowlist. Production source compatibility establishes mechanism
relevance, without timing or binary equivalence.

The saved execution runner selects `C/runtime-final`, passes the C built helper to
the generation installer, and runs the C harness against a disposable protected
runtime. Its provenance records the fixture digests, ordinary uid, 100 samples,
ten-sample blocks, separate warm-ups and fresh service/process recycling. The saved
runner unconditionally removed its transient runtime staging. The later
`runner-final.py` adds failure retention and differs from the actual saved runner;
`provenance.json` preserves the exact difference. The final tooling inventory must
not be used as an identity claim for the earlier execution runner. Its retained
snapshot is checkpointed by this audit, with no independent historical hash claim.

The qualification staging and loaded-dependency map are unavailable. The saved
runner imports an installer by workspace path, without freezing its implementation
in execution provenance. No current installer, host package or reconstructed `/run`
tree fills that gap. Missing retained required inputs, conflicting identities or
drift block acceptance; absent historical transient staging is an explicit
limitation, not a reconstructed fact.

## Payload and dependency relationships

Both nested input runtime manifests have **60 files**. Validation C differs from
qualification C in QtCore, QtGui, **libdbus-1** and the helper. The Qt6DBus library
is a separate file. Full path, size and SHA-256 comparisons are retained for both
baseline C and instrumented validation C in `payloads.json`.

Equal library size or version does not establish binary identity. Frozen provenance
establishes different bytes for QtCore, QtGui and libdbus-1 but does not establish
why those bytes changed. The helper comes from a distinct instrumented build;
that explains a build distinction, without explaining every changed binary byte.
`dependencies.json` retains later CPU mapping/build-ID records and the available
explanation or its absence for each file.

`mappings.json` compares the CPU protected-generation inventory with the nested
validation payload and separately binds the standalone mechanism's dependency
inputs and recorded loaded mappings. Outer inventories contain generation paths,
manifest/control records and directories; those are not nested runtime file lists.
Their file sizes are unavailable where the historical inventory records only
hashes. Recorded CPU and standalone identities cannot establish qualification
loading or an unchanged generation across executions.

## Applicability and next action

`matrix.json` separates validation-mechanism compatibility, runtime input identity,
protected-generation identity, actual loaded dependencies and execution conditions.
Each relationship has evidence, a limitation and one status: **exact identity**,
**compatible under recorded transformations**, **different**, or **unavailable**.
`populations.json` preserves reconciliation 03's measured, setup, warm-up,
instrumented, captured, profiled and standalone populations unchanged.

- **Buffered 64 KiB streaming:** relevant to the frozen file-read/SHA-256 boundary,
  but its seven positive and one negative standalone blocks are mixed-direction,
  all below the 5 ms planning threshold. This is neither an upper bound nor proof
  of an applicable startup gain. Byte coverage, EOF/error handling, digest and
  rejection behavior still require an integrity-preserving applicable alternative.
- **Avoiding repeated validation:** 52 distinct service constructions each validate
  once. Within-generation redundancy and an integrity contract authorizing reuse
  remain unproven. Matching payloads or addresses cannot supply either fact.
- **SHA-256 execution/dispatch:** CPU and mechanism investigations are complete.
  They establish sampled hashing execution, without demonstrating an avoidable
  dispatch defect or an applicable integrity-preserving replacement.

Read/hash priority and sampled hashing execution transfer only as qualitative
supporting context. No durations, scheduler states or sample percentages transfer
between executions, and diagnostic samples do not attribute qualification tails.
A candidate would require mechanism, applicability, integrity preservation and
resolution of contradictory evidence, then ranking by direct evidence to the failed
gates. Matching identities alone would not select streaming. Current evidence cannot
prioritize one smallest unresolved observation across the qualification
loading/generation gap and the three proposal-specific mechanism gaps. No experiment
is specified.

## Qualification and verification

Qualification remains **78/80**, under regression ≤max(5 ms, 10% of reference p95).
The two failed 3200×2400 textured PNG startup gates remain:

| Event | A-fixed p95 | C p95 | Allowed C p95 (rounded) |
| --- | ---: | ---: | ---: |
| Pixels (`first_ms`) | 127.828 ms | 142.332 ms | 140.611 ms |
| Final metadata (`final_ms`) | 127.835 ms | 142.340 ms | 140.619 ms |

`qualification.json` retains exact unrounded references, allowances and excesses.
No diagnostic difference is subtracted from these p95 values. The 5 ms planning
threshold is separate from the qualification allowance.

The accepted [audit 05](../../build/preview-startup-applicability-20261116-05/REPORT.md)
and [independent verification](../../build/preview-startup-applicability-20261116-05-independent.json)
record a sealed **complete** result with passing independent verification. Its seal
SHA-256 is `77a96dff3b8376ad14c112218b5251d9eecd5c6519c5d1d549f08a94272528ca`.
All **19 synthetic tests** pass, as do documentation-link and whitespace checks.
Earlier disjoint attempts and their seals remain retained; they are not accepted
in place of audit 05.

Focused synthetic tests disable process execution and cover C substitution and
unexplained edits, manifest membership, same-size/different-digest dependencies,
outer/nested scope, unavailable identities, population mixing, unsupported timing
and reuse claims, collisions, drift and resealed tampering. Tools/tests and consumed
identities are snapshotted; inputs are rechecked after analysis. Complete and blocked
partial attempts are sealed in fresh disjoint ignored `build/` directories.

```sh
python3 -m unittest discover -s tests -p test_preview_startup_applicability.py
python3 scripts/audit-preview-startup-applicability.py --output build/preview-startup-applicability-NEW
python3 scripts/verify-preview-startup-applicability.py build/preview-startup-applicability-NEW --output build/preview-startup-applicability-NEW-independent.json
```
