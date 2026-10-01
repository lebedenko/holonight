# HoloNight labwc theme

Implement the Accent decoration design using HoloNight's selected scheme, accent,
and title fonts. The Settings page remains deferred; configuration uses labwc XML
and the existing appearance-adapter CLI.

| Repository | Responsibility |
| --- | --- |
| `holonight-appearance-adapters` | Theme/SVG generation, installation, apply/status/revert, font ownership, diagnostics, recovery and verification |
| `holonight-qt` | Existing semantic colors and resolved typography; no duplicated palette |
| `holonight-shell` | Existing startup adapter invocation; no integration change required |
| `holonight-icons` | Shared design language; specialized window controls remain with the adapter |
| Umbrella | Initiative and staged-install verification |

Implementation and enablement instructions are in the
[component guide](../../../holonight-appearance-adapters/docs/labwc-theme.md).
The installed fallback is `${prefix}/share/themes/HoloNight/labwc/` with 37 files;
no user configuration is installed. The umbrella source installer already stages
appearance-adapters and records all staged files in its ownership manifest, so the
new assets follow the existing safe install/uninstall flow.

## Verification

Run the component build and CTest suite, then validate the staged payload:

```sh
python3 tests/check_staged_labwc.py /path/to/stage/usr
```

The component `labwc_install_tests` exercises actual CMake installation with `/usr`,
a user prefix and `DESTDIR`, checks all theme files in `install_manifest.txt`, then
removes only the staged manifest entries and verifies that no payload remains.
`labwc_cli_tests` covers scheme/accent/title font projection, all SVG states,
idempotence, protocol-v1 compatibility, custom paths, override and ownership
conflicts, malformed XML, concurrent calls, failed writes, rollback, interrupted
apply recovery and revert. Optional labwc 0.20.2 headless smoke screenshots verify
active/inactive focus, hover, maximize/restore, shade, menu, reload and 1×/2× rendering.

Implementation evidence (2026-10-02): 7/7 component CTests passed with Qt 6.11.2;
headless visual review completed on labwc 0.20.2 / wlroots 0.20.2. Component implementation: `holonight-appearance-adapters@8c7e328`, pinned by the
umbrella integration commit. These are local commits; no published handoff is claimed. The original `ssd.png` was not present in the workspace, so the supplied
Accent design specification is the visual reference.
