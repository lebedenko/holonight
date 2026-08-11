#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
readonly STATE_REL="var/lib/holonight/source-install"
readonly MODULES=(holonight-config holonight-qt holonight-appearance-adapters holonight-icons holonight-shell holonight-settings holonight-ai holonight-pkg-manager holonight-greeter holonightd)

TARGET_ROOT="/"
ASSUME_YES=0
CHECK_ONLY=0
BUILD_ROOT="$REPO_ROOT/.source-install"

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [--check] [--yes] [--root <staging-root>]

  --check  Run distribution, checkout, toolchain, package, and account checks only.
  --yes    Do not prompt before copying the completed stage.
  --root   Install below an alternate root (for VM/image and integration testing).
EOF
}

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
note() { printf '==> %s\n' "$*"; }

while (($#)); do
  case "$1" in
    --check) CHECK_ONLY=1 ;;
    --yes) ASSUME_YES=1 ;;
    --root) shift; (($#)) || die "--root requires a path"; TARGET_ROOT="$1" ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$TARGET_ROOT" = /* ]] || die "--root must be an absolute path"
TARGET_ROOT="${TARGET_ROOT%/}"
[[ -n "$TARGET_ROOT" ]] || TARGET_ROOT="/"

preflight() {
  [[ -r /etc/os-release ]] || die "cannot identify this distribution"
  # shellcheck disable=SC1091
  . /etc/os-release
  case "${ID:-}:${ID_LIKE:-}" in
    arch:*|*:arch*) ;;
    *) die "unsupported distribution '${PRETTY_NAME:-unknown}'; source installation currently supports Arch Linux and Arch-derived systems" ;;
  esac

  local missing_commands=() command_name
  for command_name in git cmake ninja pkg-config sha256sum find sort awk install cp readlink getent; do
    command -v "$command_name" >/dev/null 2>&1 || missing_commands+=("$command_name")
  done

  local missing_packages=() package_name
  local packages=(base-devel cmake ninja pkgconf qt6-base qt6-declarative qt6-svg qt6-wayland layer-shell-qt
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
  compiler="$(command -v c++ || command -v g++)"
  printf '#include <expected>\nint main(){std::expected<int,int> v(1); return *v-1;}\n' |
    "$compiler" -std=c++23 -x c++ -fsyntax-only - >/dev/null 2>&1 ||
    die "the default C++ compiler does not provide the required C++23 support"

  getent passwd greeter >/dev/null || die "the greeter system account is missing; install/configure greetd before installing HoloNight Greeter"

  local module expected actual
  for module in "${MODULES[@]}"; do
    [[ -e "$REPO_ROOT/$module/.git" ]] || die "submodule '$module' is not initialized; run: git submodule update --init --recursive"
    expected="$(git -C "$REPO_ROOT" ls-tree HEAD "$module" | awk '{print $3}')"
    actual="$(git -C "$REPO_ROOT/$module" rev-parse HEAD)"
    [[ -n "$expected" && "$actual" = "$expected" ]] ||
      die "submodule '$module' is at $actual, but the umbrella pins ${expected:-an unavailable revision}; run: git submodule update --init --recursive"
  done
}

configure_and_stage() {
  local module="$1" build_dir="$BUILD_ROOT/build/$1" stage="$BUILD_ROOT/stage"
  local prefix_path="$stage/usr"
  local args=(-S "$REPO_ROOT/$module" -B "$build_dir" -G Ninja
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
    -DCMAKE_PREFIX_PATH="$prefix_path" -DBUILD_TESTS=OFF -DBUILD_TESTING=OFF
    -DENABLE_COVERAGE=OFF)

  case "$module" in
    holonight-appearance-adapters)
      args+=( -DBUILD_GTK_PROBES=OFF -DHOLONIGHT_QT_DIR="$prefix_path" -DHOLONIGHT_CONFIG_DIR="$prefix_path" ) ;;
    holonight-qt)
      args+=( -DBUILD_DEMO=OFF -DBUILD_CONTROLS_GALLERY=OFF -DBUILD_QT5_PROBES=OFF ) ;;
    holonight-ai)
      args+=( -DHOLONIGHT_QML_IMPORT_PATH="$prefix_path/lib/qt6/qml" ) ;;
  esac

  note "Configuring $module"
  cmake "${args[@]}"
  note "Building $module"
  cmake --build "$build_dir" --parallel
  DESTDIR="$stage" cmake --install "$build_dir"
}

stage_icons() {
  note "Staging holonight-icons"
  mkdir -p "$BUILD_ROOT/stage/usr/share/icons/HoloNight"
  cp -a "$REPO_ROOT/holonight-icons/HoloNight/." "$BUILD_ROOT/stage/usr/share/icons/HoloNight/"
}

hash_path() {
  local path="$1"
  if [[ -L "$path" ]]; then printf '%s' "$(readlink "$path")" | sha256sum | awk '{print $1}'
  elif [[ -f "$path" ]]; then sha256sum "$path" | awk '{print $1}'
  else printf '%s' '-'; fi
}

make_manifest() {
  local stage="$BUILD_ROOT/stage" output="$BUILD_ROOT/manifest.tsv"
  : > "$output"
  local module revision path relative type mode hash owner_module
  while IFS= read -r -d '' path; do
    relative="${path#"$stage"}"
    [[ "$relative" != "/$STATE_REL"* ]] || continue
    if [[ -L "$path" ]]; then type=l; mode=-
    elif [[ -d "$path" ]]; then type=d; mode="$(stat -c '%a' "$path")"
    else type=f; mode="$(stat -c '%a' "$path")"; fi
    owner_module=umbrella
    for module in "${MODULES[@]}"; do
      if [[ -f "$BUILD_ROOT/module-paths/$module" ]] && grep -Fqx "$relative" "$BUILD_ROOT/module-paths/$module"; then
        owner_module="$module"
      fi
    done
    if [[ "$owner_module" = umbrella ]]; then revision="$(git -C "$REPO_ROOT" rev-parse HEAD)"
    else revision="$(git -C "$REPO_ROOT/$owner_module" rev-parse HEAD)"; fi
    hash="$(hash_path "$path")"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$owner_module" "$revision" "$type" "$mode" "$hash" "$relative" >> "$output"
  done < <(find "$stage" -mindepth 1 -print0 | sort -z)
}

record_module_paths() {
  local module="$1" before="$2" after="$3"
  mkdir -p "$BUILD_ROOT/module-paths"
  comm -13 "$before" "$after" > "$BUILD_ROOT/module-paths/$module"
}

collision_check() {
  local manifest="$BUILD_ROOT/manifest.tsv" old_manifest="$TARGET_ROOT/$STATE_REL/manifest.tsv"
  local module revision type mode hash relative destination
  local collisions=0
  while IFS=$'\t' read -r module revision type mode hash relative; do
    [[ "$type" != d ]] || continue
    destination="$TARGET_ROOT$relative"
    [[ ! -e "$destination" && ! -L "$destination" ]] && continue
    if [[ -f "$old_manifest" ]] && awk -F '\t' -v path="$relative" '$6 == path { found=1 } END { exit !found }' "$old_manifest"; then
      continue
    fi
    printf 'collision: %s already exists and is not owned by an earlier umbrella installation\n' "$destination" >&2
    collisions=1
  done < "$manifest"
  ((collisions == 0)) || die "installation aborted before modifying $TARGET_ROOT"
}

as_root() {
  if [[ "$TARGET_ROOT" != "/" || EUID -eq 0 ]]; then "$@"; else sudo "$@"; fi
}

copy_stage() {
  local stage="$BUILD_ROOT/stage" manifest="$BUILD_ROOT/manifest.tsv"
  local module revision type mode hash relative source destination target
  while IFS=$'\t' read -r module revision type mode hash relative; do
    source="$stage$relative"; destination="$TARGET_ROOT$relative"
    case "$type" in
      d) as_root install -d -m "$mode" "$destination" ;;
      f) as_root install -D -m "$mode" "$source" "$destination" ;;
      l)
        target="$(readlink "$source")"
        as_root install -d "$(dirname "$destination")"
        if [[ "$TARGET_ROOT" = "/" && EUID -ne 0 ]]; then sudo ln -sfn -- "$target" "$destination"; else ln -sfn -- "$target" "$destination"; fi ;;
    esac
  done < "$manifest"
  as_root install -d -m 0755 "$TARGET_ROOT/$STATE_REL"
  as_root install -m 0644 "$manifest" "$TARGET_ROOT/$STATE_REL/manifest.tsv"
  git -C "$REPO_ROOT" submodule status > "$BUILD_ROOT/revisions"
  as_root install -m 0644 "$BUILD_ROOT/revisions" "$TARGET_ROOT/$STATE_REL/revisions"
}

refresh_system() {
  if [[ "$TARGET_ROOT" = "/" ]]; then
    as_root ldconfig
    as_root systemctl daemon-reload
    command -v gtk-update-icon-cache >/dev/null && as_root gtk-update-icon-cache -q -t -f /usr/share/icons/HoloNight || true
    command -v update-desktop-database >/dev/null && as_root update-desktop-database /usr/share/applications || true
    command -v kbuildsycoca6 >/dev/null && as_root env XDG_MENU_PREFIX=arch- kbuildsycoca6 --noincremental || true
    as_root systemd-tmpfiles --create holonight-greeter.conf
  else
    systemd-tmpfiles --root="$TARGET_ROOT" --create holonight-greeter.conf ||
      note "Greeter tmpfiles could not be materialized in the alternate root; its definition is installed"
  fi
}

preflight
note "Preflight passed"
((CHECK_ONLY == 0)) || exit 0

rm -rf -- "$BUILD_ROOT"
mkdir -p "$BUILD_ROOT/build" "$BUILD_ROOT/stage" "$BUILD_ROOT/module-paths"
for module in "${MODULES[@]}"; do
  before="$BUILD_ROOT/before"; after="$BUILD_ROOT/after"
  find "$BUILD_ROOT/stage" -mindepth 1 -printf '/%P\n' | sort > "$before"
  if [[ "$module" = holonight-icons ]]; then stage_icons; else configure_and_stage "$module"; fi
  find "$BUILD_ROOT/stage" -mindepth 1 -printf '/%P\n' | sort > "$after"
  record_module_paths "$module" "$before" "$after"
done
make_manifest
collision_check

if ((ASSUME_YES == 0)); then
  printf 'All components are staged and collision-free. Install into %s? [y/N] ' "$TARGET_ROOT"
  read -r answer
  [[ "$answer" = y || "$answer" = Y || "$answer" = yes || "$answer" = YES ]] || die "installation cancelled"
fi

copy_stage
refresh_system
note "Installed HoloNight; ownership manifest: $TARGET_ROOT/$STATE_REL/manifest.tsv"
