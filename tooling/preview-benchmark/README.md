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

## Experiment 0 attribution and scheduler evidence (2026-11-09)

The new tooling keeps the original A/B latency matrix frozen. **Experiment 0 is
still incomplete:** both the scheduler pass and the attribution pass stopped at
their first unexplained cleanup failure. Neither was retried; no extra manager
cleanup was performed. The separate resource pass completed. See the
[umbrella evidence note](../../docs/initiatives/image-isolation.md#experiment-0-missing-evidence-2026-11-09)
for counts, limitations, and the conditional next experiment recommendation.
The stopped scheduler pass repeated one fixture within each batch; it is explicitly
excluded from the requested mixed-fixture control. The corrected harness cycles
all four fixtures in each batch and has in-process smoke verification. No corrected
B measurement was started after the cleanup recurrence.

Fresh preparation and execution:

```sh
python3 scripts/prepare-preview-evidence.py --kind scheduler --jobs 4
python3 scripts/prepare-preview-evidence.py --kind diagnostic --jobs 4
# Use the separately printed package roots and the existing frozen fixture directory:
python3 scripts/run-preview-evidence.py SCHEDULER_ROOT FROZEN_FIXTURES --kind scheduler
python3 scripts/run-preview-evidence.py DIAGNOSTIC_ROOT FROZEN_FIXTURES --kind diagnostic
python3 scripts/run-preview-evidence.py DIAGNOSTIC_ROOT FROZEN_FIXTURES --kind resource
python3 scripts/report-preview-evidence.py RUN_ROOT
```

Preparation archives revisions into a unique build directory, applies the checked-in
`overlays/*.patch` only to diagnostic copies, and installs native Release packages.
D uses Images `a772a67`, File Browser `2f86c9b`, and Thumbnails `9462bac`; A/B retain
their frozen revisions. PreviewQuick is enabled for all three. The host HolonightQt
package is selected explicitly to avoid an incomplete user-local package. Commands,
compiler flags, source/overlay hashes, runtime manifests and executable inventories
are retained. Builds and runs never resume a previous evidence directory.
The executed D build retains its original equivalent JSON replacement overlays;
the final checked-in patches express the same edits with C++ formatting applied.
Its archived source and executable hashes describe the actual measured artifacts.

### Interpretation and bounds

`preview-grid-control` consumes the installed `ThumbnailProvider`, with **two
scheduler threads and 256-pixel boxes**. These are experimental controls, not a
change to host production defaults. Each batch uses 16 distinct source copies.
Cold batches create a fresh provider; warm batches seed and repeat on the same
provider; cancellation batches cancel the first 12 responses and await the other
four. Each batch cycles all four fixtures four times. The schedule alternates
A/B in blocks of ten per workload, targeting 100 batches per workload and baseline (600 total).

Started means the provider entered the instrumented decoder seam. Cancellation
counts are classified after draining: a cancelled response whose decoder was never
entered is counted before-start; one whose decoder was entered is counted
after-start. Neither count proves interrupted decoding. Finished responses and
validated non-null images within the 256-pixel box are counted independently.
All responses are kept alive through completion and pending work drains before
provider teardown. Warm seed results, runtime failures and diagnostics remain in
raw JSON. The controlled-barrier test additionally verifies cancellation after
entry, exact synthetic returned pixels, warm hits, destruction of an in-flight
response and complete draining. These are scheduler response measurements, not
rendered QML frames. `grid-decode` retains its separate synchronous meaning.

D records consumer dispatch, worker entry, memory/disk cache observations,
publication and delivery, and correlates synchronous provider operations with
consumer jobs. Inspect, source decode, and cached-PNG decode are distinguished;
in these frozen call paths cached PNGs reach the client through `QBuffer`, while
source files use `QFile`. Direct synchronous grid requests have no worker queue
interval. Parent phases cover capture, runtime validation, launcher/readiness,
request transfer, response receipt/validation, acknowledgement/exit and cleanup.
Helper provider execution includes format sniffing and provider work; it is **not
codec-only time**. Helper serialization is separate. Their intervals are on a
separate timeline and are never added to overlapping parent intervals. Unexplained
parent time is the outer duration minus the union of observed child intervals.

The diagnostic-only header buffers at most 16,384 records per process and reports
overflow. The parent retains at most 65,536 bytes of helper stderr per operation,
with an explicit truncation flag. Helper records flush after provider execution
and reply serialization; parent records flush after draining. Instrumentation
cost and helper stderr flushing can affect parent timings. Stdout framing and the
production wire protocol remain unchanged. Production sources gain no probes,
environment switches or public interfaces. Missing/truncated records, absent phase
intervals and missing resource reads are explicit, never zero-duration estimates.

Scope `cpu.stat` and `memory.peak` are read before acknowledgement permits helper
exit. The separate resource pass samples parent RSS and concurrent scope
`memory.current` at a requested 10 ms interval; actual timestamps and missing
process-discovery reads are retained. Report sampled concurrent peaks separately
from individual scope peaks; never sum independent maxima. The simultaneous
RSS-plus-cgroup statistic mixes accounting domains and can count shared pages
more than once; it is not unique physical memory. One-second post-drain parent
status and tracked hierarchical scope/process counts are observations, not a leak
freedom proof. A vanished scope is not retroactive proof for a failed cleanup.

Each invocation keeps raw output/logs and appends an accounting record before a
failure stops the runner. Partial samples, setup failures, provider results,
nonzero harness exits, missing observations and remaining planned samples stay in
the report. Exit 20 means cleanup failure. Do not retry that active run or invoke
an additional manager cleanup. A separate pass is not a continuation of a stopped
pass. Resource profiling and diagnostic timing never replace qualifying A/B data.

Additional checks:

```sh
python3 -m unittest discover -s tests -p test_preview_experiment_tools.py
ctest --test-dir PACKAGE_ROOT/A/harness --output-on-failure
ctest --test-dir PACKAGE_ROOT/B/harness --output-on-failure
```
