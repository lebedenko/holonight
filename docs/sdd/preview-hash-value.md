# Practical value of buffered 64 KiB hashing

## Intent and boundary

Assess whether retained evidence justifies a private candidate experiment against
an explicitly recorded 5 ms per-preview planning threshold. This is an offline
assessment, with no production change, new measurements, source reconstruction,
build, recording, installation, download or benchmark rerun. Any later candidate
experiment requires a separate plan.

## Inputs and integrity

`scripts/assess-preview-hash-value.py` requires explicit `--mechanism-evidence`,
`--mechanism-verification`, `--verification-work-audit`, `--work-verification`
and `--output` arguments. The retained inputs are
`preview-hash-device-mechanism-20261116-01` and
`preview-verification-work-20261115-04`. Their seal hashes and unchanged passing
independent verification hashes are pinned. Existing provenance chains are
rechecked by validating seals, recursively consumed identities, frozen manifest
mapping and payload bytes, dependency identities, process mappings and tool
identities. Prior source reconstruction and workload verification are reused.

The output must be fresh and disjoint from input paths. Record the protocol and
threshold before inspecting evidence. Retain tool/checker/test snapshots, bindings,
machine-readable integer arithmetic, context, source citations, lifetimes, a report,
assessment and seal in an ignored build directory. Integrity failures retain sealed
partial evidence with blocked status and no recommendation. The separate checker
imports only the standard library and never imports the assessor or reporter.

## Arithmetic and interpretation

Compute a **new post hoc comparison**, directly from raw timing rows: device
buffered minus explicit stream 64K buffered. Use the primary read/update timer,
three sweeps per arm per block, all eight blocks and every manifest ordinal,
including empty files. Retain signed integer left/right sums and contributions
before division by three, both duration means and their ratio. Require exact
ordinal, sweep, schedule, digest, byte and process identities. Never add previously
reported effects to derive this comparison.

Report positive, negative and zero block counts separately from below/equal/above
5 ms counts. Positive savings favor streaming. If all eight differences are below
5 ms, recommend deferring a private A/B experiment on current evidence. Mixed
directions remain inconclusive. Neither classification establishes an upper bound
on future savings or proves that a future implementation cannot save 5 ms.

Historical validation/read-hash and pixel/metadata distributions remain separate
from standalone hashing measurements. Preserve measured, warm-up and setup
populations and profiled/unprofiled groups. Join endpoints only by explicit
execution/invocation/observation identities, reconciled against the work audit.
Setup endpoints remain unobserved. Retain count, minimum, median, nearest-rank p95
and maximum. Do not subtract standalone differences from endpoints, combine
quantiles, or infer exact critical-path savings.

## Source and lifecycle interpretation

Review and retain the work audit's frozen source citations. RuntimeOwner construction
calls refresh; refresh validates protected selection and the nested runtime.
verifyRuntime uses buffered QFile and hash.addData(&file) for read/hash validation.
The explicit service/session refresh entry points do not prove repeated calls.
The 52 accounted service constructions each have one validation. Distinct services,
matching payloads and object addresses do not establish repeated validation within
one unchanged owner/generation lifetime; generation identity remains unproven.

## Acceptance

Focused stdlib fixtures cover signed direct arithmetic, empty files, missing and
duplicate ordinals, warm-up exclusion, population separation, identity mismatches,
thresholds below/equal/above 5 ms, collisions/overlap, provenance drift, sealed
partial failures and arithmetic tampering after resealing. Run these fixtures, one
offline assessment and its independent checker, compare retained snapshots, and
check whitespace. No native verification is relevant to this offline change.

For reproduction, choose a fresh output name; retained directories are immutable:

```sh
python3 scripts/assess-preview-hash-value.py \
  --mechanism-evidence build/preview-hash-device-mechanism-20261116-01 \
  --mechanism-verification build/preview-hash-device-mechanism-20261116-01-independent.json \
  --verification-work-audit build/preview-verification-work-20261115-04 \
  --work-verification build/preview-verification-work-20261115-04-independent.json \
  --output build/preview-hash-value-REPRO
python3 scripts/verify-preview-hash-value.py \
  --assessment build/preview-hash-value-REPRO \
  --output build/preview-hash-value-REPRO-independent.json
python3 -m unittest discover -s tests -p 'test_preview_hash_value.py'
```
