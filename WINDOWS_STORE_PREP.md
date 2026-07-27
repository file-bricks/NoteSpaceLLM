# Windows Store Preparation — NoteSpaceLLM

Stand: 2026-07-27

## Artefakt-Inventar

| Artefakt | Zweck | Status |
|---|---|---|
| `store_package.json` | Manifest-Metadaten & Capabilities für Windows Store | OK |
| `releases/windowsstore/store_settings.json` | Release-Konfiguration für MSIX Packaging | OK |
| `STORE_LISTING.md` | Zweisprachiges (DE/EN) Store-Listing | OK |
| `PRIVACY_POLICY.md` | Datenschutzerklärung für lokale Datenverarbeitung | OK |
| `SUPPORT.md` | Kundensupport-Kontakte & FAQ | OK |
| `THIRD_PARTY_LICENSES.txt` | Inventar aller Drittanbieter-Lizenzen | OK |
| `scripts/check_store_readiness.py` | Automatisierter Preflight-Auditor | OK |
| `tests/test_store_readiness.py` | Pytest-Guard für Store-Compliance | OK |

## Publisher Credentials
- **Publisher ID:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`
- **Publisher Display Name:** `Lukas Geiger`
- **Identity Name:** `Geiger.NoteSpaceLLM`
- **Package Family Name:** `Geiger.NoteSpaceLLM_52596601bab44f3f`

## Capabilities
- `runFullTrust` — erforderlich für PySide6 Desktop-Laufzeit, lokalen ChromaDB-Vektorspeicher und PDF-Extraktion.

## Preflight Audit Command
```bash
python scripts/check_store_readiness.py
```
