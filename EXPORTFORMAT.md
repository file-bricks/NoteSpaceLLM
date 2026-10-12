# Exportformat -- notespacellm-workspace-v1

Stand: 2026-06-05

## Zweck

`notespacellm-workspace-v1.json` ist der Austauschvertrag zwischen der
Desktop-App und Web-/PWA-/Mobile-Companions. Der Export kann den vollständigen
Bericht und Chatverlauf sowie ausgewählte abgeschlossene Dokumentauszüge
enthalten. Er wird nicht anonymisiert. Lokale Rohdokumente, Vektordatenbanken
und gespeicherte API-Schlüsselfelder werden nicht kopiert. Frei verfasste
Bericht- und Chattexte können dennoch Geheimnisse enthalten und sollten vor dem
Weitergeben geprüft werden.

Der erste Consumer liegt unter `web_companion/`: ein read-only PWA-Reader, der
Workspace-JSON lokal im Browser importiert, Bericht und Dokumentmetadaten
anzeigt und eigene Review-Notizen als Markdown exportiert. Der importierte
Workspace bleibt nur in der aktuellen Sitzung; zum erneuten Öffnen muss die
Datei erneut importiert werden. Review-Notizen und UI-Sprache werden lokal
gespeichert.

## Implementierungsstatus

- Desktop-Export ist umgesetzt: `src/core/workspace_exporter.py` erzeugt das
  Payload und schreibt es atomar als UTF-8-JSON.
- GUI-Auslöser ist vorhanden: `Datei -> Workspace exportieren (JSON)...`.
- Tests: `tests/test_workspace_export.py` deckt Schema, Datenschutzregeln,
  UTF-8, atomare Ausgabe und Auszugslogik ab.
- Web/PWA-Companion validiert und liest das Format über `web_companion/library.js`
  und `web_companion/tests/library.test.mjs`.

## Datenschutzregeln

- Gespeicherte API-Schlüsselfelder werden nicht exportiert. Frei verfasste
  Bericht- und Chattexte werden nicht auf Geheimnisse geprüft und sollten vor
  dem Weitergeben überprüft werden.
- `chroma_db/`, lokale Datenbanken und Cache-Verzeichnisse werden nie exportiert.
- Vollständige Rohdokumente werden nicht eingebettet; ausgewählte abgeschlossene
  Sub-Query-Ergebnisse erscheinen als auf 2.000 Zeichen begrenzte Auszüge.
- Auszüge erscheinen nur für ausgewählte Dokumente und nur, wenn
  `include_subquery_excerpts` aktiviert ist.
- Der aktuelle vollständige Bericht und Chatnachrichten von Nutzern und Assistenten
  können enthalten sein; der Export ist nicht anonymisiert.
- Externe Provider werden nur als Typ und lokale/entfernte/unklare Einordnung
  dokumentiert. Die konfigurierte URL und geheime Werte werden nicht exportiert.
- Lokale absolute Pfade werden auf redigierte Hinweise oder relative
  `path_hint`-Werte reduziert.
- Vor dem Schreiben zeigt die Desktop-App die enthaltenen Bereiche an und fragt
  ausdrücklich nach Bestätigung.

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
    "id": "8f0c6a2e-…",
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
- Große Binärdateien bleiben außerhalb des JSON und werden nur über optionale
  Manifeste referenziert.

## Nächste Format-Aufgaben

- Companion-Rückkanal erst definieren, wenn echte Review-Notizen reimportiert
  werden sollen.
- Geräte-Smokes gegen `web_companion/PWA_TESTPLAN.md` mit realen Android-/iOS-
  oder Emulatorumgebungen durchführen.
- Bei Bedarf ein separates optionales Rohdokument-Manifest entwerfen; nicht als
  Standardbestandteil des Workspace-JSON.
