cmake_minimum_required(VERSION 3.25)
project(HoloNightExternalDependencies LANGUAGES C CXX)
find_package(PkgConfig REQUIRED)
# holonight-ai: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Quick Qml Network Concurrent Sql DBus)
# holonight-ai: secret
pkg_check_modules(External_1_holonight_ai REQUIRED libsecret-1)
# holonight-ai: md4c
pkg_check_modules(External_2_holonight_ai REQUIRED md4c)
# holonight-ai: syntax
find_package(KF6SyntaxHighlighting REQUIRED)
# holonight-ai: compiler
# holonight-ai: cmake
# holonight-ai: ninja
# holonight-ai: pkgconf
# holonight-ai: git
# holonight-ai: python
# holonight-ai: fonts
# holonight-ai: mime
# holonight-appearance-adapters: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Xml)
# holonight-appearance-adapters: gio
pkg_check_modules(External_1_holonight_appearance_adapters REQUIRED gio-2.0)
# holonight-appearance-adapters: json-glib
pkg_check_modules(External_2_holonight_appearance_adapters REQUIRED json-glib-1.0)
# holonight-appearance-adapters: kconfig
find_package(KF6Config REQUIRED)
if(NOT TARGET KF6::ConfigCore)
  message(FATAL_ERROR "holonight-appearance-adapters: installed KF6Config lacks KF6::ConfigCore")
endif()
if(NOT TARGET KF6::ConfigGui)
  message(FATAL_ERROR "holonight-appearance-adapters: installed KF6Config lacks KF6::ConfigGui")
endif()
# holonight-appearance-adapters: compiler
# holonight-appearance-adapters: cmake
# holonight-appearance-adapters: ninja
# holonight-appearance-adapters: pkgconf
# holonight-appearance-adapters: git
# holonight-appearance-adapters: python
# holonight-config: toml
pkg_check_modules(External_0_holonight_config REQUIRED tomlplusplus)
# holonight-config: compiler
# holonight-config: cmake
# holonight-config: ninja
# holonight-config: pkgconf
# holonight-config: git
# holonight-config: python
# holonight-files: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core)
# holonight-files: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Gui Quick Qml QuickControls2 Svg)
# holonight-files: toml
find_package(tomlplusplus 3.4 CONFIG REQUIRED)
# holonight-files: qmarkdown
find_package(QMarkdown 1.0...<2.0 CONFIG REQUIRED)
if(NOT TARGET QMarkdown::QMarkdown)
  message(FATAL_ERROR "holonight-files: installed QMarkdown lacks QMarkdown::QMarkdown")
endif()
get_target_property(_qmarkdown_type QMarkdown::QMarkdown TYPE)
if(NOT _qmarkdown_type STREQUAL "SHARED_LIBRARY")
  message(FATAL_ERROR "Files requires installed shared QMarkdown 1.x")
endif()
foreach(_metadata qmldir QMarkdown.qmltypes)
  if(NOT EXISTS "${QMarkdown_QML_IMPORT_PATH}/QMarkdown/${_metadata}")
    message(FATAL_ERROR "Installed QMarkdown is missing QML metadata: ${_metadata}")
  endif()
endforeach()
# holonight-files: compiler
# holonight-files: cmake
# holonight-files: ninja
# holonight-files: pkgconf
# holonight-files: git
# holonight-files: python
# holonight-files: fonts
# holonight-files: mime
# holonight-files: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Gui Quick Qml QuickControls2)
# holonight-greeter: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Quick Qml Network DBus)
# holonight-greeter: layer-shell
find_package(LayerShellQt REQUIRED)
# holonight-greeter: toml
find_package(tomlplusplus CONFIG REQUIRED)
# holonight-greeter: greetd
# holonight-greeter: cage
# holonight-greeter: compiler
# holonight-greeter: cmake
# holonight-greeter: ninja
# holonight-greeter: pkgconf
# holonight-greeter: git
# holonight-greeter: python
# holonight-greeter: fonts
# holonight-greeter: mime
# holonight-hyprlock: hyprlock
# holonight-hyprlock: compiler
# holonight-hyprlock: cmake
# holonight-hyprlock: ninja
# holonight-hyprlock: pkgconf
# holonight-hyprlock: git
# holonight-hyprlock: python
# holonight-icons: python
find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
# holonight-icons: hicolor
# holonight-images: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Svg)
# holonight-images: exif
pkg_check_modules(External_1_holonight_images REQUIRED libexif)
# holonight-images: webp
pkg_check_modules(External_2_holonight_images REQUIRED libwebp)
# holonight-images: imageformats
# holonight-images: compiler
# holonight-images: cmake
# holonight-images: ninja
# holonight-images: pkgconf
# holonight-images: git
# holonight-images: python
# holonight-pkg-manager: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Quick Qml Network Sql DBus Concurrent)
# holonight-pkg-manager: alpm
pkg_check_modules(External_1_holonight_pkg_manager REQUIRED libalpm)
# holonight-pkg-manager: icu
find_package(ICU REQUIRED COMPONENTS uc)
# holonight-pkg-manager: compiler
# holonight-pkg-manager: cmake
# holonight-pkg-manager: ninja
# holonight-pkg-manager: pkgconf
# holonight-pkg-manager: git
# holonight-pkg-manager: python
# holonight-pkg-manager: fonts
# holonight-pkg-manager: mime
# holonight-qt: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Widgets Qml Quick QuickControls2 QuickShapes Svg)
# holonight-qt: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS WaylandClient)
# holonight-qt: qt-wayland
find_package(Qt6WaylandScannerTools 6.11 REQUIRED)
# holonight-qt: wayland
pkg_check_modules(External_3_holonight_qt REQUIRED wayland-client)
# holonight-qt: wayland-scanner
pkg_check_modules(External_4_holonight_qt REQUIRED wayland-scanner)
# holonight-qt: syntax
find_package(KF6SyntaxHighlighting REQUIRED)
# holonight-qt: compiler
# holonight-qt: cmake
# holonight-qt: ninja
# holonight-qt: pkgconf
# holonight-qt: git
# holonight-qt: python
# holonight-qt: fonts
# holonight-qt: mime
# holonight-search: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core)
# holonight-search: compiler
# holonight-search: cmake
# holonight-search: ninja
# holonight-search: pkgconf
# holonight-search: git
# holonight-search: python
# holonight-settings: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core)
# holonight-settings: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Gui Quick Qml DBus)
# holonight-settings: compiler
# holonight-settings: cmake
# holonight-settings: ninja
# holonight-settings: pkgconf
# holonight-settings: git
# holonight-settings: python
# holonight-settings: fonts
# holonight-settings: mime
# holonight-shell: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Quick Qml DBus Network Concurrent Sql QuickControls2 WaylandClient)
# holonight-shell: qt-wayland
find_package(Qt6WaylandScannerTools 6.11 REQUIRED)
# holonight-shell: wayland
pkg_check_modules(External_2_holonight_shell REQUIRED wayland-client)
# holonight-shell: wayland-protocols
pkg_check_modules(External_3_holonight_shell REQUIRED wayland-protocols)
# holonight-shell: wayland-scanner
pkg_check_modules(External_4_holonight_shell REQUIRED wayland-scanner)
# holonight-shell: toml
pkg_check_modules(External_5_holonight_shell REQUIRED tomlplusplus)
# holonight-shell: secret
pkg_check_modules(External_6_holonight_shell REQUIRED libsecret-1)
# holonight-shell: polkit
pkg_check_modules(External_7_holonight_shell REQUIRED polkit-agent-1)
# holonight-shell: polkit-qt-agent
pkg_check_modules(External_8_holonight_shell REQUIRED polkit-qt6-agent-1>=0.200.0)
# holonight-shell: polkit-qt-core
pkg_check_modules(External_9_holonight_shell REQUIRED polkit-qt6-core-1>=0.200.0)
# holonight-shell: udisks
# holonight-shell: compiler
# holonight-shell: cmake
# holonight-shell: ninja
# holonight-shell: pkgconf
# holonight-shell: git
# holonight-shell: python
# holonight-shell: fonts
# holonight-shell: mime
# holonight-system-services: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core)
# holonight-system-services: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Network)
# holonight-system-services: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Gui WaylandClient)
# holonight-system-services: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS DBus)
# holonight-system-services: pulse
pkg_check_modules(External_4_holonight_system_services REQUIRED libpulse)
# holonight-system-services: wayland
pkg_check_modules(External_5_holonight_system_services REQUIRED wayland-client)
# holonight-system-services: compiler
# holonight-system-services: cmake
# holonight-system-services: ninja
# holonight-system-services: pkgconf
# holonight-system-services: git
# holonight-system-services: python
# holonight-thumbnails: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui)
# holonight-thumbnails: compiler
# holonight-thumbnails: cmake
# holonight-thumbnails: ninja
# holonight-thumbnails: pkgconf
# holonight-thumbnails: git
# holonight-thumbnails: python
# holonight-viewer: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui DBus Quick Qml QuickControls2 Svg)
# holonight-viewer: qt-wayland
find_package(Qt6WaylandScannerTools 6.11 REQUIRED)
# holonight-viewer: wayland
pkg_check_modules(External_2_holonight_viewer REQUIRED wayland-client)
# holonight-viewer: wayland-protocols
pkg_check_modules(External_3_holonight_viewer REQUIRED wayland-protocols)
# holonight-viewer: wayland-scanner
pkg_check_modules(External_4_holonight_viewer REQUIRED wayland-scanner)
# holonight-viewer: compiler
# holonight-viewer: cmake
# holonight-viewer: ninja
# holonight-viewer: pkgconf
# holonight-viewer: git
# holonight-viewer: python
# holonight-viewer: fonts
# holonight-viewer: mime
# holonightd: sqlite
find_package(SQLite3 REQUIRED)
# holonightd: json
find_package(nlohmann_json CONFIG REQUIRED)
# holonightd: toml
find_package(tomlplusplus 3.4 CONFIG REQUIRED)
# holonightd: systemd
pkg_check_modules(External_3_holonightd REQUIRED libsystemd)
# holonightd: compiler
# holonightd: cmake
# holonightd: ninja
# holonightd: pkgconf
# holonightd: git
# holonightd: python
# xdg-desktop-portal-holonight: qt
find_package(Qt6 6.11 REQUIRED COMPONENTS Core Gui Quick Qml QuickControls2 DBus Concurrent)
# xdg-desktop-portal-holonight: wayland
pkg_check_modules(External_1_xdg_desktop_portal_holonight REQUIRED wayland-client)
# xdg-desktop-portal-holonight: wayland-scanner
pkg_check_modules(External_2_xdg_desktop_portal_holonight REQUIRED wayland-scanner)
# xdg-desktop-portal-holonight: compiler
# xdg-desktop-portal-holonight: cmake
# xdg-desktop-portal-holonight: ninja
# xdg-desktop-portal-holonight: pkgconf
# xdg-desktop-portal-holonight: git
# xdg-desktop-portal-holonight: python
# xdg-desktop-portal-holonight: fonts
# xdg-desktop-portal-holonight: mime
# xdg-desktop-portal-holonight: wayland-protocols
pkg_check_modules(External_11_xdg_desktop_portal_holonight REQUIRED wayland-protocols)
find_package(Qt6 ${Qt6_VERSION} EXACT REQUIRED COMPONENTS GuiPrivate QuickControls2Private QuickPrivate QuickTemplates2Private WaylandClientPrivate)
foreach(_variable IN ITEMS CMAKE_CXX_COMPILER CMAKE_CXX_COMPILER_ID CMAKE_CXX_COMPILER_VERSION CMAKE_C_COMPILER CMAKE_C_COMPILER_ID CMAKE_C_COMPILER_VERSION External_0_holonight_config_INCLUDE_DIRS External_0_holonight_config_LIBRARY_DIRS External_0_holonight_config_PREFIX External_0_holonight_config_VERSION External_11_xdg_desktop_portal_holonight_INCLUDE_DIRS External_11_xdg_desktop_portal_holonight_LIBRARY_DIRS External_11_xdg_desktop_portal_holonight_PREFIX External_11_xdg_desktop_portal_holonight_VERSION External_1_holonight_ai_INCLUDE_DIRS External_1_holonight_ai_LIBRARY_DIRS External_1_holonight_ai_PREFIX External_1_holonight_ai_VERSION External_1_holonight_appearance_adapters_INCLUDE_DIRS External_1_holonight_appearance_adapters_LIBRARY_DIRS External_1_holonight_appearance_adapters_PREFIX External_1_holonight_appearance_adapters_VERSION External_1_holonight_images_INCLUDE_DIRS External_1_holonight_images_LIBRARY_DIRS External_1_holonight_images_PREFIX External_1_holonight_images_VERSION External_1_holonight_pkg_manager_INCLUDE_DIRS External_1_holonight_pkg_manager_LIBRARY_DIRS External_1_holonight_pkg_manager_PREFIX External_1_holonight_pkg_manager_VERSION External_1_xdg_desktop_portal_holonight_INCLUDE_DIRS External_1_xdg_desktop_portal_holonight_LIBRARY_DIRS External_1_xdg_desktop_portal_holonight_PREFIX External_1_xdg_desktop_portal_holonight_VERSION External_2_holonight_ai_INCLUDE_DIRS External_2_holonight_ai_LIBRARY_DIRS External_2_holonight_ai_PREFIX External_2_holonight_ai_VERSION External_2_holonight_appearance_adapters_INCLUDE_DIRS External_2_holonight_appearance_adapters_LIBRARY_DIRS External_2_holonight_appearance_adapters_PREFIX External_2_holonight_appearance_adapters_VERSION External_2_holonight_images_INCLUDE_DIRS External_2_holonight_images_LIBRARY_DIRS External_2_holonight_images_PREFIX External_2_holonight_images_VERSION External_2_holonight_shell_INCLUDE_DIRS External_2_holonight_shell_LIBRARY_DIRS External_2_holonight_shell_PREFIX External_2_holonight_shell_VERSION External_2_holonight_viewer_INCLUDE_DIRS External_2_holonight_viewer_LIBRARY_DIRS External_2_holonight_viewer_PREFIX External_2_holonight_viewer_VERSION External_2_xdg_desktop_portal_holonight_INCLUDE_DIRS External_2_xdg_desktop_portal_holonight_LIBRARY_DIRS External_2_xdg_desktop_portal_holonight_PREFIX External_2_xdg_desktop_portal_holonight_VERSION External_3_holonight_qt_INCLUDE_DIRS External_3_holonight_qt_LIBRARY_DIRS External_3_holonight_qt_PREFIX External_3_holonight_qt_VERSION External_3_holonight_shell_INCLUDE_DIRS External_3_holonight_shell_LIBRARY_DIRS External_3_holonight_shell_PREFIX External_3_holonight_shell_VERSION External_3_holonight_viewer_INCLUDE_DIRS External_3_holonight_viewer_LIBRARY_DIRS External_3_holonight_viewer_PREFIX External_3_holonight_viewer_VERSION External_3_holonightd_INCLUDE_DIRS External_3_holonightd_LIBRARY_DIRS External_3_holonightd_PREFIX External_3_holonightd_VERSION External_4_holonight_qt_INCLUDE_DIRS External_4_holonight_qt_LIBRARY_DIRS External_4_holonight_qt_PREFIX External_4_holonight_qt_VERSION External_4_holonight_shell_INCLUDE_DIRS External_4_holonight_shell_LIBRARY_DIRS External_4_holonight_shell_PREFIX External_4_holonight_shell_VERSION External_4_holonight_system_services_INCLUDE_DIRS External_4_holonight_system_services_LIBRARY_DIRS External_4_holonight_system_services_PREFIX External_4_holonight_system_services_VERSION External_4_holonight_viewer_INCLUDE_DIRS External_4_holonight_viewer_LIBRARY_DIRS External_4_holonight_viewer_PREFIX External_4_holonight_viewer_VERSION External_5_holonight_shell_INCLUDE_DIRS External_5_holonight_shell_LIBRARY_DIRS External_5_holonight_shell_PREFIX External_5_holonight_shell_VERSION External_5_holonight_system_services_INCLUDE_DIRS External_5_holonight_system_services_LIBRARY_DIRS External_5_holonight_system_services_PREFIX External_5_holonight_system_services_VERSION External_6_holonight_shell_INCLUDE_DIRS External_6_holonight_shell_LIBRARY_DIRS External_6_holonight_shell_PREFIX External_6_holonight_shell_VERSION External_7_holonight_shell_INCLUDE_DIRS External_7_holonight_shell_LIBRARY_DIRS External_7_holonight_shell_PREFIX External_7_holonight_shell_VERSION External_8_holonight_shell_INCLUDE_DIRS External_8_holonight_shell_LIBRARY_DIRS External_8_holonight_shell_PREFIX External_8_holonight_shell_VERSION External_9_holonight_shell_INCLUDE_DIRS External_9_holonight_shell_LIBRARY_DIRS External_9_holonight_shell_PREFIX External_9_holonight_shell_VERSION ICU_DIR ICU_VERSION ICU_VERSION_STRING ICUuc_DIR ICUuc_VERSION KF6Config_DIR KF6Config_VERSION KF6Config_VERSION_STRING KF6SyntaxHighlighting_DIR KF6SyntaxHighlighting_VERSION KF6SyntaxHighlighting_VERSION_STRING LayerShellQt_DIR LayerShellQt_VERSION LayerShellQt_VERSION_STRING Python3Interpreter_DIR Python3Interpreter_VERSION Python3_DIR Python3_VERSION Python3_VERSION_STRING QMarkdown_DIR QMarkdown_VERSION QMarkdown_VERSION_STRING Qt6Concurrent_DIR Qt6Concurrent_VERSION Qt6Core_DIR Qt6Core_VERSION Qt6DBus_DIR Qt6DBus_VERSION Qt6GuiPrivate_DIR Qt6GuiPrivate_VERSION Qt6Gui_DIR Qt6Gui_VERSION Qt6Network_DIR Qt6Network_VERSION Qt6Qml_DIR Qt6Qml_VERSION Qt6QuickControls2Private_DIR Qt6QuickControls2Private_VERSION Qt6QuickControls2_DIR Qt6QuickControls2_VERSION Qt6QuickPrivate_DIR Qt6QuickPrivate_VERSION Qt6QuickShapes_DIR Qt6QuickShapes_VERSION Qt6QuickTemplates2Private_DIR Qt6QuickTemplates2Private_VERSION Qt6Quick_DIR Qt6Quick_VERSION Qt6Sql_DIR Qt6Sql_VERSION Qt6Svg_DIR Qt6Svg_VERSION Qt6WaylandClientPrivate_DIR Qt6WaylandClientPrivate_VERSION Qt6WaylandClient_DIR Qt6WaylandClient_VERSION Qt6WaylandScannerTools_DIR Qt6WaylandScannerTools_VERSION Qt6WaylandScannerTools_VERSION_STRING Qt6Widgets_DIR Qt6Widgets_VERSION Qt6Xml_DIR Qt6Xml_VERSION Qt6_DIR Qt6_VERSION Qt6_VERSION_STRING SQLite3_DIR SQLite3_VERSION SQLite3_VERSION_STRING nlohmann_json_DIR nlohmann_json_VERSION nlohmann_json_VERSION_STRING tomlplusplus_DIR tomlplusplus_VERSION tomlplusplus_VERSION_STRING)
  file(APPEND "${CMAKE_BINARY_DIR}/resolved.txt" "${_variable}=${${_variable}}\n")
endforeach()
