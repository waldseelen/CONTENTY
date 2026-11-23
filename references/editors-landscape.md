---
title: Yeni Nesil Açık Kaynak Premiere Pro, Photoshop ve CapCut Alternatifleri
date: 2026-11-22
tags:
  - references
  - open-source
  - editors
  - premiere-alternative
  - photoshop-alternative
---

# Açık Kaynak Editörler & Ajan-Yerli Arayüzler (2025–2026)

FFmpeg dışında son dönemde çıkan tamamen açık kaynaklı Adobe Premiere Pro, Photoshop ve CapCut alternatiflerinin bizzat kaynak kodları ve README dokümanlarından çıkarılmış gerçek durum analizi.

---

## 1. Video Editörleri (Adobe Premiere Pro & CapCut Alternatifleri)

| Proje | Repo / Lisans | Yıldız | Dil | Durum & Ajan Uyumu |
| :--- | :--- | :---: | :--- | :--- |
| **FilmCraft** | [storytold/filmcraft](https://github.com/storytold/filmcraft) (MIT/Apache-2.0) | 18.8k | Saf Rust | **Premiere Pro alternatifi.** FFmpeg kullanmaz; H.264/HEVC/ProRes/AAC/VP9/AV1 kodekleri saf Rust. wgpu GPU kompozitör, 650+ motor komutu ve **yerleşik MCP sunucusu (`filmcraft-cli mcp`)**. Özellik kapsamı ~%86, üretim olgunluğu ~%56 (alpha; Windows portable zip mevcut, VST3/AV1 export henüz yok). |
| **OpenCut** | [OpenCut-app/OpenCut](https://github.com/OpenCut-app/OpenCut) (MIT) | 99.1k | Rust + TS | **CapCut alternatifi.** Şu an sıfırdan Rust çekirdeğiyle yeniden yazılıyor; yeni sürümde **MCP sunucusu, headless toplu render, eklenti mimarisi** geliyor. Bugün üretim için `opencut-app/opencut-classic` (`opencut.app`) kullanılıyor. |
| **Kdenlive** | KDE (GPL) | Olgun | C++ / MLT | **Üretimde en olgun açık kaynak Premiere alternatifi.** `auto-editor --export kdenlive` ile kaba kesim doğrudan açılabilir; **`HKUDS/CLI-Anything`** üzerinden `cli-anything-kdenlive` ajan CLI'ı ile kontrol edilebilir. |
| **Shotcut** | MLT (GPL) | Olgun | C++ / MLT | Hafif, çok formatlı, `CLI-Anything` (`cli-anything-shotcut`) destekli. |
| **Blender** | Blender Foundation (GPL) | Olgun | C/C++/Py | 3D, VFX ve düğüm tabanlı kompozisyon; `CLI-Anything` (`cli-anything-blender`) + Python API ile tam otomasyon. |

> [!WARNING] FilmCraft Windows Sürücü Notu
> FilmCraft Windows'ta yalnızca Vulkan ve DirectX 12 başlatır (OpenGL kapalıdır). AMD/çift GPU sistemlerde açılış sorunu olursa `$env:WGPU_BACKEND = "vulkan"` ile başlatılabilir.

---

## 2. Görsel & Thumbnail Editörleri (Adobe Photoshop Alternatifleri)

| Proje | Repo / Lisans | Yıldız | Dil | Durum & Ajan Uyumu |
| :--- | :--- | :---: | :--- | :--- |
| **PhotoCraft** | [storytold/photocraft](https://github.com/storytold/photocraft) (MIT/Apache-2.0) | 81.0k | Saf Rust | **Photoshop clean-room alternatifi.** 70 araç, 16 ayar katmanı, katman stilleri (Drop Shadow, Stroke, Outer Glow), gerçek `.psd` uyumu (307/309 test dosyası piksel eşleşmeli), wgpu GPU kompozitör. **Yerleşik CLI + JSON kontrol kanalı + MCP sunucusu** ile ajandan doğrudan YouTube thumbnail şablonu üretebilir (erken alpha). |
| **Graphite** | [GraphiteEditor/Graphite](https://github.com/GraphiteEditor/Graphite) (Apache-2.0) | 28.0k | Rust | **Düğüm (node) tabanlı 2D grafik + prosedürel motion graphics.** Tekrarlanabilir, parametrik thumbnail ve kanal grafiği sistemleri için ideal. |
| **GIMP 3 + PhotoGIMP** | GNU (GPL) + [Diolinux/PhotoGIMP](https://github.com/Diolinux/PhotoGIMP) | Olgun | C | **Üretimde en olgun Photoshop alternatifi.** GIMP 3 modern katman/HiDPI desteği getirir; `PhotoGIMP` yaması Photoshop kısayollarını verir; **`CLI-Anything`** (`cli-anything-gimp`) ile ajandan yönetilebilir. |
| **Krita & Inkscape** | KDE / GNU (GPL) | Olgun | C++ | İllüstrasyon (Krita) ve vektör/logo (Inkscape). İkisi de `CLI-Anything` (`cli-anything-krita`, `cli-anything-inkscape`) ile tam offline ajan kontrolüne sahip. |

---

## 3. `HKUDS/CLI-Anything` (62.5k★) — Tüm Masaüstü Yazılımlarını Ajana Açan Köprü

`CLI-Anything`, GUI uygulamalarını (Kdenlive, Shotcut, OBS, Audacity, GIMP, Krita, Inkscape, Blender, ComfyUI) ajanların JSON çıktı veren CLI/REPL üzerinden sürebilmesi için standartlaştırır:

* **Video Üretim Matrisi (`cli-hub-matrix/video-creation`):** Sabit boru hattı yerine yetenek (capability) bazlı seçim yapar; her ciddi video öncesi `creative_direction.md`, her internet B-roll'u için `sources.json` lisans kaydı ve final öncesi `video_doctor.py` (probe, caption, audio, tail, frame) denetim disiplinini zorunlu kılar.
* **Görsel Tasarım Matrisi (`cli-hub-matrix/image-design`):** `thumbnail-set` reçetesi (hero görsel → `rembg` arka plan temizliği → `cli-anything-gimp` / `Pillow` tipografi ve yerleşim → toplu varyant export).

---

## 4. Pratik Üretim Tavsiyesi

1. **Bugün Günlük Üretim (%95 iş yükü):** `FFmpeg` + `DeepFilterNet` + `auto-editor` + `OBS` + `Pillow/ASS` (hızlı, hatasız, %100 deterministik).
2. **İleri Görsel / Thumbnail İhtiyacında:** Manuel dokunuş gerekirse **Kdenlive** + **GIMP 3**; ajanla doğrudan PSD thumbnail ve katmanlı grafik için **PhotoCraft** (veya `Pillow`/`HTML→PNG` + `CLI-Anything`).
3. **Gelecek Takip Listesi:** **FilmCraft** ve **OpenCut** Rust yeniden yazımı olgunlaştıkça doğrudan MCP üzerinden tam timeline montajına geçiş yapılabilir.

İlgili rehberler: [[ARCHITECTURE]], [[references/mcp-catalog|mcp-catalog]], [[references/awesome-video-skills|awesome-video-skills]].
