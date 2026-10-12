# Dependency environment preparation

Image preparation is the only networked package-acquisition phase. The Arch recipe pins the existing accepted base
and the completed `2026/09/30` archive. Pacman performs normal dependency resolution; no supplemental archives are
extracted into `/` and no prefixes are overlaid. `daemon` is a separate Qt-free target. The `full` target retains all
direct acceptance tools and installs the pinned QMarkdown package through pacman; the historical supplement inventory is retained in the initiative audit, with transitive
entries resolved by the package manager instead of installed by archive extraction.

Build from the umbrella root:

```sh
docker build --target daemon -f packaging/ci/Dockerfile.arch -t holonight-deps-daemon .
docker build --target full -f packaging/ci/Dockerfile.arch -t holonight-deps-full .
```

Qualify both images, retain `pacman -Q`, compiler/Qt identities and offline prerequisite/test evidence, publish only
when authorized, and record the immutable digests. For a separately qualified full base, the standalone QMarkdown package image recipe is
`Dockerfile.qmarkdown`, supplying the qualified full image **digest** as `BASE_IMAGE`. That explicit preparation
builds the pinned system package and installs it with pacman. Build/runtime acceptance uses the same qualified
image revision and runs without network access after explicit source-provider preparation.

Do not replace repository `images.json`, release containers or runtime rehearsals with unqualified recipes. The
adoption work packages must switch these together after image qualification. Keep standalone source-provider pins;
umbrella integration continues to use its exact gitlinks.

Pre-release CI prioritizes the qualified Arch full and daemon environments. Debian qualification is deferred
(EDM-023 is Superseded); Debian package mappings and portable discovery remain available without a qualified
support claim. Shell’s release build gate migration belongs to EDM-012 and must preserve tests, linting and
quality checks. No application workflow changes are part of EDM-024.

Publication is manual to `ghcr.io/lebedenko/holonight-deps`, using `arch-full-<commit>` and
`arch-daemon-<commit>` tags. Qualify locally before pushing the exact image IDs, resolve registry digests,
then pull each digest and compare its image ID with the qualified identity. Consumers use digest references.
No hosted image-building workflow or distro matrix is introduced. Docker contexts admit only the recipe,
its ignore rules, package lists and PKGBUILD; local source trees, builds and package artifacts are excluded.

Status and evidence belong to the initiative ledger. A recipe, a local image ID, or an older passing CI run does not
establish qualification of a newly built environment.

The current EDM-024 published digest references, qualified image IDs, package inventories and exact next
implementation baselines are recorded in [initiative verification](../../docs/initiatives/external-dependency-management/VERIFICATION.md)
and the [coordination ledger](../../docs/initiatives/external-dependency-management/TASKS.md).
