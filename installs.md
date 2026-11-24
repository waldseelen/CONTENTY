# CONTENTY — OS-Specific Installation Guide

Ajanlar ve geliştiriciler için işletim sistemine göre gerekli sistem paketleri (Go ve MCP sunucuları hariç) ve proje bağımlılıkları.

---

## 1. Debian / Ubuntu (`apt`)

```bash
sudo apt update && sudo apt install -y \
  python3 python3-pip python3-venv \
  nodejs npm \
  ffmpeg melt yt-dlp \
  librsvg2-bin poppler-utils \
  obs-studio \
  wl-clipboard fonts-noto-core fonts-inter
```
- **X11 kullanılıyorsa:** `wl-clipboard` yerine `xclip` kur.
- **Opsiyonel (slayt PDF dönüşümü):** `sudo apt install -y libreoffice-impress`
- **`uv` (OBS CLI için):** `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

## 2. Arch Linux (`pacman`)

```bash
sudo pacman -S --needed \
  python python-pip uv \
  nodejs npm \
  ffmpeg mlt yt-dlp \
  librsvg poppler \
  obs-studio \
  wl-clipboard noto-fonts inter-font
```
- **X11 kullanılıyorsa:** `wl-clipboard` yerine `xclip` kur.
- **Opsiyonel (slayt PDF dönüşümü):** `sudo pacman -S --needed libreoffice-fresh`

---

## 3. Windows (`winget`)

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id astral-sh.uv
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Gyan.FFmpeg
winget install -e --id yt-dlp.yt-dlp
winget install -e --id OBSProject.OBSStudio
winget install -e --id Shotcut.Shotcut
```
- **`melt.exe` (`mlt`):** `Shotcut.Shotcut` ile gelir; `C:\Program Files\Shotcut\` yolunu `PATH` veya `MELT_BIN` ortam değişkenine ekle.
- **Opsiyonel (`pdftoppm` / `rsvg-convert` / LibreOffice):** `scoop install poppler`, `choco install rsvg-convert`, `winget install -e --id TheDocumentFoundation.LibreOffice`.

---

## 4. Proje İçi Python & Node Bağımlılıkları (Tüm OS'ler)

```bash
python3 -m venv .venv
# Linux / macOS:
.venv/bin/pip install -r requirements.txt
# Windows PowerShell:
# .venv\Scripts\pip.exe install -r requirements.txt

npm install
```

## 5. Kurulum Sonrası Doğrulama

```bash
npm run check
python3 scripts/obs_health.py
```
