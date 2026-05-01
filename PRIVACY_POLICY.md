# Privacy Policy

## Deutsch

NoteSpaceLLM ist als lokale Desktop-Anwendung ausgelegt. Projektdateien, Dokumentindexe, Profile, Workflow-Einstellungen und Exporte bleiben standardmäßig auf dem lokalen Gerät.

Nicht für Git vorgesehen sind insbesondere `data/`, `profiles/`, `workflows/`, `output/`, `chroma_db/`, lokale Builds und persönliche Konfigurationsdateien. Diese Pfade sind in `.gitignore` ausgeschlossen.

Wenn externe oder entfernte LLM-Provider aktiviert werden, können Prompts und ausgewählte Dokumentauszüge an diese Dienste oder Server übertragen werden. Dazu zählen insbesondere OpenAI, Anthropic, Claude Code und Remote-Ollama-Server. Die Verantwortung für die Auswahl geeigneter Provider und den Umgang mit vertraulichen Dokumenten liegt beim Nutzer.

## English

NoteSpaceLLM is designed as a local desktop application. Project files, document indexes, profiles, workflow settings, and exports stay on the local device by default.

Paths such as `data/`, `profiles/`, `workflows/`, `output/`, `chroma_db/`, local builds, and personal configuration files are not intended for Git and are excluded via `.gitignore`.

When external or remote LLM providers are enabled, prompts and selected document excerpts may be sent to those services or servers. This includes OpenAI, Anthropic, Claude Code, and remote Ollama servers. Users are responsible for choosing suitable providers and handling confidential documents appropriately.
