# Native cache publication correctness, protocol v4

The [machine protocol](CORRECTNESS-v4.json) carries forward v3 fixture hashes,
explicit membership, prerequisite ordering, installed provider bindings and
conservative cleanup. Historical protocols, verifiers and sealed evidence remain
unchanged. Only `build/preview-cache-publication-correctness-20261118-03` is accepted.
Collisions, resumes, input overlaps and symlink escapes fail before authentication.

Launch from the foreground desktop terminal, from the umbrella repository:

```sh
python3 tooling/preview-cache-publication/qualify.py --built "$PWD/build/preview-cache-publication-native-20261117-01" --output "$PWD/build/preview-cache-publication-correctness-20261118-03" --authenticate
```

Destination and desktop runtime/bus identity are validated before foreground
`sudo -v`, which inherits terminal input and output. Passwords are never captured.
Cancelled or denied authentication creates no attempt. No policy change or
background credential keepalive is used. The existing `--built … --output …`
interface remains available for an already authenticated terminal.

The frozen schedule starts with `sudo -n -v` before fixture preparation and adds
that same bounded noninteractive check immediately before each privileged
operation. Privileged commands use `process_group=0`, retaining the authenticated
terminal session with a separate process group. Desktop workloads keep
`start_new_session=True`. Command records freeze these launch policies. Only
administrative authorization, protected fixture creation and owned staging/removal
may be elevated; model workloads and consumers remain desktop processes.

All commands have a 600-second bound; process-group termination, reaping and scope
proof share a five-second cleanup deadline. Stop at the first failure and preserve
raw output, XML, remaining commands and case accounting. Only verified owned
cleanup may follow; it requires its frozen noninteractive authorization check.
Failed cleanup authorization is never retried and unverifiable staging is retained.

Reuse retained Release providers. Generate shared fixtures inside the attempt and
compile only correctness executables and consumers with four jobs. No source
repairs, retries, replacement attempts, diagnostic execution or provider rebuilds
belong to this attempt. Acceptance requires all **130 required cases** across both
arms, all consumer and identity checks and successful cleanup.

After the single attempt, including a blocked attempt, run the independent
[v4 verifier](offline/verify_correctness_v4.py) into this fresh adjacent output:

```sh
python3 tooling/preview-cache-publication/offline/verify_correctness_v4.py "$PWD/build/preview-cache-publication-correctness-20261118-03" --output "$PWD/build/preview-cache-publication-correctness-20261118-03-independent.json"
```

The verifier imports no qualifier or build implementation. It pins protocol bytes,
reconstructs commands and launch policies independently and validates stopped
schedule accounting. Verification of a blocked record confirms its blocker;
acceptance also requires the native result to be qualified. Synthetic regressions
forbid real process execution and exercise production persistence.

Latest historical attempt: blocked after 47 passing cases, at staging authorization.
Overlap and candidate selection remain **Evidence insufficient**, streaming and
validation reuse **Deferred**, and historical qualification **78/80**. Portal and
GRUB remain outside scope.
