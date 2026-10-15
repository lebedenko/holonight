# EDM-022 evidence staging

Status: preparation only; final integration has not run.

Baseline: `dfa140f5452a02b59e663e5770c4661cf0f24d89`.
Date: 2026-10-15. Bundle: 2.0.0. Qualified platform: Arch.

`canonical-tooling.log` records the 35 canonical tooling regressions. These are
focused tooling checks, not repository or final ecosystem acceptance.
Installer fixture command `python3 -m unittest discover -s tests -p 'test_install*.py'`
passed 68/68 in 202.104 seconds; this is a console result summary, not complete
real-installer acceptance evidence. A real clang-tidy probe reported the expected
modernize-use-nullptr diagnostic in an include header reached through src/../include
under a path containing spaces and regex metacharacters.

Generated production profiles also pass `python3 tooling/generate-install-profile.py --check`.
The initial drift audit found 17 repositories; canonical corrections require
all 18 to converge. See EDM-025–EDM-042 for exact starting revisions/dependencies.

## Required final automated record

After all repository packages are Done, retain a fresh checkout revision, each
clean gitlink and canonical availability result, bundle/declaration/profile
comparisons, immutable image digests/IDs and package inventories. Explicitly
prepare all inputs before clean offline repository acceptance in dependency order.
For reused providers record exact revision/content hashes, toolchain/Qt versions,
features/options and artifact hashes; preserve incompatible caches.

Retain complete commands/logs, source/artifact SHA-256 manifests, diagnostics,
skips and results per repository. Run the real umbrella installer in the qualified
isolated Arch environment against a disposable root from the fresh checkout.
Record installed discovery/runtime without development paths, ownership and
collision checks, modified-file preservation, install/reinstall/uninstall, and
unchanged package-owned QMarkdown hashes. Negative QMarkdown discovery must fail
before product configuration; test dependencies and QMarkdown payloads must be
absent from umbrella ownership. Fixtures alone do not establish real installation.

## Required user-performed VM record

Record the Arch VM image identity, package inventory, Sway/Hyprland versions and
snapshot ID before deployment. The user performs installation, session switching
and every pointer/focus interaction. Record commands, observations and relevant
logs for each item separately under both compositor sessions:

- Session startup and Shell/Settings operation.
- Greeter login, including the deferred Hyprland configuration parser check.
- Portal file selection and Files-to-Viewer opening.
- Files rendering Markdown through the installed system QMarkdown package.
- Hyprlock nested preview.

Each observation needs date, compositor/version, expected/actual behavior and
pass/fail. Do not mark EDM-022 Done or the initiative Integrated until every
required automated and manual check passes. Unrelated performance probes and
Debian qualification remain deferred.
