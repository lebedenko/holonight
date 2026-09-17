from pathlib import Path
import re
import subprocess

root = Path.cwd()
docs = root / "docs/initiatives/unified-qtquick-controls"
names = (
    "P03-RECHECK.md",
    "P03-READINESS.md",
    "p03-kit/README.md",
    "FINAL-ACCEPTANCE.md",
    "TASKS.md",
)
for name in names:
    p = docs / name
    for target in re.findall(r"\]\(([^)]+)\)", p.read_text()):
        if "://" in target or target.startswith("/"):
            continue
        path, _, anchor = target.partition("#")
        q = (p.parent / path).resolve() if path else p
        assert q.exists(), (name, target)
        if anchor:
            headings = re.findall(r"^#+ (.+)$", q.read_text(), re.M)
            slugs = [
                re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings
            ]
            assert anchor in slugs, (name, target)
    for code in re.findall(r"```sh\n(.*?)```", p.read_text(), re.S):
        r = subprocess.run(["bash", "-n"], input=code, text=True, capture_output=True)
        assert r.returncode == 0, (name, r.stderr)
subprocess.run(["git", "diff", "--check"], check=True)
print("Links, anchors, handoff shell syntax and diff check pass")
