# QMarkdown 1.18 chat migration

Chat's [local SDD](../../holonight-ai/docs/sdd/qmarkdown-migration/SPEC.md) owns
presentation and consumer acceptance. QMarkdown stays package-owned, outside the
umbrella installer manifest; native builds and installation never fetch or build it.

## Dependency contract and publication order

1. Package QMarkdown 1.18.0 release commit
   `b22d5196fa5ee94ce6f36dada45bc61c9fa6106d` through
   `packaging/qmarkdown/PKGBUILD`, with `QMARKDOWN_WITH_KSYNTAXHIGHLIGHTING=ON`.
2. Rebuild the shared dependency image with `packaging/ci/Dockerfile.arch`. Verify
   the installed package version and `MarkdownView.syntaxHighlightingAvailable`.
3. Publish the verified shared image and resolve its immutable registry digest.
4. Update coordinated `scripts/ci/image.txt` pins only after publication; the old
   pinned image contains QMarkdown 1.1.0 and cannot qualify this consumer.
5. Run chat container acceptance and installation/runtime integration, then publish
   consumers referencing the available package/image milestone.

Chat requires `find_package(QMarkdown 1.18 CONFIG REQUIRED)`, links
`QMarkdown::QMarkdown`, and imports `QMarkdown 1.18`. Its build engines and lint use
`QMarkdown_QML_IMPORT_PATH` independently of HolonightQt. Installed execution keeps
relative/system imports; separate custom prefixes need environment configuration.

## Integration checks

Qualify Files and other QMarkdown consumers against the rebuilt image. Chat tests
must instantiate real Markdown user and assistant rows in workspace and quick-panel
hosts, require highlighting availability, and exercise GFM, streaming flush, selection,
clipboard payloads, resizing, theme bindings, and scroll anchoring. Run chat's
`task check` and `task check:integration`; installed launches must load package-owned
QML plugins without build-directory imports. Preserve package ownership and installer
collision/uninstall protections. No persistence or provider protocol migration occurs.
