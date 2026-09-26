# KDE and GTK appearance synchronization

Status: Accepted

## Goal

Settings saves and session login propagate supported `appearance.toml` values into KDE and GTK. Status detects native output conflicts and canonical drift.

## Non-goals

- Installing a GTK widget theme, forcing libadwaita palettes, or managing unrelated KDE preferences.
- Files icon naming changes.
- Automatic reconciliation of external canonical edits during a running session.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `holonight-appearance-adapters` | Native writes, status, rollback, revert | [Adapter SDD](../../../holonight-appearance-adapters/docs/sdd/kde-gtk-appearance-sync/README.md) |
| `holonight-settings` | Pass canonical path on status refresh | [Settings SDD](../../../holonight-settings/docs/sdd/kde-gtk-appearance-sync/README.md) |
| `holonight-shell` | Bounded login reconciliation | [Session SDD](../../../holonight-shell/docs/sdd/kde-gtk-appearance-sync/README.md) |

## Cross-repository contracts

The adapter protocol remains version 1. `status` accepts optional `--appearance PATH`; bare `status --json` stays valid. `apply --appearance PATH --json` remains the sole native writer used by Settings and session startup. An unavailable KDE dependency yields a degraded output, while a failed write is an error. The canonical KDE `ColorScheme` is the installed `.colors` filename stem.

## Dependency order

1. Adapter at baseline `276c240a85d0865f6ce6cc91e3c634b5c8742c6c` supplies KDE outputs and canonical status.
2. Settings at baseline `d5cd9f1ffc08375baf3ece237fa81368f4851d20` consumes optional status path.
3. Shell at baseline `fbfe8f74ed4e94b0b7b73a814786d73be32acd28` invokes adapter apply at login.
4. Publish and pin the provider before accepting consumer handoffs; then perform umbrella integration review.

Local implementation and verification are complete for all three repositories. Their commits remain unpublished, so the umbrella gitlinks retain the previous revisions. Publication, pinning, and the native user check remain integration work.

## Integration acceptance criteria

- [ ] Each repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to published commits.
- [ ] Cross-repository contracts are compatible at those revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] The user checks Dolphin and representative GTK 3/4 applications in a native session.
