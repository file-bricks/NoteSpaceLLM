# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased — 2026-06-20]

### Changed (web_companion)
- `web_companion/` erweitert die Companion-Oberfläche von DE/EN auf DE/EN/ES/ZH-Hans/JA/RU. Sprachumschalter, Browser-/Workspace-Locale-Auflösung, Plattformhinweise, Validierungsfehler, Demo-Workspace und Review-Markdown-Export nutzen jetzt denselben sechssprachigen UI-Textvertrag.
- `web_companion/tests/library.test.mjs` und `web_companion/tests/pwa.test.mjs` prüfen die sechs unterstützten Locales, Key-Parität, non-latin Demo-Inhalte, lokalisierte Plattformhinweise und die sichtbaren Select-Optionen.

## [Unreleased — 2026-06-10]

### Changed (web_companion)
- `web_companion/index.html`: viewport-Meta um `viewport-fit=cover` erweitert; iOS-PWA-Meta-Tags ergänzt: `apple-mobile-web-app-status-bar-style` (default), `apple-mobile-web-app-title` (NoteSpaceLLM), `apple-touch-icon` 180×180 px
- `web_companion/app.css`: `.shell`-Padding auf vollständige Longhand-Deklarationen mit `env(safe-area-inset-top, 0px)` / `env(safe-area-inset-bottom, 0px)` umgestellt; `button`/`.file-button` erhalten `min-height: 44px` und `min-width: 44px` (Apple-HIG-Touch-Targets)
- `web_companion/icons/apple-touch-icon-180.png`: Neues 180×180-Icon aus Icon-192.png via LANCZOS-Resize generiert
- `web_companion/tests/pwa.test.mjs`: 10 neue iOS-PWA-Tests ergänzt (viewport-fit=cover, apple-status-bar-style, apple-title, apple-touch-icon-Pfad, apple-touch-icon-sizes, manifest-Link, theme-color, kein doppeltes viewport, apple-touch-icon-180.png existiert); 33/33 Tests grün (vorher 23)

## [Unreleased]

### Changed (web_companion)
- `web_companion/` nutzt jetzt ein DE/EN-i18n-System mit Browser-/Workspace-Locale und manuellem Sprachumschalter; HTML-Labels, Statusmeldungen, Offline-/PWA-Hinweise und Review-Exporttexte laufen über zentrale UI-Texte.
- `web_companion/library.js`: Review-Markdown, Plattformhinweise, Fallback-Texte und Demo-Workspace unterstützen jetzt DE/EN; Node-Tests decken Locale-Auflösung und englische Copy mit ab.

### CI / Maintenance
- Community workflows refreshed: `.github/workflows/stale.yml` now uses `actions/stale@v10`, and `.github/workflows/welcome.yml` now uses `actions/first-interaction@v3`.

### Documentation
- README restructured to English-first with full English feature/install/config/usage documentation; German translation moved to secondary section
- `llms.txt` added for LLM crawler discoverability; Last-checked: 2026-06-11, Audience and Search Phrases sections standardized
- `PORTIERUNGSPLAN.md` reference removed from README (internal file, already gitignored); `docs/` added to `.gitignore`

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
- `locales/translations.json`: i18n for es, zh, ja, ru — Premium 6-language translations added (Spanish, Chinese, Japanese, Russian) via `manage_translations.py` (0b9769d)
- `translator.py`: per-language `missing` dict bucketing for all 6 languages (en/de/es/zh/ja/ru)
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
- `web_companion/app.js`: `forEach`-Parameter `document` shadowed the DOM global causing `createElement` to crash → renamed to `doc` (73f0c98)
- `web_companion/app.js`: `escHtml()` added; all `innerHTML` assignments (doc.name, doc.format, doc.path_hint, excerpt.text, excerpt.source_hint) now HTML-escaped to prevent XSS (73f0c98)
- `web_companion/sw.js`: `caches.match` now uses `{ignoreSearch: true}` to prevent offline fail on `?`-query URLs (73f0c98)
- `tests/test_translator.py`: updated `test_scan_and_update_only_picks_up_german_strings` to match the multi-language `missing` dict returned since i18n expansion (6 languages)
- `.gitignore` ignoriert lokale Projektordner nur noch im Repository-Root, nicht mehr `.github/workflows`
- Deutsche UI-Texte verwenden echte Umlaute; die Übersetzungs-Erkennung markiert englische Wörter mit `ss` nicht mehr irrtümlich als Deutsch

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
