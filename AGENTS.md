# CONTENTY Studio — Agent Instructions

Bu depo jenerik bir AI video, YouTube ve canlı yayın üretim fabrikasıdır.

## Keşif ve Başlangıç
1. Yeni bir üretim işi geldiğinde ilk olarak `skills/studio-router/SKILL.md` dosyasını oku ve `scripts/init_project.py` ile proje klasörünü kur.
2. İş akışı, ses, kurgu, grafik, hikâye, thumbnail ve yayın adımlarında ilgili `skills/<skill>/SKILL.md` dosyasını yükle.
3. Eklenti kurulumu için `plugins/contenty-studio/` altındaki manifesti ve `scripts/install_plugin.sh` betiğini kullan.

## Değişmez Üretim Kuralları
- **Yönetmen Kapısı:** Kullanıcı onaylamadan final render alma ve YouTube'a herkese açık yükleme yapma (`private` taslak kuralı).
- **Ağır Medya Disiplini:** Ham çekimler ve büyük ara çıktılar `$STUDIO_JOBS` veya yerel `workspace/` içinde kalır; orijinal ham kaydın üzerine yazılmaz.
- **Kesim & Altyazı Sırası:** Önce tekrar/flub kesimi (`ffmpeg select`), sonra sessizlik (`remove-silence.py` / `autocut.sh`). Altyazı tüm crop ve overlay'lerden **en sonra** işlenir.
- **Koda Yazılan Kapılar:** Her final çıktı `scripts/qc_gate.py` (`ffprobe` VFR/senkron + `ebur128` `-14`/`-16 LUFS` + true peak ≤ `-1.0 dBTP` + `3x2` contact sheet) ve `scripts/caption_and_chapters.py` kapılarından geçmeden teslim edilmez.
