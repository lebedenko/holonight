"""Prepare fresh scale-1 sources; prior archives supply inventory evidence only."""
import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path
import subprocess
import tarfile
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--baseline", required=True)
parser.add_argument("--prior-archive", required=True, type=Path)
parser.add_argument("--profile", choices=("settings-scale1", "ai-scale1"), default="settings-scale1")
args = parser.parse_args()
surface = args.profile.removesuffix("-scale1")
root = Path.cwd()
docs = Path(__file__).resolve().parent.parent

def output(*command):
    return subprocess.check_output(command, text=True).strip()

baseline = output("git", "rev-parse", args.baseline + "^{commit}")
head = output("git", "rev-parse", "HEAD")
subprocess.run(["git", "merge-base", "--is-ancestor", baseline, head], check=True)
assert not output("git", "status", "--porcelain"), "Dirty umbrella checkout"
# Preparation tooling may be a local checkpoint; the planning baseline must be published.
remote = output("git", "ls-remote", "origin", "refs/heads/main").split()[0]
subprocess.run(["git", "merge-base", "--is-ancestor", baseline, remote], check=True)
rows = []
for line in output("git", "ls-tree", baseline).splitlines():
    mode, kind, pin, repo = line.split()
    if mode != "160000":
        continue
    assert output("git", "rev-parse", "HEAD:" + repo) == pin
    assert output("git", "-C", repo, "rev-parse", "HEAD") == pin
    assert not output("git", "-C", repo, "status", "--porcelain")
    canonical = output("git", "-C", repo, "ls-remote", "origin", "refs/heads/main").split()[0]
    assert canonical == pin, "Review moved canonical main; do not adopt it automatically"
    rows.append(dict(repository=repo, pin=pin, canonical_main=canonical))
archive = args.prior_archive.resolve()
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
assert digest == (archive.parent / "archive.sha256").read_text().split()[0]
with tarfile.open(archive) as saved:
    base = archive.name.removesuffix(".tar.gz")
    prior_inventory = saved.extractfile(base + "/package-inventory.txt").read().decode()
    prior_versions = saved.extractfile(base + "/PROVIDER.txt").read().decode()
current = subprocess.check_output(["pacman", "-Q"], text=True)
kit = Path(tempfile.mkdtemp(prefix=f"holonight-uqc201-{surface}-"))
work = root / ".cache" / kit.name
(work / "logs").mkdir(parents=True)
subprocess.run(["python3", docs / "prepare-guided-kit.py", kit], check=True)
(kit / "profile.json").write_text(json.dumps(dict(profile=args.profile, baseline=baseline, preparation=head), indent=2) + "\n")
(kit / "revisions.json").write_text(json.dumps(rows, indent=2) + "\n")
(kit / "package-inventory.txt").write_text(current)
(kit / "prior-inventory.txt").write_text(prior_inventory)
(kit / "prior-PROVIDER.txt").write_text(prior_versions)
(kit / "inventory.diff").write_text("".join(difflib.unified_diff(prior_inventory.splitlines(True), current.splitlines(True), fromfile="P03 inventory", tofile=f"{surface} fresh inventory")))
(kit / "prior-archive.json").write_text(json.dumps(dict(archive=str(archive), sha256=digest, reuse="Inventory comparison only; no binaries or prior suite results reused"), indent=2) + "\n")
guide = (docs / ("BATCH8-AI-SCALE1.md" if surface == "ai" else "BATCH8-SETTINGS.md")).read_text().replace("__KIT__", str(kit))
(kit / "README.md").write_text(re.sub(rf"holonight-uqc201-{surface}-[a-z0-9_]+", kit.name, guide))
(root / f".cache/uqc201-{surface}-kit").write_text(str(kit) + "\n")
print(kit)
