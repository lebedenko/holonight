# Unified HoloNight portal backend — Coordination Ledger

| ID | Repository | Deliverable | Depends on | Local SDD | State | Commit | Verification |
|---|---|---|---|---|---|---|---|
| UPB-001 | xdg-desktop-portal-holonight | Local SDD; shared service registration, Settings extraction, installed appearance watching, updated activation and payload tests, documentation and repository scope instructions | Agreed initiative contract; installed appearance provider | [Design](../../../xdg-desktop-portal-holonight/docs/sdd/unified-backend/DESIGN.md) | In Progress | `73e7cf647610ce84cc360bc08c099c69dc6002dc` | [2026-10-19](VERIFICATION.md) |
| UPB-002 | holonight-shell | Local SDD; remove Settings publication and descriptor installation; update routing, diagnostics and regression tests | Agreed initiative contract; compatible UPB-001 for coordinated deployment | [Design](../../../holonight-shell/docs/sdd/unified-portal-backend/DESIGN.md) | In Progress | `b06d5cbce95b36502dbbb1048dc984ddb312706d` | [2026-10-19](VERIFICATION.md) |
| UPB-003 | umbrella | Coordinated staging and descriptor ownership transfer; conservative legacy-file cleanup, real-broker checks, personal configuration migration documentation and integration acceptance | UPB-001 and UPB-002 at compatible revisions | [Contract](README.md) | In Progress | This umbrella commit | [2026-10-19](VERIFICATION.md) |

The backend and shell commits are published to their `origin/main` branches in that order.
This umbrella commit pins both revisions with the coordinated installer and broker checks.
[UPB-003 verification](VERIFICATION.md) retains the dated automated evidence and publication record.
Manual acceptance, pre-existing shell tidy failures and host deployment remain outstanding;
the initiative remains unintegrated and work packages stay In Progress until acceptance is complete.

States: Planned, Ready, In Progress, Done, Blocked, Superseded. Done requires a local commit and passing local
verification; it does not mean integrated. Add component SDD links when created. Record exact revisions, commands,
results and verification date in UPB-003 before changing the initiative status from Draft/Accepted to Integrated.
Retain outstanding acceptance in the historical initiatives linked from the contract.
