import json
import tempfile
import unittest
from pathlib import Path

from translator import SUPPORTED_LANGUAGES, TranslationSystem


class TranslationSystemTests(unittest.TestCase):
    def test_is_german_distinguishes_english_from_german_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            tr = TranslationSystem("de", Path(tmp))

            self.assertFalse(tr._is_german("Hello world"))
            self.assertTrue(tr._is_german("Datei öffnen"))

    def test_scan_and_update_only_picks_up_german_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "locales").mkdir()
            (project_dir / "sample.py").write_text(
                'from PySide6.QtWidgets import QPushButton\n'
                'btn1 = QPushButton("Hello")\n'
                'btn2 = QPushButton("Datei öffnen")\n',
                encoding="utf-8",
            )

            tr = TranslationSystem("de", project_dir)
            result = tr.scan_and_update(project_dir)

            self.assertEqual(result["added"], ["Datei öffnen"])
            # Missing entries are reported for every supported target locale.
            self.assertIsInstance(result["missing"], dict)
            for lang in (code for code in SUPPORTED_LANGUAGES if code != "de"):
                self.assertIn("Datei öffnen", result["missing"].get(lang, []))
            self.assertEqual(result["total"], 1)

            translations_path = project_dir / "locales" / "translations.json"
            data = json.loads(translations_path.read_text(encoding="utf-8"))
            self.assertIn("Datei öffnen", data)
            entry = data["Datei öffnen"]
            self.assertEqual(entry["de"], "Datei öffnen")
            for lang in (code for code in SUPPORTED_LANGUAGES if code != "de"):
                self.assertIn(lang, entry)

    def test_gui_catalog_lookup_is_stable_keyed_and_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            app_dir = Path(tmp)
            locale_dir = app_dir / "locales"
            locale_dir.mkdir()
            source = "{count} Dokumente geladen"
            catalog = {
                "schema": "notespacellm.gui-i18n-runtime.v1",
                "entries": [{
                    "key": "gui.status.documents_loaded",
                    "canonical_source_value": source,
                    "translations": {
                        "de": source,
                        "en": "Loaded {count} documents",
                        "fr": "{count} documents chargés",
                    },
                }],
            }
            (locale_dir / "gui_translations.json").write_text(
                json.dumps(catalog, ensure_ascii=False), encoding="utf-8"
            )
            before = (locale_dir / "gui_translations.json").read_bytes()

            tr = TranslationSystem("fr", app_dir)
            self.assertEqual(tr.t("gui.status.documents_loaded"), "{count} documents chargés")
            self.assertEqual(tr.t(source), "{count} documents chargés")
            self.assertFalse(tr.has_translation_source("Nicht im Katalog"))

            self.assertEqual((locale_dir / "gui_translations.json").read_bytes(), before)
            self.assertFalse((locale_dir / "translations.json").exists())


if __name__ == "__main__":
    unittest.main()
