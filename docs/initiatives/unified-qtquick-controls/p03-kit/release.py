"""Require focused acceptance, archive and verify restoration without overwrite."""

from common import docs, kit, prefix, run, work
from pathlib import Path
import json
import subprocess
import sys
import ast
import hashlib
import shutil
import tarfile

assert len(sys.argv) == 2, "Release cannot skip checks or restoration"


def latest(filename):
    return {
        row["name"]: row
        for row in map(json.loads, (work / filename).read_text().splitlines())
    }


profile = json.loads((kit / "profile.json").read_text())
focused = profile["profile"] == "observer-repair"
assert (
    subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    == profile["baseline"]
)
assert not subprocess.check_output(["git", "status", "--porcelain"], text=True), (
    "Dirty checkout"
)
build = latest("results.jsonl")
for component in (
    ("config", "qt", "ai")
    if focused
    else (
        "config",
        "system-services",
        "shell-config",
        "qt",
        "appearance-adapters",
        "shell",
        "settings",
        "ai",
        "pkg-manager",
        "greeter",
    )
):
    for phase in ("configure", "build", "install"):
        assert build[component + "-" + phase]["code"] == 0
checks = latest("focused-results.jsonl")
required = {
    "provider-window-core",
    "provider-palette-policy",
    "provider-package",
    "shell-launch-policy",
    "settings-startup",
    "provider-startup",
    "diagnostic-configure",
    "diagnostic-build",
    "diagnostic-collect",
    "diagnostic-shared",
    "diagnostic-positive",
    "diagnostic-plain-boundary",
    "diagnostic-external-boundary",
    "render-observer-build",
    "ai-workspace-helper",
    "collector-tests",
    "terminal-syntax",
    "sway-config",
    "installer-check",
    "licensing",
    "documentation",
}
for scale in ("1", "1.25"):
    required |= {"ai-controls-" + scale, "settings-controls-" + scale}
    required |= {"ai-qml-" + style + "-" + scale for style in ("Holonight", "Fusion")}
for name in ("ai", "pkg-manager", "greeter"):
    required |= {name + "-build", name + "-installed"}
for mode in ("default", "environment", "command-line", "configuration"):
    required.add("settings-installed-" + mode)
    required |= {
        exe + "-installed-" + mode
        for exe in ("holonight_demo", "holonight_controls_gallery")
    }
if focused:
    required = {
        "provider-window-core",
        "provider-observer-policy",
        "diagnostic-configure",
        "diagnostic-build",
        "observer-collect",
        "observer-assert",
        "observer-installed-regression",
        "render-observer-build",
        "ai-workspace-helper",
        "collector-tests",
        "terminal-syntax",
        "sway-config",
        "real-seat-device-bindings",
        "licensing",
        "documentation",
    }
assert required <= checks.keys(), required - checks.keys()
for name in required:
    expected = (
        1
        if name in ("diagnostic-plain-boundary", "diagnostic-external-boundary")
        else 0
    )
    assert checks[name]["code"] == expected, name
if focused:
    report = json.loads((work / "matrix/stability-assertions.json").read_text())
    assert len(report["cases"]) == 98 and report["failed_cases"] == 0
    assert len(report["observer_equivalence"]) == 49
else:
    assert (
        "32 palette/render transition failures"
        in (work / "logs/diagnostic-plain-boundary.log").read_text()
    )
    assert (
        "8 palette/render transition failures"
        in (work / "logs/diagnostic-external-boundary.log").read_text()
    )
    assert len(list((work / "matrix").glob("*/measurements.json"))) == 18
resolved = []
for cache in (work / "build").glob("*/CMakeCache.txt"):
    for line in cache.read_text().splitlines():
        if line.startswith(("HoloNight", "Holonight")) and "_DIR:PATH=" in line:
            assert Path(line.split("=", 1)[1]).is_relative_to(prefix), line
            resolved.append(str(cache.relative_to(work)) + ":" + line)
assert resolved
(kit / "resolved-packages.txt").write_text("\n".join(resolved) + "\n")
prior_pins = {
    row["repository"]: row["pin"]
    for row in json.loads((kit / "prior-evidence/revisions.json").read_text())
}
for row in json.loads((kit / "revisions.json").read_text()):
    repo = row["repository"]
    assert (
        subprocess.check_output(
            ["git", "-C", repo, "rev-parse", "HEAD"], text=True
        ).strip()
        == row["pin"]
    )
    assert (
        subprocess.check_output(["git", "rev-parse", "HEAD:" + repo], text=True).strip()
        == row["pin"]
    )
    assert not subprocess.check_output(
        ["git", "-C", repo, "status", "--porcelain"], text=True
    )
    assert row["canonical_main"] == row["pin"]
    assert (
        subprocess.check_output(
            ["git", "-C", repo, "ls-remote", "origin", "refs/heads/main"], text=True
        ).split()[0]
        == row["pin"]
    )
    if repo != "holonight-qt":
        assert prior_pins[repo] == row["pin"], "Prior full-suite evidence invalidated"
assert (
    subprocess.check_output(["pacman", "-Q"], text=True)
    == (kit / "package-inventory.txt").read_text()
), "Package drift blocks release"
assert (kit / "PROVIDER.txt").read_bytes() == (
    kit / "prior-evidence/PROVIDER.txt"
).read_bytes()
for style in ("default", "Fusion"):
    result_path = work / ("ai-palette-" + style) / "ai-check/result.json"
    result = json.loads(result_path.read_text())
    assert result["closed_run_refused"] and set(
        result["palette_window_dpr"].values()
    ) == {1.25}
    colors = result["workspace_color_round_trip"]
    assert colors[0] != colors[1] and colors[0] == colors[2]
    assert (
        hashlib.sha256((result_path.parent / "launch.log").read_bytes()).hexdigest()
        == result["log_sha256"]
    )
assert str(kit) in (kit / "README.md").read_text()
provenance = {}
for relative in [
    "lib/palette-diagnostics.so",
    "bin/holonight-chat",
    "lib/libholonight_config.so",
]:
    binary = prefix / relative
    provenance[relative] = hashlib.sha256(binary.read_bytes()).hexdigest()
provenance["observer_source"] = hashlib.sha256(
    (kit / "palette-diagnostics.cpp").read_bytes()
).hexdigest()
provenance["baseline"] = profile["baseline"]
(kit / "binary-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
# Snapshot complete evidence, including expected boundaries and failed harness attempts.
evidence = kit / "verification"
evidence.mkdir()
for name in ("logs", "matrix", "ai-palette-default", "ai-palette-Fusion"):
    shutil.copytree(work / name, evidence / name)
if not focused:
    shutil.copytree(work / "build/shell/uqc-launch-logs", evidence / "shell-launches")
    shutil.copy2(
        work / "build/qt/tests/package-install-test/isolated-style.log",
        evidence / "provider-installed-styles.log",
    )
    for component in ("qt", "shell", "settings", "ai"):
        shutil.copy2(
            work / "build" / component / "Testing/Temporary/LastTest.log",
            evidence / (component + "-last-ctest.log"),
        )
for name in ("results.jsonl", "focused-results.jsonl"):
    shutil.copy2(work / name, evidence / name)
for path in Path(__file__).parent.glob("*"):
    if not path.is_file():
        continue
    shutil.copy2(path, kit / "preparation" / path.name)
for path in kit.rglob("*.py"):
    ast.parse(path.read_text())
# READY is restored last; the archive hash also protects its contents.
(kit / "SHA256SUMS").write_text(
    "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(kit)}\n"
        for path in sorted(kit.rglob("*"))
        if path.is_file() and path.name not in ("SHA256SUMS", "READY")
    )
)
(kit / "READY").write_text(
    "Focused P03 automated readiness passed. Exactly two human AI Settings palette checks pending; P03 open, UQC-201 In Progress, initiative Accepted. See README.md.\n"
)
archive = work / (kit.name + ".tar.gz")
assert not archive.exists()
with tarfile.open(archive, "w:gz") as saved:
    saved.add(kit, arcname=kit.name)
backup = kit.with_name(kit.name + "-before-restore")
assert not backup.exists()
kit.rename(backup)
restore = ["python3", docs / "restore-rendering-kit.py", archive]
run("restoration", restore)
run("restoration-refusal", restore, 2)
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(work / "archive.sha256").write_text(digest + "  " + archive.name + "\n")
print("READY", kit)
print("Hashes", len((kit / "SHA256SUMS").read_text().splitlines()))
print("Archive SHA256", digest)
