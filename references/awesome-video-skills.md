---
title: Güvenlik Puanlı Açık Kaynak Video Skill Dizini (Seçki)
date: 2026-11-22
tags:
  - references
  - skills
  - faceless
  - shorts
  - motion-graphics
---

# Güvenlik Puanlı Video Skill Seçkisi

[zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) içindeki **537** güvenlik derecelendirmeli repodan (`data/skills.json`) yalnızca **`SAFE`** notlu, açık kaynaklı ve yüzsüz anlatım, OBS yayın kesiti, Shorts ve diyagram formatlarına doğrudan uyan en güçlü projeler süzülmüştür.

> [!NOTE] End-to-End Benchmark Bulgusu (16 Skill Testi, Sıfır Ücretli API)
> 16 skill hiçbir ücretli görüntü/video/ses API anahtarı olmadan test edildiğinde tamamı 4/4 teknik geçer not aldı. En hızlı üretim süreleri: **`explainroo` (2.0 dk)**, **`remotion-video-skill` (3.4 dk)**, **`vibe-motion/skills` (4.4 dk)**, **`remotion-dev/skills` (4.5 dk)**. En yavaş ama detaylı: **`hyperframes` (23.5 dk)**.

---

## 1. Yüzsüz Anlatım & Bilgi Videoları (Explainers — Felsefe / Teknoloji / Politika)

| Repo | Yıldız | Lisans | Neden Seçildi |
| :--- | :---: | :--- | :--- |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 87.7k | Apache-2.0 | HTML/CSS/GSAP ile kare-bazlı düzenlenebilir açık kaynak video motoru. |
| [EverMind-AI/Raven](https://github.com/EverMind-AI/Raven) | 6.3k | Apache-2.0 | El çizimi tarzında anlatımlı kısa film + HTML önizleme stüdyosu. |
| [Alisa0808/vox-director](https://github.com/Alisa0808/vox-director) | 3.0k | MIT | **Vox tarzı kâğıt kolaj (paper-collage) explainer** boru hattı (FFmpeg tabanlı). |
| [vincentsch/explainroo](https://github.com/vincentsch/explainroo) | 1.4k | MIT | Benchmark birincisi (2.0 dk): tamamen yerel ses (Kokoro) + Whisper zamanlama + render. |
| [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) | 1.4k | MIT | 3Blue1Brown tarzı teknik/felsefi/matematiksel diyagram animasyonları. |
| [Moh4696/cinematic-skill](https://github.com/Moh4696/cinematic-skill) | 867 | MIT | Fotoğraf, harita ve kartlar üzerinde tek sürekli kamera akışıyla anlatımlı belgesel videoları (saf kod). |
| [leodavincs/kalem](https://github.com/leodavincs/kalem) | 119 | — | Türkçe geliştirilmiş sahne bazlı çoklu motor yönlendirici (Paper.js, PixiJS, HyperFrames, Three.js, Manim). |

---

## 2. Kurgu & Yerel MCP Editörler (Editing)

| Repo | Yıldız | Lisans | Neden Seçildi |
| :--- | :---: | :--- | :--- |
| [browser-use/video-use](https://github.com/browser-use/video-use) | 31.4k | MIT | Ana referansımız: 12 üretim doğruluk kuralı, EDL, paralel animasyon ajanları. |
| [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | 9.5k | MIT | Ana referansımız: 42 deterministik FFmpeg aracı, stdlib Python, sıfır bulut. |
| [FireRedTeam/FireRed-OpenStoryline](https://github.com/FireRedTeam/FireRed-OpenStoryline) | 3.7k | Apache-2.0 | Niyet odaklı (intention-driven) ajan video kurgu yönetmeni. |
| [0xsline/OpenChatCut](https://github.com/0xsline/OpenChatCut) | 3.3k | AGPL-3.0 | Yerel, çok kanallı timeline + Agent Skills + MCP entegrasyonlu konuşmalı editör. |
| [pireel/pireel](https://github.com/pireel/pireel) | 1.5k | AGPL-3.0 | Açık kaynak MCP video editörü: altyazı, kesim, B-roll, timeline export. |
| [MakeMyClip/editor](https://github.com/MakeMyClip/editor) | 26 | — | Yerel `whisper.cpp` ile transkriptten kesim, sessizlik ve tekrar temizliği (MCP uyumlu). |

---

## 3. Yüzsüz Shorts & Sosyal Medya (9:16 Dikey)

| Repo | Yıldız | Lisans | Neden Seçildi |
| :--- | :---: | :--- | :--- |
| [nexu-io/openmotion](https://github.com/nexu-io/openmotion) | 14.5k | Apache-2.0 | Referans videoyu kendi marka kitiyle düzenlenebilir motion graphics'e çevirir. |
| [kaomei/stickman-video-director](https://github.com/kaomei/stickman-video-director) | 7.3k | MIT | Metinden çöp adam (stickman) tarzı yüzsüz YouTube & Shorts üretimi. |
| [artemnovitckii/claude-animation-skills](https://github.com/artemnovitckii/claude-animation-skills) | 1.0k | — | Ham görüntü olmadan 11 farklı yüzsüz animasyon stili (low-poly, voxel, 3D çizgi). |
| [0xS4N4TG/papercut-explainer](https://github.com/0xS4N4TG/papercut-explainer) | 251 | MIT | Kâğıt kesim (papercut) estetiğinde dikey bilgi Shorts'ları. |
| [hassancs91/claude-faceless-shorts-creator](https://github.com/hassancs91/claude-faceless-shorts-creator) | 378 | MIT | Saf Remotion TSX + kelime-senkronlu yüzsüz Shorts fabrikası (sesi yerel TTS/kendi sesinle değiştirilebilir). |

---

## 4. Hareketli Grafik, Diyagram & Kanal Büyümesi (Motion & Craft)

| Repo | Yıldız | Lisans | Neden Seçildi |
| :--- | :---: | :--- | :--- |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | 7.7k | — | Resmi Remotion ajan kuralları (kodla video yazarken çökme/performans hatalarını önler). |
| [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) | 2.9k | MIT | Slayt gibi değil gerçek video gibi akan 5 farklı tarayıcı motion-graphics explainer stili. |
| [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills) | 2.0k | — | 56 açık kaynak kinetik tipografi, veri görselleştirme ve explainer skill'i. |
| [cclank/lanshu-animated-architecture-diagram](https://github.com/cclank/lanshu-animated-architecture-diagram) | 1.1k | MIT | El çizimi tarzında hareketli teknik/mimari diyagramlar (yazılım & teknoloji bölümleri için). |
| [ythx-101/live-panel-skill](https://github.com/ythx-101/live-panel-skill) | 875 | MIT | Tek JSON veya Excalidraw dosyasından terminal tarzı hareketli diyagram üretimi. |
| [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) | 2.1k | MIT | Dramaturji, hikâye kurgusu ve senaryo ritmi için ajan skill'leri. |
| [adityaarsharma/youtube-marketing-skills](https://github.com/adityaarsharma/youtube-marketing-skills) | 88 | MIT | 21 YouTube büyüme/başlık/paketleme komutu + kanal MCP desteği. |

> [!CAUTION] Güvenlik Notu
> `OpenMontageInc/OpenMontage` (82k★) dizinde `CAUTION` güvenlik notu taşır; kaynak kodunu denetlemeden doğrudan çalıştırma. Yukarıdaki tabloların tamamı `SAFE` doğrulamalıdır.

İlgili rehberler: [[skills/faceless-and-shorts/SKILL|faceless-and-shorts]], [[references/editors-landscape|editors-landscape]], [[README]].
