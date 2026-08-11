#!/usr/bin/env bash
set -euo pipefail

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

mapfile -t entries < "$MANIFEST"
preserved=0
for ((index=${#entries[@]}-1; index>=0; index--)); do
  IFS=$'\t' read -r module revision type mode expected relative <<< "${entries[index]}"
  path="$TARGET_ROOT$relative"
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
      if [[ -d "$path" ]]; then as_root rmdir -- "$path" 2>/dev/null || true; fi ;;
  esac
done

as_root rm -f -- "$TARGET_ROOT/$STATE_REL/revisions" "$MANIFEST"
as_root rmdir -- "$TARGET_ROOT/$STATE_REL" 2>/dev/null || true
as_root rmdir -- "$TARGET_ROOT/var/lib/holonight" 2>/dev/null || true

if [[ "$TARGET_ROOT" = "/" ]]; then
  as_root ldconfig
  as_root systemctl daemon-reload
  command -v update-desktop-database >/dev/null && as_root update-desktop-database /usr/share/applications || true
  command -v kbuildsycoca6 >/dev/null && as_root env XDG_MENU_PREFIX=arch- kbuildsycoca6 --noincremental || true
fi
note "Uninstall complete; preserved $preserved modified path(s)"
