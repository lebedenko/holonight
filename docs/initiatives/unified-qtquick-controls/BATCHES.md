# Completion batches

Accepted execution order from the user plan, 2026-09-13. UQC-201 remains In Progress;
the initiative remains Accepted. Preserve existing accepted results unless affected
by a later change. Record observations once in FINDINGS.md and link local SDDs.

| Batch | Gates | Exit criteria |
|---|---|---|
| 1 | D02, F07; publication | Close Settings Weather diagnostics and both launcher styles using the verified kit; publish provider handoff and umbrella checkpoints. |
| 2 | A01, A02, A04 | Shell Polkit identity rows, password/error visibility and fractional Askpass borders; failed-authentication tests; preserve A03 cancellation acceptance. |
| 3 | F03, F04, R01–R04, C01, C02, C04–C06 | Classify Haruna crash/diagnostics first; resolve icons, conditional menu spacing, selection/keyboard feedback, Fusion ownership and help-popup behavior. F03 needs attribution, not an assumed focus repair. |
| 4 | P01, P02 | Reproduce NeoChat/Tokodon navigation palette changes and mixed picker palettes; identify application/provider/backend ownership; dark/light round trips and overrides. |
| 5 | L01, L02, C03 | Settings slider and AI Temperature geometry in their owners; classify Tokodon Switch overflow before repair. |
| 6 | S01, S02, F05 | Fractional shell stability/topbar; investigate AI keyboard delivery and activation after VT return; repair the demonstrated owner. |
| 7 | G01–G06 | Greeter keyboard/reveal, disabled/password appearance, avatar selector and power buttons; demo before real pre-session gate. |
| 8 | Remaining UQC-201 | Final ecosystem acceptance at clean published pins. |

For batches 2–7, reproduce and confirm ownership, prepare the repository-local SDD,
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


## Batch 3 implementation checkpoint — 2026-09-14

Published provider `fbffc87` repairs shared icons, conditional menu spacing,
explicit delegate selection and the whole-control Switch focus outline. Automated
verification and ownership/evidence limits are recorded once in
[FINDINGS.md](FINDINGS.md#batch-3-investigation-and-rendering-repair--2026-09-14).
The fresh immutable kit and restoration command are in the
[ledger](TASKS.md#batch-3-focused-kit--2026-09-14); use the
[focused manual instructions](RENDERING-BATCH3.md).
Batch 3 remains open. Preserve Batches 1–2; broader integration remains Batch 8.
