# Changelog / Aenderungsprotokoll

Alle wesentlichen Aenderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefuegt / Added
- Remote-Ollama-Anbindung: Konfigurierbare Server-URL pro Projekt
- API-Key-Authentifizierung fuer Ollama-Proxies (Bearer Token)
- GUI: URL- und API-Key-Felder im LLM-Einstellungsdialog
- ellmos-stack Kompatibilitaet: Nutzung eines zentralen Ollama-Servers

### Geaendert / Changed
- System-Prompts optimiert fuer kleine Modelle (qwen3:4b u.a.)
- RAG-Prompt kompakter -- weniger Token-Overhead
- ProjectSettings: Neue Felder `ollama_base_url` und `ollama_api_key` (abwaertskompatibel)

### Behoben / Fixed
-

## [1.0.0] - YYYY-MM-DD

### Hinzugefuegt / Added
- Erstveroeffentlichung / Initial release
