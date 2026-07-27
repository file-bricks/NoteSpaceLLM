#!/usr/bin/env python3
"""Preflight Store Readiness Auditor for NoteSpaceLLM.

Verifies that all required Windows Store assets, metadata JSON, listings,
support documents, third-party licenses, and packaging settings exist and are valid.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def audit_store_readiness() -> list[str]:
    errors: list[str] = []

    # 1. store_package.json
    pkg_file = PROJECT_ROOT / "store_package.json"
    if not pkg_file.exists():
        errors.append("store_package.json is missing")
    else:
        try:
            pkg_data = json.loads(pkg_file.read_text(encoding="utf-8"))
            if pkg_data.get("app_name") != "NoteSpaceLLM":
                errors.append("store_package.json app_name must be 'NoteSpaceLLM'")
            if not pkg_data.get("publisher", "").startswith("CN=52596601-BAB4-4F3F-B182-E8F3F273B202"):
                errors.append("store_package.json publisher CN invalid")
            if pkg_data.get("publisher_display") != "Lukas Geiger":
                errors.append("store_package.json publisher_display must be 'Lukas Geiger'")
            if pkg_data.get("executable") != "NoteSpaceLLM.exe":
                errors.append("store_package.json executable must be 'NoteSpaceLLM.exe'")
            if "runFullTrust" not in pkg_data.get("capabilities", ""):
                errors.append("store_package.json missing runFullTrust capability")
            if not pkg_data.get("languages"):
                errors.append("store_package.json missing languages list")
        except Exception as e:
            errors.append(f"store_package.json invalid JSON: {e}")

    # 2. releases/windowsstore/store_settings.json
    settings_file = PROJECT_ROOT / "releases" / "windowsstore" / "store_settings.json"
    if not settings_file.exists():
        errors.append("releases/windowsstore/store_settings.json is missing")
    else:
        try:
            s_data = json.loads(settings_file.read_text(encoding="utf-8"))
            if not s_data.get("store_release_enabled"):
                errors.append("store_settings.json store_release_enabled is False")
        except Exception as e:
            errors.append(f"store_settings.json invalid JSON: {e}")

    # 3. STORE_LISTING.md
    listing_file = PROJECT_ROOT / "STORE_LISTING.md"
    if not listing_file.exists():
        errors.append("STORE_LISTING.md is missing")
    else:
        content = listing_file.read_text(encoding="utf-8")
        if "Deutsch" not in content or "English" not in content:
            errors.append("STORE_LISTING.md missing bilingual DE/EN content")

    # 4. PRIVACY_POLICY.md
    privacy_file = PROJECT_ROOT / "PRIVACY_POLICY.md"
    if not privacy_file.exists():
        errors.append("PRIVACY_POLICY.md is missing")
    else:
        content = privacy_file.read_text(encoding="utf-8").lower()
        if "lokal" not in content and "local" not in content:
            errors.append("PRIVACY_POLICY.md must mention local data processing")

    # 5. SUPPORT.md
    support_file = PROJECT_ROOT / "SUPPORT.md"
    if not support_file.exists():
        errors.append("SUPPORT.md is missing")

    # 6. THIRD_PARTY_LICENSES.txt
    licenses_file = PROJECT_ROOT / "THIRD_PARTY_LICENSES.txt"
    if not licenses_file.exists():
        errors.append("THIRD_PARTY_LICENSES.txt is missing")

    # 7. WINDOWS_STORE_PREP.md
    prep_file = PROJECT_ROOT / "WINDOWS_STORE_PREP.md"
    if not prep_file.exists():
        errors.append("WINDOWS_STORE_PREP.md is missing")

    return errors


def main() -> int:
    print("Running NoteSpaceLLM Windows Store Readiness Audit...")
    errors = audit_store_readiness()
    if errors:
        print(f"STORE READINESS: FAILED ({len(errors)} errors found)")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("STORE READINESS: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
