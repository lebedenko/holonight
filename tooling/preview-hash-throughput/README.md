# Native SHA-256 diagnostic

Standalone Release harness using installed Qt Core and OpenSSL Crypto. This is a
bounded investigation of the frozen validator payload, not a production change or
performance qualification. The older hash experiment remains unchanged.

From the umbrella root:

```sh
python3 -m unittest discover -s tests -p test_preview_hash_throughput.py -v
python3 scripts/run-preview-hash-throughput.py \
  --audit build/preview-verification-work-20261115-04 \
  --verification build/preview-verification-work-20261115-04-independent.json \
  --output build/preview-hash-throughput-20261115-01
python3 scripts/verify-preview-hash-throughput.py \
  --evidence build/preview-hash-throughput-20261115-01 \
  --output build/preview-hash-throughput-20261115-01-independent.json
```

The runner refuses destination collisions and dependency/provenance drift. It
installs nothing. Its native correctness mode covers empty/standard vectors,
64 KiB boundaries, partial final chunks, multiple independent files, open and read
failures. Focused tests must finish before measurement; do not run other builds
or tests during the diagnostic.

Five cases each receive one excluded warm-up and 25 measured sweeps, in five
rotated blocks. Every sweep hashes all manifest ordinals independently. One
persistent process retains at most 128 MiB of validated inputs. File opening,
loading, digest checks and JSON output are outside the primary update timer.
Initialization and finalization are separate. Empty files retain rows and zero
logical bytes. File streaming uses identical QFile loops and reusable 64 KiB
buffers; memory streaming uses identical chunk boundaries.

`native.stdout` preserves every raw row and sweep completion; `native.stderr`
retains diagnostics. `summary.json` separates warm-ups, blocks and pooled counts,
nearest-rank p95 distributions and throughput ratios. Aggregate rates divide
summed bytes by summed update time. `REPORT.md` describes consistency across
blocks and remaining ambiguity. The historical audit has different probes/timers
and supplies context only. EVP provider and mapped library identities do not
establish Qt's provider or hardware dispatch.

The evidence directory includes preregistration, tool/source snapshots, CPU/host
identity, build commands/output, CMake cache, compile commands, binary identity,
linkage and mapped files. A failure seals partial evidence and uncompleted sweeps;
performance interpretation is blocked. The independent stdlib-only checker imports
neither runner nor reporter and recomputes raw accounting against the manifest.
Its result must be outside the evidence seal. Prior native, scheduler and CPU
profile verification is reused without repeating unrelated workloads.
