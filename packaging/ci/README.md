# Shared development and acceptance image

Every component and the umbrella pins the same image in `scripts/ci/image.txt`.
The current digest is the existing full Arch environment, dated 2026/09/30, including
Clang 22, Qt 6.11, REUSE, testing tools and the separately packaged QMarkdown provider.
Native builds can use newer installed tools; container acceptance defines the gate.

Build the next image from the umbrella root:

```sh
docker build -f packaging/ci/Dockerfile.arch -t holonight-development .
```

There is one package list, `arch.packages`, one dated Arch archive and one Dockerfile.
QMarkdown is built by the existing `packaging/qmarkdown/PKGBUILD` and installed with
pacman. It stays outside umbrella installer ownership. Runtime acceptance starts fresh
containers from the same image and copies only staged payloads into them.

Refresh the archive date and base digest deliberately. Verify the new image, publish
when authorized, resolve its registry digest, then update every `scripts/ci/image.txt`
together. Never replace pins with mutable tags or invent a digest for an unpublished image.
Logs print the exact image, compiler, Qt and tool versions for local and GitHub checks.
The existing digest remains in use until a replacement is built and verified.

`task check` automatically acquires the image and pinned provider sources, then runs
without networking. Docker, Python 3, Git and tar are the host launcher prerequisites.
No separate preparation command or binary cache is required.
