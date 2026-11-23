---
name: diagram-svg
description: Create 100% local, zero-network SVG diagrams with CSS custom properties for dark and light themes. Ideal for video explainers, HyperFrames overlays, and presentation sites.
license: MIT
---

# Local SVG Diagram Generator (`diagram-svg`)

Adapted from `JimLiu/baoyu-skills` (`baoyu-diagram`, MIT). Produces clean, network-free SVG diagrams themed with CSS custom properties.

## 1. Output Contract
- Save source SVG as `<name>.svg` using CSS variables in `<style>:root { ... }</style>`.
- Never hardcode hex/rgba colors on `<rect>`, `<path>`, or `<text>` attributes; always reference `var(--bg)`, `var(--text)`, `var(--color-primary-fill)`, etc.
- Theme palettes are stored in `skills/diagram-svg/themes/dark.json` and `skills/diagram-svg/themes/light.json`.

## 2. Structural & Visual Rules
- Define explicit `viewBox="0 0 W H"` (e.g., `0 0 1920 1080` for 16:9 video overlays or `0 0 1200 800` for slides).
- Include `<defs>` arrow markers (`marker-end="url(#arrow)"`) and consistent stroke widths (`1.5px`–`2px`).
- Keep labels short (2–5 words per node), minimum `14px` font size, and generous padding (`24px+` inside boxes, `40px+` between nodes) so text remains legible in 1080p video or mobile thumbnails.
- Zero external `<image>`, `<link>`, or webfont URLs so SVG renders deterministically in headless Chromium, FFmpeg, or HyperFrames.

## 3. PNG Export (Optional)
Convert SVG to crisp `@2x` PNG locally when raster overlays are needed:
```bash
rsvg-convert -z 2 diagram.svg -o diagram@2x.png
# or with ImageMagick / Inkscape
```
