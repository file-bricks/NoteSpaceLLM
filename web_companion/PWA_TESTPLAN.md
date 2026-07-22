# NoteSpaceLLM Companion – Android/iOS-PWA-Testplan

Stand: 2026-07-22

## Ziel

Dieser Testplan prüft genau den mobilen P2-Pfad des Companions:

- Installierbarkeit als PWA auf Android und iOS
- lokaler JSON-Import ohne Server-Upload
- Offline-Start mit zuletzt lokal gespeichertem Workspace
- Export lokaler Review-Notizen

## Voraussetzungen

- Ein exportierter `notespacellm-workspace-v1.json`-Workspace
- Lokaler Companion-Start über statischen Server
- Android-Testgerät mit Chrome oder Edge
- iPhone/iPad mit Safari

## Lokaler Start

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m http.server 8765 -d web_companion
```

URL: `http://127.0.0.1:8765`

## Testmatrix

| ID | Plattform | Prüfschritt | Erwartung |
|---|---|---|---|
| A1 | Android | Seite in Chrome öffnen | Hero, Status und PWA-Hinweise sind ohne horizontales Scrollen sichtbar |
| A2 | Android | „Zum Startbildschirm hinzufügen“ oder Installieren auslösen | Companion erscheint als eigene PWA mit Titel und Theme-Farbe |
| A3 | Android | Workspace importieren | Bericht, Dokumente und lokale Review-Notizen werden sichtbar |
| A4 | Android | Netz deaktivieren, PWA neu öffnen | Zuletzt gespeicherter Workspace wird lokal wiederhergestellt |
| A5 | Android | Review-Notizen exportieren | System-Share-Sheet erhält genau eine Markdown-Datei; ohne File-Share-Unterstützung wird sie lokal heruntergeladen |
| I1 | iOS | Seite in Safari öffnen | Layout bleibt mobil lesbar, Import- und Notizbereich bleiben bedienbar |
| I2 | iOS | Teilen → Zum Home-Bildschirm | Companion erscheint als Home-Screen-PWA |
| I3 | iOS | Workspace importieren | Bericht und Dokumentauszüge werden lokal angezeigt |
| I4 | iOS | Safari/PWA offline erneut öffnen | Zuletzt gespeicherter Workspace wird lokal wiederhergestellt |
| I5 | iOS | Review-Notizen exportieren | Safari/PWA öffnet den System-Share-Sheet mit genau einer Markdown-Datei; bei fehlender Unterstützung greift der lokale Download-Fallback |

## Checkliste pro Lauf

- [ ] Import ohne Fehlermeldung
- [ ] Status nennt geladene Quelle korrekt
- [ ] Plattform-Pill zeigt Android, iPhone/iPad oder Browser korrekt
- [ ] Offline-Hinweis reagiert auf Online/Offline-Wechsel
- [ ] Cache-Hinweis zeigt den zuletzt gespeicherten Workspace
- [ ] „Workspace-Cache löschen“ entfernt den Offline-Startpfad wie erwartet
- [ ] Share-Abbruch erzeugt keinen zusätzlichen Download; Share-Fehler fällt auf
      den lokalen Markdown-Download zurück

## Bekannte Grenzen

- Der Companion bleibt read-only für importierte Workspaces.
- Rohdokumente, ChromaDB und API-Schlüssel werden nicht in die PWA übernommen.
- Native Android-/iOS-Hüllen sind weiterhin kein Pflichtpfad; PWA bleibt die Referenzlinie.
- Der System-Share-Sheet ist eine bewusste lokale Übergabe an eine vom Nutzer
  gewählte App. NoteSpaceLLM lädt dabei selbst nichts auf einen Server hoch.
