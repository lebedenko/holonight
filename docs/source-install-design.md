# Source installation state and explicit retry

The umbrella coordinates source installation. Components continue to own CMake
packages and installed-consumer tests. Native caches under `.source-install` are
separate from development and container acceptance builds. Container outputs
never become deployment inputs.

`scripts/install_catalog.py` is the component catalog: provider edges, build
options, Arch requirements, and refresh hooks. An explicit selection uses local
checkouts and expands through installed dependents only. CMake validates required
installed package versions before deployment. Full installation enforces umbrella
pins. The development ecosystem builder also reads this catalog.

Preparation holds an exclusive lock on the persistent workspace directory inode.
CMake and Ninja always run; their dependency tracking decides what recompiles.
Full builds reuse `.source-install/build` and the stable staging prefix. Explicit
selections use distinct caches, so installed-provider and coordinated package
paths do not share CMake cache entries. Each preparation gets an independent
payload directory, source-content identities, build options, host package
identity, and six-column payload inventories. Prefix reconciliation preserves
identical files and timestamps and removes obsolete inventoried entries.

Completed preparation publishes a pointer only after all components succeed.
`--resume` loads that exact preparation, validates every payload and host package
identity, and performs no configure or build. Source edits do not affect it.
Failed preparations and deployments remain available for diagnosis.

Deployment holds a target-wide lock on the persistent state directory inode at
`/var/lib/holonight/source-install`. That directory is never uninstalled. Approved
payloads are copied into private state and validated before deployment intent is
published. `transaction.json` retains previous ownership, intended ownership,
actions, and completed steps. Intent is fsynced before mutation; publication uses
atomic replacement and directory fsync. Retry accepts each action only in its
previous or intended state. A conflicting administrator change stops recovery.
Refresh failures leave the transaction pending after ownership publication.
Recovery is explicit forward completion, without automatic rollback or an
atomic replacement of the whole ecosystem.

`scripts/install_state.py` validates the shared six-column format, entry types,
modes, digests, paths, duplicate ownership, and non-directory ancestors. Install
merges selected records with untouched records. Uninstall and obsolete cleanup
retain original evidence for modified files, including repeated removal attempts.
Directories may be shared and are removed only when empty. Symlinked ancestors
are rejected for deployment and preserved during removal.

Protected Images generations remain lease-managed, verified protected copies
with a two-generation bound. Writers serialize on the stable parent directory
inode; new operations create no ownership-sensitive lock files. The umbrella
journal authorizes Images generation publication and control-file writes before
they occur. The Images journal records allowed previous/intended states; recovery
rejects unexpected changes. The resulting generation inventory is merged into
the same pending umbrella transaction before manifest publication.

Legacy conversion remains maintenance-only, with consumers stopped. Reserved
legacy locks require complete payload ownership validation and must be empty,
root-owned regular files with mode 0644 and protected ancestors. Explicit
maintenance records quarantine intent durably before moving them into retained
backups. Other unowned files are never inferred to be installer output.

Verification uses disposable roots, inert application fixtures for ordinary
ownership and recovery, and a host-built Images helper for protected runtime
acceptance. Container acceptance remains a separate integration gate.
