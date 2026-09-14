# Batch 2 — targeted authentication checkpoint

Status 2026-09-14: **Batch 2 complete.** A01/A04 manually accepted, A02 verified
and saved process outcomes classified; see the
[canonical evidence review](FINDINGS.md#batch-2-authentication-manual-acceptance--2026-09-14).
The instructions below are retained as run provenance, not a request to repeat the
accepted visual checks.

Fresh kit: `/tmp/holonight-uqc205-b2_vmvoyd51`. A03 and Batch 1 stay accepted. A02 is verified synthetically;
no failed password submission is requested. Use one fresh real **tux VT login**,
outside a compositor, then start this kit's Hyprland session (output scale 1):

```sh
python3 /tmp/holonight-uqc205-b2_vmvoyd51/guided-session.py hyprland
```

The commands below default to Qt scale 1.25. Every run is automatically indexed in
`~/uqc-auth-evidence/session-<login-id>.jsonl`; no evidence path needs copying.
Use only this kit's terminals. Each agent launch records preflight files and asks
for `ISOLATED` after you review them for competing agents. Stop if one is present.
Do not stop another login's agent or any existing service.

1. In the first terminal, start owned Polkit with HoloNight:

   ```sh
   python3 "$UQC_KIT/authentication-test.py" polkit --style Holonight
   ```

   Wait for **Exclusive registration verified**. Open another kit terminal with
   Super+Return and run:

   ```sh
   python3 "$UQC_KIT/authentication-test.py" challenge --style Holonight
   ```

   Inspect the identity selector's labels and avatars. Select an identity, confirm
   it with Continue, inspect the password prompt, then Cancel without credentials.
   Let the bounded challenge finish; do not interrupt its terminal. In the agent
   terminal, Ctrl+C stops only that test agent after the challenge has returned.

2. Repeat with Fusion in the same login after the first agent has stopped:

   ```sh
   python3 "$UQC_KIT/authentication-test.py" polkit --style Fusion
   ```

   In the other terminal, after exclusive registration is verified:

   ```sh
   python3 "$UQC_KIT/authentication-test.py" challenge --style Fusion
   ```

   Repeat the identity/prompt inspection and credential-free cancellation, then
   Ctrl+C in the Fusion agent terminal after the challenge returns.

3. Inspect Askpass with Fusion:

   ```sh
   python3 "$UQC_KIT/authentication-test.py" askpass --style Fusion
   ```

   Move focus away from the editor yourself and inspect all four unfocused borders.
   Focus the editor and inspect its ring. Cancel; expected normal exit 1, zero output
   bytes. Use disposable text only if needed. No actual credentials are needed.

Exit this test Hyprland session with Super+Shift+E. Report the identity labels/avatars
and selection in each style, Askpass border/ring appearance, challenge outcomes and
any abnormal shutdown. The indexed evidence contains session identity, output and
Qt scales, requested/actual style, PID and loader module paths, diagnostics and
bounded exit classifications. Agent/module records use the PID-tagged loader log
because authentication processes deliberately deny `/proc/<pid>/maps` access.

Record returned observations once in FINDINGS.md. Missing evidence leaves only its
corresponding gate pending. Other compositors, successful authentication and broader
activation remain in Batch 8. Batch 3 begins with Haruna crash/diagnostic classification.
