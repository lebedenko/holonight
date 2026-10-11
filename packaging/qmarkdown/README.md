# QMarkdown system package

The Arch recipe pins the accepted QMarkdown revision
`595ca4fea32155766c2eafb3b670995d2ea75a2f` (1.0.0). Build it explicitly with `makepkg`, then install the resulting
package with `pacman -U`. Source acquisition belongs to this package preparation operation. HoloNight CMake,
Task configuration/build commands and the umbrella installer never acquire it.

Build against the same installed Qt/toolchain used by Files. The package owns the shared `libQMarkdown.so.1`,
QML plugin, public/private QML metadata, CMake exports and QMarkdown/cmark license notices. The umbrella installer
requires the installed package and never adds those paths to its ownership manifest.

For development, set `HOLONIGHT_EXTERNAL_PREFIX` to an explicit installed prefix. `QMARKDOWN_SOURCE` remains an
explicit local preparation override in the Files adoption work package. Neither override deploys unmanaged runtime
libraries through the umbrella system installer.

The recipe is source-pinned; package build and Files startup qualification must be recorded before deployment.

The recipe disables Arch's optional LTO to match the upstream Release build configuration. GCC 16 LTO emitted a
string-buffer warning in the pinned cmark bundle during package qualification. Standard Release compilation and
installed QML rendering are checked separately; no warning-suppression flags are added. Upstream install rules
include both the QMarkdown license and the cmark license/provenance notices.
