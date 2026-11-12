# Preview timings: before isolation → before latest improvements → current

Date: 2026-11-12. All times are **milliseconds, median / p95**. These measure service pixel delivery and final source metadata, not a painted QML frame.

## Summary

Isolation initially added substantial preview overhead. The transaction implementation immediately before the latest work still needed roughly **94–131 ms median** for a ready source preview and **95–99 ms** for disk hits. The current reusable-worker implementation reduces these to **1.2–6.7 ms** for lightweight ready previews and **1.7–3.9 ms** for disk hits. The textured large-image source decode remains about **36 ms**.

Warm ready previews are now in the same millisecond range as the historical in-process implementation. **Genuine startup remains roughly 94–137 ms median**, because validation and first-worker creation still have to occur.

## What the three stages mean

| Stage | Implementation | Evidence |
| --- | --- | --- |
| Before isolation | Historical in-process decoder, with no sandbox/helper | Historical transaction comparison, variant A |
| Before latest improvements | Isolated source transaction; repeated runtime validation and a fresh helper per transaction | Latest frozen comparison, variant A |
| Current | Protected generation validation reuse, reusable helpers and the two-slot preview scheduler | Latest frozen comparison, variant C |

Each displayed distribution has **100 successful observations**. Fixture hashes match across both runs. Recorded native Release build inputs also match: **GCC 16.2.1, Qt 6.12.0, libexif 0.6.26 and libwebp 1.6.0**. Both comparisons used separate warm-ups and alternating blocks of ten. Host page caches were not flushed.

The historical and latest harnesses differ: historical `first` is a first request with service construction outside timing; current `ready` explicitly warms a worker with another source. Therefore the historical first-request column is context, **not a controlled three-way ready-worker experiment**. Disk and memory cases represent the corresponding cache paths, but cross-run differences still should not be interpreted as precise causal savings. The before-latest/current pair uses the same latest harness.

## Pixels: source previews

Historical first-request timings versus latest ready-preview timings; construction is outside these measurements.

| Fixture | Before isolation: first | Before latest: ready | Current: ready | Median reduction vs before latest |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png | 2.168 / 3.756 | 96.596 / 115.667 | 1.833 / 3.147 | 94.763 ms (98.1%) |
| 1600x1200.png | 12.107 / 18.587 | 101.000 / 120.886 | 6.645 / 14.427 | 94.356 ms (93.4%) |
| 3200x2400.png | 35.447 / 41.871 | 130.759 / 153.022 | 36.144 / 41.853 | 94.615 ms (72.4%) |
| oriented.jpg | 1.235 / 2.315 | 93.584 / 115.246 | 1.240 / 2.456 | 92.344 ms (98.7%) |

The 3200×2400 texture is source-decode work, reported separately from the lightweight ready-preview target.

## Pixels: disk-cache hits

| Fixture | Before isolation | Before latest | Current | Median reduction vs before latest |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png | 1.233 / 1.757 | 99.283 / 120.895 | 1.734 / 2.755 | 97.550 ms (98.3%) |
| 1600x1200.png | 1.416 / 2.096 | 95.478 / 114.992 | 2.016 / 3.403 | 93.462 ms (97.9%) |
| 3200x2400.png | 1.975 / 2.305 | 96.522 / 119.590 | 3.839 / 4.610 | 92.684 ms (96.0%) |
| oriented.jpg | 0.934 / 1.446 | 98.116 / 122.191 | 1.836 / 2.981 | 96.280 ms (98.1%) |

## Pixels: decoded-memory hits

| Fixture | Before isolation | Before latest | Current | Current − before latest, median / p95 |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png | 0.162 / 0.341 | 0.320 / 0.478 | 0.309 / 0.451 | -0.010 / -0.028 ms |
| 1600x1200.png | 0.161 / 0.345 | 0.314 / 0.487 | 0.278 / 0.469 | -0.036 / -0.019 ms |
| 3200x2400.png | 0.311 / 0.470 | 0.167 / 0.329 | 0.308 / 0.332 | +0.141 / +0.003 ms |
| oriented.jpg | 0.159 / 0.217 | 0.170 / 0.330 | 0.172 / 0.331 | +0.002 / +0.001 ms |

Memory hits are sub-millisecond. Absolute differences are more useful here than percentages.

## Final source metadata

Final metadata follows pixels and includes source dimensions and EXIF. The source/ready comparability caveat above also applies here.

| Fixture | Case | Before isolation | Before latest | Current |
| --- | --- | ---: | ---: | ---: |
| 160x80.png | first / ready | 2.171 / 3.792 | 96.619 / 115.678 | 1.840 / 3.166 |
| 160x80.png | disk | 1.237 / 1.807 | 99.301 / 120.906 | 1.747 / 2.769 |
| 160x80.png | memory | 0.163 / 0.343 | 0.330 / 0.508 | 0.316 / 0.469 |
| 1600x1200.png | first / ready | 12.111 / 18.591 | 101.012 / 120.900 | 6.661 / 14.441 |
| 1600x1200.png | disk | 1.418 / 2.099 | 95.496 / 115.016 | 2.026 / 3.562 |
| 1600x1200.png | memory | 0.161 / 0.433 | 0.321 / 0.510 | 0.284 / 0.471 |
| 3200x2400.png | first / ready | 35.449 / 41.878 | 130.767 / 153.037 | 36.155 / 41.859 |
| 3200x2400.png | disk | 1.989 / 2.306 | 96.532 / 119.613 | 3.849 / 4.619 |
| 3200x2400.png | memory | 0.313 / 0.470 | 0.194 / 0.354 | 0.314 / 0.344 |
| oriented.jpg | first / ready | 1.325 / 2.472 | 93.689 / 115.271 | 1.248 / 2.467 |
| oriented.jpg | disk | 1.044 / 1.602 | 98.135 / 122.370 | 1.846 / 3.005 |
| oriented.jpg | memory | 0.161 / 0.337 | 0.181 / 0.348 | 0.180 / 0.340 |

## Genuine startup: not the ready-worker path

The latest startup scenario starts timing **before service construction**. The older pre-isolation run did not measure this equivalent scenario, so that value is unavailable rather than inferred.

| Fixture | Before isolation | Before latest: final metadata | Current: final metadata | p95 change |
| --- | ---: | ---: | ---: | ---: |
| 160x80.png | Not measured | 99.878 / 116.096 | 97.631 / 113.902 | -2.194 ms (-1.9%) |
| 1600x1200.png | Not measured | 100.039 / 122.442 | 101.242 / 122.909 | +0.466 ms (+0.4%) |
| 3200x2400.png | Not measured | 127.800 / 148.996 | 136.716 / 161.171 | +12.175 ms (+8.2%) |
| oriented.jpg | Not measured | 95.834 / 109.713 | 94.089 / 113.512 | +3.799 ms (+3.5%) |

## Qualification and limitations

- Current and protected one-shot variants each recorded **4,000 successful observations** across the full latest matrix. All calculated numerical gates pass. Lightweight ready and every disk-hit case meet median ≤30 ms / p95 ≤50 ms.
- Across pixels and metadata, maximum memory-hit median/p95 regressions are **0.141 / 0.003 ms**. The largest startup p95 regression is **8.171%**, within the 10% allowance for that fixture.
- **Strict overall qualification remains incomplete.** The frozen before-latest baseline recorded **eight cleanup-flagged observations and 17 missing placeholders** in PNG navigation at 100-ms intervals. These are outside the successful ready/disk/memory/startup rows above, but leave the full navigation reference unqualified. None were removed or replaced.
- The earlier historical transaction run had no missing/failed qualifying observations, but its own strict acceptance gate failed because of small memory-hit p95 regressions. It is historical evidence, not a retrospective pass.
- No equivalent pre-isolation samples exist for the latest startup, recycling, cancellation-depletion or interval-navigation scenarios. Historical burst timings are not substituted for them.
- These are host-native service measurements; native interactive presentation and low-end hardware performance are not qualified.

## Source evidence

- [Historical before-isolation and transaction comparison](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/comparison-final.md), [raw summary](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/summary.json), [provenance](../../build/preview-transaction-20261111-144758/measurement-r_z8c7dw/provenance.json).
- [Latest full comparison](../../build/preview-reuse-dgi4528s/reuse-measurement-ml9f0eu3/comparison.md), [raw summary](../../build/preview-reuse-dgi4528s/reuse-measurement-ml9f0eu3/summary.json), [provenance](../../build/preview-reuse-dgi4528s/reuse-measurement-ml9f0eu3/provenance.json).
- [Implementation, resource and verification assessment](../../build/preview-reuse-dgi4528s/ASSESSMENT.md).
- [Current cross-project contract and assessment](immutable-runtime-standby.md).
