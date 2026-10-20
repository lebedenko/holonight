# Breadcrumb geometry contract

[Provider design](../holonight-qt/docs/sdd/breadcrumb-geometry.md) owns sizing,
containment and centering. [Files design](../holonight-files/docs/sdd/breadcrumb-geometry.md)
owns header placement and selects Normal with 5 px top and bottom padding
inside the 42 px header, without painting a second frame.

Build and stage holonight-qt before building Files against that isolated prefix.
Verify shared default and Xs geometry, Files navigation and alignment, then
container acceptance with current sibling providers and isolated runtime checks.
Keep all changes local; publication and umbrella pin updates are separate.
