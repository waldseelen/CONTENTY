---
name: audio-and-roughcut
title: Stüdyo Ses Temizliği, Mastering ve Otomatik Kaba Kurgu
date: 2026-11-22
description: DeepFilterNet, Auto-Editor ve video-editing-skill kurallarıyla yüzsüz anlatım, OBS yayını ve podcast kayıtları için ses temizliği ve kaba kesim boru hattı.
tags:
  - skill
  - audio
  - deepfilternet
  - auto-editor
  - podcast
  - lufs
---

# Ses Temizliği & Kaba Kurgu (`audio-and-roughcut`)

Yüzsüz (faceless) videolarda ve podcastlerde **ses = ürün**. İzleyici zayıf görseli affeder ama dip gürültülü, patlayan veya uzun sessizlikli sesi 10 saniyede kapatır.

Kaynak projeler:
* [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) (5.1k★, Rust/Python — tam bant 48 kHz yapay zekâ gürültü temizliği)
* [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) (6.0k★, Nim, Unlicense — ultra hızlı sessizlik/hareket kesici)
* [social-media-skills/video-editing-skill](https://github.com/social-media-skills/video-editing-skill) (MIT — konuşma ritmi, dolgu kesimi ve `-14`/`-16 LUFS` ses zinciri)

---

## 1. İki Katmanlı Ses Temizliği Stratejisi

### Katman A — Kayıt Anında (OBS Canlı Yayın)
`OBS_MCP` içindeki `clean_audio_input(input_name="Mic/Aux")` tek çağrıda şu sırayı OBS filtrelerine uygular:
1. **Noise Gate** (konuşma yokken mikrofonu kapatır)
2. **Noise Suppression — RNNoise** (klavye, fan, oda uğultusunu canlı keser)
3. **Compressor** (bağırma ve fısıldama arasındaki uçurumu dengeler)

### Katman B — Kayıt Sonrası (Offline Stüdyo Kalitesi: `DeepFilterNet`)
`DeepFilterNet` pre-compiled **tek Rust binary (`deep-filter.exe`)** olarak Python kurmadan çalışır. Şart: Girdi **`48 kHz WAV`** olmalıdır.

```powershell
# 1) Videodan veya ham kayıttan 48kHz mono/stereo WAV çıkar
ffmpeg -i "workspace/01-raw/kayit.mp4" -vn -ar 48000 -ac 1 -c:a pcm_s16le "workspace/02-cleaned/raw_48k.wav"

# 2) DeepFilterNet ile dip gürültü temizliği (-D gecikme telafisi, --pf post-filter)
deep-filter -D --pf -o "workspace/02-cleaned" "workspace/02-cleaned/raw_48k.wav"
```

---

## 2. Yayın & Podcast Mastering Zinciri (FFmpeg)

`DeepFilterNet` sonrası ses, yayın standartlarına şu sırayla getirilir (`video-editing-skill` + `video-use` birleşik zinciri):

1. **80 Hz High-Pass Filtresi (`highpass=f=80`):** Mikrofon sehpası titremesi, klima uğultusu ve patlamalı "p/b" alt frekanslarını keser.
2. **Hafif Sıkıştırma (`acompressor` — 3:1 oran):** Konuşmayı dolgun ve tutarlı tutar.
3. **Peak Limiter (`alimiter`):** Anlık piklerin `-1.0 dBTP` üstüne çıkıp patlamasını (clipping) önler.
4. **İki Geçişli EBU R128 Loudness (`loudnorm`):**
   * **YouTube Uzun Video & Shorts:** `-14 LUFS`, `LRA=11`, `TP=-1.0 dBTP`
   * **Podcast / Uzun Sohbet:** `-16 LUFS`, `LRA=11`, `TP=-1.0 dBTP`

```powershell
# İki geçişli mastering (örnek: YouTube -14 LUFS)
# 1. Geçiş: ölçüm al (measured_I, measured_LRA, measured_TP, measured_thresh)
ffmpeg -i "workspace/02-cleaned/raw_48k.wav" ^
  -af "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=50,loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json" ^
  -f null -

# 2. Geçiş: linear=true ile şeffaf final mastering (ölçülen değerlerle)
ffmpeg -i "workspace/02-cleaned/raw_48k.wav" ^
  -af "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=50,loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=-18.4:measured_LRA=7.2:measured_TP=-2.1:measured_thresh=-28.9:linear=true" ^
  -ar 48000 -c:a pcm_s16le "workspace/02-cleaned/master_voice.wav"
```

### Müzik Altlığı (Ducking) Kuralları
* Arka plan müziği konuşma altında **-12 ila -15 dB** bastırılır (ducking).
* Müzik asla tek düze loop halinde baştan sona gitmez; bölüm geçişlerinde nefes açılır veya kapanıştan önce yumuşakça sönümlenir (`afade`).
* Ham gürültü/sentetik drone müzik altlığı olarak kullanılmaz.

---

## 3. Kaba Kurgu (Rough Cut): Sessizlik, Dolgu ve Tekrar Kesimi

### Seçenek 1 — Sıfır Python ile Hızlı Kaba Kesim (`auto-editor`)
`auto-editor` (Nim standalone binary) saniyeler içinde ölü sessizlikleri keser veya açık kaynak editörlere zaman çizelgesi aktarır:

```powershell
# Standart YouTube / anlatım kaba kesimi (0.2s doğal pay, -19dB eşiği)
auto-editor "workspace/01-raw/kayit.mp4" --edit audio:-19dB --margin 0.2s -o "workspace/02-cleaned/rough.mp4"

# Konuşma öncesi kısa, sonrası nefes payı (podcast için daha doğal)
auto-editor "workspace/01-raw/podcast.mp4" --edit audio:-24dB --margin 0.3s,0.6s -o "workspace/02-cleaned/podcast_rough.mp4"

# Çok kanallı OBS kaydında yalnızca mikrofon kanalına (stream 0) göre kes
auto-editor "workspace/01-raw/obs_multitrack.mkv" --edit "audio:threshold=-22dB,stream=0" --margin 0.25s

# İleride Kdenlive / Shotcut açmak gerekirse doğrudan proje çıktısı
auto-editor "workspace/01-raw/kayit.mp4" --export kdenlive
```

### Seçenek 2 — Kelime-Zamanlı Akıllı Kesim Presetleri (`video-editing-skill`)
Yerel `faster-whisper` ile kelime-zamanlı transkript çıkarıldığında formata göre şu ritim hedefleri kullanılır:

| Parametre | `youtube` (Uzun Bilgi) | `tight` (Shorts / Reels) | `podcast` (Sohbet) |
| :--- | :---: | :---: | :---: |
| Kısaltılacak min. duraksama | `> 0.50 s` | `> 0.30 s` | `> 0.80 s` |
| Cümle içi bırakılan nefes | `0.30 s` | `0.22 s` | `0.40 s` |
| Cümle sonu bırakılan nefes | `0.45 s` | `0.25 s` | `0.60 s` |
| Uzun boşluk / geçiş nefesi | `0.90 s` | `0.50 s` | `1.00 s` |
| Kesmeye değer en küçük boşluk | `0.40 s` | `0.25 s` | `0.60 s` |
| Hedef Loudness | **`-14 LUFS`** | **`-14 LUFS`** | **`-16 LUFS`** |

### Kesim Kalitesi & Transkript Tabanlı Sıra Kuralları
* **Önce Tekrar (Flub), Sonra Sessizlik:** Tekrar zaman kodları ham kayda (`01-raw`) göredir. Bu yüzden **önce** onaylı tekrar/hata aralıklarını `ffmpeg` `select`/`aselect` filtresiyle kes, **sonra** sessizlik budamasına (`./scripts/autocut.sh` veya `python3 scripts/remove-silence.py`) geç.
* **`auto-editor` v29 `--cut-out` Hatası:** Çoklu `--cut-out a,b c,d` argümanında son aralığı girdi dosyası sanıp hata verebilir; içerik kesimlerinde her zaman `ffmpeg` `select='between(t,...)+...'` kullan.
* **`certifi` SSL Düzeltmesi:** `auto-editor` ve `mlx-whisper` indirmelerinde `CERTIFICATE_VERIFY_FAILED` hatasını önlemek için `SSL_CERT_FILE` ve `REQUESTS_CA_BUNDLE` değişkenlerini `certifi.where()` ile dışa aktar (`scripts/autocut.sh` ve `scripts/transcribe.py` bunu otomatik yapar).
* **ASR Terim Temizliği:** `python3 scripts/transcribe.py` sonrası transkriptteki özel ad hatalarını (`Claude` → `Cloud`, `HyperFrames` → `Hyper frames`) `brand/caption-corrections.example.json` şablonundan ürettiğin sözlükle düzelt.
* **Türkçe Dolgu Kelimeleri:** `eee`, `ııı`, `şey`, `yani` (yalnızca izole duraksama içindeyse; anlam taşıyan cümle içi kullanımlar kesilmez).
* **Tekrarlar (Retakes):** Konuşmacı cümleyi yarım bırakıp yeniden başlarsa **her zaman son temiz çekim** tutulur; şüpheli çiftler otomatik kesilmez, `edit-plan.md` içinde kullanıcı onayına bırakılır.
* **Tepki & Kahkaha Koruma:** Kahkaha, vurucu espri veya vurgu anlarının hemen sonrasından kesilmez; tepki nefesi korunur.
* **Tıkırtı Önleme:** Her kesim noktasında `4–30 ms` `afade` uygulanır.

### Sahne Bazlı TTS Süre Manifesti Sözleşmesi (`skill-tts` MIT)
Yerel TTS (Kokoro / Piper) ile sahne bazlı seslendirme üretildiğinde her sahnenin görsel süresi ses dosyasının gerçek süresinden türetilir; bunun için `manifest.json` standardı kullanılır:
```json
{
  "sample_rate": 24000,
  "duration": 9.476,
  "segments": [
    {"id": "01-hook", "file": "voiceover/01-hook.wav", "start": 0.0, "end": 1.647, "duration": 1.647}
  ]
}
```
HyperFrames (`gsap-motion` / `video-motoru`) ve `mltgen.py` bu `start` / `duration` değerlerini okuyarak ses-görüntü kaymasını sıfırlar.

İlgili rehberler: [[skills/video-edit-core/SKILL|video-edit-core]], [[skills/faceless-and-shorts/SKILL|faceless-and-shorts]], [[skills/ajanla-video-kurgu/references/06-ses-transkript|06-ses-transkript]], [[ARCHITECTURE]].
