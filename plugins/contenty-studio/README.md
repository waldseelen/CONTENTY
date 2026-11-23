# Contenty Studio Plugin

Video kurgu, hikâye/retention planlama, HyperFrames motion grafik, yüksek CTR thumbnail ve OBS/YouTube operasyonlarını tek pakette toplayan jenerik eklenti paketi.

## Kurulum

### Antigravity
```bash
./scripts/install_plugin.sh antigravity
```
Kurulum sonrası Antigravity Customization panelinden `contenty-studio` eklentisini etkinleştir.

### Claude Code / Codex
```bash
./scripts/install_plugin.sh claude
```
(Veya `skills/` klasöründeki istediğiniz alt dizinleri doğrudan `~/.claude/skills/` altına kopyalayın.)

### MCP Sunucuları (Opsiyonel)
`mcp_config.template.json` dosyasındaki hazır bloklardan ihtiyacın olanları (`obs`, `kinocut`, `ffmpeg-skill`, `youtube-uploader`, `youtube-studio`) kendi dosya yollarınla kullanıcı MCP konfigürasyonuna ekle.
