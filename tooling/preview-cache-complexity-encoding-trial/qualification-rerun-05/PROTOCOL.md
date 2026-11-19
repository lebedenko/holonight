# Conditional directional-variation qualification and startup

This phase is eligible only after the pinned attempt-02 investigation independently
selects the unchanged adaptive policy. Missing, altered, failed or unverified phase
prerequisites are rejected before commands, authentication or staging. Interfaces:

- `run.py prepare --output <fixed prepared path>`
- `offline/verify.py <prepared> --output <adjacent independent.json>`
- `run.py build --package <prepared> --output <fixed built path>`
- `offline/verify.py <built> --output <adjacent independent.json>`
- `qualify.py --built <built> --output <fixed correctness path>`
- `offline/verify_correctness.py <correctness> --output <adjacent independent.json>`
- `execute.py --built <built> --correctness <correctness> --output <fixed execution path>`
- `offline/verify_execution.py <execution> --output <adjacent independent.json>`

Paths are `build/preview-cache-complexity-encoding-trial-20261119-02-<phase>`.
The preparation, build, correctness and execution controllers and independent verifiers
are adapted from the retained publication trial. The publication change is removed:
both arms retain frozen-C synchronous publication. Only the candidate's private
Thumbnails raster encoder and directional detector may differ from frozen C.
The harness's retained loading snapshot runs after timing and shutdown.

Host Release builds use four jobs, shared unchanged Images/runtime, arm-specific
Thumbnails and File Browser providers, harnesses, provider tests and installed consumers.
Frozen sources include their fixture generators and tests. Exact package resolution,
linkage and loaded images are checked. Both arms must freshly pass provider CTest,
installed-package checks, all 130 behavioral checks with exact case membership, the
investigation's six-format detector checks, and additional SVG fallback, store failure,
cancellation, cross-arm PNG readability and concurrent atomic-store checks.

Each phase captures its complete consumed tool membership. Independent verification
checks frozen snapshots and captured identities rather than a growing directory's
membership. Command records persist launch, exit, failure and owned cleanup. Configure
and build commands allow 600 seconds; linkage allows 30 seconds; workloads allow 30
seconds. Termination, reaping, process-group absence and helper supervision share five
seconds. Stop on the first failure. No retries or replacement observations.

Protected staging uses the umbrella installer's ownership, collision and conservative
uninstall checks in private `/run/holonight-directional-*` generations. Production
installations remain unchanged. Foreground desktop authentication is preserved through
`--authenticate`; scheduled privileged actions use noninteractive authorization.

Freeze 202 startup processes: one excluded warm-up per arm, then ten alternating blocks
of ten observations per arm. Use the retained textured PNG, count one, 256x256, offscreen,
and private sources/caches. No flushing, affinity changes or artificial load. Recommend
only if whole-population control-minus-candidate p95 gains reach 5 ms for both first_ms
and final_ms, and neither candidate median regresses. Nearest-rank p95 is rank 95/100.
Block differences are descriptive candidate-minus-control and never select a candidate.
Complete valid results otherwise yield Deferred; invalid/interrupted results yield
Evidence insufficient. Historical qualification remains 78/80 and prior Deferred
outcomes remain unchanged. No universal size guarantee or production rollout is claimed.
