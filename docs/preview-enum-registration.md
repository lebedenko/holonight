# Preview enum registration contract

The [provider contract](../holonight-file-browser/docs/preview-enum-registration.md)
and [Files migration](../holonight-files/docs/preview-enum-registration.md) require
scoped-only PreviewService QML enums. C++ names, values and properties stay stable;
flattened QML aliases are intentionally removed. Files preserves QML_FOREIGN.

Build and install holonight-file-browser into an isolated prefix first, then build
Files with that CMAKE_PREFIX_PATH and matching QML and runtime library paths.
Publish the provider before dependent Files changes when publication is authorized.
This change does not authorize publication, system installation or umbrella pin updates.

Integration acceptance: establish failure of files-preview-scoped-enums before the
provider fix, then pass it in a fresh process against the updated installation.
Run Files preview sidebar, Quick Look error, eligibility and consumer-size regressions;
provider preview and installed Preview/PreviewQuick consumers; Core-only acceptance;
QML lint, generated metadata and formatting checks. Finish with both component
`task check` gates and isolated installed-runtime acceptance using current sibling
sources. Confirm no enum-clash or undefined-enum diagnostics. Native preview and
Quick Look interaction checks are manual; never automate native input or focus.
