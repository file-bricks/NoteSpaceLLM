#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for TextExtractor and DocumentManager RAG metadata integration.
"""

import logging
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from src.core.document_manager import DocumentItem, DocumentManager, DocumentStatus
from src.core.text_extractor import ExtractionResult, TextExtractor


def _stub_external_langchain_clients(monkeypatch, request):
    """Stub provider/vector bindings; these tests never call them."""
    original_rag_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "src.rag" or name.startswith("src.rag.")
    }
    for name in original_rag_modules:
        del sys.modules[name]

    def restore_rag_modules():
        for name in tuple(sys.modules):
            if name == "src.rag" or name.startswith("src.rag."):
                del sys.modules[name]
        sys.modules.update(original_rag_modules)

    request.addfinalizer(restore_rag_modules)

    chroma_module = ModuleType("langchain_chroma")
    ollama_module = ModuleType("langchain_ollama")
    chromadb_module = ModuleType("chromadb")
    chromadb_module.__path__ = []
    chromadb_config_module = ModuleType("chromadb.config")

    class TestChromaSettings:
        def __init__(self, *, anonymized_telemetry=True):
            self.anonymized_telemetry = anonymized_telemetry

    chromadb_config_module.Settings = TestChromaSettings
    chromadb_module.config = chromadb_config_module

    class UnusedChroma:
        pass

    class UnusedOllamaClient:
        pass

    chroma_module.Chroma = UnusedChroma
    ollama_module.ChatOllama = UnusedOllamaClient
    ollama_module.OllamaEmbeddings = UnusedOllamaClient
    monkeypatch.setitem(sys.modules, "langchain_chroma", chroma_module)
    monkeypatch.setitem(sys.modules, "langchain_ollama", ollama_module)
    monkeypatch.setitem(sys.modules, "chromadb", chromadb_module)
    monkeypatch.setitem(sys.modules, "chromadb.config", chromadb_config_module)


def test_local_chroma_client_disables_anonymized_telemetry(monkeypatch, request, tmp_path):
    _stub_external_langchain_clients(monkeypatch, request)
    from src.rag import engine as engine_module

    captured = {}

    class FakeEmbeddingsManager:
        def __init__(self, **_kwargs):
            self.embeddings = object()

    class FakeChatClient:
        def __init__(self, **_kwargs):
            pass

    class FakeChroma:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(engine_module, "EmbeddingsManager", FakeEmbeddingsManager)
    monkeypatch.setattr(engine_module, "ChatOllama", FakeChatClient)
    monkeypatch.setattr(engine_module, "Chroma", FakeChroma)

    rag = engine_module.RAGEngine(persist_directory=str(tmp_path / "vector-store"))
    _ = rag.vectorstore

    assert captured["client_settings"].anonymized_telemetry is False


def test_installed_langchain_ollama_clients_apply_auth_headers_without_requests():
    """Exercise the real LangChain Ollama constructors without opening a connection."""
    from langchain_ollama import ChatOllama, OllamaEmbeddings

    marker = "notespace-test-only-sentinel"
    headers = {"Authorization": f"Bearer {marker}"}
    base_url = "http://127.0.0.1:1"
    clients = (
        ChatOllama(
            model="notespace-test-model",
            base_url=base_url,
            temperature=0.3,
            client_kwargs={"headers": headers},
        ),
        OllamaEmbeddings(
            model="notespace-test-embedding",
            base_url=base_url,
            client_kwargs={"headers": headers},
        ),
    )

    for client in clients:
        http_client = client._client._client
        try:
            assert str(http_client.base_url) == base_url
            assert http_client.headers.get("authorization") == f"Bearer {marker}"
        finally:
            http_client.close()


def test_rtf_extraction_umlauts_and_metadata_stripping(tmp_path):
    """Test RTF extraction correctly decodes German umlauts, unicode and strips metadata."""
    rtf_content = (
        r"{\rtf1\ansi\ansicpg1252\deff0\nouicompat\deflang1031{\fonttbl{\f0\fnil\fcharset0 Arial;}}" + "\n"
        r"{\colortbl ;\red0\green0\blue0;}" + "\n"
        r"{\*\generator Riched20 10.0.19041}\viewkind4\uc1 " + "\n"
        r"\pard\sa200\sl276\slmult1\f0\fs22\lang7 Dies ist ein Test f\'fcr deutsche Umlaute: \'e4, \'f6, \'fc, \'df, \'c4, \'d6, \'dc.\par" + "\n"
        r"Zweite Zeile mit \b fetter\b0  Schrift und Unicode: \u8364? 250.\par" + "\n"
        r"}"
    )

    rtf_file = tmp_path / "sample.rtf"
    rtf_file.write_bytes(rtf_content.encode("latin-1"))

    extractor = TextExtractor()
    result = extractor.extract(rtf_file)

    assert result.success is True
    assert "Riched20" not in result.text
    assert "fonttbl" not in result.text
    assert "Arial" not in result.text
    assert "Dies ist ein Test für deutsche Umlaute: ä, ö, ü, ß, Ä, Ö, Ü." in result.text
    assert "Zweite Zeile mit fetter Schrift und Unicode: € 250." in result.text
    assert result.word_count > 0


def test_html_to_text_helper():
    """Test HTML parsing and entity decoding in TextExtractor."""
    html_input = (
        "<html><head><title>Ignored Title</title><style>body { color: red; }</style></head>"
        "<body>"
        "<h1>Projekt &amp; Analyse</h1>"
        "<p>Absatz mit <b>fettem</b> Text und &Uuml;bersicht.</p>"
        "<div>Zweite Zeile mit &quot;Zitaten&quot; &lt;und&gt; Sonderzeichen.</div>"
        "<script>console.log('secret');</script>"
        "</body></html>"
    )

    text = TextExtractor._html_to_text(html_input)

    assert "Projekt & Analyse" in text
    assert "Absatz mit fettem Text und Übersicht." in text
    assert 'Zweite Zeile mit "Zitaten" <und> Sonderzeichen.' in text
    assert "secret" not in text
    assert "color: red" not in text


def test_eml_extraction_html_only(tmp_path):
    """Test EML extraction from multipart email that only contains HTML body."""
    eml_raw = (
        b"From: sender@example.com\r\n"
        b"To: receiver@example.com\r\n"
        b"Subject: Wichtige Mitteilung\r\n"
        b"Date: Mon, 14 Aug 2026 12:00:00 +0200\r\n"
        b"Content-Type: multipart/alternative; boundary=\"bound123\"\r\n\r\n"
        b"--bound123\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n\r\n"
        b"<html><body><p>Sehr geehrte Damen und Herren,<br>der Bericht ist <b>fertig</b>.</p></body></html>\r\n"
        b"--bound123--\r\n"
    )

    eml_file = tmp_path / "message.eml"
    eml_file.write_bytes(eml_raw)

    extractor = TextExtractor()
    result = extractor.extract(eml_file)

    assert result.success is True
    assert "From: sender@example.com" in result.text
    assert "Subject: Wichtige Mitteilung" in result.text
    assert "Sehr geehrte Damen und Herren" in result.text
    assert "der Bericht ist fertig." in result.text


def test_eml_extraction_plain_text(tmp_path):
    """Test EML extraction from plain text email."""
    eml_raw = (
        b"From: alice@example.com\r\n"
        b"To: bob@example.com\r\n"
        b"Subject: Treffen\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
        b"Hallo Bob, treffen wir uns morgen um 10 Uhr?"
    )

    eml_file = tmp_path / "plain.eml"
    eml_file.write_bytes(eml_raw)

    extractor = TextExtractor()
    result = extractor.extract(eml_file)

    assert result.success is True
    assert "From: alice@example.com" in result.text
    assert "Hallo Bob, treffen wir uns morgen um 10 Uhr?" in result.text


def test_document_manager_index_tags_serialization(tmp_path):
    """Test that DocumentManager passes serialized tags to RAGEngine.index_document."""
    mock_rag = MagicMock()
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.chunks_created = 3
    mock_rag.index_document.return_value = mock_result

    dm = DocumentManager(project_path=tmp_path, rag_engine=mock_rag)
    dm.set_auto_index(False)  # Explicit indexing test

    test_file = tmp_path / "test.txt"
    test_file.write_text("Inhalt des Dokuments für die RAG-Suche.", encoding="utf-8")

    doc = dm.add_file(test_file)
    assert doc is not None

    dm.add_tag(doc.id, "finanzen")
    dm.add_tag(doc.id, "analyse")
    dm.update_content(doc.id, "Inhalt des Dokuments für die RAG-Suche.")

    success = dm.index_document(doc.id)
    assert success is True

    # Verify RAGEngine was called with string tags metadata
    mock_rag.index_document.assert_called_once()
    kwargs = mock_rag.index_document.call_args.kwargs
    metadata = kwargs.get("metadata", {})

    assert isinstance(metadata.get("tags"), str)
    assert "finanzen" in metadata["tags"]
    assert "analyse" in metadata["tags"]


def test_authenticated_embedding_setup_error_never_logs_key_or_url(monkeypatch, request, caplog):
    _stub_external_langchain_clients(monkeypatch, request)
    from src.rag import embeddings as embeddings_module

    secret = "test-bearer-secret"
    userinfo = "user:pass@remote.example"
    calls = []

    class FailingEmbeddings:
        def __init__(self, **kwargs):
            calls.append(kwargs)
            raise ValueError(f"bad endpoint https://{userinfo}; Bearer {secret}")

    monkeypatch.setattr(embeddings_module, "OllamaEmbeddings", FailingEmbeddings)
    manager = embeddings_module.EmbeddingsManager(
        base_url=f"https://{userinfo}",
        headers={"Authorization": f"Bearer {secret}"},
    )

    with caplog.at_level(logging.WARNING), pytest.raises(RuntimeError) as raised:
        manager._create_embeddings()

    assert len(calls) == 1
    assert calls[0]["client_kwargs"]["headers"]["Authorization"] == f"Bearer {secret}"
    assert secret not in str(raised.value)
    assert userinfo not in str(raised.value)
    assert secret not in caplog.text
    assert userinfo not in caplog.text


def test_authenticated_rag_client_error_does_not_retry_without_headers(
    monkeypatch, request, tmp_path, caplog
):
    _stub_external_langchain_clients(monkeypatch, request)
    from src.rag import engine as engine_module

    secret = "test-bearer-secret"
    userinfo = "user:pass@remote.example"
    calls = []

    class FakeEmbeddingsManager:
        def __init__(self, **kwargs):
            self.model_name = kwargs["model_name"]
            self.embeddings = object()

    class FailingChatClient:
        def __init__(self, **kwargs):
            calls.append(kwargs)
            raise ValueError(f"bad endpoint https://{userinfo}; Bearer {secret}")

    monkeypatch.setattr(engine_module, "EmbeddingsManager", FakeEmbeddingsManager)
    monkeypatch.setattr(engine_module, "ChatOllama", FailingChatClient)

    with caplog.at_level(logging.WARNING), pytest.raises(RuntimeError) as raised:
        engine_module.RAGEngine(
            persist_directory=str(tmp_path / "vector-store"),
            ollama_base_url=f"https://{userinfo}",
            api_key=secret,
        )

    assert len(calls) == 1
    assert calls[0]["client_kwargs"]["headers"]["Authorization"] == f"Bearer {secret}"
    assert secret not in str(raised.value)
    assert userinfo not in str(raised.value)
    assert secret not in caplog.text
    assert userinfo not in caplog.text


def test_ollama_request_error_redacts_bearer_and_url_userinfo(monkeypatch):
    import urllib.error

    from src.llm import ollama_client as ollama_module

    secret = "test-bearer-secret"
    userinfo = "user:pass@remote.example"
    requests = []

    def fail_request(request, timeout):
        requests.append(request)
        assert timeout == 300
        raise urllib.error.URLError(f"https://{userinfo}/api/chat Bearer {secret}")

    monkeypatch.setattr(ollama_module.urllib.request, "urlopen", fail_request)
    client = ollama_module.OllamaClient(
        model="test-model",
        base_url=f"https://{userinfo}",
        api_key=secret,
    )
    client._is_available = True

    with pytest.raises(RuntimeError) as raised:
        client.chat("test prompt")

    assert len(requests) == 1
    assert requests[0].get_header("Authorization") == f"Bearer {secret}"
    assert secret not in str(raised.value)
    assert userinfo not in str(raised.value)


def test_rag_worker_emits_sanitized_provider_error(caplog):
    from src.gui import chat_panel

    if not chat_panel.PYSIDE_AVAILABLE:
        pytest.skip("PySide6 is not installed")

    secret = "test-bearer-secret"
    userinfo = "user:pass@remote.example"

    class FailingEngine:
        def query(self, **_kwargs):
            raise RuntimeError(f"https://{userinfo} Bearer {secret}")

    worker = chat_panel.RAGWorker(FailingEngine(), "question")
    errors = []
    worker.error_occurred.connect(errors.append)
    with caplog.at_level(logging.ERROR):
        worker.run()

    assert len(errors) == 1
    assert secret not in errors[0]
    assert userinfo not in errors[0]
    assert secret not in caplog.text
    assert userinfo not in caplog.text
