# Child-only directory listings

The [provider contract](../holonight-file-browser/README.md) now exposes actual children
only. Empty folders have zero rows. Parent metadata, synthetic rows, the parent flag,
and its model/QML role are removed outright. Remaining role numbers and real-entry
identities retain their values and native path bytes.

Build and install the native provider into a development prefix first, then rebuild
Files, the portal chooser and Viewer against that installed package. Files retains
creation placeholders, history, cursor restoration and parent commands. Portal Open,
Save and folder modes retain toolbar and keyboard navigation. Viewer consumes only
actual image children. Enumeration skips and filename rejection for `.` and `..` remain.

Verify provider load/refresh/root/symlink absence, sorting, hidden and native paths,
async and failed refreshes; Files navigation/history/editing/operations/previews;
portal modes and Viewer browsing. Installed Core/Quick/QML consumers, Core-only builds,
and affected-component acceptance cover the coordinated interface removal. Native
interaction checks remain manual. Historical SDDs describe the earlier contract and
are preserved. Consumer dependency manifests and umbrella pins advance together after
publishing the provider and consumers. System installation remains a separate action.
