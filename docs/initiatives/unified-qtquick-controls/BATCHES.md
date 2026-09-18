# Completion batches

Current repair checkpoint (2026-09-18): UQC-220 Settings acceptance is preserved.
[UQC-222](UQC-222.md) shared-window repair and [UQC-224](UQC-224.md) passive observer
repair are Done; [UQC-223](UQC-223.md) diagnosis remains Done. **P03 is closed** by
[verified human acceptance](FINDINGS.md#p03-human-acceptance-after-observer-repair--2026-09-18): correct Fusion and replacement
default pass light-time Settings construction and activation/hover palette stability.
The initial default attempt remains superseded evidence. No further P03 checks
are requested. UQC-201 remains In Progress; initiative Accepted; unrelated gates
and earlier accepted results remain unchanged.

Execution order from the user plan, updated with scope corrections on 2026-09-14. UQC-201 remains In Progress;
the initiative remains Accepted. Preserve existing accepted results unless affected
by a later change. Record observations once in FINDINGS.md and link local SDDs.

| Batch | Gates | Exit criteria |
|---|---|---|
| 1 | D02, F07; publication | Complete: Settings Weather diagnostics and both launcher styles accepted; published handoffs recorded. |
| 2 | A01, A02, A04 | Complete: shell Polkit identity rows, password/error visibility and fractional Askpass borders accepted; A03 cancellation preserved. |
| 3 | UQC-207 / compatibility dispositions | Closed by user-directed disposition: accepted rendering preserved; ScrollBar warnings, historical Haruna crash and Settings/Haruna Fusion hover deferred as non-blocking historical findings. Tokodon chevron deferral unchanged. [Closure](FINDINGS.md#batch-3-user-directed-closure--2026-09-16). |
| 4 | P01, P02 | Complete for scoped provider work: P02 accepted after nine runs; P01 external activation defect documented with owner-specific follow-ups. Raw evidence verified; navigation alternation is not claimed fixed. |
| 6 | S01, S02, F05 | S01/S02 accepted. F05 diagnosis complete: [external plain-Qt reproduction](FINDINGS.md#f05-plain-qt-external-reproduction--2026-09-15), report draft prepared but not submitted. Exact upstream mechanism/repair remain open; no HoloNight repair owner or further variant runs. |
| 7 | Remaining greeter-specific G01–G06 checks | Complete: G01–G06 accepted in all four Sway style/scale runs. [G01–G06 acceptance](FINDINGS.md#batch-7-manual-acceptance--2026-09-15). |
| 8 | Remaining UQC-201 | In Progress: [reconciled final checklist](FINAL-ACCEPTANCE.md), fresh automated verification and unresolved manual gates at clean published pins. |

G07 is closed as not an issue for intended fullscreen use; both scale-1 style
comparisons passed. See [fullscreen acceptance and closure](FINDINGS.md#g07-fullscreen-acceptance-and-closure--2026-09-16).
The specific windowed reproduction and UQC-216–218 investigations are retained
as historical evidence. Production is unchanged and no G07 follow-up is planned.

Batch numbers remain stable for historical references. **Batch 5 is removed.**
L01/L02 are incorrect application layouts, outside controls-unification scope.
Future Settings and AI sessions must address them in their own local SDDs; they
are not dependencies of this initiative. UQC-209/UQC-210 are Superseded. C03
Tokodon Fusion Switch overflow was already classified as external FormCard/Fusion
composition and does not become an application-layout repair here.

For remaining repair batches, reproduce and confirm ownership, prepare the repository-local SDD,
confirm the exact canonical baseline and set the package Ready before implementation.
Keep one repository per implementation handoff. Each batch ends with local
verification, published commits, an umbrella checkpoint and scoped manual checks.
An observation may be application-owned or an accepted limitation. A reproduced
failure needs a failing regression, bounded owner follow-up and fresh verified kit.
Missing evidence leaves its gate pending. Do not automate desktop pointer or focus.

## Batch 1 manual runs

Update 2026-09-13: Batch 1 is complete. D02 and F07 are accepted, all three
runtime paths were recovered, and the user confirms deliberate Fusion session
shutdown (numeric exit unavailable). Do not repeat the checks below. See [results](FINDINGS.md#settings-and-launcher-manual-results--2026-09-13).

Use the immutable `/tmp/holonight-uqc206-06_tsrg6` kit. READY, all 244 hashes and
recorded package versions were verified on 2026-09-13. Implementation is provider
`2965d8d`, shell `f55cb5f`; provider `68b7069` adds only tests/documentation.
The archived recovery command and checksum remain in TASKS.md. If packages change,
use the existing builder and its verification; never bypass refusal checks.

From a fresh real tux VT login outside a compositor:

```sh
python3 /tmp/holonight-uqc206-06_tsrg6/guided-session.py sway
```

The test session uses output scale 1; application helpers default to Qt scale 1.25.
Retain each printed evidence directory. Do not repeat the accepted F06 greeter/dropdown run.

1. Run Settings under HoloNight:

   ```sh
   python3 "$UQC_KIT/dropdown-test.py" settings
   ```

   Visit Weather and open provider, location source, temperature, wind, pressure
   and refresh selectors. Navigate away and return, then close Settings. Report
   whether all popups are usable and bounded. Acceptance also requires completed
   launch.log with required diagnostic logging enabled and no height binding loops
   or related QML failures, matching PID/environment and verified staged loading
   in isolation.json. Terminal silence is not diagnostic evidence. NeoChat/Tokodon
   warning checks remain in the final third-party matrix.

2. Run the HoloNight launcher:

   ```sh
   python3 "$UQC_KIT/launcher-test.py" run
   ```

   In a second test terminal (Super+Return), toggle it:

   ```sh
   python3 "$UQC_KIT/launcher-test.py" toggle
   ```

   Check stationary-pointer opening/reopening, browse/search, query/filter changes,
   Up/Down and the intended Enter target. Deliberate movement within a row must
   restore pointer selection; direct clicking must work. Activate harmless apps.
   Stop only the test shell with Ctrl+C and retain its recorded exit evidence.

3. Repeat the same launcher checks under Fusion after stopping the first shell:

   ```sh
   python3 "$UQC_KIT/launcher-test.py" run --style Fusion
   ```

Both styles need successful observations and staged shell/provider runtime evidence.
Distinguish deliberate shutdown from crashes or missing exit evidence. Return the
three evidence paths and observations. Batch 2 follows only after Batch 1 acceptance.

## Batch 2 manual checkpoint

Update 2026-09-14: shell repairs are published at `fffb171`, provider remains
`68b7069`, and shell CI passes. A01/A04 are manually accepted; A02 is closed by
synthetic lifecycle/rendered tests. See the
[canonical acceptance and saved outcomes](FINDINGS.md#batch-2-authentication-manual-acceptance--2026-09-14).
Saved process outcomes are classified and **Batch 2 is complete**. A03 and Batch 1
stay accepted. The immutable kit and previous kits remain preserved; the
[targeted instructions](AUTHENTICATION-BATCH2.md) are retained as run provenance.
Batch 3 follows with Haruna crash/diagnostic classification.

## Final acceptance coverage

Batch 8 must cover Haruna, NeoChat, Tokodon and compatible Qt hyprpolkitagent with
actual control-origin/fallback classifications; remaining Hyprland/Sway,
HoloNight/Fusion and scale 1/1.25 cases; palette transitions; terminal, desktop,
shipped D-Bus and systemd activation including wrappers and loaded modules;
authentication beyond cancellation and real pre-session greeter acceptance.

Run dependency-order builds/tests, import policy, installed consumers, negative
deployment fixtures and shared-contract review at clean canonical published pins.
Record final versions, evidence, limitations and date before marking UQC-201 Done
and the initiative Integrated. Account-dependent surfaces retain prerequisites;
the accepted logged-out scope does not add account sign-in.


## Historical Batch 3 disposition — 2026-09-14

Superseded by the [user-directed closure](FINDINGS.md#batch-3-user-directed-closure--2026-09-16).

Provider popup-background repair is published and pinned. Haruna icons, menu and
selection, Switch feedback and backgrounds in all three third-party apps are
accepted. Busy-button focus is expected Qt behavior. Tokodon's intermittent
chevron is deferred at the user's request, with no further comparison requested.
The recurring provider ScrollBar warning, historical Haruna crash and unclassified
Fusion hover remain separate from accepted rendering and external limitations.

See [canonical findings](FINDINGS.md#batch-3-dropdown-background-manual-acceptance--2026-09-14)
and [chevron deferral](FINDINGS.md#tokodon-intermittent-chevron--investigation-deferred-2026-09-14).
[RENDERING-BATCH3.md](RENDERING-BATCH3.md) preserves the completed session commands;
it is not a request to repeat accepted checks. Earlier publication/kit history
remains in TASKS.md. Batch 4 is complete for scoped provider work; see the [palette findings](FINDINGS.md#batch-4-palette-investigation-and-repair--2026-09-14)
and [scoped instructions](PALETTE-BATCH4.md).

## Batch 7 review — 2026-09-14

Use the [reviewed greeter dispositions](FINDINGS.md#greeter--holonight-greeter-demo-evidence-only).
D01/D03/D04 and the reported F06 sequence are accepted; do not retest them as open
repairs. The avatar display already uses HnAvatar, while the user selector remains
a separate ComboBox. Shared avatar use does not prove the requested avatar-selector
composition or user-selector keyboard reachability. Do not treat generic focus or
authentication acceptance as acceptance of greeter-specific reveal/Tab behavior.
Real pre-session acceptance remains in Batch 8.
