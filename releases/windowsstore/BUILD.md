# NoteSpaceLLM Pro — Windows Store Build- & Packaging-Anleitung

## Voraussetzungen

1. Python 3.10+ mit PySide6
2. PyInstaller für den Desktop-EXE-Build
3. Windows 10/11 SDK mit makeappx.exe, signtool.exe und appcert.exe
4. Lokaler Arbeitsbereich außerhalb von Cloud-Ordnern, z. B. `C:\_Local_DEV\codex_build\notespacellm-store`

## Schritt 0: Store-Metadaten & Screenshots validieren

```powershell
Set-Location C:\_Local_DEV\repos\NoteSpaceLLM
python scripts\check_store_readiness.py
python scripts\run_windows_wack.py
```

Erwartetes Ergebnis:
- Alle Manifeste, Kacheln und Metadaten PASS (0 Fehler)
- WACK-Preflight-Report generiert unter `releases\windowsstore\test_reports\`

## Schritt 1: Desktop-Executable mit PyInstaller bauen

```powershell
Set-Location C:\_Local_DEV\repos\NoteSpaceLLM
.\build_exe.bat
```

Erzeugt die Standalone-Anwendung `dist\NoteSpaceLLM\NoteSpaceLLM.exe` bzw. `dist\NoteSpaceLLM.exe`.

## Schritt 2: Desktop-Bridge AppX-Layout vorbereiten

```powershell
$StoreDir = "C:\_Local_DEV\codex_build\notespacellm-store"
New-Item -ItemType Directory -Force -Path "$StoreDir\PackageRoot" | Out-Null

# Binärdateien kopieren
Copy-Item -Recurse "dist\NoteSpaceLLM\*" "$StoreDir\PackageRoot\"

# Manifest und Store-Icons kopieren
Copy-Item "store_package\NoteSpaceLLM\AppxManifest.xml" "$StoreDir\PackageRoot\"
New-Item -ItemType Directory -Force -Path "$StoreDir\PackageRoot\icons" | Out-Null
Copy-Item "releases\windowsstore\*.png" "$StoreDir\PackageRoot\icons\"
```

## Schritt 3: MSIX-Paket erstellen

```powershell
& "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\makeappx.exe" pack `
    /d "$StoreDir\PackageRoot" `
    /p "$StoreDir\NoteSpaceLLM.msix" `
    /nv
```

## Schritt 4: Mit Partner-Center Zertifikat signieren

```powershell
& "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe" sign `
    /fd SHA256 `
    /a `
    /f "$PfxPath" `
    /p "$PfxPassword" `
    /tr "http://timestamp.digicert.com" `
    /td SHA256 `
    "$StoreDir\NoteSpaceLLM.msix"
```

## Schritt 5: WACK-Zertifizierungstest ausführen

```powershell
python scripts\run_windows_wack.py --msix "$StoreDir\NoteSpaceLLM.msix"
```
