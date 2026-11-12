#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly STATE_REL="var/lib/holonight/source-install"
TARGET_ROOT="/"
ASSUME_YES=0
CHECK_ONLY=0

usage() { echo "Usage: scripts/uninstall.sh [--check] [--yes] [--root <staging-root>]"; }
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
TARGET_ROOT="${TARGET_ROOT%/}"; [[ -n "$TARGET_ROOT" ]] || TARGET_ROOT="/"
MANIFEST="$TARGET_ROOT/$STATE_REL/manifest.tsv"
[[ -f "$MANIFEST" ]] || die "no umbrella source-install manifest exists at $MANIFEST"
note "Manifest found: $MANIFEST"
((CHECK_ONLY == 0)) || exit 0

if ((ASSUME_YES == 0)); then
  printf 'Remove unmodified HoloNight source-install artifacts from %s? [y/N] ' "$TARGET_ROOT"
  read -r answer
  [[ "$answer" = y || "$answer" = Y || "$answer" = yes || "$answer" = YES ]] || die "uninstallation cancelled"
fi

as_root() { if [[ "$TARGET_ROOT" != "/" || EUID -eq 0 ]]; then "$@"; else sudo "$@"; fi; }
hash_path() {
  if [[ -L "$1" ]]; then printf '%s' "$(readlink "$1")" | sha256sum | awk '{print $1}'
  elif [[ -f "$1" ]]; then sha256sum "$1" | awk '{print $1}'
  else printf '%s' '-'; fi
}

images_operation_fd=""
if [[ "$TARGET_ROOT" = / || -e "$TARGET_ROOT/usr/libexec/holonight-images/.images-install.lock" ]]; then
  images_operation_lock="$(as_root python3 "$SCRIPT_DIR/manage-images-generations.py" operation-lock \
    --runtime "$TARGET_ROOT/usr/libexec/holonight-images/runtime" --helper /bin/false \
    --ownership-manifest "$MANIFEST")"
  exec {images_operation_fd}< "$images_operation_lock"
  flock -x "$images_operation_fd"
fi

# Managed payloads are removed only under generation leases. Keep their ownership
# records, including a busy or modified generation, out of generic removal loops.
managed_images=0
managed_images_removed=0
managed_manifest=""
if awk -F '\t' '$6 == "/usr/libexec/holonight-images/runtime/ownership.json" { found=1 } END { exit !found }' "$MANIFEST"; then
  managed_images=1
  helper=""
  revision=managed
  while IFS=$'\t' read -r module revision type mode expected relative; do
    if [[ "$module" = holonight-images && "$type" = f && "$relative" = /usr/libexec/holonight-images/runtime/generations/*/usr/libexec/holonight-images-helper ]]; then
      candidate="$TARGET_ROOT$relative"
      if [[ -f "$candidate" && ! -L "$candidate" && "$(hash_path "$candidate")" = "$expected" ]]; then helper="$candidate"; break; fi
    fi
  done < "$MANIFEST"
  if [[ -z "$helper" && -f "$TARGET_ROOT/usr/libexec/holonight-images/runtime/ownership.json" &&
        "$(cat "$TARGET_ROOT/usr/libexec/holonight-images/runtime/ownership.json")" = "[]" ]]; then helper=/bin/false; fi
  managed_manifest="$(mktemp)"
  trap '[[ -z "$managed_manifest" ]] || rm -f -- "$managed_manifest"' EXIT
  if [[ -n "$helper" ]] && as_root python3 "$SCRIPT_DIR/manage-images-generations.py" remove \
      --runtime "$TARGET_ROOT/usr/libexec/holonight-images/runtime" --helper "$helper" \
      --ownership-manifest "$MANIFEST" --revision "$revision" --emit-manifest > "$managed_manifest"; then
    managed_images_removed=1
  else
    printf 'preserved managed Images runtime: modified, unowned, busy, or unverifiable; ownership records retained\n' >&2
  fi
fi

mapfile -t entries < "$MANIFEST"
preserved=0
for ((index=${#entries[@]}-1; index>=0; index--)); do
  IFS=$'\t' read -r module revision type mode expected relative <<< "${entries[index]}"
  if ((managed_images)) && [[ "$relative" = /usr/libexec/holonight-images/runtime || "$relative" = /usr/libexec/holonight-images/runtime/* || "$relative" = /usr/libexec/holonight-images/.images-install.lock ]]; then continue; fi
  if [[ -n "$images_operation_fd" && "$relative" = /usr/libexec/holonight-images/.images-install.lock ]]; then continue; fi
  path="$TARGET_ROOT$relative"
  parent="${path%/*}"
  unsafe_parent=0
  while [[ "$parent" != / && "$parent" != . ]]; do
    if [[ -L "$parent" ]]; then unsafe_parent=1; break; fi
    parent="${parent%/*}"
    parent="${parent:-/}"
  done
  if ((unsafe_parent)); then
    printf 'preserved path under symlinked parent: %s\n' "$path" >&2
    preserved=$((preserved + 1))
    continue
  fi
  case "$type" in
    f|l)
      [[ -e "$path" || -L "$path" ]] || continue
      actual="$(hash_path "$path")"
      if [[ "$actual" = "$expected" ]]; then
        as_root rm -f -- "$path"
      else
        printf 'preserved modified path: %s\n' "$path" >&2
        preserved=$((preserved + 1))
      fi ;;
    d)
      if [[ -d "$path" && ! -L "$path" ]]; then as_root rmdir -- "$path" 2>/dev/null || true; fi ;;
  esac
done

if ((managed_images)); then
  if ((managed_images_removed)); then
    as_root install -m 0644 "$managed_manifest" "$MANIFEST"
    note "Retained managed Images lock and empty ownership bookkeeping for serialized future operations"
  fi
elif [[ -n "$images_operation_fd" ]]; then
  managed_manifest="$(mktemp)"
  trap '[[ -z "$managed_manifest" ]] || rm -f -- "$managed_manifest"' EXIT
  printf 'holonight-images\tmanaged\tf\t644\t%s\t/usr/libexec/holonight-images/.images-install.lock\n' \
    "$(hash_path "$images_operation_lock")" > "$managed_manifest"
  as_root install -m 0644 "$managed_manifest" "$MANIFEST"
  note "Retained source-install operation lock ownership for serialized future installation"
else
  as_root rm -f -- "$TARGET_ROOT/$STATE_REL/revisions" "$MANIFEST"
  as_root rmdir -- "$TARGET_ROOT/$STATE_REL" 2>/dev/null || true
  as_root rmdir -- "$TARGET_ROOT/var/lib/holonight" 2>/dev/null || true
fi

if [[ "$TARGET_ROOT" = "/" ]]; then
  as_root ldconfig
  as_root systemctl daemon-reload
  command -v update-desktop-database >/dev/null && as_root update-desktop-database /usr/share/applications || true
  command -v kbuildsycoca6 >/dev/null && as_root env XDG_MENU_PREFIX=arch- kbuildsycoca6 --noincremental || true
fi
note "Uninstall complete; preserved $preserved modified path(s)"
