#!/usr/bin/env python3
"""check_store_readiness.py — Validiert 21 Microsoft Store Readiness Kriterien fuer NoteSpaceLLM Pro."""

from __future__ import annotations

import argparse
import json
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Ungueltige PNG-Signatur: {path.name}")
    width, height = struct.unpack(">II", header[16:24])
    return int(width), int(height)


def check_readiness(project_root: Path) -> list[str]:
    findings: list[str] = []

    # 1. Pflichtdokumente
    required_docs = [
        "PRIVACY_POLICY.md",
        "SUPPORT.md",
        "STORE_LISTING.md",
        "WINDOWS_STORE_PREP.md",
        "PORTIERUNGSPLAN.md",
        "THIRD_PARTY_LICENSES.txt",
        "LICENSE",
    ]
    for doc in required_docs:
        if not (project_root / doc).is_file():
            findings.append(f"Pflichtdokument fehlt: {doc}")

    # 2. store_package.json (Root)
    pkg_json = project_root / "store_package.json"
    if not pkg_json.is_file():
        findings.append("store_package.json im Projekt-Root fehlt.")
    else:
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8"))
            for req in ["app_name", "publisher", "identity_name", "version", "executable", "capabilities", "privacy_url"]:
                if req not in data or not data[req]:
                    findings.append(f"store_package.json: Feld '{req}' fehlt oder ist leer.")
        except Exception as exc:
            findings.append(f"Fehler beim Parsen von store_package.json: {exc}")

    # 3. releases/windowsstore Struktur
    ws_dir = project_root / "releases" / "windowsstore"
    if not ws_dir.is_dir():
        findings.append("Verzeichnis releases/windowsstore/ fehlt.")
        return findings

    ws_files = [
        "store_settings.json",
        "BUILD.md",
        "WACK_PROTOCOL.md",
        "store_listing_de.md",
        "store_listing_en.md",
    ]
    for wf in ws_files:
        if not (ws_dir / wf).is_file():
            findings.append(f"releases/windowsstore/{wf} fehlt.")

    # 4. store_settings.json Richtlinien
    settings_file = ws_dir / "store_settings.json"
    if settings_file.is_file():
        try:
            st = json.loads(settings_file.read_text(encoding="utf-8"))
            kw_de = st.get("keywords_de", [])
            kw_en = st.get("keywords_en", [])
            if len(kw_de) > 7:
                findings.append(f"store_settings.json: Keywords DE ueberschreiten Limit ({len(kw_de)} > 7, Policy 10.1.3)")
            if len(kw_en) > 7:
                findings.append(f"store_settings.json: Keywords EN ueberschreiten Limit ({len(kw_en)} > 7, Policy 10.1.3)")
            if len(kw_de) == 0:
                findings.append("store_settings.json: Keywords DE fehlen.")
            if len(kw_en) == 0:
                findings.append("store_settings.json: Keywords EN fehlen.")
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
                    findings.append(f"Kachel {tile_name} hat falsche Groesse ({actual} != {exp_dim})")
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
        for s in screens:
            try:
                w, h = _png_size(s)
                if (w, h) not in [(1920, 1080), (1366, 768)]:
                    findings.append(f"Screenshot {s.name} hat kein gueltiges 16:9 Format ({w}x{h})")
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
            if ident is None or ident.attrib.get("Name") != "Geiger.NoteSpaceLLM":
                findings.append("AppxManifest.xml: Identity Name weicht ab von Geiger.NoteSpaceLLM.")
        except Exception as exc:
            findings.append(f"AppxManifest XML-Fehler: {exc}")

    # 8. WACK-Runner & Preflight-Report
    wack_runner = project_root / "scripts" / "run_windows_wack.py"
    if not wack_runner.is_file():
        findings.append("scripts/run_windows_wack.py fehlt.")

    test_reports = ws_dir / "test_reports"
    if not test_reports.is_dir() or not list(test_reports.glob("wack_preflight_*.json")):
        findings.append("Kein WACK-Preflight-Report unter releases/windowsstore/test_reports/ vorhanden.")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Windows Store Readiness for NoteSpaceLLM")
    parser.parse_args()

    print("=== NoteSpaceLLM Pro — Store Readiness Check ===")
    findings = check_readiness(PROJECT_ROOT)

    if findings:
        print(f"FAILED: {len(findings)} Pruefpunkte nicht erfuellt:")
        for idx, f in enumerate(findings, 1):
            print(f"  [{idx}] {f}")
        return 1
    else:
        print("PASS: Alle 21 Microsoft Store Readiness Kriterien erfolgreich erfuellt! (0 Fehler)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
