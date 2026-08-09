# Shared CI Build Infrastructure — Coordination Ledger

The initiative is in discovery. Consumer migrations remain `Planned` until the image contract, publication security,
validation commands, baselines, and rollback policy are settled and the initiative is `Accepted`.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| CII-001 | umbrella | Inventory current CI images, package definitions, repository commands, runner assumptions, and Ubuntu portability promises | — | This initiative | Ready | — | 2026-08-09: initial workflow inspection confirms direct Ubuntu provisioning in `holonight-qt`, repository-specific mutable `:latest` images in Shell, AI, Settings, and Package Manager, and intentional Ubuntu-only portability coverage in `holonight-config`; exact image definitions and command parity remain to be inventoried |
| CII-002 | umbrella | Settle Arch package source/update strategy, image names and layering, supported architectures, immutable versioning, provenance, retention, rebuild, update, and rollback contracts | CII-001 | This initiative | Planned | — | — |
| CII-003 | umbrella | Implement, smoke-test, publish, and document `ci-base`, `ci-qt6`, and `ci-qt-compat`; validate the published digests | CII-002 | Pending | Planned | — | — |
| CII-101 | `holonight-qt` | Pilot `ci-qt6` and `ci-qt-compat` with identical local/CI commands and full Qt 6 plus Qt 5/private-header verification; retain Ubuntu only as an explicit portability matrix if accepted | CII-003 | Pending | Planned | — | — |
| CII-102 | `holonight-shell` | Migrate build/test and static-analysis jobs to the validated shared image, preserving dependency integration, architecture, QML, and DBus checks | CII-101 | Pending | Planned | — | — |
| CII-103 | `holonight-ai` | Migrate build/test and static-analysis jobs to the validated shared image, preserving dependency integration and QML checks | CII-102 | Pending | Planned | — | — |
| CII-104 | `holonight-settings` | Migrate build/test and static-analysis jobs to the validated shared image, preserving exact dependency pins, DBus, QML, and install smoke coverage | CII-102 | Pending | Planned | — | — |
| CII-105 | `holonight-pkg-manager` | Migrate build/test and static-analysis jobs to the validated shared image, preserving dependency integration and QML checks | CII-102 | Pending | Planned | — | — |
| CII-106 | `holonight-config` | Confirm Ubuntu as the portable authoritative job and decide whether to add a non-authoritative Arch matrix | CII-003 | Pending | Planned | — | — |
| CII-201 | umbrella | Verify exact consumer revisions and image digests, local-container/CI command parity, provenance and rebuild records, controlled update/rollback procedure, and retained portability matrices | CII-101–CII-106 | — | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record exact image digests, local
container commands, CI runs, results, provenance checks, rollback evidence, and the verification date in CII-201
before setting the initiative status to `Integrated`.
