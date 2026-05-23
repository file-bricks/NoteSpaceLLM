# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- Remote-Ollama-Anbindung: Konfigurierbare Server-URL pro Projekt
- API-Key-Authentifizierung für Ollama-Proxies (Bearer Token)
- GUI: URL- und API-Key-Felder im LLM-Einstellungsdialog
- ellmos-stack Kompatibilität: Nutzung eines zentralen Ollama-Servers
- Windows-Launcher, App-Icon, README-Screenshot und GitHub-Issue-Templates
- Privacy Policy und README-Hinweise zu lokaler Datenhaltung und externen LLM-Providern
- GitHub Actions Smoke-Test für Python 3.10 bis 3.12

### Geändert / Changed
- System-Prompts optimiert für kleine Modelle (qwen3:4b u.a.)
- RAG-Prompt kompakter -- weniger Token-Overhead
- ProjectSettings: Neue Felder `ollama_base_url` und `ollama_api_key` (abwärtskompatibel)
- Repository-Metadaten auf `file-bricks/NoteSpaceLLM`, AGPL-3.0 und DCO aktualisiert
- GitHub Actions führt neben dem Compile-Smoke-Test jetzt auch die Unit-Tests aus

### Behoben / Fixed
- `.gitignore` ignoriert lokale Projektordner nur noch im Repository-Root, nicht mehr `.github/workflows`
- Deutsche UI-Texte verwenden echte Umlaute; die Übersetzungs-Erkennung markiert englische Wörter mit `ss` nicht mehr irrtümlich als Deutsch

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
