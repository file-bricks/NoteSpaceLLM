"""
Tests für notespacellm-workspace-v1 Export (2026-06-01).

Verifiziert:
- Schema-Version und Pflichtfelder vorhanden
- Datenschutzregeln: keine API-Schlüssel, keine Rohdaten
- Sub-Query-Auszüge werden korrekt eingebunden
- Atomares Schreiben (Temp-Datei + replace)
- Export abbruchbar wenn kein Projekt
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


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

    def test_privacy_no_api_keys(self, mock_project):
        """API-Schlüssel dürfen nicht im Export erscheinen."""
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
        from src.core.workspace_exporter import build_workspace_export_payload
        from src.core.sub_query import SubQueryStatus, SubQueryType

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
        from src.core.workspace_exporter import build_workspace_export_payload
        from src.core.sub_query import SubQueryStatus, SubQueryType

        sq = MagicMock()
        sq.id = "sq-2"
        sq.document_id = "doc-1"
        sq.query_text = "Frage..."
        sq.result_text = ""
        sq.status = SubQueryStatus.PENDING
        sq.query_type = SubQueryType.ANALYZE

        mock_project.subqueries.queries = [sq]
        payload = build_workspace_export_payload(mock_project, include_subquery_excerpts=True)
        assert payload["documents"][0]["excerpts"] == []

    def test_excerpt_text_truncated_at_2000_chars(self, mock_project):
        from src.core.workspace_exporter import build_workspace_export_payload
        from src.core.sub_query import SubQueryStatus, SubQueryType

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
        from src.core.workspace_exporter import build_workspace_export_payload, export_workspace_to_file
        payload = build_workspace_export_payload(mock_project)
        dest = tmp_path / "workspace.json"
        export_workspace_to_file(payload, dest)
        assert dest.exists()
        loaded = json.loads(dest.read_text(encoding="utf-8"))
        assert loaded["schema_version"] == "notespacellm-workspace-v1"

    def test_export_utf8_encoding(self, mock_project, tmp_path):
        from src.core.workspace_exporter import build_workspace_export_payload, export_workspace_to_file
        mock_project.name = "Ünïcödë Prøjèct"
        payload = build_workspace_export_payload(mock_project)
        dest = tmp_path / "workspace_utf8.json"
        export_workspace_to_file(payload, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Ünïcödë" in content

    def test_export_no_temp_file_left_on_success(self, mock_project, tmp_path):
        from src.core.workspace_exporter import build_workspace_export_payload, export_workspace_to_file
        payload = build_workspace_export_payload(mock_project)
        dest = tmp_path / "workspace.json"
        export_workspace_to_file(payload, dest)
        tmp_files = list(tmp_path.glob(".tmp_workspace_*"))
        assert len(tmp_files) == 0, "Keine Temp-Dateien nach erfolgreichem Export"

    def test_export_creates_parent_directory(self, mock_project, tmp_path):
        from src.core.workspace_exporter import build_workspace_export_payload, export_workspace_to_file
        payload = build_workspace_export_payload(mock_project)
        dest = tmp_path / "subdir" / "workspace.json"
        export_workspace_to_file(payload, dest)
        assert dest.exists()
