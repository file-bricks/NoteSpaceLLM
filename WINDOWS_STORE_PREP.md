# Windows Store Release Preparation — NoteSpaceLLM Pro

Stand: 2026-11-03  
Status: Bereit zur Einreichung / Staged  

---

## 1. Identität & Partner Center Metadaten

| Eigenschaft | Wert |
|---|---|
| **App-Name** | NoteSpace LLM Pro |
| **Package / Identity Name** | `Geiger.NoteSpaceLLM` |
| **Publisher ID** | `CN=52596601-BAB4-4F3F-B182-E8F3F273B202` |
| **Publisher Display Name** | `Geiger` |
| **Version** | `1.0.0.0` |
| **Package Version** | `1.0.0.0` |
| **Haupt-Executable** | `NoteSpaceLLM.exe` |
| **Kategorie** | `Productivity` |
| **Altersfreigabe** | `3+` (IARC konform) |
| **Preise** | Kostenlos / Free |
| **Support-URL** | `https://github.com/doc-bricks/NoteSpaceLLM/issues` |
| **Datenschutz-URL** | `https://github.com/doc-bricks/NoteSpaceLLM/blob/master/PRIVACY_POLICY.md` |

---

## 2. Richtlinien-Konformität (Microsoft Store Policies)

### Policy 10.1.3 — Suchbegriffe (Search Terms / Keywords)
- **Vorgabe:** Maximal 7 relevante Suchbegriffe pro Sprache, keine Keyword-Stuffing-Verstöße.
- **Deutsch (7 Keywords):**
  1. Notizen
  2. Dokumentenanalyse
  3. Lokale KI
  4. RAG-Suche
  5. PDF-Zusammenfassung
  6. Forschungsassistent
  7. Wissensdatenbank
- **Englisch (7 Keywords):**
  1. notes
  2. document analysis
  3. local AI
  4. RAG search
  5. PDF summary
  6. research assistant
  7. knowledge base

### Policy 10.2 — Datenschutz (Privacy)
- `PRIVACY_POLICY.md` liegt im Projektstamm und deklariert die lokale Datenverarbeitung.
- Dokumente verbleiben standardmäßig auf dem lokalen Rechner; Netzwerkaufrufe erfolgen nur bei konfigurierter Cloud-LLM-Nutzung.

### Policy 10.5 — Altersfreigabe (Age Rating)
- Altersfreigabe `3+`, da reine Produktivitäts- und Textanalyse-Software ohne anstößige Inhalte.

---

## 3. Paketierung & WACK-Workflow

1. **Vorbereitung:**
   ```powershell
   python scripts\check_store_readiness.py
   python scripts\run_windows_wack.py
   ```
2. **MSIX-Erstellung:**
   Ausführen von `releases\windowsstore\BUILD.md` zur Generierung des signierten MSIX-Pakets.
3. **WACK-Zertifizierung:**
   Das Windows App Certification Kit prüft das fertige MSIX auf Manifest-Integrität, Capabilities und Binary Security.
