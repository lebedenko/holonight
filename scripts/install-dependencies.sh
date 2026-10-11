#!/usr/bin/env bash
# Sourceable, read-only dependency checks shared by the installer and fixtures.

check_qt_wayland_capabilities() (
  # A subshell keeps the cleanup trap local to this probe, including failures.
  local probe_dir
  probe_dir="$(mktemp -d "${TMPDIR:-/tmp}/holonight-qt-check.XXXXXXXX")" || return 1
  trap 'rm -rf -- "$probe_dir"' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  local helper_dir
  helper_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  cp "$helper_dir/../tooling/install-profile.cmake" "$probe_dir/CMakeLists.txt"
  if ! cmake -S "$probe_dir" -B "$probe_dir/build" -G Ninja "-DPython3_EXECUTABLE=$(command -v python3)"; then
    printf 'error: Qt >= 6.11 with WaylandClient, Qt6WaylandScannerTools, matching Qt private modules, Python >= 3.10 (icons), tomlplusplus >= 3.4 (Files), installed shared QMarkdown 1.x with QML metadata, and the full installation profile is required; see CMake diagnostics above for the unavailable capability or configuration failure.\n' >&2
    return 1
  fi
)

check_install_dependencies() {
  local missing_commands=() command_name
  for command_name in git cmake ninja pkg-config sha256sum find sort awk install cp readlink getent mktemp rm cat dirname python3 wayland-scanner; do
    command -v "$command_name" >/dev/null 2>&1 || missing_commands+=("$command_name")
  done

  local missing_packages=() package_name
  # Papirus and Breeze are optional and may be installed in user icon paths.
  # Icon lookup still falls back to hicolor when neither theme is available.
  local helper_dir
  helper_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  # shellcheck source=install-profile.sh
  . "$helper_dir/install-profile.sh"
  local packages=("${HOLONIGHT_INSTALL_PACKAGES[@]}")
  if command -v pacman >/dev/null 2>&1; then
    local package_output package_status=0
    package_output="$(pacman -T "${packages[@]}")" || package_status=$?
    # Deptest returns 127 for unsatisfied dependencies; other failures must
    # not be mistaken for an empty (successful) dependency report.
    if ((package_status != 0 && package_status != 127)); then
      printf 'error: pacman dependency check failed (exit %s)\n' "$package_status" >&2
      return 1
    fi
    while IFS= read -r package_name; do
      [[ -n "$package_name" ]] && missing_packages+=("$package_name")
    done <<< "$package_output"
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
