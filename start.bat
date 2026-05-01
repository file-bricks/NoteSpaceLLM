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
        echo [FEHLER] Python 3 nicht gefunden!
        pause
        exit /b 1
    )
    set "PYTHON_CMD=py -3"
)

%PYTHON_CMD% main.py %*
if errorlevel 1 pause
