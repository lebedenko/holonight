# HoloNight Umbrella Coordination

This repository is the coordination and integration layer for the HoloNight ecosystem. Product code remains in the
independently buildable repositories checked out at the top level.

## Ownership

- `holonight-qt` owns reusable Qt/QML design-system primitives and shared window/frame APIs.
- `holonight-shell` owns desktop-shell composition and system surfaces.
- `holonight-ai` owns AI application layout and product behavior.
- `holonight-icons` owns shared icon assets.
- `holonight-pkg-manager`, `holonight-settings`, and `holonightd` own their respective product behavior.
- The umbrella repository owns cross-project initiatives, integration state, and submodule pins.

Put a change in the narrowest repository that owns the behavior. Do not put product implementation in the umbrella.

## Cross-Repository Initiatives

1. Create `docs/initiatives/<slug>/README.md` and `TASKS.md` from the templates in
   `docs/initiatives/_template/`.
2. Inspect every affected repository and resolve shared contracts before accepting the initiative.
3. Mark the initiative `Accepted` only when its scope, dependency order, and integration criteria are settled.
4. Assign only work packages in the `Ready` state.
5. Give each implementer one repository, an exact upstream baseline, and the relevant work-package ID.
6. Keep detailed requirements, design decisions, file changes, and implementation tasks in that repository's local
   SDD. Link the local SDD from the umbrella ledger.
7. After local verification, confirm the implementation commit is available from the canonical remote before
   updating its submodule pin.
8. Run umbrella integration checks only after all repository work packages are `Done`.

Allowed work-package states are `Planned`, `Ready`, `In Progress`, `Done`, `Blocked`, and `Superseded`. A repository
task marked `Done` has passed local verification; it does not make the initiative integrated. Only a successful final
umbrella integration task permits the initiative status to become `Integrated`.

## Session and Commit Boundaries

- Start cross-project sessions at this umbrella root and read both this file and the assigned repository's
  `AGENTS.md`.
- Repository implementers modify and commit only their assigned repository. They do not edit umbrella status or
  submodule pointers.
- The umbrella coordinator alone updates initiative status, coordination records, and gitlinks.
- Never combine implementation from multiple repositories in one repository commit.
- Never pin an unpublished commit or treat an uncommitted submodule working tree as an integration state.
- Make umbrella checkpoint commits after accepted repository handoffs so downstream sessions have an exact baseline.
- The pinned gitlinks are authoritative. Initiative documents record decisions and verification, not a second
  compatibility manifest.

## Integration Review

Before marking an initiative `Integrated`:

1. Confirm every participating submodule is clean and pinned to a commit available from its canonical remote.
2. Review cross-repository contracts and compatibility at those exact revisions.
3. Run repository builds and tests in dependency order, followed by required manual ecosystem checks.
4. Record commands, results, and the verification date in the final integration row in `TASKS.md`.
5. Mark the integration task `Done`, change the initiative status to `Integrated`, and commit the umbrella state.
