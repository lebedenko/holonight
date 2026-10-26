# Application playback grouping integration

The [provider contract](../../holonight-system-services/docs/sdd/application-audio.md)
adds optional application identity metadata without changing existing stream roles or
controls. The [shell design](../../holonight-shell/docs/sdd/application-audio/DESIGN.md)
owns grouping, display and lifetime-scoped control inheritance.

Build holonight-system-services against host dependencies, stage it in a private prefix,
then configure holonight-shell against that installed package. Keep the provider and
consumer diffs independently reviewable. Publishing, deployment and umbrella pin updates
are separate from this implementation.

Verify focused provider audio tests and its audio install-consumer check, then shell
group-model and audio QML tests, qml-lint, qmltypes-check and the compositor smoke
checklist. Live acceptance: play mpv during a Teams call, then repeat with browser
playback; confirm distinct application rows and isolated grouped controls.
