# Icons infrastructure integration — Coordination ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| III-001 | holonight-icons | Validated system staging and documentation | — | [SDD](../../../holonight-icons/docs/sdd/umbrella-packaging/README.md) | Done | 5eb892baa242e216121f28ff2b68b23ee03e833e | Clean task verify: 39 tests, rendering, previews, four REUSE checks; published origin/main confirmed with ls-remote |
| III-002 | umbrella | Installation lifecycle, tasks and CI adoption | III-001 | — | Done | 2457ab9 | 24 installer tests; root icons verification; staged rendering; shell syntax, YAML and REUSE passed |
| III-003 | umbrella | Verify integrated published revisions | III-001, III-002 | — | Done | Local closure commit | 2026-09-24: git ls-tree/status and canonical remote/API confirmation; contract review; provider task verify (39 tests), task test:installer (24 tests), staged renderer, YAML/shell/REUSE checks passed; details below |

Baseline review (2026-09-24): 33 icons tests, 16 installer tests, source/theme validation, source REUSE,
and offscreen rendering passed. Review found obsolete source-copy staging, missing dark-theme/cache/bundle
integration, missing upgrade cleanup, and stale Places documentation. Current Qt renderer baseline is
863af4183bdf09ce05199b37e8f5dfb46a311ba1. These baseline results are not final acceptance evidence.

Icons CI checked once: [Theme verification](https://github.com/lebedenko/holonight-icons/actions/runs/35982751550), revision `5eb892baa242e216121f28ff2b68b23ee03e833e`, status `completed`, conclusion `success`. No CI polling or umbrella push.

## Umbrella implementation acceptance — 2026-09-24

- `task test:installer`: 24 tests passed, including both-theme/bundle ownership, final cache hashes,
  repeat installation, obsolete unchanged files/links and empty-directory cleanup, preservation of
  modified/unowned files and legacy untracked caches, collision rejection, real GTK cache validation,
  cache failure before deployment, and symlink-safe pruning/uninstall.
- `task icons:verify` repository delegation: 39 Python tests, source/generated validation, 206 rendered
  masters, all eleven Places sizes at 1x/2x, generated previews, and four REUSE checks passed.
- `python3 tests/check_staged_icons.py`: staged source validation and the same real Qt renderer/lookup
  checks passed in a disposable root. The harness requires adjacent metadata/fixtures, supplied only
  in that test root; none are added to the installation payload.
- `bash -n scripts/install.sh scripts/install-dependencies.sh scripts/uninstall.sh`, YAML parsing of
  the Taskfile/workflow, `task --dry icons:verify icons:preview`, `reuse --no-multiprocessing lint` and
  `git diff --check` passed. ShellCheck is not installed; shell syntax and behavioral tests were used.
- The complete clean icons build and umbrella verification logs were inspected; no actionable compiler
  warnings occurred. Preview inspection is recorded in the provider SDD; artwork is unchanged.
- `scripts/install.sh --check` correctly reports missing `papirus-icon-theme` on this host. No packages
  or live system files were installed. A full unchanged ecosystem build/live deployment is outside this
  infrastructure acceptance; icon payload deployment and removal were exercised in disposable roots.
- Cache detail: generate before staging ownership, refresh owned caches after deployment, and record
  final hashes. Earlier untracked caches remain unowned and are reported for optional manual removal.
- Umbrella CI cannot run until these intentionally local commits are published. Its equivalent installer
  commands passed locally; the published icons CI result above is separate evidence.

## Final integration review — 2026-09-24

The icons checkout is clean and the umbrella gitlink equals published
`5eb892baa242e216121f28ff2b68b23ee03e833e`; publication was confirmed with
`git ls-remote origin refs/heads/main`. The unchanged Qt checkout is clean at its umbrella pin,
`863af4183bdf09ce05199b37e8f5dfb46a311ba1`, also confirmed available through the canonical
repository commit API. `git ls-tree HEAD holonight-icons holonight-qt` and repository status checks
confirmed these exact revisions. No extra compatibility manifest was introduced.

Reviewed the packaging CLI, installed locations, both theme names/inheritance, shared bundle,
relative aliases, renderer compatibility, cache ownership, and upgrade/removal contracts at these
revisions. Provider clean acceptance preceded umbrella acceptance; the commands/results above apply
to implementation checkpoint `2457ab9`. Final closure only updates coordination documentation,
so unchanged build/tests were reused. Markdown local-link checks, REUSE and diff whitespace checks
cover closure. Generated previews were inspected as recorded in the provider SDD; no live UI
interaction or full application rebuild was required for this infrastructure-only change.

The host's missing Papirus package and unrelated package-manager checkout do not form part of the
verified disposable installation state. They remain untouched. Umbrella checkpoints are local,
including the provider pin checkpoint `cdf318a`; no umbrella publication or live installation occurred.
