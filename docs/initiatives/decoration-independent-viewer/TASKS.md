# Decoration-independent Viewer — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-001 | holonight-viewer | Fullscreen-only heading and accurate native titles | — | [SDD](../../../holonight-viewer/docs/sdd/decoration-independent-viewer/README.md) | Done | `408d45390549c2cd72de463982cb276c4ab61720` (includes implementation e2670ec and verified CI provider pins) | 2026-10-08: task check and all 27 tests passed; native checks passed by user confirmation. |
| I-002 | holonight-qt | Remove decoration helpers and dependencies | I-001 | [SDD](../../../holonight-qt/docs/sdd/decoration-independent-viewer/README.md) | Done | `6c7ac33004702e166b8c152dcde918296be54286` | 2026-10-08: clean ON/OFF builds; 95/86 checks covered with affected input retests passing; package/QML/format/REUSE and focused lint passed. |
| I-003 | holonight-system-services | Remove decoration contract; preserve compositor behavior | I-002 | [SDD](../../../holonight-system-services/docs/sdd/decoration-independent-viewer/README.md) | Done | `39472e6dcafc93acea218a234213c346be256586` | 2026-10-08: enabled 6/6 and disabled 2/2 suites, install consumers and focused lint/format passed; unrelated AudioBackend global format blocker retained. |
| I-004 | holonight-shell | Compositor adapter and plugin ABI 3 | I-003 | [SDD](../../../holonight-shell/docs/sdd/decoration-independent-viewer/README.md) | Done | `7d82bd5162d52df1fcbcfbb747b6c7654be4df45` (includes implementation 54ce600 and verified CI provider pins) | 2026-10-08: clean staged-provider build; 1156-check suite covered with private-bus execution and corrected uqc_launch retest (124.01 s); plugin rejection, architecture, QML/package, focused lint/format and REUSE passed. Unrelated edits preserved. |
| I-005 | umbrella | Verify published integrated revisions and native ecosystem | I-001–I-004 | — | Planned | — | 2026-10-08: published canonical main revisions confirmed with git ls-remote and pinned; local acceptance and native Viewer evidence retained. Final umbrella integration review not run; unrelated Shell edits preserved. |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands, results,
and verification date in the final umbrella row before setting the initiative status to `Integrated`.

Native Viewer checks passed by user confirmation on 2026-10-08. Publication and pinning authorized separately on 2026-10-08. Final umbrella integration remains Planned; no deployment or CI polling was requested.

## Publication CI snapshot — 2026-10-08

Each published revision was queried once; pending checks are not claimed as passed.

| Repository | Revision | Workflow | Status | Conclusion |
|---|---|---|---|---|
| holonight-qt | `6c7ac33004702e166b8c152dcde918296be54286` | [CI](https://github.com/lebedenko/holonight-qt/actions/runs/37790721261) | in_progress | pending |
| holonight-qt | `6c7ac33004702e166b8c152dcde918296be54286` | [Licensing](https://github.com/lebedenko/holonight-qt/actions/runs/37790720869) | completed | success |
| holonight-system-services | `39472e6dcafc93acea218a234213c346be256586` | [Licensing](https://github.com/lebedenko/holonight-system-services/actions/runs/37790717925) | completed | success |
| holonight-system-services | `39472e6dcafc93acea218a234213c346be256586` | [Build and component checks](https://github.com/lebedenko/holonight-system-services/actions/runs/37790717649) | in_progress | pending |
| holonight-viewer | `408d45390549c2cd72de463982cb276c4ab61720` | [Build and checks](https://github.com/lebedenko/holonight-viewer/actions/runs/37790757154) | in_progress | pending |
| holonight-viewer | `408d45390549c2cd72de463982cb276c4ab61720` | [Licensing](https://github.com/lebedenko/holonight-viewer/actions/runs/37790757181) | completed | success |
| holonight-shell | `7d82bd5162d52df1fcbcfbb747b6c7654be4df45` | [CI](https://github.com/lebedenko/holonight-shell/actions/runs/37795453444) | in_progress | pending |

## Publication and pinning — 2026-10-08

All four repository revisions are available on canonical origin/main and are pinned in this umbrella checkpoint. Consumer CI pins match locally verified Config, Qt, SystemServices, Images and Thumbnails providers. Shell acceptance additionally used a git archive of committed revision 7d82bd5, excluding the six unrelated working-tree edits: clean Debug build, format, architecture and QML checks passed. The 1155-check isolated suite passed except uqc_launch, whose sibling build directory was read-only under the archive-local isolation wrapper; rerunning that check with the enclosing Shell directory bound writable passed (124.10 seconds). The four outer native-systemd skips were covered by the passing dedicated private-bus test. Logs: /tmp/decoration-shell-publication-{configure,build,format,qml,architecture,tests,launch}.log. No implementation change was required for that local isolation correction.

Existing AudioBackend formatting and historical Shell lint limitations remain recorded in the local handoffs. No deployment occurred. Initiative status remains Accepted and I-005 remains Planned: pinning is a publication checkpoint, not final umbrella integration, and participating Shell remains dirty with unrelated user work.
