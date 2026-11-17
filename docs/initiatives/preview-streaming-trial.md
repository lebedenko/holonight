# Private buffered runtime hashing trial

The approved experiment tests whether feeding Qt SHA-256 through a reusable 65,536-byte
buffer improves startup with frozen qualification C. It changes no production repository,
deployment, historical qualification, or historical evidence. The accepted input review is
`build/preview-identity-review-20261117-03`, seal
`5856c6e014e06c2a356baddb078b39ae79f0e82af4a24eacf7957e2cd7705ac9`.
See [identity baseline](preview-identity-baseline.md) for the prior identity boundary and
[contribution guidance](../../CONTRIBUTING.md) for proportional verification.

## Interfaces and provenance

[Trial runner](../../scripts/run-preview-streaming-trial.py) exposes `prepare --output`,
`build --package --output`, and `execute --built --output`. Each output must be fresh,
beneath ignored `build/`, and separate from its inputs. Use `build/preview-streaming-trial-*`
with advancing suffixes on collision. Execution consumes a build only once; an exclusive
sibling execution marker prevents retries. Tools, the protocol, consumed identities,
complete source and harness inventories, and the retained `3200x2400.png` are frozen.

[Read-only evidence module](../../scripts/preview-streaming-trial-evidence.py) binds the
accepted review and its unchanged retained provenance. Both arms copy complete frozen C
sources and harness sources. Control keeps `QCryptographicHash::addData(QIODevice*)`.
Only candidate `verification.cpp` changes: one reusable buffer per runtime verification,
short positive reads continue to EOF, negative reads and unexpected zero reads fail,
byte count must match, and the original digest comparison/rejection remains. Inventory,
ownership, path, generation, and lifecycle checks remain byte-for-byte intact.

Both native Release builds use four jobs, separate prefixes, and installed providers for
consumers. Runtime preparation uses each arm's matching helper. Dependency payload
membership and bytes must agree except the candidate helper and its manifest identity.
Commands, compiler, caches, linkage, ELF identities, manifests, host dependency hashes,
and environment are retained. These are new builds: input identities establish neither
historical nor uncaptured loading identities.

## Preregistered measurement and decision

Run 202 fresh harness processes with `startup`, `count=1`, and offscreen Qt. Exclude one
warm-up per arm. Ten blocks each contain ten observations per arm. Even blocks run
control then candidate; odd blocks reverse that order. There is no recording, cache
flushing, affinity change, artificial load, or instrumentation in timed binaries.

Reuse the existing bounded process primitive: workload deadline 30 seconds, shared
five-second process/descriptor/scope cleanup budget. Protected staging and cleanup
are authorized separately outside workload timing. The frozen conservative installer
retains ownership, collision, lease, and uninstall checks. Cleanup checks the full staged
tree before removal. Partial or modified staging is retained rather than force-removed.

Stop on the first execution, correctness, identity, or cleanup failure. Seal partial
observations and preserve the unexecuted schedule. Never retry or adjust sample count.
Compute separate first/final median and nearest-rank p95 over each arm's 100 measured
samples. Report candidate-minus-control block medians/p95s and negative/zero/positive
sign counts as descriptive evidence.

Recommend later production work only with complete valid integrity evidence, both
startup p95 improvements at least 5 ms, and neither median regressing. Otherwise the
proposal is **Deferred**. Incomplete or invalid evidence is **Evidence insufficient**.
No historical timing transfer, capture-overhead correction, or revision of **78/80** is
permitted. A favorable decision authorizes no production change in this task.

## Verification and acceptance

[Synthetic tests](../../tests/test_preview_streaming_trial.py) disable process execution
and check schedule arithmetic, warm-up exclusion, quantiles, signs, decision boundaries,
collisions, conflicting bindings, drift and resealed source tampering.
[Native loop tests](../../tooling/preview-streaming-trial/hash-loop-test.cpp) execute the
[exact candidate loop](../../tooling/preview-streaming-trial/hash-loop.inc) against real
files and controlled short/error/zero-read devices: empty input, chunk boundaries,
truncation, extra bytes, read errors, zero reads and digest disagreement. Before timing,
each arm must pass focused runtime verification, generation and cleanup tests, and an
installed-package consumer check. Reuse unchanged historical verification; no full
ecosystem acceptance or earlier investigation reruns.

[Independent verifier](../../scripts/verify-preview-streaming-trial.py) accepts an evidence
directory and separate fresh result `--output`. It imports neither runner nor build recipes,
replays complete private source membership, verifies provenance, build/test identities,
staged payloads and raw process/sample bindings, and independently recomputes statistics
and decisions. Seals cover complete artifact membership, including partial evidence.
Acceptance requires passing independent verification, explicitly complete assessment,
and a reported performance decision. Findings, raw observations, statistics, block
comparisons, identities, native correctness, integrity checks and seals remain in the
ignored experiment directories. Finish with documentation-link and whitespace checks.
