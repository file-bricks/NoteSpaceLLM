"""
TranslationSystem - Multi-Language Support für Anwendungen
============================================================
Version: 2.0.0 (11-Sprachen-Ausbau)
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

SUPPORTED_LANGUAGES = ['en', 'de', 'es', 'zh', 'ja', 'ru', 'fr', 'hi', 'ar', 'bn', 'pt']
DEFAULT_LANGUAGE = 'de'
FALLBACK_CHAIN = ['en', 'de']
LANGUAGE_NAMES = {
    'en': 'English',
    'de': 'Deutsch',
    'es': 'Español',
    'zh': '简体中文',
    'ja': '日本語',
    'ru': 'Русский',
    'fr': 'Français',
    'hi': 'हिन्दी',
    'ar': 'العربية',
    'bn': 'বাংলা',
    'pt': 'Português',
}


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
        self.ui_translations_file = self.app_dir / "locales" / "gui_translations.json"
        self.ui_translations = {}
        self.ui_keys = {}

        self.string_patterns = [
            re.compile(r'setText\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QLabel\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'QPushButton\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addAction\s*\([^,]*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'addTab\s*\([^,]+,\s*["\']([^"\']+)["\']\s*\)'),
            re.compile(r'text\s*=\s*"([^"]+)"'),
        ]

        # Nur eindeutig deutsche Wörter -- englisch identische Begriffe wie
        # "ok", "start", "stop", "pause", "filter", "export", "import" würden
        # englische UI-Texte fälschlich als deutsch einstufen.
        self.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "öffnen", "speichern",
            "schließen", "einstellungen", "abbrechen", "ja", "nein",
            "fortsetzen", "laden", "aktualisieren",
            "fehler", "optionen", "anzeigen",
        ]
        # Ganzwort-Abgleich: "ja" darf nicht in "Jakarta", "laden" nicht in "Paladin" greifen
        self._german_hint_re = re.compile(
            r"\b(?:" + "|".join(re.escape(h) for h in self.german_hints) + r")\b"
        )

        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        if self.translations_file.exists():
            try:
                with open(self.translations_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                self.translations = loaded if isinstance(loaded, dict) else {}
            except Exception:
                self.translations = {}
        else:
            self.translations = {}
        self._load_ui_translations()

    def _load_ui_translations(self):
        """Load the stable-key GUI catalog and index it by its German source text."""
        self.ui_translations = {}
        self.ui_keys = {}
        if not self.ui_translations_file.exists():
            return
        try:
            with open(self.ui_translations_file, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except (OSError, json.JSONDecodeError):
            return

        records = payload.get('entries', []) if isinstance(payload, dict) else []
        if not isinstance(records, list):
            return
        for record in records:
            if not isinstance(record, dict):
                continue
            stable_key = record.get('key')
            source = record.get('canonical_source_value')
            translations = record.get('translations', {})
            if not isinstance(stable_key, str) or not isinstance(source, str):
                continue
            if not isinstance(translations, dict):
                translations = {}
            self.ui_keys[stable_key] = source
            self.ui_translations[source] = translations

    def _save_translations(self):
        self.translations_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.translations_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations, f, indent=2, ensure_ascii=False)

    def _resolve_entry(self, entry, fallback: str) -> str:
        if not isinstance(entry, dict):
            return fallback
        value = entry.get(self.current_lang)
        if isinstance(value, str) and value:
            return value
        for language in FALLBACK_CHAIN:
            value = entry.get(language)
            if isinstance(value, str) and value:
                return value
        return fallback

    @staticmethod
    def _translation_for(entry, language: str) -> str:
        if isinstance(entry, dict):
            value = entry.get(language)
            return value if isinstance(value, str) else ""
        return ""

    def t(self, key: str) -> str:
        """
        Übersetzt einen Quelltext oder stabilen GUI-Schlüssel.

        Fallback-Kette: aktuelle Sprache -> en -> de -> Quelltext.
        Eine fehlende Übersetzung wird nicht automatisch in den Quellkatalog
        geschrieben; der Translator bleibt beim bloßen Anzeigen schreibfrei.
        """
        if key in self.ui_keys:
            source = self.ui_keys[key]
            return self._resolve_entry(self.ui_translations.get(source), source)
        if key in self.ui_translations or key in self.translations:
            gui_entry = self.ui_translations.get(key)
            legacy_entry = self.translations.get(key)
            for entry in (gui_entry, legacy_entry):
                value = self._translation_for(entry, self.current_lang)
                if value:
                    return value
            for language in FALLBACK_CHAIN:
                for entry in (gui_entry, legacy_entry):
                    value = self._translation_for(entry, language)
                    if value:
                        return value
            return key
        return key

    def has_translation_source(self, source: str) -> bool:
        """Return whether a string is present in either read-only GUI catalog."""
        return source in self.ui_translations or source in self.translations

    def ui(self, stable_key: str, source: str) -> str:
        """Translate a GUI string by its stable key, falling back to source text."""
        if stable_key in self.ui_keys:
            return self.t(stable_key)
        return self.t(source)

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
        return bool(self._german_hint_re.search(text.lower()))

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
