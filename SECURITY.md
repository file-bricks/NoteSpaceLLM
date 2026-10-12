# Security Policy / Sicherheitsrichtlinie

Stand: 2026-10-12 | Deutsch / English

---

## Deutsch

### Unterstützte Versionen

| Version | Unterstützt | Anmerkungen |
| ------- | ----------- | ----------- |
| 1.0.x   | :white_check_mark: | Aktuelle Versionsreihe; Sicherheitsmeldungen können über die unten genannten Wege eingereicht werden |
| < 1.0.0 | :x:         | Vorabversionen werden nicht mehr gepflegt |

### Sicherheitsarchitektur & Datenflüsse

NoteSpaceLLM ist ein Local-First-Werkzeug. Der Datenfluss hängt vom ausgewählten Modell- und Embedding-Endpunkt ab:

1. **Lokaler Betrieb und Remote-Datenfluss**: Dokumentextraktion, Chunking und der ChromaDB-Vektorindex laufen lokal. Wird ein entfernter LLM- oder Embedding-Endpunkt konfiguriert, werden die dafür verwendeten Dokumenttexte, Embeddings, Prompts und Kontext an diesen Endpunkt gesendet. Die Anwendung deaktiviert die anonymisierte ChromaDB-Telemetrie für ihren lokalen Client und implementiert keine eigene Telemetrie.
2. **Parser-Abhängigkeiten**: Für XML-, ZIP- und PDF-Parsing sind Mindestversionen in den Projektmetadaten deklariert. Diese Versionsangaben sind keine Prüfung der gesamten Abhängigkeitskette und keine Garantie gegen schädliche Dateien.
3. **Umgang mit API-Schlüsseln**: Gespeicherte Ollama-Schlüssel werden über unterstützte native Zugangsdienste des Betriebssystems abgerufen; die Verfügbarkeit und der Schutz hängen von OS und Konfiguration ab und sind keine Garantie für Transportsicherheit. `NOTESPACELLM_OLLAMA_API_KEY` überschreibt den gespeicherten Ollama-Schlüssel und wird nicht persistiert. Ältere Klartextschlüssel werden erst nach ausdrücklicher Migration verwendet. Gespeicherte API-Schlüsselfelder und Authorization-Header werden nicht protokolliert; gespeicherte Credential-Felder werden nicht in Workspace-Exports aufgenommen. Frei verfasste Berichte und Chats können dennoch Geheimnisse enthalten und müssen vor dem Weitergeben geprüft werden.
4. **Remote-Transport**: Ollama sendet Dokumenttexte für Embeddings sowie Prompts und Kontext für Antworten an die konfigurierte URL. Ein API-Schlüssel wird als Bearer-Header mitgesendet. HTTP bietet keine Transportverschlüsselung; bei HTTPS hängt der Schutz vom Endpunkt und dessen Zertifikat ab.

### Meldung von Sicherheitslücken

Wenn Sie eine Sicherheitslücke in NoteSpaceLLM entdecken, melden Sie diese bitte vertraulich:

1. **Bevorzugter Meldeweg**: Nutzen Sie die private Schwachstellenmeldung auf GitHub:
   [GitHub Security Advisory Einreichung](https://github.com/file-bricks/NoteSpaceLLM/security/advisories)
2. **E-Mail-Kontakt**: Sollte GitHub nicht verfügbar sein, kontaktieren Sie uns direkt unter:
   `security@file-bricks.org`
3. **Dach- und Fallback-Kontakt**: `support@lukasgeiger.com`

**Bitte eröffnen Sie keine öffentlichen Issues für ungepatchte Sicherheitslücken.**

### Angestrebte Reaktionszeiten

- **Erstbestätigung**: Ziel sind **48 Stunden** nach Eingang der Meldung.
- **Triage & Schweregrad-Einstufung**: Ziel sind **5 Werktage**.
- Diese Zeiten sind Ziele, keine garantierte SLA oder Zusage für einen Patch-Zeitplan.

### Wartung

Für laufende Wartung oder Verfügbarkeit gibt es keine Zusage.

---

## English

### Supported Versions

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| 1.0.x   | :white_check_mark: | Current release series; security reports may be submitted through the channels below |
| < 1.0.0 | :x:                | Pre-release versions are no longer maintained |

### Security Architecture & Data Flows

NoteSpaceLLM is a local-first tool. Data flow depends on the selected model and embedding endpoints:

1. **Local operation and remote data flow**: Document extraction, chunking, and the ChromaDB vector index run locally. If a remote LLM or embedding endpoint is configured, the document text, embeddings, prompts, and context used by that operation are sent to that endpoint. The application disables ChromaDB's anonymized telemetry for its local client and does not implement its own telemetry.
2. **Parser dependencies**: Minimum versions for XML, ZIP, and PDF parsing packages are declared in project metadata. These version declarations are not an audit of the full dependency chain or a guarantee against malicious files.
3. **API Key Handling**: Saved Ollama keys are accessed through supported native operating-system credential services; availability and protection depend on the OS and its configuration and do not guarantee transport security. `NOTESPACELLM_OLLAMA_API_KEY` overrides a saved Ollama key and is not persisted. Legacy plaintext keys are not used until explicitly migrated. Saved API key fields and Authorization headers are not logged; saved credential fields are not included in workspace exports. User-authored reports and chats may still contain secrets and should be reviewed before sharing.
4. **Remote Transport**: Ollama sends document text for embeddings and prompts/context for responses to the configured URL. An API key is sent in a Bearer header. HTTP does not encrypt transport; with HTTPS, protection depends on the endpoint and its certificate.

### Reporting a Vulnerability

If you discover a security vulnerability in NoteSpaceLLM, please report it confidentially:

1. **Preferred Method**: Submit a private advisory via GitHub:
   [GitHub Security Advisory Submission](https://github.com/file-bricks/NoteSpaceLLM/security/advisories)
2. **Direct Security Email**: `security@file-bricks.org`
3. **Umbrella / Fallback Contact**: `support@lukasgeiger.com`

**Please do not open public issues for undisclosed security vulnerabilities.**

### Target Response Times

- **Initial confirmation**: The target is within **48 hours** of receiving the report.
- **Triage & severity assessment**: The target is within **5 business days**.
- These are targets, not a guaranteed SLA or a promise of a patch timeline.

### Maintenance

There is no promise of ongoing maintenance or availability.
