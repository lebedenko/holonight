# Batch 6 — next-session handoff

## Stop instruction

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
- UQC-211 and UQC-201 remain In Progress; UQC-213 is Planned; initiative Accepted.

Canonical results and limitations are recorded once in
[FINDINGS.md](FINDINGS.md#batch-6-investigation--2026-09-15). See the
[ledger](TASKS.md), [shell SDD](../../../holonight-shell/docs/sdd/unified-qtquick-controls/UQC-211.md),
[proposed provider package](UQC-213.md), and [draft human checklist](SHELL-BATCH6.md).
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
5. Keep S01's provider repair branch stopped under UQC-211. UQC-213 needs a
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
