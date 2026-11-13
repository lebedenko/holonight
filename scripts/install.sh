#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
readonly STATE_REL="var/lib/holonight/source-install"
readonly MODULES=(holonight-config holonight-system-services holonight-qt holonight-appearance-adapters holonight-icons holonight-images holonight-thumbnails holonight-search holonight-file-browser holonight-shell holonightd holonight-settings holonight-viewer holonight-files xdg-desktop-portal-holonight holonight-ai holonight-pkg-manager holonight-greeter holonight-hyprlock)

TARGET_ROOT="/"
ASSUME_YES=0
CHECK_ONLY=0
ADOPT_EXISTING=0
PROTECTED_IMAGES=0
MAINTENANCE_IMAGES=0
BUILD_ROOT="$REPO_ROOT/.source-install"

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [--check] [--yes] [--adopt-existing] [--root <staging-root>]

  --check  Run distribution, checkout, toolchain, package, and account checks only.
  --yes    Do not prompt before copying the completed stage.
  --root   Install below an alternate root (for VM/image and integration testing).
  --protected-images-runtime  Use managed generations under a protected alternate root.
                             Enabled automatically for system installation.
  --maintenance-migrate-images-runtime  Convert an owned legacy runtime; all image-consuming
                                        applications must be stopped first.
  --adopt-existing  Back up and replace unowned files; reject package-owned files.
EOF
}

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
note() { printf '==> %s\n' "$*"; }

while (($#)); do
  case "$1" in
    --check) CHECK_ONLY=1 ;;
    --yes) ASSUME_YES=1 ;;
    --adopt-existing) ADOPT_EXISTING=1 ;;
    --protected-images-runtime) PROTECTED_IMAGES=1 ;;
    --maintenance-migrate-images-runtime) MAINTENANCE_IMAGES=1 ;;
    --root) shift; (($#)) || die "--root requires a path"; TARGET_ROOT="$1" ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$TARGET_ROOT" = /* ]] || die "--root must be an absolute path"
TARGET_ROOT="${TARGET_ROOT%/}"
[[ -n "$TARGET_ROOT" ]] || TARGET_ROOT="/"
[[ "$TARGET_ROOT" != / ]] || PROTECTED_IMAGES=1

# shellcheck source=install-dependencies.sh
. "$SCRIPT_DIR/install-dependencies.sh"

preflight() {
  [[ -r /etc/os-release ]] || die "cannot identify this distribution"
  # shellcheck disable=SC1091
  . /etc/os-release
  case "${ID:-}:${ID_LIKE:-}" in
    arch:*|*:arch*) ;;
    *) die "unsupported distribution '${PRETTY_NAME:-unknown}'; source installation currently supports Arch Linux and Arch-derived systems" ;;
  esac

  [[ -z "${HOLONIGHT_EXTERNAL_PREFIX:-}" ]] || die "system deployment requires package-managed external libraries; HOLONIGHT_EXTERNAL_PREFIX is for development/staging"
  check_install_dependencies || return 1

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
    holonight-images)
      args+=( -DHOLONIGHT_IMAGES_ISOLATED=ON ) ;;
    holonight-thumbnails)
      args+=( -DHOLONIGHT_THUMBNAILS_ISOLATED=ON ) ;;
    holonight-appearance-adapters)
      args+=( -DBUILD_GTK_PROBES=OFF -DHOLONIGHT_QT_DIR="$prefix_path" -DHOLONIGHT_CONFIG_DIR="$prefix_path" ) ;;
    holonight-qt)
      args+=( -DBUILD_DEMO=OFF -DBUILD_CONTROLS_GALLERY=OFF -DBUILD_QT5_PROBES=OFF ) ;;
    holonight-file-browser|holonight-viewer|holonight-files|xdg-desktop-portal-holonight)
      args+=( -DQML_IMPORT_PATH="$prefix_path/lib/qt6/qml" ) ;;
    holonight-ai)
      args+=( -DHOLONIGHT_QML_IMPORT_PATH="$prefix_path/lib/qt6/qml" ) ;;
  esac

  note "Configuring $module"
  cmake "${args[@]}"
  note "Building $module"
  cmake --build "$build_dir" --parallel
  if [[ "$module" = holonight-images ]]; then
    # A fresh bundle is prepared from this host build, never a container artifact.
    local runtime_parent
    runtime_parent="$(mktemp -d "$build_dir/runtime-XXXXXXXX")"
    python3 "$REPO_ROOT/holonight-images/scripts/prepare-isolated-runtime.py" \
      --helper "$build_dir/holonight-images-helper" --plugins /usr/lib/qt6/plugins \
      --output "$runtime_parent/bundle"
    cmake -S "$REPO_ROOT/$module" -B "$build_dir" \
      -DHOLONIGHT_IMAGES_RUNTIME_BUNDLE="$runtime_parent/bundle"
  fi
  # Images' install rules verify the prepared inventory and helper before copying.
  DESTDIR="$stage" cmake --install "$build_dir"
}

stage_icons() {
  note "Staging holonight-icons"
  python3 "$REPO_ROOT/holonight-icons/scripts/stage.py" --destdir "$BUILD_ROOT/stage"
  # Generate caches before recording ownership, including for alternate roots.
  # Deployment refreshes owned caches again and records their final hashes.
  if command -v gtk-update-icon-cache >/dev/null; then
    local theme
    for theme in HoloNight HoloNight-Dark; do
      gtk-update-icon-cache -q -t -f "$BUILD_ROOT/stage/usr/share/icons/$theme"
    done
  fi
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
        if [[ "$type" != d && "$owner_module" != umbrella ]]; then
          die "multiple components install $relative: $owner_module and $module"
        fi
        owner_module="$module"
      fi
    done
    if [[ "$owner_module" = umbrella ]]; then revision="$(git -C "$REPO_ROOT" rev-parse HEAD)"
    else revision="$(git -C "$REPO_ROOT/$owner_module" rev-parse HEAD)"; fi
    hash="$(hash_path "$path")"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$owner_module" "$revision" "$type" "$mode" "$hash" "$relative" >> "$output"
  done < <(find "$stage" -mindepth 1 -print0 | sort -z)
}

validate_portal_payload() {
  local descriptor=/usr/share/xdg-desktop-portal/portals/holonight.portal
  local service=/usr/share/dbus-1/services/org.freedesktop.impl.portal.desktop.holonight.service
  local executable=/usr/libexec/xdg-desktop-portal-holonight
  local relative
  for relative in "$descriptor" "$service" "$executable"; do
    awk -F '\t' -v path="$relative" '$1 == "xdg-desktop-portal-holonight" && $3 == "f" && $6 == path { found=1 } END { exit !found }' \
      "$BUILD_ROOT/manifest.tsv" || die "incompatible portal components: unified backend must own $relative"
  done
  grep -Fxq 'DBusName=org.freedesktop.impl.portal.desktop.holonight' "$BUILD_ROOT/stage$descriptor" || die "incorrect portal identity"
  grep -Fxq 'Interfaces=org.freedesktop.impl.portal.FileChooser;org.freedesktop.impl.portal.Settings;' "$BUILD_ROOT/stage$descriptor" || die "incomplete unified portal interfaces"
  grep -Fxq 'Name=org.freedesktop.impl.portal.desktop.holonight' "$BUILD_ROOT/stage$service" || die "incorrect portal activation identity"
  for relative in /usr/share/xdg-desktop-portal/portals/holonight-filechooser.portal \
      /usr/share/dbus-1/services/org.freedesktop.impl.portal.desktop.holonight_filechooser.service; do
    [[ ! -e "$BUILD_ROOT/stage$relative" ]] || die "incompatible legacy portal payload: $relative"
  done
}

record_module_paths() {
  local module="$1" before="$2" after="$3"
  mkdir -p "$BUILD_ROOT/module-paths"
  if [[ -f "$BUILD_ROOT/build/$module/install_manifest.txt" ]]; then
    # CMake lists every installed file, including an overwritten staging path. A
    # before/after inventory alone would hide duplicate component ownership.
    sort -u "$BUILD_ROOT/build/$module/install_manifest.txt" > "$BUILD_ROOT/module-paths/$module"
  else
    comm -13 "$before" "$after" > "$BUILD_ROOT/module-paths/$module"
  fi
}

managed_images_runtime() {
  local args=() revision
  ((MAINTENANCE_IMAGES == 0)) || args+=(--maintenance-migrate)
  revision="$(git -C "$REPO_ROOT/holonight-images" rev-parse HEAD)"
  as_root python3 "$SCRIPT_DIR/manage-images-generations.py" install \
    --runtime "${TARGET_ROOT%/}/usr/libexec/holonight-images/runtime" \
    --source "$BUILD_ROOT/stage/usr/libexec/holonight-images/runtime" \
    --helper "$BUILD_ROOT/stage/usr/libexec/holonight-images/runtime/usr/libexec/holonight-images-helper" \
    --ownership-manifest "$TARGET_ROOT/$STATE_REL/manifest.tsv" --revision "$revision" "${args[@]}" "$@"
}

reconcile_images_runtime() {
  if ((PROTECTED_IMAGES)) && [[ -d "$BUILD_ROOT/stage/usr/libexec/holonight-images/runtime" ]]; then
    local module revision type mode hash relative
    while IFS=$'\t' read -r module revision type mode hash relative; do
      case "$relative" in
        /usr|/usr/libexec|/usr/libexec/holonight-images)
          [[ "$type" = d ]] && (( (8#$mode & 0022) == 0 )) || die "staged runtime ancestor must remain protected: $relative" ;;
      esac
    done < "$BUILD_ROOT/manifest.tsv"
    managed_images_runtime --check
    return
  fi
  as_root python3 "$SCRIPT_DIR/reconcile-images-runtime.py" --root "$TARGET_ROOT" \
    --old-manifest "$TARGET_ROOT/$STATE_REL/manifest.tsv" \
    --new-manifest "$BUILD_ROOT/manifest.tsv" "$@"
}

collision_check() {
  reconcile_images_runtime
  local manifest="$BUILD_ROOT/manifest.tsv" old_manifest="$TARGET_ROOT/$STATE_REL/manifest.tsv"
  local module revision type mode hash relative destination
  local collisions=0 parent
  local preserved_caches="$BUILD_ROOT/preserved-icon-caches"
  local adopted_paths="$BUILD_ROOT/adopted-paths"
  : > "$preserved_caches"
  : > "$adopted_paths"
  while IFS=$'\t' read -r module revision type mode hash relative; do
    if ((PROTECTED_IMAGES)) && [[ "$relative" = /usr/libexec/holonight-images/runtime || "$relative" = /usr/libexec/holonight-images/runtime/* || "$relative" = /usr/libexec/holonight-images/.images-install.lock ]]; then continue; fi
    destination="$TARGET_ROOT$relative"
    parent="${destination%/*}"
    while [[ "$parent" != / && "$parent" != . ]]; do
      [[ ! -L "$parent" ]] || die "symlinked installation parent: $parent"
      parent="${parent%/*}"
      parent="${parent:-/}"
    done
    if [[ "$type" = d ]]; then
      [[ ! -L "$destination" && ( ! -e "$destination" || -d "$destination" ) ]] ||
        die "installation directory is occupied by a file or symlink: $destination"
      continue
    fi
    if [[ ( "$type" = f && -L "$destination" ) || ( -d "$destination" && ! -L "$destination" ) ]]; then
      die "incompatible installation path type: $destination"
    fi
    [[ ! -e "$destination" && ! -L "$destination" ]] && continue
    if [[ -f "$old_manifest" ]] && awk -F '\t' -v path="$relative" '$6 == path { found=1 } END { exit !found }' "$old_manifest"; then
      if [[ "$relative" = /usr/share/xdg-desktop-portal/portals/holonight.portal ]]; then
        local previous_owner previous_type previous_hash
        IFS=$'\t' read -r previous_owner previous_type previous_hash < <(
          awk -F '\t' -v path="$relative" '$6 == path { print $1 "\t" $3 "\t" $5 }' "$old_manifest")
        [[ "$previous_owner" = holonight-shell || "$previous_owner" = xdg-desktop-portal-holonight ]] || die "unexpected portal descriptor owner: $previous_owner"
        [[ "$previous_type" = f && -f "$destination" && ! -L "$destination" && "$(hash_path "$destination")" = "$previous_hash" ]] ||
          die "modified portal descriptor collision: $destination; preserve or resolve it manually before upgrading"
      fi
      continue
    fi
    if [[ "$relative" = /usr/share/xdg-desktop-portal/portals/holonight.portal ]]; then
      die "unmanaged portal descriptor collision: $destination; resolve it manually before upgrading"
    fi
    # Older umbrella releases generated untracked caches. Preserve those files
    # rather than adopting them as owned. Theme changes invalidate their timestamps.
    case "$relative" in
      /usr/share/icons/HoloNight/icon-theme.cache|/usr/share/icons/HoloNight-Dark/icon-theme.cache)
        if [[ -f "$old_manifest" ]] && awk -F '\t' -v path="${relative%/*}/index.theme" \
          '$1 == "holonight-icons" && $6 == path { found=1 } END { exit !found }' "$old_manifest"; then
          note "Preserving unowned legacy cache: $destination (remove it manually to enable managed cache refresh)"
          printf '%s\n' "$relative" >> "$preserved_caches"
          continue
        fi ;;
    esac
    if ((ADOPT_EXISTING)); then
      command -v pacman >/dev/null || die "pacman is required to check ownership before adopting existing files"
      pacman --root "$TARGET_ROOT" -Q >/dev/null 2>&1 || die "cannot read the package database for $TARGET_ROOT; refusing to adopt existing files"
      # Query the selected root's package database, including in image installs.
      if pacman --root "$TARGET_ROOT" -Qo -- "$relative" >/dev/null 2>&1; then
        printf 'collision: %s is package-owned; remove its package before migration\n' "$destination" >&2
        collisions=1
      else
        note "Will back up and adopt: $destination"
        printf '%s\n' "$relative" >> "$adopted_paths"
      fi
      continue
    fi
    printf 'collision: %s already exists and is not owned by an earlier umbrella installation\n' "$destination" >&2
    collisions=1
  done < "$manifest"
  ((collisions == 0)) || die "installation aborted before modifying $TARGET_ROOT; for unmanaged source files, retry with --adopt-existing to back up and migrate them"
  if [[ -s "$preserved_caches" ]]; then
    awk -F '\t' 'NR == FNR { preserved[$0]=1; next } !($6 in preserved)' \
      "$preserved_caches" "$manifest" > "$BUILD_ROOT/filtered-manifest.tsv"
    mv "$BUILD_ROOT/filtered-manifest.tsv" "$manifest"
  fi
}

as_root() {
  if [[ "$TARGET_ROOT" != "/" || EUID -eq 0 ]]; then "$@"; else sudo "$@"; fi
}

refresh_owned_icon_caches() {
  command -v gtk-update-icon-cache >/dev/null || return 0
  local theme relative hash manifest="$BUILD_ROOT/manifest.tsv"
  for theme in HoloNight HoloNight-Dark; do
    relative="/usr/share/icons/$theme/icon-theme.cache"
    if awk -F '\t' -v path="$relative" '$1 == "holonight-icons" && $6 == path { found=1 } END { exit !found }' "$manifest"; then
      as_root gtk-update-icon-cache -q -t -f "$TARGET_ROOT/usr/share/icons/$theme" ||
        note "Cache refresh failed for $theme; recording the deployed cache for uninstall"
      hash="$(hash_path "$TARGET_ROOT$relative")"
      awk -F '\t' -v OFS='\t' -v path="$relative" -v hash="$hash" \
        '$6 == path { $5=hash } { print }' "$manifest" > "$BUILD_ROOT/cache-manifest.tsv"
      mv "$BUILD_ROOT/cache-manifest.tsv" "$manifest"
    fi
  done
}

copy_stage() {
  local stage="$BUILD_ROOT/stage" manifest="$BUILD_ROOT/manifest.tsv"
  local module revision type mode hash relative source destination target
  # Serialize managed installation and removal through ownership publication.
  local images_operation_fd images_operation_lock
  if ((PROTECTED_IMAGES)) && [[ -d "$stage/usr/libexec/holonight-images/runtime" ]]; then
    images_operation_lock="$(as_root python3 "$SCRIPT_DIR/manage-images-generations.py" operation-lock \
      --runtime "${TARGET_ROOT%/}/usr/libexec/holonight-images/runtime" --helper /bin/false \
      --ownership-manifest "$TARGET_ROOT/$STATE_REL/manifest.tsv")"
    exec {images_operation_fd}< "$images_operation_lock"
    flock -x "$images_operation_fd"
  fi
  # Recheck the full runtime before changing any installed payload.
  if ((PROTECTED_IMAGES)) && [[ -d "$stage/usr/libexec/holonight-images/runtime" ]]; then
    managed_images_runtime --emit-manifest > "$BUILD_ROOT/managed-images.tsv"
    awk -F '\t' '$6 != "/usr/libexec/holonight-images/runtime" && index($6, "/usr/libexec/holonight-images/runtime/") != 1' \
      "$manifest" > "$BUILD_ROOT/ordinary-manifest.tsv"
    cat "$BUILD_ROOT/ordinary-manifest.tsv" "$BUILD_ROOT/managed-images.tsv" | sort -t $'\t' -k6,6 > "$BUILD_ROOT/next-manifest.tsv"
    mv "$BUILD_ROOT/next-manifest.tsv" "$manifest"
  else
    reconcile_images_runtime --prune
  fi
  # Complete every backup before replacing any payload. mktemp avoids reusing
  # a previous migration directory and cp -a preserves symlinks and metadata.
  if [[ -s "$BUILD_ROOT/adopted-paths" ]]; then
    local backup
    as_root install -d -m 0700 "$TARGET_ROOT/var/backups"
    backup="$(as_root mktemp -d "$TARGET_ROOT/var/backups/holonight-source-migration.XXXXXXXX")"
    while IFS= read -r relative; do
      as_root install -d "${backup}${relative%/*}"
      as_root cp -a -- "$TARGET_ROOT$relative" "$backup$relative"
    done < "$BUILD_ROOT/adopted-paths"
    note "Existing files backed up to $backup"
  fi
  while IFS=$'\t' read -r module revision type mode hash relative; do
    if ((PROTECTED_IMAGES)) && [[ "$relative" = /usr/libexec/holonight-images/runtime || "$relative" = /usr/libexec/holonight-images/runtime/* || "$relative" = /usr/libexec/holonight-images/.images-install.lock ]]; then continue; fi
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
  if ((PROTECTED_IMAGES == 0)) && [[ -d "$stage/usr/libexec/holonight-images/runtime" ]]; then
    "$stage/usr/libexec/holonight-images/runtime/usr/libexec/holonight-images-helper" \
      --verify-runtime "$TARGET_ROOT/usr/libexec/holonight-images/runtime" ||
      die "deployed Images runtime verification failed; previous ownership manifest preserved; resolve the runtime manually before retrying"
  fi
  if ((PROTECTED_IMAGES)) && [[ -d "$stage/usr/libexec/holonight-images/runtime" ]]; then
    as_root python3 "$SCRIPT_DIR/manage-images-generations.py" validate \
      --runtime "${TARGET_ROOT%/}/usr/libexec/holonight-images/runtime" \
      --helper "$stage/usr/libexec/holonight-images/runtime/usr/libexec/holonight-images-helper"
  fi
  # Retain original hashes for modified obsolete icons and retired portal files
  # so future upgrades and uninstall preserve them too. Cleanup is allowlisted.
  local old_manifest="$TARGET_ROOT/$STATE_REL/manifest.tsv"
  if [[ -f "$old_manifest" ]]; then
    as_root python3 "$SCRIPT_DIR/prune-icons.py" --root "$TARGET_ROOT" \
      --old-manifest "$old_manifest" --new-manifest "$manifest" > "$BUILD_ROOT/retained-icons.tsv"
    cat "$manifest" "$BUILD_ROOT/retained-icons.tsv" | sort -t $'\t' -k6,6 > "$BUILD_ROOT/next-manifest.tsv"
    mv "$BUILD_ROOT/next-manifest.tsv" "$manifest"
  fi
  # Refresh after all copies/removals so cache timestamps reflect deployed trees.
  # Rehash only our caches; never touch unowned caches or paths outside TARGET_ROOT.
  refresh_owned_icon_caches
  as_root install -d -m 0755 "$TARGET_ROOT/$STATE_REL"
  as_root install -m 0644 "$manifest" "$TARGET_ROOT/$STATE_REL/manifest.tsv"
  git -C "$REPO_ROOT" submodule status > "$BUILD_ROOT/revisions"
  as_root install -m 0644 "$BUILD_ROOT/revisions" "$TARGET_ROOT/$STATE_REL/revisions"
  if [[ -n "${images_operation_fd:-}" ]]; then
    flock -u "$images_operation_fd"
    exec {images_operation_fd}<&-
  fi
}

refresh_system() {
  if [[ "$TARGET_ROOT" = "/" ]]; then
    as_root ldconfig
    as_root systemctl daemon-reload
    as_root update-desktop-database /usr/share/applications || die "desktop database refresh failed"
    if command -v kbuildsycoca6 >/dev/null; then
      as_root env XDG_MENU_PREFIX=arch- kbuildsycoca6 --noincremental || die "KDE desktop cache refresh failed"
    fi
    as_root systemd-tmpfiles --create holonight-greeter.conf
  else
    systemd-tmpfiles --root="$TARGET_ROOT" --create holonight-greeter.conf ||
      note "Greeter tmpfiles could not be materialized in the alternate root; its definition is installed"
  fi
}

extend_viewer_defaults() {
  [[ "$TARGET_ROOT" = / && "$CHECK_ONLY" = 0 ]] || return 0
  if ((EUID == 0)); then
    note "Skipping Viewer preference extension for direct root installation"
  else
    python3 "$SCRIPT_DIR/extend-viewer-defaults.py" /usr/share/applications/org.holonight.Viewer.desktop
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
validate_portal_payload
collision_check

if ((ASSUME_YES == 0)); then
  printf 'All components are staged and collision-free. Install into %s? [y/N] ' "$TARGET_ROOT"
  read -r answer
  [[ "$answer" = y || "$answer" = Y || "$answer" = yes || "$answer" = YES ]] || die "installation cancelled"
fi

copy_stage
refresh_system
extend_viewer_defaults
note "Installed HoloNight; ownership manifest: $TARGET_ROOT/$STATE_REL/manifest.tsv"
