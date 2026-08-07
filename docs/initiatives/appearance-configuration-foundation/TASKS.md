# Appearance Configuration Foundation — Coordination Ledger

The initiative is in discovery. Repository implementation packages remain `Planned` until the canonical schema
owner, document format/path, field classification, migration policy, dependency order, baselines, and local SDDs are
settled and the initiative is `Accepted`.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| ACF-001 | umbrella | Audit `theme.conf`, `appearance.json`, `config.toml`, all field owners/writers/consumers, and color/metric/shape token responsibilities | — | This initiative | Done | Umbrella commit containing this row | 2026-08-07: inspected redacted live-file structure and metadata; traced Qt ThemeConfig/AppearanceConfig, Settings ConfigFileService/ThemeConfigFile and public TOML package, Shell ConfigService/ThemeService/SettingsPortalBackend, watchers/path helpers, ColorTokens, ShapeTokens, HnControlMetrics, call sites, tests, and docs; no secret values recorded |
| ACF-002 | umbrella | Classify every field; select canonical document format/path, shared schema owner, single-writer/notification contract, clean-break migration policy, and metric taxonomy | ACF-001 | This initiative | Done | Umbrella commit containing this row | 2026-08-07: selected versioned TOML at `$XDG_CONFIG_HOME/holonight/appearance.toml`, new neutral `holonight-config` repository, Settings-only production writes, consumer-owned validated reload, no automatic legacy migration, removal of unused transparency/blur and persisted mode, explicit field ledger, and separate ColorTokens/MetricTokens/ShapeTokens with HnMetrics QML facade |
| ACF-003 | `holonight-config` | Implement and publish canonical neutral appearance schema, defaults, validation, path resolution, atomic TOML serialization, diagnostics, and test helpers | ACF-002 | Pending | Planned | — | Published initial baseline `a4db5d8` pinned; waiting for local SDD and initiative acceptance |
| ACF-004 | `holonight-qt` | Separate color, metric, and shape responsibilities; adopt canonical appearance input; remove superseded readers/writers/watchers/aliases | ACF-003 | Pending | Planned | — | — |
| ACF-005 | `holonight-settings` | Adopt canonical appearance writer and errors; remove duplicate theme/shape schemas and appearance fields from shell-product TOML transactions | ACF-003–ACF-004 | Pending | Planned | — | — |
| ACF-006 | `holonight-shell` | Adopt canonical appearance notification/projection; remove independent theme parsing/path logic; retain only shell-product configuration ownership | ACF-003–ACF-005 | Pending | Planned | — | — |
| ACF-007 | umbrella | Pin published revisions and verify the clean break, rollback, inert legacy files, configuration security boundary, exact contracts, and complete repository test order | ACF-003–ACF-006 | — | Planned | — | — |

Allowed states:

- `Planned`: defined, but dependencies are not ready.
- `Ready`: may be assigned to an implementer.
- `In Progress`: repository implementation has started.
- `Done`: a local commit exists and local verification passed.
- `Blocked`: cannot proceed; include the reason in the Verification cell.
- `Superseded`: intentionally replaced or removed.

`Done` on a repository task is a local checkpoint, not an integrated initiative. Record integration commands,
results, versions, and the verification date in ACF-007 before setting the initiative status to `Integrated`.
