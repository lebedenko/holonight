# HoloNight umbrella

Read CONTRIBUTING.md. Preserve repository boundaries, installed-package tests, and the
installer staging, ownership, collision and conservative uninstall protections.
Build deployed binaries against host dependencies; container binaries are acceptance only.
Use Conventional Commits. Do not publish repositories or images without authorization.

Before executing a supplied plan, evaluate each step for relevance, cost, and redundant
checks. Apply the proportional-verification guidance in CONTRIBUTING.md. Explain material
departures from the plan before expensive work; proceed within the authorized scope
without routine approval requests.

## Package-manager deployment

Use the build tree, a staging directory, or a disposable root for development.
For an explicitly requested live package-manager deployment, run
`./scripts/install.sh holonight-pkg-manager` from the umbrella checkout. If a required
check fails or the installer refuses deployment, report the blocker. Never copy the
helper directly into the live system, run a privileged component install, or edit the
installer's ownership records to bypass deployment checks.
