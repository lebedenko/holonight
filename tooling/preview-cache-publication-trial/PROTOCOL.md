# Early publication selection trial

Historical prerequisites reuse exact pinned independent records, verify their sealed inventories,
and compare the complete frozen C source/harness inventory to the accepted provenance. No
historical diagnostic durations are used for performance.

This separate private experiment consumes the accepted overlap execution and independently
qualified correctness `-04`, then prepares frozen uninstrumented C sources. It does not
modify production providers or historical evidence. Its only provider edit publishes a
validated cold eligible raster before synchronous store, suppressing the duplicate later
publication. Ineligible fallback, source and cancellation checks, metadata, memory cache,
atomic storage and shutdown remain in their original order. No background writer exists.

`run.py prepare --output build/preview-cache-publication-trial-20261118-01-prepared`
and `run.py build --package <prepared absolute path> --output <built absolute path>`
are separate interfaces. All interfaces require canonical absolute paths. The fixed
attempt names in contract.py reject collisions and reuse. Each ended phase is sealed.
Use `offline/verify.py <phase> --output <phase>-independent.json` after each phase.

Build host dependencies in Release mode with four jobs. Compile Images and Thumbnails
once, copying identical installed packages and runtime payloads to each arm. Compile
separate File Browser providers and benchmark harnesses. Then run:

```
python3 tooling/preview-cache-publication-trial/qualify.py --built "$PWD/build/preview-cache-publication-trial-20261118-01-built" --output "$PWD/build/preview-cache-publication-trial-20261118-01-correctness" --authenticate
python3 tooling/preview-cache-publication-trial/offline/verify_correctness.py "$PWD/build/preview-cache-publication-trial-20261118-01-correctness" --output "$PWD/build/preview-cache-publication-trial-20261118-01-correctness-independent.json"
python3 tooling/preview-cache-publication-trial/execute.py --built "$PWD/build/preview-cache-publication-trial-20261118-01-built" --correctness "$PWD/build/preview-cache-publication-trial-20261118-01-correctness" --output "$PWD/build/preview-cache-publication-trial-20261118-01-execution" --authenticate
python3 tooling/preview-cache-publication-trial/offline/verify_execution.py "$PWD/build/preview-cache-publication-trial-20261118-01-execution" --output "$PWD/build/preview-cache-publication-trial-20261118-01-execution-independent.json"
```

Authentication must run in a foreground desktop terminal, inheriting input and preserving
terminal-session sudo authorization. Every protected operation is preceded by `sudo -n -v`.
No credential capture or keepalive. Workloads run as the desktop user in separate sessions;
privileged staging uses separate process groups in the terminal session. Staging and
removal retain conservative installer ownership, collision and unchanged-tree checks.

CORRECTNESS.json preserves all 130 required cases and installed consumers across both arms.
The named context case now checks delivery and cache behavior: one progressive oriented
image, final-only EXIF, source dimensions, cache pixels equal delivered pixels, and arm-specific
publication relative to the synchronous commit barrier. No instrumentation-specific
context property is required. Test instrumentation exists only in correctness harnesses;
the exact timed provider archives remain uninstrumented and BUILD_TESTING=OFF.

Freeze all tooling, source diffs, fixture hashes, build artifacts, effective environments,
commands and the full schedule before the first timed process. Use the retained textured
3200×2400 PNG, startup/count one/256×256/offscreen, private source and cache per invocation.
One excluded warm-up per arm precedes ten blocks of ten observations per arm. Even blocks
run control then early; odd blocks reverse order. There are exactly 202 fresh processes,
100 measured observations per arm. No retries, replacements, count changes, cache flushes,
affinity changes or artificial load. Ordinary endpoint timing is the only measured-path
instrumentation. Parent maps and executable identity are captured after timing and shutdown;
helper mappings are explicitly unavailable. No cache, lease, tracing or publication probes.

Workloads have 30 seconds. Process-group termination/reaping and helper scope proof share
five seconds. Stop at the first failure; afterward only verified owned cleanup may run.
Retain staging if ownership, unchanged tree or authorization cannot be verified. Independent
verification reconstructs prerequisites, commands, artifacts, XML correctness, raw samples,
loading identities, cleanup and statistics without importing a controller.

Use separate medians and nearest-rank p95 (rank 95 of 100). Recommend only if both p95s
improve by at least 5 ms and neither median regresses, using unrounded populations.
A complete valid trial missing any condition is Deferred. Invalid or incomplete evidence
is Evidence insufficient. Block differences are descriptive. Historical qualification
78/80 remains unchanged; never subtract diagnostic durations from historical p95s.
Streaming, validation reuse and SHA dispatch remain Deferred. Production changes, full
qualification, rollout and deployment require a subsequent plan.
