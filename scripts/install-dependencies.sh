#!/usr/bin/env bash
# Sourceable, read-only dependency checks shared by the installer and fixtures.

check_qt_wayland_capabilities() (
  # A subshell keeps the cleanup trap local to this probe, including failures.
  local probe_dir
  probe_dir="$(mktemp -d "${TMPDIR:-/tmp}/holonight-qt-check.XXXXXXXX")" || return 1
  trap 'rm -rf -- "$probe_dir"' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  cat > "$probe_dir/CMakeLists.txt" <<'EOF'
cmake_minimum_required(VERSION 3.25)
project(HoloNightDependencyCheck LANGUAGES CXX)
find_package(Qt6 6.11 REQUIRED COMPONENTS WaylandClient)
find_package(Qt6WaylandScannerTools 6.11 REQUIRED)
EOF
  if ! cmake -S "$probe_dir" -B "$probe_dir/build" -G Ninja; then
    printf 'error: Qt >= 6.11 with WaylandClient and Qt6WaylandScannerTools is required; see CMake diagnostics above for the unavailable capability or configuration failure.\n' >&2
    return 1
  fi
)

check_install_dependencies() {
  local missing_commands=() command_name
  for command_name in git cmake ninja pkg-config sha256sum find sort awk install cp readlink getent mktemp rm cat; do
    command -v "$command_name" >/dev/null 2>&1 || missing_commands+=("$command_name")
  done

  local missing_packages=() package_name
  local packages=(base-devel cmake ninja pkgconf qt6-base qt6-declarative qt6-svg layer-shell-qt
    tomlplusplus json-glib gtk3 gtk4 wayland wayland-protocols libpulse libsecret pacman sqlite systemd
    syntax-highlighting md4c greetd cage)
  if command -v pacman >/dev/null 2>&1; then
    while IFS= read -r package_name; do
      [[ -n "$package_name" ]] && missing_packages+=("$package_name")
    done < <(pacman -T "${packages[@]}" 2>/dev/null || true)
  else
    missing_commands+=(pacman)
  fi

  if ((${#missing_commands[@]})); then
    printf 'Missing required commands: %s\n' "${missing_commands[*]}" >&2
  fi
  if ((${#missing_packages[@]})); then
    printf 'Missing required Arch packages. Install them explicitly with:\n  sudo pacman -S --needed %s\n' "${missing_packages[*]}" >&2
  fi
  ((${#missing_commands[@]} == 0 && ${#missing_packages[@]} == 0)) || return 1

  local compiler
  compiler="$(command -v c++ || command -v g++)" || {
    printf 'error: a C++23 compiler (c++ or g++) is required\n' >&2
    return 1
  }
  printf '#include <expected>\nint main(){std::expected<int,int> v(1); return *v-1;}\n' |
    "$compiler" -std=c++23 -x c++ -fsyntax-only - >/dev/null 2>&1 ||
    { printf 'error: the default C++ compiler does not provide the required C++23 support\n' >&2; return 1; }

  check_qt_wayland_capabilities
}
