# Cross-Repository Initiatives

Each directory here represents one HoloNight-wide change. Copy `_template/` to a descriptive kebab-case slug, settle
the cross-repository contract, and commit the accepted planning state before implementation begins.

An initiative has two umbrella-owned files:

- `README.md` is the stable contract: status, goal, non-goals, repository ownership, shared interfaces, dependency
  order, acceptance criteria, and links to local SDDs.
- `TASKS.md` is the coordination ledger: one work package per repository plus a final umbrella integration task.

Do not duplicate local implementation checklists here. Component repositories own their specifications, designs,
tests, and commits.

## Deferred backlog

| Initiative | Status | Priority | Scheduling |
|---|---|---|---|
| [GTK Visual Fidelity](gtk-visual-fidelity/README.md) | Draft | Low | Deferred until explicitly prioritized |

- [Files refactoring and onboarding](files-holonight-alignment/README.md) — Accepted; Files published and pinned; final integration review pending.

- [Shared image architecture](shared-image-architecture/README.md) — Integrated; published pins verified and manual checks passed on 2026-09-22.
