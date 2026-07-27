"""Store Readiness Tests for NoteSpaceLLM.

Asserts that all Windows Store release materials exist, are valid JSON/Markdown,
and pass preflight auditing with 0 findings.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.check_store_readiness import audit_store_readiness

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_store_readiness_audit_passes():
    errors = audit_store_readiness()
    assert errors == [], f"Store readiness preflight failed: {errors}"


def test_store_package_json_valid():
    pkg_file = PROJECT_ROOT / "store_package.json"
    assert pkg_file.exists(), "store_package.json missing"
    data = json.loads(pkg_file.read_text(encoding="utf-8"))
    assert data["app_name"] == "NoteSpaceLLM"
    assert data["publisher"].startswith("CN=52596601-BAB4-4F3F-B182-E8F3F273B202")
    assert data["publisher_display"] == "Lukas Geiger"
    assert data["executable"] == "NoteSpaceLLM.exe"
    assert "runFullTrust" in data["capabilities"]
    assert len(data["languages"]) >= 2


def test_store_settings_json_valid():
    settings_file = PROJECT_ROOT / "releases" / "windowsstore" / "store_settings.json"
    assert settings_file.exists(), "store_settings.json missing"
    data = json.loads(settings_file.read_text(encoding="utf-8"))
    assert data["store_release_enabled"] is True
    assert data["target_platform"] == "Windows.Desktop"


def test_store_listing_bilingual():
    listing_file = PROJECT_ROOT / "STORE_LISTING.md"
    assert listing_file.exists()
    content = listing_file.read_text(encoding="utf-8")
    assert "Deutsch" in content
    assert "English" in content
    assert "NoteSpaceLLM" in content


def test_support_md_present():
    support_file = PROJECT_ROOT / "SUPPORT.md"
    assert support_file.exists()
    content = support_file.read_text(encoding="utf-8")
    assert "GitHub Issue Tracker" in content


def test_third_party_licenses_present():
    licenses_file = PROJECT_ROOT / "THIRD_PARTY_LICENSES.txt"
    assert licenses_file.exists()
    content = licenses_file.read_text(encoding="utf-8")
    assert "PySide6" in content
    assert "pypdfium2" in content
    assert "pypdf" in content
