#!/usr/bin/env python3
"""check_store_readiness.py — Validiert Microsoft Store Readiness Kriterien für NoteSpaceLLM Pro.

Prüft alle Windows Store Release Readiness Artefakte auf Vollständigkeit, Konsistenz
und Richtlinienkonformität nach dem Tier-2 6-Sprachen-Standard (Policy P-006 & Partner Center Policy 10.1.3).
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BANNED_TRADEMARKS = {"windows", "microsoft", "google", "apple", "adobe", "openai", "anthropic"}
EXPECTED_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
EXPECTED_IDENTITY = "Geiger.NoteSpaceLLM"
EXPECTED_LANGUAGES = ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]
MANIFEST_LANGUAGES = ["de-de", "en-us", "es-es", "zh-cn", "ja-jp", "ru-ru"]


def _png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Ungültige PNG-Signatur: {path.name}")
    width, height = struct.unpack(">II", header[16:24])
    return int(width), int(height)


def check_readiness(project_root: Path = PROJECT_ROOT) -> tuple[list[str], list[str]]:
    """Führt alle Preflight-Prüfungen für die Windows Store Release Readiness durch.

    Returns:
        tuple[list[str], list[str]]: (passed_checks, findings)
    """
    passed: list[str] = []
    findings: list[str] = []

    # 1. Pflichtdokumente
    required_docs = [
        ("PRIVACY_POLICY.md", "Datenschutzerklärung (DE/EN)"),
        ("SUPPORT.md", "Support-Dokumentation"),
        ("STORE_LISTING.md", "Store Listing (DE/EN/ES/ZH/JA/RU)"),
        ("WINDOWS_STORE_PREP.md", "Store Vorbereitungsleitfaden"),
        ("PORTIERUNGSPLAN.md", "Multi-Target Portierungsplan"),
        ("THIRD_PARTY_LICENSES.txt", "Drittanbieter-Lizenzen"),
        ("LICENSE", "Projektlizenz (AGPL-3.0)"),
    ]
    for doc, label in required_docs:
        p = project_root / doc
        if not p.is_file():
            findings.append(f"Pflichtdokument fehlt: {doc} ({label})")
        elif p.stat().st_size < 100:
            findings.append(f"Pflichtdokument zu kurz: {doc} ({p.stat().st_size} Bytes)")
        else:
            passed.append(f"Pflichtdokument vorhanden: {doc} ({label})")

    # 2. store_package.json (Root)
    pkg_json = project_root / "store_package.json"
    if not pkg_json.is_file():
        findings.append("store_package.json im Projekt-Root fehlt.")
    else:
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            for req in ["app_name", "publisher", "publisher_display", "identity_name", "version", "executable", "capabilities", "privacy_url"]:
                if req not in data or not data[req]:
                    findings.append(f"store_package.json: Feld '{req}' fehlt oder ist leer.")
                else:
                    passed.append(f"store_package.json: Feld '{req}' vorhanden")

            if data.get("identity_name") != EXPECTED_IDENTITY:
                findings.append(f"store_package.json: Unerwartete identity_name '{data.get('identity_name')}' != '{EXPECTED_IDENTITY}'")
            else:
                passed.append(f"store_package.json: identity_name '{EXPECTED_IDENTITY}' korrekt")

            languages = data.get("languages", [])
            for elang in EXPECTED_LANGUAGES:
                if elang not in languages:
                    findings.append(f"store_package.json: Sprache '{elang}' fehlt in languages.")
                else:
                    passed.append(f"store_package.json: Sprache '{elang}' deklariert")

            for lang_code in ["de", "en", "es", "zh", "ja", "ru"]:
                desc_k = f"description_{lang_code}"
                if desc_k in data:
                    val = data[desc_k]
                    if len(val) > 100:
                        findings.append(f"store_package.json: {desc_k} überschreitet 100 Zeichen ({len(val)})")
                    else:
                        passed.append(f"store_package.json: {desc_k} <= 100 Zeichen ({len(val)})")
                else:
                    findings.append(f"store_package.json: {desc_k} fehlt.")

                kw_k = f"keywords_{lang_code}"
                if kw_k in data:
                    kws = data[kw_k]
                    if len(kws) != 7:
                        findings.append(f"store_package.json: {kw_k} hat {len(kws)} Keywords (genau 7 erwartet)")
                    else:
                        passed.append(f"store_package.json: {kw_k} genau 7 Keywords")
                    for kw in kws:
                        if len(kw) > 30:
                            findings.append(f"store_package.json: {kw_k} Keyword '{kw}' > 30 Zeichen")
                        if kw.lower() in BANNED_TRADEMARKS:
                            findings.append(f"store_package.json: {kw_k} enthält verbotene Marke '{kw}'")
                else:
                    findings.append(f"store_package.json: {kw_k} fehlt.")

        except Exception as exc:
            findings.append(f"Fehler beim Parsen von store_package.json: {exc}")

    # 3. releases/windowsstore Struktur
    ws_dir = project_root / "releases" / "windowsstore"
    if not ws_dir.is_dir():
        findings.append("Verzeichnis releases/windowsstore/ fehlt.")
        return passed, findings

    ws_files = [
        "store_settings.json",
        "store_package.json",
        "BUILD.md",
        "WACK_PROTOCOL.md",
        "store_listing_de.md",
        "store_listing_en.md",
        "store_listing_es.md",
        "store_listing_zh.md",
        "store_listing_ja.md",
        "store_listing_ru.md",
    ]
    for wf in ws_files:
        p = ws_dir / wf
        if not p.is_file():
            findings.append(f"releases/windowsstore/{wf} fehlt.")
        else:
            passed.append(f"releases/windowsstore/{wf} vorhanden")

    # 4. store_settings.json Richtlinien
    settings_file = ws_dir / "store_settings.json"
    if settings_file.is_file():
        try:
            st = json.loads(settings_file.read_text(encoding="utf-8"))
            st_langs = st.get("languages", [])
            for elang in EXPECTED_LANGUAGES:
                if elang not in st_langs:
                    findings.append(f"store_settings.json: Sprache '{elang}' fehlt in languages.")
                else:
                    passed.append(f"store_settings.json: Sprache '{elang}' vorhanden")

            for lang_code in ["de", "en", "es", "zh", "ja", "ru"]:
                kw_k = f"keywords_{lang_code}"
                kws = st.get(kw_k, [])
                if len(kws) != 7:
                    findings.append(f"store_settings.json: {kw_k} hat {len(kws)} Keywords (genau 7 erwartet)")
                else:
                    passed.append(f"store_settings.json: {kw_k} genau 7 Keywords")
                for kw in kws:
                    if len(kw) > 30:
                        findings.append(f"store_settings.json: {kw_k} Keyword '{kw}' > 30 Zeichen")
                    if kw.lower() in BANNED_TRADEMARKS:
                        findings.append(f"store_settings.json: {kw_k} enthält verbotene Marke '{kw}'")

                desc_k = f"description_{lang_code}"
                if desc_k in st:
                    val = st[desc_k]
                    if len(val) > 100:
                        findings.append(f"store_settings.json: {desc_k} > 100 Zeichen ({len(val)})")
                    else:
                        passed.append(f"store_settings.json: {desc_k} <= 100 Zeichen")
                else:
                    findings.append(f"store_settings.json: {desc_k} fehlt.")

        except Exception as exc:
            findings.append(f"store_settings.json Parsing-Fehler: {exc}")

    # 5. Kachel-Assets
    required_tiles = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square50x50Logo.png": (50, 50),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "Square310x310Logo.png": (310, 310),
    }
    for tile_name, exp_dim in required_tiles.items():
        tp = ws_dir / tile_name
        if not tp.is_file():
            findings.append(f"Kachel-Asset fehlt: releases/windowsstore/{tile_name}")
        else:
            try:
                actual = _png_size(tp)
                if actual != exp_dim:
                    findings.append(f"Kachel {tile_name} hat falsche Größe ({actual} != {exp_dim})")
                else:
                    passed.append(f"Kachel {tile_name} Größe {actual} OK")
            except Exception as exc:
                findings.append(f"Fehler bei Kachel {tile_name}: {exc}")

    # 6. Screenshots
    screen_dir = ws_dir / "screenshots"
    if not screen_dir.is_dir():
        findings.append("releases/windowsstore/screenshots/ fehlt.")
    else:
        screens = list(screen_dir.glob("*.png"))
        if len(screens) < 4:
            findings.append(f"Zu wenige Screenshots in releases/windowsstore/screenshots/ ({len(screens)} < 4)")
        else:
            passed.append(f"Screenshots Anzahl {len(screens)} >= 4 OK")
        for s in screens:
            try:
                w, h = _png_size(s)
                if (w, h) not in [(1920, 1080), (1366, 768)]:
                    findings.append(f"Screenshot {s.name} hat kein gültiges 16:9 Format ({w}x{h})")
                else:
                    passed.append(f"Screenshot {s.name} ({w}x{h}) OK")
            except Exception as exc:
                findings.append(f"Fehler bei Screenshot {s.name}: {exc}")

    # 7. AppxManifest
    manifest = project_root / "store_package" / "NoteSpaceLLM" / "AppxManifest.xml"
    if not manifest.is_file():
        findings.append("store_package/NoteSpaceLLM/AppxManifest.xml fehlt.")
    else:
        try:
            tree = ET.parse(manifest)
            root = tree.getroot()
            ns = {"m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}
            ident = root.find("m:Identity", ns)
            if ident is None or ident.attrib.get("Name") != EXPECTED_IDENTITY:
                findings.append(f"AppxManifest.xml: Identity Name weicht ab von {EXPECTED_IDENTITY}.")
            else:
                passed.append(f"AppxManifest.xml: Identity Name '{EXPECTED_IDENTITY}' OK")

            res_elem = root.find("m:Resources", ns)
            if res_elem is None:
                findings.append("AppxManifest.xml: <Resources> Element fehlt.")
            else:
                present_langs = [r.attrib.get("Language", "").lower() for r in res_elem.findall("m:Resource", ns)]
                for mlang in MANIFEST_LANGUAGES:
                    if mlang not in present_langs:
                        findings.append(f"AppxManifest.xml: <Resource Language=\"{mlang}\"/> fehlt.")
                    else:
                        passed.append(f"AppxManifest.xml: <Resource Language=\"{mlang}\"/> vorhanden")

        except Exception as exc:
            findings.append(f"AppxManifest XML-Fehler: {exc}")

    # 8. STORE_LISTING.md 6-Sprachen-Prüfung
    listing_md = project_root / "STORE_LISTING.md"
    if listing_md.is_file():
        text = listing_md.read_text(encoding="utf-8")
        sections = [
            ("Deutsch", r"## Deutsch"),
            ("Englisch", r"## Englisch|## English"),
            ("Español", r"## Español"),
            ("Chinesisch", r"## 简体中文"),
            ("Japanisch", r"## 日本語"),
            ("Russisch", r"## Русский"),
        ]
        for name, pattern in sections:
            if re.search(pattern, text):
                passed.append(f"STORE_LISTING.md: Abschnitt für {name} vorhanden")
            else:
                findings.append(f"STORE_LISTING.md: Abschnitt für {name} fehlt")

    # 9. WACK-Runner & Preflight-Report
    wack_runner = project_root / "scripts" / "run_windows_wack.py"
    if not wack_runner.is_file():
        findings.append("scripts/run_windows_wack.py fehlt.")
    else:
        passed.append("scripts/run_windows_wack.py vorhanden")

    test_reports = ws_dir / "test_reports"
    if not test_reports.is_dir() or not list(test_reports.glob("wack_preflight_*.json")):
        findings.append("Kein WACK-Preflight-Report unter releases/windowsstore/test_reports/ vorhanden.")
    else:
        passed.append("WACK-Preflight-Report vorhanden")

    return passed, findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Windows Store Readiness for NoteSpaceLLM")
    parser.parse_args()

    print("=== NoteSpaceLLM Pro — Store Readiness Check ===")
    passed, findings = check_readiness(PROJECT_ROOT)

    print(f"PASS: {len(passed)} Kriterien erfolgreich geprüft.")
    if findings:
        print(f"FAILED: {len(findings)} Prüfpunkte nicht erfüllt:")
        for idx, f in enumerate(findings, 1):
            print(f"  [{idx}] {f}")
        return 1
    else:
        print("ALL PASS: Alle Microsoft Store Readiness & Tier-2 6-Sprachen-Kriterien erfüllt! (0 Fehler)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
