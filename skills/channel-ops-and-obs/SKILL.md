---
name: channel-ops-and-obs
title: OBS Canlı Yayın Kontrolü ve YouTube Kanal Operasyonları
date: 2026-11-22
description: xDarkzx/OBS_MCP (148 araç), anwerj/youtube-uploader-mcp (Go) ve pauling-ai/youtube-mcp-server (40 araç) ile canlı yayın, kayıt ve kanal yönetimi otomasyonu.
tags:
  - skill
  - obs
  - youtube-ops
  - mcp
  - livestream
---

# OBS Kontrol & Kanal Operasyonları (`channel-ops-and-obs`)

Bu skill canlı yayın/kayıt sürecini ([xDarkzx/OBS_MCP](https://github.com/xDarkzx/OBS_MCP)) ve YouTube yayınlama/analitik/SEO süreçlerini ([anwerj/youtube-uploader-mcp](https://github.com/anwerj/youtube-uploader-mcp), [pauling-ai/youtube-mcp-server](https://github.com/pauling-ai/youtube-mcp-server)) tek operasyonda birleştirir.

---

## 1. OBS Studio Hazırlık & WebSocket Bağlantısı

OBS Studio v28+ içinde WebSocket sunucusu yerleşik gelir (ek eklenti gerekmez, tamamen yerel `localhost:4455`):
1. OBS Studio → **Araçlar (Tools) → WebSocket Sunucu Ayarları**.
2. **WebSocket sunucusunu etkinleştir** kutusunu işaretle (Port: `4455`).
3. Güçlü bir şifre belirle (veya tek PC yerel kullanım için boş bırak).
4. **Kayıt Formatı Önerisi:** Ayarlar → Çıkış → Kayıt Biçimi olarak **Hybrid MP4** (veya MKV) seç.
   * **Hybrid MP4 avantajı:** Elektrik/çökme korumalıdır, FFmpeg ile hemen işlenir ve OBS'nin canlı **`create_record_chapter`** bölüm işaretleme aracını destekler!
5. **Çoklu Ses Kanalı (Multi-Track Audio):**
   * Track 1: Karışık yayın sesi (Mikrofon + Masaüstü)
   * Track 2: Yalnızca Mikrofon (kayıt sonrası `DeepFilterNet` + `auto-editor` için tertemiz!)
   * Track 3: Yalnızca Masaüstü / Müzik / Konuk sesi

---

## 2. OBS_MCP Kritik Araç Seti (148 Araçtan En Yüksek Değerliler)

### Yayın / Kayıt Öncesi Otomatik Kurulum
| Araç | Görevi |
| :--- | :--- |
| `set_record_directory("workspace/01-raw")` | Tüm ham kayıtları doğrudan stüdyo giriş klasörüne yazar (tam mutlak yol ver). |
| `clean_audio_input(input_name="Mic/Aux")` | Tek çağrıda doğrulanmış OBS **Noise Gate → RNNoise → Compressor** zincirini kurar. |
| `diagnose_av_health()` | CPU, GPU render-skip, encoder-skip, ağ tıkanıklığı ve boş disk alanını yorumlar. |
| `get_scene_list()` / `set_current_program_scene(name)` | Sahne kontrolü (Başlıyor, Ana Ekran, Podcast, Ara, Kapanış). |
| `get_source_screenshot(source_name, "png")` | Ajanın yayında ekranda ne göründüğünü bizzat görmesini sağlar. |

### Yayın / Kayıt Sırasında Akıllı Kısayollar
| Araç | Görevi |
| :--- | :--- |
| `start_record()` / `stop_record()` | Kaydı başlatır/durdurur (`stop_record` kaydedilen tam dosya yolunu döner). |
| `create_record_chapter("Felsefe: Determinizm")` | Hybrid MP4 kaydına canlı bölüm damgası düşer → sonra otomatik YouTube chapter olur. |
| `start_replay_buffer()` / `save_replay_buffer()` | Son 60–90 saniyeyi anlık Shorts klibi olarak diske yazar (`get_last_replay_buffer_replay`). |
| `split_record_file()` | Uzun yayında yeni konuya geçerken kaydı kesintisiz yeni dosyaya böler. |

---

## 3. YouTube Paketleme & Yayınlama Protokolü

Her video yüklemeden önce `workspace/04-metadata/<proje>-publish.json` dosyası hazırlanır ve kullanıcı onayına sunulur:

### Paketleme Standartları
1. **Başlık:** 55–70 karakter arası, ana merak kancası ilk 40 karakterde, yapay tık tuzağı yok (kanala özgü keskin, zekice, sorgulayıcı ton).
2. **Thumbnail (3 Varyant A/B Adayı):** `1280x720`, `< 2 MB`, mobilde okunabilir maks 3–4 kelime yüksek kontrast tipografi. Ayrıntılı kanca (hook) matrisi, maskot güvenliği ve üretim akışı için: [[skills/thumbnail-factory/SKILL|thumbnail-factory]]. Açık kaynak üretim: `PhotoCraft` (Rust MCP), `Graphite`, `GIMP 3 + CLI-Anything` veya `Pillow/HTML→PNG`.
3. **Açıklama Şablonu:**
   * İlk 2 satır: İzleyicinin bu videodan alacağı ana fikir (YouTube "Daha fazla göster" katlamasının üstü).
   * Kaynaklar & Okuma Listesi (felsefe/teknoloji/politika atıfları).
   * `00:00` ile başlayan **Bölüm Zaman Damgaları** (`chapters.txt`).
4. **Etiketler & Kategori:** `youtube_search_suggestions` (0 kota maliyeti!) ile gerçek Türkçe arama sorgularından türetilmiş 10–15 etiket.

### Yükleme Sırası (MCP)
1. `upload_video` → `privacy_status: "private"`, başlık, açıklama, etiketler, `default_language: "tr"`.
2. `update_video` → özel thumbnail (`<2 MB`), Türkçe `captions.srt` altyazı dosyası, uygun oynatma listesi (örn. *Felsefe*, *Teknoloji*, *Politika*, *Canlı Yayın Özetleri*).
3. **İnsan Onayı:** YouTube Studio'da son önizleme → tek tıkla `Herkese Açık` veya zamanlama.

---

## 4. Yayın Sonrası Analitik Döngüsü (`youtube-mcp-server`)

Yayın sonrası 48 saat ve 7. günde ajandan şu kontroller istenir (kota dostu):
* `youtube_analytics_video_detail` — İzlenme, ortalama izlenme süresi, beğeni/yorum oranı.
* `youtube_analytics_retention` — İzleyicinin hangi saniyede çıktığını bul → sonraki videonun giriş kancasını ve kesim ritmini ona göre iyileştir.
* `youtube_analytics_content_type_breakdown` — Uzun video vs Shorts vs Canlı Yayın performans kıyaslaması.
* `youtube_analytics_traffic_sources` — Keşfet / Arama / Önerilen oranlarına göre başlık & thumbnail kalibrasyonu.

İlgili rehberler: [[YOUTUBE_API_GUIDE]], [[references/mcp-catalog|mcp-catalog]], [[ARCHITECTURE]].
