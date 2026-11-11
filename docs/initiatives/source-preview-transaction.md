# First preview transaction iteration

This iteration permits one short-lived sandbox spanning one source inspection,
up to four cached PNG attempts and at most one retained-source decode for one
selected raster preview. It does not permit runtime-validation caching, persistent
helpers, prestarting, grid changes, cache expansion or launcher tuning.

Local contracts: [Images](../../holonight-images/docs/sdd/source-preview-transaction/DESIGN.md),
[Thumbnails](../../holonight-thumbnails/docs/sdd/source-preview-transaction/DESIGN.md),
[File Browser](../../holonight-file-browser/docs/sdd/source-preview-transaction/DESIGN.md).

Build/install dependency order is Images, Thumbnails, File Browser, Files/chooser.
Use host-native installed providers in private prefixes. No publication,
deployment or umbrella pin update is part of this iteration.

Pre-edit sources, dirty state, archive hashes, compiler and dependency versions
are frozen in `build/preview-transaction-20261111-144758/freeze.json`. Historical
evidence remains untouched. Qualifying service latency measurements must use the
same frozen fixtures and harness, alternating A/B/C in blocks of ten, 100 samples
per fixture/scenario/variant with separate warm-ups. Pixel and metadata completion
are distinct observations. Stop on cleanup failure; do not retry or perform
additional manager cleanup. These timings do not measure screen presentation.

Acceptance requires correct pixels/metadata and zero correctness/cleanup failures,
at least 30% lower median cold/disk latency on every fixture, and p95 no worse
than B. The 40–50% estimate is a hypothesis. Warm-hit sub-millisecond differences
are reported as absolute differences. Interactive navigation remains manual.

Verification and measurements are recorded in ignored evidence directories.

## Results (2026-11-11)

The transaction implementation meets the cold/disk median target. First-preview
pixel-delivery medians improve **44.9–51.9%** versus current isolated B, and disk
hits improve **51.1–54.1%**. Metadata completion has essentially the same savings.
Every cold/disk and burst p95 improves. The strict overall gate **does not pass**:
several memory-hit p95 values increase by **0.001–0.138 ms**. Warm-hit median
absolute changes range from a 0.001 ms improvement to a 0.074 ms increase;
these sub-millisecond differences are not treated as meaningful gains. No further
optimization or resampling was attempted.

All 4,800 qualifying samples (100 per fixture/scenario/variant), 48 separate
warm-ups and 36 separate resize checks pass pixel, source metadata, resolution,
setup and cleanup checks. There are no missing qualifying observations or
excluded qualifying samples. Service delivery remains substantially slower than
pre-isolation A; this is not a screen-presentation measurement.

Pixel-delivery times below are median / p95 in milliseconds. The complete table
also contains metadata completion, memory hits, bursts, milliseconds saved,
percentages saved and remaining slowdown versus A.

| Fixture | Scenario | A | B | C | ms saved vs B | % saved vs B | slowdown vs A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 160x80.png | first | 2.168 / 3.756 | 192.026 / 228.550 | 92.374 / 115.245 | 99.651 | 51.9% | +4160.0% |
| 160x80.png | disk | 1.233 / 1.757 | 199.066 / 235.547 | 97.261 / 116.679 | 101.805 | 51.1% | +7787.5% |
| 1600x1200.png | first | 12.107 / 18.587 | 201.167 / 232.753 | 104.124 / 121.542 | 97.043 | 48.2% | +760.0% |
| 1600x1200.png | disk | 1.416 / 2.096 | 207.326 / 240.381 | 97.718 / 120.763 | 109.608 | 52.9% | +6799.5% |
| 3200x2400.png | first | 35.447 / 41.871 | 230.990 / 265.712 | 127.317 / 156.777 | 103.673 | 44.9% | +259.2% |
| 3200x2400.png | disk | 1.975 / 2.305 | 199.703 / 233.452 | 91.580 / 110.829 | 108.123 | 54.1% | +4536.9% |
| oriented.jpg | first | 1.235 / 2.315 | 192.628 / 220.783 | 95.835 / 115.787 | 96.794 | 50.2% | +7661.6% |
| oriented.jpg | disk | 0.934 / 1.446 | 202.214 / 236.454 | 97.738 / 125.295 | 104.476 | 51.7% | +10365.6% |

Evidence is retained in
[`build/preview-transaction-20261111-144758`](../../build/preview-transaction-20261111-144758).
The [complete comparison](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/comparison-final.md),
[raw accounting](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/summary.json)
and [measurement provenance](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/provenance.json)
record all fixture/binary hashes, denominators, raw observations and failures.
`A/B/C/harness-qualified-provenance.json` records matching harness sources and
compilation commands. A uses the historical pre-isolation Browser `caec685` and
Images `c1f6da5`; B uses frozen current Browser `9e7ff60` and Images `59384f1`;
both use Thumbnails `9462bac`. C sources, diffs and archive hashes are retained in
`C/qualifying-source-provenance.json`. All variants use GCC 16.2.1, Qt 6.12.0 and
host-native Release builds against installed packages. Fixture hashes match the
historical frozen comparison. The host page cache was not flushed.

The first comparison stopped during its first warm-up: A's harness rebuild had
failed because its older EXIF adapter lacks `format`, leaving an obsolete binary.
The runner rejected the missing correctness fields before any qualifying samples.
That evidence remains in `measurement-ljc6pj5i`. Fresh `harness-qualified` builds
use common raw metadata fields and checked build commands. The original and final
reporters/comparisons are both preserved; the final reporter only improves table
formatting and suppresses misleading warm-hit percentages, without changing
statistics or acceptance thresholds.

## Verification

- Images: all 11 configured CTest entries pass, including protocol/capture/cleanup,
  transaction command validation, installed/relocated provider consumers and native
  fault runtimes. The installed matrix compares legacy and transaction decoding
  against direct provider results across formats, orientation, precision, color
  profiles and limits. Focused failure tests also pass after the final poisoned
  transaction guard; they cover cancellation, standard/non-standard exceptions,
  caught invalid commands, malformed/truncated/trailing/misidentified responses,
  crashes, shared timeout and descendant cleanup. Existing cleanup-unit tests
  retain unsuccessful-final-cleanup and cancellation-precedence coverage.
- Thumbnails: all five CTest entries pass, including installed packages. The same
  cache-policy matrix runs through legacy isolated and transaction-backed lookup,
  retaining identity, adequacy, cancellation and tier fallback checks.
- Browser: seven focused preview and installed C++/QML consumer CTest entries pass;
  both Core-only checks pass. A new disk-hit regression verifies source EXIF and
  orientation, one cache decode, no source decode, and pixels-before-metadata order.
- Files: all 115 host tests pass, including Quick Look/resize, source mutation,
  native paths, stale selection and cache commit regressions. Unknown-dimension
  portable/host checks pass. Offscreen observer, rendered Files and chooser checks
  pass for staged and relocated private prefixes. The initial gate incorrectly
  received the production binary for its test-only observer; remaining checks use
  the lab executable and reuse completed valid results. This is recorded separately
  in `application-acceptance` and `rendered-acceptance`.
- Separate lifecycle link-wrapper diagnostics verify one validation/launch per C
  miss (versus two in B), zero additional launches on adequate memory hits, and
  unique scope names for every launch; see `lifecycle-report.json`. These runs do
  not contribute latency samples.
- Changed C++ formatting and whitespace checks pass. Focused host clang-tidy checks
  pass with an analysis-only compilation database removing GCC's unsupported
  `-mno-direct-extern-access` and disabling Clang 23's new trailing-comma check for
  existing initializer style. The 33 benchmark/accounting tests pass. No container
  binaries were used as deployed or measured binaries.

The initial sandboxed native test attempt could not access the user manager and
reported unverified cleanup; authorized host runs provide the accepted native
results. No qualifying latency run had a cleanup failure, and no additional
manager cleanup was performed. Interactive native navigation remains manual.
Nothing was published, deployed to the host prefix or pinned in the umbrella.

## Changed files

- Images: `include/holonight_images/isolated.h`; `src/isolated/client.cpp`,
  `helper.cpp`, `runtime.cpp`, `runtime.h`; `tests/CMakeLists.txt`,
  `isolated_transaction_test.cpp`, `isolated_fault_helper.cpp`,
  `isolated-consumer/main.cpp`; local transaction design.
- Thumbnails: `include/holonight_thumbnails/isolated.h`, `src/isolated.cpp`,
  `tests/CMakeLists.txt`, `tests/cache_test.cpp`; local transaction design.
- File Browser: `include/HolonightFileBrowser/preview/thumbnail_service.h`,
  `src/preview/thumbnail_service.cpp`, `src/preview/preview_service.cpp`,
  `tests/isolated_preview_test.cpp`; local transaction design.
- Umbrella: this note, `tooling/preview-benchmark/main.cpp`,
  `scripts/measure-preview-transactions.py`, `tests/test_preview_transaction_tools.py`.
  Files and chooser source files are unchanged; their private native builds and
  installed/rendered acceptance exercise the shared service implementation.
