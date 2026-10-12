# NoteSpaceLLM — Selected Dependency and License Notes

**Paketangaben:** Dokumentationsstand 2026-09-22 (historischer Snapshot)
**Scope-Hinweis aktualisiert:** 2026-10-12
**Projektlizenz:** GNU Affero General Public License v3.0 only (AGPL-3.0-only)
**Kanonisches Repository:** https://github.com/file-bricks/NoteSpaceLLM  
**Organisation:** file-bricks / open-bricks  

Diese manuell gepflegte Momentaufnahme fasst ausgewählte deklarierte Abhängigkeiten und Lizenzhinweise zusammen. Sie ist keine generierte SBOM und erfasst weder alle aufgelösten transitiven Abhängigkeiten noch eingebundene, native oder ausgelieferte Dateien. Die Versionsangaben sind Projektvorgaben und keine Liste installierter Versionen. Die Lizenzkennungen dienen der Orientierung; dieses Dokument bewertet weder Lizenzkompatibilität noch Compliance oder konkrete Weitergabepflichten. Maßgeblich sind die jeweils aktuellen Lizenztexte und Paketinformationen.

---

## 1. Projektlizenz und ausgewählte Lizenzhinweise

Die Projektlizenz ist **GNU Affero General Public License v3.0 only (AGPL-3.0-only)**; siehe [LICENSE](LICENSE). Die folgende Tabelle notiert ausgewählte Lizenzangaben für deklarierte Pakete, ohne eine rechtliche Kompatibilitäts- oder Compliance-Aussage zu treffen.

PyMuPDF und die Qt-for-Python-Pakete haben eigene Lizenztexte und Bedingungen. Ihre Einbindung oder der Import über Python bewertet hier nicht, welche Pflichten für einen konkreten Build oder eine Weitergabe gelten. Prüfen Sie hierfür die jeweils aktuellen Upstream-Lizenztexte und das tatsächlich ausgelieferte Paket.

## 2. Ausgewählte deklarierte Laufzeit-Abhängigkeiten

| Paket | Deklarierte Version | Lizenzhinweis | Verwendung & Zweck |
| :--- | :--- | :--- | :--- |
| `PySide6` | `>=6.5.0` | Multiple upstream licensing options; see resolved distribution license files. | Desktop-GUI, Event-Loop, Widgets, Qt-Framework |
| `shiboken6` | `>=6.5.0` | Multiple upstream licensing options; see resolved distribution license files. | CPython-Bindings-Laufzeit für PySide6 |
| `PyMuPDF` | `>=1.24.10` | AGPL-3.0-or-later | High-Performance PDF-Parsing und Textextraktion |
| `python-docx` | `>=1.1.0` | MIT | Word (.docx) Extraktion und Berichtsgenerierung |
| `openpyxl` | `>=3.1.3` | MIT | Excel (.xlsx) Analyse |
| `extract-msg` | `>=0.48.0` | MIT | Outlook E-Mail (.msg) Extraktion |
| `langchain` | `>=0.3.0` | MIT | Prompt-Orchestrierung und Document-Pipeline |
| `langchain-core` | `>=0.3.0` | MIT | Basis-Schnittstellen für RAG und Chat |
| `langchain-community` | `>=0.3.0` | MIT | Community-Treiber und Dokumentenlader |
| `langchain-ollama` | `>=0.2.0` | MIT | Native lokale Ollama-Anbindung |
| `langchain-chroma` | `>=0.1.0` | MIT | Vektorspeicher-Adapter für ChromaDB |
| `chromadb` | `>=0.5.4` | Apache-2.0 | Lokale Embedding-Vektordatenbank |
| `keyring` | `>=25.7.0` | MIT | API-Zugriff auf erlaubte native Betriebssystem-Schlüsselspeicher |

---

## 3. Ausgewählte optionale Erweiterungen & Backends

| Paket | Deklarierte Version | Lizenz (SPDX) | Verwendung & Zweck |
| :--- | :--- | :--- | :--- |
| `pytesseract` | `>=0.3.10` | Apache-2.0 | Optionale OCR-Bildtextextraktion |
| `Pillow` | `>=10.2.0` | HPND | Bildvorverarbeitung für OCR |
| `weasyprint` | `>=60.0` | BSD-3-Clause | Optionale PDF-Rendererweiterung |
| `openai` | `>=1.0.0` | Apache-2.0 | Optionaler Cloud-Zugriff (OpenAI API) |
| `anthropic` | `>=0.18.0` | MIT | Optionaler Cloud-Zugriff (Anthropic Claude API) |
| `tiktoken` | `>=0.5.0` | MIT | Exakte Token-Zählung für Cloud-Modelle |

---

## 4. Ausgewählte Entwicklungs- & Test-Abhängigkeiten

| Paket | Deklarierte Version | Lizenz (SPDX) | Verwendung & Zweck |
| :--- | :--- | :--- | :--- |
| `pytest` | `>=9.1.1` | MIT | Test-Framework |
| `pytest-asyncio` | `>=1.4.0` | Apache-2.0 | Asynchrone Testausführung |
| `pytest-timeout` | `>=2.4.0` | MIT | Timeout-Sicherung gegen Test-Hänger |
| `ruff` | `>=0.9.0` | MIT / Apache-2.0 | High-Speed Linter und Code-Formatierer |

---

*Ausgewählte Lizenztexte und Quellenhinweise stehen in `THIRD_PARTY_LICENSES.txt`; aktuelle Upstream-Angaben sind dort maßgeblich.*
