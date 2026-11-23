---
title: Açık Kaynak MCP Sunucuları Kataloğu ve Konfigürasyon Matrisi
date: 2026-11-22
tags:
  - references
  - mcp
  - catalog
  - youtube
  - ffmpeg
  - obs
---

# Açık Kaynak MCP Sunucuları Kataloğu

Tüm sunucular bizzat indirilen kaynak kodlarından doğrulanmıştır. Tamamı **%100 ücretsiz, açık kaynak ve yerel** çalışır (sıfır SaaS abonelik).

---

## 1. Karşılaştırma Matrisi

| MCP Sunucusu | GitHub Reposu | Yıldız | Dil / Runtime | Araç Sayısı | Temel Rol |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **ffmpeg-skill MCP** | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | 9.5k | Python 3.10+ (stdlib) + FFmpeg 6.1+ | 42 | Deterministik kesim, sessizlik, altyazı, 9:16, audiogram, `-14 LUFS`, doğrulama. |
| **Kinocut MCP** | [KyaniteLabs/kinocut](https://github.com/KyaniteLabs/kinocut) | 278 | Python (`uvx`) + FFmpeg | 206 (18 default) | Güvenlik bariyerli kurgu, katman kompozisyonu, Shorts repurpose & QC makbuzu. |
| **OBS-MCP** | [xDarkzx/OBS_MCP](https://github.com/xDarkzx/OBS_MCP) | 30 | Python 3.10+ + OBS 28+ | 148 | Tam obs-websocket v5 + `clean_audio_input` + `diagnose_av_health` + canlı chapter. |
| **YouTube Uploader MCP** | [anwerj/youtube-uploader-mcp](https://github.com/anwerj/youtube-uploader-mcp) | 72 | **Go (tek `.exe` binary)** | 7 | Video yükleme, zamanlama, thumbnail (<2MB), **altyazı (`.srt`) yükleme**, playlist. |
| **YouTube MCP Server** | [pauling-ai/youtube-mcp-server](https://github.com/pauling-ai/youtube-mcp-server) | 34 | Python 3.11+ (`FastMCP`) | 40 | Data API v3 + **Analytics API** (retention) + Reporting API + 0-kota SEO + kota koruması. |
| **YouTube Studio MCP** | [i1s-abhishek/youtube-studio-mcp](https://github.com/i1s-abhishek/youtube-studio-mcp) | 23 | Python 3.10+ (yalnız stdlib) | 11 | Sıfır harici paketle hafif metadata, thumbnail, yorum ve temel analitik. |
| **FilmCraft MCP** | [storytold/filmcraft](https://github.com/storytold/filmcraft) | 18.8k | **Saf Rust binary** | 650+ komut | Yerleşik NLE kontrolü (alpha; headless veya canlı arayüz köprüsü). |
| **PhotoCraft MCP** | [storytold/photocraft](https://github.com/storytold/photocraft) | 81.0k | **Saf Rust binary** | Komut kanalı | PSD katmanları, tipografi, efektler ve thumbnail üretimi (erken alpha). |

---

## 2. Hazır `mcpServers` Konfigürasyon Şablonları

Kurulum fazına geçildiğinde MCP istemcine eklenecek doğrulanmış JSON blokları:

### A) Sıfır Python / Saf Binary Başlangıç Paketi
Yalnızca `youtube-uploader-mcp-windows-amd64.exe` (Go) ve isteğe bağlı `filmcraft-cli.exe` (Rust):

```json
{
  "mcpServers": {
    "youtube-uploader": {
      "command": "C:/Users/HP/YOUTUBE/bin/youtube-uploader-mcp-windows-amd64.exe",
      "args": [
        "-client_secret_file",
        "C:/Users/HP/YOUTUBE/.secrets/client_secret.json"
      ]
    }
  }
}
```

### B) Önerilen Hibrit Stüdyo Paketi (FFmpeg + OBS + Kinocut + YouTube Tam Set)

```json
{
  "mcpServers": {
    "obs": {
      "command": "uvx",
      "args": ["obs-mcp"],
      "env": {
        "OBS_HOST": "localhost",
        "OBS_PORT": "4455",
        "OBS_PASSWORD": "BURAYA_OBS_SIFRESI"
      }
    },
    "kinocut": {
      "command": "uvx",
      "args": ["kinocut==2.0.1"],
      "env": {
        "KINOCUT_TOOLS": "profile:editor",
        "KINOCUT_VISION_MODE": "off"
      }
    },
    "youtube-uploader": {
      "command": "C:/Users/HP/YOUTUBE/bin/youtube-uploader-mcp-windows-amd64.exe",
      "args": [
        "-client_secret_file",
        "C:/Users/HP/YOUTUBE/.secrets/client_secret.json"
      ]
    },
    "youtube-analytics": {
      "command": "youtube-studio-mcp",
      "env": {
        "YOUTUBE_MCP_CLIENT_SECRET": "C:/Users/HP/YOUTUBE/.secrets/client_secret.json"
      }
    }
  }
}
```

> [!TIP] `ffmpeg-skill` MCP Notu
> `ffmpeg-skill` MCP varsayılan 12 aracı listeler; `FFMPEG_SKILL_MCP_TOOLS=probe,cut,silence,fit,caption,audio,loudness,render,export,check,look` ortam değişkeniyle odak listesi daraltılabilir (42 aracın tamamı yine adıyla çağrılabilir).

### C) FilmCraft (Rust NLE) MCP Köprüsü (Deneysel)

```json
{
  "mcpServers": {
    "filmcraft": {
      "command": "C:/Users/HP/YOUTUBE/bin/filmcraft-cli.exe",
      "args": ["mcp", "--bridge", "127.0.0.1:9876"]
    },
    "filmcraft-headless": {
      "command": "C:/Users/HP/YOUTUBE/bin/filmcraft-cli.exe",
      "args": ["mcp"]
    }
  }
}
```

İlgili rehberler: [[YOUTUBE_API_GUIDE]], [[skills/channel-ops-and-obs/SKILL|channel-ops-and-obs]], [[references/editors-landscape|editors-landscape]].
