# Security Policy / Sicherheitsrichtlinie

Stand: 2026-09-18 | Policy: Bilingual (DE/EN) | P-006 Core Level

---

## Deutsch

### Unterstützte Versionen

| Version | Unterstützt | Anmerkungen |
| ------- | ----------- | ----------- |
| 1.0.x   | :white_check_mark: | Aktiver Support, reguläre Sicherheits- und Wartungsupdates |
| < 1.0.0 | :x:         | Vorabversionen werden nicht mehr gepflegt |

### Sicherheitsarchitektur & Datenschutzgarantien

NoteSpaceLLM ist als **Local-First & Privacy-First Forschungs- und Dokumentenanalysewerkzeug** konzipiert:

1. **Lokale Verarbeitung & Zero-Egress**: Die Dokumentenextraktion (PDF, DOCX, XLSX, MSG), das Chunking, die Vektorspeicherung (ChromaDB) und lokale Sprachmodelle (via Ollama) laufen standardmäßig vollständig offline auf dem lokalen Gerät. Es erfolgt keinerlei unaufgeforderte Telemetrie oder externe Übertragung analysierter Dokumente.
2. **Schutz vor bösartigen Dokumenten**: Abhängigkeiten für XML-, Zip- und PDF-Parsing sind mit strengen Mindestversionen gegen Denial-of-Service (z. B. XML Entity Expansion CVE-2024-34064) und Speicherfehler gehärtet.
3. **Sicherer Umgang mit API-Schlüsseln**: Werden optionale Cloud-Modelle (OpenAI, Anthropic) genutzt, verbleiben die Schlüssel im Arbeitsspeicher bzw. im lokalen Keyring. API-Schlüssel werden niemals in Logdateien, getrackten Repositories oder Export-Paketen gespeichert.

### Meldung von Sicherheitslücken

Wenn Sie eine Sicherheitslücke in NoteSpaceLLM entdecken, melden Sie diese bitte vertraulich:

1. **Bevorzugter Meldeweg**: Nutzen Sie die private Schwachstellenmeldung auf GitHub:
   [GitHub Security Advisory Einreichung](https://github.com/file-bricks/NoteSpaceLLM/security/advisories)
2. **E-Mail-Kontakt**: Sollte GitHub nicht verfügbar sein, kontaktieren Sie uns direkt unter:
   `security@file-bricks.org`
3. **Dach- und Fallback-Kontakt**: `support@lukasgeiger.com`

**Bitte eröffnen Sie keine öffentlichen Issues für ungepatchte Sicherheitslücken.**

### Reaktionszeit & SLA

- **Erstbestätigung**: Innerhalb von **48 Stunden** nach Eingang der Meldung.
- **Triage & Schweregrad-Einstufung**: Innerhalb von **5 Werktagen**.
- **Sicherheits-Patch**: Kritische Schwachstellen werden prioritär behoben und mit einem Patch-Release bereitgestellt.

---

## English

### Supported Versions

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| 1.0.x   | :white_check_mark: | Active support, regular security and maintenance updates |
| < 1.0.0 | :x:                | Pre-release versions are no longer maintained |

### Security Architecture & Privacy Invariants

NoteSpaceLLM is engineered as a **Local-First & Privacy-First document analysis and research tool**:

1. **Local Processing & Zero-Egress**: Document parsing (PDF, DOCX, XLSX, MSG), text chunking, local vector storage (ChromaDB), and local model execution (via Ollama) occur entirely offline on your local device. There is zero unsolicited telemetry, tracking, or network egress of document contents.
2. **Malicious Document Defense**: Parsers and dependencies are hardened to secure floors to guard against XML Entity Expansion (CVE-2024-34064), archive bombs, and memory corruption vulnerabilities.
3. **Secure API Key Management**: When optional cloud models (OpenAI, Anthropic) are enabled, user API keys reside in process memory or secure OS keyrings. Keys are never logged, exported, or tracked in git repositories.

### Reporting a Vulnerability

If you discover a security vulnerability in NoteSpaceLLM, please report it confidentially:

1. **Preferred Method**: Submit a private advisory via GitHub:
   [GitHub Security Advisory Submission](https://github.com/file-bricks/NoteSpaceLLM/security/advisories)
2. **Direct Security Email**: `security@file-bricks.org`
3. **Umbrella / Fallback Contact**: `support@lukasgeiger.com`

**Please do not open public issues for undisclosed security vulnerabilities.**

### Response Time & SLA

- **Initial Confirmation**: Within **48 hours** of receiving the report.
- **Triage & Severity Assessment**: Within **5 business days**.
- **Security Patch**: Critical vulnerabilities receive top priority and will be released in an expedited patch update.
