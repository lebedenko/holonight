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

Debian release coverage remains required. The current `debian:trixie` release lane does not satisfy Qt >= 6.11 merely
by installing the distribution's Qt development packages. A pinned Debian environment needs a separately prepared,
package-managed Qt >= 6.11 installation, matching private modules and all release acceptance dependencies before
qualification. No Debian Qt artifact has been supplied or qualified in this work package; the existing release lane
is preserved until that handoff is available. The locally cached Debian base digest was audited as
`debian@sha256:d07d1b51c39f51188e60be9b64e6bf769fa94e187f092bc32b91305cfa34ba5a`.

Status and evidence belong to the initiative ledger. A recipe, a local image ID, or an older passing CI run does not
establish qualification of a newly built environment.
