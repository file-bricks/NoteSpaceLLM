# NoteSpaceLLM

Ein privater NotebookLM-Clone für lokale Dokumentenanalyse und Berichterstellung.

## Features

- **Dokumentenverwaltung**: Dateien und Verzeichnisse per Drag & Drop hinzufügen
- **Selektive Auswahl**: Dokumente für Berichterstellung auswählen/abwählen
- **Detailrecherchen**: Rechtsklick für dokumentspezifische Analysen (Sub-Queries)
- **Workflow-Visualisierung**: Grafische Darstellung des Berichtsprozesses
- **Chat-Interface**: Interaktives Chatten über die Dokumente mit LLM
- **Multi-Format-Export**: Ausgabe in MD, PDF, DOCX, HTML, TXT
- **Profile**: Wiederverwendbare Ausgabeformat-Kombinationen

## Installation

```bash
# Repository klonen oder Ordner kopieren
cd NoteSpaceLLM

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
python main.py
```

## Abhängigkeiten prüfen

```bash
python main.py --check
```

## LLM-Konfiguration

### Ollama (Lokal - Empfohlen)

1. [Ollama installieren](https://ollama.ai)
2. Modell herunterladen: `ollama pull llama3`
3. In der App: Menü > LLM > Ollama verwenden

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

### Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Verwendung

### 1. Dokumente hinzufügen

- **Drag & Drop**: Dateien/Ordner in das linke Panel ziehen
- **Button**: "Dateien hinzufügen" oder "Ordner hinzufügen"

### 2. Dokumente auswählen

- Checkbox: Dokumente für Analyse ein-/ausschließen
- Buttons: "Alle" / "Keine" für Massenauswahl

### 3. Detailrecherchen (optional)

Rechtsklick auf ein Dokument:
- **Zusammenfassung erstellen**: Automatische Zusammenfassung
- **Informationen extrahieren**: Spezifische Daten finden
- **Analysieren**: Gezielte Analyse
- **Frage stellen**: Konkrete Frage zum Dokument

### 4. Hauptfragestellung definieren

Im Workflow-Panel die zentrale Fragestellung eingeben.

### 5. Workflow/Berichtsart wählen

- **Analyse**: Umfassende Analyse mit Empfehlungen
- **Zusammenfassung**: Kurze Zusammenfassung
- **Forschungsbericht**: Akademische Struktur
- **Vergleich**: Systematischer Dokumentenvergleich

### 6. Bericht erstellen

Klick auf "Bericht erstellen" - die Ausgabe erscheint im rechten Panel.

### 7. Exportieren

Ausgabeformate wählen und "Exportieren" klicken.

## Projektstruktur

```
NoteSpaceLLM/
├── main.py                 # Startpunkt
├── requirements.txt        # Abhängigkeiten
├── README.md              # Diese Datei
├── src/
│   ├── core/              # Kernfunktionalität
│   │   ├── document_manager.py   # Dokumentenverwaltung
│   │   ├── text_extractor.py     # Textextraktion
│   │   ├── sub_query.py          # Detailrecherchen
│   │   └── project.py            # Projektverwaltung
│   ├── gui/               # PyQt6 Benutzeroberfläche
│   │   ├── main_window.py        # Hauptfenster
│   │   ├── document_panel.py     # Dokument-Panel
│   │   ├── workflow_panel.py     # Workflow-Panel
│   │   ├── chat_panel.py         # Chat-Panel
│   │   └── output_panel.py       # Ausgabe-Panel
│   ├── llm/               # LLM-Integration
│   │   ├── client.py             # Basis-Client
│   │   ├── ollama_client.py      # Ollama
│   │   ├── openai_client.py      # OpenAI
│   │   └── anthropic_client.py   # Anthropic
│   └── reports/           # Berichterstellung
│       ├── generator.py          # Berichtsgenerierung
│       ├── templates.py          # Vorlagen
│       └── exporter.py           # Export
├── data/                  # Datenverzeichnis
├── workflows/             # Workflow-Definitionen
├── profiles/              # Ausgabeprofile
└── output/                # Exportierte Berichte
```

## Unterstützte Dateiformate

| Format | Lesen | Schreiben |
|--------|-------|-----------|
| PDF    | ✅    | ✅        |
| DOCX   | ✅    | ✅        |
| DOC    | ⚠️    | -         |
| TXT    | ✅    | ✅        |
| MD     | ✅    | ✅        |
| XLSX   | ✅    | -         |
| HTML   | -     | ✅        |
| EML    | ✅    | -         |
| MSG    | ✅    | -         |

⚠️ .doc benötigt antiword oder LibreOffice

## Tips

1. **Große Dokumente**: Bei vielen Dokumenten zuerst nur wichtige auswählen
2. **Detailrecherchen**: Für bessere Ergebnisse gezielte Sub-Queries nutzen
3. **Ollama**: Für Datenschutz und Offline-Nutzung empfohlen
4. **Workflow anpassen**: Schritte können umgeordnet werden

## Entwicklung

Basiert auf dem BACH-System (Personal Agentic OS) und nutzt dessen:
- Document Collector Service
- Report Workflow Service
- Text Extractor Patterns

## Lizenz

Privates Projekt - Nutzung nach Absprache.

---

Erstellt mit BACH v1.1 | 2026
