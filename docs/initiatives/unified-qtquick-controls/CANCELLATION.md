# UQC-205 — one manual direct-cancel check

Completed on 2026-09-12: see the [canonical manual result](FINDINGS.md#manual-polkit-cancellation-acceptance--2026-09-12).
No repeat is requested. Instructions below are retained for reference.
A01/A02/A04 remain pending. Broad acceptance stays paused.
Ready kit: `/tmp/holonight-uqc205-irzzhjcz`. Installed private-authority cancellation and shutdown checks pass.
Provider remains `65c806f`; default HoloNight, Qt scale 1.25, Sway output scale 1.

From a fresh real **tux VT login**, outside the previous compositor, run:

```sh
python3 /tmp/holonight-uqc205-irzzhjcz/guided-session.py sway
```

In the Sway terminal, run `python3 "$UQC_KIT/owned-auth/auth-test.py" preflight`.
Use its printed evidence directory as `UQC_RUN` in both terminals. Review the
session/process/service records: use this isolated login with no competing agent.
Do not stop or replace an existing agent. Then run:

```sh
export UQC_RUN=/home/tux/uqc-auth-evidence/PRINTED_TIMESTAMP
python3 "$UQC_KIT/owned-auth/auth-test.py" agent --run "$UQC_RUN"
```

Type `ISOLATED` after that review. Open a second terminal with Super+Return,
set the same `UQC_RUN`, then run each command separately:

```sh
python3 "$UQC_KIT/owned-auth/auth-test.py" registration --run "$UQC_RUN"
python3 "$UQC_KIT/owned-auth/auth-test.py" challenge --run "$UQC_RUN"
```

Registration must report PASS. Type `REGISTERED` when ready, then **Cancel the
prompt without entering credentials or selecting an identity**. The helper forces
default HoloNight at Qt scale 1.25. Report whether Cancel closed the prompt, the
printed challenge outcome/exit, and the evidence directory. Do not press Ctrl+C
in the challenge terminal: it is bounded to 60 seconds and records timeout as a
failure. Normal denial/cancellation (126 or 127) plus the observed prompt is required.

After the challenge returns and its result is recorded, Ctrl+C in the **agent**
terminal stops only that child agent. Report its exit too, then exit Sway with
Super+Shift+E. Agent exit is cleanup, not evidence of challenge completion.
No failed password submission, desktop input automation, or other acceptance run.
