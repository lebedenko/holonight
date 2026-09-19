# Files alignment — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| F-001 | holonight-files | Refactor and local acceptance | Existing Config/Qt pins | [SDD](../../../holonight-files/docs/sdd/holonight-alignment/README.md) | Done | 21d1589d28c70cb8a045019badb2a56167268744 (published) | 2026-09-19: clean Debug/Release, 9/9 CTest, QML/format/tidy/license, staged and isolated runtime passed; native checks passed per user |
| F-002 | umbrella | Register published Files and installer ownership | F-001 | — | Done | This onboarding checkpoint | Canonical origin/main verified at 21d1589 on 2026-09-19; existing checkout registered without replacement. Installer, inventory and ownership fixtures included; 16 tests passed |
| F-003 | umbrella | Verify integrated revisions and native behavior | F-001–F-002 | — | Planned | — | Exact-revision umbrella integration review remains pending. User native functional checks passed on 2026-09-19; Files CI snapshot recorded below |

Done is a local checkpoint, not integrated acceptance. Record final integration commands, results and date
in F-003 before marking this initiative Integrated.

Files was already published when authorization was received; `git ls-remote origin refs/heads/main`
confirmed 21d1589d28c70cb8a045019badb2a56167268744 on 2026-09-19. No redundant push was performed.
`git submodule add git@github.com:lebedenko/holonight-files.git holonight-files` registered the existing clean
checkout without replacing it. This umbrella checkpoint remains local. Initiative status stays Accepted
until the final integration review is complete.

CI inspected once on 2026-09-19 for exactly 21d1589d28c70cb8a045019badb2a56167268744:

- [Build and checks](https://github.com/lebedenko/holonight-files/actions/runs/35463475495):
  status `in_progress`, conclusion not yet available.
- [Licensing](https://github.com/lebedenko/holonight-files/actions/runs/35463475496):
  status `completed`, conclusion `success`.

No polling or waiting for CI completion was performed. Older failing runs are not evidence for this pin.
No application implementation changed during onboarding; prior local acceptance remains applicable.

Focused umbrella checks: `python3 -m unittest discover -s tests -p 'test_install_*.py'` (16 passed),
`bash -n scripts/install.sh scripts/install-dependencies.sh`, `reuse lint` (148/148 files) and
`git diff --check` (passed), 2026-09-19.
