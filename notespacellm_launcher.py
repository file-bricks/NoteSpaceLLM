from __future__ import annotations

import ctypes
from pathlib import Path
import shutil
import subprocess
import sys


APP_NAME = "NoteSpaceLLM"
SCRIPT_NAME = "main.py"


def _project_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _show_error(message: str) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(0, message, APP_NAME, 0x10)
    except Exception:
        print(message, file=sys.stderr)


def _python_command() -> list[str] | None:
    for candidate in ("pythonw.exe", "python.exe"):
        resolved = shutil.which(candidate)
        if resolved:
            return [resolved]
    launcher = shutil.which("py.exe") or shutil.which("py")
    if launcher:
        return [launcher, "-3"]
    return None


def main() -> int:
    base_dir = _project_dir()
    app_script = base_dir / SCRIPT_NAME
    if not app_script.exists():
        _show_error(f"{SCRIPT_NAME} wurde nicht gefunden:\n{app_script}")
        return 1

    python_cmd = _python_command()
    if not python_cmd:
        _show_error(
            "Python wurde nicht gefunden.\n"
            "Bitte Python 3.10+ installieren und die Abhängigkeiten aus requirements.txt einrichten."
        )
        return 1

    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen(
            python_cmd + [str(app_script)],
            cwd=str(base_dir),
            creationflags=creationflags,
        )
    except FileNotFoundError as exc:
        _show_error(f"Start fehlgeschlagen:\n{exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
