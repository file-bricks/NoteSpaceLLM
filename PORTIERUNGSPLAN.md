# PORTIERUNGSPLAN — NoteSpaceLLM Pro

Dieses Dokument definiert die plattformübergreifende Portierungsstrategie,
die Zielsystem-Architektur und den Schnittstellenvertrag für **NoteSpaceLLM Pro**.

Stand: 2026-11-03  
Status: Aktiv / Gepflegt  

---

## 1. Zielplattformen & Priorisierung

| Plattform | Technologie | Priorität | Status | Kanonischer Pfad / Artefakt |
|---|---|---|---|---|
| **Windows Desktop** | Python 3.10+, PySide6 (Qt6), SQLite, ChromaDB/FAISS | P0 (Kanonisch) | Aktiv (v1.0.0) | `main.py`, `build_exe.bat`, `src/` |
| **Windows Store (MSIX)** | Desktop-Bridge (Centennial), AppxManifest, WACK | P1 (Staged / Ready) | Staged (v1.0.0.0) | `store_package/NoteSpaceLLM/`, `releases/windowsstore/` |
| **Web Companion & PWA** | Statisches HTML5 / Vanilla JS, Service Worker, Web App Manifest | P2 (Vollständig) | Bereit (v1.0.0) | `web_companion/` (67/67 Tests bestanden) |
| **Mobile Companion (Android/iOS)** | PWA mit Mobile-Install-Banner, Offline-Cache, Web Share API | P2 (Verifiziert) | Bereit | `web_companion/manifest.webmanifest`, `PWA_TESTPLAN.md` |
| **macOS & Linux Desktop** | PySide6 Source-Execution, Plattform-unabhängiges RAG | P3 (Wartung) | Kompatibel | Source-Start via Python (`tests/test_platform_smoke.py`) |

---

## 2. Architektur & Schichtenmodell

```
+-------------------------------------------------------------------------+
|                           NoteSpaceLLM Core                             |
+------------------------------------+------------------------------------+
|          Desktop (PySide6)         |       Web / Mobile PWA Companion   |
|  - main.py / src/gui/              |  - web_companion/index.html        |
|  - RAG Vector Index (Chroma/FAISS) |  - library.js / app.js             |
|  - Document Parser & OCR           |  - Offline Service Worker (sw.js)  |
|  - Local/Remote LLM Orchestrator   |  - JSON Workspace Viewer & Review  |
|  - Multi-Format Exporter           |  - Mobile Share Sheet Adapter      |
+------------------------------------+------------------------------------+
                                     |
                                     v
                 +---------------------------------------+
                 | notespacellm-workspace-v1.json Export |
                 +---------------------------------------+
```

### Kern- und Schichtentrennung:
1. **Core-Schicht (`src/core/`):**
   - RAG-Indizierung, Chunking, Embeddings und LLM-Provider (Ollama, Anthropic, OpenAI).
   - Vollständig GUI-unabhängig und portabel.
2. **Daten- & Dokumenten-Extraktion (`src/reports/`, `src/tools/`):**
   - Multi-Format Ingestion (PDF, Word, TXT, MD, HTML).
   - Generierung von Forschungsberichten und Deep-Research-Artefakten.
3. **Desktop-Präsentation (`src/gui/`):**
   - PySide6-basierte Benutzeroberfläche mit Tabbed Document Viewer, Prompt-Inspektor und Pipeline-Hilfe.
4. **Web / Mobile PWA (`web_companion/`):**
   - Offline-fähiger Workspace-Reader für mobile Review-Workflows (Android/iOS) ohne Cloud-Zwang.

---

## 3. Windows Store Packaging (Target 1)

Die Windows-Store-Bereitstellung erfolgt über die Microsoft Desktop Bridge (Centennial):
- **Paket-Identität:** `Geiger.NoteSpaceLLM`
- **Publisher:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`
- **Capabilities:** `runFullTrust`, `internetClient` (für optionale Cloud-LLM-APIs und lokalen Ollama-Netzwerkverkehr)
- **Manifest:** `store_package/NoteSpaceLLM/AppxManifest.xml`
- **Asset-Auflösungen:**
  - StoreLogo: `50x50`
  - Square44x44Logo: `44x44`
  - Square150x150Logo: `150x150`
  - Wide310x150Logo: `310x150`
  - Square310x310Logo: `310x310`
- **WACK-Zertifizierung:** Preflight automatisiert via `scripts/run_windows_wack.py` (6 PASS / 0 FAIL / 0 WARN).
- **Listing & Richtlinien:** `store_listing_de.md` und `store_listing_en.md` erfüllen Microsoft Store Policy 10.1.3 (maximal 7 Keywords je Sprache).

---

## 4. Web & Mobile Companion (Targets 2 & 3)

Der Companion unter `web_companion/` bedient Web- und Mobilnutzer:
- **Offline-First:** Vollständig gecacht via Service Worker `sw.js` (Cache v3).
- **Plattform-Integration:** Web App Manifest `manifest.webmanifest`, iOS Touch Icons, Theme-Color.
- **Datenaustausch:** Liest und exportiert `notespacellm-workspace-v1.json` ohne Server-Upload.
- **Testvertrag:** 67 automatisierte Node.js Tests (`npm test`), 100% grün.

---

## 5. macOS & Linux Source-Execution (Targets 5 & 6)

- PySide6, ChromaDB und PDF-Backends sind plattformneutral.
- Lokale Pfade nutzen `pathlib.Path` für saubere POSIX- und Windows-Kompatibilität.
- Ausführung auf macOS und Linux erfolgt über die Standard-Python-Laufzeit (`python main.py`).
