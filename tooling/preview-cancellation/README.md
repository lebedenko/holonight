# Private cancellation diagnostic design

The umbrella owns preparation, native harness, execution and offline ledger validation.
Only verified copies of frozen v3 C/D sources are instrumented. Installed provider
packages and all build products remain inside the exclusive diagnostic package.
The tracing header is copied byte for byte; diagnostic JSONL is separate from TRACE.
Probes capture current context without filling missing worker/preparation identities.
Qt objects remain on their owning threads. Gates use condition variables and one
second deadlines, never a production lock. Main-thread waits process Qt events.
Failure releases all gates; the destructor supervisor only observes diagnostic
state and releases a gate, and never calls a QObject.

Execute C then D, preparation/active/cleanup/destruction, three repetitions each.
Each invocation creates one service and unique primary/replacement source copies
under a private cache directory; preserve those directories as runtime evidence.
There are no warmups, retries, repairs after execution starts, or replacement cases.

- Preparation: block after scope ownership and before cancellation check/gate write;
  establish primary pool pending; clear and refresh; observe preparation cancellation
  before release. Require cleanup without gate opening/readiness/selection, then recovery.
- Active: block after inspection at the existing before-full-decode seam; clear;
  observe cancellation then release. Require terminal cancellation and retirement
  before submitting recovery.
- Cleanup: cancel at active seam then block retirement before native cleanup;
  submit recovery and acknowledge pool pending before releasing retirement.
  Recovery cannot execute before verified retirement completes.
- Destruction: block active primary; supersede with a second pending pool request;
  destroy on main thread. Supervisor releases active only after destructor cancellation
  acknowledgement. Neither request may successfully deliver. Destruction must finish
  after worker cleanup, without callbacks applying to the destroyed object.

Accepted pixels and successful final metadata for cancelled requests fail validation.
Success means runtime success, successful raster outcome and no preview error;
image presence is recorded separately. A successful metadata-only final callback
must follow successful pixels for the same service/job/selection. Each accepted
callback must join a preceding publication and application attempt with matching
worker/preparation, payload flags and status. Rejected stale callbacks are retained
as attempts. Replacements require correct
pixels, oriented dimensions and EXIF against an independent in-process reference.
The separate ledger validator imports the unchanged v3 parser and identity checker;
it never invokes startup accounting. Standby and shutdown records are retained
separately and have no overlap target. Destructor end proves cleanup-path completion;
optional shutdown spans still require valid pairing, identity, role and ordering.

Root only stages protected generations and supervises ordinary-user harnesses with
existing user D-Bus/systemd session, offscreen Qt and a verified writable output path.
Preexisting helpers block execution; scope snapshots surround every invocation.
At first failure stop, preserve partial evidence, recheck inputs and payloads.
A timeout terminates the process group with TERM, five seconds grace, then KILL;
cleanup remains unverified. Never kill unidentified units.

A pass requires all 24 invocations, 24 service lifetimes, 30 cancelled/superseded
requests and 18 successful recoveries, all scenario/identity/lifecycle/cleanup/content
checks, and unchanged retained inputs and staged payloads. Otherwise report
**cancellation tracing validation blocked** with the first failing command.
Only these forced interleavings are covered: no A/B, arbitrary races, overhead,
performance, production correction, deployment, publication or qualification.

Preparation records live tooling and private header/template identities. The build
tool verifies them, runs the focused Python suite and five native checks without
helpers (result-status predicate, gate release, watchdog, destructor supervisor and
supervisor failure), then builds the private providers and harnesses. It records
commands, dependency resolution, environment, artifact hashes and a sealed control
manifest automatically. A started package cannot be rebuilt or resealed.
Historical failed packages remain unchanged; corrected tooling always uses a fresh
package and a newly preregistered complete matrix.
