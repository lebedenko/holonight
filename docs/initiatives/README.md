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

- [Shared image current status](shared-image-architecture/README.md#current-status--2026-09-23) — completed delivery, closure records and intentional deferrals.
- [Shared image maintenance](shared-image-maintenance/README.md) — Accepted; local fuzzing and paired comparison tooling.

- [Icons infrastructure integration](icons-infrastructure-integration/README.md) — Integrated; generated themes, system packaging, safe upgrades and umbrella verification.

- [Shared UDisks2 storage](udisks2-storage/README.md) — Accepted; provider and consumers published and pinned; USB discovery and Files unmount recovery confirmed. Discovery review, optical media, authorization cancellation, recovery message and device-list update checks remain open.

- [Shared search engine](shared-search-engine/README.md) — Accepted; reopened on 2026-10-02 for user-requested adjustments. Previous provider and Files delivery is published; Files exclusions are published, pinned and native-verified; baseline lint and corrected-revision reacceptance remain pending.

- [Configuration architecture](configuration-architecture/README.md) — Integrated; Appearance and Shell first, preserving edits and app-owned configuration.
- [Manual configuration editing and Settings interoperability](configuration-editing-interoperability/README.md) — Abandoned; replaced by configuration architecture; Files Settings page cancelled.
- [Developer tooling and standalone Serena](developer-tooling/README.md) — accepted follow-up to maintainability standardization.

- [Decoration-independent Viewer](decoration-independent-viewer/README.md) — Accepted; replaces the abandoned decoration-aware Viewer and external window title presentation initiatives. Local verification and native integration are recorded in its ledger.

- [FileChooser portal](filechooser-portal/README.md) — Accepted; Files provider locally committed and verified, publication/pin authorization pending; standalone backend and Shell routing follow its published and pinned handoff.
