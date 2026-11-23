---
title: CONTENTY — Açık Kaynak AI Video & YouTube Üretim Fabrikası
date: 2026-11-23
tags:
  - youtube
  - studio
  - open-source
  - mcp
  - skills
  - contenty
status: reference-ready
---

# CONTENTY — AI Video & YouTube Üretim Fabrikası

Herhangi bir YouTube kanalı veya video projesi için **açık kaynaklı araçlar**, **ajan skill setleri**, **üretim şablonları**, **marka kilitleri** ve **otomatik kalite kapılarıyla** uçtan uca içerik üretmek üzere derlenmiş jenerik üretim fabrikası (`skills`, `scripts`, `templates`, `brand`, `references`, `plugins`, `workspace`).

> [!IMPORTANT] Odak Profili
> * **Formatlar:** Canlı yayın (OBS) + yayından uzun özet & dikey Shorts/Reels + Yüzsüz (faceless) seslendirme/görsel explainer + Podcast/sohbet + Video eşlikçi sunum sitesi.
> * **Otomasyon:** Hikâye/retention planı → pano haritası → tekrar & sessizlik kesimi → stüdyo ses temizliği (`DeepFilterNet` + `-14`/`-16 LUFS`) → kelime-zamanlı altyazı (`faster-whisper` / `mlx-whisper`) → HyperFrames/MLT birleştirme → yüksek CTR thumbnail → YouTube Data API v3 ile taslak (`private`) yükleme.

---

## Depo Haritası

### 1. Çekirdek Dokümanlar & Yönlendirici
* [[AGENTS]] — Çalışma alanı keşif kuralları ve değişmez stüdyo kapıları.
* [[skills/studio-router/SKILL|studio-router]] — Tüm formatlar (`OBS Yayın`, `Yüzsüz`, `Podcast`, `Shorts`, `Thumbnail`, `Sunum`) için tek giriş yönlendiricisi.
* [[ARCHITECTURE]] — OBS, yüzsüz explainer ve podcast için uçtan uca üretim boru hattı, 10 sert doğruluk kuralı ve kalite kapıları.
* [[YOUTUBE_API_GUIDE]] — Google Cloud OAuth 2.0 kurulumu, `resumable` yükleme, kotalar, `private`-taslak stratejisi ve MCP bağlantı şablonları.
* [[FUTURE]] — GitHub araştırmasından çıkan ileri faz açık kaynak skill, plugin ve MCP adayları envanteri.

### 2. Ajan Skill Fabrikası (`skills/`)

#### Çekirdek Kurgu & Kanal Operasyonları
* [[skills/video-edit-core/SKILL|video-edit-core]] — Çekirdek kurgu, EDL, `mltgen.py` + `vrender.sh` hattı, `ffmpeg-skill` (42 araç), `kinocut` (206 araç) ve kalite kapıları.
* [[skills/audio-and-roughcut/SKILL|audio-and-roughcut]] — `DeepFilterNet`, `auto-editor`, `remove-silence.py`, `transcribe.py`, flub-first kesim sırası ve `-14`/`-16 LUFS` mastering.
* [[skills/faceless-and-shorts/SKILL|faceless-and-shorts]] — Yüzsüz görsel motor seçici, HyperFrames deterministik GSAP sözleşmesi, 9:16 Shorts kesimi, Whisper/ASS altyazı ve Audiogram.
* [[skills/channel-ops-and-obs/SKILL|channel-ops-and-obs]] — `OBS_MCP` (148 araç) canlı yayın/kayıt kontrolü + YouTube yükleme/analitik/SEO akışı.

#### Kurgu Atölyesi, Hikâye & Marka Hafızası
* [[skills/ajanla-video-kurgu/SKILL|ajanla-video-kurgu]] — Tek şef orkestrasyonu, pano haritası (*"sadece dinleyen anlar mı?"*), dosya sözleşmesi, kodlanmış kapılar (`04-kapilar`), arıza kataloğu (`09-pahali-dersler`).
* [[skills/video-motoru/SKILL|video-motoru]] — HyperFrames tabanlı kendi kendine öğrenen marka/sahne/ders defteri, etiketli varlık kütüphanesi (`KUTUPHANE.md`) ve referans videodan mekanizma çıkarma (`REFERANS.md`).
* [[skills/video-prompt-builder/SKILL|video-prompt-builder]] — 4 katmanlı hikâye & retention motoru (psikoloji mekanizmaları, anlatı omurgaları, kitle preset'leri, çoklu klip birleştirme ve karakter tutarlılığı).
* [[skills/thumbnail-factory/SKILL|thumbnail-factory]] — Maskot/karakter tabanlı yüksek CTR kapak fabrikası (hook kalıpları, karakter güvenlik kuralları, resmi logo kütüphanesi).
* [[skills/sunum-sitesi/SKILL|sunum-sitesi]] — Video/ders eşlikçisi koyu temalı tek sayfa HTML/CSS/JS sunum sitesi tarifleri.

#### Opsiyonel Harici AI Üretim Skill'leri
* [[skills/higgsfield-generate/SKILL|higgsfield-generate]] — Higgsfield CLI/MCP görsel, video, 3D ve ses üretim kılavuzu (opsiyonel harici servis).
* [[skills/higgsfield-soul-id/SKILL|higgsfield-soul-id]] — Yüz/karakter kimliği eğitimi ve tutarlılık kılavuzu (opsiyonel harici servis).

### 3. Üretim Scriptleri & Kalite Kapıları (`scripts/`)
* `scripts/init_project.py` — Yeni video/yayın projesini (`01-raw`..`06-metadata` + `edit.json`, `pano-haritasi.md`, `KURGU-NOTU.md`, `marka.md`) tek komutta kurar.
* `scripts/qc_gate.py` — `ffprobe` (VFR/süre/A-V senkron) + `ebur128` (`-14`/`-16 LUFS`, true peak ≤ `-1.0 dBTP`) + `blackdetect`/`freezedetect` + `3x2` temas sayfası kalite kapısı.
* `scripts/caption_and_chapters.py` — ASR terim düzeltme (`caption-corrections.json`), 16:9 `.srt` / 9:16 güvenli alanlı `.ass` üretimi ve YouTube `chapters.txt` doğrulama.
* `scripts/mltgen.py` — JSON kesim planını (`templates/edit.json`) Kdenlive/Shotcut/melt uyumlu `.mlt` projesine çevirir.
* `scripts/vrender.sh` — `.mlt` projesini başsız `melt` ile taslak (`fast`) veya master (`quality`, `libx264 CRF 18`) MP4'e render alır.
* `scripts/transcribe.py` — Yerel `faster-whisper` (Linux/Windows) veya `mlx-whisper` (Apple Silicon) ile zaman kodlu transkript çıkarır (`certifi` SSL yamalı).
* `scripts/remove-silence.py` — `ffmpeg silencedetect` + tek re-encode sessizlik kesici.
* `scripts/autocut.sh` — `auto-editor` wrapper (`kdenlive` / `premiere` / `shotcut` XML veya `mp4` export).
* `scripts/slides2png.sh` — Reveal.js sunumlarını `decktape` ile slayt PNG'lerine basar.
* `scripts/grabshot.sh` — Pano görselini diske alır (`wl-paste` / `xclip` / macOS `osascript`).
* `scripts/install_plugin.sh` — `plugins/contenty-studio` paketini Antigravity veya Claude Code skill/plugin dizinine bağlar.

### 4. Marka, Şablonlar & Eklenti Paketi (`brand/`, `templates/`, `plugins/`)
* `brand/frame.template.md` — Renk paleti, tipografi, sabit seed grain dokusu ve anti-slop yasak listesi şablonu.
* `brand/caption-corrections.example.json` — Whisper ASR özel isim düzeltme sözlüğü şablonu.
* `brand/presets/youtube-16x9.json` — 1080p60 render, `-14 LUFS` ses ve altyazı teknik preset'i.
* `templates/edit.json` — `mltgen.py` için örnek JSON kurgu planı.
* `templates/kurgu-atolyesi/` — Marka kilidi, pano haritası, bölüm brief'i, teslim formu, prompt sözleşmesi ve beğenmeme defteri şablonları.
* `templates/video-motoru/` — `Marka`, `Dersler`, `Sahne-Envanteri`, `Araclar`, `Acik-Isler`, `Referanslar`, `Kutuphane` ve `KURGU-NOTU` şablonları.
* `plugins/contenty-studio/` — Antigravity & Claude Code uyumlu eklenti manifesti (`plugin.json`), stüdyo kuralları (`rules/AGENTS.md`) ve `mcp_config.template.json`.

### 5. Referans Analizleri & Notlar (`references/`)
* [[references/mcp-catalog|mcp-catalog]] — Doğrulanmış açık kaynak MCP sunucuları ve hazır `mcpServers` JSON şablonları.
* [[references/editors-landscape|editors-landscape]] — Açık kaynak Premiere Pro, Photoshop ve CapCut alternatifleri.
* [[references/awesome-video-skills|awesome-video-skills]] — Yüzsüz anlatım, kurgu, Shorts ve diyagram için `SAFE` açık kaynak skill'ler.
* `references/notes/` — Kurgu atölyesi bölüm notları (`kurgu-atolyesi-bolumler.md`), tam transkript (`kurgu-atolyesi-transkript.md`), Seedance ve oyun reklamı prompt notları (`seedance-uretim-notlari.md`, `oyun-reklami-promptlari.md`, `gorsel/oyun-reklami/`).

### 6. Çalışma Alanı İskeleti (`workspace/`)
* `workspace/01-raw/`, `workspace/02-cleaned/`, `workspace/03-exports/`, `workspace/04-metadata/` (boş proje şablon iskeleti; ağır medya yerel tutulur).
