# Files enum and drag-event compatibility

The [provider note](../holonight-file-browser/docs/qt-enum-compatibility.md) and
[Files note](../holonight-files/docs/qt-enum-compatibility.md) describe Qt-recognized
8-bit enum types and version-adapted drag-test coordinates. Preserve public names,
enum values, width, signedness, scoped registration, QML_FOREIGN wrappers, package
identities, Qt 6.11 support and application behavior.

Build and stage File Browser first in an isolated prefix, then configure Files
with matching CMAKE_PREFIX_PATH, QML_IMPORT_PATH and runtime library paths.
If publication is later authorized, publish the provider first. This work does
not authorize publication, system installation or umbrella pin updates.

Regenerate QML registration for all five affected Files executables and record
before/after diagnostics with the same toolchain, even if enum warnings do not
reproduce. Reject std::uint8_t/std::int8_t bases in generated application metadata.
Run scoped-enum, drag, sidebar, places, devices, task-manager, Vim-mode and Quick
Look regressions plus metadata and QML lint. Run provider preview/storage checks,
installed Storage/Preview/PreviewQuick consumers and Core-only acceptance.
Use separate Qt 6.11 and 6.12 build directories and report unavailable toolchains.
Finish both component task check gates and isolated Files runtime acceptance using
updated sibling sources. Native interaction checks remain manual.
