---
title: FUTURE — İleri Faz Açık Kaynak Skill, Plugin ve MCP Adayları
date: 2026-11-23
tags:
  - future
  - roadmap
  - skills
  - plugins
  - mcp
status: research-backlog
---

# FUTURE — Genişleme ve İleri Faz Adayları

Bu dosya, **CONTENTY** fabrikasını büyütmek için GitHub üzerinde taranan açık kaynaklı `SKILL.md`, `.claude-plugin` ve MCP adaylarının tam envanteridir. Zaten depoda bulunan (`references/awesome-video-skills.md`, `references/mcp-catalog.md`, `references/editors-landscape.md`) projeler hariç tutulmuştur.

> [!NOTE] Kullanım Kuralı
> Bir repo `/home/hp/Work/temp/` altına klonlandığında önce **lisans**, **harici/ücretli API bağımlılığı** ve **güvenlik** açısından incelenir; yalnızca temiz ve tekrar etmeyen parçalar `skills/`, `scripts/` veya `plugins/` içine uyarlanır.

---

## 1. Öncelikli Faz (İlk Çekilecek 8 Aday — Tamamlandı)

| Öncelik | Repo | Lisans | Odak Alanı | Durum / Uyarlanan Parçalar |
| :---: | :--- | :--- | :--- | :--- |
| 1 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | MIT | Motion / HyperFrames | `skills/gsap-motion/SKILL.md` |
| 2 | [AgriciDaniel/claude-shorts](https://github.com/AgriciDaniel/claude-shorts) | MIT | 9:16 Shorts Kesimi | `skills/faceless-and-shorts/references/` (`scoring-rubric.md`, `platform-specs.md`, `caption-styles.md`) |
| 3 | [lxgicstudios/lxgic-clipper](https://github.com/lxgicstudios/lxgic-clipper) | MIT | Canlı Yayın Kesiti | `scripts/detect_highlights.sh` |
| 4 | [danielrosehill/Claude-OBS-Plugin](https://github.com/danielrosehill/Claude-OBS-Plugin) | MIT | OBS Kurulum & Sahne | `scripts/obs_ws.py`, `scripts/obs_health.py`, `scripts/obs_hotkeys.py` |
| 5 | [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) | MIT | Senaryo & Paketleme | `scripts/yt_hookscore.py`, `scripts/hooks.json`, `scripts/yt_title_lint.py`, `scripts/yt_retention.py`, `scripts/yt_deadair.py` |
| 6 | [AgriciDaniel/claude-youtube](https://github.com/AgriciDaniel/claude-youtube) | MIT | YouTube Büyüme & SEO | `skills/youtube-growth/SKILL.md` + `references/` (`retention-scripting-guide.md`, `thumbnail-ctr-guide.md`, `seo-playbook.md`) |
| 7 | [captjt/skill-tts](https://github.com/captjt/skill-tts) | MIT | Yerel Seslendirme | `skills/audio-and-roughcut/SKILL.md` (JSON süre manifesti sözleşmesi) |
| 8 | [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) | MIT | Diyagram & Görsel | `skills/diagram-svg/SKILL.md` + `themes/` (`dark.json`, `light.json`) |

---

## 2. Video Kurgu, Motion Graphics & Shorts

| Repo | Lisans | Yetenekler | Notlar / Kısıtlar |
| :--- | :--- | :--- | :--- |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | MIT | `skills/manim-video/SKILL.md` ve `remotion-video-creation`. | Dev repo; yalnızca medya skill'leri seçilip alınmalı. Remotion ticari lisans sınırına dikkat. |
| [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) | MIT | Remotion React+TSX ile marka girişi, explainer ve dikey klip tarifleri. | Yerel Remotion gerekir (küçük ekip/bireysel ücretsiz; büyük şirkette ticari lisans). |
| [Hainrixz/editor-pro-max](https://github.com/Hainrixz/editor-pro-max) | MIT | Remotion bileşen şablonları, Google Fonts betiği ve lisans takip dosyası (`LICENCIAS.md`). | Medya/SFX içermez; Remotion lisans şartı geçerli. |
| [remotion-dev/claude-code-plugin](https://github.com/remotion-dev/claude-code-plugin) | — | Resmi Remotion skill'lerini paketleyen `.claude-plugin`. | Remotion lisans şartına dikkat. |
| [akachandan1/video-studio](https://github.com/akachandan1/video-studio) | MIT | HyperFrames + FFmpeg + WhisperX + Kokoro + DeepFilterNet; beat-grid cue ve çoklu oran (`16:9`/`9:16`/`4:5`) yerleşimi. | Çok erken aşama; `setup.sh` macOS varsayar; opsiyonel ücretli API anahtarları vardır. |
| [iart-ai/tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills) | MIT | Dikey hook-retention döngüleri, kelime zamanlı altyazı, geri sayım ve alt bantlar. | Bazı ileri akışlar ücretli ElevenLabs/fal API çağırabilir; çekirdek yerel. |
| [iart-ai/explainer-video-skills](https://github.com/iart-ai/explainer-video-skills) | MIT | Anlatımlı diyagram ve storyboard paketleri. | Bazı ileri ses/medya akışları opsiyonel ücretli API kullanır. |
| [mutonby/openshorts-plugin](https://github.com/mutonby/openshorts-plugin) | MIT | Dosya/URL'den kesit çıkarma, karaoke altyazı ve çoklu platform yayını (MCP + skill). | Self-host ücretsiz; barındırılan bulut render API'si ücretli ($12/ay+). |
| [social-media-skills/video-to-shorts-skill](https://github.com/social-media-skills/video-to-shorts-skill) | MIT | 9:16 puanlama rubriği ve FFmpeg kırpma kuralları (`video-editing-skill`'in kardeşi). | Opsiyonel üçüncü taraf WoopSocial entegrasyonu içerir. |
| [skulitom/cutbolt-plugin](https://github.com/skulitom/cutbolt-plugin) | MIT | Talking-head, çoklu kamera senkronu ve transactional undo/retry destekli Rust MCP motoru ([Cutbolt](https://github.com/skulitom/Cutbolt)). | Çok yeni/erken aşama; Rust toolchain gerekir. |
| [PaulBratslavsky/roughcut-ai-local-first-editor](https://github.com/PaulBratslavsky/roughcut-ai-local-first-editor) | GPL-3.0 | `whisper.cpp` + yerel Ollama (Gemma) ile kaba kesim, NLE export ve MCP yüzeyi. | **GPL-3.0** copyleft lisansı (doğrudan kod kopyalamada GPL zorunlu). |
| [limin112/video-subtitle](https://github.com/limin112/video-subtitle) | Belirtilmemiş | Çift dilli gömülü `.ass` ve özel fontlu altyazı işleme. | Lisans belirsiz; yalnızca fikir/referans. |
| [YanlongLai/video-subtitle-skill](https://github.com/YanlongLai/video-subtitle-skill) | MIT | Kısa form videolar için hareketli başlık bindirmeleri. | Erken aşama. |

---

## 3. Canlı Yayın (OBS / Twitch / Kick / Overlay)

| Repo | Lisans | Yetenekler | Notlar / Kısıtlar |
| :--- | :--- | :--- | :--- |
| [mtane0412/twitch-mcp-server](https://github.com/mtane0412/twitch-mcp-server) | MIT | Twitch Helix/GraphQL MCP: canlı durum, izleyici sayısı, klip listesi, VOD chat yorumları. | Ücretsiz Twitch Developer API anahtarı gerekir (`TWITCH_CLIENT_ID`). |
| [rlmsinclair/stream-dashboard](https://github.com/rlmsinclair/stream-dashboard) | Belirtilmemiş | Twitch/Kick/YouTube çoklu chat birleştirme + yayın başlığı/kategori/etiket güncelleme MCP'si. | Kök lisans dosyası doğrulanmalı. |
| [Jugachi/multi-chat-for-streamers](https://github.com/Jugachi/multi-chat-for-streamers) | MIT | Twitch/YouTube/Kick/TikTok sohbetini 7TV/BTTV/FFZ emote'larıyla yerel OBS Browser Source'a basar. | Rust/Tauri masaüstü uygulaması (%100 yerel). |
| [hkopenai/vtube-studio-plugin-mcp-server](https://github.com/hkopenai/vtube-studio-plugin-mcp-server) | MIT | MCP üzerinden Live2D model parametrelerini gerçek zamanlı yönetir. | VTube Studio masaüstü uygulaması (freemium) gerekir. |

---

## 4. Ses, Yerel TTS & Podcast

| Repo | Lisans | Yetenekler | Notlar / Kısıtlar |
| :--- | :--- | :--- | :--- |
| [codecraftersllc/local-voice-mcp](https://github.com/codecraftersllc/local-voice-mcp) | MIT | Kokoro ONNX + Chatterbox (`[laugh]`, `[sigh]` etiketleri & zero-shot ses klonlama) MCP sunucusu. | %100 yerel (`npx` + Python 3.10–3.12). |
| [mberg/kokoro-tts-mcp](https://github.com/mberg/kokoro-tts-mcp) | Apache-2.0 | Saf Python Kokoro-82M yerel TTS MCP sunucusu. | Python 3.9+ gerekir. |
| [demon24ru/fish-speech-mcp](https://github.com/demon24ru/fish-speech-mcp) | MIT | Yerel Fish Speech sunucusuna bağlanan ses klonlama/TTS MCP köprüsü. | Yerel Fish Speech sunucusu + GPU önerilir. |
| [ebmarquez/audio-transcription-mcp](https://github.com/ebmarquez/audio-transcription-mcp) | MIT | `Faster-Whisper` + `pyannote.audio` ile **çoklu konuşmacı ayrıştırma (speaker diarization)**. | Docker + Python (%100 yerel; podcast kurgusu için ideal). |
| [xDarkzx/Audacity-MCP](https://github.com/xDarkzx/Audacity-MCP) | Apache-2.0 | 140+ araçlı Audacity ses temizliği ve podcast mastering MCP'si (`OBS_MCP` yazarından). | Audacity 3.x masaüstü kurulumu gerekir. |
| [TwelveTake-Studios/reaper-mcp](https://github.com/TwelveTake-Studios/reaper-mcp) | MIT | 180+ araçlı çok kanallı REAPER DAW miks/mastering MCP'si. | REAPER + ReaPack gerekir. |

---

## 5. Senaryo, SEO, Büyüme & Thumbnail

| Repo | Lisans | Yetenekler | Notlar / Kısıtlar |
| :--- | :--- | :--- | :--- |
| [tenfoldmarc/script-skill](https://github.com/tenfoldmarc/script-skill) | — | Kişiselleştirilmiş ses profili çıkarma + rakip outlier hook veritabanı + retention senaryosu. | %100 yerel `SKILL.md` akışı. |
| [milad-ahmd/agent-skills](https://github.com/milad-ahmd/agent-skills) | — | `youtube-script-writer` (cold-open, open loop, B-roll notları) ve `youtube-seo-optimizer`. | %100 yerel `SKILL.md`. |
| [deeployCO/youtube-seo-skills](https://github.com/deeployCO/youtube-seo-skills) | — | Kanal denetimi, anahtar kelime kümeleme, thumbnail kontrast/renk CV puanlama. | CV scriptleri yerel; canlı metrikler için YouTube/MCP gerekir. |
| [hassancs91/claude-youtube-editor](https://github.com/hassancs91/claude-youtube-editor) | — | A/B/C thumbnail stratejisi (1–3 kelime, görsel hiyerarşi) + Remotion otomasyon hattı. | Tam otomasyon ücretli API'ler kullanır (Gemini, AssemblyAI, ElevenLabs). |

---

## 6. Diyagram, Görsel, Slayt & Tasarım (Canva-Free)

| Repo | Lisans | Yetenekler | Notlar / Kısıtlar |
| :--- | :--- | :--- | :--- |
| [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill) | — | Doğal dilden `.excalidraw` diyagram + Playwright/Python ile render-ve-incele hizalama döngüsü. | %100 yerel. |
| [ZunbaRan/excalidraw-slides-skills](https://github.com/ZunbaRan/excalidraw-slides-skills) | — | Metinden `1600x900` 16:9 Excalidraw slayt desteleri. | %100 yerel. |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | — | 50+ yerleşim tipinde saf HTML + SVG editoryal diyagramlar. | %100 yerel. |
| [twwch/comfyui-workflow-skill](https://github.com/twwch/comfyui-workflow-skill) | — | Doğal dilden FLUX, SDXL, Wan 2.2, HunyuanVideo için geçerli ComfyUI workflow JSON üretimi. | Yerel ComfyUI kurulumu ile ücretsiz. |
| [LevyBytes/AI-SKILL-gimp](https://github.com/LevyBytes/AI-SKILL-gimp) / [sandraschi/gimp-mcp](https://github.com/sandraschi/gimp-mcp) | — | GIMP üzerinden katmanlı thumbnail ve görsel düzenleme alternatifleri. | Yerel GIMP gerekir. |

---

## 7. Genel Ekosistem Koleksiyonları, Araştırma & Metin Stratejisi

| Repo | Lisans | İçeriden Alınabilecek İlgili Skill'ler | Format |
| :--- | :--- | :--- | :--- |
| [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 (örnekler) | `frontend-design`, `canvas-design`, `theme-factory`, `brand-guidelines`, `algorithmic-art`, `slack-gif-creator` | `SKILL.md` + `.claude-plugin` |
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | MIT | `copywriting` (anti-AI-klişe, PAS/BAB hook), `content-strategy`, `social` | `SKILL.md` + Marketplace |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Apache-2.0 (repo) | `content-research-writer`, `video-downloader` (`yt-dlp`), `image-enhancer` | `SKILL.md` |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | MIT | `copywriting`, `content-production`, `social-content` | `SKILL.md` + `.claude-plugin` |
| [wshobson/agents](https://github.com/wshobson/agents) | MIT | `content-marketing`, `seo-content-creation`, `social-publishing` | `.claude-plugin` |
| [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills) | MIT | `deep-research`, `fact-checker`, `meeting-minutes-taker` | `SKILL.md` + Marketplace |
| [obsidianmd/obsidian-skills](https://github.com/obsidianmd/obsidian-skills) | MIT | `defuddle` (web'den temiz Markdown araştırma çekme), `knap` | `SKILL.md` + Marketplace |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | MIT | `npx skills add <owner/repo>` CLI (`pbakaus/impeccable` Apache-2.0, `nextlevelbuilder/ui-ux-pro-max-skill` MIT) | CLI + `SKILL.md` |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | MIT | Kürasyonlu medya, tasarım ve sosyal medya `SKILL.md` dizini | Awesome list |
| [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) | MIT / CC BY 4.0 | Geniş topluluk skill arşivi | `.claude-plugin` + `SKILL.md` |
