# Shared UDisks2 storage — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-000 | umbrella | UDisks2 runtime dependency preflight | — | This initiative | Done | This checkpoint | 2026-09-24: 14 dependency fixtures and bash syntax check passed |
| I-001 | holonight-system-services | Storage component | — | [SDD](../../../holonight-system-services/docs/sdd/udisks2-storage/README.md) | Done | 5f2ecda7eea653995f4c860bfb7f3a3f53beb279 (published) | 2026-09-24: clean build, 4/4 CTest suites; affected Storage rerun; format/diff/REUSE checks passed |
| I-002 | holonight-shell | Storage widget and popup | I-001 published and pinned | docs/sdd/udisks2-storage/ | Ready | — | Baseline cdb58290d9f39178d44c7e4e09dcf50f4329bdfa |
| I-003 | holonight-files | Devices and navigation recovery | I-001 published and pinned | docs/sdd/udisks2-storage/ | Ready | — | Baseline 672b7193fd5523dd5d52dabe0c666044f81b9ab7 |
| I-004 | umbrella | Integrated revision acceptance | I-001–I-003 | — | Planned | — | Pending published revisions and manual scenarios |

Done requires a local implementation commit and passing local verification. Integration additionally requires
published pins, dependency-order verification and manual ecosystem checks. No integration result is claimed yet.

Provider publication and pinning authorized on 2026-09-24. Canonical origin/main confirmed at
5f2ecda7eea653995f4c860bfb7f3a3f53beb279 after push. CI checked once: revision
5f2ecda7eea653995f4c860bfb7f3a3f53beb279, status completed, conclusion success,
[run 36004310274](https://github.com/lebedenko/holonight-system-services/actions/runs/36004310274).
Shell and Files implementation may now start against this provider revision.

Focused umbrella verification: `python3 -m unittest discover -s tests -p test_install_dependencies.py` (14 passed),
`bash -n scripts/install-dependencies.sh`, and `git diff --check`, all on 2026-09-24. These are dependency fixture
checks, not final ecosystem integration. The pre-existing untracked root `build/` was left untouched.
