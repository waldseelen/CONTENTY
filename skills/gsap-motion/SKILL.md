---
name: gsap-motion
description: Official GSAP motion rules for HyperFrames compositions, SVG animations, and presentation sites. Covers core tweens, timeline positioning, ScrollTrigger, prefers-reduced-motion, and 60fps compositor performance.
license: MIT
---

# GSAP Motion (`gsap-motion`)

Adapted from `greensock/gsap-skills` (MIT) for CONTENTY `video-motoru` (HyperFrames) and `sunum-sitesi`.

## 1. Core Tweens & Transform Aliases
- Use `gsap.to()`, `gsap.from()`, `gsap.fromTo()`, `gsap.set()` with **camelCase** CSS properties.
- Prefer GSAP transform aliases (`x`, `y`, `xPercent`, `yPercent`, `scale`, `rotation`, `autoAlpha`) over raw `transform` strings or layout properties (`top`, `left`, `width`, `height`, `margin`).
- Use `autoAlpha` instead of `opacity` when hiding interactive elements (`autoAlpha: 0` sets `visibility: hidden`).
- For SVG global coordinates, use `svgOrigin: "cx cy"` (cannot be combined with `transformOrigin`).
- When multiple `from()` / `fromTo()` tweens target the same property, set `immediateRender: false` on later tweens.

## 2. Timelines & HyperFrames Sync
- Build deterministic sequences with `gsap.timeline({ defaults: { ease: "power2.out", duration: 0.5 } })`.
- Position parameter:
  - Absolute time: `1.2` (1.2s)
  - Relative: `"+=0.3"`, `"-=0.2"`
  - Labels: `"scene2"`, `"scene2+=0.15"`
  - Concurrent: `"<"` (same start as previous), `"<0.1"` (0.1s after previous start)
- For HyperFrames video compositions, register timelines with deterministic durations matching audio/TTS `manifest.json` segment offsets so `seek()` / frame-capture remains frame-accurate.

## 3. ScrollTrigger & Responsive Motion
- Register once: `gsap.registerPlugin(ScrollTrigger)`.
- Wrap responsive and accessibility logic in `gsap.matchMedia()`:
  ```javascript
  const mm = gsap.matchMedia();
  mm.add("(prefers-reduced-motion: no-preference)", () => {
    // motion timelines here
  });
  ```
- In React / Vue / framework components, clean up via `gsap.context()` or `useGSAP()`.

## 4. 60fps Performance Rules
- Animate only compositor properties (`x`, `y`, `scale`, `rotation`, `opacity`/`autoAlpha`) whenever possible.
- Avoid interleaving DOM reads and writes (batch layout reads before GSAP writes).
- Add `will-change: transform` only on actively animated layers; clear temporary inline styles with `clearProps` on completion when static CSS should resume.
