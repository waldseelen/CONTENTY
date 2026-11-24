# CONTENTY Studio — Core Engine Agent Instructions

Bu depo jenerik, kanalsız (channel-agnostic) **ortak çekirdek üretim motorudur** (plugin, skill, MCP konfigürasyonu, script, şablon ve kalite kapıları).

## Çekirdek Sınırı ve Sahiplik
- **Tek Sahiplik:** `CONTENTY` (ortak motor), `SACMA` (kişisel kanal deposu) ve `sis` (çok kanallı üretim stüdyosu) depolarının tamamının teknik sahibi Buğra'dır.
- **Karışıklık Yasağı:** Hiçbir tek kanala özel strateji, marka kilidi, OAuth sırrı veya operatör kuralı (`SACMA` veya `sis`) `CONTENTY` içine yazılmaz. Tüketici depoları `CONTENTY`'yi `core/` Git alt modülü (submodule) olarak tüketir ve kendi kurallarını kendi depolarında izole tutar.
- **Döngüsel Submodule Yasağı:** `CONTENTY` içine asla tüketici depoları (`SACMA`, `sis`) alt modül olarak eklenmez.

## Keşif ve Başlangıç
1. Yeni bir üretim işi geldiğinde ilk olarak `skills/studio-router/SKILL.md` dosyasını oku ve `scripts/init_project.py` ile proje klasörünü kur.
2. İş akışı, ses, kurgu, grafik, hikâye, thumbnail ve yayın adımlarında ilgili `skills/<skill>/SKILL.md` dosyasını yükle.
3. Eklenti kurulumu için `plugins/contenty-studio/` altındaki manifesti ve `scripts/install_plugin.sh` betiğini kullan.

## Değişmez Üretim Kuralları
- **Yönetmen Kapısı:** Kullanıcı onaylamadan final render alma ve YouTube'a herkese açık yükleme yapma (`private` taslak kuralı).
- **Ağır Medya Disiplini:** Ham çekimler ve büyük ara çıktılar `$STUDIO_JOBS` veya yerel `workspace/` içinde kalır; orijinal ham kaydın üzerine yazılmaz.
- **Kesim & Altyazı Sırası:** Önce tekrar/flub kesimi (`ffmpeg select`), sonra sessizlik (`remove-silence.py` / `autocut.sh`). Altyazı tüm crop ve overlay'lerden **en sonra** işlenir.
- **Koda Yazılan Kapılar:** Her final çıktı `scripts/qc_gate.py` (`ffprobe` VFR/senkron + `ebur128` `-14`/`-16 LUFS` + true peak ≤ `-1.0 dBTP` + `3x2` contact sheet) ve `scripts/caption_and_chapters.py` kapılarından geçmeden teslim edilmez.
