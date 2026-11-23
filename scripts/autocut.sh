#!/usr/bin/env bash
# autocut.sh — auto-editor wrapper (sessizlik kesimi / NLE XML export)
# Kullanim:
#   ./autocut.sh "video.mp4" [agresif|denge|koruyucu | threshold% margin] [export_fmt]
#   export_fmt varsayilan: kdenlive (secenekler: kdenlive, premiere, shotcut, mp4)
set -euo pipefail

AE="${AUTO_EDITOR_BIN:-$(command -v auto-editor || true)}"
IN="${1:-}"
MODE="${2:-denge}"
EXPORT_FMT="${4:-${3:-kdenlive}}"

if [ -z "$IN" ] || [ ! -f "$IN" ]; then
  echo "HATA: Dosya yok. Kullanim: autocut.sh <video> [agresif|denge|koruyucu | threshold% margin] [kdenlive|premiere|shotcut|mp4]" >&2
  exit 1
fi

# certifi SSL duzeltmesi (auto-editor v29 binary indirme hatasini onler)
if command -v python3 >/dev/null 2>&1; then
  CERT_PATH="$(python3 -c 'import certifi; print(certifi.where())' 2>/dev/null || true)"
  if [ -n "$CERT_PATH" ]; then
    export SSL_CERT_FILE="$CERT_PATH"
    export REQUESTS_CA_BUNDLE="$CERT_PATH"
  fi
fi

case "$MODE" in
  agresif|aggressive)     THRESH="0.6%"; MARGIN="0.4s" ;;
  ""|denge|balanced)      THRESH="0.6%"; MARGIN="2s" ;;
  koruyucu|conservative)  THRESH="0.6%"; MARGIN="7.5s" ;;
  *)                      THRESH="$MODE"; MARGIN="${3:-2s}"; EXPORT_FMT="${4:-kdenlive}" ;;
esac

BASE="${IN%.*}"
echo "Kesiliyor: $(basename "$IN") (threshold=$THRESH, margin=$MARGIN, format=$EXPORT_FMT)"

if [ -n "$AE" ]; then
  CMD=("$AE")
else
  CMD=(python3 -m auto_editor)
fi

if [ "$EXPORT_FMT" = "mp4" ]; then
  OUT="${BASE}_cut.mp4"
  "${CMD[@]}" "$IN" --edit "audio:threshold=$THRESH" --margin "$MARGIN" --no-open -o "$OUT"
else
  EXT="xml"
  [ "$EXPORT_FMT" = "kdenlive" ] && EXT="kdenlive"
  [ "$EXPORT_FMT" = "shotcut" ] && EXT="mlt"
  OUT="${BASE}_cut.${EXT}"
  "${CMD[@]}" "$IN" --edit "audio:threshold=$THRESH" --margin "$MARGIN" --export "$EXPORT_FMT" -o "$OUT"
fi

echo "Hazir: $OUT"
