# Crisp separators — coordination ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| CS-001 | holonight-qt | Geometry/API/rendering | — | [SDD](../../../holonight-qt/docs/sdd/reusable-hn-separator/SPEC.md) | Done | [`863af41`](https://github.com/lebedenko/holonight-qt/commit/863af4183bdf09ce05199b37e8f5dfb46a311ba1) | Baseline `27970cfe3ed3dc8bf0585dfee7927eae697979ac`; Qt build/full default suite 96/96; final affected tests 16/16; both backends × six DPRs; lint/package pass |
| CS-002 | holonight-files | Connected Files boundaries | CS-001 | [SDD](../../../holonight-files/docs/sdd/crisp-separator-joins/SPEC.md) | Done | [`212e14b`](https://github.com/lebedenko/holonight-files/commit/212e14b84d887cf6837a19dc26b4683c1e170c94) | Baseline `46557c287f37c3d2d6cafad17d37d834bb68b1b5`; Files builds, working-tree 22/22 and clean publication snapshot 21/21 tests, lint/license/install pass; final native joins clean and console warning-free (user confirmed) |
| CS-003 | holonight-shell | API migration | CS-001 | [SDD](../../../holonight-shell/docs/sdd/crisp-separator-joins/SPEC.md) | Done | [`cdb5829`](https://github.com/lebedenko/holonight-shell/commit/cdb58290d9f39178d44c7e4e09dcf50f4329bdfa) | Baseline `d109fb3b4883c9d1ae40f7ec7706c9e4407e95a8`; Build; 1175 cases pass with isolated retries; final QML 5/5; lint/metadata pass |
| CS-004 | holonight-ai | Header audit/adoption | CS-001 | [SDD](../../../holonight-ai/docs/sdd/crisp-separator-joins/SPEC.md) | Done | [`c014946`](https://github.com/lebedenko/holonight-ai/commit/c014946899b560d1ce23c57970cd209d8ba0a80d) | Baseline `7e25e78cc7fb33aa63ed480bc3f328a65e04ca0c`; Build; 714 entries pass (one skipped); final QML 48/48; strict lint pass |
| CS-005 | holonight-pkg-manager | Header alignment | CS-001 | [SDD](../../../holonight-pkg-manager/docs/sdd/crisp-separator-joins/SPEC.md) | Done | [`fbe6e62`](https://github.com/lebedenko/holonight-pkg-manager/commit/fbe6e620748c620e945b7547da028a6b71062995) | Baseline `32f989f2949092886c26cea4459945c875746089`; Build; 98 tests pass; final UI 15/15; lint pass |
| CS-006 | holonight-viewer | Consumer audit | CS-001 | [SDD](../../../holonight-viewer/docs/sdd/crisp-separator-joins/SPEC.md) | Done | [`2240c4a`](https://github.com/lebedenko/holonight-viewer/commit/2240c4a4b9860ae74efae30cee253a2bbc26d7ab) | Baseline `2ba1e5217002bf369fbbc4223866e37e176d4879`; Audit requires no product edits; build, 20 tests pass; final UI 11/11; lint pass |
| CS-007 | umbrella | Publication and pin checkpoint | CS-001–006 | [Record](PUBLICATION.md) | Done | This checkpoint | Canonical heads verified; exact CI snapshot recorded; installer tests 16/16 |
| CS-008 | umbrella | Final clean-checkout integration | CS-007 | — | Planned | — | Preserve unrelated Files/Viewer work; clean participating checkouts and final integration review still required |

Local verification recorded 2026-09-21 against the explicitly rebuilt/staged, uncommitted provider.
The user subsequently authorized publication and pinning. Repository commits are published; the gitlinks
select them. Done repository packages mean local acceptance, not final ecosystem integration.
Files' [verification record](../../../holonight-files/docs/sdd/crisp-separator-joins/VERIFICATION.md) contains
runtime hashes, commands, native observations and remaining limitations. Earlier sandbox socket/D-Bus
failures passed with access or an isolated session bus; those retries are not hidden fallback acceptance.

Publication and the one-time CI status snapshot are recorded in [PUBLICATION.md](PUBLICATION.md).
