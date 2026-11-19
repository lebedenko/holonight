# Clang-tidy compilation database compatibility

The umbrella and all 19 components keep identical, independently usable
`scripts/quality.py` and `scripts/test-quality.py` helpers. No product API,
dependency ordering or installed-package boundary changes are required.

Analysis replaces only the exact GCC `-mno-direct-extern-access` argument with
Clang's `-fno-direct-access-external-data`. Both JSON `arguments` arrays and
shell-quoted `command` strings are supported. Native compiler invocations and
original compilation databases remain unchanged; no manually edited database is
needed. Unrelated flags and clang-tidy failures remain visible.

Each discovered database, including nested installed-package consumers, stays
independent. Only databases requiring translation receive private temporary
copies. Their working directories and source identities are anchored to their
original locations, retaining relative include, response-file and output paths.
Copies live until all analysis workers finish and are removed on success or
failure. Source selection, diagnostic configuration, warnings-as-errors and
`JOBS` parallelism retain their existing interfaces.

Run `python3 scripts/test-quality.py` in any checkout for focused regressions.
The umbrella's `python3 scripts/check-quality-copies.py` checks all declared
submodules for helper drift. Both checks run from their acceptance entrypoints.
Run native `task tidy` for C/C++ components (`build/dev`, or `build/rendering`
for icons). Hyprlock is asset-only and has no tidy task. These tooling checks do
not require installer acceptance or rebuilding the ecosystem in containers.

Component development guidance is in each repository's `CONTRIBUTING.md` or
`AGENTS.md`; the shared workflow is described in the umbrella
[contribution guide](../../CONTRIBUTING.md). Keep synchronized helper changes in
their owning repositories; publication and umbrella pin updates are separate.

See [native source cleanup](tidy-cleanup.md) for the follow-up diagnostic fixes.
