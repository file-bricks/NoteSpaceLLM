"""Runtime helpers for NoteSpaceLLM's desktop interface localization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QSettings, QTimer, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QTreeWidget,
)
import re
from string import Formatter

from translator import (
    DEFAULT_LANGUAGE,
    LANGUAGE_NAMES,
    SUPPORTED_LANGUAGES,
    TranslationSystem,
)


SETTINGS_ORGANIZATION = "BACH"
SETTINGS_APPLICATION = "NoteSpaceLLM"
UI_LANGUAGE_KEY = "ui_language"

_SOURCE_PROPERTY = "_notespacellm_i18n_source"
_NO_TRANSLATE_PROPERTY = "_notespacellm_i18n_skip"
_TRANSLATE_PROPERTY = "_notespacellm_i18n_translatable"
_COMBO_ITEMS_PROPERTY = "_notespacellm_i18n_combo_items"
_TAB_ITEMS_PROPERTY = "_notespacellm_i18n_tab_items"
_TREE_HEADERS_PROPERTY = "_notespacellm_i18n_tree_headers"


def make_ui_settings() -> QSettings:
    """Create the per-application preference store used only for the UI locale."""
    return QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)


def load_ui_language(settings: QSettings) -> str:
    language = settings.value(UI_LANGUAGE_KEY, DEFAULT_LANGUAGE, type=str)
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def create_translator(settings: QSettings, app_dir: Path | None = None) -> TranslationSystem:
    if app_dir is None:
        app_dir = Path(__file__).resolve().parents[2]
    return TranslationSystem(load_ui_language(settings), app_dir=app_dir)


def persist_ui_language(settings: QSettings, translator: TranslationSystem, language: str) -> bool:
    """Persist a valid UI locale; restore the old runtime state if QSettings fails."""
    if language not in SUPPORTED_LANGUAGES:
        return False
    previous = translator.get_language()
    try:
        settings.setValue(UI_LANGUAGE_KEY, language)
        settings.sync()
        if settings.status() != QSettings.Status.NoError:
            settings.setValue(UI_LANGUAGE_KEY, previous)
            settings.sync()
            return False
    except Exception:
        try:
            settings.setValue(UI_LANGUAGE_KEY, previous)
            settings.sync()
        except Exception:
            pass
        return False
    translator.set_language(language)
    return True


def tr(translator: TranslationSystem | None, source: str, **values: Any) -> str:
    """Translate source UI text and safely format its named placeholders."""
    translated = translator.t(source) if translator is not None else source
    if not values:
        return translated
    try:
        return translated.format(**values)
    except (KeyError, IndexError, TypeError, ValueError):
        # A stale or malformed translation must not break an interaction.
        try:
            return source.format(**values)
        except (KeyError, IndexError, TypeError, ValueError):
            return source


class _PreformattedValue:
    """Keep the already-rendered opaque portion of a dynamic UI message intact."""

    def __init__(self, value: str):
        self.value = value

    def __format__(self, _format_spec: str) -> str:
        return self.value


def find_translator(parent: QObject | None) -> TranslationSystem | None:
    current = parent
    while current is not None:
        translator = getattr(current, "_translator", None)
        if isinstance(translator, TranslationSystem):
            return translator
        current = current.parent() if callable(getattr(current, "parent", None)) else None
    return None


def translate_ui_text(text: str, translator: TranslationSystem | None) -> str:
    """Translate an exact UI source or a catalog template, preserving opaque values."""
    if translator is None or not isinstance(text, str):
        return text
    if translator.has_translation_source(text):
        return translator.t(text)

    # A few application-owned checkboxes append a protected format suffix to
    # a translatable label, e.g. "Word (.docx)". Translate only the label.
    suffix_label = re.fullmatch(r"(.*?)\s+(\(\.[A-Za-z0-9]+(?:\s+\.[A-Za-z0-9]+)*\))", text)
    if suffix_label and translator.has_translation_source(suffix_label.group(1)):
        return f"{translator.t(suffix_label.group(1))} {suffix_label.group(2)}"

    # Match only explicit catalog templates. Captured runtime values are copied
    # verbatim into the translated template; they are never translated.
    for source in translator.ui_translations:
        if "{" not in source or "}" not in source:
            continue
        try:
            parts = list(Formatter().parse(source))
        except ValueError:
            continue
        pattern = []
        names = []
        valid = True
        for literal, field_name, _format_spec, _conversion in parts:
            pattern.append(re.escape(literal))
            if field_name is None:
                continue
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", field_name):
                valid = False
                break
            names.append(field_name)
            pattern.append("(.*?)")
        if not valid or not names:
            continue
        match = re.fullmatch("".join(pattern), text, flags=re.DOTALL)
        if not match:
            continue
        values = {name: _PreformattedValue(value) for name, value in zip(names, match.groups())}
        return tr(translator, source, **values)
    return text


class TranslatableLabel(QLabel):
    """Opt-in label for static application chrome.

    Plain QLabel instances are treated as data by the widget-tree translator.
    This prevents a project/document/workflow value that happens to equal a UI
    source string from being rewritten during a live language change.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setProperty(_TRANSLATE_PROPERTY, True)


class LocalizedLabel(QLabel):
    """Label for app-owned status text that can replay its source template."""

    def __init__(self, source_text: str = "", translator: TranslationSystem | None = None, parent=None):
        self._translator = translator
        self._source_text = ""
        super().__init__(parent)
        self.setProperty(_TRANSLATE_PROPERTY, True)
        self.setText(source_text)

    def setText(self, text: str) -> None:
        self._source_text = text
        if self.property(_NO_TRANSLATE_PROPERTY):
            super().setText(text)
        else:
            super().setText(translate_ui_text(text, self._translator))

    def retranslate(self) -> None:
        if self.property(_NO_TRANSLATE_PROPERTY):
            super().setText(self._source_text)
        else:
            super().setText(translate_ui_text(self._source_text, self._translator))


class LocalizedStatusBar(QStatusBar):
    """Status bar that translates catalog-backed messages and can replay its source."""

    def __init__(self, translator: TranslationSystem, parent=None):
        self._translator = translator
        self._source_message = ""
        self._message_timeout = 0
        super().__init__(parent)
        self.messageChanged.connect(self._on_message_changed)

    def _on_message_changed(self, message: str) -> None:
        # QStatusBar clears timed messages itself. Mirror that expiration in
        # our replay state so a later language switch cannot resurrect it.
        if not message:
            self._source_message = ""
            self._message_timeout = 0

    def showMessage(self, message: str, timeout: int = 0) -> None:
        self._source_message = message
        self._message_timeout = timeout
        super().showMessage(translate_ui_text(message, self._translator), timeout)

    def retranslate(self) -> None:
        if self._source_message:
            super().showMessage(
                translate_ui_text(self._source_message, self._translator),
                self._message_timeout,
            )

    def clearMessage(self) -> None:
        self._source_message = ""
        super().clearMessage()


def mark_not_translatable(widget: QObject) -> None:
    """Keep user data and internal values out of the widget-tree translator."""
    widget.setProperty(_NO_TRANSLATE_PROPERTY, True)
    widget.setProperty(_TRANSLATE_PROPERTY, False)


def mark_combo_items_translatable(combo: QObject, source_values: list[str] | None = None) -> None:
    """Allow selected built-in combo labels to follow the current UI language."""
    if source_values is None:
        source_values = [combo.itemText(index) for index in range(combo.count())]
    combo.setProperty(_COMBO_ITEMS_PROPERTY, source_values)


def _source_for(widget: QObject, getter) -> str:
    source = widget.property(_SOURCE_PROPERTY)
    if isinstance(source, str):
        return source
    current = getter()
    if not isinstance(current, str) or not current:
        return ""
    widget.setProperty(_SOURCE_PROPERTY, current)
    return current


def _apply_text(widget: QObject, translator: TranslationSystem, getter, setter) -> None:
    source = _source_for(widget, getter)
    if source and translator.has_translation_source(source):
        setter(tr(translator, source))


def _apply_property(widget: QObject, translator: TranslationSystem, getter_name: str, setter_name: str) -> None:
    getter = getattr(widget, getter_name, None)
    setter = getattr(widget, setter_name, None)
    if callable(getter) and callable(setter):
        _apply_text(widget, translator, getter, setter)


def translate_widget_tree(root: QObject, translator: TranslationSystem) -> None:
    """Retranslate catalog-backed GUI chrome while leaving dynamic user data alone."""
    objects = [root, *root.findChildren(QObject)]
    for widget in objects:
        if widget.property(_NO_TRANSLATE_PROPERTY):
            continue
        if isinstance(widget, LocalizedLabel):
            # Its current status source is dynamic and authoritative. Do not
            # cache/replay the text currently rendered by an older locale.
            widget.retranslate()
        elif isinstance(widget, QLabel):
            if widget.property(_TRANSLATE_PROPERTY):
                _apply_property(widget, translator, "text", "setText")
        elif isinstance(widget, (QPushButton, QCheckBox, QRadioButton, QAction)):
            _apply_property(widget, translator, "text", "setText")
        if isinstance(widget, (QGroupBox, QMenu, QToolBar, QDialog, QMainWindow)):
            _apply_property(widget, translator, "title", "setTitle")
            _apply_property(widget, translator, "windowTitle", "setWindowTitle")
        if hasattr(widget, "toolTip") and hasattr(widget, "setToolTip"):
            _apply_property(widget, translator, "toolTip", "setToolTip")
        if hasattr(widget, "statusTip") and hasattr(widget, "setStatusTip"):
            _apply_property(widget, translator, "statusTip", "setStatusTip")
        if isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit)):
            _apply_property(widget, translator, "placeholderText", "setPlaceholderText")
        if isinstance(widget, QTabWidget):
            original = widget.property(_TAB_ITEMS_PROPERTY)
            if not isinstance(original, list):
                original = [widget.tabText(index) for index in range(widget.count())]
                widget.setProperty(_TAB_ITEMS_PROPERTY, original)
            for index, source in enumerate(original):
                if index < widget.count() and translator.has_translation_source(source):
                    widget.setTabText(index, tr(translator, source))
        if isinstance(widget, QTreeWidget):
            original = widget.property(_TREE_HEADERS_PROPERTY)
            if not isinstance(original, list):
                header = widget.headerItem()
                original = [header.text(index) for index in range(widget.columnCount())] if header else []
                widget.setProperty(_TREE_HEADERS_PROPERTY, original)
            if original:
                headers = [tr(translator, value) if translator.has_translation_source(value) else value for value in original]
                widget.setHeaderLabels(headers)
        if isinstance(widget, QComboBox):
            original = widget.property(_COMBO_ITEMS_PROPERTY)
            if isinstance(original, list):
                old_index = widget.currentIndex()
                previous_block = widget.blockSignals(True)
                try:
                    for index, source in enumerate(original):
                        if index < widget.count() and translator.has_translation_source(source):
                            widget.setItemText(index, tr(translator, source))
                    if old_index >= 0:
                        widget.setCurrentIndex(old_index)
                finally:
                    widget.blockSignals(previous_block)

        if isinstance(widget, QDialogButtonBox):
            translate_standard_buttons(widget, translator)


_STANDARD_BUTTON_SOURCES = {
    QDialogButtonBox.StandardButton.Ok: "OK",
    QDialogButtonBox.StandardButton.Cancel: "Abbrechen",
    QDialogButtonBox.StandardButton.Yes: "Ja",
    QDialogButtonBox.StandardButton.No: "Nein",
    QDialogButtonBox.StandardButton.Close: "Schließen",
}


def translate_standard_buttons(root: QObject, translator: TranslationSystem) -> None:
    """Translate Qt-owned standard button captions without touching button roles."""
    if isinstance(root, QMessageBox):
        for standard, source in _STANDARD_BUTTON_SOURCES.items():
            button = root.button(QMessageBox.StandardButton(standard.value))
            if button is not None and translator.has_translation_source(source):
                button.setProperty(_SOURCE_PROPERTY, source)
                button.setText(tr(translator, source))
    boxes = [root] if isinstance(root, QDialogButtonBox) else root.findChildren(QDialogButtonBox)
    for box in boxes:
        for standard, source in _STANDARD_BUTTON_SOURCES.items():
            button = box.button(standard)
            if button is not None and translator.has_translation_source(source):
                button.setProperty(_SOURCE_PROPERTY, source)
                button.setText(tr(translator, source))


def _translate_filter_entry(item: str, translator: TranslationSystem | None) -> str:
    match = re.fullmatch(r"(.*?)\s+(\(.*\))", item)
    if not match:
        return translate_ui_text(item, translator)
    label, patterns = match.groups()
    return f"{translate_ui_text(label, translator)} {patterns}"


def _translated_filters(filters: str, translator: TranslationSystem | None) -> list[str]:
    return [_translate_filter_entry(item, translator) for item in filters.split(";;")]


def _translate_input_dialog_buttons(dialog: QInputDialog, translator: TranslationSystem | None) -> None:
    """Set Qt's built-in input-dialog captions before it creates its buttons."""
    if translator is None:
        return
    cancel = translate_ui_text("Abbrechen", translator)
    ok = translate_ui_text("OK", translator)
    dialog.setCancelButtonText(cancel)
    dialog.setOkButtonText(ok)
    # Keep this pass for Qt styles that materialize the button box early.
    translate_standard_buttons(dialog, translator)
    QTimer.singleShot(0, lambda: translate_standard_buttons(dialog, translator))


class LocalizedInputDialog:
    """Drop-in static helpers that translate app copy and standard buttons."""

    @staticmethod
    def getText(parent, title, label, echo=QLineEdit.EchoMode.Normal, text="", flags=Qt.WindowType.Dialog,
                inputMethodHints=Qt.InputMethodHint.ImhNone):
        dialog = QInputDialog(parent, flags)
        translator = find_translator(parent)
        dialog.setWindowTitle(translate_ui_text(title, translator))
        dialog.setLabelText(translate_ui_text(label, translator))
        dialog.setTextEchoMode(echo)
        dialog.setTextValue(text)
        dialog.setInputMethodHints(inputMethodHints)
        if translator:
            _translate_input_dialog_buttons(dialog, translator)
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        return dialog.textValue(), accepted

    @staticmethod
    def getItem(parent, title, label, items, current=0, editable=True, flags=Qt.WindowType.Dialog,
                inputMethodHints=Qt.InputMethodHint.ImhNone):
        dialog = QInputDialog(parent, flags)
        translator = find_translator(parent)
        dialog.setWindowTitle(translate_ui_text(title, translator))
        dialog.setLabelText(translate_ui_text(label, translator))
        dialog.setComboBoxItems(items)
        dialog.setComboBoxEditable(editable)
        dialog.setTextValue(items[current] if 0 <= current < len(items) else "")
        dialog.setInputMethodHints(inputMethodHints)
        if translator:
            _translate_input_dialog_buttons(dialog, translator)
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        return dialog.textValue(), accepted


class LocalizedFileDialog:
    """Static QFileDialog-compatible calls; filters keep their file patterns verbatim."""

    @staticmethod
    def getOpenFileNames(parent=None, caption="", directory="", filter="", selectedFilter="", options=QFileDialog.Option(0)):
        translator = find_translator(parent)
        dialog = QFileDialog(parent)
        dialog.setWindowTitle(translate_ui_text(caption, translator))
        if directory:
            dialog.setDirectory(directory)
        translated_filters = _translated_filters(filter, translator)
        if translated_filters:
            dialog.setNameFilters(translated_filters)
            if selectedFilter:
                dialog.selectNameFilter(_translate_filter_entry(selectedFilter, translator))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setOptions(options)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selectedFiles(), dialog.selectedNameFilter()
        return [], dialog.selectedNameFilter()

    @staticmethod
    def getSaveFileName(parent=None, caption="", directory="", filter="", selectedFilter="", options=QFileDialog.Option(0)):
        translator = find_translator(parent)
        dialog = QFileDialog(parent)
        dialog.setWindowTitle(translate_ui_text(caption, translator))
        if directory:
            dialog.setDirectory(directory)
        translated_filters = _translated_filters(filter, translator)
        if translated_filters:
            dialog.setNameFilters(translated_filters)
            if selectedFilter:
                dialog.selectNameFilter(_translate_filter_entry(selectedFilter, translator))
        preferred_filter = selectedFilter or (filter.split(";;", maxsplit=1)[0] if filter else "")
        suffix_match = re.search(r"\*\.([A-Za-z0-9]+)", preferred_filter)
        if suffix_match:
            dialog.setDefaultSuffix(suffix_match.group(1))
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setOptions(options)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selectedFiles()[0], dialog.selectedNameFilter()
        return "", dialog.selectedNameFilter()

    @staticmethod
    def getExistingDirectory(parent=None, caption="", directory="", options=QFileDialog.Option.ShowDirsOnly):
        translator = find_translator(parent)
        dialog = QFileDialog(parent)
        dialog.setWindowTitle(translate_ui_text(caption, translator))
        if directory:
            dialog.setDirectory(directory)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setOptions(options)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.selectedFiles()
            return selected[0] if selected else ""
        return ""


class LocalizedMessageBox:
    """QMessageBox static-call facade with app-locale text and button captions."""

    StandardButton = QMessageBox.StandardButton
    Icon = QMessageBox.Icon

    _ICONS = {
        "information": QMessageBox.Icon.Information,
        "about": QMessageBox.Icon.Information,
        "warning": QMessageBox.Icon.Warning,
        "critical": QMessageBox.Icon.Critical,
        "question": QMessageBox.Icon.Question,
    }

    @classmethod
    def _show(cls, kind, parent, title, text, buttons=None, default_button=QMessageBox.StandardButton.NoButton):
        translator = find_translator(parent)
        box = QMessageBox(parent)
        box.setIcon(cls._ICONS[kind])
        box.setWindowTitle(translate_ui_text(title, translator))
        box.setText(translate_ui_text(text, translator))
        if buttons is None:
            if kind == "question":
                buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            else:
                buttons = QMessageBox.StandardButton.Ok
        box.setStandardButtons(buttons)
        if default_button != QMessageBox.StandardButton.NoButton:
            box.setDefaultButton(default_button)
        if translator:
            translate_standard_buttons(box, translator)
        return box.exec()

    @classmethod
    def information(cls, parent, title, text, buttons=QMessageBox.StandardButton.Ok,
                    defaultButton=QMessageBox.StandardButton.NoButton):
        return cls._show("information", parent, title, text, buttons, defaultButton)

    @classmethod
    def warning(cls, parent, title, text, buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.NoButton):
        return cls._show("warning", parent, title, text, buttons, defaultButton)

    @classmethod
    def critical(cls, parent, title, text, buttons=QMessageBox.StandardButton.Ok,
                 defaultButton=QMessageBox.StandardButton.NoButton):
        return cls._show("critical", parent, title, text, buttons, defaultButton)

    @classmethod
    def question(cls, parent, title, text,
                 buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                 defaultButton=QMessageBox.StandardButton.NoButton):
        return cls._show("question", parent, title, text, buttons, defaultButton)

    @classmethod
    def about(cls, parent, title, text):
        return cls._show("about", parent, title, text, QMessageBox.StandardButton.Ok)


def set_translated_text(widget: QObject, source: str, translator: TranslationSystem) -> None:
    """Set and retain the source string for a later locale change."""
    widget.setProperty(_SOURCE_PROPERTY, source)
    widget.setProperty(_TRANSLATE_PROPERTY, True)
    widget.setText(tr(translator, source))


__all__ = [
    "LANGUAGE_NAMES",
    "SETTINGS_APPLICATION",
    "SETTINGS_ORGANIZATION",
    "SUPPORTED_LANGUAGES",
    "UI_LANGUAGE_KEY",
    "create_translator",
    "find_translator",
    "load_ui_language",
    "make_ui_settings",
    "mark_combo_items_translatable",
    "mark_not_translatable",
    "LocalizedFileDialog",
    "LocalizedInputDialog",
    "LocalizedLabel",
    "LocalizedMessageBox",
    "LocalizedStatusBar",
    "TranslatableLabel",
    "persist_ui_language",
    "set_translated_text",
    "tr",
    "translate_ui_text",
    "translate_standard_buttons",
    "translate_widget_tree",
]
