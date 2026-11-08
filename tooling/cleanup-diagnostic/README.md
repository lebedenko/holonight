# Isolated cleanup diagnostic probe

This installed-package consumer is diagnostic evidence only, never a qualifying
latency benchmark or a replacement for fixed B. Build against a freshly installed
host-native Images package:

```sh
cmake -S tooling/cleanup-diagnostic -B build/UNIQUE/probe -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/absolute/diagnostic/prefix
cmake --build build/UNIQUE/probe
build/UNIQUE/probe/cleanup-diagnostic /absolute/diagnostic/runtime \
  build/UNIQUE/operations.jsonl frozen/160x80.png frozen/1600x1200.png \
  frozen/3200x2400.png frozen/oriented.jpg
```

The output must not exist. Supply the four already frozen fixtures; this tool
never regenerates or writes them. Each cycle rotates through one fixture and
performs inspection, source decoding to a 1024×1024 bound, and decoding a cached
PNG encoded from the returned pixels. Limits match File Browser's raster policy.
Each operation has a three-second cooperative cancellation timer. Execution needs
the actual user systemd manager and namespace support.

The run stops at 1,000 cycles or ten minutes (no new operation starts after the
wall budget), or immediately after the first client-returned CleanupFailure.
An in-flight operation may finish its bounded cleanup beyond the wall budget.
JSONL records include operation/cycle IDs, input SHA-256, runtime/provider outcomes,
elapsed time and the complete failure diagnostic string. For cached decoding the
hash identifies the actual encoded PNG; the source is identified by the matching
cycle's source record. There is no retry or additional manager cleanup attempt.
Missing runtime/fixtures or output creation failures return 2; cleanup failure
returns 1. Other operation failures remain visible in the records.

The November 8 run is documented in the Images isolation design and umbrella note.
