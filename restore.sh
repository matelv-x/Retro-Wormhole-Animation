#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-/home/pi/sg1_v4/web}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$TARGET" == "--target" ]]; then
  TARGET="${2:-/home/pi/sg1_v4/web}"
fi

if [ -d "$TARGET/web/retro" ]; then
  TARGET="$TARGET/web"
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
else
  echo "No v2 backup pointer found; applying legacy marked-fragment removal."
  python3 "$SCRIPT_DIR/remove_overlay.py" "$TARGET"
fi

echo "=== RETRO WORMHOLE ANIMATION SURGICAL RESTORE COMPLETE ==="
