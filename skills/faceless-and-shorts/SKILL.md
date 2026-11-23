---
name: faceless-and-shorts
title: Yüzsüz (Faceless) Video, Dikey Shorts Kesimi, Türkçe Altyazı ve Audiogram
date: 2026-11-22
description: Yüzsüz anlatımlar, OBS yayınından 9:16 Shorts çıkarımı, yerel Türkçe Whisper altyazı, ASS güvenli alanları ve Podcast→Video reçetesi.
tags:
  - skill
  - faceless
  - shorts
  - subtitles
  - whisper
  - audiogram
---

# Yüzsüz Anlatım, Shorts & Altyazı (`faceless-and-shorts`)

Bu skill `video-use`, `ffmpeg-skill`, `kinocut-repurpose`, `CLI-Anything` (`video-creation` matrisi) ve `claude-youtube-editor` repolarından **yüzsüz (faceless) + OBS yayın özeti + podcast** formatları için sentezlenmiştir.

---

## 1. Yüzsüz Video (Faceless) Görsel Motor Seçici

Her sahne için aynı aracı zorlamak yerine içeriğe göre en hafif ve en temiz açık kaynak motoru seç:

| Sahne Türü | En İyi Açık Kaynak Motor | Ne Zaman Kullanılır |
| :--- | :--- | :--- |
| Alıntı kartı, sayaç, başlık, daktilo yazısı | **PIL + PNG + FFmpeg** (`overlay.py`, `graphics.py`, `insert.py`) | En hızlı; Node.js gerekmez. Ken Burns (`--zoom in --pan right`) ile durağan görsele hareket verir. |
| Felsefi kavram haritası, teknik diyagram, grafik, tarih/sistem akışı | **Manim** (`manim-video` / `adithya-s-k/manim_skill`) | 3Blue1Brown tarzı net diyagram ve denklem/sistem dönüşümleri. |
| Modern kinetik tipografi, haber/makale/UI ekranı, veri hikâyesi | **HyperFrames** (HTML/CSS/GSAP) | Saf web bileşenleriyle deterministik kare yakalama + şeffaf WebM overlay. |
| Yeniden kullanılabilir kanal bileşen şablonları | **Remotion** (React/TSX) | Bir kez tasarlanan kanal şablonunu (`brand.ts`) her videoda tekrar kullanmak için. |
| Kamu malı / telifsiz B-roll arşivleri | **Wikimedia Commons + CC0 + `broll.py`** | Her indirilen klip için `sources.json` (URL, lisans, atıf metni) tutulur. |
| Podcast / ses odaklı bölüm | **FFmpeg Audiogram (`waveform.py` / `render.py --template audiogram`)** | Kapak görseli + canlı ses dalga formu + bölüm başlığı + altyazı. |

### Yüzsüz Görsel Altın Kuralları (`video-use` & `CLI-Anything`)
* **Önce `creative_direction.md`:** Ciddi bir yüzsüz videoda kurgudan önce tek cümlelik vaat, duygusal eğri, bölüm tablosu (zaman, konu, görsel rolü, ses olayı) ve kapanış vurgusu yazılır.
* **Söz-Görüntü Senkronu (Payoff Timing):** Vurucu kelimenin zaman damgası alınır; grafik animasyonu `reveal_duration` saniye önce başlatılır ki son karesi tam o kelimede otursun.
* **Son Kare Tutma:** Her bilgi kartı veya diyagram kesimden önce en az **`≥ 1.0 s`** sabit tutulur.
* **Aynı Anda Tek Yeni Öğe:** Ekranda iki bağımsız görsel/metin aynı anda açılmaz; izleyici gözü takip edemez.
* **Linear Easing Yasak:** Tüm hareketlerde `ease_out_cubic` veya `ease_in_out_cubic` kullanılır.
* **Veri/Metin Üstünde Yapay Sallantı Yasak:** Grafik, harita ve alıntı okunurken sahte el kamerası sallantısı eklenmez.

### HyperFrames Deterministik Kompozisyon Sözleşmesi & Tuzaklar
* **Marka Kaynağı:** Üretim öncesi `brand/frame.template.md` dosyasından kilitlenen `brand/frame.md` okunur (anti-AI-slop: neon, mor gradyan, glassmorphism, 3D parlama yasak).
* **Seek-Safe GSAP Zaman Çizelgesi:** `#root` üzerinde `data-composition-id="main"`, `data-start`, `data-duration`, `data-width`, `data-height`; zamanlı elemanlarda `class="clip"` tanımlanır. Tek duraklatılmış timeline (`window.__timelines["main"] = gsap.timeline({paused:true})`) kaydedilir; `fromTo`/`set` kullanılır.
* **Sıfır Rastgelelik:** `Date.now()`, `Math.random()` ve canlı `fetch` yasaktır. SVG `feTurbulence` kağıt dokusunda mutlaka **sabit `seed`** verilir, yoksa kareler titrer (flicker).
* **Tam Ekran Cutaway Yerine Şeffaf Overlay:** Ekran kaydında yararlı içerik varken ekranı tamamen kapatma; `--format mov` (veya `webm`) şeffaf overlay kullan. Tam ekran cutaway yalnızca giriş, çıkış ve boş geçişlerde kullanılır.
* **Bindirme Zaman Kaydırması:** `ffmpeg` ile her sahneyi kendi zaman koduna oturturken `[i:v]setpts=PTS+{START}/TB[ovi]` ardından `overlay=enable='between(t,{START},{END})':eof_action=pass` uygulanır.
* **Maskot Arka Plan Temizliği:** Açık krem/tek renk plakadan maskot ayıklamak için HSV eşikleme (`s < 0.22 & v > 0.60`) veya flood-fill RGBA maskeleme kullanılır.
* **Dikey Motion İlkesi:** Shorts/Reels için yatay sahneyi zorla kırpmak yerine kritik motion sahnelerini baştan `1080×1920` dikey kur.
* **Hafıza & Hikâye Entegrasyonu:** Marka/sahne hafızası için [[skills/video-motoru/SKILL|video-motoru]], retention/hikâye omurgası için [[skills/video-prompt-builder/SKILL|video-prompt-builder]] kullanılır.

---

## 2. Uzun Yayından / Podcastten 9:16 Dikey Shorts Boru Hattı

### Aşama 1 — Aday Kesit Bulma
* **Canlı Yayında:** OBS Replay Buffer (`save_replay_buffer`) veya `create_record_chapter` ile işaretlenen anlar doğrudan önceliklidir.
* **Kayıt Sonrası:**
  * Metin tabanlı (en doğru): Kelime-zamanlı transkriptten 35–58 saniyelik **kendi başına anlamlı** (kanca + argüman + vurucu kapanış) 3–5 blok seçilir.
  * Enerji/ses tabanlı hızlı tarama: `scenes.py long.mp4 --highlights 5 --target 55 --edl picks.txt` (sadece ses yüksekliğine bakar; mutlaka transkriptle teyit edilir).

### Aşama 2 — 9:16 Kadrajlama (1080×1920)
16:9 yatay videoyu dikeye çevirirken 3 güvenli strateji:
1. **`crop`:** Merkezde tek odak varsa (16:9 → 9:16 genişliğin %70'ini atar, önemli yazıları kesme!).
2. **`blur` (Yüzsüz & Ekran Kaydı için Önerilen):** Yatay içeriği bozmadan ortaya yerleştirir, üst/alt boşluğu bulanık arka planla doldurur (`fit.py in.mp4 --aspect 9:16 --width 1080 --fit blur`).
3. **`split` / `pad`:** Üst yarıda görsel/ekran, alt yarıda dalga formu + büyük altyazı.

### Aşama 3 — Platform Güvenli Alanları (Safe Zones)
> [!WARNING] YouTube Shorts / Reels / TikTok Arayüz Çakışması
> * **Alt %20** (kanal adı, başlık, ses bandı) ve **sağ sütun** (beğeni/yorum/paylaşım butonları) platform arayüzü tarafından örtülür.
> * Dikey altyazıları ve ana metinleri mutlaka güvenli orta-alt bölgeye (`MarginV` yüksek) yerleştir ve `look.py --safe tiktok` ile doğrula.

### Aşama 4 — `kinocut` ile Toplu Shorts Paketleme
```bash
kino repurpose-plan workspace/02-cleaned/kesit.mp4 --platforms youtube-shorts instagram-reel tiktok -o workspace/03-exports/shorts
kino repurpose workspace/02-cleaned/kesit.mp4 --platforms youtube-shorts instagram-reel tiktok -o workspace/03-exports/shorts
kino video-quality-check workspace/03-exports/shorts/youtube_shorts.mp4
```

---

## 3. Yerel Türkçe Altyazı (`faster-whisper`) & ASS Kuralları

### Transkripsiyon Kuralları
* **Model Seçimi:** Türkçe için asla `.en` modeli kullanma (İngilizceye çevirir). Çok dilli **`faster-whisper`** (`small` hızlı taslak, `medium` veya `large-v3-turbo` yüksek doğruluk) + `--language tr` + `--word_timestamps True` kullan.
* **Özel İsim & Terim Düzeltme:** Felsefe/teknoloji/politika terimlerini (`Nietzsche`, `Kubernetes`, `Antigravity` vb.) Whisper initial prompt / terim listesiyle ver ki yanlış yazılmasın.

### İki Ayrı Altyazı Çıktısı Üret
1. **Uzun YouTube Videosu (16:9):**
   * Videoya gömme (burn-in) yapma; harici **`captions.srt`** üret ve YouTube API (`youtube-uploader-mcp` → `update_video`) ile yükle (izleyici açıp kapatabilir, YouTube SEO için indeksler).
   * Satır kuralı: En fazla **2 satır × 42 karakter**, her ekran **1–7 saniye**, özel isim ortasından bölme yok.
2. **Dikey Shorts / Reels (9:16):**
   * Sessiz izleme oranı yüksek olduğu için **ASS formatında gömülü (burn-in)** altyazı üret.
   * Satır kuralı: 2–3 kelimelik vurucu bloklar, maks 32 karakter, beyaz kalın yazı + siyah dış çizgi (`Outline=2`) + hafif gölge.
   * **ASS `PlayResX`/`PlayResY` Kuralı:** `PlayResX: 1080` ve `PlayResY: 1920` değerleri final render çözünürlüğüyle birebir eşleşmelidir.
   * **Türkçe Glif Kontrolü:** `ç, ğ, ı, İ, ö, ş, ü` karakterlerini destekleyen açık font dosyası (`Noto Sans`, `Inter`, `Montserrat`, `Poppins` veya `C:/Windows/Fonts/segoeui.ttf`) kullan ve temas sayfasında kontrol et.

---

## 4. Otomatik YouTube Bölüm Zaman Damgaları (`chapters.txt`)

YouTube'da bölümlerin (chapters) aktif olması için uyulması zorunlu teknik kurallar:
* İlk bölüm mutlaka **`00:00`** ile başlamalıdır.
* En az **3 bölüm** olmalıdır.
* Her bölüm en az **10 saniye** sürmelidir (`edit_video.py` 10 saniye altı uyarısı verir).
* Zaman damgaları kesim sonrası **final video zaman çizelgesine** göre hesaplanır, ham kayda göre değil.

---

## 5. Vurucu Kesit Puanlama & Otomatik Highlight Tespiti
* **Otomatik Ses Piki + Sahne Değişimi Tespiti (`lxgic-clipper` MIT):**
  ```bash
  ./scripts/detect_highlights.sh 01-raw/yayin.mp4 70
  ```
* **5 Boyutlu Short Puanlama Rubriği & Platform Safe-Zone:**
  * Puanlama ağırlıkları (`Hook 0.30 + Coherence 0.25 + Emotion 0.20 + Value 0.15 + Payoff 0.10`, eşik `>= 60`): `skills/faceless-and-shorts/references/scoring-rubric.md`
  * TikTok / Reels / YouTube Shorts güvenli alan ölçüleri: `skills/faceless-and-shorts/references/platform-specs.md`
  * Kinetik altyazı stilleri: `skills/faceless-and-shorts/references/caption-styles.md`

İlgili rehberler: [[skills/video-edit-core/SKILL|video-edit-core]], [[skills/audio-and-roughcut/SKILL|audio-and-roughcut]], [[references/awesome-video-skills|awesome-video-skills]].
