# NoteSpaceLLM Web/PWA-Companion

Der Companion ist der erste mobile und browserbasierte Reader für exportierte
`notespacellm-workspace-v1.json`-Dateien aus NoteSpaceLLM. Er bleibt bewusst
read-only für den importierten Workspace und erzeugt nur eigene
Review-Notizen.

## Ziel

- lokaler Import ohne Server-Upload
- mobile Lesbarkeit für Android, iOS und Browser
- Bericht, Dokumentmetadaten und ausgewählte Auszüge anzeigen
- importierte Workspace-Inhalte nur in der aktuellen Sitzung anzeigen; nach einem Neustart erneut importieren
- eigene Review-Notizen lokal speichern und als Markdown exportieren
- DE/EN/ES/ZH-Hans/JA/RU-Oberfläche mit Browser-/Workspace-Locale und
  manuellem Sprachumschalter

## Lokaler Start

Für einen kurzen lokalen Test reicht ein statischer Server:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m http.server 8765 -d web_companion
```

Danach im Browser öffnen:

```text
http://127.0.0.1:8765
```

## Tests

```powershell
cd web_companion
npm test
```

Der konkrete Android-/iOS-PWA-Ablauf steht in `PWA_TESTPLAN.md`.

## Scope des ersten Strangs

- kein Upload auf entfernte Server
- keine Bearbeitung des Workspaces im Browser
- keine vollständigen Rohdokumente, Vektordatenbanken oder gespeicherten API-Schlüsselfelder im Workspace-Export. Frei verfasste Berichte und Chats können dennoch Geheimnisse enthalten; prüfe sie vor dem Weitergeben.
- Workspace-Payloads werden nicht dauerhaft im Browser gespeichert; Review-Notizen und UI-Sprache sind separate lokale Daten
- kein nativer Android-/iOS-Clone
