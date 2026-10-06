"""
Regressionstests für die Bugfix-Runde 2026-10.

Abgedeckt (Nummern = Befunde der Review):
 1  QThread-Lebensdauer, kein Ersetzen laufender Extraktion, closeEvent wartet
 2  HTML-Export: Escaping, Titel, nur sichere Link-Schemata, GUI nutzt Exporter
 3  update_content indexiert nicht synchron (Queue für IndexWorker)
 4  Chat-Panel: Dokument-Manager immer gesetzt, None-Engine wird weitergereicht
 5  RAG-Scores sind Relevanzen (höher = besser)
 6  Project.create übernimmt App-Konfiguration
 7  Projekt öffnen per ID, eindeutige Verzeichnisnamen
 8  Datei-Queue geht bei laufendem Worker nicht verloren
 9  Unterstützte Dateitypen aus einer Quelle (+ HTML-Extraktion)
10  TXT-Export entfernt nur Markdown-Syntax
11  Excel-Zellen 0/False bleiben erhalten
12  RTF \\uN-Fallback, Mehrbyte-Codepages, BOM-Erkennung
13  PPTX-Folien numerisch sortiert
14  Ollama-Verfügbarkeit wird erneut geprüft
15  Re-Index: erst einbetten, dann löschen; Fehlschlag setzt is_indexed=False
sowie Ressourcen-Freigabe, YAML-Front-Matter, pandoc, Chat-PlainText,
Translator und Workspace-ID.
"""

import json
import subprocess
import sys
import types
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.core.document_manager import DocumentManager
from src.core.text_extractor import SUPPORTED_EXTENSIONS, TextExtractor
from src.reports.exporter import ReportExporter

try:
    from PySide6.QtCore import QThread
    from PySide6.QtWidgets import QApplication

    PYSIDE_AVAILABLE = True
except ImportError:  # pragma: no cover - Umgebung ohne Qt
    PYSIDE_AVAILABLE = False

requires_qt = pytest.mark.skipif(not PYSIDE_AVAILABLE, reason="PySide6 nicht installiert")


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def qt_app():
    if not PYSIDE_AVAILABLE:
        pytest.skip("PySide6 nicht installiert")
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def _process_events_until(app, condition, timeout_s=5.0):
    import time

    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        app.processEvents()
        if condition():
            return True
        time.sleep(0.01)
    app.processEvents()
    return condition()


def _drain_events(app, duration_s=0.15):
    """Ausstehende QTimer (z.B. Chat-Scroll nach 50 ms) abarbeiten, bevor Widgets sterben."""
    import time

    deadline = time.monotonic() + duration_s
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)


@pytest.fixture
def main_window(qt_app, tmp_path):
    from src.gui.main_window import MainWindow

    with patch("pathlib.Path.home", return_value=tmp_path):
        with patch.object(MainWindow, "_init_rag_engine", lambda self: None):
            window = MainWindow()
        yield window
        window.close()
        _process_events_until(qt_app, lambda: not window._workers, timeout_s=5)
        _drain_events(qt_app)


if PYSIDE_AVAILABLE:

    class _SleepWorker(QThread):
        """Kleiner Test-Worker, der auf requestInterruption reagiert."""

        def __init__(self, duration_ms=200):
            super().__init__()
            self._duration_ms = duration_ms

        def run(self):
            waited = 0
            while waited < self._duration_ms and not self.isInterruptionRequested():
                self.msleep(10)
                waited += 10


class _FakeRagEngine:
    """Minimaler RAG-Engine-Ersatz für DocumentManager-Tests."""

    def __init__(self, success=True, present=None):
        self.calls = []
        self._success = success
        self._present = set(present or [])

    def index_document(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            success=self._success, chunks_created=2, error=None if self._success else "boom"
        )

    def get_indexed_document_ids(self, ids):
        return {i for i in ids if i in self._present}

    def get_statistics(self):
        return {"total_chunks": 0}


# --------------------------------------------------------------------------- #
# 1 / 8: Worker-Lebensdauer und Extraktions-Queue
# --------------------------------------------------------------------------- #


@requires_qt
def test_retain_until_finished_releases_only_after_thread_end(qt_app):
    from src.gui.worker_utils import retain_until_finished

    registry = {}
    finished = []
    worker = _SleepWorker(100)
    retain_until_finished(registry, worker, lambda w: finished.append(w.isRunning()))
    worker.start()

    assert len(registry) == 1
    assert _process_events_until(qt_app, lambda: not registry)
    # Callback läuft erst, wenn der Thread wirklich beendet ist
    assert finished == [False]


@requires_qt
def test_stop_workers_requests_interruption_and_waits(qt_app):
    from src.gui.worker_utils import stop_workers

    worker = _SleepWorker(10_000)
    worker.start()
    assert stop_workers([worker, None], timeout_ms=3000) is True
    assert not worker.isRunning()


@requires_qt
def test_tracked_worker_attr_cleared_on_finished_not_on_complete(main_window, qt_app):
    worker = _SleepWorker(50)
    main_window._start_tracked_worker("_analysis_worker", worker)
    assert main_window._analysis_worker is worker
    assert _process_events_until(qt_app, lambda: main_window._analysis_worker is None)
    assert _process_events_until(qt_app, lambda: not main_window._workers)


@requires_qt
def test_extract_all_text_does_not_replace_running_worker(main_window, tmp_path):
    from src.core.project import Project

    project = Project.create("Extraktion")
    sample = tmp_path / "a.txt"
    sample.write_text("Inhalt", encoding="utf-8")
    project.documents.add_file(sample)
    main_window._current_project = project

    running = MagicMock()
    running.isRunning.return_value = True
    main_window._extraction_worker = running

    called = []
    main_window._extract_all_text(on_complete=lambda: called.append(True))

    assert main_window._extraction_worker is running
    assert len(main_window._deferred_extraction_callbacks) == 1
    assert called == []
    main_window._extraction_worker = None


@requires_qt
def test_files_added_queue_survives_busy_worker(main_window, qt_app, tmp_path):
    from src.core.project import Project

    project = Project.create("Queue")
    main_window._current_project = project
    first = tmp_path / "eins.txt"
    second = tmp_path / "zwei.txt"
    first.write_text("Erster Text", encoding="utf-8")
    second.write_text("Zweiter Text", encoding="utf-8")

    running = MagicMock()
    running.isRunning.return_value = True
    main_window._extraction_worker = running

    project.documents.add_file(first)
    main_window._on_files_added()
    # Worker belegt -> nichts darf aus der Queue verloren gehen
    assert project.documents.has_pending_extractions()

    main_window._extraction_worker = None
    project.documents.add_file(second)
    main_window._on_files_added()
    assert _process_events_until(
        qt_app,
        lambda: all(d.extracted_text for d in project.documents.documents),
    )
    texts = sorted(d.extracted_text for d in project.documents.documents)
    assert texts == ["Erster Text", "Zweiter Text"]


@requires_qt
def test_close_event_waits_for_running_workers(main_window, qt_app):
    worker = _SleepWorker(10_000)
    main_window._start_tracked_worker("_analysis_worker", worker)
    assert worker.isRunning()

    main_window.close()

    assert not worker.isRunning()
    assert _process_events_until(qt_app, lambda: not main_window._workers)


# --------------------------------------------------------------------------- #
# 2: HTML-Export-Injection
# --------------------------------------------------------------------------- #


def test_markdown_to_html_escapes_raw_html_and_dangerous_links():
    md = (
        "# Titel <img src=x onerror=alert(1)>\n\n"
        "<script>alert('xss')</script>\n\n"
        "[böse](javascript:alert(1)) [tab](java\tscript:alert(1)) "
        "[gut](https://example.org/?a=1&b=2) [mail](mailto:a@b.de) [anker](#teil)"
    )
    out = ReportExporter.markdown_to_html(md)

    assert "<script>" not in out
    assert "&lt;script&gt;" in out
    assert "<img" not in out
    assert 'href="javascript' not in out
    assert 'href="java' not in out
    assert '<a href="https://example.org/?a=1&amp;b=2">gut</a>' in out
    assert '<a href="mailto:a@b.de">mail</a>' in out
    assert '<a href="#teil">anker</a>' in out


def test_html_document_title_is_escaped(tmp_path):
    exporter = ReportExporter(tmp_path)
    result = exporter._export_html("Text", "bericht", "</title><script>x()</script>")
    html = result.filepath.read_text(encoding="utf-8")
    assert "<script>x()</script>" not in html
    assert "&lt;/title&gt;&lt;script&gt;" in html


@requires_qt
def test_gui_html_export_uses_hardened_exporter():
    from src.gui.main_window import MainWindow

    fake_self = SimpleNamespace(_current_project=SimpleNamespace(name="A & <B>"))
    html = MainWindow._md_to_html(fake_self, "**fett** <script>alert(1)</script>")
    assert "<strong>fett</strong>" in html
    assert "<script>alert(1)</script>" not in html
    assert "<title>A &amp; &lt;B&gt;</title>" in html


# --------------------------------------------------------------------------- #
# 3 / 15: Indexierung
# --------------------------------------------------------------------------- #


def test_update_content_queues_instead_of_indexing_synchronously(tmp_path):
    engine = _FakeRagEngine()
    dm = DocumentManager(project_path=tmp_path, rag_engine=engine)
    sample = tmp_path / "doc.txt"
    sample.write_text("x", encoding="utf-8")
    doc = dm.add_file(sample)

    dm.update_content(doc.id, "Neuer Inhalt")

    assert engine.calls == []  # kein HTTP-Embedding im GUI-Thread
    assert dm.pop_pending_index() == [(doc.id, doc.name)]
    assert dm.pop_pending_index() == []


def test_update_content_with_changed_text_invalidates_index(tmp_path):
    dm = DocumentManager(project_path=tmp_path, rag_engine=_FakeRagEngine())
    sample = tmp_path / "doc.txt"
    sample.write_text("x", encoding="utf-8")
    doc = dm.add_file(sample)
    dm.update_content(doc.id, "Version 1")
    assert dm.index_document(doc.id) is True
    assert doc.is_indexed

    dm.update_content(doc.id, "Version 2")
    assert doc.is_indexed is False
    assert doc.chunk_count == 0


def test_failed_index_resets_is_indexed(tmp_path):
    dm = DocumentManager(project_path=tmp_path, rag_engine=_FakeRagEngine(success=False))
    sample = tmp_path / "doc.txt"
    sample.write_text("x", encoding="utf-8")
    doc = dm.add_file(sample)
    dm.set_auto_index(False)
    dm.update_content(doc.id, "Text")
    doc.is_indexed = True
    doc.chunk_count = 7

    assert dm.index_document(doc.id) is False
    assert doc.is_indexed is False
    assert doc.chunk_count == 0


def test_sync_index_flags_resets_documents_missing_from_index(tmp_path):
    dm = DocumentManager(project_path=tmp_path)
    paths = []
    for name in ("a.txt", "b.txt"):
        p = tmp_path / name
        p.write_text(name, encoding="utf-8")
        paths.append(p)
    doc_a = dm.add_file(paths[0])
    doc_b = dm.add_file(paths[1])
    for d in (doc_a, doc_b):
        d.is_indexed = True
        d.chunk_count = 3

    dm.set_rag_engine(_FakeRagEngine(present={doc_a.id}))
    dm.sync_index_flags()

    assert doc_a.is_indexed is True
    assert doc_b.is_indexed is False and doc_b.chunk_count == 0


# --------------------------------------------------------------------------- #
# RAG-Engine (mit langchain-Stubs, falls langchain fehlt)
# --------------------------------------------------------------------------- #


def _install_langchain_stubs(monkeypatch):
    def module(name, **attrs):
        mod = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(mod, key, value)
        monkeypatch.setitem(sys.modules, name, mod)
        return mod

    class _Doc:
        def __init__(self, page_content="", metadata=None):
            self.page_content = page_content
            self.metadata = metadata or {}

    module("langchain_core")
    module("langchain_core.documents", Document=_Doc)
    module("langchain_core.prompts", PromptTemplate=MagicMock())
    module("langchain_core.embeddings", Embeddings=object)
    module("langchain_chroma", Chroma=MagicMock())
    module("langchain_ollama", ChatOllama=MagicMock(), OllamaEmbeddings=MagicMock())
    module("langchain_text_splitters", RecursiveCharacterTextSplitter=MagicMock())


@pytest.fixture
def rag_engine_module(monkeypatch):
    rag_modules = ("src.rag", "src.rag.engine", "src.rag.embeddings", "src.rag.splitter")
    saved = {name: sys.modules.get(name) for name in rag_modules}
    try:
        import langchain_chroma  # noqa: F401
        import langchain_ollama  # noqa: F401
    except ImportError:
        _install_langchain_stubs(monkeypatch)
        for name in rag_modules:
            sys.modules.pop(name, None)

    import importlib

    module = importlib.import_module("src.rag.engine")
    yield module

    for name, mod in saved.items():
        if mod is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = mod


def _bare_engine(module, store):
    engine = module.RAGEngine.__new__(module.RAGEngine)
    engine._vectorstore = store
    return engine


def test_search_uses_relevance_scores_and_threshold(rag_engine_module):
    doc_hi, doc_lo = object(), object()
    store = MagicMock()
    store.similarity_search_with_relevance_scores.return_value = [(doc_hi, 0.9), (doc_lo, 0.2)]
    engine = _bare_engine(rag_engine_module, store)

    results = engine.search("frage", k=2, document_ids=["d1"], score_threshold=0.5)

    assert results == [(doc_hi, 0.9)]
    store.similarity_search_with_score.assert_not_called()
    kwargs = store.similarity_search_with_relevance_scores.call_args.kwargs
    assert kwargs["filter"] == {"document_id": {"$in": ["d1"]}}


def test_search_fallback_converts_distance_to_relevance(rag_engine_module):
    near, far = object(), object()
    store = MagicMock(spec=["similarity_search_with_score"])
    store.similarity_search_with_score.return_value = [(near, 0.0), (far, 3.0)]
    engine = _bare_engine(rag_engine_module, store)

    results = engine.search("frage", k=2)

    assert results[0] == (near, 1.0)
    assert results[1][1] == pytest.approx(0.25)
    # Nähere Treffer haben die höhere Relevanz
    assert results[0][1] > results[1][1]


def test_reindex_keeps_old_chunks_when_embedding_fails(rag_engine_module):
    store = MagicMock()
    engine = _bare_engine(rag_engine_module, store)
    chunk = SimpleNamespace(
        content="Chunk", metadata=SimpleNamespace(chunk_index=0, total_chunks=1)
    )
    engine.splitter = MagicMock()
    engine.splitter.split_text.return_value = [chunk]
    engine.embeddings_manager = MagicMock()
    engine.embeddings_manager.embeddings.embed_documents.side_effect = ConnectionError("down")

    result = engine.index_document("Text", "doc-1", "quelle.txt")

    assert result.success is False
    store._collection.delete.assert_not_called()
    store._collection.add.assert_not_called()


def test_reindex_replaces_chunks_after_successful_embedding(rag_engine_module):
    store = MagicMock()
    engine = _bare_engine(rag_engine_module, store)
    chunk = SimpleNamespace(
        content="Chunk", metadata=SimpleNamespace(chunk_index=0, total_chunks=1)
    )
    engine.splitter = MagicMock()
    engine.splitter.split_text.return_value = [chunk]
    engine.embeddings_manager = MagicMock()
    engine.embeddings_manager.embeddings.embed_documents.return_value = [[0.1, 0.2]]

    order = []
    store._collection.delete.side_effect = lambda **kw: order.append("delete")
    store._collection.add.side_effect = lambda **kw: order.append("add")

    result = engine.index_document("Text", "doc-1", "quelle.txt")

    assert result.success is True and result.chunks_created == 1
    assert order == ["delete", "add"]
    add_kwargs = store._collection.add.call_args.kwargs
    assert add_kwargs["embeddings"] == [[0.1, 0.2]]
    assert add_kwargs["metadatas"][0]["document_id"] == "doc-1"


# --------------------------------------------------------------------------- #
# 4: Chat-Panel / RAG-Verdrahtung
# --------------------------------------------------------------------------- #


@requires_qt
def test_connect_rag_engine_sets_document_manager_and_propagates_none(main_window):
    from src.core.project import Project

    project = Project.create("Chat")
    main_window._current_project = project

    engine = _FakeRagEngine()
    main_window._rag_engine = engine
    main_window._connect_rag_engine()
    assert main_window.chat_panel._document_manager is project.documents
    assert main_window.chat_panel._rag_engine is engine
    assert project.documents._rag_engine is engine

    # Engine abgeschaltet (z.B. Provider-Wechsel) -> keine veraltete Engine
    main_window._rag_engine = None
    main_window._connect_rag_engine()
    assert main_window.chat_panel._rag_engine is None
    assert project.documents._rag_engine is None
    assert main_window.chat_panel._document_manager is project.documents


@requires_qt
def test_chat_rag_query_without_document_manager_is_not_unfiltered(qt_app):
    from src.gui.chat_panel import ChatPanel

    panel = ChatPanel()
    panel._rag_engine = MagicMock()
    with patch("src.gui.chat_panel.RAGWorker") as worker_cls:
        panel._request_rag_response("Frage?")
    worker_cls.assert_not_called()
    assert panel._current_worker is None
    _drain_events(qt_app)


@requires_qt
def test_chat_message_widget_renders_plain_text_and_file_names(qt_app):
    from datetime import datetime, timezone

    from PySide6.QtCore import Qt

    from src.gui.chat_panel import ChatMessage, MessageWidget

    msg = ChatMessage(
        "assistant",
        "<b>nicht fett</b>",
        datetime.now(timezone.utc),
        sources=[{"source": "/tmp/ordner/bericht.pdf"}, {"source": None}],
    )
    widget = MessageWidget(msg)
    assert widget.content_label.textFormat() == Qt.TextFormat.PlainText
    from PySide6.QtWidgets import QLabel

    texts = [label.text() for label in widget.findChildren(QLabel)]
    assert any("bericht.pdf" in t and "/tmp/ordner" not in t for t in texts)


# --------------------------------------------------------------------------- #
# 6 / 7: Projekte
# --------------------------------------------------------------------------- #


def test_project_create_uses_saved_app_config(monkeypatch):
    from src.core import app_config
    from src.core.project import Project

    fake_cfg = SimpleNamespace(
        llm_provider="anthropic",
        llm_model="claude-test",
        ollama_base_url="http://remote:11434",
        ollama_api_key="geheim",
    )
    monkeypatch.setattr(app_config, "get_app_config", lambda: fake_cfg)

    project = Project.create("Konfig")

    assert project.settings.llm_provider == "anthropic"
    assert project.settings.llm_model == "claude-test"
    assert project.settings.ollama_base_url == "http://remote:11434"


def test_open_project_by_id_with_duplicate_names_and_unique_dirs(tmp_path):
    from src.core.project import ProjectManager

    pm = ProjectManager(tmp_path)
    first = pm.create_project("Doppelt", "Frage 1")
    second = pm.create_project("Doppelt", "Frage 2")

    dirs = [p for p in tmp_path.iterdir() if p.is_dir()]
    assert len(dirs) == 2  # gleiche Sekunde, trotzdem kein Überschreiben

    opened = pm.open_project(first.id)
    assert opened is not None and opened.id == first.id
    assert opened.main_question == "Frage 1"

    opened = pm.open_project(second.id)
    assert opened.id == second.id


@requires_qt
def test_project_choice_labels_are_unique_for_duplicate_names():
    from src.gui.main_window import MainWindow

    projects = [
        {"id": "aaaaaaaa-1", "name": "Doppelt", "modified_at": "2026-10-01T10:00:00"},
        {"id": "bbbbbbbb-2", "name": "Doppelt", "modified_at": "2026-10-02T10:00:00"},
        {"id": "cccccccc-3", "name": "Einzeln", "modified_at": "2026-10-03T10:00:00"},
    ]
    labels = MainWindow._project_choice_labels(projects)
    assert len(labels) == 3
    assert sorted(labels.values()) == ["aaaaaaaa-1", "bbbbbbbb-2", "cccccccc-3"]
    assert labels["Einzeln"] == "cccccccc-3"


# --------------------------------------------------------------------------- #
# 9: unterstützte Dateitypen
# --------------------------------------------------------------------------- #


def test_supported_extensions_single_source(tmp_path):
    assert DocumentManager.SUPPORTED_EXTENSIONS == SUPPORTED_EXTENSIONS
    dm = DocumentManager(project_path=tmp_path)
    for ext, expected in ((".pptx", True), (".html", True), (".htm", True),
                          (".odt", False), (".ods", False)):
        f = tmp_path / f"datei{ext}"
        f.write_bytes(b"x")
        assert (dm.add_file(f) is not None) is expected, ext


def test_html_files_are_converted_to_text(tmp_path):
    page = tmp_path / "seite.htm"
    page.write_text(
        "<html><head><title>T</title><style>p{}</style></head>"
        "<body><p>Grüße &amp; mehr</p><script>alert(1)</script></body></html>",
        encoding="utf-8",
    )
    result = TextExtractor().extract(page)
    assert result.success
    assert "Grüße & mehr" in result.text
    assert "<p>" not in result.text and "alert" not in result.text


# --------------------------------------------------------------------------- #
# 10: TXT-Export
# --------------------------------------------------------------------------- #


def test_plain_text_export_keeps_literal_characters():
    md = (
        "# Überschrift\n\n"
        "C# und Ticket #12 in file_name sowie **fett** und *kursiv*.\n\n"
        "* Punkt\n\n```python\nx = 1\n```\n[Link](https://example.org)"
    )
    plain = ReportExporter.markdown_to_plain_text(md)
    assert plain.startswith("Überschrift")
    assert "C# und Ticket #12 in file_name sowie fett und kursiv." in plain
    assert "- Punkt" in plain
    assert "```" not in plain and "x = 1" in plain
    assert "Link" in plain and "](" not in plain


# --------------------------------------------------------------------------- #
# 11-13: Extraktor
# --------------------------------------------------------------------------- #


def test_excel_keeps_zero_and_false(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["A", 0, False, None, 1.5])
    path = tmp_path / "tabelle.xlsx"
    wb.save(path)

    result = TextExtractor().extract(path)
    assert result.success
    assert "A | 0 | False |  | 1.5" in result.text


def test_rtf_unicode_fallback_and_hex_bytes():
    rtf = rb"{\rtf1\ansi\ansicpg1252 Gr\u252\'fc\'df \u8364? Ende}"
    assert TextExtractor._parse_rtf_bytes(rtf) == "Grüß € Ende"


def test_rtf_uc2_skips_two_hex_units():
    rtf = rb"{\rtf1\uc2 A\u8364\'80\'80B}"
    assert TextExtractor._parse_rtf_bytes(rtf) == "A€B"


def test_rtf_multibyte_codepage_bytes_are_buffered():
    # "あ" in cp932 = 0x82 0xA0 -- nur korrekt, wenn beide Bytes gemeinsam dekodiert werden
    rtf = rb"{\rtf1\ansi\ansicpg932 \'82\'a0 ok}"
    assert TextExtractor._parse_rtf_bytes(rtf) == "あ ok"


@pytest.mark.parametrize(
    "raw",
    [
        "Grüße".encode("utf-16"),  # BOM + UTF-16-LE
        b"\xfe\xff" + "Grüße".encode("utf-16-be"),
        b"\xef\xbb\xbf" + "Grüße".encode(),
        "Grüße".encode(),
        "Grüße".encode("cp1252"),
    ],
)
def test_plain_text_encoding_detection(tmp_path, raw):
    path = tmp_path / "text.txt"
    path.write_bytes(raw)
    result = TextExtractor().extract(path)
    assert result.success
    assert result.text == "Grüße"


def test_cp1252_specific_characters(tmp_path):
    path = tmp_path / "euro.txt"
    path.write_bytes("Preis: 5 € – „gut“".encode("cp1252"))
    assert TextExtractor().extract(path).text == "Preis: 5 € – „gut“"


def test_pptx_slides_sorted_numerically(tmp_path):
    ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    path = tmp_path / "folien.pptx"
    with zipfile.ZipFile(path, "w") as z:
        for number in (1, 2, 10):
            z.writestr(
                f"ppt/slides/slide{number}.xml",
                f'<p:sld xmlns:p="p" xmlns:a="{ns}"><a:t>Folie {number}</a:t></p:sld>',
            )
        z.writestr("ppt/slides/_rels/slide1.xml.rels", "<x/>")

    result = TextExtractor().extract(path)
    assert result.success
    order = [result.text.index(f"Folie {n}") for n in (1, 2, 10)]
    assert order == sorted(order)


def test_pdf_document_closed_on_error(tmp_path, monkeypatch):
    pytest.importorskip("fitz")
    import fitz

    fake_doc = MagicMock()
    fake_doc.__iter__.side_effect = RuntimeError("kaputt")
    monkeypatch.setattr(fitz, "open", lambda *a, **k: fake_doc)
    path = tmp_path / "x.pdf"
    path.write_bytes(b"%PDF")

    result = TextExtractor()._extract_pdf(path)
    assert result.success is False
    fake_doc.close.assert_called_once()


# --------------------------------------------------------------------------- #
# 14: Ollama-Verfügbarkeit
# --------------------------------------------------------------------------- #


def test_ollama_availability_is_rechecked(monkeypatch):
    from src.llm.ollama_client import OllamaClient

    checks = []

    def fake_check(self):
        checks.append(True)
        self._is_available = len(checks) >= 2  # erster Check scheitert
        self._last_check = 0.0

    monkeypatch.setattr(OllamaClient, "_check_availability", fake_check)
    monkeypatch.setattr(OllamaClient, "RECHECK_INTERVAL", 0.0)

    client = OllamaClient("modell", "http://127.0.0.1:9")
    assert checks == []  # kein Netzwerkzugriff im Konstruktor (GUI-Thread)

    assert client._ensure_available() is False
    assert client._ensure_available() is True
    assert len(checks) == 2


def test_ollama_unavailable_raises_connection_error(monkeypatch):
    from src.llm.ollama_client import OllamaClient

    def fake_check(self):
        self._is_available = False
        self._last_check = 0.0

    monkeypatch.setattr(OllamaClient, "_check_availability", fake_check)
    client = OllamaClient("modell", "http://127.0.0.1:9")
    with pytest.raises(ConnectionError):
        client.chat("Hallo")


# --------------------------------------------------------------------------- #
# Niedrige Schwere
# --------------------------------------------------------------------------- #


def test_markdown_front_matter_quotes_title(tmp_path):
    yaml = pytest.importorskip("yaml")
    exporter = ReportExporter(tmp_path)
    title = 'Bericht: "Q3" # final'
    result = exporter._export_markdown("Inhalt", "bericht", title, "Ä: B")
    text = result.filepath.read_text(encoding="utf-8")
    front = text.split("---\n")[1]
    data = yaml.safe_load(front)
    assert data["title"] == title
    assert data["author"] == "Ä: B"


@requires_qt
def test_gui_pdf_export_reports_missing_pandoc_and_cleans_temp(tmp_path):
    from src.gui.main_window import MainWindow

    seen = {}

    def fake_run(cmd, **kwargs):
        seen["md"] = Path(cmd[1])
        seen["timeout"] = kwargs.get("timeout")
        assert seen["md"].exists()
        raise FileNotFoundError("pandoc")

    with patch.object(subprocess, "run", fake_run), pytest.raises(RuntimeError, match="pandoc"):
        MainWindow._export_pdf(SimpleNamespace(), "# Text", tmp_path / "out.pdf")

    assert seen["timeout"]
    assert not seen["md"].exists()


def test_translator_whole_word_and_readonly_safe(tmp_path):
    from translator import TranslationSystem

    tr = TranslationSystem("de", tmp_path)
    assert tr._is_german("Start") is False
    assert tr._is_german("Export") is False
    assert tr._is_german("Jakarta") is False
    assert tr._is_german("Datei laden") is True

    # Schreibfehler beim Speichern dürfen t() nicht abbrechen
    tr.translations_file = tmp_path  # Verzeichnis -> OSError beim Schreiben
    assert tr.t("Fehler beim Öffnen") == "Fehler beim Öffnen"


def test_workspace_export_contains_project_id():
    from src.core.project import Project
    from src.core.workspace_exporter import build_workspace_export_payload

    project = Project.create("Workspace")
    payload = build_workspace_export_payload(project)
    assert payload["workspace"]["id"] == project.id
    json.dumps(payload)  # weiterhin serialisierbar
