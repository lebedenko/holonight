# Preview sandbox experiment evidence

This tooling establishes fixed Release baselines for the preview-overhead work.
It does **not** implement or qualify session reuse, runtime-generation reuse, or
prestarted workers. Experiment 0 remains incomplete until phase attribution,
helper/capture counters, cleanup sampling, and the actual grid scheduling control
are added. No candidate retain/reject decision can be made from this harness alone.

## Reproduction

From the umbrella root:

```sh
python3 scripts/preview-experiment-baselines.py --jobs 4
```

The command prints a unique ignored `build/preview-experiments-*` directory. It
archives historical benchmark sources, samples, binaries, package prefixes, build
metadata and traces before building anything. `provenance.json` records file
hashes, modes, symlinks, archive hashes, toolchain versions and full Git revisions.
Failed attempts remain in their own directories with `FAILED.txt`; runs never
resume or overwrite them.

The complete archived pre-isolation File Browser tree matches `caec685`, which
defines A. B uses File Browser `2f86c9b`, Images `c1f6da5`, and Thumbnails `9462bac`.
A uses the same Images/Thumbnails revisions through their in-process interfaces.
Both build with `/usr/bin/c++`, Ninja and `CMAKE_BUILD_TYPE=Release`, installing
Images, Thumbnails and File Browser Core/Preview in that order into independent
prefixes. Both isolated bundles are explicitly prepared from host dependencies.
Historical Debug and unspecified-configuration measurements are not comparison
inputs. Application QML and PreviewQuick are not built by this baseline script.

For each baseline, configure the same installed consumer harness, substituting
the absolute evidence directory for `EVIDENCE`:

```sh
cmake -S tooling/preview-benchmark -B EVIDENCE/A/harness -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DISOLATED=OFF -DCMAKE_PREFIX_PATH=EVIDENCE/A/prefix
cmake --build EVIDENCE/A/harness
cmake -S tooling/preview-benchmark -B EVIDENCE/B/harness -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DISOLATED=ON -DCMAKE_PREFIX_PATH=EVIDENCE/B/prefix
cmake --build EVIDENCE/B/harness
python3 scripts/measure-preview-experiments.py EVIDENCE
```

Native execution requires the actual user systemd manager and namespace support;
an agent/container sandbox may prevent cleanup verification. Such failures are
retained, not accepted as successful measurements. Nothing is installed into the
host prefix, published, or pinned by these commands.

## Measurement meaning

The default run alternates ten blocks of ten samples per case and implementation,
reversing A/B order in every second block. Each process uses its own temporary
application cache and pre-copied source files. Deterministic red 160×80 and
1600×1200 PNGs, a 3200×2400 textured PNG, and the provider's fixed EXIF orientation-6
JPEG are generated before timing and hashed once. Fixture generation and source
copies are outside timing; the host page cache is not flushed. These are fixed
bytes shared across the new comparison, not recovered bytes from the historical
benchmarks' deleted temporary fixtures.

| Case | Setup and timed operation |
| --- | --- |
| `first` | New service, first raster request; service construction precedes timing |
| `uncached` | Successful seed request, then a different uncached source on that service |
| `disk` | Successful request, destroy service, revisit with a fresh decoded-memory cache |
| `memory` | Successful request, clear selection, revisit on the same service |
| `upgrade` | Pane at 256×256, activate Quick Look at 1280×960; small sources need no new decode |
| `burst` | Twenty distinct superseding selections, then the final target, timed from the first selection |
| `grid-decode` | Synchronous 128×128 grid decoder call; **not** the grid scheduler control |

`changed` signals observe first pixels and final completion separately. Existing
pane pixels do not count as first upgraded pixels when more resolution is needed.
Event processing polls every 100 microseconds, so very short results include that
observation overhead. This measures service delivery, not a rendered QML frame.

Every requested sample remains in raw JSON. Missing times use `-1`; summaries count
missing observations separately instead of treating them as zero. Wall-time
statistics include failures. Signal-time statistics describe observed events only
and must be read with failure/setup-failure/missing counts. A final signal on a
failed request is error completion, not successful metadata delivery. The harness records
errors and a separate ten-second harness timeout without changing the service's
three-second deadline. Superseded selection counts are issued requests, not proof
that each request reached a particular cancellation phase.

Successful samples without both observations are counted as invalid. The runner
writes its full report before returning failure for failed requests, setup failures,
harness timeouts or invalid successful observations. An affected case can be rerun
using `--scenario upgrade --harness-directory harness-v2` after building the corrected
harness into fresh `A/harness-v2` and `B/harness-v2` directories. Preserve earlier
binaries and raw results; record exclusions explicitly when combining evidence.

`getrusage` CPU and maximum RSS values cover the whole block, including setup and
shutdown. Reaped-child values are not an aggregate helper-tree memory measurement
and do not establish idle footprint, per-request CPU, or cleanup latency. No
tracing or detailed resource polling occurs during these runs. A/B have no ready
workers; candidate readiness still needs explicit instrumentation.

The harness currently checks successful image delivery and setup completion. It
does not replace exact-pixel, protocol, mutation, cancellation, package-relocation,
or Files/chooser rendered-acceptance tests. Existing consumer container failures
remain recorded in the umbrella isolation note.

## Focused tooling checks

```sh
python3 -m unittest discover -s tests -p test_preview_experiment_tools.py
clang-format --style=file:holonight-file-browser/.clang-format \
  --dry-run --Werror tooling/preview-benchmark/main.cpp
```

Tests cover failure denominators, missing observations, nearest-rank p95,
deterministic valid PNG fixtures, and evidence inventory sensitivity to byte,
mode and symlink changes.
