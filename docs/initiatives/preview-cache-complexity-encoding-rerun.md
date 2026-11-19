# Directional-variation encoding rerun findings

Independent verification confirms **Recommend** for the frozen candidate on the retained startup scenario. Fresh qualification passed all 130 behavioral checks, provider CTest, installed consumers and focused store checks. Execution completed all 202 startup processes with 200 measured observations and verified owned cleanup. Production rollout remains outside scope.

## Fixes and retained evidence

The user authorized fixing and rerunning the blocked trial and selected `sudo -A`. Authentication now uses askpass under the same Python parent as the subsequent noninteractive privileged commands. Prerequisite verification precedes authentication and evidence creation; passwords are neither captured nor persisted.

The root-side build verifier reconstructs the retained desktop environment from the build owner, rather than the privileged staging caller. This preserves the independently verified build proof when staging executes as root. File Browser provider tests that copy a runtime now receive the flat built runtime payload; protected-session tests continue to use the owned staging generation. The retained linkage, mapped-artifact and phase-snapshot verification functions are wired into the final verifier. Unexpected post-processing AttributeError is now recorded as a stopped failure.

Each failed attempt stopped at its first failure and remains sealed. Reruns used fresh paths; no observations were replaced or pooled across attempts. The detector, compression setting, 28-image investigation corpus, metadata, thresholds, uninstrumented frozen-C sources and built candidate/control artifacts were unchanged. The independently eligible investigation and verified preparation/build were reused rather than repeated.

| Evidence | Outcome |
|---|---|
| Investigation 01 | Preserved preliminary evidence; missing independent classification verification |
| Investigation 02 | Independent eligibility passed; 1,736 stores, 1,680 measured |
| Correctness 02 | Stopped at missing noninteractive authorization |
| Correctness 03 | Stopped at root/desktop build-verifier environment mismatch; 47 required cases passed |
| Correctness 04 | Stopped at File Browser provider fixture configuration; 47 required cases and all five control Thumbnails CTest checks passed; staging removed |
| Correctness 05 | Independently qualified: 72 commands, all 130 required cases, both arms’ provider/installed/store checks; staging removed |
| Execution 05 | Invalid post-processing record after the first excluded warm-up; zero measured observations; staging removed; independent rejection retained |
| Execution 06 | Independently complete, 202 processes, 200 measured observations; Recommend; staging removed |

## Fresh qualification

Both arms passed five Thumbnails CTest checks (including installed and isolated installed packages) and four File Browser CTest checks (including installed Core and Preview consumers). The 130 required behavioral checks retain exact source/XML membership and are counted separately from provider CTest and focused store checks. Installed consumers resolve each arm’s installed providers. Host Release builds, linked dependencies, artifact identities and private runtime payloads remain bound to the retained build proof.

Focused installed-store checks passed SVG default-byte equality, write failure, cancellation, concurrent atomic stores and cross-arm PNG readability in both directions. The investigation’s previously verified native detector checks remain valid. Writable provider test trees live under correctness evidence, so CTest does not mutate sealed build inputs. No historical early-publication change was applied; both arms preserve synchronous publication.

## Whole-population startup selection

The schedule has one excluded warm-up per arm followed by ten alternating blocks of ten observations per arm. All 202 processes ran once in execution 06. Each arm contributes 100 measured endpoint values. P95 is nearest rank 95/100; exact unrounded values determine the gate.

| Endpoint | Control median ms | Candidate median ms | Control p95 ms | Candidate p95 ms | p95 gain ms |
|---|---:|---:|---:|---:|---:|
| first_ms | 132.3570145 | 118.9618885 | 148.366539 | 138.889651 | 9.476888 |
| final_ms | 132.3754475 | 118.9830930 | 148.380136 | 138.898029 | 9.482107 |

Both endpoint p95 gains exceed 5 ms, and neither candidate median regresses. This supports the registered recommendation for the retained textured/count-one/256x256/offscreen scenario. No universal image-size or startup-performance guarantee is claimed.

## Descriptive block differences

These values are candidate minus control; negative values favor the candidate. Each block has 10 observations per arm, so its nearest-rank p95 is its maximum. Block differences do not select a candidate; block 2 illustrates that an individual block can have a p95 regression while the whole-population gate passes.

| Block | First median difference ms | First p95 difference ms | Final median difference ms | Final p95 difference ms |
|---|---:|---:|---:|---:|
| 0 | -26.391002 | -14.380416 | -26.400293 | -14.381769 |
| 1 | -17.674723 | -9.550490 | -17.685771 | -9.525367 |
| 2 | -4.435357 | 0.806990 | -4.436889 | 0.803348 |
| 3 | -18.796080 | -3.549810 | -18.785991 | -3.548975 |
| 4 | -8.413793 | -3.207470 | -8.427705 | -3.208388 |
| 5 | -3.993794 | -11.128544 | -4.003851 | -11.249968 |
| 6 | -19.366411 | -6.537411 | -19.360062 | -6.538497 |
| 7 | -13.022910 | -33.781077 | -13.035007 | -33.767414 |
| 8 | -12.874641 | -10.119411 | -12.874947 | -10.124924 |
| 9 | -16.975796 | -1.498089 | -16.986911 | -1.495425 |

## Supervision, verification and entry points

All workload and command records verify, including exact schedule/environment, endpoint deliveries, loading identities, source/artifact bindings, scope isolation and owned cleanup. No retries within an attempt, replacement observations, cache flushing, affinity changes or artificial load occurred. Workloads retain a 30-second bound; termination, reaping, process-group absence and helper supervision share five seconds. The longest successful workload process was 0.414707 seconds and the longest shared execution cleanup was 0.128223 seconds. Both private staging generations were removed. The umbrella installer’s ownership, collision and conservative uninstall protections remain unchanged.

All **42 focused process-forbidden synthetic tests** pass. New regressions cover same-parent askpass ordering, root-side verification, flat provider fixtures versus protected-session paths, retained linkage/mapped inode and digest checks, and frozen phase snapshot validation. Existing coordinate, classification, native-input, eligibility, source-drift, schedule, warm-up, statistics and failure-path coverage remains passing.

Qualification 05 uses `tooling/preview-cache-complexity-encoding-trial/qualification-rerun-05/correctness_phase.py --askpass` and its `offline/verify_correctness_phase.py`. Execution 06 uses `qualification-rerun-06/execute_phase.py --askpass`, consuming the unchanged qualified attempt-05 proof. Final verification uses `qualification-rerun-06/offline/verify_execution_final.py`; it connects the original captured phase snapshot validator without altering observations or statistics. Captured phase versions remain present to preserve earlier tool identities. Each evidence directory is immutable; the interfaces reject path collisions.

| Phase | Evidence seal SHA-256 | Adjacent independent record SHA-256 |
|---|---|---|
| `preview-cache-complexity-encoding-trial-20261119-02-investigation` | `3b320920e297cbb184f7b4acde04c83f45e0f63f92ae8c82dfc87d76563f0373` | `7a13e7afdf091f47c392d4954c02149aee29ea4ef5325e6165e36f5b983a2ac1` |
| `preview-cache-complexity-encoding-trial-20261119-02-prepared` | `57a5c585b47d0399a96ecc9d4b0b2d0a0327a0ba23694f703e04036869ac39fb` | `b0e7164150f5aac13a4ba4b6e54b80acb6822e3d4aca1332680338fe032d2012` |
| `preview-cache-complexity-encoding-trial-20261119-02-built` | `1cace58cbe3fe4b4d76e5eb1dd5ad979f369b08422f0c778a47938bf62817c44` | `84840d45799938cec6ec1b683f56b89bae662d46a28dd7da9ded1e98a85b5536` |
| `preview-cache-complexity-encoding-trial-20261119-03-correctness` | `859c90b8995aaf61bc692564450c2940e336bd97abc7dbf1441a5069aac68407` | `3d6350f038d36a659d5e5d77fc7e9dd9594f32d99633344c37c06923ef789ff6` |
| `preview-cache-complexity-encoding-trial-20261119-04-correctness` | `86708047ce2f503c7b4adf4b72a1adb1769a705b35a03d635f34853495076769` | `f38b42b2e3b268854a87c48685d0475a5af24038927e3b41d34635fad04ca649` |
| `preview-cache-complexity-encoding-trial-20261119-05-correctness` | `e47b48495b790c928f3fca6151dcac2a60934581c21c24689452e7e136d08ceb` | `d3c22310c215144339f79a0d1d6ffee622fe19cface8a41e287a2aa1fda9a658` |
| `preview-cache-complexity-encoding-trial-20261119-05-execution` | `04e7a1693bc085ac3c9f4e1a47a35a3c06747918b9eca4e5bcdbf8f0e90579e4` | `108ea4301c5a7f036ed4dd6358ed232054cebf6bca8b7d6b70112c0665847498` |
| `preview-cache-complexity-encoding-trial-20261119-06-execution` | `7acb55385e18d03309b76917fefe1ca4c195d5c52b272e3f7ff1255375c646ab` | `6ecc08bba29347c61ccad964ae0a7c5d52756fb9dc8f3825cc3ccb4ddc13cee0` |

Generated evidence remains in ignored build directories. The [initial findings](../../tooling/preview-cache-complexity-encoding-trial/FINDINGS.md) and all earlier sealed attempts remain historical. Historical qualification stays **78/80**, and prior Deferred decisions remain unchanged. No production installation, provider publication, consumer rollout or deployment occurred.
