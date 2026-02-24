#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NoteSpaceLLM Setup Script
=========================

Initial setup and dependency installation.
"""

import subprocess
import sys
from pathlib import Path


def main():
    print("=" * 50)
    print("NoteSpaceLLM Setup")
    print("=" * 50)
    print()

    # Check Python version
    if sys.version_info < (3, 10):
        print(f"ERROR: Python 3.10+ required. You have {sys.version}")
        sys.exit(1)

    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")

    # Install dependencies
    print("\nInstalling dependencies...")
    requirements_file = Path(__file__).parent / "requirements.txt"

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("[OK] Dependencies installed")
    except subprocess.CalledProcessError:
        print("[WARN] Some dependencies may have failed to install")

    # Create directories
    print("\nCreating directories...")
    base = Path(__file__).parent
    directories = ["data", "workflows", "profiles", "output", "assets"]

    for dirname in directories:
        (base / dirname).mkdir(exist_ok=True)
        print(f"  Created: {dirname}/")

    # Create default workflow file
    workflows_file = base / "workflows" / "default.json"
    if not workflows_file.exists():
        import json
        default_workflows = {
            "standard": {
                "id": "standard",
                "name": "Standard-Analyse",
                "description": "Umfassende Dokumentenanalyse",
                "steps": [
                    {"id": "1", "name": "Textextraktion", "order": 1},
                    {"id": "2", "name": "Einzelanalysen", "order": 2},
                    {"id": "3", "name": "Synthese", "order": 3},
                    {"id": "4", "name": "Berichterstellung", "order": 4}
                ]
            }
        }
        workflows_file.write_text(json.dumps(default_workflows, indent=2), encoding="utf-8")
        print(f"  Created: workflows/default.json")

    # Create default profile file
    profiles_file = base / "profiles" / "default.json"
    if not profiles_file.exists():
        import json
        default_profiles = {
            "default": {"name": "default", "formats": ["md"], "is_default": True},
            "full": {"name": "full", "formats": ["md", "pdf", "docx"], "is_default": False}
        }
        profiles_file.write_text(json.dumps(default_profiles, indent=2), encoding="utf-8")
        print(f"  Created: profiles/default.json")

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nStart the application with:")
    print("  python main.py")
    print("\nOr on Windows:")
    print("  run.bat")


if __name__ == "__main__":
    main()
