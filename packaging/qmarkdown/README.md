# QMarkdown system package

The Arch recipe pins QMarkdown 1.18.0 release commit
`b22d5196fa5ee94ce6f36dada45bc61c9fa6106d` and enables
`QMARKDOWN_WITH_KSYNTAXHIGHLIGHTING=ON`. The package owns its library, QML plugin,
metadata, bundled parser notices, and CMake exports. Native consumers and the
umbrella installer require the installed package and never acquire or deploy it.

Build explicitly with `makepkg` and install with `pacman -U`, using the same Qt
and toolchain as consumers. The recipe disables optional Arch LTO to use upstream
Release compilation. QMarkdown's syntax-highlighting backend is a package dependency.

A separate installed prefix can be selected using `CMAKE_PREFIX_PATH`. Installed
launches using a custom prefix need its QML root in `QML_IMPORT_PATH` and its shared
libraries on the platform library search path.

See [chat migration contract](../../docs/initiatives/qmarkdown-chat-migration.md)
for shared-image publication order and integration requirements.
