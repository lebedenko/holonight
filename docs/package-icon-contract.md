# Package icon delivery contract

Packages owns candidate ordering, workers, the GUI cache and PNG data URL publication.
Images owns synchronous bounded raster and SVG decoding on caller-owned devices.
The installed public API stays unchanged. See
[Packages design](../holonight-pkg-manager/docs/sdd/package-icon-coverage/SPEC.md).

The Arch installation profile and acceptance image require archlinux-appstream-data
and kimageformats. Dependency checks remain read-only; incomplete installations
retain tile fallback. Rebuild and publish the acceptance image before updating its pin.
Packages builds the published Images revision into its disposable provider prefix.
Publish provider changes before consumer pins requiring those changes; no publication
is authorized by this implementation task.

Verify Images CTest and installed-package decoding, then Packages resolver regressions,
model/QML acceptance and staged JPEG XL decoding. Use identical package/catalog
snapshots for before/after resolver-success counts; never equate metadata candidates
with decoded images. Production inspection is read-only with isolated HOME/XDG.
