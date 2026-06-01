"""
Tests für UX-Verbesserungen (2026-06-01):
- Toolbar-Buttons haben Tooltips
- Pipeline-Phasen-Label vorhanden und korrekte Texte
- "LLM-Prompt exportieren" Button korrekt beschriftet
"""

import sys
import pytest
from unittest.mock import MagicMock, patch

try:
    from PySide6.QtWidgets import QApplication, QAction, QLabel, QPushButton
    from PySide6.QtCore import Qt
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

requires_pyside = pytest.mark.skipif(not PYSIDE_AVAILABLE, reason="PySide6 nicht installiert")


@pytest.fixture(scope="session")
def qt_app():
    if not PYSIDE_AVAILABLE:
        pytest.skip("PySide6 nicht installiert")
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


class TestToolbarTooltips:
    """Toolbar-Buttons haben aussagekräftige Tooltips (Source-Code-Analyse)."""

    def test_setup_toolbar_action_tooltips_defined(self):
        """_setup_toolbar setzt Tooltips auf alle 5 Actions."""
        import ast
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        # Prüfen ob setToolTip in _setup_toolbar aufgerufen wird
        # Mindestens 5 setToolTip-Aufrufe im Toolbar-Bereich
        toolbar_start = source.index("def _setup_toolbar(self):")
        toolbar_end = source.index("def _setup_panels(self):")
        toolbar_code = source[toolbar_start:toolbar_end]

        tooltip_count = toolbar_code.count("setToolTip(")
        assert tooltip_count >= 5, \
            f"Erwartet ≥5 setToolTip-Aufrufe in _setup_toolbar, gefunden: {tooltip_count}"

    def test_toolbar_tooltips_mention_step_numbers(self):
        """Tooltips erklären Pipeline-Reihenfolge (Schritt 1/2/3)."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        toolbar_start = source.index("def _setup_toolbar(self):")
        toolbar_end = source.index("def _setup_panels(self):")
        toolbar_code = source[toolbar_start:toolbar_end]

        assert "Schritt 1" in toolbar_code, "Toolbar-Tooltip soll Schritt 1 erwähnen"
        assert "Schritt 3" in toolbar_code, "Toolbar-Tooltip soll Schritt 3 erwähnen"

    def test_bericht_erstellen_tooltip_mentions_auto_extract(self):
        """'Bericht erstellen'-Tooltip erklärt automatische Extraktion."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        toolbar_start = source.index("def _setup_toolbar(self):")
        toolbar_end = source.index("def _setup_panels(self):")
        toolbar_code = source[toolbar_start:toolbar_end]

        # "automatisch" oder "Extraktion" soll im Bericht-Tooltip stehen
        assert "automatisch" in toolbar_code.lower() or "extraktion" in toolbar_code.lower(), \
            "Bericht-Tooltip soll erklären dass Extraktion automatisch ausgelöst wird"


class TestPipelinePhaseLabel:
    """Pipeline-Phasen-Label (Source-Code + Runtime-Tests)."""

    def test_pipeline_label_added_to_statusbar(self):
        """_setup_statusbar legt _pipeline_label als permanentes Widget an."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        statusbar_start = source.index("def _setup_statusbar(self):")
        statusbar_end = source.index("def _connect_signals(self):")
        statusbar_code = source[statusbar_start:statusbar_end]

        assert "_pipeline_label" in statusbar_code, \
            "_pipeline_label muss in _setup_statusbar angelegt werden"
        assert "addPermanentWidget" in statusbar_code, \
            "Pipeline-Label muss als Permanent-Widget zur Statusleiste hinzugefügt werden"

    def test_pipeline_label_has_tooltip(self):
        """_pipeline_label erklärt alle 4 Pipeline-Phasen im Tooltip."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        statusbar_start = source.index("def _setup_statusbar(self):")
        statusbar_end = source.index("def _connect_signals(self):")
        statusbar_code = source[statusbar_start:statusbar_end]

        assert "setToolTip" in statusbar_code, \
            "Pipeline-Label braucht Tooltip der die Phasen erklärt"

    @requires_pyside
    def test_update_pipeline_phase_no_project(self):
        """_update_pipeline_phase läuft ohne Projekt ohne Exception."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("mw2", "src/gui/main_window.py")
        mod = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {
            'langchain_chroma': MagicMock(),
            'chromadb': MagicMock(),
        }):
            spec.loader.exec_module(mod)

        obj = MagicMock()
        obj._pipeline_label = MagicMock()
        obj._current_project = None

        mod.MainWindow._update_pipeline_phase(obj)
        obj._pipeline_label.setText.assert_called_with("📄 Keine Dokumente")

    @requires_pyside
    def test_update_pipeline_phase_with_unextracted_docs(self):
        """Pipeline-Label zeigt 'extrahieren' wenn Docs ohne Text vorhanden."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("mw3", "src/gui/main_window.py")
        mod = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {
            'langchain_chroma': MagicMock(),
            'chromadb': MagicMock(),
        }):
            spec.loader.exec_module(mod)

        mock_doc = MagicMock()
        mock_doc.is_directory = False
        mock_doc.extracted_text = None
        mock_doc.is_indexed = False

        mock_project = MagicMock()
        mock_project.documents.documents = [mock_doc]

        obj = MagicMock()
        obj._pipeline_label = MagicMock()
        obj._current_project = mock_project

        mod.MainWindow._update_pipeline_phase(obj)
        call_text = obj._pipeline_label.setText.call_args[0][0]
        assert "extrahieren" in call_text.lower() or "schritt 1" in call_text.lower(), \
            f"Unerwarteter Text: '{call_text}'"

    @requires_pyside
    def test_update_pipeline_phase_with_extracted_docs(self):
        """Pipeline-Label zeigt 'Bericht erstellen' wenn alle Docs extrahiert."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("mw4", "src/gui/main_window.py")
        mod = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {
            'langchain_chroma': MagicMock(),
            'chromadb': MagicMock(),
        }):
            spec.loader.exec_module(mod)

        mock_doc = MagicMock()
        mock_doc.is_directory = False
        mock_doc.extracted_text = "Extrahierter Text..."
        mock_doc.is_indexed = False

        mock_project = MagicMock()
        mock_project.documents.documents = [mock_doc]

        obj = MagicMock()
        obj._pipeline_label = MagicMock()
        obj._current_project = mock_project

        mod.MainWindow._update_pipeline_phase(obj)
        call_text = obj._pipeline_label.setText.call_args[0][0]
        assert "bericht" in call_text.lower() or "✅" in call_text, \
            f"Unerwarteter Text: '{call_text}'"


class TestOutputPanelUX:
    """Output-Panel UX-Korrekturen."""

    def test_prompt_export_button_label_is_clear(self):
        """'LLM-Prompt exportieren' statt altem 'Prompt exportieren'."""
        with open("src/gui/output_panel.py", "r", encoding="utf-8") as f:
            source = f.read()

        assert '"LLM-Prompt exportieren"' in source or "'LLM-Prompt exportieren'" in source, \
            "Button-Label soll 'LLM-Prompt exportieren' heißen"

    def test_prompt_export_button_old_label_gone(self):
        """Alter Label-Text 'Prompt exportieren' nicht mehr als Button-Titel vorhanden."""
        with open("src/gui/output_panel.py", "r", encoding="utf-8") as f:
            source = f.read()

        # Suche nach QPushButton("Prompt exportieren") — nicht mehr erlaubt
        import re
        old_label = re.search(r'QPushButton\(["\']Prompt exportieren["\']\)', source)
        assert old_label is None, \
            "Alter Button-Titel 'Prompt exportieren' ist noch vorhanden — bitte auf 'LLM-Prompt exportieren' aktualisieren"

    def test_prompt_export_button_has_informative_tooltip(self):
        """Tooltip erklärt dass es der an das LLM gesendete Prompt ist."""
        with open("src/gui/output_panel.py", "r", encoding="utf-8") as f:
            source = f.read()

        tooltip_start = source.index("prompt_export_btn.setToolTip(")
        tooltip_end = source.index(")", tooltip_start + 40)
        tooltip_code = source[tooltip_start:tooltip_end + 50]

        assert "llm" in tooltip_code.lower() or "an das llm" in tooltip_code.lower(), \
            "Tooltip soll erklären dass es der an das LLM gesendete Prompt ist"
