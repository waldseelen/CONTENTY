---
name: video-edit-core
title: Çekirdek Video Kurgu, FFmpeg Kontratları ve Kalite Kapıları
date: 2026-11-22
description: browser-use/video-use, kajisho5/ffmpeg-skill (42 araç) ve KyaniteLabs/kinocut (206 araç) projelerinden sentezlenen yerel, ücretsiz, ajan-kontrollü video kurgu kılavuzu.
tags:
  - skill
  - video-editing
  - ffmpeg
  - kinocut
  - edl
---

# Çekirdek Video Kurgu (`video-edit-core`)

Bu skill üç doğrulanmış açık kaynak repodan birleştirilmiştir:
* **Kurgu felsefesi & EDL doğruluk kuralları:** [browser-use/video-use](https://github.com/browser-use/video-use) (31.4k★, MIT)
* **42 deterministik yerel FFmpeg aracı & tuzaklar:** [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) (9.5k★, MIT)
* **Güvenlik bariyerli MCP, katmanlı kompozisyon & kalite kapıları:** [KyaniteLabs/kinocut](https://github.com/KyaniteLabs/kinocut) (278★, Apache-2.0)

---

## 1. Standart Çalışma Protokolü (Sırayı Bozma)

1. **Envanter & İnceleme (`probe`):** Önce `ffprobe` / `probe.py` / `kino --format json info <dosya>` çalıştır. Süre, çözünürlük, FPS (VFR mi CFR mi?), renk uzayı (SDR/HDR/Log) ve ses kanallarını gerçek sayıdan oku.
2. **Transkript Önbellekleme:** Kelime-zamanlı (word-level verbatim) transkript çıkar ve `02-cleaned/transcripts/` altına kaydet. Kaynak dosya değişmedikçe asla yeniden transkribe etme.
3. **Planla ve Onay Al:** Kesim listesini (`edl.json` veya `edit-plan.md`) düz Türkçe özetle sun (eski süre → yeni süre, çıkarılan kısımlar, tempo). Kullanıcı onaylamadan final render alma.
4. **Zincir Sırası:** `renk/HDR düzeltme → kesim → birleştirme → sessizlik budama → kadraj/boyut (16:9 veya 9:16) → görsel/overlay → altyazı (EN SON!) → ses/loudness (-14/-16 LUFS) → export`.
5. **Kendi Çıktını Doğrula:**
   * `ffprobe` ile çıktı süresi + A/V senkron kontrolü.
   * `ffmpeg -i final.mp4 -af ebur128=peak=true -f null -` ile gerçek LUFS + true peak ölçümü.
   * Kesim sınırlarından ve video başı/ortası/sonundan temas sayfası (`look.py --tiles 3x2`) çıkarıp görsel inceleme yap.
   * En fazla 3 öz-düzeltme turu yap; sorun sürerse kullanıcıya raporla.

---

## 2. EDL (Edit Decision List) Şeması (`video-use` Standardı)

Tüm kurgu kararları okunabilir, yeniden üretilebilir JSON olarak `workspace/04-metadata/<proje>-edl.json` içine yazılır:

```json
{
  "version": 1,
  "sources": {
    "RAW_01": "workspace/01-raw/yayin_01.mp4"
  },
  "ranges": [
    {
      "source": "RAW_01",
      "start": 12.40,
      "end": 58.85,
      "beat": "HOOK",
      "quote": "Felsefe neden teknoloji olmadan yarım kalır?",
      "reason": "Temiz giriş, 59.1s'deki duraksama öncesi kesildi."
    }
  ],
  "grade": "none",
  "overlays": [
    {
      "file": "workspace/02-cleaned/slot_1.mp4",
      "start_in_output": 4.0,
      "duration": 6.0
    }
  ],
  "subtitles": "workspace/03-exports/master.srt",
  "total_duration_s": 46.45
}
```

---

## 3. 42 FFmpeg Aracı Hızlı Yönlendirme Tablosu (`ffmpeg-skill`)

Python 3.10+ (yalnızca stdlib) ve FFmpeg 6.1+ ile çalışan deterministik komutlar (hepsi `--dry-run --json` destekler):

| İstek | Komut / Araç |
| :--- | :--- |
| Dosya bilgisi + Log/HDR analizi | `probe.py in.mp4 --analyze` |
| Kesme / segment çıkarma (GOP-akıllı) | `cut.py in.mp4 --segments 0-1:00,1:30-2:00 --smart` |
| Sessizlik & dolgu kelimesi kesimi | `silence.py in.mp4 --speech-aware --filler --words words.json` |
| Uzun yayından en enerjik kesitler | `scenes.py long.mp4 --highlights 6 --target 60 --edl picks.txt` |
| 9:16 dikey / kare dönüşüm | `fit.py in.mp4 --aspect 9:16 --width 1080 --fit crop` (`pad` veya `blur`) |
| B-roll bindirme | `broll.py talk.mp4 --insert broll.mp4 --at 12 --end 16 --audio mix` |
| Alt bant / hook kartı / meme yazısı | `graphics.py in.mp4 --template lower-third --name "Channel Title"` |
| Altyazı gömme / karaoke pop | `caption.py in.mp4 --srt subs.srt --max-lines 2` (`--animate pop --karaoke`) |
| Podcast → Audiogram videosu | `render.py --template audiogram ep.m4a --image cover.png` |
| Dalga formu (waveform) videosu | `waveform.py ep.wav -o waveform.mp4` |
| Ses temizliği & müzik ducking | `audio.py in.mp4 --voice` / `audio.py in.mp4 --music bed.mp3 --duck --fade-out 3` |
| Loudness mastering (-14 LUFS) | `loudness.py in.mp4 --versions streaming` |
| J-cut / L-cut birleştirme | `join.py a.mp4 b.mp4 --transition none --audio-lead 0.5` |
| Bölüm (chapter) & metadata gömme | `metadata.py ep.mp4 --chapters chapters.txt --title "..."` |
| Platforma uygun export | `export.py in.mp4 --preset youtube` (`reels`, `shorts`, `gif`) |
| Yükleme öncesi teknik denetim | `check.py final.mp4 --platform youtube` (veya `reels`) |
| Görsel kontrol temas sayfası | `look.py out.mp4 --tiles 3x2 --guides title,action` |
| Çok adımlı önbellekli proje | `render.py project.json --cache ./cache` (`--export-timeline edit.fcpxml`) |

---

## 4. Kinocut Guardrailed MCP & Katmanlı Kompozisyon

`kinocut` (`uvx kinocut==2.0.1`), ajanın ham FFmpeg komutu uydurmasını engelleyen ve her adımda doğrulama makbuzu (`receipt`) üreten 206 araçlık MCP sunucusudur:

* **Önerilen MCP Profili:** `KINOCUT_TOOLS=profile:editor` (varsayılan 18 araçlık kompakt yüzey de `list_operations` + `describe_operation` üzerinden tüm 206 araca ulaşır).
* **Katmanlı Kompozisyon (`composite_layers`):** Arka plan + B-roll + alt bant + PiP + maske katmanlarını JSON şemasıyla kurar (`--dry-run --save-layer-plan` ile önce doğrulanır).
* **Yayın-Öncesi Bariyerler:** `video_quality_check` (varsayılan 80 puan altı fail-closed) + `video_release_checkpoint` geçmeden teslimat yapılmaz.
* **Kayıtlı Yayın Shorts Akışı:** `kino shorts-plan-show` → `kino shorts-review --decision approve` → `kino shorts-render` → `kino shorts-package`.

---

## 5. Kritik FFmpeg Tuzakları (`gotchas.md` Özeti)

> [!CAUTION] "Çalıştı" Görünüp Bozuk Çıktı Veren Durumlar
> * **VFR (Değişken Kare Hızı):** OBS veya telefon kayıtlarında `-c copy` ile kesim ses/görüntü kayması veya donuk başlangıç karesi yaratır → `fps` filtresiyle CFR'ye çevir.
> * **Crop Öncesi Altyazı:** 16:9 videoya önce altyazı gömüp sonra 9:16 kırparsan yazılar kesilir. Önce `1080x1920` yap, sonra altyazı göm.
> * **HDR → SDR Düzleşmesi:** HDR/BT.2020 kaynak doğrudan SDR olarak kodlanırsa renkler solar → önce ton eşleme (`--to-sdr`) uygula.
> * **True Peak Kırpması (Clipping):** `-14 LUFS` normalizasyon tek başına kırpmayı engellemez; true peak mutlaka `≤ -1.0 dBTP` kontrol edilir.
> * **Sessiz Ortam Yükseltme:** `-40 LUFS` altındaki oda gürültüsünü konuşma hedefine çekmek yalnızca dip gürültüyü patlatır.
> * **Windows `drawtext` Font Çökmesi:** Windows FFmpeg derlemelerinde aile adı yerine açık `--font-file` yolu (`C:/Windows/Fonts/...`) ver.

---

## 6. Yerel JSON → MLT Kurgu Hattı (`mltgen.py` & `vrender.sh`)

Kaba kesim + HyperFrames grafik kliplerini Kdenlive/Shotcut uyumlu `.mlt` projesine çevirmek ve başsız (headless) render almak için:

1. `templates/edit.json` şablonunu iş klasörüne kopyalayıp `cut/*.mp4`, `graphics/*.mp4` ve arka plan müziğini tanımla (`brand/presets/youtube-16x9.json` ile uyumlu).
2. MLT XML üret:
   ```bash
   python3 scripts/mltgen.py edit.json project.mlt --base "$STUDIO_JOBS/<proje>"
   ```
3. Önce hızlı taslak üret (**Yönetmen Onay Kapısı** — onay gelmeden final render alma), onay sonrası master render al:
   ```bash
   ./scripts/vrender.sh project.mlt draft.mp4 fast
   ./scripts/vrender.sh project.mlt final.mp4 quality   # libx264 CRF 18 slow
   ```
4. İstersen aynı `project.mlt` dosyasını Kdenlive veya Shotcut içinde açıp elle ince ayar (hybrid finishing) yap.

> [!NOTE] Atölye Düzeni & Tek Render Kuyruğu
> Çoklu paralel ajanla çalışırken **tek şef** dosya sözleşmelerini yönetir ve render komutları sırayla (tek kuyruk) çalıştırılır. Ayrıntı için: [[skills/ajanla-video-kurgu/SKILL|ajanla-video-kurgu]].

İlgili rehberler: [[skills/audio-and-roughcut/SKILL|audio-and-roughcut]], [[skills/faceless-and-shorts/SKILL|faceless-and-shorts]], [[skills/ajanla-video-kurgu/SKILL|ajanla-video-kurgu]], [[ARCHITECTURE]].
