# Protocol v4 rerun after the staging import blocker

The sealed `preview-cache-publication-correctness-20261118-03` attempt remains
blocked after 47 of 130 required cases. Authorization succeeded; staging failed
while importing the installer's `install_state` dependency. Independent
verification confirmed that blocked outcome. No protected staging remained.

The staging loader now temporarily adds the installer's own scripts directory to
Python's import path, matching direct script execution, and restores the path
after loading. The regression reproduces the sudo script import context without
starting any process. Installer behavior and ownership protections are unchanged.

The user authorized a fresh rerun. The qualifier and staging validation now accept
only `build/preview-cache-publication-correctness-20261118-04`; all previous attempts
remain immutable. The [v4 protocol](CORRECTNESS-v4.json) and independent
[v4 verifier](offline/verify_correctness_v4.py) remain unchanged. This supersedes
the destination in the historical [v4 launch instructions](CORRECTNESS-v4.md).

From the umbrella repository, launch once in a foreground desktop terminal:

```sh
python3 tooling/preview-cache-publication/qualify.py --built "$PWD/build/preview-cache-publication-native-20261117-01" --output "$PWD/build/preview-cache-publication-correctness-20261118-04" --authenticate
```

After a sealed attempt, including a blocked result, verify independently:

```sh
python3 tooling/preview-cache-publication/offline/verify_correctness_v4.py "$PWD/build/preview-cache-publication-correctness-20261118-04" --output "$PWD/build/preview-cache-publication-correctness-20261118-04-independent.json"
```

The desktop terminal launcher runs those commands sequentially, skips verification
if authentication creates no sealed attempt, and never captures terminal input.
No source changes, retries or replacement runs belong to the frozen attempt.
Acceptance still requires all 130 cases, consumers, identities, cleanup and
independent verification. Diagnostic execution and provider rebuilds remain
outside scope. Overlap and candidate selection remain Evidence insufficient,
streaming and validation reuse Deferred, and historical qualification 78/80.
