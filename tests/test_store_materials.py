"""test_store_materials.py — Hermetische Vertragstests für Store-Readiness & Tier-2 6-Sprachen-Standard.

Verifiziert:
- store_package.json Vollständigkeit und 6 Tier-2 Zielsprachen
- store_settings.json Parität und Richtlinie 10.1.3 Compliance (exakt 7 Keywords <= 30 Zeichen je Sprache)
- AppxManifest.xml mehrsprachige Ressourcen-Deklaration (<Resource Language="..."/>)
- Vollständigkeit der Staging-Dateien in releases/windowsstore/ (de, en, es, zh, ja, ru)
- STORE_LISTING.md 6-Sprachen-Parität
- manage_translations.py --check 100% Paritäts-Gate
- scripts/check_store_readiness.py 0 Findings Gate
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LANGUAGES = ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]
EXPECTED_MANIFEST_LANGS = ["de-de", "en-us", "es-es", "zh-cn", "ja-jp", "ru-ru"]
BANNED_TRADEMARKS = {"windows", "microsoft", "google", "apple", "adobe", "openai", "anthropic"}


def test_store_package_json_has_six_tier2_languages():
    pkg_file = REPO_ROOT / "store_package.json"
    assert pkg_file.is_file(), "store_package.json fehlt im Root"
    data = json.loads(pkg_file.read_text(encoding="utf-8"))

    langs = data.get("languages", [])
    for elang in EXPECTED_LANGUAGES:
        assert elang in langs, f"Sprache {elang} fehlt in store_package.json"

    assert data.get("identity_name") == "Geiger.NoteSpaceLLM"
    assert data.get("publisher") == "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
    assert data.get("executable") == "NoteSpaceLLM.exe"


def test_store_package_json_descriptions_and_keywords_compliance():
    pkg_file = REPO_ROOT / "store_package.json"
    data = json.loads(pkg_file.read_text(encoding="utf-8"))

    for lang in ["de", "en", "es", "zh", "ja", "ru"]:
        desc_key = f"description_{lang}"
        assert desc_key in data, f"{desc_key} fehlt in store_package.json"
        desc_val = data[desc_key]
        assert 0 < len(desc_val) <= 100, f"{desc_key} ('{desc_val}') überschreitet 100 Zeichen Limit ({len(desc_val)})"

        kw_key = f"keywords_{lang}"
        assert kw_key in data, f"{kw_key} fehlt in store_package.json"
        kws = data[kw_key]
        assert len(kws) == 7, f"{kw_key} hat {len(kws)} Keywords (genau 7 erforderlich)"
        for kw in kws:
            assert len(kw) <= 30, f"Keyword '{kw}' in {kw_key} überschreitet 30 Zeichen ({len(kw)})"
            assert kw.lower() not in BANNED_TRADEMARKS, f"Verbotene Marke '{kw}' in {kw_key}"


def test_store_settings_json_parity():
    settings_file = REPO_ROOT / "releases" / "windowsstore" / "store_settings.json"
    assert settings_file.is_file(), "store_settings.json fehlt in releases/windowsstore"
    st = json.loads(settings_file.read_text(encoding="utf-8"))

    st_langs = st.get("languages", [])
    for elang in EXPECTED_LANGUAGES:
        assert elang in st_langs, f"Sprache {elang} fehlt in store_settings.json"

    for lang in ["de", "en", "es", "zh", "ja", "ru"]:
        assert f"description_{lang}" in st
        assert len(st[f"description_{lang}"]) <= 100
        kws = st.get(f"keywords_{lang}", [])
        assert len(kws) == 7
        for kw in kws:
            assert len(kw) <= 30
            assert kw.lower() not in BANNED_TRADEMARKS


def test_appx_manifest_six_languages():
    manifest_file = REPO_ROOT / "store_package" / "NoteSpaceLLM" / "AppxManifest.xml"
    assert manifest_file.is_file(), "AppxManifest.xml fehlt"

    tree = ET.parse(manifest_file)
    root = tree.getroot()
    ns = {"m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}

    resources = root.find("m:Resources", ns)
    assert resources is not None, "<Resources> fehlt in AppxManifest.xml"

    res_langs = [r.attrib.get("Language", "").lower() for r in resources.findall("m:Resource", ns)]
    for mlang in EXPECTED_MANIFEST_LANGS:
        assert mlang in res_langs, f"<Resource Language=\"{mlang}\"/> fehlt im Manifest"


def test_store_listing_markdown_files_exist():
    ws_dir = REPO_ROOT / "releases" / "windowsstore"
    for lang in ["de", "en", "es", "zh", "ja", "ru"]:
        lf = ws_dir / f"store_listing_{lang}.md"
        assert lf.is_file(), f"Staging-Datei store_listing_{lang}.md fehlt"
        content = lf.read_text(encoding="utf-8")
        assert len(content) > 100, f"store_listing_{lang}.md ist zu kurz"


def test_store_listing_master_document_multilingual():
    listing_md = REPO_ROOT / "STORE_LISTING.md"
    assert listing_md.is_file(), "STORE_LISTING.md fehlt"
    text = listing_md.read_text(encoding="utf-8")

    sections = [
        "## Deutsch",
        "## Englisch",
        "## Español",
        "## 简体中文",
        "## 日本語",
        "## Русский",
    ]
    for sec in sections:
        assert sec in text, f"Abschnitt '{sec}' fehlt in STORE_LISTING.md"


def test_manage_translations_check_passes():
    from manage_translations import check_translations
    code, stats = check_translations(REPO_ROOT)
    assert code == 0, f"check_translations meldet Fehler: {stats}"
    assert len(stats) == 6
    for lang, count in stats.items():
        assert count >= 40, f"Zu wenige Übersetzungen für {lang}: {count}"


def test_check_store_readiness_script_clean():
    from scripts.check_store_readiness import check_readiness
    passed, findings = check_readiness(REPO_ROOT)
    assert not findings, f"check_store_readiness meldet Findings: {findings}"
    assert len(passed) >= 80, f"Zu wenige bestandene Prüfpunkte: {len(passed)}"


def test_readme_tier2_language_parity():
    readme_files = [
        "README.md",
        "README_de.md",
        "README_es.md",
        "README_zh.md",
        "README_ja.md",
        "README_ru.md",
    ]
    expected_bar = "[English](README.md) · [Deutsch](README_de.md) · [Español](README_es.md) · [简体中文](README_zh.md) · [日本語](README_ja.md) · [Русский](README_ru.md)"

    for rmf in readme_files:
        p = REPO_ROOT / rmf
        assert p.is_file(), f"README-Datei {rmf} fehlt"
        content = p.read_text(encoding="utf-8")
        assert expected_bar in content, f"Reziproke Sprachleiste fehlt in {rmf}"
        assert len(content) > 300, f"{rmf} ist unvollständig oder zu kurz"

