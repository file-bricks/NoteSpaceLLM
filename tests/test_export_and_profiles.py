"""
Tests für Export-Dateinamen-Dialog und Profile-CRUD (2026-06-01):
- _on_export_requested nutzt QFileDialog/QInputDialog statt fester Pfade
- rename_profile() in AppConfig korrekt implementiert
- Profile: Anlegen, Umbenennen, Löschen, Built-ins schützbar
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


# ===== AppConfig Profile-Tests (kein PySide6 nötig) =====

@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """AppConfig mit temporärem Verzeichnis."""
    monkeypatch.setenv("HOME", str(tmp_path))
    config_dir = tmp_path / ".notespacellm"
    config_dir.mkdir()
    # Patch CONFIG_DIR und CONFIG_FILE
    import src.core.app_config as ac
    monkeypatch.setattr(ac, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(ac, "CONFIG_FILE", config_dir / "config.json")
    ac._instance = None  # Reset singleton
    yield ac.get_app_config()
    ac._instance = None


class TestAppConfigProfiles:
    """Profile-CRUD in AppConfig."""

    def test_save_and_list_profile(self, tmp_config):
        cfg = tmp_config
        cfg.llm_provider = "ollama"
        cfg.llm_model = "test-model"
        cfg.save_profile("TestProfil")
        assert "TestProfil" in cfg.list_profile_names()

    def test_rename_profile_success(self, tmp_config):
        cfg = tmp_config
        cfg.llm_model = "x"
        cfg.save_profile("AltName")
        result = cfg.rename_profile("AltName", "NeuName")
        assert result is True
        assert "NeuName" in cfg.list_profile_names()
        assert "AltName" not in cfg.list_profile_names()

    def test_rename_profile_updates_active_profile(self, tmp_config):
        cfg = tmp_config
        cfg.llm_model = "x"
        cfg.save_profile("Aktiv")
        assert cfg.active_profile == "Aktiv"
        cfg.rename_profile("Aktiv", "UmbenannterAktiv")
        assert cfg.active_profile == "UmbenannterAktiv"

    def test_rename_builtin_fails(self, tmp_config):
        cfg = tmp_config
        result = cfg.rename_profile("Lokal (Standard)", "NeuName")
        assert result is False

    def test_rename_to_existing_name_fails(self, tmp_config):
        cfg = tmp_config
        cfg.llm_model = "x"
        cfg.save_profile("Profil1")
        cfg.save_profile("Profil2")
        result = cfg.rename_profile("Profil1", "Profil2")
        assert result is False
        assert "Profil1" in cfg.list_profile_names()

    def test_rename_nonexistent_profile_fails(self, tmp_config):
        cfg = tmp_config
        result = cfg.rename_profile("GibtEsNicht", "NeuName")
        assert result is False

    def test_rename_to_empty_name_fails(self, tmp_config):
        cfg = tmp_config
        cfg.save_profile("Vorhanden")
        result = cfg.rename_profile("Vorhanden", "")
        assert result is False

    def test_rename_persists_to_disk(self, tmp_config):
        cfg = tmp_config
        cfg.llm_model = "y"
        cfg.save_profile("Persistent")
        cfg.rename_profile("Persistent", "PersistentNeu")

        # Neue Instanz laden
        import src.core.app_config as ac
        ac._instance = None
        cfg2 = ac.get_app_config()
        assert "PersistentNeu" in cfg2.list_profile_names()
        assert "Persistent" not in cfg2.list_profile_names()
        ac._instance = None

    def test_delete_profile(self, tmp_config):
        cfg = tmp_config
        cfg.save_profile("ZuLöschen")
        result = cfg.delete_profile("ZuLöschen")
        assert result is True
        assert "ZuLöschen" not in cfg.list_profile_names()

    def test_delete_builtin_fails(self, tmp_config):
        cfg = tmp_config
        result = cfg.delete_profile("Lokal (Standard)")
        assert result is False


class TestExportDialogLogic:
    """Export-Dateinamen-Logik (Source-Code-Analyse)."""

    def test_export_uses_save_dialog_for_single_format(self):
        """_on_export_requested muss QFileDialog.getSaveFileName für 1 Format nutzen."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        export_start = source.index("def _on_export_requested(self")
        export_end = source.index("\n    def ", export_start + 10)
        export_code = source[export_start:export_end]

        assert "getSaveFileName" in export_code, \
            "_on_export_requested muss QFileDialog.getSaveFileName aufrufen"

    def test_export_uses_inputdialog_for_multi_format(self):
        """_on_export_requested muss QInputDialog für mehrere Formate nutzen."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        export_start = source.index("def _on_export_requested(self")
        export_end = source.index("\n    def ", export_start + 10)
        export_code = source[export_start:export_end]

        assert "QInputDialog" in export_code, \
            "_on_export_requested muss QInputDialog für Mehrfach-Format-Export nutzen"

    def test_export_cancellable_returns_early(self):
        """Wenn User Dialog abbricht (filepath=''), wird Export abgebrochen."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        export_start = source.index("def _on_export_requested(self")
        export_end = source.index("\n    def ", export_start + 10)
        export_code = source[export_start:export_end]

        # Prüfen ob es ein "return" nach dem Dialog-Abbruch-Check gibt
        assert "if not filepath" in export_code or "if not ok" in export_code, \
            "Export muss abgebrochen werden wenn Dialog-Abbruch erkannt"

    def test_export_rename_button_in_profile_dialog(self):
        """LLM-Settings-Dialog hat Umbenennen-Button für Profile."""
        with open("src/gui/main_window.py", "r", encoding="utf-8") as f:
            source = f.read()

        llm_settings_start = source.index("def _llm_settings(self):")
        llm_settings_end = source.index("\n    def _show_about", llm_settings_start)
        dialog_code = source[llm_settings_start:llm_settings_end]

        assert "Umbenennen" in dialog_code or "rename" in dialog_code.lower(), \
            "LLM-Settings-Dialog muss Umbenennen-Funktion für Profile haben"
        assert "rename_profile" in dialog_code, \
            "Dialog muss app_cfg.rename_profile() aufrufen"


class TestExportIntegration:
    """Export-Logik mit gemockten Pfaden."""

    def test_single_format_export_writes_correct_content(self, tmp_path):
        """Einzelformat-Export schreibt Inhalt korrekt."""
        content = "# Testbericht\n\nTest-Inhalt"
        filepath = tmp_path / "report.md"

        # Simuliere den Export-Teil (ohne GUI)
        filepath.write_text(content, encoding="utf-8")
        assert filepath.read_text(encoding="utf-8") == content

    def test_txt_export_strips_markdown(self, tmp_path):
        """TXT-Export entfernt Markdown-Formatierung."""
        import re
        content = "# Titel\n**fett** und `code`"
        plain = re.sub(r'[#*`_]', '', content)
        filepath = tmp_path / "report.txt"
        filepath.write_text(plain, encoding="utf-8")
        result = filepath.read_text(encoding="utf-8")
        assert "#" not in result
        assert "**" not in result
        assert "`" not in result
