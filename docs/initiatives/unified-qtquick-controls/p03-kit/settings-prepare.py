"""Prepare fresh Settings sources; prior archives supply inventory evidence only."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--baseline", required=True)
parser.add_argument("--prior-archive", required=True, type=Path)
args = parser.parse_args()
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
kit = Path(tempfile.mkdtemp(prefix="holonight-uqc201-settings-"))
work = root / ".cache" / kit.name
(work / "logs").mkdir(parents=True)
subprocess.run(["python3", docs / "prepare-guided-kit.py", kit], check=True)
(kit / "profile.json").write_text(json.dumps(dict(profile="settings-scale1", baseline=baseline, preparation=head), indent=2) + "\n")
(kit / "revisions.json").write_text(json.dumps(rows, indent=2) + "\n")
(kit / "package-inventory.txt").write_text(current)
(kit / "prior-inventory.txt").write_text(prior_inventory)
(kit / "prior-PROVIDER.txt").write_text(prior_versions)
(kit / "inventory.diff").write_text("".join(difflib.unified_diff(prior_inventory.splitlines(True), current.splitlines(True), fromfile="P03 inventory", tofile="Settings fresh inventory")))
(kit / "prior-archive.json").write_text(json.dumps(dict(archive=str(archive), sha256=digest, reuse="Inventory comparison only; no binaries or prior suite results reused"), indent=2) + "\n")
(kit / "README.md").write_text((docs / "BATCH8-SETTINGS.md").read_text().replace("__KIT__", str(kit)))
(root / ".cache/uqc201-settings-kit").write_text(str(kit) + "\n")
print(kit)
