# Startup evidence reconciliation — 2026-11-16

**Evidence insufficient.** All three existing optimization proposals remain deferred.
The retained evidence cannot prioritize one smallest unresolved observation across
these proposals. No candidate, experiment, build, recording, installation or fresh
qualification is prepared or executed.

The [offline assessor](../../scripts/assess-preview-startup-reconciliation.py) and
[independent verifier](../../scripts/verify-preview-startup-reconciliation.py) bind
remainder **04**, helper review **03**, completed validation **04**, CPU profile
**03**, verification-work audit **04**, hashing-mechanism **01**, practical-value
assessment **02**, and qualification provenance. The checker never imports the
assessor. The [read-only boundary](../../scripts/startup-reconciliation-evidence.py)
checks accepted seals, pinned passing verification records, consumed retained
identities, source citations, and frozen dependency provenance. Historical host
mappings are provenance, not a requirement to recreate the current installation.
Historical experiments and their passing native/package checks are reused.

The accepted [assessment 03](../../build/preview-startup-reconciliation-20261116-03/REPORT.md)
and [independent verification](../../build/preview-startup-reconciliation-20261116-03-independent.json)
retain the decision and its evidence bindings.
The machine-readable matrix preserves each question, result, population, limitations,
remaining uncertainty and consumed source/dependency identities. Warm-ups, setup,
standby, measured observations, instrumentation and profiling remain separate.
No diagnostic or standalone difference is subtracted from a qualification p95.

## What the investigations establish

| Investigation | Retained result | Practical limit |
| --- | --- | --- |
| Remainder 04 | Generation/runtime validation leads all 32 required C views; 150 measured observations / 300 endpoints, with six warm-ups separate | Temporal coverage, not attribution to a validation substep |
| Helper review 03 | Competing readiness/scope waits and dominant uncovered startup time; Evidence insufficient | Helper scheduler states do not describe the earlier validation interval |
| Validation 04 | Combined file reading/SHA-256 leads validation in both arms and all retained C selections; 600 measured observations, six warm-ups and 22 C setup groups separate | Separate execution; its durations and scheduler states cannot decompose remainder 04 |
| CPU profile 03 | Sampled userspace execution identifies hashing/dispatch; 20 profiled and 20 unprofiled measured observations, two warm-ups separate | Sample shares do not identify exact elapsed cost, kernel cost, a dispatch defect or a whole-preview saving; zero-sample windows are unavailable |
| Work audit 04 | 52 distinct service constructions each validate once | Matching payloads or addresses do not prove unchanged owner/generation identity or redundant verification |
| Mechanism 01 | Completed buffering/chunk-size contrasts and separate counting process | Qt-level counts are not syscall counts; hardware dispatch and exact I/O decomposition are unproven |
| Practical value 02 | Buffered device minus buffered 64 KiB streaming has seven positive and one negative blocks; all eight below 5 ms | Mixed direction; private A/B deferred; neither an upper bound nor proof that future savings cannot reach 5 ms |

Finer validation observations therefore **already exist in separate populations**.
The remainder discussion's missing per-file distinction is missing for its own
execution. It is not a reason to repeat the completed validation, CPU or mechanism
investigations. Their read/hash priority and sampled hashing execution provide
supporting context, never a substep decomposition of the newer observations.
Scheduler states, sample percentages and durations are not transferred between runs.
The [historical practical-value design](../sdd/preview-hash-value.md) records the
completed chain and its separate populations.

## Source relationship

The frozen baseline C `verification.cpp`, `generation.cpp`, `session_pool.cpp` and
`preview_service.cpp` match between validation preparation 04 and helper preparation
06 after normalizing **only the first generated trace-header include path**. Exact
path differences, hashes and unified diffs are retained in `sources.json`. There are
no other baseline residual differences in these four files.

The recorded C validation anchors locate 11 replacements in verification and 10 in
generation, including `read_hash`, `file_open`, runtime validation and protected
selection validation. The result retains these anchors and full baseline-to-overlay
diffs for both investigations, including their different instrumentation. Caller
construction/refresh and explicit refresh entry points remain visible in frozen
source citations. These relationships establish boundary compatibility only.
They do not establish timing equivalence, runtime-generation identity, identical
probe costs or interchangeable populations. Complete consumed inventories retain
the frozen dependency identities; matching source alone does not establish matching
runtime dependencies.

## Proposal dispositions and unresolved observations

- **Buffered 64 KiB streaming — deferred.** The mechanism is relevant to the frozen
  `hash.addData(&file)` path, but practical value is mixed and below the planning
  threshold in every retained block. The smallest proposal-specific gap is an
  identity-bound effect of the proposed loop inside the applicable startup validation
  boundary, with byte coverage, EOF/error handling, digest checks and rejection
  behavior preserved. Standalone timing cannot supply that observation.
- **Avoiding repeated validation — deferred.** Distinct service lifetimes do not
  establish redundancy. The smallest gap is evidence of repeated verification within
  one proven unchanged owner/generation, together with the integrity contract that
  would permit reuse. Current records demonstrate no such repetition. No weakened
  validation or caching policy is justified.
- **SHA-256 execution/dispatch — deferred.** CPU and mechanism investigations are
  complete. Sampled hashing execution does not prove unexpectedly slow execution or
  a faulty hardware/backend dispatch. The smallest gap is a specific avoidable
  execution/dispatch mechanism on the applicable frozen dependency path, with an
  integrity-preserving alternative. Repeating the completed broad investigations
  is not the next action.

An eligible candidate would require mechanism, applicability, preservation of the
integrity contract, and no unresolved contradiction in applicable evidence. Eligible
candidates would be ranked by direct evidence to the failed startup gates; ties or
missing evidence yield Evidence insufficient. None is currently eligible. Validation
is a justified investigation boundary, but that fact does not rank these three
proposal-specific gaps. The retained evidence cannot select a single smallest gap;
no experiment is specified.

## Qualification remains numerically failed

The frozen corrected-reference comparison still passes **78/80** gates. Both failed
gates concern startup of the 3200×2400 textured PNG:

| Event | A-fixed p95 | C p95 | Allowed C p95 (rounded) |
| --- | ---: | ---: | ---: |
| Pixels (`first_ms`) | 127.828 ms | 142.332 ms | 140.611 ms |
| Final metadata (`final_ms`) | 127.835 ms | 142.340 ms | 140.619 ms |

The exact unrounded reference values, allowances and excesses are derived from the
frozen summary in `qualification.json`. The gate is still regression
≤max(5 ms, 10% of reference p95). Numerical failure is established; insufficient
optimization evidence is a separate conclusion. The **5 ms candidate-planning
threshold** remains separate from qualification allowances and does not bound
possible savings. No threshold or historical result is changed.

## Verification

Run the focused synthetic tests, then choose a fresh disjoint destination under
ignored `build/` for the offline assessment and its independent verification:

```sh
python3 -m unittest discover -s tests -p test_preview_startup_reconciliation.py
python3 scripts/assess-preview-startup-reconciliation.py --output build/preview-startup-reconciliation-NEW
python3 scripts/verify-preview-startup-reconciliation.py build/preview-startup-reconciliation-NEW --output build/preview-startup-reconciliation-NEW-independent.json
```

New tools and tests are snapshotted, consumed hashes and inventories are rechecked,
collisions/overlap are rejected, and complete or blocked partial results are sealed.
Synthetic tests disable process execution and cover population separation,
unavailable versus zero, incompatible identities, conflicting evidence, unsupported
reuse/candidate claims, prohibited qualification subtraction, arithmetic tampering,
collisions, drift and sealed blocked failures. Native/package verification is reused
because no production source, dependency, package or installed interface changes.

The subsequent [qualification C applicability audit](startup-validation-applicability.md)
checks the failed qualification's own C source and payload against validation 04,
CPU profile 03 and the completed hashing chain. It preserves differing input bytes
and unavailable qualification generation/loading identities as separate relationships.
Source compatibility selects no optimization; qualification remains **78/80**.
