# Consistent file browsing

The browser provider owns identity-based selection and file information presentation.
Applications own navigation policy, validation, operations, and window composition.
Native path bytes are identities; display names must never identify operation targets.

`SelectionSession` exposes Normal, Visual and Mark modes, membership, counts, cursor,
anchor and commands. Pointer selection replaces, toggles, replaces a range, or adds a
range for click, Ctrl-click, Shift-click and Ctrl+Shift-click respectively. Modifier
selection enters V-MARK. Visual movement replaces a contiguous eligible range; Mark
movement leaves marks unchanged. Escape clears all marks. Directory navigation clears
the session. Filtering preserves hidden marks; reconciliation uses a successful,
settled underlying directory snapshot, never transient filtered rows. Missing anchors
end Visual range extension and retain surviving marks.

Files alone supports empty-space grid rectangles. Geometry uses content coordinates
and uniform cell pitch, independent of delegate creation; edge scrolling recomputes
intersections. Ctrl adds to the initial set. Item drags keep file-transfer semantics.

The browser FilePreview owns the square image area, DPR requests, fallback delay,
filename/type hierarchy and aligned optional EXIF tables. Holonight.Controls owns
metadata layout, byte-size formatting and a fixed-width mode badge. Viewer retains
its compact image-specific popup and selectable path using those generic controls.

Dependency order: install host-native holonight-qt, then holonight-file-browser into
an explicit development prefix; build Files and the portal against installed packages.
Viewer consumes the toolkit without acquiring browser selection state. Keep Core
independent of Qt Quick and optional services. Publication and umbrella pins are separate.

Local contracts:
- [Browser](../../holonight-file-browser/docs/sdd/consistent-browsing.md)
- [Files](../../holonight-files/docs/sdd/consistent-browsing.md)
- [Chooser](../../xdg-desktop-portal-holonight/docs/sdd/consistent-browsing.md)
- [Toolkit](../../holonight-qt/docs/consistent-browsing.md)
- [Viewer popup](../../holonight-viewer/docs/sdd/image-information-popup/DESIGN.md)

Files operation paths preserve undecodable bytes with private surrogate escapes. Only
lexical path operations use this representation; filesystem calls recover native bytes,
and progress text uses decoded display strings. Trash metadata percent-encodes raw bytes.

Verification starts with selection state and consumer controller regressions, then QML
lint and offscreen presentation. Shared interfaces require installed C++/QML consumers,
Core-only builds and relevant component/integration acceptance. Native pointer gestures,
resize parity and Viewer popup behavior require user-operated checks. Do not automate
native desktop focus or pointer interaction. Preserve historical SDDs and installer safeguards.

## Acceptance

The user confirmed that all requested native manual checks passed: pointer selection,
grid rectangles and scrolling, file-transfer gestures, chooser resizing and preview
parity, and Viewer information-popup behavior. The follow-up selection-highlight
notification fix and stable right-aligned footer count were also manually accepted.

Automated verification includes shared selection regressions, installed C++/QML
consumers, Core-only builds, provider container acceptance, Files controller and
presentation regressions, the chooser portable suite, and Viewer popup regressions.
Provider pins are advanced in dependency order when publishing this milestone.

The native publication gate completed successfully for both staged and relocated
prefixes, using host-built consumers and the real session manager, namespaces and
cgroups. Provider inspection, unknown-size codec checks, required Files/chooser
lanes, Files observation and rendered previews all passed.

Consumer container acceptance passed: Files completed all 24 CTest checks and the
portal all five, followed by formatting, static analysis, QML and licensing checks.
Unchanged provider build results were reused for incremental consumer reruns.
