"""
Tests für _PipelineHelpDialog (UX-HOCH c) — 2026-06-01

Verifiziert:
- Dialog definiert alle 5 Schritte mit Pflichtfeldern
- Schritte haben Titel, Icon, Farbe, Beschreibung
- Optional-Badge nur auf Schritt 3 (Detailanalysen)
- Schritt-Reihenfolge korrekt
- Alle 5 Schritte decken den vollständigen Workflow ab
"""

import re
import ast
import pytest
from unittest.mock import patch


class TestPipelineHelpDialogSteps:
    """Schritt-Definitionen im Dialog sind korrekt und vollständig."""

    def _get_steps(self):
        """Lädt STEPS-Daten direkt aus dem Quelltext (kein GUI-Import nötig)."""
        import ast
        import re
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()
        # STEPS-Liste aus Quelltext extrahieren
        match = re.search(r'STEPS\s*=\s*(\[.*?\])\s*\n\s*def ', source, re.DOTALL)
        if not match:
            raise RuntimeError("STEPS-Liste nicht in main_window.py gefunden")
        return ast.literal_eval(match.group(1))

    def test_five_steps_defined(self):
        """Dialog hat genau 5 Schritte."""
        steps = self._get_steps()
        assert len(steps) == 5, f"Erwartet 5 Schritte, gefunden: {len(steps)}"

    def test_all_steps_have_required_fields(self):
        """Jeder Schritt hat number, title, icon, color, desc, optional."""
        required = {"number", "title", "icon", "color", "desc", "optional"}
        steps = self._get_steps()
        for s in steps:
            missing = required - set(s.keys())
            assert not missing, f"Schritt '{s.get('title','?')}' fehlt: {missing}"

    def test_step_numbers_sequential(self):
        """Schritte sind sequentiell nummeriert: 1, 2, 3, 4, 5."""
        steps = self._get_steps()
        numbers = [s["number"] for s in steps]
        assert numbers == ["1", "2", "3", "4", "5"], f"Falsche Reihenfolge: {numbers}"

    def test_only_step_3_is_optional(self):
        """Nur Schritt 3 (Detailanalysen) ist optional."""
        steps = self._get_steps()
        optional_steps = [s["title"] for s in steps if s["optional"]]
        assert len(optional_steps) == 1, f"Erwartet 1 optionalen Schritt, gefunden: {optional_steps}"
        assert "3" == steps[2]["number"]
        assert steps[2]["optional"] is True

    def test_step_colors_are_valid_hex(self):
        """Alle Schritt-Farben sind gültige Hex-Farben."""
        import re
        steps = self._get_steps()
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{3,6}$')
        for s in steps:
            assert hex_pattern.match(s["color"]), \
                f"Ungültige Farbe in Schritt '{s['title']}': {s['color']}"

    def test_step_descriptions_not_empty(self):
        """Alle Beschreibungen sind nicht leer."""
        steps = self._get_steps()
        for s in steps:
            assert s["desc"].strip(), f"Leere Beschreibung in Schritt '{s['title']}'"

    def test_step_icons_not_empty(self):
        """Alle Schritte haben ein Icon."""
        steps = self._get_steps()
        for s in steps:
            assert s["icon"].strip(), f"Fehlendes Icon in Schritt '{s['title']}'"

    def test_workflow_coverage(self):
        """Die Schritte decken den vollständigen Workflow ab: hinzufügen → exportieren."""
        steps = self._get_steps()
        titles_lower = " ".join(s["title"].lower() for s in steps)
        assert "dokument" in titles_lower or "hinzuf" in titles_lower, \
            "Schritt 1 muss Dokumente/Hinzufügen thematisieren"
        assert "text" in titles_lower or "extrahier" in titles_lower, \
            "Schritt 2 muss Textextraktion thematisieren"
        assert "analyse" in titles_lower or "detail" in titles_lower, \
            "Schritt 3 muss Analyse thematisieren"
        assert "bericht" in titles_lower, "Schritt 4 muss Bericht thematisieren"
        assert "export" in titles_lower, "Schritt 5 muss Export thematisieren"

    def test_report_step_mentions_automatic_extraction(self):
        """Bericht-Schritt erklärt automatische Extraktion."""
        steps = self._get_steps()
        report_step = next((s for s in steps if "bericht" in s["title"].lower()), None)
        assert report_step is not None, "Bericht-Schritt nicht gefunden"
        desc_lower = report_step["desc"].lower()
        assert "automatisch" in desc_lower, \
            "Bericht-Schritt muss erklären, dass Extraktion automatisch ausgelöst wird"

    def test_toolbar_help_button_defined_in_setup_toolbar(self):
        """'?' Hilfe-Button ist in _setup_toolbar definiert."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()
        toolbar_start = source.index("def _setup_toolbar(self):")
        toolbar_end = source.index("def _setup_panels(self):")
        toolbar_code = source[toolbar_start:toolbar_end]
        assert "_show_pipeline_help" in toolbar_code, \
            "_show_pipeline_help muss in _setup_toolbar verdrahtet sein"
        assert '"?"' in toolbar_code or "'?'" in toolbar_code, \
            "Hilfe-Button '?' muss in Toolbar definiert sein"

    def test_pipeline_help_method_exists_in_main_window(self):
        """_show_pipeline_help Methode existiert in MainWindow."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()
        assert "def _show_pipeline_help(self):" in source, \
            "_show_pipeline_help Methode fehlt in MainWindow"

    def test_pipeline_help_dialog_class_exists(self):
        """_PipelineHelpDialog Klasse ist definiert."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()
        assert "class _PipelineHelpDialog" in source, \
            "_PipelineHelpDialog Klasse fehlt"
