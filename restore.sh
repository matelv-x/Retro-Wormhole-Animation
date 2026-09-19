#!/usr/bin/env bash
set -euo pipefail

TARGET="/home/pi/sg1_v4/web"
REMOVE_ALL=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage:
  ./restore.sh [--target /home/pi/sg1_v4] [--remove-all]

Without --remove-all, restore the exact state from immediately before the most
recent v2 installation. If v1 was present before v2, v1 remains installed.

With --remove-all, first restore the pre-v2 state and then remove both the v1
GIF overlay and all v2 files, configuration, and numbered uploaded portal media.
Repository clone folders and timestamped backups are not deleted.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      if [ "$#" -lt 2 ] || [ -z "$2" ]; then
        echo "ERROR: --target requires a path." >&2
        exit 2
      fi
      TARGET="$2"
      shift 2
      ;;
    --remove-all)
      REMOVE_ALL=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ -d "$TARGET/web/retro" ]; then
  TARGET="$TARGET/web"
fi
if [ ! -d "$TARGET/retro" ]; then
  echo "ERROR: target web folder not found: $TARGET" >&2
  exit 1
fi

APP_ROOT="$(dirname "$TARGET")"
POINTER="$TARGET/backups/.retro-wormhole-animation-latest"

if [ -f "$POINTER" ]; then
  BACKUP_DIR="$(head -n 1 "$POINTER")"
  MANIFEST="$BACKUP_DIR/manifest.tsv"
  if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: backup manifest not found: $MANIFEST" >&2
    exit 1
  fi
  while IFS=$'\t' read -r existed rel; do
    [ -n "$rel" ] || continue
    destination="$APP_ROOT/$rel"
    if [ "$existed" = "1" ]; then
      mkdir -p "$(dirname "$destination")"
      cp -a "$BACKUP_DIR/original/$rel" "$destination"
      echo "Restored: $destination"
    else
      rm -f "$destination"
      echo "Removed added file: $destination"
    fi
  done < "$MANIFEST"
  rm -f "$POINTER"
  echo "Restored exact pre-install state from: $BACKUP_DIR"
elif [ "$REMOVE_ALL" -eq 0 ]; then
  echo "No v2 backup pointer found; applying legacy marked-fragment removal."
  python3 "$SCRIPT_DIR/remove_overlay.py" "$TARGET"
fi

if [ "$REMOVE_ALL" -eq 1 ]; then
  echo "Removing all Retro Wormhole GIF v1 and Retro Wormhole Animation v2 components."
  python3 "$SCRIPT_DIR/remove_overlay.py" "$TARGET" --remove-all-media
  echo "Uploaded numbered Wormhole and Black Hole media were removed."
fi

echo "=== RETRO WORMHOLE ANIMATION SURGICAL RESTORE COMPLETE ==="
