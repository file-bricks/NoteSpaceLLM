import sys

import pytest

try:
    from PySide6.QtWidgets import QApplication

    from src.gui.document_panel import DocumentPanel
    from src.gui.workflow_panel import WorkflowPanel

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


@requires_pyside
def test_document_panel_primary_controls_expose_accessible_context(qt_app):
    panel = DocumentPanel()

    assert panel.add_files_btn.toolTip()
    assert panel.add_files_btn.accessibleName() == "Dateien hinzufügen"
    assert panel.add_folder_btn.toolTip()
    assert panel.add_folder_btn.accessibleName() == "Ordner hinzufügen"
    assert panel.select_all_btn.toolTip()
    assert panel.select_all_btn.accessibleName() == "Alle Dokumente auswählen"
    assert panel.deselect_all_btn.toolTip()
    assert panel.deselect_all_btn.accessibleName() == "Keine Dokumente auswählen"
    assert panel.tree.toolTip()
    assert panel.tree.accessibleName() == "Dokumentenliste"


@requires_pyside
def test_workflow_panel_primary_controls_expose_accessible_context(qt_app):
    panel = WorkflowPanel()

    assert panel.report_type_combo.toolTip()
    assert panel.report_type_combo.accessibleName() == "Berichtstyp"
    assert panel.workflow_combo.toolTip()
    assert panel.workflow_combo.accessibleName() == "Workflow"
    assert panel.question_edit.toolTip()
    assert panel.question_edit.accessibleName() == "Hauptfragestellung"
    assert panel.edit_workflow_btn.toolTip()
    assert panel.edit_workflow_btn.accessibleName() == "Workflow bearbeiten"
    assert panel.start_btn.toolTip()
    assert panel.start_btn.accessibleName() == "Bericht erstellen"
