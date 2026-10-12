# NoteSpaceLLM Companion – Android/iOS-PWA-Testplan

Stand: 2026-05-30

## Ziel

Dieser Testplan prüft genau den mobilen P2-Pfad des Companions:

- Installierbarkeit als PWA auf Android und iOS
- lokaler JSON-Import ohne Server-Upload
- Offline-Start der PWA-Shell; ein Workspace muss nach erneutem Öffnen erneut importiert werden
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
| A4 | Android | Workspace importieren, PWA schließen, offline erneut öffnen | PWA-Shell startet; Workspace wird nicht wiederhergestellt und muss erneut importiert werden |
| A5 | Android | Review-Notizen exportieren | Markdown-Datei wird erzeugt oder Download wird angeboten |
| I1 | iOS | Seite in Safari öffnen | Layout bleibt mobil lesbar, Import- und Notizbereich bleiben bedienbar |
| I2 | iOS | Teilen → Zum Home-Bildschirm | Companion erscheint als Home-Screen-PWA |
| I3 | iOS | Workspace importieren | Bericht und Dokumentauszüge werden lokal angezeigt |
| I4 | iOS | Workspace importieren, Safari/PWA schließen, offline erneut öffnen | PWA-Shell startet; Workspace wird nicht wiederhergestellt und muss erneut importiert werden |
| I5 | iOS | Review-Notizen exportieren | Markdown-Export wird gestartet; falls iOS Download begrenzt, Share-/Datei-Dialog prüfen |

## Checkliste pro Lauf

- [ ] Import ohne Fehlermeldung
- [ ] Status nennt geladene Quelle korrekt
- [ ] Plattform-Pill zeigt Android, iPhone/iPad oder Browser korrekt
- [ ] Offline-Hinweis reagiert auf Online/Offline-Wechsel
- [ ] Cache-Hinweis zeigt, dass keine Workspace-Payload dauerhaft gespeichert ist
- [ ] Review-Notizen bleiben getrennt vom Workspace lokal erhalten
- [ ] Ein erneuter Start verlangt den Dateiimport; lokale UI-Sprache bleibt erhalten

## Bekannte Grenzen

- Der Companion bleibt read-only für importierte Workspaces.
- Importierte Workspace-Payloads bleiben nur in der aktuellen Sitzung; Offline-Verfügbarkeit betrifft die PWA-Shell, nicht Workspace-Inhalte.
- Vollständige Rohdokumente, lokale ChromaDB und gespeicherte API-Schlüsselfelder werden nicht in die PWA übernommen. Frei verfasste Berichte und Chats können dennoch Geheimnisse enthalten und sind vor dem Weitergeben zu prüfen.
- Native Android-/iOS-Hüllen sind weiterhin kein Pflichtpfad; PWA bleibt die Referenzlinie.
