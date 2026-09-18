"""Release Settings only after all fresh-build and readiness gates pass."""
from common import docs, kit, prefix, root, run, work
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

assert len(sys.argv) == 2, "Release cannot skip checks"
spec = importlib.util.spec_from_file_location("policy", Path(__file__).with_name("settings-policy.py"))
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

def latest(name):
    return {r["name"]: r for r in map(json.loads, (work / name).read_text().splitlines())}

def output(*cmd):
    return subprocess.check_output(cmd, text=True).strip()

profile = json.loads((kit / "profile.json").read_text())
assert profile["profile"] in ("settings-scale1", "ai-scale1")
surface = profile["profile"].removesuffix("-scale1")
executable = "holonight-chat" if surface == "ai" else "holonight-settings"
assert output("git", "rev-parse", "HEAD") == profile["preparation"]
assert not output("git", "status", "--porcelain"), "Dirty umbrella checkout"
policy.validate(latest("results.jsonl"), latest("focused-results.jsonl"),
                (kit / "package-inventory.txt").read_text(),
                subprocess.check_output(["pacman", "-Q"], text=True), profile["profile"])
for row in json.loads((kit / "revisions.json").read_text()):
    repo, pin = row["repository"], row["pin"]
    assert output("git", "rev-parse", "HEAD:" + repo) == pin
    assert output("git", "-C", repo, "rev-parse", "HEAD") == pin
    assert not output("git", "-C", repo, "status", "--porcelain")
    assert output("git", "-C", repo, "ls-remote", "origin", "refs/heads/main").split()[0] == pin
resolved = []
for cache in (work / "build").glob("*/CMakeCache.txt"):
    for line in cache.read_text().splitlines():
        if line.startswith(("HoloNight", "Holonight")) and "_DIR:PATH=" in line:
            assert Path(line.split("=", 1)[1]).is_relative_to(prefix), line
            resolved.append(str(cache.relative_to(work)) + ":" + line)
assert resolved
(kit / "resolved-packages.txt").write_text("\n".join(resolved) + "\n")
for style in ("default", "Fusion"):
    result = json.loads((work / (surface + "-helper-" + style) / "result.json").read_text())
    assert result["isolation"] == "verified" and set(result["measured_dpr"].values()) == {1}
    assert result["selector"] == (None if style == "default" else style)
    assert result["exit"] == -15 and result["origins"]
    assert result["executable"] == str(prefix / "bin" / executable)
    log = Path(result["evidence"]) / "launch.log"
    assert hashlib.sha256(log.read_bytes()).hexdigest() == result["log_sha256"]
assert str(kit) in (kit / "README.md").read_text()
if surface == "ai":
    guide = (kit / "README.md").read_text()
    assert "__KIT__" not in guide
    (kit / "README.md").write_text(guide.replace(
        "**Preparation pending; no READY kit has been released.**",
        "**Automated readiness passed; exactly two human runs pending.**"))
provenance = {str(p.relative_to(kit)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (
    prefix / "bin" / executable, prefix / "lib/render-diagnostics.so", kit / "render-diagnostics.cpp")}
provenance.update({str(p.relative_to(kit)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in (prefix / "lib").rglob("*.so*") if p.is_file()})
(kit / "binary-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
evidence = kit / "verification"
evidence.mkdir()
for name in ("logs", surface + "-helper-default", surface + "-helper-Fusion"):
    shutil.copytree(work / name, evidence / name)
for name in ("results.jsonl", "focused-results.jsonl"):
    shutil.copy2(work / name, evidence)
for component in ("qt", surface):
    shutil.copy2(work / "build" / component / "Testing/Temporary/LastTest.log", evidence / (component + "-last-ctest.log"))
(kit / "SHA256SUMS").write_text("".join(
    f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(kit)}\n"
    for p in sorted(kit.rglob("*")) if p.is_file() and p.name not in ("SHA256SUMS", "READY")))
(kit / "READY").write_text(f"{surface} scale-1 automated readiness passed; exactly two human runs pending. P03 and Weather remain closed. UQC-201 In Progress; initiative Accepted.\n")
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
print("READY", kit, "Archive SHA256", digest)
