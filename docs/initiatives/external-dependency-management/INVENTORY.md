# Dependency inventory

This is the accepted adoption inventory derived from canonical declarations. [CMAKE-AUDIT.json](CMAKE-AUDIT.json)
retains current compile/test/export discovery and options at the audited baselines, including download fallbacks
and optional discovery that adoption replaces. Internal providers remain governed by gitlinks and module.json.
Unconstrained libraries remain unconstrained; brackets identify the feature controlling a requirement.

| Repository | External build/tool requirements | Runtime profile | Additional verification |
|---|---|---|---|
| holonight-ai | Qt6 6.11 (Core, Gui, Quick, Qml, Network, Concurrent, Sql, DBus); libsecret-1; md4c; KF6SyntaxHighlighting; c++; cmake; ninja; pkg-config; git; python3 3.10 | fonts; mime | GTest 1.14; Qt6 6.11 (Test) |
| holonight-appearance-adapters | Qt6 6.11 (Core, Gui, Xml); gio-2.0; json-glib-1.0; KF6Config [BUILD_KCONFIG]; c++; cmake; ninja; pkg-config; git; python3 3.10 |  | gtk+-3.0 [BUILD_GTK_PROBES]; gtk4 [BUILD_GTK_PROBES]; xvfb-run; dbus-run-session; GTest 1.14; Qt6 6.11 (Test) |
| holonight-config | tomlplusplus; c++; cmake; ninja; pkg-config; git; python3 3.10 |  |  |
| holonight-files | Qt6 6.11 (Core); Qt6 6.11 (Gui, Quick, Qml, QuickControls2, Svg) [BUILD_FILES_APP]; tomlplusplus 3.4 [BUILD_FILES_APP]; QMarkdown 1.0...<2.0 [BUILD_FILES_APP]; c++; cmake; ninja; pkg-config; git; python3 3.10 | fonts; mime | libexif; GTest 1.14; Qt6 6.11 (Test); Qt6 6.11 (OpenGL) |
| holonight-greeter | Qt6 6.11 (Core, Gui, Quick, Qml, Network, DBus); LayerShellQt; tomlplusplus; c++; cmake; ninja; pkg-config; git; python3 3.10 | greetd; cage; fonts; mime | GTest 1.14; Qt6 6.11 (Test); Qt6 6.11 (QmlPrivate) |
| holonight-hyprlock | c++; cmake; ninja; pkg-config; git; python3 3.10 | hyprlock | GTest 1.14; Qt6 6.11 (Test) |
| holonight-icons | Python3 3.10 (Interpreter) | hicolor | Qt6 6.11 (Core, Gui, Svg); gtk+-3.0; gtk4; python-render; xvfb-run; KF6IconThemes [VERIFY_KDE] |
| holonight-images | Qt6 6.11 (Core, Gui, Svg); libexif; libwebp; c++; cmake; ninja; pkg-config; git; python3 3.10 | imageformats | GTest 1.14; Qt6 6.11 (Test) |
| holonight-pkg-manager | Qt6 6.11 (Core, Gui, Quick, Qml, Network, Sql, DBus, Concurrent); libalpm; ICU (uc); c++; cmake; ninja; pkg-config; git; python3 3.10 | fonts; mime | GTest 1.14; Qt6 6.11 (Test); Qt6 6.11 (QmlPrivate) |
| holonight-qt | Qt6 6.11 (Core, Gui, Widgets, Quick, QuickControls2, QuickShapes, Svg, GuiPrivate, QuickPrivate, QuickControls2Private, QuickTemplates2Private); Qt6WaylandScannerTools 6.11 [BUILD_WAYLAND]; wayland-client [BUILD_WAYLAND]; wayland-scanner [BUILD_WAYLAND]; KF6SyntaxHighlighting [BUILD_SYNTAX_THEMES]; c++; cmake; ninja; pkg-config; git; python3 3.10 | fonts; mime | patchelf; GTest 1.14; Qt6 6.11 (Test); Qt5 5.15 (Core, Gui, Test, Widgets) [BUILD_QT5_PROBES]; Qt6 6.11 (OpenGL) |
| holonight-search | Qt6 6.11 (Core); c++; cmake; ninja; pkg-config; git; python3 3.10 |  | fzf; GTest 1.14; Qt6 6.11 (Test) |
| holonight-settings | Qt6 6.11 (Core); Qt6 6.11 (Gui, Quick, Qml, DBus) [BUILD_APP]; c++; cmake; ninja; pkg-config; git; python3 3.10 | fonts; mime | GTest 1.14; Qt6 6.11 (Test) |
| holonight-shell | Qt6 6.11 (Core, Gui, Quick, Qml, DBus, Network, Concurrent, Sql, QuickControls2, WaylandClient, WaylandClientPrivate); Qt6WaylandScannerTools 6.11; wayland-client; wayland-protocols; wayland-scanner; tomlplusplus; libsecret-1; polkit-agent-1; polkit-qt6-agent-1>=0.200.0; polkit-qt6-core-1>=0.200.0; c++; cmake; ninja; pkg-config; git; python3 3.10 | udisks; fonts; mime | bwrap; sway; dbus-run-session; GTest 1.14; Qt6 6.11 (Test) |
| holonight-system-services | Qt6 6.11 (Core); Qt6 6.11 (Network) [BUILD_COMPOSITOR]; Qt6 6.11 (Gui, WaylandClient) [BUILD_COMPOSITOR_WAYLAND]; Qt6 6.11 (DBus) [BUILD_STORAGE]; libpulse [BUILD_AUDIO]; wayland-client [BUILD_COMPOSITOR_WAYLAND]; c++; cmake; ninja; pkg-config; git; python3 3.10 |  | GTest 1.14; Qt6 6.11 (Test) |
| holonight-thumbnails | Qt6 6.11 (Core, Gui); c++; cmake; ninja; pkg-config; git; python3 3.10 |  | GTest 1.14; Qt6 6.11 (Test) |
| holonight-viewer | Qt6 6.11 (Core, Gui, GuiPrivate, DBus, Quick, Qml, QuickControls2, Svg); Qt6WaylandScannerTools 6.11; wayland-client; wayland-protocols; wayland-scanner; c++; cmake; ninja; pkg-config; git; python3 3.10 | fonts; mime | dbus-run-session; xvfb-run; python-render; GTest 1.14; Qt6 6.11 (Test) |
| holonightd | SQLite3; nlohmann_json; tomlplusplus 3.4; libsystemd [BUILD_SYSTEMD]; c++; cmake; ninja; pkg-config; git; python3 3.10 |  | GTest 1.14 |
| xdg-desktop-portal-holonight | Qt6 6.11 (Core, Gui, GuiPrivate, Quick, Qml, QuickControls2, DBus, Concurrent); wayland-client; wayland-scanner; wayland-protocols; c++; cmake; ninja; pkg-config; git; python3 3.10 | fonts; mime | dbus-run-session; Qt6 6.11 (Test) |

Historical supplemental packages and their classification remain in CI-PACKAGE-AUDIT.json.
