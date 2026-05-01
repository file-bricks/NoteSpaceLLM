# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- Remote-Ollama-Anbindung: Konfigurierbare Server-URL pro Projekt
- API-Key-Authentifizierung für Ollama-Proxies (Bearer Token)
- GUI: URL- und API-Key-Felder im LLM-Einstellungsdialog
- ellmos-stack Kompatibilitaet: Nutzung eines zentralen Ollama-Servers
- Windows-Launcher, App-Icon, README-Screenshot und GitHub-Issue-Templates
- Privacy Policy und README-Hinweise zu lokaler Datenhaltung und externen LLM-Providern
- GitHub Actions Smoke-Test für Python 3.10 bis 3.12

### Geändert / Changed
- System-Prompts optimiert für kleine Modelle (qwen3:4b u.a.)
- RAG-Prompt kompakter -- weniger Token-Overhead
- ProjectSettings: Neue Felder `ollama_base_url` und `ollama_api_key` (abwaertskompatibel)
- Repository-Metadaten auf `file-bricks/NoteSpaceLLM`, AGPL-3.0 und DCO aktualisiert

### Behoben / Fixed
- `.gitignore` ignoriert lokale Projektordner nur noch im Repository-Root, nicht mehr `.github/workflows`

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveroeffentlichung / Initial release
