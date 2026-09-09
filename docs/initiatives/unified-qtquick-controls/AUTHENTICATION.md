# UQC-201 isolated authentication kit

Pending user operation. This kit uses the provider and consumers recorded in
PROVIDER.txt. It is temporary and must be regenerated if /tmp is cleared or Qt
packages change. No agent or challenge ran during preparation.

Save work and enter a real, separate local login as tux on a spare VT. Do not use
sudo, su, SSH, a nested compositor, or a private bus as a replacement for a login.
Do not change either user's normal services, passwords, configuration or Polkit
rules. If the existing tux login is unavailable, report that prerequisite.

Start one minimal compositor, with no normal session configuration:

```sh
Hyprland --config /tmp/holonight-uqc201-manual/hyprland.conf
# Or, in a separate test login:
sway --config /tmp/holonight-uqc201-manual/sway.conf
```

Super+Enter opens another test terminal; Super+Shift+E exits the test compositor.
The terminal wrapper keeps its shell in the real logind session. Its disabled
Kitty user-bus warning is expected; the shell receives the real session bus.

```sh
UQC_KIT=/tmp/holonight-uqc201-manual
/usr/bin/python3 "$UQC_KIT/auth-test.py" preflight
```

The helper refuses any user except tux (UID 1001). Review identity.txt (actual
session, Active=yes, Remote=no), processes.txt, user-services.txt,
registration-before.txt and policy.txt in the printed evidence directory. Confirm
no known competing agent serves this test session. Leave agents belonging to other
sessions untouched. Policy must require auth_admin for the harmless exec action.
Journal absence does not prove registration absence.

Set UQC_RUN to the exact printed evidence path in EACH terminal. Do not reuse a
run from an earlier login. First terminal:

```sh
LD_LIBRARY_PATH="$UQC_KIT/prefix/lib" /usr/bin/python3 "$UQC_KIT/auth-test.py" agent --run "$UQC_RUN"
```

Type ISOLATED only after reviewing preflight. The helper checks hyprpolkitagent
0.1.3-10 and Qt6 linkage, then launches only its own agent with this kit's prefix.
Second terminal, same actual login:

```sh
UQC_KIT=/tmp/holonight-uqc201-manual
# Set UQC_RUN here too.
/usr/bin/python3 "$UQC_KIT/auth-test.py" registration --run "$UQC_RUN"
/usr/bin/python3 "$UQC_KIT/auth-test.py" challenge --run "$UQC_RUN"
```

Registration must print PASS: the actual successful request/reply, live bus owner,
PID and logind session must agree. If it fails, stop only the helper's agent with
Ctrl+C in its own terminal and preserve evidence. Never replace a running agent.
The challenge rechecks registration and asks for REGISTERED before running exactly
`pkexec --disable-internal-agent /usr/bin/true`. It changes nothing if unexpectedly
authorized; no prompt does not count as acceptance.

Manually inspect actual controls and geometry, type and erase disposable text to
check masking, navigate with Tab/Shift+Tab, hover buttons and CANCEL. Never type a
real password or submit. No automated pointer or focus interaction is permitted.
Record prompt appearance, component/library origins, scale, masking, focus,
clipping and cancellation result. Stop only the helper's child using Ctrl+C in
the first terminal, then exit the compositor and log tux out. Repeat for the other
compositor in a fresh login. Return evidence paths under /home/tux/uqc-auth-evidence
and observations; do not publish whole authentication logs.

The adjacent MANUAL.md contains the full UQC-201 matrix. Its umbrella source paths
are for the original workspace; this accessible kit prefix may be used for
terminal-only disposable checks. D-Bus service files record the original configured
prefix, so relocated D-Bus activation remains blocked until a separately configured
accessible staging prefix is prepared. Do not edit service Exec paths and call
that a test of the original installed activation contract.
