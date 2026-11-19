# Native cache publication execution

Consume only `build/preview-cache-publication-20261117-01`, seal
`7f8f076c9020bb7f7d399f0eaefe69ce032a9db4d255e57aff907d15a7e4ce6c`.
The [preparation protocol](../../docs/initiatives/preview-cache-publication.md)
and its live inventory remain unchanged.

Interfaces:

```sh
python3 -B tooling/preview-cache-publication/run.py build --output build/preview-cache-publication-native-20261117-01
python3 -B tooling/preview-cache-publication/qualify.py --built build/preview-cache-publication-native-20261117-01 --output build/preview-cache-publication-correctness-20261117-01
python3 -B tooling/preview-cache-publication/run.py execute --built build/preview-cache-publication-native-20261117-01 --output build/preview-cache-publication-execution-20261117-01
python3 -B tooling/preview-cache-publication/offline/verify.py build/preview-cache-publication-native-20261117-01 --output build/preview-cache-publication-native-20261117-01-independent.json
python3 -B tooling/preview-cache-publication/offline/verify_correctness.py build/preview-cache-publication-correctness-20261117-01 --output build/preview-cache-publication-correctness-20261117-01-independent.json
```

Build Release against native host dependencies, four jobs, Images then Thumbnails
then File Browser, each arm in its own fresh output and install prefix. Never
install into the host prefix. Freeze source identities; never repair a failing
source, retry an observation, or replace evidence. A build failure ends the
attempt. Raw stdout, stderr, exact command, relevant environment, exit status and
monotonic start/stop times are retained. Seal the complete artifact membership,
including failed build outputs. Independent offline verification imports neither
the builder nor a runner.

Execution requires passing native correctness gates for both arms: target change
during commit, cancellation, timeout, shutdown, store failure, progressive pixels
before final metadata, cache availability at final completion, session cleanup,
and stale result rejection. Focused runtime verification, generation, cleanup and
installed consumer checks must pass without skips. Missing or unimplemented gates
block execution. No startup smoke invocation is allowed.

The frozen schedule is control/early warm-ups, then five pairs in alternating
order starting control/early: twelve fresh processes, ten measured. Each uses
startup, count one, 256 by 256, offscreen Qt, unique nonempty invocation ID,
private source and cache directories. The workload deadline is 30 seconds; cleanup
shares one five-second budget. Protected staging and removal must use the existing
authorization and conservative identity checks. Modified or unverifiable staging
must be retained. Input/linkage identity never substitutes for actual loading
evidence; unavailable loading evidence is explicit.

Retain raw stderr and harness JSON. Decimal monotonic timestamps are integers.
Join only invocation, service, request, worker, preparation and transaction
identities. Reject missing, duplicate, conflicting or malformed events, wrong
source, non-original decode, tier or outcome. Control enqueue follows store;
early enqueue precedes store. Accepted pixels follow enqueue and precede adequate
notification; final completion follows storage. Only strict
`store_entry < adequate < store_return` supports overlap; equality does not.

Only a complete, valid schedule with passing native gates can yield **overlap
observed** (at least one supporting measured early observation) or **overlap not
observed in this population**. Every blocked/incomplete result is **Evidence
insufficient**. No performance gain, p95, visible Files rendering or qualification
claim follows. Streaming and validation reuse remain Deferred, candidate selection
Evidence insufficient, qualification 78/80 unchanged.

Current implementation is partial. Both provider arms and harnesses compiled.
The separate installed-provider correctness executable compiled for control, then
failed one of 21 checks (20 passed). It stopped before the early correctness arm
and all twelve diagnostic entries. The failing supersession check waits for
`active_job_` to become false; that can occur between the old job and the queued
replacement job. This gate failure does not establish a provider defect. The
captured correctness source and raw result are retained without a replacement run.

The Release builds were reused for the separate correctness step, avoiding a
second provider build. The initial build record is blocked pending correctness;
the correctness record binds its seal. No protected staging was attempted. The
test filter also omits the actual `RuntimeVerification`, `GenerationOwner` and
`ProtectedGeneration` suites, so those prerequisites remain unvalidated. Timeout
and shutdown subcases were not reached after the supersession assertion failed.

The observation controller and protected staging integration are not implemented;
the execute interface refuses to launch. The offline interfaces validate blocked
evidence only and cannot accept a completed diagnostic. A passing blocked
verification confirms the retained record, not execution readiness or fulfillment
of the full plan. A follow-up must address the correctness gate and remaining
tooling before a new attempt. This attempt must not be resumed or replaced.
