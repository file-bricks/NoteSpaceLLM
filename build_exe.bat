@echo off
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set "PYTHON_CMD=python"
python --version >nul 2>&1
if errorlevel 1 (
    py -3 --version >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] Python wurde nicht gefunden. Bitte Python 3.10+ installieren.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=py -3"
)

%PYTHON_CMD% -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] PyInstaller ist nicht installiert.
    echo Bitte ausführen: %PYTHON_CMD% -m pip install pyinstaller
    pause
    exit /b 1
)

echo [INFO] Bereinige alte Build-Artefakte...
powershell -NoProfile -Command "Get-ChildItem -LiteralPath 'build','dist' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force"

echo [INFO] Baue NoteSpaceLLM.exe als Windows-Launcher...
%PYTHON_CMD% -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name NoteSpaceLLM ^
  --specpath build ^
  --icon "%cd%\NoteSpaceLLM.ico" ^
  notespacellm_launcher.py

if errorlevel 1 (
    echo [FEHLER] PyInstaller-Build fehlgeschlagen.
    pause
    exit /b 1
)

if exist "dist\NoteSpaceLLM.exe" copy /Y "dist\NoteSpaceLLM.exe" "NoteSpaceLLM.exe" >nul

echo.
echo [OK] Build fertig: dist\NoteSpaceLLM.exe
echo [HINWEIS] Der Launcher erwartet eine lokale Python-Umgebung mit den Abhängigkeiten aus requirements.txt.
