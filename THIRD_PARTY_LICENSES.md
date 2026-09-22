# NoteSpaceLLM — Level 1 Software Bill of Materials (SBOM)

**Stand:** 2026-09-22  
**Projektlizenz:** GNU Affero General Public License v3.0 (AGPL-3.0)  
**Kanonisches Repository:** https://github.com/file-bricks/NoteSpaceLLM  
**Organisation:** file-bricks / open-bricks  

---

## 1. Lizenzanalyse & Copyleft-Architektur

NoteSpaceLLM ist lizenziert unter der **GNU Affero General Public License v3.0 (AGPL-3.0)**.
Die Softwarearchitektur wahrt strikte Kompatibilität und rechtliche Grenzziehungen:

1. **PyMuPDF (fitz)**: Lizenziert unter GNU AGPL-3.0-or-later. Die AGPL-3.0-Lizenz von NoteSpaceLLM erfüllt sämtliche Anforderungen der reziproken Copyleft-Klausel von PyMuPDF direkt und vollständig.
2. **PySide6 (Qt for Python)**: Lizenziert unter GNU Lesser General Public License v3 (LGPL-3.0-only). NoteSpaceLLM bindet PySide6 und shiboken6 ausschließlich über dynamische Bindungen (Standard CPython Shared Object / DLL Import) ein, ohne Modifikation des Quellcodes der Qt-Bibliotheken. Dies erfüllt die Anforderungen von LGPL-3.0 § 4 vollumfänglich.
3. **Permissive Komponenten**: LangChain, ChromaDB, python-docx, openpyxl, extract-msg, Pillow und pytesseract stehen unter permissiven Open-Source-Lizenzen (MIT, Apache-2.0, BSD-3-Clause) und sind uneingeschränkt kompatibel.
4. **Keine proprietären Binary Blobs**: Sämtliche Ausführungslogik basiert auf offenen, einsehbaren und lokal lauffähigen Python- und Web-Komponenten.

---

## 2. Invarianten-Matrix (INV-LOCAL-01 bis INV-LOCAL-10)

| Invariante | Bezeichnung | Technische Durchsetzung |
| :--- | :--- | :--- |
| **INV-LOCAL-01** | Local-First Privacy Boundary | Dokumente, Extrakte, ChromaDB und SQLite verbleiben lokal auf dem Rechner. |
| **INV-LOCAL-02** | Unprivileged User-Space Execution | `RunAsInvoker` Non-Elevation; keine Admin- oder Root-Rechte erforderlich. |
| **INV-LOCAL-03** | Zero Unsolicited Egress | Keine automatische Telemetrie; externe APIs nur nach expliziter Nutzerkonfiguration. |
| **INV-LOCAL-04** | Offline-First Local Model Execution | Vollständige Unterstützung lokaler Ollama-Instanzen ohne Internetverbindung. |
| **INV-LOCAL-05** | Hardened Parser Security | Mindestversions-Floors (openpyxl>=3.1.3, PyMuPDF>=1.24.10, python-docx>=1.1.0). |
| **INV-LOCAL-06** | Portable Workspace Serialization | Strukturierte Spezifikation (`notespacellm-workspace-v1.json`) für Austausch und Review. |
| **INV-LOCAL-07** | PWA Offline Isolation | Web Companion läuft 100% client-seitig via Service Worker ohne Tracker. |
| **INV-LOCAL-08** | AGPL-3.0 & LGPL-3.0 Boundary Purity | Vollständige Einhaltung von Copyleft und dynamischer Qt-Bindung. |
| **INV-LOCAL-09** | Version Freeze Discipline | Strikte Einhaltung von Policy T-20260920-167562623 (kein Versions-Bump bei Pfad A/B). |
| **INV-LOCAL-10** | Statutory Disclaimer & SLA | Haftungsprivilegierung gem. § 521 BGB und verbindliche 48h Response / 5d Triage SLA. |

---

## 3. Laufzeit-Abhängigkeiten (Runtime SBOM)

| Paket | Deklarierte Version | Lizenz (SPDX) | Verwendung & Zweck |
| :--- | :--- | :--- | :--- |
| `PySide6` | `>=6.5.0` | LGPL-3.0-only | Desktop-GUI, Event-Loop, Widgets, Qt-Framework |
| `shiboken6` | `>=6.5.0` | LGPL-3.0-only | CPython-Bindings-Laufzeit für PySide6 |
| `PyMuPDF` | `>=1.24.10` | AGPL-3.0-or-later | High-Performance PDF-Parsing und Textextraktion |
| `python-docx` | `>=1.1.0` | MIT | Word (.docx) Extraktion und Berichtsgenerierung |
| `openpyxl` | `>=3.1.3` | MIT | Excel (.xlsx) Analyse (gehärtet gegen CVE-2024-34064) |
| `extract-msg` | `>=0.48.0` | MIT | Outlook E-Mail (.msg) Extraktion |
| `langchain` | `>=0.3.0` | MIT | Prompt-Orchestrierung und Document-Pipeline |
| `langchain-core` | `>=0.3.0` | MIT | Basis-Schnittstellen für RAG und Chat |
| `langchain-community` | `>=0.3.0` | MIT | Community-Treiber und Dokumentenlader |
| `langchain-ollama` | `>=0.2.0` | MIT | Native lokale Ollama-Anbindung |
| `langchain-chroma` | `>=0.1.0` | MIT | Vektorspeicher-Adapter für ChromaDB |
| `chromadb` | `>=0.5.4` | Apache-2.0 | Lokale Embedding-Vektordatenbank |

---

## 4. Optionale Erweiterungen & Backends

| Paket | Deklarierte Version | Lizenz (SPDX) | Verwendung & Zweck |
| :--- | :--- | :--- | :--- |
| `pytesseract` | `>=0.3.10` | Apache-2.0 | Optionale OCR-Bildtextextraktion |
| `Pillow` | `>=10.2.0` | HPND | Bildvorverarbeitung für OCR |
| `weasyprint` | `>=60.0` | BSD-3-Clause | Optionale PDF-Rendererweiterung |
| `openai` | `>=1.0.0` | Apache-2.0 | Optionaler Cloud-Zugriff (OpenAI API) |
| `anthropic` | `>=0.18.0` | MIT | Optionaler Cloud-Zugriff (Anthropic Claude API) |
| `tiktoken` | `>=0.5.0` | MIT | Exakte Token-Zählung für Cloud-Modelle |

---

## 5. Entwicklungs- & Test-Abhängigkeiten

| Paket | Deklarierte Version | Lizenz (SPDX) | Verwendung & Zweck |
| :--- | :--- | :--- | :--- |
| `pytest` | `>=9.1.1` | MIT | Test-Framework (gehärtet gegen CVE-2025-7117) |
| `pytest-asyncio` | `>=1.4.0` | Apache-2.0 | Asynchrone Testausführung |
| `pytest-timeout` | `>=2.4.0` | MIT | Timeout-Sicherung gegen Test-Hänger |
| `ruff` | `>=0.9.0` | MIT / Apache-2.0 | High-Speed Linter und Code-Formatierer |

---

*Vollständige Lizenztexte und URLs sind zusätzlich in `THIRD_PARTY_LICENSES.txt` dokumentiert.*
