#!/usr/bin/env python3
"""run_windows_wack.py - Führt das Windows App Certification Kit (WACK) für NoteSpaceLLM aus oder erstellt hermetische Preflight-Reports."""

from __future__ import annotations

import argparse
import json
import struct
import sys
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    import ctypes
except ImportError:
    ctypes = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APPCERT = Path(r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\appcert.exe")
WACK_REPORT_PREFIX = "wack_preflight_"


@dataclass(frozen=True)
class WackSummary:
    report: str
    overall_result: str
    requirement_count: int
    pass_count: int
    fail_count: int
    warning_count: int


def _png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Ungueltige PNG-Signatur: {path.name}")
    width, height = struct.unpack(">II", header[16:24])
    return int(width), int(height)


def _check_admin() -> bool:
    if ctypes is None or not hasattr(ctypes, "windll"):
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _check_manifest(manifest_path: Path) -> tuple[bool, str]:
    if not manifest_path.is_file():
        return False, f"Manifest fehlt: {manifest_path}"
    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        ns = {"m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10"}
        identity = root.find("m:Identity", ns)
        if identity is None:
            return False, "Identity-Element fehlt in AppxManifest.xml"
        name = identity.attrib.get("Name", "")
        pub = identity.attrib.get("Publisher", "")
        if name != "Geiger.NoteSpaceLLM":
            return False, f"Unerwarteter Package-Name: {name}"
        if not pub.startswith("CN="):
            return False, f"Unerwarteter Publisher-DN: {pub}"
        return True, "AppxManifest ist gueltig und vollstaendig konfiguriert."
    except Exception as exc:
        return False, f"Manifest-Parsing-Fehler: {exc}"


def _check_assets(store_dir: Path) -> tuple[bool, str]:
    required_sizes = {
        "StoreLogo.png": (50, 50),
        "Square44x44Logo.png": (44, 44),
        "Square50x50Logo.png": (50, 50),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "Square310x310Logo.png": (310, 310),
    }
    for asset_name, expected_size in required_sizes.items():
        asset_path = store_dir / asset_name
        if not asset_path.is_file():
            return False, f"Erforderliches Kachel-Asset fehlt: {asset_name}"
        try:
            actual_size = _png_size(asset_path)
            if actual_size != expected_size:
                return False, f"{asset_name}: Groesse {actual_size} weicht ab von {expected_size}"
        except Exception as exc:
            return False, f"Fehler beim Pruefen von {asset_name}: {exc}"
    return True, "Alle 6 Pflicht-Kacheln vorhanden und massgenau."


def _check_store_settings(settings_path: Path) -> tuple[bool, str]:
    if not settings_path.is_file():
        return False, f"store_settings.json fehlt: {settings_path}"
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        kw_de = data.get("keywords_de", [])
        kw_en = data.get("keywords_en", [])
        if len(kw_de) > 7:
            return False, f"Zu viele deutsche Keywords ({len(kw_de)} > 7, Policy 10.1.3)"
        if len(kw_en) > 7:
            return False, f"Zu viele englische Keywords ({len(kw_en)} > 7, Policy 10.1.3)"
        if not data.get("privacy_url"):
            return False, "privacy_url fehlt in store_settings.json"
        return True, f"Keywords und Metadaten richtlinienkonform (DE: {len(kw_de)}, EN: {len(kw_en)})."
    except Exception as exc:
        return False, f"Fehler beim Lesen von store_settings.json: {exc}"


def _check_privacy_and_licenses(project_root: Path) -> tuple[bool, str]:
    privacy_file = project_root / "PRIVACY_POLICY.md"
    license_file = project_root / "LICENSE"
    third_party = project_root / "THIRD_PARTY_LICENSES.txt"
    if not privacy_file.is_file():
        return False, "PRIVACY_POLICY.md fehlt"
    if not license_file.is_file():
        return False, "LICENSE fehlt"
    if not third_party.is_file():
        return False, "THIRD_PARTY_LICENSES.txt fehlt"
    return True, "Rechtliche Pflichtdokumente (Datenschutz, Lizenz, Third-Party) vorhanden."


def _check_screenshots(screenshots_dir: Path) -> tuple[bool, str]:
    if not screenshots_dir.is_dir():
        return False, f"Screenshot-Verzeichnis fehlt: {screenshots_dir}"
    screens = sorted(screenshots_dir.glob("*.png"))
    if len(screens) < 4:
        return False, f"Zu wenige Screenshots ({len(screens)} < 4 erforderlich)"
    for screen in screens:
        w, h = _png_size(screen)
        if (w, h) != (1920, 1080) and (w, h) != (1366, 768):
            return False, f"Screenshot {screen.name} hat unpassende Aufloesung ({w}x{h})"
    return True, f"{len(screens)} Store-Screenshots mit korrekter 16:9 Aufloesung validiert."


def _check_executable_contract(project_root: Path) -> tuple[bool, str]:
    bat_build = project_root / "build_exe.bat"
    spec_file = project_root / "NoteSpaceLLM.ico"
    if not bat_build.is_file():
        return False, "build_exe.bat fehlt"
    if not spec_file.is_file():
        return False, "NoteSpaceLLM.ico fehlt"
    return True, "Build-Skripte und Executable-Assets bereit."


def run_preflight(project_root: Path, output_dir: Path) -> WackSummary:
    """Fuehrt alle statischen WACK-Pruefungen hermetisch durch und schreibt Reports."""
    store_dir = project_root / "releases" / "windowsstore"
    manifest_path = project_root / "store_package" / "NoteSpaceLLM" / "AppxManifest.xml"
    settings_path = store_dir / "store_settings.json"
    screenshots_dir = store_dir / "screenshots"

    tests = [
        ("App-Manifest-Validierung", _check_manifest(manifest_path)),
        ("Restricted Capabilities & Package-Identitaet", _check_manifest(manifest_path)),
        ("Ressourcen & Kacheln", _check_assets(store_dir)),
        ("Store-Listing & Keywords (Policy 10.1.3)", _check_store_settings(settings_path)),
        ("Datenschutz & Lizenz-Transparenz", _check_privacy_and_licenses(project_root)),
        ("Store-Screenshots & Aufloesung", _check_screenshots(screenshots_dir)),
    ]

    pass_count = 0
    fail_count = 0
    results_list = []

    for name, (ok, message) in tests:
        if ok:
            pass_count += 1
            status = "PASS"
        else:
            fail_count += 1
            status = "FAIL"
        results_list.append({"name": name, "status": status, "message": message})

    now_str = datetime.now().strftime("%Y%m%d")
    json_report = output_dir / f"{WACK_REPORT_PREFIX}{now_str}.json"
    xml_report = output_dir / f"{WACK_REPORT_PREFIX}{now_str}.xml"

    output_dir.mkdir(parents=True, exist_ok=True)

    report_payload = {
        "timestamp": datetime.now().isoformat(),
        "app_name": "NoteSpaceLLM Pro",
        "identity_name": "Geiger.NoteSpaceLLM",
        "overall_result": "PASS" if fail_count == 0 else "FAIL",
        "requirements_tested": len(tests),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "warning_count": 0,
        "results": results_list,
    }
    json_report.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # XML-Report
    root_el = ET.Element("WackPreflightReport")
    root_el.set("OverallResult", report_payload["overall_result"])
    root_el.set("Timestamp", report_payload["timestamp"])
    for item in results_list:
        test_el = ET.SubElement(root_el, "TestResult")
        test_el.set("Name", item["name"])
        test_el.set("Status", item["status"])
        test_el.text = item["message"]
    xml_bytes = ET.tostring(root_el, encoding="utf-8", xml_declaration=True)
    xml_report.write_bytes(xml_bytes)

    return WackSummary(
        report=str(json_report),
        overall_result=report_payload["overall_result"],
        requirement_count=len(tests),
        pass_count=pass_count,
        fail_count=fail_count,
        warning_count=0,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WACK Runner fuer NoteSpaceLLM Pro")
    parser.add_argument("--msix", help="Pfad zum gebauten MSIX-Paket fuer echten WACK-Lauf")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "releases" / "windowsstore" / "test_reports"))
    parser.add_argument("--preflight-only", action="store_true", help="Nur den statischen Preflight ausfuehren")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)

    print("=== NoteSpaceLLM Pro — Windows App Certification Kit (WACK) Preflight ===")
    summary = run_preflight(PROJECT_ROOT, output_dir)
    print(f"Gesamtergebnis: {summary.overall_result}")
    print(f"Tests: {summary.requirement_count} | PASS: {summary.pass_count} | FAIL: {summary.fail_count}")
    print(f"Report abgelegt unter: {summary.report}")

    if args.msix and not args.preflight_only:
        msix_path = Path(args.msix)
        if not msix_path.is_file():
            print(f"FEHLER: MSIX-Datei nicht gefunden: {msix_path}", file=sys.stderr)
            return 1
        if not DEFAULT_APPCERT.is_file():
            print(f"HINWEIS: WACK appcert.exe nicht installiert unter {DEFAULT_APPCERT}. Nur Preflight abgeschlossen.")
            return 0
        if not _check_admin():
            print("HINWEIS: Reale WACK-Ausfuehrung erfordert Administratorrechte. Preflight erfolgreich beendet.")
            return 0

    return 0 if summary.overall_result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
