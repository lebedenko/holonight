# External window title presentation — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | holonight-system-services | Shared core | — | [SDD](../../../holonight-system-services/docs/sdd/external-window-title-presentation/README.md) | Done | `398804a7cce5a57f9f6870c4e7ec99e9b1f3ddaa` | Enabled 6/6 and disabled 2/2 suites; install consumers and focused lint passed; baseline AudioBackend format blocker |
| I-002 | holonight-shell | Shell adoption | I-001 | [SDD](../../../holonight-shell/docs/sdd/external-window-title-presentation/README.md) | Done | `a5f4469d04041127adcf42fd0a73a9e44891c09d` | Serial 1,128 tests, architecture and QML checks passed; baseline StatusPopupGeometry lint blocker |
| I-003 | holonight-qt | Qt bridge | I-002 | [SDD](../../../holonight-qt/docs/sdd/external-window-title-presentation/README.md) | Done | `c434d6821140d5269550cb2388820f9cbfb2e163` | All 96 checks covered, enabled/disabled helper and install consumers passed; baseline isolated_style_probe lint blocker |
| I-004 | holonight-viewer | Viewer adoption | I-003 | [SDD](../../../holonight-viewer/docs/sdd/external-window-title-presentation/README.md) | Done | `236a1a296a42dc51913055f995df2349188f794e` | 27/27 clean tests and full task check passed |
| I-005 | umbrella | Verify published integrated revisions | I-001–I-004 | — | Superseded | — | Publication and native verification pending; pins unchanged |

Local verification date: 2026-10-05. Done records implementation and local regression verification; the baseline formatting/lint blockers above remain unresolved acceptance limitations. Full logs were inspected. Local SDDs record commands and scope. No commits have been pushed, no gitlinks have been changed, and no CI success is claimed for these unpublished revisions.

I-005 remains Planned. Required publication, clean pinned revisions, dependency-order umbrella checks and native Hyprland/Sway/Qt CSD/fullscreen/surface recreation verification remain pending. Offscreen tests are not native acceptance evidence. The unrelated Viewer report and pre-existing icons working tree were preserved.

Unfinished work is superseded by [the replacement](../decoration-independent-viewer/TASKS.md). Historical records above remain unchanged otherwise.
