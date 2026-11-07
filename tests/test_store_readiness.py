import json
import os
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _png_dimensions(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        header = f.read(24)
    assert len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path}"
    w, h = struct.unpack(">II", header[16:24])
    return int(w), int(h)


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
    for expected_lang in ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]:
        assert expected_lang in data["languages"], f"Missing {expected_lang} in store_package.json"

    for lang in ["de", "en", "es", "zh", "ja", "ru"]:
        assert f"description_{lang}" in data, f"Missing description_{lang}"
        assert len(data[f"description_{lang}"]) <= 100, f"description_{lang} exceeds 100 characters"
        assert f"keywords_{lang}" in data, f"Missing keywords_{lang}"
        assert len(data[f"keywords_{lang}"]) == 7, f"keywords_{lang} must have exactly 7 entries"


def test_releases_windowsstore_files():
    store_dir = os.path.join(REPO_DIR, "releases", "windowsstore")
    assert os.path.isdir(store_dir), "releases/windowsstore directory missing"

    pkg_path = os.path.join(store_dir, "store_package.json")
    settings_path = os.path.join(store_dir, "store_settings.json")
    assert os.path.isfile(pkg_path), "releases/windowsstore/store_package.json missing"
    assert os.path.isfile(settings_path), "releases/windowsstore/store_settings.json missing"

    for lang in ["de", "en", "es", "zh", "ja", "ru"]:
        lf = os.path.join(store_dir, f"store_listing_{lang}.md")
        assert os.path.isfile(lf), f"releases/windowsstore/store_listing_{lang}.md missing"

    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    assert settings.get("target_platform") == "Windows.Desktop"
    assert settings.get("architecture") == "x64"
    assert settings.get("wack_passed") is True
    assert settings.get("identity_name") == "Geiger.NoteSpaceLLM"
    assert settings.get("executable") == "NoteSpaceLLM.exe"


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


def test_portierungsplan_exists_and_covers_targets():
    port_path = os.path.join(REPO_DIR, "PORTIERUNGSPLAN.md")
    assert os.path.isfile(port_path), "PORTIERUNGSPLAN.md missing"

    with open(port_path, "r", encoding="utf-8") as f:
        text = f.read()

    assert "Windows Desktop" in text
    assert "Windows Store" in text
    assert "Web Companion" in text
    assert "Mobile Companion" in text
    assert "Geiger.NoteSpaceLLM" in text


def test_store_listing_documents_and_keywords_limit():
    store_dir = os.path.join(REPO_DIR, "releases", "windowsstore")
    for lang in ["de", "en", "es", "zh", "ja", "ru"]:
        listing = os.path.join(store_dir, f"store_listing_{lang}.md")
        assert os.path.isfile(listing), f"store_listing_{lang}.md missing"

    settings_path = os.path.join(store_dir, "store_settings.json")
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    for lang in ["de", "en", "es", "zh", "ja", "ru"]:
        kws = settings.get(f"keywords_{lang}", [])
        assert len(kws) == 7, f"Keywords {lang} count violates Policy 10.1.3: {len(kws)}"
        for kw in kws:
            assert len(kw) <= 30, f"Keyword '{kw}' ({lang}) exceeds 30 chars"


def test_support_and_prep_md_exist():
    support_path = os.path.join(REPO_DIR, "SUPPORT.md")
    prep_path = os.path.join(REPO_DIR, "WINDOWS_STORE_PREP.md")
    assert os.path.isfile(support_path), "SUPPORT.md missing"
    assert os.path.isfile(prep_path), "WINDOWS_STORE_PREP.md missing"


def test_store_tile_assets_dimensions():
    store_dir = os.path.join(REPO_DIR, "releases", "windowsstore")
    expected_tiles = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square50x50Logo.png": (50, 50),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "Square310x310Logo.png": (310, 310),
    }
    for tile_name, exp_dim in expected_tiles.items():
        p = os.path.join(store_dir, tile_name)
        assert os.path.isfile(p), f"Tile asset missing: {tile_name}"
        assert _png_dimensions(p) == exp_dim, f"Tile {tile_name} dimensions wrong"


def test_store_screenshots_resolution():
    screen_dir = os.path.join(REPO_DIR, "releases", "windowsstore", "screenshots")
    assert os.path.isdir(screen_dir), "screenshots directory missing"
    screens = [s for s in os.listdir(screen_dir) if s.endswith(".png")]
    assert len(screens) >= 4, f"At least 4 screenshots required, found {len(screens)}"
    for s in screens:
        p = os.path.join(screen_dir, s)
        dim = _png_dimensions(p)
        assert dim in [(1920, 1080), (1366, 768)], f"Screenshot {s} resolution {dim} is not 16:9 HD/FHD"


def test_appx_manifest_structure():
    manifest_path = os.path.join(REPO_DIR, "store_package", "NoteSpaceLLM", "AppxManifest.xml")
    assert os.path.isfile(manifest_path), "AppxManifest.xml missing"

    tree = ET.parse(manifest_path)
    root = tree.getroot()
    ns = {"m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}
    identity = root.find("m:Identity", ns)
    assert identity is not None, "m:Identity element missing in AppxManifest.xml"
    assert identity.attrib.get("Name") == "Geiger.NoteSpaceLLM"
    assert identity.attrib.get("Publisher") == "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
    assert identity.attrib.get("Version") == "1.0.0.0"

    resources = root.find("m:Resources", ns)
    assert resources is not None, "<Resources> element missing in AppxManifest.xml"
    res_langs = [r.attrib.get("Language", "").lower() for r in resources.findall("m:Resource", ns)]
    for lang in ["de-de", "en-us", "es-es", "zh-cn", "ja-jp", "ru-ru"]:
        assert lang in res_langs, f"Missing resource language {lang} in AppxManifest.xml"


def test_wack_runner_and_preflight_report():
    wack_script = os.path.join(REPO_DIR, "scripts", "run_windows_wack.py")
    assert os.path.isfile(wack_script), "scripts/run_windows_wack.py missing"

    report_dir = os.path.join(REPO_DIR, "releases", "windowsstore", "test_reports")
    assert os.path.isdir(report_dir), "test_reports directory missing"
    reports = [r for r in os.listdir(report_dir) if r.startswith("wack_preflight_") and r.endswith(".json")]
    assert len(reports) > 0, "No wack_preflight_*.json report found"

    latest_report = os.path.join(report_dir, sorted(reports)[-1])
    with open(latest_report, "r", encoding="utf-8") as f:
        rep_data = json.load(f)

    assert rep_data.get("overall_result") == "PASS"
    assert rep_data.get("fail_count") == 0
    assert rep_data.get("requirements_tested") >= 6


def test_check_store_readiness_cli_passes():
    check_script = os.path.join(REPO_DIR, "scripts", "check_store_readiness.py")
    assert os.path.isfile(check_script), "scripts/check_store_readiness.py missing"

    res = subprocess.run([sys.executable, check_script], capture_output=True, text=True, cwd=REPO_DIR)
    assert res.returncode == 0, f"check_store_readiness.py failed:\n{res.stdout}\n{res.stderr}"
    assert "ALL PASS" in res.stdout or "PASS:" in res.stdout
