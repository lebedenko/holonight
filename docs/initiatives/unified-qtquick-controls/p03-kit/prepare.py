"""Create a fresh P03 kit, retaining prior evidence without modifying earlier releases."""

import argparse
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--prior", required=True, type=Path)
args = parser.parse_args()
root = Path.cwd()
docs = Path(__file__).resolve().parent.parent
assert (
    subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    == "6f7af409a38b7a217fec38bf607e43446f86c07f"
)
assert (args.prior / "READY").is_file()
versions = (args.prior / "PROVIDER.txt").read_text()
assert (
    subprocess.check_output(
        ["pacman", "-Q", *[line.split()[0] for line in versions.splitlines()]],
        text=True,
    )
    == versions
), "Package drift blocks reuse"
rows = []
for line in subprocess.check_output(["git", "ls-tree", "HEAD"], text=True).splitlines():
    mode, kind, pin, repo = line.split()
    if mode != "160000":
        continue
    assert (
        subprocess.check_output(
            ["git", "-C", repo, "rev-parse", "HEAD"], text=True
        ).strip()
        == pin
    )
    assert not subprocess.check_output(
        ["git", "-C", repo, "status", "--porcelain"], text=True
    )
    remote = subprocess.check_output(
        ["git", "-C", repo, "remote", "get-url", "origin"], text=True
    ).strip()
    published = subprocess.check_output(
        ["git", "-C", repo, "ls-remote", "origin", "refs/heads/main"], text=True
    ).split()[0]
    assert published == pin, (
        "Review publication ancestry explicitly if canonical main moved; never adopt it"
    )
    rows.append(dict(repository=repo, pin=pin, canonical_main=published, remote=remote))
retained = (
    "results.jsonl",
    "revisions.json",
    "PROVIDER.txt",
    "retained-package-provenance.json",
)
manifest = dict(
    line.split("  ", 1)[::-1]
    for line in (args.prior / "SHA256SUMS").read_text().splitlines()
)
for name in retained:
    assert (
        hashlib.sha256((args.prior / name).read_bytes()).hexdigest() == manifest[name]
    )
prior_work = root / ".cache" / args.prior.name
archive = prior_work / (args.prior.name + ".tar.gz")
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
assert digest == (prior_work / "archive.sha256").read_text().split()[0]
kit = Path(tempfile.mkdtemp(prefix="holonight-uqc201-p03-"))
kit.chmod(0o755)
work = root / ".cache" / kit.name
(work / "logs").mkdir(parents=True)
subprocess.run(["python3", str(docs / "prepare-guided-kit.py"), str(kit)], check=True)
(kit / "BASELINE.txt").write_text("6f7af409a38b7a217fec38bf607e43446f86c07f\n")
(kit / "PROVIDER.txt").write_text(versions)
(kit / "package-inventory.txt").write_text(
    subprocess.check_output(["pacman", "-Q"], text=True)
)
(kit / "revisions.json").write_text(json.dumps(rows, indent=2) + "\n")
for name in ("appearance-dark.toml", "appearance-light.toml"):
    shutil.copy2(args.prior / name, kit / name)
prior = kit / "prior-evidence"
prior.mkdir()
for name in (
    "results.jsonl",
    "revisions.json",
    "PROVIDER.txt",
    "retained-package-provenance.json",
):
    shutil.copy2(args.prior / name, prior / name)
(prior / "README.md").write_text(
    "Prior evidence only from "
    + str(args.prior)
    + ". Full-suite results apply to recorded revisions and listed package versions, not a fresh pass. The provider changed and receives focused revalidation. Other pins must remain identical. The full current inventory is separate; prior inventory covers only its listed packages.\n"
)
print(kit)

(prior / "archive.json").write_text(
    json.dumps(
        dict(archive=str(archive), sha256=digest, verified_manifest_entries=retained),
        indent=2,
    )
    + "\n"
)
