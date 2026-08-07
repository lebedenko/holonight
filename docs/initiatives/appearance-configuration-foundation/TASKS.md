# Appearance Configuration Foundation — Coordination Ledger

The initiative was accepted on 2026-08-07. A repository package becomes `Ready` only when its accepted dependencies
have published verified implementation commits and the umbrella has pinned those exact revisions.

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| ACF-001 | umbrella | Audit `theme.conf`, `appearance.json`, `config.toml`, all field owners/writers/consumers, and color/metric/shape token responsibilities | — | This initiative | Done | Umbrella commit containing this row | 2026-08-07: inspected redacted live-file structure and metadata; traced Qt ThemeConfig/AppearanceConfig, Settings ConfigFileService/ThemeConfigFile and public TOML package, Shell ConfigService/ThemeService/SettingsPortalBackend, watchers/path helpers, ColorTokens, ShapeTokens, HnControlMetrics, call sites, tests, and docs; no secret values recorded |
| ACF-002 | umbrella | Classify every field; select canonical document format/path, shared schema owner, single-writer/notification contract, clean-break migration policy, and metric taxonomy | ACF-001 | This initiative | Done | Umbrella commit containing this row | 2026-08-07: selected versioned TOML at `$XDG_CONFIG_HOME/holonight/appearance.toml`, new neutral `holonight-config` repository, Settings-only production writes, consumer-owned validated reload, no automatic legacy migration, removal of unused transparency/blur and persisted mode, explicit field ledger, and separate ColorTokens/MetricTokens/ShapeTokens with HnMetrics QML facade |
| ACF-003 | `holonight-config` | Implement and publish canonical neutral appearance schema, defaults, validation, path resolution, atomic TOML serialization, diagnostics, and test helpers | ACF-002 | [Local SDD](../../../holonight-config/docs/sdd/appearance-configuration-foundation/SPEC.md) | Done | `81b01d3` | 2026-08-07: implementation `acb9a45` published; local build, 25 focused tests, 2/2 CTest entries including install-tree consumer, format check, and clang-tidy passed; GitHub `CI` passed; final handoff evidence published in `81b01d3` and pinned |
| ACF-004 | `holonight-qt` | Separate color, metric, and shape responsibilities; adopt canonical appearance input; remove superseded readers/writers/watchers/aliases | ACF-003 | [Local SDD](../../../holonight-qt/docs/sdd/appearance-configuration-foundation/SPEC.md) | Done | `6f591cb` | 2026-08-07: implementation `89887c1` and visual-fix handoff `6f591cb` published; 20/20 CTest targets, clang-tidy, package/install and QML policy checks passed; Hyprland/Wayland light-violet-chamfered and dark-cyan-rounded matrices accepted after ComboBox, menu, icon-hover, submenu, and tooltip corrections; pinned |
| ACF-006 | `holonight-shell` | Own and publish the Shell product-config package; adopt canonical appearance notification/projection; remove independent theme parsing and appearance from product TOML | ACF-003–ACF-004 | [Local SDD](../../../holonight-shell/docs/sdd/appearance-configuration-foundation/SPEC.md) | Done | `d9f388d` | 2026-08-08: standalone package and installed consumer passed; 1,126/1,126 CTest entries passed with one intentional environment-dependent skip; format, clang-tidy, architecture, QML lint/types, metadata, and packaging checks passed; Hyprland verification accepted live accent reload, canonical metrics, warning-free weather graphs, and unchanged Shell surfaces; published and pinned |
| ACF-005 | `holonight-settings` | Adopt canonical appearance writer and Shell-owned product-config package; remove duplicate schemas and mixed appearance/product save transactions | ACF-003–ACF-004, ACF-006 | [Local SDD](../../../holonight-settings/docs/sdd/appearance-configuration-foundation/SPEC.md) | Ready | — | Published design baseline `73f3d15` pinned; implement against exact providers `holonight-config@81b01d3`, `holonight-qt@6f591cb`, and `holonight-shell@d9f388d` |
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
