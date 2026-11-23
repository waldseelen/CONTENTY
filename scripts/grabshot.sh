#!/usr/bin/env bash
# grabshot.sh — Save clipboard image to workspace/02-cleaned/screenshots/ (Linux Wayland/X11 + macOS)
# Usage: grabshot.sh [optional-name]
set -euo pipefail

DIR="${STUDIO_JOBS:-workspace/02-cleaned}/screenshots"
mkdir -p "$DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
NAME="${1:-shot_$STAMP}"
OUT="$DIR/${NAME}.png"

if [ "$(uname -s)" = "Darwin" ]; then
  osascript <<OSA >/dev/null 2>&1 || true
set outFile to POSIX file "$OUT"
try
    set pngData to (the clipboard as «class PNGf»)
on error
    return "NO_IMAGE"
end try
set fh to open for access outFile with write permission
set eof fh to 0
write pngData to fh
close access fh
return "OK"
OSA
elif command -v wl-paste >/dev/null 2>&1 && wl-paste --list-types 2>/dev/null | grep -q "image/png"; then
  wl-paste --type image/png > "$OUT"
elif command -v xclip >/dev/null 2>&1; then
  xclip -selection clipboard -t image/png -o > "$OUT" 2>/dev/null || true
else
  echo "HATA: Desteklenen pano araci yok (wl-paste, xclip veya macOS osascript gerekli)." >&2
  exit 1
fi

if [ -s "$OUT" ]; then
  echo "saved: $OUT ($(du -h "$OUT" | cut -f1))"
else
  rm -f "$OUT"
  echo "Panoda PNG gorsel bulunamadi." >&2
  exit 1
fi
