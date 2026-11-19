# Native clang-tidy source cleanup

This coordinated cleanup fixes source diagnostics exposed after the
[analysis flag translation](clang-tidy-compatibility.md). Each component owns its
source changes and keeps its native build and installed-package tests. Hyprlock
has no C/C++ analysis target. No publication or umbrella pin update is included.

Mechanical changes add braces, explicit initialization, casts, nodiscard
annotations and multiline trailing commas. Clang 23's single-line comma fix can
remove required separators after empty brace expressions; affected components use
the same single-line policy already established in the application repositories.
The multiline check and warnings-as-errors remain enabled. GTest fixture state
retains its protected visibility for generated test subclasses.

Behavior-preserving helper extraction reduces complexity in appearance-adapter
transactions, Qt navigation and Bluetooth coordination. Transaction ordering,
rollback, discovery ownership and asynchronous generation checks remain intact.
Published enum representations, Qt role constants and D-Bus member spellings must
remain compatible; any check exception is local and explains that contract.

Verification starts with each affected native compilation unit and existing
component tests, then the normal tidy entrypoint. Native test buses disable host
service activation; Shell uses its existing isolated test launcher. Provider
checks retain installed consumer tests. Consumers use a private native package
prefix when existing development prefixes contain stale headers. No source-tree
provider substitution or system installation is used. Routine logs remain under
`build/tidy-cleanup/`.
