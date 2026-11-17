# Native cache publication correctness, protocol v3

The [machine protocol](CORRECTNESS-v3.json) preserves v2's explicit required test
membership and adds ordered prerequisite groups and pinned fixture identities.
The [qualifier](qualify.py) keeps `--built … --output …`; the only approved fresh
attempt is `build/preview-cache-publication-correctness-20261118-02`. Collisions,
resumes, overlapping inputs and symlink escapes are rejected. Historical protocols,
verifiers, preparation tools and sealed attempts remain unchanged.

Before execution, freeze the complete schedule, native sources, tooling, protocol
and fixture generator. Copy protocol bytes verbatim and check the independent
verifier's protocol digest before launching any command. Both retained provider
arms must contain identical frozen Images `format-fixtures.py` bytes. Snapshot
that generator and run it as the first bounded, unprivileged schedule command.
Record its complete output inventory and require the protocol's fixture hashes,
including `sample.png`, `sample.jpg`, `sample.bmp`, `sample.tif`, `sample.webp` and
`sample.gif`. The fixture hashes were checked in a temporary directory in process
with the frozen generator and the host libwebp; synthetic tests forbid processes.
Both CMake configurations bind the same attempt-local fixture directory.

Reuse the pinned retained native Release providers and their installed packages.
Compile only correctness executables and focused consumers in fresh Release build
directories with four jobs. For each arm, run runtime verification, generation
ownership, cleanup, scheduling, pool lifecycle and selected Preview cases in six
ordered invocations. Filter order is not an execution-order guarantee. Follow
with mutable publication and consumer checks, protected-generation fixtures,
protected publication/Preview/session checks and the protected consumer.

Model workloads and consumers run as the desktop user. Only protected-generation
fixture tests and conservative staging/removal are elevated. Each process has a
600-second bound. Process-group termination, reaping and scope proof share one
five-second cleanup deadline. All cases must run and pass; skipped, disabled,
missing or duplicate cases block qualification. Stop on the first preparation,
compilation, validation, identity, correctness or cleanup failure. Only verified
owned cleanup may follow. Retain modified or unverifiable staging, raw output,
available XML, attempted/skipped/unexecuted cases and staging records.

The independent [v3 verifier](offline/verify_correctness_v3.py) imports neither
qualifier nor build implementation. It pins protocol bytes and reconstructs
commands, environment, cases, fixture bindings, cleanup obligations and outcome.
Synthetic records use the qualifier's production persistence path. A passing
verification of a blocked record confirms the blocker, not qualification.

Run exactly one frozen native attempt, followed by independent offline verification
into a fresh adjacent file. No source repairs, replacement runs, provider rebuilds,
warm-ups or diagnostic observations belong to this attempt. Both arms must pass
every gate and cleanup, with successful independent verification, for acceptance.
Overlap and candidate selection remain **Evidence insufficient**; diagnostic
execution stays disabled. Streaming and validation reuse remain **Deferred** and
historical qualification remains **78/80**. Portal and GRUB remain outside scope.
