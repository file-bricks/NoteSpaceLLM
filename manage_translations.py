"""
manage_translations.py - Auto-Scanner fuer deutsche GUI-Strings
================================================================
Findet deutsche Strings in .py-Dateien und pflegt locales/translations.json.

Verwendung:
    python manage_translations.py [--dir PROJEKTVERZEICHNIS]
"""

import json
import re
import os
import sys

TRANSLATION_FILE = "locales/translations.json"

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurueck", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "oeffnen", "schliessen", "start", "aktualisieren",
]


def is_german(text):
    if any(ch in text for ch in "\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def find_german_strings(source_dir):
    german_strings = set()
    skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases'}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    continue
                for pattern in STRING_PATTERNS:
                    for match in pattern.findall(content):
                        if is_german(match):
                            german_strings.add(match.strip())
    return german_strings


def manage_translations(source_dir="."):
    trans_file = os.path.join(source_dir, TRANSLATION_FILE)

    if os.path.exists(trans_file):
        with open(trans_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
    else:
        translations = {}

    found = find_german_strings(source_dir)

    added = []
    for s in sorted(found):
        if s not in translations:
            translations[s] = {"de": s, "en": ""}
            added.append(s)

    os.makedirs(os.path.dirname(trans_file), exist_ok=True)
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)

    if added:
        print(f"[+] {len(added)} neue Eintraege hinzugefuegt:")
        for s in added[:20]:
            print(f"    - {s}")
        if len(added) > 20:
            print(f"    ... und {len(added) - 20} weitere")
    else:
        print("[i] Keine neuen deutschen Strings gefunden.")

    missing = [k for k, v in translations.items() if not v.get("en")]
    if missing:
        print(f"\n[!] {len(missing)} fehlende englische Uebersetzungen")
    else:
        print("\n[ok] Alle Strings haben englische Uebersetzungen.")

    print(f"\n[i] Gesamt: {len(translations)} Strings in {trans_file}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    manage_translations(target)
