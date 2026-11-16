# Separate Qt hashing chunk-size and buffering effects

This bounded diagnostic uses installed Qt Core SHA-256 and the frozen 60-file,
87,215,960-byte manifest. It binds exact-source audit
`preview-hash-device-path-20261116-15`, its passing independent verification,
and the prior throughput run's complete payload/provenance chain. Destination
collisions and consumed-input drift fail closed. No production change is selected.

## Arms and execution

The fixed order is device buffered, device unbuffered, streaming 1 KiB buffered,
streaming 1 KiB unbuffered, streaming 64 KiB buffered, streaming 64 KiB unbuffered,
memory 1 KiB and memory 64 KiB. File arms use ordinary QFile; unbuffered uses
ReadOnly | Unbuffered. Qt's exact-source device loop requests 1 KiB.

One excluded warm-up per arm precedes eight blocks. Block i rotates the arm
order left by i, with three consecutive sweeps per arm. All sweeps retain manifest
ordinal order, including empty files. There are 192 measured sweeps, 11,520 file
rows and 16,745,464,320 logical bytes. Eight warm-ups and eight counting sweeps
are separate. There are no retries, cache drops, CPU pinning or governor changes.
No concurrent builds or tests run during measurement.

The host Release binary passes native correctness before timing. One single-threaded
process performs timing, then the same binary runs once in counting mode. Each
process has a 180-second limit, each sweep 30 seconds, followed by five seconds
each for termination and forced-kill cleanup. Validated retained payload is capped
at 128 MiB. Process groups and cleanup records follow the established throughput
runner's helpers. Partial failures retain raw output and unfinished schedules and
block performance interpretation.

Initialization, combined reads/hash updates and finalization have separate timers.
Opening, reusable buffer allocation, preloading, common EOF/error/position and byte
validation, digest comparison and output are outside these timers. Qt device API
internal checks remain in its timer. File-streaming loops differ only by chunk size
and open flags. Every arm must match SHA-256 and byte count; file arms also require
error-free EOF and final position equal to the expected size.

Counting uses a QFile subclass forwarding readData and records joint requested /
returned size histograms. Streaming loops count public reads (including terminal
EOF read) and hash updates; memory loops count updates. Device public-read and
hash-update counts are null, because they remain unobserved. Counting verifies
bytes and digests again. These are Qt-level calls, never syscall counts; the
subclass in another process cannot prove identical uninstrumented branch selection.

## Analysis and evidence

Prespecified contrasts are 1 KiB versus 64 KiB within each buffering mode,
buffered versus unbuffered within each file interface, device versus explicit
1 KiB within each buffering mode, and memory 1 KiB versus 64 KiB. Each contrast
uses three-sweep block means. Signed per-file integer sums reconcile exactly before
division by three. Retain every block's signed magnitude and duration ratio
(left / right); positive difference means left takes longer. Disagreeing directions
are inconclusive. Pooled throughput is descriptive. Effects need not be additive;
no adjacent-sweep pairing or memory subtraction estimates exact I/O cost.

Retain preregistration, source/tool snapshots, command/flags, host and CPU identity,
dependency hashes/build IDs, binary/linkage and both process mapping identities,
raw timing/counting output, histograms, summaries and cleanup. A separate
stdlib-only checker imports neither runner nor reporter. It replays coverage,
counts and arithmetic and revalidates seals, source snapshots and consumed bindings.
Focused Python fixtures cover schedules, separation, coverage, signed arithmetic,
histograms, malformed output, cleanup, collisions, drift and resealed tampering.
Native tests cover standard/empty vectors, both chunk boundaries and partial chunks,
all eight arms and counting equivalence, missing/open/read errors and unexpected
zero reads. Verification is focused fixtures, native correctness, one diagnostic,
independent final verification, snapshot and whitespace checks. Unaffected prior
verification is reused. No hardware dispatch, statistical significance, exact
elapsed-time decomposition or whole-preview gain is inferred.
