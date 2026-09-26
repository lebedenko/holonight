# Size roles and icon resolution

Status: Accepted

## Goal

Give Files a 42 px shared header and fix platform-theme icon lookup so HoloNight artwork wins over inherited themes.

## Non-goals

- Change icon artwork or theme selection.
- Change the already committed Files badge corners.
- Close the manual desktop integration check in this publication handoff.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| `holonight-qt` | Xs metrics, role-aware header, platform icon resolution | [Qt SDD](../../../holonight-qt/docs/sdd/size-roles-icon-resolution/README.md) |
| `holonight-files` | Consume Xs in the application header | [Files SDD](../../../holonight-files/docs/sdd/size-roles-icon-resolution/README.md) |

## Cross-repository contracts

`HnControlSize.Xs = 4`; existing values 0–3 remain stable. Xs has 24 px control height, 16 px icon size, 6 px horizontal padding, and 4 px spacing. `HnHeaderBar.sizeRole` defaults to Normal, with heights Xs 42, Compact 48, Normal 56, Large 64, and Hero 72 px. Files consumes the shared APIs and does not force an icon theme.

## Dependency order

1. Verify and publish the Qt provider from baseline `0d5bdf094e6e759210531c4babdd2023e5d56485`.
2. Verify and publish Files from baseline `c85e0e0d9d75e2ddcd2130fb23c8ba3fedc0051c`, built against that provider.
3. Pin the published revisions, then complete umbrella integration checks at those exact revisions.

Published handoff on 2026-09-26: Qt `61d0c16` and Files `1a46a54` are pinned as separate repository commits. Files passed its complete local check against the installed Qt provider. The initiative remains unintegrated pending the final manual desktop check and umbrella integration review.

## Integration acceptance criteria

- [x] Both local work packages pass their repository checks.
- [x] Both implementation commits are published and the gitlinks pin those exact revisions.
- [ ] Provider and consumer builds and tests pass in dependency order at the pinned revisions.
- [ ] Manual Files appearance and navigation check passes in the desktop session.
