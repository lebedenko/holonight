# Shared image maintenance

Status: Accepted

## Goal

Consolidate architecture status, provide local opt-in provider fuzzing, and make
five-trial consumer measurements reproducibly comparable.

## Non-goals

Public APIs, application behavior, codecs, cache policies, hosted CI, timing gates,
new native qualification and multimonitor checks. Publication and pin updates
require separate authorization. Existing Integrated initiatives remain Integrated.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| holonight-images | Bounded local Clang/libFuzzer harnesses | [SDD](../../../holonight-images/docs/sdd/shared-image-maintenance/SPEC.md) |
| holonight-files | Preview report contract and paired measurements | [SDD](../../../holonight-files/docs/sdd/shared-image-maintenance/SPEC.md) |
| holonight-viewer | Release report contract and paired measurements | [SDD](../../../holonight-viewer/docs/sdd/shared-image-maintenance/SPEC.md) |

## Cross-repository contracts

Provider APIs and production sources remain unchanged. Each consumer owns its
versioned measurement contract and comparison command. Require identical workloads,
fixtures and instrumentation, five successful raw trials, and explicit named-field
reasons for intentional provenance differences. Normalize checkout/build paths;
retain original provenance. Do not equate whole CMake cache hashes with build settings.

## Dependency order

1. Verify current published provider and consumer baselines; define local contracts.
2. Independent local provider fuzzing and consumer tooling against existing installed
   provider artifacts. No new provider interface or artifact is required by consumers.
3. Complete local acceptance, then await publication and pin authorization.
4. Final umbrella integration after published repository handoffs and authorized pins.

## Integration acceptance criteria

- [ ] Every repository work package has a published commit and passed local verification.
- [ ] Participating submodules are clean and pinned to published commits.
- [ ] Contracts reviewed at those revisions and root checks pass in dependency order.
- [ ] Local evidence includes bounded fuzz campaigns and 50 fresh measurement processes.

No new manual ecosystem gate is introduced by these tooling-only changes.
