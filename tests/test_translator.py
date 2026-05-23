import json
import tempfile
import unittest
from pathlib import Path

from translator import TranslationSystem


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
            self.assertEqual(result["missing"], ["Datei öffnen"])
            self.assertEqual(result["total"], 1)

            translations_path = project_dir / "locales" / "translations.json"
            data = json.loads(translations_path.read_text(encoding="utf-8"))
            self.assertEqual(
                data,
                {"Datei öffnen": {"de": "Datei öffnen", "en": ""}},
            )


if __name__ == "__main__":
    unittest.main()
