#!/usr/bin/env python3
"""Restore a saved rendering kit to its original /tmp prefix without overwriting files."""
import argparse
import hashlib
from pathlib import Path
import re
import tarfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    name = args.archive.name.removesuffix(".tar.gz")
    if not re.fullmatch(r"holonight-uqc(?:201-(?:final|p03|settings)|20[78]|21[126])-[a-z0-9_]+", name):
        parser.error("expected a saved holonight-uqc201-final/p03/settings/207/208/211/212/216-*.tar.gz kit")
    kit = Path("/tmp") / name
    if kit.exists():
        parser.error(f"preserving existing {kit}; restoration requires that path to be absent")
    with tarfile.open(args.archive, "r:gz") as saved:
        members = saved.getmembers()
        if any(Path(item.name).parts[0] != name for item in members):
            parser.error("archive contains files outside the expected kit directory")
        ready = saved.extractfile(name + "/READY")
        if ready is None:
            parser.error("archive has no READY marker")
        ready_text = ready.read()
        saved.extractall("/tmp", members=[item for item in members if item.name != name + "/READY"], filter="data")
    for line in (kit / "SHA256SUMS").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        path = kit / relative
        if not path.resolve().is_relative_to(kit) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Checksum failed: {relative}; do not launch this kit")
    (kit / "READY").write_bytes(ready_text)
    print(f"Restored and checksums verified: {kit}")
    compositor = "sway" if name.startswith(("holonight-uqc201-settings-", "holonight-uqc201-p03-", "holonight-uqc212-", "holonight-uqc216-")) else "hyprland"
    print(f"From a fresh tux VT login: python3 {kit}/guided-session.py {compositor}")


if __name__ == "__main__":
    main()
