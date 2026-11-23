---
title: YouTube Data API v3, OAuth 2.0 ve MCP Yükleme Rehberi
date: 2026-11-22
tags:
  - youtube-api
  - oauth2
  - mcp
  - publishing
---

# YouTube Data API v3 & MCP Yükleme Rehberi

Bu rehber, YouTube kanalına ücretsiz, yerel ve güvenli biçimde video, Shorts, özel thumbnail, altyazı (`captions.srt`), bölüm zaman damgaları ve analitik erişimi kurmak için `youtube-uploader-mcp` (Go), `youtube-mcp-server` (Python, 40 araç) ve `youtube-studio-mcp` (Python stdlib) repolarından derlenmiştir.

---

## 1. Neden API Key Yetmez? (OAuth 2.0 Zorunluluğu)

YouTube Data API v3 üzerinde yalnızca herkese açık okuma işlemleri API Key ile yapılabilir. Video yükleme, açıklama güncelleme, thumbnail atama, altyazı yükleme ve kanal analitiği okuma işlemleri için **Google Cloud Console → OAuth 2.0 Desktop App** (`client_secret.json`) zorunludur ve tamamen **ücretsizdir**.

### Adım Adım Google Cloud Kurulumu
1. [Google Cloud Console](https://console.cloud.google.com/) üzerinde yeni proje oluştur (örn. `ContentyStudio`).
2. **APIs & Services → Library** altından şu 3 API'yi etkinleştir:
   * **YouTube Data API v3** (yükleme, metadata, thumbnail, altyazı, playlist, yorum)
   * **YouTube Analytics API** (izlenme süresi, retention eğrisi, Shorts vs uzun video karşılaştırması)
   * **YouTube Reporting API** (isteğe bağlı toplu CSV raporlar)
3. **APIs & Services → OAuth consent screen (Google Auth Platform):**
   * User Type: **External**
   * Uygulama adı + geliştirici e-postası gir.
   * **Audience → Test Users** bölümüne **YouTube kanalının sahibi (owner) olan Google hesabını** ekle (Analytics API yalnızca kanal sahibi hesapla çalışır, yönetici hesapla değil).
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID:**
   * Application Type: **Desktop app**
   * İndirilen JSON dosyasını yerel ve güvenli bir yere kaydet (örn. `c:\Users\HP\YOUTUBE\.secrets\client_secret.json`). **Asla public Git reposuna gönderme!**

### Gerekli OAuth Scope'ları
* `https://www.googleapis.com/auth/youtube.upload` — Video yükleme (`videos.insert`).
* `https://www.googleapis.com/auth/youtube` — Video/playlist/thumbnail düzenleme.
* `https://www.googleapis.com/auth/youtube.force-ssl` — **Altyazı (`.srt`) yükleme ve yorum yazma** için zorunlu hassas scope (olmazsa altyazı yüklemede `403 Forbidden` döner).
* `https://www.googleapis.com/auth/youtube.readonly` — Kanal ve video listesi okuma.
* `https://www.googleapis.com/auth/yt-analytics.readonly` — İzlenme, tutunma (retention) ve trafik kaynakları.

> [!NOTE] "Google hasn't verified this app" Uyarı Ekranı
> Kişisel geliştirici uygulamanı Test Users modunda yetkilendirirken tarayıcıda doğrulama uyarısı çıkar. Bu normaldir: **Advanced (Gelişmiş) → Go to ContentyStudio (unsafe)** seçilerek yalnızca kendi yerel uygulamana izin verilir. Token yerel diskte saklanır ve otomatik yenilenir.

---

## 2. Kritik Kural: Unaudited App → `private` Taslak Stratejisi

> [!IMPORTANT] Google API Uyumluluk Kuralı (July 2020+)
> Google'ın YouTube API uyumluluk denetiminden (audit) geçmemiş kişisel projelerden API ile yüklenen tüm videolar — kodda `public` yazılsa bile — YouTube tarafından otomatik **`private`** durumuna kilitlenir.

**Bizim İş Akışımız İçin Bu Bir Avantajdır:**
1. Ajan montajı bitirir, `upload_video` ile videoyu `privacy_status: "private"` olarak yükler.
2. Ardından `update_video` ile başlık, açıklama, `00:00` bölüm zaman damgaları (chapters), etiketler, kategori, playlist, `<2 MB` özel thumbnail ve Türkçe `captions.srt` altyazısını ekler.
3. Sen YouTube Studio'yu açıp tek bakışta kontrol eder, **tek tıkla `Herkese Açık` veya `Planla`** yaparsın. Yanlışlıkla bozuk video yayınlama riski sıfırlanır.

---

## 3. Teknik Referans: `videos.insert` ve Kota Tablosu

* **Uç Nokta:** `POST https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status`
* **Yükleme Modu:** Büyük video dosyaları için her zaman **`uploadType=resumable`** (kesinti olursa kaldığı yerden devam eder; parça boyutu `256 KB` katları olmalıdır).
* **Maksimum Dosya Boyutu:** `256 GB` | **MIME:** `video/*` veya `application/octet-stream`.
* **Thumbnail Sınırı:** Maksimum `2 MB` (JPG/PNG, önerilen `1280x720`, 16:9).

### Günlük Kota Maliyetleri (Standart Havuz: `10.000 birim / gün`, sıfırlama: 00:00 PT)

| İşlem | API Metodu | Kota Maliyeti | Not |
| :--- | :--- | :---: | :--- |
| Video yükleme | `videos.insert` | **1.600 birim** | Günde ~6 tam yükleme (standart havuzda) |
| Arama | `search.list` | **100 birim** | Pahalı; SEO için ücretsiz autocomplete kullan |
| Yazma / Güncelleme | `videos.update`, `thumbnails.set`, `playlistItems.insert` | **50 birim** | Başlık, açıklama, thumbnail, playlist |
| Altyazı yükleme | `captions.insert` | **400 birim** | `youtube.force-ssl` scope gerekir |
| Okuma / Listeleme | `channels.list`, `videos.list`, `playlists.list` | **1 birim** | Çok ucuz |
| SEO Önerileri | Autocomplete endpoint (`youtube-mcp-server`) | **0 birim** | Kota harcamaz |

---

## 4. Hangi YouTube MCP'yi Seçmeliyiz?

| Özellik | `youtube-uploader-mcp` (Go) | `youtube-mcp-server` (Python) | `youtube-studio-mcp` (Python stdlib) |
| :--- | :---: | :---: | :---: |
| **Çalışma Zamanı** | **Tek `.exe` binary (sıfır bağımlılık)** | Python 3.11+ (`pip`/`uv`) | Python 3.10+ (harici paket yok) |
| **Video Yükleme (`upload_video`)** | Evet (çoklu kanal + zamanlama) | Evet (kota korumalı) | Hayır (metadata/thumbnail/analitik) |
| **Altyazı (`.srt`) Yükleme** | **Evet (`update_video`)** | Hayır (yalnız okuma) | Hayır |
| **Thumbnail (<2MB)** | Evet | Evet | Evet |
| **Analytics & Retention API** | Hayır | **Evet (13 analitik aracı)** | Temel (kanal + video analitik) |
| **SEO & Trend & Kota Sayacı** | Hayır | **Evet (40 araç toplam)** | Hayır |

> [!TIP] En İyi Kombinasyon
> * **Sıfır Python kurulumuyla başlamak için:** Yalnızca `youtube-uploader-mcp-windows-amd64.exe` (Go tek binary — yükleme + thumbnail + altyazı + playlist + zamanlama).
> * **Python ortamı açıldığında:** Yanına `pauling-ai/youtube-mcp-server` ekle → izleyici tutunma (retention) eğrisi, Shorts vs uzun video performansı ve sıfır-kotalı SEO önerileri de ajana açılır.

### Örnek MCP Konfigürasyonu (Go Binary — Sıfır Runtime)
```json
{
  "mcpServers": {
    "youtube-uploader-mcp": {
      "command": "C:/Users/HP/YOUTUBE/bin/youtube-uploader-mcp-windows-amd64.exe",
      "args": [
        "-client_secret_file",
        "C:/Users/HP/YOUTUBE/.secrets/client_secret.json"
      ]
    }
  }
}
```

### Örnek MCP Konfigürasyonu (Python — 40 Araçlık Tam Analitik + Yönetim)
```json
{
  "mcpServers": {
    "youtube": {
      "command": "youtube-studio-mcp",
      "env": {
        "YOUTUBE_MCP_CLIENT_SECRET": "C:/Users/HP/YOUTUBE/.secrets/client_secret.json"
      }
    }
  }
}
```

İlgili rehberler: [[ARCHITECTURE]], [[skills/channel-ops-and-obs/SKILL|channel-ops-and-obs]], [[references/mcp-catalog|mcp-catalog]].
