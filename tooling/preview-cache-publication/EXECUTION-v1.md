# Cache publication observation execution

The [execution protocol](EXECUTION-v1.json) preserves the frozen preparation
schedule: control/early warm-ups, then five alternating pairs, ten measured
observations in twelve fresh processes. The [controller](execute.py) and independent
[offline verifier](offline/verify_execution.py) require the qualified, independently
verified correctness `-04` seal and its exact retained native Release providers.
Historical inputs and tooling remain unchanged. The older `run.py execute` stub
remains historical; use the separate controller below.

Only `build/preview-cache-publication-execution-20261118-01` is accepted. Validate
canonical nonoverlapping inputs, destination availability and desktop identity
before foreground terminal authentication. Freeze commands, invocation IDs,
environment, protocol, tools, fixture and harness sources. Run noninteractive
`sudo -n -v` before protected staging or removal. Administrative commands preserve
the terminal session with a separate process group; model workloads run as the
desktop user in separate sessions. No credential capture or keepalive is used.

Reuse the qualified provider archives and installed packages; compile only two
small harness executables with four jobs. A literal, reversible overlay augments
the retained startup harness with diagnostics after final delivery: cache lookup
and pixel comparison, retained source/cache PNGs, source identity, selected
protected generation and live shared generation-lock descriptor. After workload
completion, record actual parent mappings and executable identity. Providers are
statically linked: record archive hashes and exact linker inputs rather than
claiming separate provider mappings. Helper loading identities remain explicitly
unavailable; protected payload identities and live generation leases are bound.

Each observation remains startup/count one/256 by 256/offscreen with private source
and cache directories and a unique invocation ID. Do not run startup smoke,
retries, replacement observations, cache flushing, affinity changes or artificial
load. Workloads have a 30-second deadline. Process-group termination, reaping and
helper-scope proof share five seconds. Stop on the first process, observation,
identity or cleanup failure; only authorized verified owned cleanup may follow.
Retain unverifiable staging and raw evidence on failure.

The independent verifier reconstructs the complete command schedule and launch
policies, reverses the permitted harness overlay, validates the prerequisite
proof chain, raw events, source/cache identities, live lease, linked/mapped image
identities, scope proofs, cleanup, complete artifact membership and stopped
schedule accounting. Missing or inconsistent data blocks a conclusion.

For the same eligible request and transaction, only strict
`store_entry < adequate < store_return` supports overlap. Equality does not.
A complete valid run with at least one supporting measured early observation
reports **overlap observed**; a complete valid run without one reports **overlap
not observed in this population**. Warm-ups cannot establish support. Incomplete
or invalid runs report **Evidence insufficient**.

```sh
python3 tooling/preview-cache-publication/execute.py --built "$PWD/build/preview-cache-publication-native-20261117-01" --correctness "$PWD/build/preview-cache-publication-correctness-20261118-04" --output "$PWD/build/preview-cache-publication-execution-20261118-01" --authenticate
python3 tooling/preview-cache-publication/offline/verify_execution.py "$PWD/build/preview-cache-publication-execution-20261118-01" --output "$PWD/build/preview-cache-publication-execution-20261118-01-independent.json"
```

No performance gain, p95, visible Files rendering or production candidate decision
follows from this diagnostic. Candidate selection remains Evidence insufficient,
streaming and validation reuse Deferred, historical qualification 78/80 unchanged.
