@echo off
REM NoteSpaceLLM Starter for Windows
REM =================================

echo Starting NoteSpaceLLM...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the application
python main.py %*

REM If error, pause to show message
if errorlevel 1 (
    echo.
    echo Application exited with error.
    pause
)
