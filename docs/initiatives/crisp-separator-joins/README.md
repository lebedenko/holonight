# Crisp separator lines and connected boundaries

Status: Accepted

## Goal

Implement the approved HnSeparator redesign: integer physical thickness, logical occupancy,
complete snapped rectangles, explicit boundary ownership, and matching joins in Files.

## Non-goals

Commits combining repositories, a compatibility API,
custom scene-graph rendering, arbitrary rotation/shear/custom-transform guarantees.

## Participating repositories

| Repository | Ownership | Local SDD |
|---|---|---|
| holonight-qt | Geometry, public control, shared consumers, gallery, rendered tests | [SDD](../../../holonight-qt/docs/sdd/reusable-hn-separator/SPEC.md) |
| holonight-files | Connected window boundaries, runtime regression and launch evidence | [SDD](../../../holonight-files/docs/sdd/crisp-separator-joins/SPEC.md) |
| holonight-shell | Opacity and physical-thickness migration | [SDD](../../../holonight-shell/docs/sdd/crisp-separator-joins/SPEC.md) |
| holonight-ai | Audit/adopt header boundary alignment | [SDD](../../../holonight-ai/docs/sdd/crisp-separator-joins/SPEC.md) |
| holonight-pkg-manager | Header boundary alignment | [SDD](../../../holonight-pkg-manager/docs/sdd/crisp-separator-joins/SPEC.md) |
| holonight-viewer | Audit existing consumers, preserve animation work | [SDD](../../../holonight-viewer/docs/sdd/crisp-separator-joins/SPEC.md) |

## Cross-repository contracts

`thickness` is an integer physical-pixel count (default 1); nonpositive values suppress paint
and default minor occupancy. Default color is borderPassive. Inherited opacity composes with
color alpha and a three-stop fade (one-sided fades reach full strength at the center).
Leading/Center/Trailing select placement inside the minor slot; default Leading.
Bottom/right owners use Trailing; top/left owners use Leading. Touching endpoints reference
the same logical boundary. Consumers perform no DPR calculations and do not overlap alpha strokes.

## Dependency order

1. Qt provider contract and focused verification.
2. Files, Shell, AI, Package Manager and Viewer migration/verification against that local provider.
3. Publish the accepted commits and update the umbrella pins.
4. Complete the clean-checkout integration review separately.

The implementation was initially scoped to local work. After native acceptance, the user authorized
committing, publishing and pinning. All six repositories are now published; the umbrella gitlinks select
those revisions. Local validation reused the verified provider artifacts, and Files additionally passed
a clean publication-snapshot build and all 21 tests without the unrelated dependency-refresh edits.

## Integration acceptance criteria

- [x] All repository work packages pass local verification.
- [x] Native fractional-scale Files junction inspection observed (manual interaction only); user also confirmed warnings gone.
- [x] Final native recheck after header stacking correction: user confirmed clean joins and no warnings.
- [x] Published commits verified on canonical remotes and umbrella pins updated.
- [ ] All participating checkouts clean; unrelated Files and Viewer work remains preserved.
- [x] Umbrella installer regression suite: 16/16 passed during publication.
- [ ] Final clean-checkout integration review recorded; status remains Accepted until then.

See the [publication and CI record](PUBLICATION.md) for exact revisions and the single CI snapshot.
