# Publication checkpoint

The user authorized commit, publication and pin updates after successful native acceptance.
Each repository was pushed once to `origin/main`; canonical heads were checked using `git ls-remote`.
Consumer CI/Task dependency references select the published Qt provider `863af4183bdf09ce05199b37e8f5dfb46a311ba1`.
Repository implementation and dependency-reference commits remain separate and were sent together.

## Verification

Previous provider and consumer acceptance remains applicable: publication changes add documentation
and exact provider references, without altering the accepted rendering implementation. The clean Files
publication snapshot passed its build without compiler warnings, QML lint/metadata and all 21 tests;
its excluded 22nd working-tree test belongs to the unrelated dependency-refresh work. Both renderers
pass the six-DPR matrix. Native joins and warning-free console were confirmed by the user.

Changed Taskfiles parse, workflow provider references match the accepted Qt revision, and staged diff
checks pass. `python3 -m unittest discover -s tests -p 'test_install*.py' -v` passes all 16 umbrella tests.
Published-revision CI results are recorded below; a running check is not a passing check. No CI polling
or waiting was performed. Full hosted workflow execution remains CI-owned.

## Single CI snapshot

Observed at 2026-09-21T20:20:37.494834+00:00. Every listed run matches the full commit in its row.

| Repository | Revision | Workflow | Status | Conclusion |
|---|---|---|---|---|
| holonight-qt | `863af4183bdf09ce05199b37e8f5dfb46a311ba1` | [Licensing](https://github.com/lebedenko/holonight-qt/actions/runs/35650375487) | completed | success |
| holonight-qt | `863af4183bdf09ce05199b37e8f5dfb46a311ba1` | [CI](https://github.com/lebedenko/holonight-qt/actions/runs/35650375388) | in_progress | — |
| holonight-files | `212e14b84d887cf6837a19dc26b4683c1e170c94` | [Licensing](https://github.com/lebedenko/holonight-files/actions/runs/35650380906) | completed | success |
| holonight-files | `212e14b84d887cf6837a19dc26b4683c1e170c94` | [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/35650380738) | in_progress | — |
| holonight-shell | `cdb58290d9f39178d44c7e4e09dcf50f4329bdfa` | [CI](https://github.com/lebedenko/holonight-shell/actions/runs/35650385990) | in_progress | — |
| holonight-ai | `c014946899b560d1ce23c57970cd209d8ba0a80d` | [CI](https://github.com/lebedenko/holonight-ai/actions/runs/35650392032) | in_progress | — |
| holonight-ai | `c014946899b560d1ce23c57970cd209d8ba0a80d` | [Licensing](https://github.com/lebedenko/holonight-ai/actions/runs/35650392030) | completed | success |
| holonight-pkg-manager | `fbe6e620748c620e945b7547da028a6b71062995` | [Licensing](https://github.com/lebedenko/holonight-pkg-manager/actions/runs/35650397755) | completed | success |
| holonight-pkg-manager | `fbe6e620748c620e945b7547da028a6b71062995` | [CI](https://github.com/lebedenko/holonight-pkg-manager/actions/runs/35650397727) | in_progress | — |
| holonight-viewer | `2240c4a4b9860ae74efae30cee253a2bbc26d7ab` | [Licensing](https://github.com/lebedenko/holonight-viewer/actions/runs/35650404765) | completed | success |
| holonight-viewer | `2240c4a4b9860ae74efae30cee253a2bbc26d7ab` | [Build and checks](https://github.com/lebedenko/holonight-viewer/actions/runs/35650404574) | in_progress | — |

## Preserved work and integration boundary

Files' README, Taskfile, dependency preparation script, provider-revision test and its CMake registration
remain outside the separator commit. Viewer retains unrelated TIFF draft/formatting work. Its already
published GIF playback commit `28b5bca5a9687850c1db28f0fe4fb658ffb4aa15` is an ancestor of the new Viewer pin.
No unrelated work was discarded or included in the separator commits.

The initiative remains Accepted, not Integrated: participating checkouts are not all clean and the final
clean-checkout integration review is still pending. This does not prevent the explicitly requested
publication and pin updates. Gitlinks are authoritative; this record is verification evidence.
