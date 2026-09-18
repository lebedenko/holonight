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


AI_COMPONENTS = ("config", "qt", "ai")
AI_GATES = (GATES - {name for name in GATES if name.startswith("settings-")}) | {
    "ai-controls-policy", "ai-full", "ai-installed", "ai-helper",
}


def validate(build, checks, recorded_inventory, current_inventory, profile="settings-scale1"):
    if profile not in ("settings-scale1", "ai-scale1"):
        raise ValueError("Unknown scale-1 profile: " + profile)
    components, gates = (AI_COMPONENTS, AI_GATES) if profile == "ai-scale1" else (COMPONENTS, GATES)
    if recorded_inventory != current_inventory:
        raise ValueError("Package drift blocks release; prepare a fresh kit")
    required_build = {f"{c}-{p}" for c in components for p in ("configure", "build", "install")}
    for required, results in ((required_build, build), (gates, checks)):
        for name in sorted(required):
            if name not in results or results[name]["code"] != 0:
                raise ValueError("Missing or failed release gate: " + name)
