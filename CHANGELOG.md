# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Build / Release
- macOS-Source-Smoke für die Desktop-Linie ergänzt: `tests/platform_smoke.py`
  startet `MainWindow` offscreen, importiert ein temporäres Dokument und
  exportiert ein `notespacellm-workspace-v1.json` ohne echten LLM-/Ollama-Server
- GitHub Actions um `macos-source-smoke` auf `macos-latest` erweitert
- Linux-Source-Smoke ergänzt: `tests/linux_platform_smoke.py` prüft
  App-Start, Dokumentimport mit echten Umlauten, Markdown-/TXT-Berichtsexport
  und `notespacellm-workspace-v1.json` auf `ubuntu-latest`
- GitHub Actions um `linux-source-smoke` auf `ubuntu-latest` erweitert
- EXE neu gebaut 2026-06-01 (PyInstaller --onefile, `notespacellm_launcher.py`-Launcher → `C:\_Local_DEV\codex_build\notespacellm`); 72/72 Tests grün (3 skipped), Smoke OK. Vorherige EXE: 2026-05-01. Anlass: QTimer-RAG-Init-Fix in `src/gui/main_window.py` (verhindert Startup-Freeze bei Remote-Ollama).

### Bekannte Einschränkungen / Known Issues (Nutzerfeedback 2026-06-01)

- ~~**Langer Start (mehrere Minuten)**~~ **Behoben:** `_init_rag_engine()` wird
  jetzt via `QTimer.singleShot(0, ...)` nach dem ersten GUI-Render aufgerufen —
  Fenster erscheint sofort, Statusbar zeigt RAG-Verbindungsstatus.
- GUI friert bei langen Operationen (Text-Extraktion, Indexierung, Analyse, Bericht)
  ein — Qt-Hauptthread wird blockiert. Workaround: Geduld; Fix in Arbeit (QThread).
- Export: Dateiname kann nicht frei gewählt werden — Pfad wird automatisch gesetzt.
- Profile: Nach dem Erstellen nicht editier- oder löschbar.
- Begriffe (Extraktion/Indexierung/Analyse/Bericht) und deren Reihenfolge sind
  für Neunutzer unklar — Hilfetexte/visuelle Pipeline-Darstellung geplant.
- Button "Prompt exportieren" ist missverständlich — Umbenennung zu
  "An LLM gesendeten Prompt exportieren" geplant.

**Positiv-Feedback:** Brauchbare Berichte mit lokalem Ollama-Modell (Mac/qwen3)
wurden erfolgreich erstellt — Remote-Ollama-Anbindung funktioniert produktiv.

### Hinzugefügt / Added
- Portierungsplan für Windows Store, Web/PWA, Android, iOS, macOS und Linux
- Geplantes Austauschformat `notespacellm-workspace-v1.json` für Desktop-zu-Companion-Workflows
- Erster Web/PWA-Companion unter `web_companion/` mit lokalem Workspace-Import, read-only Bericht-/Dokumentansicht und Export für Review-Notizen
- `web_companion/PWA_TESTPLAN.md` für Android-/iOS-PWA-Smokes zu Installierbarkeit, Import, Offline-Start und Review-Notiz-Export
- `web_companion/manifest.webmanifest`: `id` und `scope` ergänzt (PWA-Installierbarkeits-Best-Practice)
- `web_companion/sw.js`: CACHE_NAME v2, `skipWaiting()` + `self.clients.claim()`, 4 Icon-Pfade in ASSETS
- `web_companion/tests/pwa.test.mjs`: 22 Node.js-Strukturtests (Manifest-Pflichtfelder, Icons, SW-Inhalt, HTML-Integrationskette), kein npm install
- `web_companion/package.json`: Testscript auf beide Testdateien erweitert (28/28 grün)
- README-Screenshot und SEO-Metadaten für den Web/PWA-Companion
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
- Der Web/PWA-Companion stellt den zuletzt geladenen Workspace lokal für Offline-Starts wieder her und zeigt Android-/iOS-Install-Hinweise direkt in der UI
- ProjectSettings: Neue Felder `ollama_base_url` und `ollama_api_key` (abwärtskompatibel)
- Repository-Metadaten auf `file-bricks/NoteSpaceLLM`, AGPL-3.0 und DCO aktualisiert
- GitHub Actions führt neben dem Compile-Smoke-Test jetzt auch die Unit-Tests aus

### Behoben / Fixed
- `.gitignore` ignoriert lokale Projektordner nur noch im Repository-Root, nicht mehr `.github/workflows`
- Deutsche UI-Texte verwenden echte Umlaute; die Übersetzungs-Erkennung markiert englische Wörter mit `ss` nicht mehr irrtümlich als Deutsch

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
