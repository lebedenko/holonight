# <Initiative Name>

Status: Draft

Allowed statuses: `Draft`, `Accepted`, `Integrated`, or `Abandoned`.

## Goal

Describe the user-facing outcome.

## Non-goals

- State adjacent work that is intentionally excluded.

## Participating repositories

| Repository | Ownership in this initiative | Local SDD |
|---|---|---|
| `<repository>` | `<owned deliverable>` | Pending |

## Cross-repository contracts

Describe shared interfaces, compatibility constraints, and decisions consumers must follow. Keep repository-specific
implementation details in local SDDs.

## Dependency order

1. `<provider repository and deliverable>`
2. `<consumer repository and adoption>`
3. Umbrella integration review

Provider revisions must be published and pinned before dependent consumer work starts.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to those published commits.
- [ ] Cross-repository contracts are compatible at the pinned revisions.
- [ ] Root integration builds and tests pass in dependency order.
- [ ] Required manual ecosystem checks pass.
