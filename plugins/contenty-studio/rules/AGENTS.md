# Contenty Studio — Üretim Kuralları

1. **Tek Şef ve Yönetmen Kapısı:** Final render ve YouTube yayını kullanıcı onayı olmadan alınmaz. Önce kesim planı (`edl.json` / `edit.json`), pano haritası ve hızlı taslak (`draft`) gösterilir.
2. **Ağır Medya Senkron Dışında:** Ham videolar (`workspace/01-raw/`) asla üzerine yazılmaz ve bulut senkron klasörlerine taşınmaz.
3. **Ses Öncelikli, Altyazı En Sonda:** Kesimler kelime sınırına (`30–200 ms` pay) hizalanır; `afade` (`4–30 ms`) uygulanır. Altyazı tüm crop, overlay ve grafiklerden **en sonra** işlenir; uzun videoda harici `.srt`, dikey Shorts'ta güvenli alan içinde burn-in `.ass` kullanılır.
4. **Sıralı Kesim Kuralı:** Önce tekrar/hata kesimi (flub-cut — ham zaman kodlarıyla `ffmpeg select`), ardından sessizlik kesimi (`auto-editor` veya `remove-silence.py`). `auto-editor` v29 `--cut-out` yerine `ffmpeg select` kullanılır.
5. **Marka ve Karakter Kilidi:** Grafik ve thumbnail üretiminde `brand/frame.template.md` / `brand/frame.md` dışına çıkılmaz (anti-AI-slop: neon, mor gradyan, parlama, rastgele seed yok). Karakter pozlarında düz uzatılmış kol/açık avuç kullanılmaz.
6. **Ölçmeden Teslim Etme:** Her çıktı `ffprobe` (süre ±1 kare, A/V senkron), `ebur128` (`-14 LUFS` video / `-16 LUFS` podcast, true peak ≤ `-1.0 dBTP`) ve `3x2` temas sayfası (`contact sheet`) ile doğrulanır.
7. **Aynı Hata İki Kez Olursa Koda Yaz:** Tekrarlayan kurgu/senkron/format hataları yalnızca nota değil doğrulama kapısına (script/check) dönüştürülür.
