#!/usr/bin/env bash
# install_plugin.sh — Package or link contenty-studio skills/plugin for Antigravity or Claude Code.
# Usage:
#   ./scripts/install_plugin.sh antigravity   # symlink/copy to ~/.gemini/config/plugins/contenty-studio
#   ./scripts/install_plugin.sh claude        # symlink skills into ~/.claude/skills/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-}"

case "$TARGET" in
  antigravity)
    DEST="$HOME/.gemini/config/plugins/contenty-studio"
    mkdir -p "$DEST"
    cp "$ROOT/plugins/contenty-studio/plugin.json" "$DEST/"
    cp "$ROOT/plugins/contenty-studio/README.md" "$DEST/"
    cp -R "$ROOT/plugins/contenty-studio/rules" "$DEST/"
    ln -sfn "$ROOT/skills" "$DEST/skills"
    echo "Antigravity plugin baglandi: $DEST"
    echo "Not: MCP sunucularini eklemek icin plugins/contenty-studio/mcp_config.template.json dosyasini kendi yollarinla ~/.gemini/config/mcp_config.json icine uyarla."
    ;;
  claude)
    DEST="$HOME/.claude/skills"
    mkdir -p "$DEST"
    for dir in "$ROOT"/skills/*/; do
      name="$(basename "$dir")"
      ln -sfn "$dir" "$DEST/$name"
    done
    echo "Claude Code skill'leri baglandi: $DEST"
    ;;
  *)
    echo "Kullanim: $0 [antigravity|claude]" >&2
    exit 1
    ;;
esac
