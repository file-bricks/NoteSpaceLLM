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

## Aktueller Belegstand (2026-10-12)

Die `OK`-Einträge oben belegen nur vorhandene Artefakte und einfache lokale
Formatprüfungen. Sie belegen weder eine Store-Einreichung noch Veröffentlichung
oder Zertifizierung. In den gelesenen Metadaten gibt es eine Versionsabweichung:
`pyproject.toml` und die Laufzeit melden `1.0.0`; das Root-Manifest
`store_package.json` nennt `1.1.0.0`, während
`releases/windowsstore/store_package.json` `1.0.0.0` nennt. Diese Abweichung
bleibt ungeklärt und wurde wegen des Versions-Freeze nicht geändert. Es wurde
keine Store-Einreichung oder Veröffentlichung ausgeführt.

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
