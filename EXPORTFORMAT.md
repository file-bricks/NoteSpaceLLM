# Exportformat -- notespacellm-workspace-v1

Stand: 2026-05-28

## Zweck

`notespacellm-workspace-v1.json` ist der geplante Austauschvertrag zwischen der Desktop-App und Web-/PWA-/Mobile-Companions. Das Format soll mobile Recherche- und Review-Workflows ermöglichen, ohne lokale Rohdatenordner, Vektordatenbanken oder API-Schlüssel zu kopieren.

Der erste Consumer liegt unter `web_companion/`: ein read-only PWA-Reader, der Workspace-JSON lokal im Browser importiert, Bericht und Dokumentmetadaten anzeigt und eigene Review-Notizen als Markdown exportiert.

## Datenschutzregeln

- API-Schlüssel werden nie exportiert.
- `chroma_db/`, lokale Datenbanken und Cache-Verzeichnisse werden nie exportiert.
- Rohdokumente werden standardmäßig nicht eingebettet.
- Dokumentauszüge werden nur exportiert, wenn sie bereits für Bericht, Chat, Prompt oder Review ausgewählt wurden.
- Externe Provider werden nur als Typ und Konfigurationshinweis dokumentiert, nicht mit geheimen Werten.

## Minimales Schema

```json
{
  "schema_version": "notespacellm-workspace-v1",
  "app": {
    "name": "NoteSpaceLLM",
    "version": "1.0.0",
    "exported_at": "2026-05-26T00:00:00Z"
  },
  "workspace": {
    "title": "Projektname",
    "question": "Zentrale Fragestellung",
    "workflow_type": "analysis",
    "locale": "de"
  },
  "documents": [
    {
      "id": "doc-1",
      "name": "quelle.pdf",
      "path_hint": "quelle.pdf",
      "format": "pdf",
      "selected": true,
      "content_included": false,
      "excerpts": [
        {
          "id": "doc-1-excerpt-1",
          "text": "Kurzer ausgewählter Auszug.",
          "source_hint": "Seite 3"
        }
      ]
    }
  ],
  "report": {
    "title": "Bericht",
    "format": "markdown",
    "content": "# Bericht\n\n..."
  },
  "chat": {
    "messages": []
  },
  "provider": {
    "mode": "local-or-remote",
    "name": "ollama",
    "secret_exported": false
  }
}
```

## Erweiterungsregeln

- Neue optionale Felder sind erlaubt, solange bestehende Felder ihre Bedeutung behalten.
- Consumer müssen unbekannte Felder ignorieren.
- Breaking Changes erhöhen den Schema-Namen auf `notespacellm-workspace-v2`.
- Große Binärdateien bleiben außerhalb des JSON und werden nur über optionale Manifeste referenziert.

## Aktuelle Implementierungsaufgaben

Die Desktop-App soll eine Funktion `build_workspace_export_payload()` erhalten, die aus aktuellem Projekt, Dokumentauswahl, Workflow, Bericht und optionalem Chat-Verlauf dieses Schema erzeugt. Danach kann eine Schreibfunktion das JSON atomar als UTF-8-Datei speichern.

Der Web/PWA-Companion kann das Schema bereits lesen und validiert es mit `node --test tests/library.test.mjs`. Bis der Desktop-Export implementiert ist, dient die Demo-Workspace-Funktion in `web_companion/library.js` als Testdatenquelle.
