---
name: youtube-growth
description: Data-driven YouTube script hooks, title+thumbnail pairing lint, audience retention leak analysis, dead-air EDL detection, and SEO/CTR playbooks. Uses local zero-dependency Python tools.
license: MIT
---

# YouTube Growth, Hook & Packaging (`youtube-growth`)

Adapted from `Jakeschincariol/youtube-agent-skill` (MIT) and `AgriciDaniel/claude-youtube` (MIT).

## 1. Local Analysis Tools (`scripts/`)
- **Hook Scoring (21 formulas, weakest-link weighting):**
  ```bash
  python3 scripts/yt_hookscore.py --hook "Your opening line here" --json
  python3 scripts/yt_hookscore.py hooks.txt
  ```
  Reference formulas live in `scripts/hooks.json`.
- **Title + Thumbnail Pairing Lint (40/60/100 char limits + duplicate word check):**
  ```bash
  python3 scripts/yt_title_lint.py --title "Your Video Title" --thumb "THUMB TEXT" --json
  ```
  Rule: Never repeat thumbnail words in the title — title and thumbnail are one click unit.
- **Audience Retention Leak Analyzer (YouTube Studio CSV):**
  ```bash
  python3 scripts/yt_retention.py retention.csv --transcript captions.srt --json
  ```
  Reports `HOOK LEAK` (first 30s), `CLIFFS` (steepest drops with spoken context), and `SLIDE` (mid-video bleed).
- **Dead-Air / Transcript EDL:**
  ```bash
  python3 scripts/yt_deadair.py transcript.srt --floor 0.35 --json
  ```

## 2. Playbook References (`references/`)
Read the targeted reference before drafting scripts, thumbnails, or metadata:
- `references/retention-scripting-guide.md` — Cold opens, open loops, pattern interrupts, pacing beats.
- `references/thumbnail-ctr-guide.md` — 3-element rule, focal hierarchy, mobile contrast, curiosity gap.
- `references/seo-playbook.md` — Search intent, keyword placement, chapter & description structure.
