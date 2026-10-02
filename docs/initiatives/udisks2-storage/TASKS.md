# Shared UDisks2 storage — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| I-000 | umbrella | UDisks2 runtime dependency preflight | — | This initiative | Done | This checkpoint | 2026-09-24: 14 dependency fixtures and bash syntax check passed |
| I-001 | holonight-system-services | Storage component | — | [SDD](../../../holonight-system-services/docs/sdd/udisks2-storage/README.md) | Done | 5f2ecda7eea653995f4c860bfb7f3a3f53beb279 (published) | 2026-09-24: clean build, 4/4 CTest suites; affected Storage rerun; format/diff/REUSE checks passed |
| I-002 | holonight-shell | Storage widget and popup | I-001 published and pinned | [SDD](../../../holonight-shell/docs/sdd/udisks2-storage/SPEC.md) | Done | f0fb0574beae8401970806c25e8242d964e70774 (published) | 2026-09-24: clean build, 1179 tests, scoped tidy/format, architecture, QML metadata and REUSE passed; QML lint retains existing Audio metadata warnings |
| I-003 | holonight-files | Devices and navigation recovery | I-001 published and pinned | [SDD](../../../holonight-files/docs/sdd/udisks2-storage/SPEC.md) | Done | 7b15eee1f2ab09118e95133e5246b612ee88d341 (published) | 2026-09-24: clean build, 27/27 CTest suites, format/lint/REUSE, install/QML checks and isolated Docker desktop launch passed |
| I-004 | umbrella | Integrated revision acceptance | I-001–I-003, I-005 | — | In Progress | This checkpoint | Published revisions confirmed; remaining manual scenarios unconfirmed |
| I-005 | umbrella | Discovery review: provider events and Shell/Files filtering; evidence and concrete correction packages | I-001–I-003 | This initiative | Ready | — | Review required before I-004; hardware observations and correction decisions pending |

Done requires a local implementation commit and passing local verification. Integration additionally requires
published pins, dependency-order verification and manual ecosystem checks. No integration result is claimed yet.

Provider publication and pinning authorized on 2026-09-24. Canonical origin/main confirmed at
5f2ecda7eea653995f4c860bfb7f3a3f53beb279 after push. CI checked once: revision
5f2ecda7eea653995f4c860bfb7f3a3f53beb279, status completed, conclusion success,
[run 36004310274](https://github.com/lebedenko/holonight-system-services/actions/runs/36004310274).
Shell and Files implementation may now start against this provider revision.

Focused umbrella verification: `python3 -m unittest discover -s tests -p test_install_dependencies.py` (14 passed),
`bash -n scripts/install-dependencies.sh`, and `git diff --check`, all on 2026-09-24. These are dependency fixture
checks, not final ecosystem integration. The pre-existing untracked root `build/` was left untouched.

Consumer handoff: implementation commits are verified against the pinned provider. Publication and pinning
were authorized by the user; both consumer commits are published and pinned in this checkpoint. Detailed command
evidence is in each local SDD. User-confirmed USB display works directly and through a hub. The initial hub
failure was a disconnected cable, resolved by reconnecting it; no code correction was required.

Manual follow-up on 2026-09-24: in response to the requested Shell-unmount scenario, the user confirmed
that Files returns Home. This confirms cross-application unmount recovery. The explanatory message and
both device-list updates were not explicitly confirmed. Optical-media and authorization-cancellation
checks remain unconfirmed. The initiative remains Accepted, pending final integration acceptance.

Publication on 2026-09-24: canonical `origin/main` was confirmed with `git ls-remote` at the exact
Shell and Files revisions above. Both participating consumer working trees and the provider are clean.
CI checked once after publication (no wait or polling):

- Shell `f0fb0574beae8401970806c25e8242d964e70774`: in_progress, no conclusion yet,
  [CI run 36011405230](https://github.com/lebedenko/holonight-shell/actions/runs/36011405230).
- Files `7b15eee1f2ab09118e95133e5246b612ee88d341`: in_progress, no conclusion yet,
  [Build and checks run 36012035861](https://github.com/lebedenko/holonight-files/actions/runs/36012035861).

Provider/consumer contracts were reviewed at these exact revisions. The dependency-order build and
local test evidence above remains applicable: there were no code changes after acceptance. Remaining
manual checks prevent marking the initiative Integrated; pending CI is reported separately.

Umbrella checks on 2026-09-24 after all repository work packages were Done:
`python3 -m unittest discover -s tests -p 'test_install*.py' -v`: 27/27 passed (40.060 seconds);
`bash -n scripts/install-dependencies.sh` and `git diff --check`: passed.

## Discovery review required — 2026-10-02

Review UDisks properties and provider ObjectManager add/remove/property events plus owner restart/reconnection.
Cover direct USB storage, hubs, external SSDs, SD readers, embedded eMMC, optical media and encrypted
backing/cleartext duplication. Do not introduce a manually maintained VID:PID database.

Source-review baselines are the current pins: provider `3e2928eb55bbc3de2b1e877e29aa57d47077c05d`,
Shell `1c8a3e191b6bcc93df385656174bff0e938e69d7`, Files `2b8da3fccc0829a2b9c33b79e56304e9861f7b97`.
These do not replace the historical delivery evidence above. Future correction packages need their own exact baselines.

Initial source inspection identifies Files `storage_policy.h::classify` as treating every nonempty
`ConnectionBus` as external. `devices_model.cpp` uses that classification together with `Removable` when
filtering unmounted volumes. Shell `StorageService.cpp` relies on removable/media-present and volume eligibility.
Provider `UDisks2Backend.cpp` subscribes to InterfacesAdded/Removed and owner changes, exports bus/removable
properties, and associates cleartext mappings with their backing drives. This is source evidence, not hardware acceptance.

The [UDisks Drive API](https://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Drive.html)
lists `sdio` as including eMMC and describes `Removable` as heuristic. Validate classification against real property
snapshots and lifecycle traces; bus presence alone is insufficient evidence of external storage. Record exact
revisions, scenarios, property/event traces and expected/observed consumer lists, then define correction packages
with owner, baseline and regression criteria before implementation decisions. Keep existing optical-media,
authorization-cancellation, recovery-message and both device-list-update checks open. Status remains Accepted.
