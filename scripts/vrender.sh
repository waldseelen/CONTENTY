#!/usr/bin/env bash
# vrender.sh — Render an MLT project to MP4 with melt (headless, cross-platform).
# Usage: vrender.sh PROJECT.mlt [OUT.mp4] [quality|fast]
#   quality (default) = libx264 CRF 18, slow
#   fast              = h264_videotoolbox (macOS) or libx264 veryfast (Linux/Windows)
set -euo pipefail

MELT="${MELT_BIN:-$(command -v melt || true)}"
if [ -z "$MELT" ] && [ -x "/Applications/kdenlive.app/Contents/MacOS/melt" ]; then
  MELT="/Applications/kdenlive.app/Contents/MacOS/melt"
fi

PROJ="${1:-}"
OUT="${2:-out.mp4}"
MODE="${3:-quality}"

if [ -z "$PROJ" ] || [ ! -f "$PROJ" ]; then
  echo "HATA: .mlt dosyasi bulunamadi. Kullanim: vrender.sh PROJECT.mlt [OUT.mp4] [quality|fast]" >&2
  exit 1
fi
if [ -z "$MELT" ]; then
  echo "HATA: melt bulunamadi (Linux: sudo apt install melt | macOS: brew install mlt)" >&2
  exit 1
fi

if [ "$MODE" = "fast" ]; then
  if [ "$(uname -s)" = "Darwin" ]; then
    "$MELT" "$PROJ" -consumer avformat:"$OUT" \
      vcodec=h264_videotoolbox b=14M acodec=aac ab=256k pix_fmt=yuv420p
  else
    "$MELT" "$PROJ" -consumer avformat:"$OUT" \
      vcodec=libx264 crf=21 preset=veryfast acodec=aac ab=192k pix_fmt=yuv420p
  fi
else
  "$MELT" "$PROJ" -consumer avformat:"$OUT" \
    vcodec=libx264 crf=18 preset=slow acodec=aac ab=256k pix_fmt=yuv420p
fi

echo "rendered: $OUT"
