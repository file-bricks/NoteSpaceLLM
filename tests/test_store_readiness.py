import json
import os
import pytest

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_store_package_json_exists_and_valid():
    store_pkg_path = os.path.join(REPO_DIR, "store_package.json")
    assert os.path.isfile(store_pkg_path), "store_package.json missing in repository root"
    
    with open(store_pkg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    required_keys = [
        "app_name", "publisher", "publisher_display", "identity_name",
        "version", "executable", "capabilities", "category",
        "age_rating", "privacy_url", "support_url", "languages"
    ]
    for key in required_keys:
        assert key in data, f"Missing required key in store_package.json: {key}"
        assert data[key], f"Key {key} must not be empty"
        
    assert data["executable"] == "NoteSpaceLLM.exe"
    assert data["publisher_display"] == "Geiger"
    assert data["identity_name"] == "Geiger.NoteSpaceLLM"
    assert "de-DE" in data["languages"]
    assert "en-US" in data["languages"]

def test_releases_windowsstore_files():
    store_dir = os.path.join(REPO_DIR, "releases", "windowsstore")
    assert os.path.isdir(store_dir), "releases/windowsstore directory missing"
    
    pkg_path = os.path.join(store_dir, "store_package.json")
    settings_path = os.path.join(store_dir, "store_settings.json")
    assert os.path.isfile(pkg_path), "releases/windowsstore/store_package.json missing"
    assert os.path.isfile(settings_path), "releases/windowsstore/store_settings.json missing"
    
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)
        
    assert settings.get("target_platform") == "Windows.Desktop"
    assert settings.get("architecture") == "x64"
    assert settings.get("wack_passed") is True

def test_privacy_policy_exists_and_compliant():
    policy_path = os.path.join(REPO_DIR, "PRIVACY_POLICY.md")
    assert os.path.isfile(policy_path), "PRIVACY_POLICY.md missing"
    
    with open(policy_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "Deutsch" in content
    assert "English" in content
    assert "lokal" in content.lower() or "local" in content.lower()
    assert "ollama" in content.lower() or "openai" in content.lower()

def test_third_party_licenses_complete():
    lic_path = os.path.join(REPO_DIR, "THIRD_PARTY_LICENSES.txt")
    assert os.path.isfile(lic_path), "THIRD_PARTY_LICENSES.txt missing"
    
    with open(lic_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "AGPL-3.0" in content
    assert "PySide6" in content
    assert "pypdfium2" in content
    assert "pypdf" in content

def test_logo_assets_exist():
    ico_path = os.path.join(REPO_DIR, "NoteSpaceLLM.ico")
    svg_path = os.path.join(REPO_DIR, "assets", "banner.svg")
    jpg_path = os.path.join(REPO_DIR, "NoteSpace_logo.jpg")
    
    assert os.path.isfile(ico_path), "NoteSpaceLLM.ico missing"
    assert os.path.isfile(svg_path), "assets/banner.svg missing"
    assert os.path.isfile(jpg_path), "NoteSpace_logo.jpg missing"

def test_build_exe_script_exists():
    bat_path = os.path.join(REPO_DIR, "build_exe.bat")
    assert os.path.isfile(bat_path), "build_exe.bat missing"
    
    with open(bat_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    assert "pyinstaller" in content.lower() or "python" in content.lower()
