# Keyboard layout reporting

Build and stage [system services](../../holonight-system-services/docs/sdd/sway-input-observer/README.md)
first, then build [the shell](../../holonight-shell/docs/sdd/keyboard-layout-reporting/README.md)
against the installed Compositor component. The provider exports an observed
Sway layout name, and the shell owns the short code, top bar, and OSD.

Run the Compositor install-tree consumer and focused compositor tests, then
verify the shell's installed labwc, Sway, and generic Wayland plugin factories.
Exercise layout switches in compositor sessions and check the top bar and OSD.
