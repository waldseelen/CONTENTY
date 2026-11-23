---
name: studio-router
description: >-
  Main entry router for the CONTENTY AI video, YouTube, and live-stream production
  factory. Routes any request (OBS live stream -> highlights/Shorts, faceless explainer,
  podcast, rough-cut, motion graphics, thumbnail, or presentation site) to the exact
  skill chain, templates, and quality gate scripts.
---

# CONTENTY Studio Router

Gelen içerik isteğini formatına göre doğru skill zincirine ve yerel scriptlere yönlendirir.

## 1. Proje Başlatma (İlk Adım)
Her yeni video veya yayın özetinde yerel çalışma klasörünü ve şablonları kur:
```bash
python3 scripts/init_project.py "<proje-adi>" --format <youtube|faceless|shorts|podcast|stream>
```

## 2. Format Bazlı Skill Zinciri

| İstek / Format | İzlenecek Skill Sırası | Kullanılacak Scriptler |
| :--- | :--- | :--- |
| **Ham ekran kaydı / talking-head kurgusu** | `ajanla-video-kurgu` → `audio-and-roughcut` → `video-edit-core` | `transcribe.py`, `remove-silence.py` / `autocut.sh`, `mltgen.py`, `vrender.sh` |
| **Yüzsüz (faceless) anlatım / hikâye videosu** | `video-prompt-builder` → `ajanla-video-kurgu` (pano haritası) → `video-motoru` → `faceless-and-shorts` | `transcribe.py`, `mltgen.py`, `vrender.sh`, HyperFrames |
| **Canlı yayın (OBS) → özet + Shorts** | `channel-ops-and-obs` → `audio-and-roughcut` → `faceless-and-shorts` | `transcribe.py`, `caption_and_chapters.py`, `qc_gate.py` |
| **Podcast → video / audiogram + kesitler** | `audio-and-roughcut` (`podcast` profili) → `faceless-and-shorts` | `transcribe.py`, `caption_and_chapters.py`, `qc_gate.py --profile podcast` |
| **Yüksek CTR Thumbnail** | `thumbnail-factory` | `ffmpeg` / `PIL` (`1280x720`, `<2MB`) |
| **Video eşlikçi sunum sitesi** | `sunum-sitesi` | Statik HTML/CSS/JS + `python3 -m http.server` |

## 3. Değişmez Çıkış Kapısı
Her teslimat öncesi kullanıcıya hızlı taslak gösterilir ve final MP4 üzerinde fail-closed kapı çalıştırılır:
```bash
python3 scripts/caption_and_chapters.py transcript/raw_timed.json --corrections 06-metadata/caption-corrections.json --srt 05-exports/captions.srt
python3 scripts/qc_gate.py 05-exports/final.mp4 --profile youtube --contact-sheet 05-exports/qc_3x2.jpg --json
```
Onay sonrası `channel-ops-and-obs` + `YOUTUBE_API_GUIDE.md` protokolüyle `private` taslak olarak yüklenir.
