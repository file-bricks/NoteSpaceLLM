"""Guard the release license inventory against dependency drift."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _requirement_names():
    names = []
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        base = line.split(";", 1)[0].strip()
        names.append(re.split(r"[<>=!~\[]", base, 1)[0].strip())
    return names


def test_third_party_license_inventory_covers_runtime_dependencies():
    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")

    assert "Checked: 2026-07-02" in inventory
    assert "licensed under AGPL-3.0-only according to `LICENSE`" in inventory
    assert "not a frozen transitive SBOM" in inventory

    for package in _requirement_names():
        assert f"| {package}" in inventory

    for package in ("PySide6_Addons", "PySide6_Essentials", "shiboken6"):
        assert f"| {package}" in inventory


def test_web_companion_has_no_undocumented_runtime_dependencies():
    package_json = json.loads((ROOT / "web_companion" / "package.json").read_text(encoding="utf-8"))
    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")

    assert not package_json.get("dependencies")
    assert not package_json.get("devDependencies")
    assert "`web_companion/package.json` has no dependencies or devDependencies" in inventory
