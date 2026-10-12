#!/usr/bin/env python3
"""Opt-in local environment bootstrap for NoteSpaceLLM.

This script installs the repository requirements and creates starter
directories/configuration when a developer explicitly runs it. Package builds
and metadata inspection use the side-effect-free setuptools entry point instead.
"""

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    print("=" * 50)
    print("NoteSpaceLLM Environment Setup")
    print("=" * 50)
    print()

    if sys.version_info < (3, 10):  # noqa: UP036 - keep a friendly explicit-bootstrap error
        print(f"ERROR: Python 3.10+ required. You have {sys.version}")
        return 1

    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")
    base = Path(__file__).resolve().parent
    requirements_file = base / "requirements.txt"

    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("[OK] Dependencies installed")
    except subprocess.CalledProcessError:
        print("[ERROR] Dependency installation failed; setup did not complete.")
        return 1

    print("\nCreating directories...")
    for dirname in ("data", "workflows", "profiles", "output", "assets"):
        (base / dirname).mkdir(exist_ok=True)
        print(f"  Created: {dirname}/")

    workflows_file = base / "workflows" / "default.json"
    if not workflows_file.exists():
        default_workflows = {
            "standard": {
                "id": "standard",
                "name": "Standard-Analyse",
                "description": "Umfassende Dokumentenanalyse",
                "steps": [
                    {"id": "1", "name": "Textextraktion", "order": 1},
                    {"id": "2", "name": "Einzelanalysen", "order": 2},
                    {"id": "3", "name": "Synthese", "order": 3},
                    {"id": "4", "name": "Berichterstellung", "order": 4},
                ],
            }
        }
        workflows_file.write_text(
            json.dumps(default_workflows, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print("  Created: workflows/default.json")

    profiles_file = base / "profiles" / "default.json"
    if not profiles_file.exists():
        default_profiles = {
            "default": {"name": "default", "formats": ["md"], "is_default": True},
            "full": {
                "name": "full",
                "formats": ["md", "pdf", "docx"],
                "is_default": False,
            },
        }
        profiles_file.write_text(
            json.dumps(default_profiles, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print("  Created: profiles/default.json")

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nStart the application with:")
    print("  python main.py")
    print("\nOr on Windows:")
    print("  run.bat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
