"""Release requirements for fresh Settings scale-1 verification."""

COMPONENTS = ("config", "system-services", "shell-config", "qt", "settings")
GATES = {
    "provider-controls-policy", "settings-controls-policy", "provider-full",
    "settings-full", "render-observer-build", "settings-helper",
    "collector-tests", "profile-tests", "terminal-syntax", "sway-config",
    "real-seat-device-bindings", "licensing", "documentation",
} | {"settings-installed-" + mode for mode in (
    "default", "environment", "command-line", "configuration"
)}


def validate(build, checks, recorded_inventory, current_inventory):
    if recorded_inventory != current_inventory:
        raise ValueError("Package drift blocks release; prepare a fresh kit")
    required_build = {f"{c}-{p}" for c in COMPONENTS for p in ("configure", "build", "install")}
    for required, results in ((required_build, build), (GATES, checks)):
        for name in sorted(required):
            if name not in results or results[name]["code"] != 0:
                raise ValueError("Missing or failed release gate: " + name)
