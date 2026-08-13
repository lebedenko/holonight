# ComboBox Popup Geometry — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| CPG-001 | `holonight-qt` | Overlay-relative shared popup and package `0.1.1` | — | [`combobox-popup-geometry`](../../../holonight-qt/docs/sdd/combobox-popup-geometry/) | Done | `8b25b72` | Focused ComboBox coverage and all 25 CTest tests passed 2026-08-13; published to `origin/main` |
| CPG-002 | `holonight-greeter` | Remove footer workaround and require `HolonightQt 0.1.1` | CPG-001 | [`visual-refinement`](../../../holonight-greeter/docs/sdd/visual-refinement/) | Done | `e89abc9` | Isolated-prefix build, 34 non-socket tests, QML compile/lint, 8 demo smoke tests, and physical-display confirmation passed 2026-08-13; published to `origin/main`; two socket tests environment-blocked on repeat |
| CPG-003 | umbrella | Verify and pin published revisions | CPG-001–CPG-002 | — | Done | — | 2026-08-13: confirmed clean published revisions; ran provider `task test` (25/25), installed `HolonightQt 0.1.1`, built and installed the Release greeter, and pinned both gitlinks |

Allowed states are `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`. Repository work is not
`Done` until a local commit exists and verification passes; the initiative remains non-integrated until published
commits are pinned and the final umbrella review succeeds.
