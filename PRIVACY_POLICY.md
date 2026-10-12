# Privacy Policy

## Deutsch

NoteSpaceLLM ist als lokale Desktop-Anwendung ausgelegt. Projektdateien, Dokumentindexe, Profile, Workflow-Einstellungen und Exporte bleiben standardmäßig auf dem lokalen Gerät.

Nicht für Git vorgesehen sind insbesondere `data/`, `profiles/`, `workflows/`, `output/`, `chroma_db/`, lokale Builds und persönliche Konfigurationsdateien. Diese Pfade sind in `.gitignore` ausgeschlossen.

Wenn externe oder entfernte LLM-Provider aktiviert werden, können Prompts und ausgewählte Dokumentauszüge an diese Dienste oder Server übertragen werden. Dazu zählen insbesondere OpenAI, Anthropic, Claude Code und Remote-Ollama-Server. Die Verantwortung für die Auswahl geeigneter Provider und den Umgang mit vertraulichen Dokumenten liegt beim Nutzer.

Bei einem entfernten Ollama-Endpunkt werden außerdem Dokumenttexte zur Erstellung von Embeddings sowie Prompts und Kontext für die Antwortgenerierung an die konfigurierte URL gesendet. Ein gespeicherter Ollama-Schlüssel wird als Bearer-Header an diesen Endpunkt übermittelt. HTTP verschlüsselt weder Inhalt noch Zugangsdaten; HTTPS hängt vom Endpunkt und dessen Zertifikat ab. NoteSpaceLLM prüft nicht, welchem Betreiber ein entfernter Endpunkt gehört.

Die Anwendung deaktiviert die anonymisierte ChromaDB-Telemetrie für ihren lokalen Client und implementiert keine eigene Telemetrie.

Gespeicherte Ollama-Schlüssel nutzt die App über unterstützte native Zugangsdienste des Betriebssystems. Verfügbarkeit und Schutz hängen von Betriebssystem und dessen Konfiguration ab. `NOTESPACELLM_OLLAMA_API_KEY` überschreibt den gespeicherten Schlüssel, wird aber nicht von der App gespeichert. Vorhandene ältere Klartextschlüssel bleiben bis zu einer ausdrücklich gestarteten Migration in der Konfigurationsdatei und werden vorher nicht gesendet.

Workspace-Exporte können den vollständigen Bericht, den Chatverlauf und ausgewählte abgeschlossene Dokumentauszüge enthalten. Sie werden nicht anonymisiert. Die PWA hält importierte Workspace-Inhalte nur in der aktuellen Sitzung; lokal gespeichert werden eigene Review-Notizen und die UI-Sprache.

## English

NoteSpaceLLM is designed as a local desktop application. Project files, document indexes, profiles, workflow settings, and exports stay on the local device by default.

Paths such as `data/`, `profiles/`, `workflows/`, `output/`, `chroma_db/`, local builds, and personal configuration files are not intended for Git and are excluded via `.gitignore`.

When external or remote LLM providers are enabled, prompts and selected document excerpts may be sent to those services or servers. This includes OpenAI, Anthropic, Claude Code, and remote Ollama servers. Users are responsible for choosing suitable providers and handling confidential documents appropriately.

With a remote Ollama endpoint, document text used to create embeddings and prompts/context sent for answer generation are also sent to the configured URL. A saved Ollama key is sent to that endpoint in a Bearer header. Plain HTTP encrypts neither content nor credentials; HTTPS protection depends on the endpoint and its certificate. NoteSpaceLLM does not verify who operates a remote endpoint.

The application disables ChromaDB's anonymized telemetry for its local client and does not implement its own telemetry.

Saved Ollama keys are accessed through supported native operating-system credential services. Availability and protection depend on the operating system and its configuration. `NOTESPACELLM_OLLAMA_API_KEY` overrides a saved key but is not saved by the app. Existing legacy plaintext keys remain in the configuration file until the user explicitly starts migration and are not sent before then.

Workspace exports can contain the complete report, chat history, and selected completed document excerpts. They are not anonymized. The PWA keeps imported workspace content only in the current session; only the user's review notes and UI language are stored locally.
