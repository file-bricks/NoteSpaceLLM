"""
TranslationSystem - Multi-Language Support für Anwendungen
============================================================
Version: 2.0.0 (6-Sprachen-Ausbau)
Quelle: ARC_EntwicklungsschleifeAdvanced/TranslationSystem.py v2.4
Referenz: _LANG/LANGUAGE_CODES.md

Verwendung:
-----------
from translator import TranslationSystem

translator = TranslationSystem('de')
label.setText(translator.t('Datei öffnen'))
translator.set_language('en')
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set

SUPPORTED_LANGUAGES = ['de', 'en', 'es', 'zh', 'ja', 'ru']
DEFAULT_LANGUAGE = 'de'
FALLBACK_CHAIN = ['en', 'de']


class TranslationSystem:
    """Multi-Language Support System v2.0"""

    def __init__(self, default_lang: str = 'de', app_dir: Path = None):
        """
        Initialisiert Translation-System.

        Args:
            default_lang: Standard-Sprache (siehe LANGUAGE_CODES.md)
            app_dir: Verzeichnis der Anwendung (default: aktuelles Verzeichnis)
        """
        self.current_lang = default_lang if default_lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

        if app_dir is None:
            app_dir = Path.cwd()
        self.app_dir = Path(app_dir)

        self.translations_file = self.app_dir / "locales" / "translations.json"

        self.string_patterns = [
            re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addTab\s*\([^,]+,\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'text\s*=\s*"([^"]+)"'),
        ]

        self.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "öffnen", "speichern",
            "schließen", "einstellungen", "abbrechen", "ok", "ja", "nein",
            "start", "stop", "pause", "fortsetzen", "laden", "aktualisieren",
            "filter", "fehler", "export", "import", "optionen", "anzeigen",
        ]

        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        if self.translations_file.exists():
            try:
                with open(self.translations_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception:
                self.translations = {}
        else:
            self.translations = {}

    def _save_translations(self):
        self.translations_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.translations_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations, f, indent=2, ensure_ascii=False)

    def t(self, key: str) -> str:
        """
        Übersetzt einen Key in die aktuelle Sprache.
        Fallback-Kette: aktuelle Sprache -> en -> de -> Key selbst.
        """
        if key in self.translations:
            entry = self.translations[key]
            value = entry.get(self.current_lang)
            if value:
                return value
            for fb in FALLBACK_CHAIN:
                value = entry.get(fb)
                if value:
                    return value
            return key

        if self._is_german(key):
            entry = {"de": key}
            for lang in SUPPORTED_LANGUAGES:
                if lang != 'de':
                    entry[lang] = ""
            self.translations[key] = entry
            self._save_translations()

        return key

    def set_language(self, lang: str):
        if lang in SUPPORTED_LANGUAGES:
            self.current_lang = lang

    def get_language(self) -> str:
        return self.current_lang

    def get_supported_languages(self) -> List[str]:
        return list(SUPPORTED_LANGUAGES)

    def add_translation(self, key: str, **translations: str):
        if key not in self.translations:
            self.translations[key] = {lang: "" for lang in SUPPORTED_LANGUAGES}
        for lang, value in translations.items():
            if lang in SUPPORTED_LANGUAGES:
                self.translations[key][lang] = value
        self._save_translations()

    def scan_and_update(self, project_dir: Path = None) -> Dict:
        """Scannt Projekt-Dateien nach deutschen Strings und aktualisiert translations.json."""
        if project_dir is None:
            project_dir = self.app_dir

        found_strings = self._find_german_strings(project_dir)

        added = []
        for string in sorted(found_strings):
            if string not in self.translations:
                entry = {"de": string}
                for lang in SUPPORTED_LANGUAGES:
                    if lang != 'de':
                        entry[lang] = ""
                self.translations[string] = entry
                added.append(string)

        if added:
            self._save_translations()

        missing = {lang: [] for lang in SUPPORTED_LANGUAGES if lang != 'de'}
        for k, v in self.translations.items():
            for lang in SUPPORTED_LANGUAGES:
                if lang != 'de' and not v.get(lang):
                    missing[lang].append(k)

        return {'added': added, 'missing': missing, 'total': len(self.translations)}

    def _find_german_strings(self, directory: Path) -> Set[str]:
        german_strings = set()
        skip_dirs = {'build', 'dist', 'venv', '.venv', '__pycache__', 'releases'}

        for py_file in directory.rglob("*.py"):
            if any(folder in py_file.parts for folder in skip_dirs):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            for pattern in self.string_patterns:
                for match in pattern.findall(content):
                    if match and self._is_german(match):
                        german_strings.add(match.strip())

        return german_strings

    def _is_german(self, text: str) -> bool:
        # Echte deutsche Sonderzeichen oder klare deutsche Schlüsselwörter.
        if any(ch in text for ch in "\u00e4\u00f6\u00fc\u00c4\u00d6\u00dc\u00df"):
            return True
        text_lower = text.lower()
        return any(hint in text_lower for hint in self.german_hints)

    def get_missing_translations(self, lang: str = None) -> Dict[str, List[str]]:
        """Gibt fehlende Übersetzungen zurück. Ohne Argument: alle Sprachen."""
        if lang and lang in SUPPORTED_LANGUAGES:
            return {lang: [k for k, v in self.translations.items() if not v.get(lang)]}
        missing = {}
        for l in SUPPORTED_LANGUAGES:
            if l == 'de':
                continue
            m = [k for k, v in self.translations.items() if not v.get(l)]
            if m:
                missing[l] = m
        return missing


if __name__ == "__main__":
    tr = TranslationSystem('de')
    print(f"Sprache: {tr.get_language()}")
    print(f"Unterstützt: {', '.join(SUPPORTED_LANGUAGES)}")
    result = tr.scan_and_update()
    print(f"Scan: {result['total']} Strings, {len(result['added'])} neu")
    for lang, keys in result['missing'].items():
        print(f"  {lang}: {len(keys)} fehlend")
