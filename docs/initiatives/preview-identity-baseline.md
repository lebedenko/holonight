# Identity-bound startup baseline

This is a new diagnostic population using the retained qualification A-fixed and C
harnesses and runtime bytes and the `3200x2400.png` fixture. It cannot recover
historical loading identities, revise **78/80**, or select an optimization. The
[applicability audit](startup-validation-applicability.md) remains historical.

## Preparation boundary

[Preparation](../../scripts/prepare-preview-identity-baseline.py) imports only the
[read-only evidence boundary](../../scripts/preview-identity-evidence.py). It binds
accepted audit 05's pinned seal and passing independent verification, reuses its
unchanged source and native/package verification, and checks complete historical
runtime membership, sizes and digests. A-fixed uses qualification A's corrected
harness and legacy `runtime`; C uses qualification C's harness and `runtime-final`.
Validation-instrumented binaries cannot substitute for either.

The package copies the binaries, runtime manifests/payloads and fixture, current
Python tools (including transitive execution support), installer/support modules,
focused tests and this protocol into a fresh disjoint ignored `build/` directory.
Installer identity describes **new staging only**, not the historical installation.
Sources are rechecked after copying. Collisions, overlapping inputs, symlink escapes,
conflicting bindings and drift fail closed. Blocked partial packages remain sealed.
A successful package means **prepared; execution capability unvalidated**. Preparation
never imports an execution recipe and launches zero builds, staging operations,
recorder rehearsals, recordings or workloads.

## Future execution

The [runner](../../scripts/run-preview-identity-baseline.py) has a dependency-injected
OS boundary so that the entire schedule and stop/cleanup protocol can be exercised
synthetically. Its native adapter reuses the existing gated-launch/control-ack
primitive, not an instrumented harness. Real execution requires later explicit
authorization and a passing capability rehearsal bound to the preparation seal,
recorder bytes, host/boot identity, ordinary desktop UID and exact protocol. Unsupported options,
permissions, metadata formats or identities block execution; there is no privileged
recorder fallback. A future authorized `rehearse` action runs only the four excluded
combinations in a separate sealed population; its independent verification must
pass before `execute` can consume it. Neither action is invoked during preparation.
Preparation does not validate this capability.

There are four combinations, in canonical order: A-fixed uncaptured, A-fixed
metadata-captured, C uncaptured, C metadata-captured. Each has one excluded warm-up.
Five measured blocks each contain five observations per combination. Block order
rotates left by the block index modulo four, then reverses odd blocks. Thus there
are **104 fresh harness processes, each with count 1: 100 measured observations and
four excluded warm-ups**. No retries occur. Startup success, setup, pixel and
metadata correctness, finite ordered first/final timings and worker cleanup retain
the qualification checks.

Run as the ordinary desktop user with offscreen Qt and private observation directories.
No cache flushing, CPU affinity, artificial load or environment tuning is permitted.
Each gated invocation has a 30-second deadline and shared five-second termination
budget. The native primitive conservatively includes recorder shutdown in its
reported elapsed duration. Staging uses a narrowly elevated worker only for disposable
`/run/holonight-identity-*` trees, marked with the package seal and execution owner.
The frozen installer copies A's legacy runtime and publishes C's protected generation;
the deployed runtime is never a destination. The complete outer tree records modes,
owners, generation names, selector contents and manifest bytes. Nested payload
membership is checked separately before execution and between invocations. Historical
source verification is reused; between invocations, recheck the sealed executable
package and current tool identities rather than replaying the historical analysis.

The first execution, correctness, recorder, identity or cleanup failure stops the
schedule. Evidence retains attempted counts, accepted observations, failure and
all unexecuted schedule entries. Cleanup checks exact ownership and the complete
staged identity, uses the installer's lease-aware C removal, and preserves modified
or partially staged trees rather than adopting or deleting them.

## Captured identity contract

Perf attaches to the gated PID before release. `enable` must be acknowledged before
releasing that same PID into the harness. Descendant tracking is inherited. Recording
uses `dummy:u`, `--no-samples`, mapping build IDs, task and namespace metadata,
the required `sample_id_all` event attribute, and the monotonic clock. Build-ID cache writes and automatic symbol
downloads are disabled. CPU samples, stacks and scheduler events are excluded.

Retain `perf.data`, raw exported metadata, gate identity, acknowledgement, release,
recorder stderr/shutdown and normalized process/fork, exec, namespace, mapping and
exit records. Explicit fork parentage, lifetime tokens and namespace transitions
bind mappings; timestamp proximity never establishes ancestry. PID reuse starts a
new lifetime; forked children inherit the parent's loading context before their
own exec. Missing exits, unavailable identities/build IDs, capture loss,
unsupported records, ambiguous candidate bytes or conflicting mapping bytes block
acceptance. Anonymous/non-file mappings have explicit exclusion records.

Captured warm-ups establish separate A-fixed/C dependency-path ledgers, with desktop
and sandbox scopes distinguished. Freeze ELF bytes, sizes, SHA-256 and available GNU
build IDs without running the binaries. New captures resolve exact build-ID-matching
candidates from the current execution's desktop paths and frozen sandbox payload;
ambiguous bytes block. This lookup is never used for historical recordings. Recheck
sources and frozen copies before and after every measured invocation. Unexpected
measured paths or changed identities block; repeated paths within a scope cannot
silently denote different bytes. The strict decoder supports little-endian ELF64
and Linux perf's build-ID MMAP2 metadata; other formats require a later reviewed
implementation, not a fallback that weakens identity checks.

## Reporting and verification

[Independent verification](../../scripts/verify-preview-identity-baseline.py) imports
neither preparation nor runner. It independently reconstructs schedule arithmetic,
checks bindings and snapshot membership, validates synthetic execution fixtures,
rejoins lifetime/namespace evidence, and recomputes all reporting arithmetic.

Report first/final median and nearest-rank p95 separately for each combination, plus
signed C-minus-A-fixed block comparisons within each capture population. Warm-ups
never enter these distributions. Captured mappings establish identities only for
captured executions; uncaptured loading identities remain unavailable. No overhead
correction, quantile subtraction across populations, historical timing transfer,
qualification inference or automatic authorization of streaming, validation reuse
or dispatch changes is allowed. Complete real execution means a verified new
baseline with these limitations; synthetic completion never means a real baseline.

Preparation acceptance uses only the focused synthetic suite, one fresh preparation
package and its independent offline verification, documentation links and whitespace.
Existing native/package results are reused. No native build or real workload is
necessary or authorized by this preparation step.

```sh
python3 -m unittest discover -s tests -p test_preview_identity_baseline.py
python3 scripts/prepare-preview-identity-baseline.py --output build/preview-identity-baseline-NEW
python3 scripts/verify-preview-identity-baseline.py build/preview-identity-baseline-NEW --output build/preview-identity-baseline-NEW-independent.json
```

The preparation-only acceptance artifacts are the
[sealed preparation report](../../build/preview-identity-baseline-20261116-03/REPORT.md)
and [independent result](../../build/preview-identity-baseline-20261116-03-independent.json).
The focused suite covers 33 synthetic cases, including binary perf fixtures and ELF
note parsing, with all real process execution disabled. These artifacts do not
attest real recorder or execution capability.
