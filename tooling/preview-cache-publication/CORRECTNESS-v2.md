# Native cache publication correctness, protocol v2

The [machine protocol](CORRECTNESS-v2.json) enumerates every required case.
The qualifier retains its `--built … --output …` interface. It accepts only the
pinned successful native compilation package, whose historical blocked status is
unchanged. It creates only `build/preview-cache-publication-correctness-20261118-01`;
collisions, resumes, overlapping roots and symlink escapes are rejected.

Before any command, freeze the native source, complete commands, environment,
required cases and tools. Configure fresh Release test/consumer builds against
the retained installed providers, with four jobs. Never rebuild providers.
Run ordinary prerequisites, publication tests and installed consumers as the
desktop user. Run only ProtectedGeneration fixture tests with elevated identity.
Stage protected reusable generations through the conservative umbrella installer;
all Preview/session model workloads stay unprivileged. Exercise each publication
gate against mutable one-shot and protected reusable runtimes in both arms.

Each process has a 600-second bound. Group termination/reaping and scope proof
share one five-second cleanup deadline. Each test invocation uses an exact filter
and fail-fast execution. XML membership must match exactly, with no missing,
duplicate, disabled or skipped case. A failed command or validation ends the
schedule; only conservative cleanup remains permitted. Modified or unverifiable
staging is retained. Raw output, XML, attempted and unexecuted work are sealed.
Compiler/dependency/linkage identities describe current builds; they do not
reconstruct uncaptured historical loading evidence.

The independent [v2 verifier](offline/verify_correctness_v2.py) imports no qualifier
or build implementation. The [historical verifier](offline/verify_correctness.py)
continues to validate the earlier failed attempt unchanged.

Both arms must complete every prerequisite and publication gate with successful
cleanup to produce `qualified`. Otherwise the record is `blocked`. Both outcomes
retain **Evidence insufficient** for overlap; diagnostic execution remains disabled.
No warm-ups, measured observations, source repair or replacement run is allowed.
Streaming and validation reuse remain Deferred; candidate selection remains
Evidence insufficient; historical qualification remains 78/80. Portal and GRUB
are outside this milestone.
