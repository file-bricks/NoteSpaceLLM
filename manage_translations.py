#!/usr/bin/env python3
"""manage_translations.py — Translation Management CLI & CI Parity Gate für NoteSpaceLLM.

Unterstützt 6 Tier-2 Sprachen nach Policy P-006:
de, en, es, zh, ja, ru.

Verwendung:
    python manage_translations.py --check
    python manage_translations.py --stats
    python manage_translations.py --scan [--dir PROJEKTVERZEICHNIS]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
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

DEFAULT_APP_DIR = Path(__file__).resolve().parent
SUPPORTED_LANGUAGES = ["de", "en", "es", "zh", "ja", "ru"]

STRING_PATTERNS = [
    re.compile(r'text\s*=\s*"([^"]+)"'),
    re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
]

GERMAN_HINTS = [
    "datei", "filter", "fehler", "laden", "speichern",
    "ansicht", "optionen", "zurück", "anzeigen", "export",
    "import", "einstellungen", "abbrechen", "hilfe", "bearbeiten",
    "öffnen", "schließen", "start", "aktualisieren", "bericht",
    "notizen", "dokumente", "suche", "wissensdatenbank"
]


def resolve_translation_file(project_dir: Path | str | None = None) -> Path:
    base = Path(project_dir).resolve() if project_dir else DEFAULT_APP_DIR
    candidates = [
        base / "locales" / "translations.json",
        DEFAULT_APP_DIR / "locales" / "translations.json",
        base / "translations.json",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return base / "locales" / "translations.json"


def is_german(text: str) -> bool:
    if any(ch in text for ch in "äöüÄÖÜß"):
        return True
    text_lower = text.lower()
    return any(w in text_lower for w in GERMAN_HINTS)


def check_translations(project_dir: Path | str | None = None) -> tuple[int, dict[str, int]]:
    tf = resolve_translation_file(project_dir)
    if not tf.is_file():
        print(f"[!] translations.json nicht gefunden: {tf}")
        return 1, {}

    try:
        data = json.loads(tf.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[!] Fehler beim Parsen von {tf}: {exc}")
        return 1, {}

    total_keys = len(data)
    missing_by_lang: dict[str, list[str]] = {lang: [] for lang in SUPPORTED_LANGUAGES}

    for key, entry in data.items():
        if not isinstance(entry, dict):
            for lang in SUPPORTED_LANGUAGES:
                missing_by_lang[lang].append(key)
            continue
        for lang in SUPPORTED_LANGUAGES:
            val = entry.get(lang, "")
            if not val or not str(val).strip():
                missing_by_lang[lang].append(key)

    stats = {lang: total_keys - len(missing_by_lang[lang]) for lang in SUPPORTED_LANGUAGES}
    has_errors = any(len(miss) > 0 for miss in missing_by_lang.values())

    print(f"=== Translations Status: {tf.name} ({total_keys} Keys) ===")
    for lang in SUPPORTED_LANGUAGES:
        covered = stats[lang]
        missing_count = len(missing_by_lang[lang])
        pct = (covered / total_keys * 100) if total_keys > 0 else 0.0
        status = "OK" if missing_count == 0 else f"{missing_count} MISSING"
        print(f"  [{lang}] {covered}/{total_keys} ({pct:.1f}%) — {status}")

    if has_errors:
        print("\n[!] Übersetzungslücken gefunden:")
        for lang, missing in missing_by_lang.items():
            if missing:
                print(f"  {lang} ({len(missing)}): {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}")
        return 1, stats
    else:
        print("\n[✓] 100% Parität über alle 6 Zielsprachen gewahrt (0 fehlende Übersetzungen).")
        return 0, stats


def find_german_strings(source_dir: Path) -> set[str]:
    german_strings = set()
    skip_dirs = {"build", "dist", "venv", ".venv", "__pycache__", "releases", ".git"}

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for pattern in STRING_PATTERNS:
                    for match in pattern.findall(content):
                        if is_german(match):
                            german_strings.add(match.strip())
    return german_strings


def scan_and_update(source_dir: Path | None = None) -> int:
    base = Path(source_dir).resolve() if source_dir else DEFAULT_APP_DIR
    trans_file = resolve_translation_file(base)

    if trans_file.exists():
        try:
            translations = json.loads(trans_file.read_text(encoding="utf-8"))
        except Exception:
            translations = {}
    else:
        translations = {}

    found = find_german_strings(base)
    added = []
    upgraded = []

    for s in sorted(found):
        if s not in translations:
            entry = {"de": s}
            for lang in SUPPORTED_LANGUAGES:
                if lang != "de":
                    entry[lang] = ""
            translations[s] = entry
            added.append(s)
        else:
            for lang in SUPPORTED_LANGUAGES:
                if lang not in translations[s]:
                    translations[s][lang] = ""
                    if s not in upgraded:
                        upgraded.append(s)

    trans_file.parent.mkdir(parents=True, exist_ok=True)
    trans_file.write_text(json.dumps(translations, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"[i] Scan abgeschlossen. {len(translations)} Strings in {trans_file}")
    if added:
        print(f"[+] {len(added)} neue Strings hinzugefügt.")
    if upgraded:
        print(f"[+] {len(upgraded)} Strings um neue Sprach-Slots erweitert.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage NoteSpaceLLM translations")
    parser.add_argument("--check", action="store_true", help="CI Paritäts-Gate (Exit 0 wenn 100% komplett, sonst 1)")
    parser.add_argument("--stats", action="store_true", help="Statistiken anzeigen")
    parser.add_argument("--scan", action="store_true", help="Codebasis nach deutschen Strings scannen")
    parser.add_argument("--dir", type=str, default=None, help="Projektverzeichnis")

    args = parser.parse_args()

    project_dir = Path(args.dir) if args.dir else DEFAULT_APP_DIR

    if args.check:
        code, _ = check_translations(project_dir)
        return code
    elif args.stats:
        check_translations(project_dir)
        return 0
    elif args.scan:
        return scan_and_update(project_dir)
    else:
        # Default behavior: run check
        code, _ = check_translations(project_dir)
        return code


if __name__ == "__main__":
    sys.exit(main())
