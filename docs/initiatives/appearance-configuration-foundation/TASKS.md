# Appearance Configuration Foundation — Coordination Ledger

The initiative was accepted on 2026-08-07. A repository package becomes `Ready` only when its accepted dependencies
have published verified implementation commits and the umbrella has pinned those exact revisions.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| ACF-001 | umbrella | Audit `theme.conf`, `appearance.json`, `config.toml`, all field owners/writers/consumers, and color/metric/shape token responsibilities | — | This initiative | Done | Umbrella commit containing this row | 2026-08-07: inspected redacted live-file structure and metadata; traced Qt ThemeConfig/AppearanceConfig, Settings ConfigFileService/ThemeConfigFile and public TOML package, Shell ConfigService/ThemeService/SettingsPortalBackend, watchers/path helpers, ColorTokens, ShapeTokens, HnControlMetrics, call sites, tests, and docs; no secret values recorded |
| ACF-002 | umbrella | Classify every field; select canonical document format/path, shared schema owner, single-writer/notification contract, clean-break migration policy, and metric taxonomy | ACF-001 | This initiative | Done | Umbrella commit containing this row | 2026-08-07: selected versioned TOML at `$XDG_CONFIG_HOME/holonight/appearance.toml`, new neutral `holonight-config` repository, Settings-only production writes, consumer-owned validated reload, no automatic legacy migration, removal of unused transparency/blur and persisted mode, explicit field ledger, and separate ColorTokens/MetricTokens/ShapeTokens with HnMetrics QML facade |
| ACF-003 | `holonight-config` | Implement and publish canonical neutral appearance schema, defaults, validation, path resolution, atomic TOML serialization, diagnostics, and test helpers | ACF-002 | [Local SDD](../../../holonight-config/docs/sdd/appearance-configuration-foundation/SPEC.md) | Ready | — | 2026-08-07: accepted contract and published design baseline `c0e4aa2` pinned |
| ACF-004 | `holonight-qt` | Separate color, metric, and shape responsibilities; adopt canonical appearance input; remove superseded readers/writers/watchers/aliases | ACF-003 | [Local SDD](../../../holonight-qt/docs/sdd/appearance-configuration-foundation/SPEC.md) | Planned | — | Published design baseline `767cf3d` pinned; waiting for ACF-003 |
| ACF-006 | `holonight-shell` | Own and publish the Shell product-config package; adopt canonical appearance notification/projection; remove independent theme parsing and appearance from product TOML | ACF-003–ACF-004 | [Local SDD](../../../holonight-shell/docs/sdd/appearance-configuration-foundation/SPEC.md) | Planned | — | Published design baseline `4fe7516` pinned; provider for ACF-005 |
| ACF-005 | `holonight-settings` | Adopt canonical appearance writer and Shell-owned product-config package; remove duplicate schemas and mixed appearance/product save transactions | ACF-003–ACF-004, ACF-006 | [Local SDD](../../../holonight-settings/docs/sdd/appearance-configuration-foundation/SPEC.md) | Planned | — | Published design baseline `73f3d15` pinned; waiting for provider packages |
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
