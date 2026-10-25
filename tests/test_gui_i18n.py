import json
from datetime import datetime
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings, QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QInputDialog,
    QPushButton,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.i18n import (
    LANGUAGE_NAMES,
    LocalizedLabel,
    LocalizedStatusBar,
    SUPPORTED_LANGUAGES,
    LocalizedInputDialog,
    LocalizedMessageBox,
    UI_LANGUAGE_KEY,
    _translated_filters,
    load_ui_language,
    persist_ui_language,
    translate_ui_text,
    translate_widget_tree,
)
from src.gui.main_window import MainWindow
from src.gui.chat_panel import ChatMessage
from translator import TranslationSystem


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def write_test_catalog(app_dir: Path) -> TranslationSystem:
    entries = [
        ("gui.language.label", "Sprache:", {"fr": "Langue :", "ar": "اللغة:"}),
        ("gui.common.open", "Öffnen", {"en": "Open", "fr": "Ouvrir"}),
        ("gui.common.input_placeholder", "Eingabe:", {"en": "Input:", "fr": "Saisie :"}),
        ("gui.common.cancel", "Abbrechen", {"fr": "Annuler", "ar": "إلغاء"}),
        ("gui.common.ok", "OK", {"fr": "OK", "ar": "موافق"}),
        ("gui.common.yes", "Ja", {"fr": "Oui", "ar": "نعم"}),
        ("gui.common.no", "Nein", {"fr": "Non", "ar": "لا"}),
        ("gui.dialog.new_project", "Neues Projekt", {"fr": "Nouveau projet"}),
        ("gui.dialog.project_name", "Projektname:", {"fr": "Nom du projet :"}),
        ("gui.dialog.error", "Fehler", {"fr": "Erreur"}),
        ("gui.dialog.failed", "Der Vorgang ist fehlgeschlagen.", {"fr": "L’opération a échoué."}),
        ("gui.workflow.analysis", "Analyse", {"en": "Analysis", "fr": "Analyse"}),
        ("gui.workflow.summary", "Zusammenfassung", {"en": "Summary", "fr": "Résumé"}),
        ("gui.workflow.research", "Forschungsbericht", {"en": "Research report", "fr": "Rapport de recherche"}),
        ("gui.workflow.comparison", "Vergleich", {"en": "Comparison", "fr": "Comparaison"}),
        ("gui.files.documents", "Dokumente", {"fr": "Documents"}),
        ("gui.files.report", "Bericht", {"en": "Report", "fr": "Rapport"}),
        ("gui.files.text", "Text", {"en": "Text", "fr": "Texte"}),
        ("gui.workflow.label", "Workflow", {"en": "Workflow", "fr": "Flux de travail"}),
        ("gui.files.word", "Word", {"fr": "Document Word"}),
        ("gui.status.project_created", "Projekt '{value1}' erstellt", {"fr": "Projet '{value1}' créé"}),
        ("gui.chat.confidence", " (Konfidenz: {percent:.0%})", {"fr": " (Confiance : {percent:.0%})"}),
        ("gui.status.ready", "Bereit", {"en": "Ready", "fr": "Prêt"}),
        ("gui.status.finished", "Fertig", {"en": "Finished", "fr": "Terminé"}),
    ]
    records = []
    for key, source, partial in entries:
        translations = {"de": source, **partial}
        records.append({"key": key, "canonical_source_value": source, "translations": translations})
    locale_dir = app_dir / "locales"
    locale_dir.mkdir(parents=True, exist_ok=True)
    (locale_dir / "gui_translations.json").write_text(
        json.dumps({"schema": "notespacellm.gui-i18n-runtime.v1", "entries": records}, ensure_ascii=False),
        encoding="utf-8",
    )
    return TranslationSystem("de", app_dir)


def test_worldset_language_codes_and_names_are_complete():
    assert SUPPORTED_LANGUAGES == ["en", "de", "es", "zh", "ja", "ru", "fr", "hi", "ar", "bn", "pt"]
    assert set(LANGUAGE_NAMES) == set(SUPPORTED_LANGUAGES)
    assert len(set(LANGUAGE_NAMES.values())) == len(SUPPORTED_LANGUAGES)


def test_widget_retranslation_preserves_user_text_and_code_values(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    root = QWidget()
    layout = QVBoxLayout(root)
    button = QPushButton("Öffnen")
    path_field = QLineEdit()
    path_field.setPlaceholderText("Eingabe:")
    path_field.setText("C:/private/Report.txt")
    provider_combo = QComboBox()
    provider_combo.addItem("ollama", "ollama")
    provider_combo.addItem("claude-code", "claude-code")
    layout.addWidget(button)
    layout.addWidget(path_field)
    layout.addWidget(provider_combo)

    translator.set_language("fr")
    translate_widget_tree(root, translator)

    assert button.text() == "Ouvrir"
    assert path_field.placeholderText() == "Saisie :"
    assert path_field.text() == "C:/private/Report.txt"
    assert provider_combo.currentText() == "ollama"
    assert provider_combo.currentData() == "ollama"


def test_dynamic_localized_status_label_keeps_latest_source_across_language_changes(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    root = QWidget()
    layout = QVBoxLayout(root)
    status = LocalizedLabel("Bereit", translator, root)
    layout.addWidget(status)

    # Cache/replay a static tree pass, then move the runtime status forward.
    translate_widget_tree(root, translator)
    assert status.text() == "Bereit"
    status.setText("Fertig")
    assert status.text() == "Fertig"

    for language, expected in (("fr", "Terminé"), ("en", "Finished"), ("de", "Fertig"), ("fr", "Terminé")):
        translator.set_language(language)
        translate_widget_tree(root, translator)
        status.retranslate()
        assert status.text() == expected
        assert status._source_text == "Fertig"


def test_expired_localized_statusbar_message_is_not_resurrected_on_language_change(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    window = QMainWindow()
    statusbar = LocalizedStatusBar(translator, window)
    window.setStatusBar(statusbar)
    window.show()
    qapp.processEvents()

    statusbar.showMessage("Fertig", 30)
    assert statusbar.currentMessage() == "Fertig"
    QTest.qWait(90)
    assert statusbar.currentMessage() == ""
    assert statusbar._source_message == ""

    translator.set_language("fr")
    statusbar.retranslate()
    assert statusbar.currentMessage() == ""

    # A message that has not expired remains replayable in the current locale.
    statusbar.showMessage("Fertig", 0)
    assert statusbar.currentMessage() == "Terminé"
    translator.set_language("en")
    statusbar.retranslate()
    assert statusbar.currentMessage() == "Finished"
    window.close()


def test_live_language_change_preserves_data_that_collides_with_ui_sources(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    settings = QSettings(str(tmp_path / "collisions.ini"), QSettings.Format.IniFormat)
    window = MainWindow(
        settings=settings,
        translator=translator,
        project_manager=object(),
        start_background_tasks=False,
    )
    try:
        # User, project, document, and workflow values intentionally equal
        # strings that are also translated UI sources. These remain unmarked.
        window.chat_panel._add_message(
            ChatMessage(role="user", content="Bericht", timestamp=datetime.now())
        )
        user_text = window.chat_panel._message_widgets[-1].content_label
        project_name = QLabel("Text")
        window.document_panel.layout().insertWidget(0, project_name)
        document_item = QTreeWidgetItem(window.document_panel.tree, ["Sprache:", "", ""])
        workflow_name = window.workflow_panel._step_widgets[0].name_label
        workflow_name.setText("Workflow")

        expected = {
            "user": user_text.text().encode("utf-8"),
            "project": project_name.text().encode("utf-8"),
            "document": document_item.text(0).encode("utf-8"),
            "workflow": workflow_name.text().encode("utf-8"),
        }
        window._language_combo.setCurrentIndex(window._language_combo.findData("fr"))
        qapp.processEvents()

        assert translator.get_language() == "fr"
        assert window._language_label.text() == "Langue :"
        assert user_text.text().encode("utf-8") == expected["user"]
        assert project_name.text().encode("utf-8") == expected["project"]
        assert document_item.text(0).encode("utf-8") == expected["document"]
        assert workflow_name.text().encode("utf-8") == expected["workflow"]
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_ui_templates_keep_opaque_project_names_and_file_patterns(tmp_path):
    translator = write_test_catalog(tmp_path)
    translator.set_language("fr")
    assert translate_ui_text("Projekt 'Projekt Lumière' erstellt", translator) == "Projet 'Projekt Lumière' créé"
    assert translate_ui_text(" (Konfidenz: 83%)", translator) == " (Confiance : 83%)"
    assert translate_ui_text("Word (.docx)", translator) == "Document Word (.docx)"
    assert _translated_filters("Dokumente (*.pdf *.docx)", translator) == ["Documents (*.pdf *.docx)"]


def test_dialog_standard_buttons_are_translated(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    translator.set_language("fr")
    dialog = QDialog()
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
    layout = QVBoxLayout(dialog)
    layout.addWidget(buttons)
    translate_widget_tree(dialog, translator)
    assert buttons.button(QDialogButtonBox.StandardButton.Cancel).text() == "Annuler"
    assert buttons.button(QDialogButtonBox.StandardButton.Ok).text() == "OK"


def test_static_input_dialog_translates_chrome_and_returns_entered_text(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    translator.set_language("fr")
    parent = QWidget()
    parent._translator = translator
    observed = {}

    def complete_dialog():
        dialog = next(widget for widget in QApplication.topLevelWidgets() if isinstance(widget, QInputDialog))
        observed["title"] = dialog.windowTitle()
        observed["label"] = dialog.labelText()
        cancel = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Cancel)
        observed["cancel"] = cancel.text()
        dialog.setTextValue("Projet expérimental")
        dialog.accept()

    QTimer.singleShot(20, complete_dialog)
    value, accepted = LocalizedInputDialog.getText(parent, "Neues Projekt", "Projektname:")
    assert accepted is True
    assert value == "Projet expérimental"
    assert observed == {"title": "Nouveau projet", "label": "Nom du projet :", "cancel": "Annuler"}


def test_static_message_box_translates_message_and_button(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    translator.set_language("fr")
    parent = QWidget()
    parent._translator = translator
    observed = {}

    def complete_dialog():
        dialog = next(widget for widget in QApplication.topLevelWidgets() if isinstance(widget, QMessageBox))
        observed["title"] = dialog.windowTitle()
        observed["text"] = dialog.text()
        observed["ok"] = dialog.button(QMessageBox.StandardButton.Ok).text()
        dialog.accept()

    QTimer.singleShot(20, complete_dialog)
    LocalizedMessageBox.warning(parent, "Fehler", "Der Vorgang ist fehlgeschlagen.")
    assert observed == {"title": "Erreur", "text": "L’opération a échoué.", "ok": "OK"}


def test_question_box_localizes_buttons_and_returns_the_selected_standard_button(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    translator.set_language("fr")
    parent = QWidget()
    parent._translator = translator
    observed = {}

    def choose_yes():
        dialog = next(widget for widget in QApplication.topLevelWidgets() if isinstance(widget, QMessageBox))
        observed["yes"] = dialog.button(QMessageBox.StandardButton.Yes).text()
        observed["no"] = dialog.button(QMessageBox.StandardButton.No).text()
        dialog.button(QMessageBox.StandardButton.Yes).click()

    QTimer.singleShot(20, choose_yes)
    result = LocalizedMessageBox.question(
        parent,
        "Question",
        "Continue?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    assert result == QMessageBox.StandardButton.Yes
    assert observed == {"yes": "Oui", "no": "Non"}


def test_settings_persistence_and_invalid_code_fallback(tmp_path):
    translator = write_test_catalog(tmp_path)
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    assert load_ui_language(settings) == "de"
    assert persist_ui_language(settings, translator, "ar") is True
    assert translator.get_language() == "ar"
    assert load_ui_language(settings) == "ar"
    settings.setValue(UI_LANGUAGE_KEY, "xx")
    settings.sync()
    assert load_ui_language(settings) == "de"
    assert persist_ui_language(settings, translator, "xx") is False
    assert translator.get_language() == "ar"


def test_main_window_language_selector_changes_locale_persists_and_sets_rtl(tmp_path, qapp):
    translator = write_test_catalog(tmp_path)
    settings = QSettings(str(tmp_path / "ui.ini"), QSettings.Format.IniFormat)
    window = MainWindow(
        settings=settings,
        translator=translator,
        project_manager=object(),
        start_background_tasks=False,
    )
    try:
        assert window._language_combo.count() == 11
        assert window._language_combo.currentData() == "de"
        assert window._language_label.text() == "Sprache:"

        french_index = window._language_combo.findData("fr")
        window._language_combo.setCurrentIndex(french_index)
        qapp.processEvents()
        assert translator.get_language() == "fr"
        assert settings.value(UI_LANGUAGE_KEY) == "fr"
        assert window._language_label.text() == "Langue :"
        assert window.workflow_panel.report_type_combo.currentData() == "analysis"
        assert window.workflow_panel.report_type_combo.currentText() == "Analyse"

        arabic_index = window._language_combo.findData("ar")
        window._language_combo.setCurrentIndex(arabic_index)
        qapp.processEvents()
        assert translator.get_language() == "ar"
        assert window.layoutDirection() == Qt.LayoutDirection.RightToLeft
        assert settings.value(UI_LANGUAGE_KEY) == "ar"
        assert window.workflow_panel.report_type_combo.currentData() == "analysis"
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_main_window_loads_saved_locale_without_project_language(tmp_path, qapp):
    settings = QSettings(str(tmp_path / "saved-locale.ini"), QSettings.Format.IniFormat)
    settings.setValue(UI_LANGUAGE_KEY, "ar")
    settings.sync()
    window = MainWindow(
        settings=settings,
        project_manager=object(),
        start_background_tasks=False,
    )
    try:
        assert window._translator.get_language() == "ar"
        assert window._language_combo.currentData() == "ar"
        assert window.layoutDirection() == Qt.LayoutDirection.RightToLeft
        assert window._language_label.text() == "اللغة:"
    finally:
        window.deleteLater()
        qapp.processEvents()
