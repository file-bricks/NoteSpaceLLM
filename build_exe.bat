@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set "LOCAL_BUILD_ROOT=C:\_Local_DEV\codex_build\notespacellm"
set "LOCAL_BUILD=%LOCAL_BUILD_ROOT%\build"
set "LOCAL_DIST=%LOCAL_BUILD_ROOT%\dist"
set "SCANNER=%~dp0..\..\_tools\build_exclude_scanner.py"

python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden. Bitte Python 3.10+ installieren.
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] PyInstaller ist nicht installiert.
    echo Bitte ausfuehren: python -m pip install pyinstaller
    exit /b 1
)

echo [INFO] Bereinige alte Build-Artefakte...
powershell -NoProfile -Command "Remove-Item -LiteralPath '%LOCAL_BUILD_ROOT%' -Recurse -Force -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force -Path '%LOCAL_BUILD%','%LOCAL_DIST%' | Out-Null"

echo [INFO] Ermittle PyInstaller-Excludes...
for /f "delims=" %%E in ('python "%SCANNER%" --project "%~dp0" --emit pyinstaller 2^>nul') do set "EXCLUDES=%%E"

REM FIX 2026-06-27: Entry von notespacellm_launcher.py auf main.py geaendert,
REM damit das Haupt-Script direkt ins Bundle kommt (EXE startet eigenstaendig).
REM Workpath/Distpath auf C:\_Local_DEV gesetzt (BUILD-VERFAHREN Regel 2).
echo [INFO] Baue NoteSpaceLLM.exe (Entry: main.py)...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name NoteSpaceLLM ^
  --workpath "%LOCAL_BUILD%" ^
  --distpath "%LOCAL_DIST%" ^
  --specpath "%LOCAL_BUILD_ROOT%" ^
  --icon "%cd%\NoteSpaceLLM.ico" ^
  --collect-submodules src ^
  %EXCLUDES% ^
  main.py

if errorlevel 1 (
    echo [FEHLER] PyInstaller-Build fehlgeschlagen.
    exit /b 1
)

if exist "%LOCAL_DIST%\NoteSpaceLLM.exe" copy /Y "%LOCAL_DIST%\NoteSpaceLLM.exe" "NoteSpaceLLM.exe" >nul

echo.
echo [OK] Build fertig: %LOCAL_DIST%\NoteSpaceLLM.exe
echo [HINWEIS] Die EXE ist eigenstaendig und benoetigt kein externes Python.
