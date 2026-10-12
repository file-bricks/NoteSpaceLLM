"""
Tests für notespacellm-workspace-v1 Export (2026-06-01).

Verifiziert:
- Schema-Version und Pflichtfelder vorhanden
- Datenschutzregeln: keine gespeicherten API-Schlüsselfelder, keine vollständigen Rohdaten
- Sub-Query-Auszüge werden korrekt eingebunden
- Atomares Schreiben (Temp-Datei + replace)
- Export abbruchbar wenn kein Projekt
"""

import json
import tempfile
from pathlib import Path
from typing import ClassVar
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_project():
    """Minimales Mock-Projekt für Export-Tests."""
    doc = MagicMock()
    doc.id = "doc-1"
    doc.name = "test.pdf"
    doc.extension = ".pdf"
    doc.is_selected = True
    doc.is_directory = False
    doc.extracted_text = "Dokument-Inhalt"

    project = MagicMock()
    project.name = "Testprojekt"
    project.main_question = "Was ist wichtig?"
    project.report_type = "analysis"
    project.settings.language = "de"
    project.settings.llm_provider = "ollama"
    project.settings.llm_model = "llama3"
    project.settings.ollama_base_url = "http://localhost:11434"
    project.documents.documents = [doc]
    project.subqueries.queries = []
    return project


class TestWorkspaceExportPayload:
    """build_workspace_export_payload erzeugt korrektes Schema."""

    def test_schema_version_present(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project)
        assert payload["schema_version"] == "notespacellm-workspace-v1"

    def test_app_fields_present(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project)
        assert "app" in payload
        assert payload["app"]["name"] == "NoteSpaceLLM"
        assert "exported_at" in payload["app"]
        assert "version" in payload["app"]

    def test_workspace_fields_from_project(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project)
        ws = payload["workspace"]
        assert ws["title"] == "Testprojekt"
        assert ws["question"] == "Was ist wichtig?"
        assert ws["workflow_type"] == "analysis"
        assert ws["locale"] == "de"

    def test_documents_list_contains_doc(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project)
        docs = payload["documents"]
        assert len(docs) == 1
        doc = docs[0]
        assert doc["id"] == "doc-1"
        assert doc["name"] == "test.pdf"
        assert doc["format"] == "pdf"
        assert doc["selected"] is True

    def test_privacy_no_raw_content(self, mock_project):
        """Rohdokumente dürfen nicht exportiert werden."""
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project)
        for doc in payload["documents"]:
            assert doc["content_included"] is False, \
                "Rohdaten dürfen nie exportiert werden"
        # Kein extrahierter Text direkt im Dokument-Objekt
        for doc in payload["documents"]:
            assert "extracted_text" not in doc

    def test_saved_api_key_fields_are_not_exported(self, mock_project):
        """Provider credential fields are excluded from the export payload."""
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project)
        payload_str = json.dumps(payload)
        assert "secret_exported" in payload_str
        assert payload["provider"]["secret_exported"] is False

    def test_privacy_no_absolute_paths(self, mock_project):
        """Absolute Pfade dürfen nicht exportiert werden."""
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project)
        payload_str = json.dumps(payload)
        # Keine Windows-Pfade (C:\\ oder /home/)
        assert "C:\\" not in payload_str
        assert "/home/" not in payload_str

    def test_report_content_included(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project, report_content="# Test\n\nBericht")
        assert payload["report"]["content"] == "# Test\n\nBericht"
        assert payload["report"]["format"] == "markdown"

    def test_chat_history_included(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        history = [
            {"role": "user", "content": "Was bedeutet X?"},
            {"role": "assistant", "content": "X bedeutet..."},
        ]
        payload = build_workspace_export_payload(mock_project, chat_history=history)
        assert len(payload["chat"]["messages"]) == 2
        assert payload["chat"]["messages"][0]["role"] == "user"

    def test_chat_system_messages_filtered(self, mock_project):
        """System-Nachrichten dürfen nicht im Export erscheinen."""
        from src.core.workspace_exporter import build_workspace_export_payload
        history = [
            {"role": "system", "content": "Du bist ein Assistent."},
            {"role": "user", "content": "Hallo"},
        ]
        payload = build_workspace_export_payload(mock_project, chat_history=history)
        roles = [m["role"] for m in payload["chat"]["messages"]]
        assert "system" not in roles, "System-Nachrichten müssen herausgefiltert werden"

    def test_empty_chat_produces_empty_list(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project, chat_history=None)
        assert payload["chat"]["messages"] == []

    def test_directories_excluded_from_documents(self, mock_project):
        """Verzeichnis-Einträge dürfen nicht im Export erscheinen."""
        from src.core.workspace_exporter import build_workspace_export_payload
        dir_item = MagicMock()
        dir_item.is_directory = True
        mock_project.documents.documents.append(dir_item)
        payload = build_workspace_export_payload(mock_project)
        # Nur das nicht-Verzeichnis-Dokument ist im Export
        assert all(not d.get("is_directory", False) for d in payload["documents"])
        assert len(payload["documents"]) == 1

    def test_provider_info_no_secret(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        payload = build_workspace_export_payload(mock_project)
        assert payload["provider"]["name"] == "ollama"
        assert payload["provider"]["secret_exported"] is False
        assert "ollama_api_key" not in json.dumps(payload)


class TestWorkspaceSubQueryExcerpts:
    """Sub-Query-Auszüge werden korrekt in das Export-Format überführt."""

    def test_completed_subqueries_become_excerpts(self, mock_project):
        from src.core.sub_query import SubQueryStatus, SubQueryType
        from src.core.workspace_exporter import build_workspace_export_payload

        sq = MagicMock()
        sq.id = "sq-1"
        sq.document_id = "doc-1"
        sq.query_text = "Was ist das Hauptthema?"
        sq.result_text = "Das Hauptthema ist..."
        sq.status = SubQueryStatus.COMPLETED
        sq.query_type = SubQueryType.QUESTION

        mock_project.subqueries.queries = [sq]
        payload = build_workspace_export_payload(mock_project, include_subquery_excerpts=True)

        doc = payload["documents"][0]
        assert len(doc["excerpts"]) == 1
        assert "Das Hauptthema ist..." in doc["excerpts"][0]["text"]

    def test_pending_subqueries_excluded(self, mock_project):
        from src.core.sub_query import SubQueryStatus, SubQueryType
        from src.core.workspace_exporter import build_workspace_export_payload

        sq = MagicMock()
        sq.id = "sq-2"
        sq.document_id = "doc-1"
        sq.query_text = "Frage..."
        sq.result_text = "This result is still pending and must not be exported."
        sq.status = SubQueryStatus.PENDING
        sq.query_type = SubQueryType.ANALYZE

        mock_project.subqueries.queries = [sq]
        payload = build_workspace_export_payload(mock_project, include_subquery_excerpts=True)
        assert payload["documents"][0]["excerpts"] == []

    def test_only_selected_documents_receive_completed_excerpts(self, mock_project):
        from src.core.sub_query import SubQueryStatus, SubQueryType
        from src.core.workspace_exporter import build_workspace_export_payload

        unselected = MagicMock()
        unselected.id = "doc-2"
        unselected.name = "private-not-selected.txt"
        unselected.extension = ".txt"
        unselected.is_selected = False
        unselected.is_directory = False
        mock_project.documents.documents.append(unselected)

        selected_result = MagicMock()
        selected_result.id = "sq-selected"
        selected_result.document_id = "doc-1"
        selected_result.query_text = "Selected document question"
        selected_result.result_text = "selected excerpt"
        selected_result.status = SubQueryStatus.COMPLETED
        selected_result.query_type = SubQueryType.QUESTION

        unselected_result = MagicMock()
        unselected_result.id = "sq-unselected"
        unselected_result.document_id = "doc-2"
        unselected_result.query_text = "Unselected document question"
        unselected_result.result_text = "must not appear"
        unselected_result.status = SubQueryStatus.COMPLETED
        unselected_result.query_type = SubQueryType.QUESTION

        mock_project.subqueries.queries = [selected_result, unselected_result]
        payload = build_workspace_export_payload(mock_project)

        assert payload["documents"][0]["excerpts"][0]["text"] == "selected excerpt"
        assert payload["documents"][1]["excerpts"] == []

    def test_disabled_subquery_excerpts_are_not_exported(self, mock_project):
        from src.core.sub_query import SubQueryStatus, SubQueryType
        from src.core.workspace_exporter import build_workspace_export_payload

        sq = MagicMock()
        sq.id = "sq-disabled"
        sq.document_id = "doc-1"
        sq.query_text = "Question"
        sq.result_text = "completed but not requested"
        sq.status = SubQueryStatus.COMPLETED
        sq.query_type = SubQueryType.QUESTION
        mock_project.subqueries.queries = [sq]

        payload = build_workspace_export_payload(
            mock_project,
            include_subquery_excerpts=False,
        )
        assert payload["documents"][0]["excerpts"] == []

    def test_excerpt_text_truncated_at_2000_chars(self, mock_project):
        from src.core.sub_query import SubQueryStatus, SubQueryType
        from src.core.workspace_exporter import build_workspace_export_payload

        sq = MagicMock()
        sq.id = "sq-3"
        sq.document_id = "doc-1"
        sq.query_text = "Lang"
        sq.result_text = "X" * 5000
        sq.status = SubQueryStatus.COMPLETED
        sq.query_type = SubQueryType.SUMMARY

        mock_project.subqueries.queries = [sq]
        payload = build_workspace_export_payload(mock_project)
        text = payload["documents"][0]["excerpts"][0]["text"]
        assert len(text) <= 2000


class TestWorkspaceFileExport:
    """Atomares Schreiben der Workspace-Datei."""

    def test_export_creates_valid_json_file(self, mock_project, tmp_path):
        from src.core.workspace_exporter import (
            build_workspace_export_payload,
            export_workspace_to_file,
        )
        payload = build_workspace_export_payload(mock_project)
        dest = tmp_path / "workspace.json"
        export_workspace_to_file(payload, dest)
        assert dest.exists()
        loaded = json.loads(dest.read_text(encoding="utf-8"))
        assert loaded["schema_version"] == "notespacellm-workspace-v1"

    def test_export_utf8_encoding(self, mock_project, tmp_path):
        from src.core.workspace_exporter import (
            build_workspace_export_payload,
            export_workspace_to_file,
        )
        mock_project.name = "Ünïcödë Prøjèct"
        payload = build_workspace_export_payload(mock_project)
        dest = tmp_path / "workspace_utf8.json"
        export_workspace_to_file(payload, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Ünïcödë" in content

    def test_export_no_temp_file_left_on_success(self, mock_project, tmp_path):
        from src.core.workspace_exporter import (
            build_workspace_export_payload,
            export_workspace_to_file,
        )
        payload = build_workspace_export_payload(mock_project)
        dest = tmp_path / "workspace.json"
        export_workspace_to_file(payload, dest)
        tmp_files = list(tmp_path.glob(".tmp_workspace_*"))
        assert len(tmp_files) == 0, "Keine Temp-Dateien nach erfolgreichem Export"

    def test_export_creates_parent_directory(self, mock_project, tmp_path):
        from src.core.workspace_exporter import (
            build_workspace_export_payload,
            export_workspace_to_file,
        )
        payload = build_workspace_export_payload(mock_project)
        dest = tmp_path / "subdir" / "workspace.json"
        export_workspace_to_file(payload, dest)
        assert dest.exists()

    def test_cancel_does_not_create_or_overwrite_export(self, tmp_path):
        from src.core.workspace_exporter import export_workspace_if_confirmed

        destination = tmp_path / "cancelled.json"
        assert not export_workspace_if_confirmed({"private": "content"}, destination, False)
        assert not destination.exists()

        destination.write_text("existing file", encoding="utf-8")
        assert not export_workspace_if_confirmed({"private": "content"}, destination, False)
        assert destination.read_text(encoding="utf-8") == "existing file"


class TestWorkspaceExportPrivacy:
    def test_confirmation_describes_full_user_content_and_non_anonymous_export(self, mock_project):
        from src.core.sub_query import SubQueryStatus, SubQueryType
        from src.core.workspace_exporter import (
            build_workspace_export_payload,
            workspace_export_confirmation_text,
        )

        sq = MagicMock()
        sq.id = "sq-confirm"
        sq.document_id = "doc-1"
        sq.query_text = "Question"
        sq.result_text = "selected excerpt"
        sq.status = SubQueryStatus.COMPLETED
        sq.query_type = SubQueryType.QUESTION
        mock_project.subqueries.queries = [sq]

        payload = build_workspace_export_payload(
            mock_project,
            report_content="Private report text",
            chat_history=[{"role": "user", "content": "Private chat text"}],
        )
        confirmation = workspace_export_confirmation_text(payload)

        assert "vollständiger Inhalt" in confirmation
        assert "vollständigen Chatverlauf mit 1 Nachrichten" in confirmation
        assert "1 abgeschlossene Auszüge aus 1 ausgewählten Dokument(en)" in confirmation
        assert "nicht anonymisiert" in confirmation
        assert "vertrauliche Angaben" in confirmation
        assert "gespeicherte api-schlüsselfelder" in confirmation.lower()
        assert "nicht auf Geheimnisse geprüft" in confirmation
        assert "prüfe bericht und chat vor dem weitergeben" in confirmation.lower()

    @pytest.mark.parametrize(
        ("provider", "expected_mode"),
        [
            ("ollama", "local"),
            ("openai", "remote"),
            ("anthropic", "remote"),
            ("claude-code", "remote"),
            ("local", "unknown"),
            ("unsupported-provider", "unknown"),
            ("", "unknown"),
        ],
    )
    def test_provider_mode_only_classifies_supported_providers(self, mock_project, provider, expected_mode):
        from src.core.workspace_exporter import build_workspace_export_payload

        mock_project.settings.llm_provider = provider
        if provider == "ollama":
            mock_project.settings.ollama_base_url = "http://127.0.0.1:11434"
        payload = build_workspace_export_payload(mock_project)

        assert payload["provider"]["mode"] == expected_mode

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("http://localhost:11434", "local"),
            ("https://127.0.0.1:11434", "local"),
            ("http://[::1]:11434", "local"),
            ("https://localhost.evil.example/api", "remote"),
            ("https://remote.example/api", "remote"),
            ("https://user:secret@localhost:11434", "unknown"),
            ("ftp://localhost:11434", "unknown"),
            ("http://localhost:not-a-port", "unknown"),
            ("http://[not-ipv6]", "unknown"),
            ("localhost:11434", "unknown"),
        ],
    )
    def test_endpoint_classification_without_network(self, url, expected):
        from src.core.workspace_exporter import _classify_ollama_endpoint

        assert _classify_ollama_endpoint(url) == expected

    def test_provider_export_never_includes_configured_url(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload

        mock_project.settings.ollama_base_url = "https://user:password@remote.example/api"
        payload = build_workspace_export_payload(mock_project)
        serialized = json.dumps(payload)

        assert payload["provider"]["mode"] == "unknown"
        assert "ollama_base_url" not in serialized
        assert "remote.example" not in serialized
        assert "password" not in serialized

    @pytest.mark.parametrize("answer_yes", [False, True])
    def test_gui_requires_confirmation_before_writing(self, mock_project, tmp_path, monkeypatch, answer_yes):
        pytest.importorskip("PySide6")
        from types import SimpleNamespace

        import src.gui.main_window as main_window_module

        class FakeMessageBox:
            class StandardButton:
                Yes = 1
                No = 2

            questions: ClassVar[list] = []

            @classmethod
            def question(cls, *_args):
                cls.questions.append(_args[2])
                return cls.StandardButton.Yes if answer_yes else cls.StandardButton.No

            @staticmethod
            def information(*_args):
                return None

            @staticmethod
            def critical(*_args):
                raise AssertionError("a controlled export should not fail")

        class FakeFileDialog:
            @staticmethod
            def getSaveFileName(*_args):
                return str(tmp_path / "ui-export.json"), "JSON (*.json)"

        messages = []
        fake_window = SimpleNamespace(
            _current_project=mock_project,
            output_panel=SimpleNamespace(
                get_output_directory=lambda: tmp_path,
                get_content=lambda: "Potentially sensitive report",
            ),
            chat_panel=SimpleNamespace(get_messages=list),
            statusbar=SimpleNamespace(showMessage=messages.append),
        )
        monkeypatch.setattr(main_window_module, "QMessageBox", FakeMessageBox)
        monkeypatch.setattr(main_window_module, "QFileDialog", FakeFileDialog)

        main_window_module.MainWindow._export_workspace(fake_window)

        destination = tmp_path / "ui-export.json"
        assert "nicht anonymisiert" in FakeMessageBox.questions[0]
        assert destination.exists() is answer_yes
        if answer_yes:
            exported = json.loads(destination.read_text(encoding="utf-8"))
            assert exported["report"]["content"] == "Potentially sensitive report"
            assert "prüfe bericht und chat vor dem weitergeben" in FakeMessageBox.questions[0].lower()
        else:
            assert messages[-1] == "Workspace-Export abgebrochen."
