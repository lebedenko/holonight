# Batch 6 — next-session handoff

## F05 external reproduction established — 2026-09-15

[Plain Qt reproduces](FINDINGS.md#f05-plain-qt-external-reproduction--2026-09-15)
in Fusion at actual DPR 1.25/output scale 1 with no HoloNight library mappings.
Real keyboard callbacks show capability loss without leave, replacement enter
and navigation delivery while Qt focus remains null. The user confirms failure
before pointer movement and later click recovery; exit 0 is verified.
[The upstream-report draft](f05/UPSTREAM-REPORT.md) includes sanitized evidence
and a bounded private-cache investigation. It is not submitted. Exact upstream
mechanism remains unresolved; F05 is not repaired and no HoloNight repair owner
is assigned. This diagnosis iteration is complete; no theme/hn or AI repeats.
S01/S02 remain accepted, UQC-211/UQC-215 Done, UQC-201 In Progress, initiative
Accepted. Upstream follow-up, other batches and final integration remain open.

The setup and earlier handoffs below are historical checkpoints.

## F05 activation diagnosis — 2026-09-15

[Setup revalidation](FINDINGS.md#f05-activation-diagnosis-setup--2026-09-15) passes:
230 released kit hashes, archive checksum, all recorded package versions and
unchanged reduced sources. Retained three-mode automated verification is reused.
The [plain-Qt manual checklist](f05/README.md#one-focused-manual-check-when-ready)
now includes session identity/output capture and required returned evidence.
Real-keyboard VT evidence is pending; no external disposition or HoloNight owner
is established. Collect plain first, correlate callbacks/focus/frame signals if
it fails, and run theme/hn only if it passes. Keep F05 unresolved if evidence is
incomplete. S01/S02 remain accepted, UQC-211/UQC-215 Done, UQC-201 In Progress,
initiative Accepted. Other batches and final integration stay outside this work.

## S01 accepted — 2026-09-15

[Verified repair results](FINDINGS.md#s01-repair-accepted-on-hyprland--2026-09-15)
pass both fractional Hyprland styles. S01 accepted; S02 preserved; UQC-211 and
UQC-215 Done. No shell repetition is requested. F05/UQC-201 remain open; next
manual evidence is the [plain-Qt reduced VT check](f05/README.md). Initiative
remains Accepted, not Integrated. The repair-preparation entries below are historical.

## Provider repair and reduced F05 diagnosis — 2026-09-15

Provider repair `0e0f92e` is published and pinned by umbrella `0ee4ef5`.
[UQC-215](UQC-215.md) is Done locally: coordinate matrix, 87 provider CTests,
164 shell hosting tests and 11 AI panel tests pass. No consumer source changes.
Fresh immutable kit `/tmp/holonight-uqc211-8ptiz_ko` is released: 230 hashes,
16 installed checks, 16 staged runtime checks, observer/collector checks and
restoration pass. See [release evidence](FINDINGS.md#s01-provider-repair-and-f05-reduced-diagnosis--2026-09-15)
and the [S01 repair checklist](S01-REPAIR.md).

[F05 diagnosis and fixture](f05/README.md) compare plain Qt, platform theme and
HnApplicationWindow with Fusion. Qt's keyboard-destruction/cache path matches the
retained Hyprland/Sway difference, but exact ownership remains unresolved. Only
a reduced plain-Qt VT check is pending; the completed AI matrix is not repeated.
No focus or repaint workaround was implemented. S01 and F05 remain open;
UQC-211/UQC-201 In Progress, initiative Accepted. Batch 7, deferred Batch 3 work
and final ecosystem integration remain outside this handoff.

The entries below are historical checkpoints.

## Completed manual review — 2026-09-15

[The manual sequence is complete](FINDINGS.md#batch-6-uninstrumented-confirmation-and-manual-sequence-complete--2026-09-15).
No repeat runs are requested. Scale-1 shell frame checks pass on both compositors;
fractional shell failure persists. AI VT-return behavior passes the observed Sway
comparison and fails Hyprland in both styles with and without observation.

Next work: settle the provider-local UQC-215 coordinate contract/SDD and exact
canonical assignment before repair; investigate F05 compositor/Qt activation
ownership using the retained evidence before assigning an AI/provider repair.
S01/F05 remain open; UQC-211/UQC-201 In Progress, UQC-215 Planned, initiative Accepted.
The original checkpoint and preparation instructions below are historical.

## Resume completed — 2026-09-15

Shell tests are published and pinned; the fresh Batch 6 kit passed automated
preparation and restoration. Continue with the [human checklist](SHELL-BATCH6.md)
and record results against the [release evidence](FINDINGS.md#batch-6-verified-investigation-kit--2026-09-15).
The stop instruction and exact state below are the historical starting checkpoint.

## Original stop instruction

On 2026-09-15 the user requested: **make commits, do not generate the Batch 6 kit,
and leave a note to proceed next session**. No kit preparation command was run.
This document is the continuation entry point, not acceptance or a kit release.

## Exact state

- Work began at umbrella `eb9b80c` with clean checkouts and canonical baseline checks.
- Draft umbrella tooling is committed as `19c7119`; this handoff follows it.
- Umbrella shell gitlink remains `fffb1715bac5a57127af5e671033ac33335ffc16`.
- Shell checkout is clean at local `ab780d5d477400cdc70195d37783e9e080ee1d05`,
  following `954a721410804b429f43b0cd65df5dc252a387a1`. Both are test/SDD commits;
  no shell product repair was made.
- Shell local `origin/main` still points at `fffb171`. The push tool request was
  interrupted before a success result; publication is **unconfirmed**. Recheck
  canonical state before retrying publication. Never pin an unpublished commit.
- Provider stays at `638eec25c0934538e747b969b37ab8f63d1722de`; AI stays at
  `7e25e78cc7fb33aa63ed480bc3f328a65e04ca0c`. Neither repository was modified.
- Umbrella `git status` intentionally reports the shell checkout ahead of its
  pinned gitlink. Do not discard those commits with `git submodule update`.
- UQC-211 and UQC-201 remain In Progress; UQC-215 is Planned; initiative Accepted.

Canonical results and limitations are recorded once in
[FINDINGS.md](FINDINGS.md#batch-6-investigation--2026-09-15). See the
[ledger](TASKS.md), [shell SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-211.md),
[proposed provider package](UQC-215.md), and [draft human checklist](SHELL-BATCH6.md).
Raw probes, captures, observer checks and build/test logs remain in `.cache/uqc211/`.

## Continue in this order

1. Re-read umbrella/shell instructions and inspect Git state. Confirm canonical
   publication of the two shell commits, publishing them if still needed and
   authorized. Only then checkpoint the umbrella gitlink. Preserve other pins.
2. Review the **draft** Batch 6 harness before running it:
   - `prepare-rendering-kit.py --batch6` adds shell/AI staging to the existing
     rendering kit procedure; it has not been exercised end to end.
   - `verify-shell-kit.py` is a draft bounded headless Sway startup/mapping matrix;
     it has not run against a Batch 6 prefix. Validate exit classification as well
     as mapping isolation; do not accept a shutdown crash as a clean exit.
   - `session-diagnostics.cpp` and `verify-session-observer.py` have offscreen
     fixture coverage. Actual Wayland keyboard listener coverage is unverified.
     Final Qt event acceptance cannot be collected by the current event filter.
     Resolve the necessary observation gap or preserve it explicitly; never infer
     delivered-but-unhandled navigation solely from unchanged focus.
   - Confirm installed QML/library discovery and runtime paths for shell and AI,
     private profiles, disabled providers, session polling and collector failures.
     Keep entered text and raw non-navigation keys out of F05 evidence.
3. Prepare a **fresh** immutable kit using the reviewed harness. Verify installed
   HoloNight/Fusion behavior at Qt scales 1/1.25, staged module mappings, hashes,
   index records, restoration/refusals, and actual normal/interrupted/forced
   process outcomes. Unit tests for the latter currently use mocked children.
   Keep failed preparation evidence and never mutate earlier released kits.
4. Record the exact kit path/archive hash in FINDINGS.md and finalize the draft
   instructions only after those checks. Then request user-operated Hyprland
   shell comparisons, scale-1 Sway frame confirmation, and Hyprland F05 comparisons
   at Qt scale 1.25. Output scale stays 1. No pointer/focus/VT automation.
5. Keep S01's provider repair branch stopped under UQC-211. UQC-215 needs a
   provider-local SDD and a Ready assignment before implementation. S02 remains
   unconfirmed outside fixtures. F05 remains an umbrella/AI ownership gate.
6. Record returned evidence once in FINDINGS.md. Do not close UQC-211 or F05
   without their acceptance or explicit evidence-based disposition. Preserve
   Batch 4 acceptance, external P01, removed Batch 5, reviewed Batch 7 and deferred
   Batch 3 findings. Stop after the focused sequence and confirming comparison.

## Verification already performed

Exact results are in FINDINGS.md and the shell SDD. There is no need to rerun the
full product suite merely to resume documentation work. Narrow checks should be
repeated for any further harness/fixture edits. A new installed kit still requires
its own installation, mapping, restoration, outcome and manual verification.
