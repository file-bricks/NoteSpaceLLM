"""
Tests für QThread-Worker in main_window.py.

Verifiziert:
- Worker-Klassen existieren und sind korrekt definiert
- Signals sind vorhanden
- Doppelstart-Schutz (kein zweiter Worker wenn einer läuft)
- ModelLoadWorker emittiert korrektes Ergebnis bei nicht erreichbarem Server
"""

import sys
import pytest
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path


# PySide6 prüfen
try:
    from PySide6.QtCore import QThread, Signal
    from PySide6.QtWidgets import QApplication
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

pytestmark = pytest.mark.skipif(not PYSIDE_AVAILABLE, reason="PySide6 nicht installiert")


@pytest.fixture(scope="session")
def qt_app():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


class TestWorkerClassDefinitions:
    """Worker-Klassen sind korrekt definiert und haben die erwarteten Signals."""

    def test_extraction_worker_has_signals(self):
        from src.gui.main_window import ExtractionWorker
        assert hasattr(ExtractionWorker, 'progress')
        assert hasattr(ExtractionWorker, 'doc_extracted')
        assert hasattr(ExtractionWorker, 'all_complete')

    def test_analysis_worker_has_signals(self):
        from src.gui.main_window import AnalysisWorker
        assert hasattr(AnalysisWorker, 'query_complete')
        assert hasattr(AnalysisWorker, 'all_complete')

    def test_index_worker_has_signals(self):
        from src.gui.main_window import IndexWorker
        assert hasattr(IndexWorker, 'progress')
        assert hasattr(IndexWorker, 'doc_indexed')
        assert hasattr(IndexWorker, 'all_complete')

    def test_model_load_worker_exists(self):
        from src.gui.main_window import ModelLoadWorker
        assert ModelLoadWorker is not None

    def test_model_load_worker_has_signal(self):
        from src.gui.main_window import ModelLoadWorker
        assert hasattr(ModelLoadWorker, 'models_loaded')

    def test_all_workers_are_qthread_subclasses(self):
        from src.gui.main_window import (
            ExtractionWorker, AnalysisWorker, IndexWorker, ModelLoadWorker
        )
        for cls in [ExtractionWorker, AnalysisWorker, IndexWorker, ModelLoadWorker]:
            assert issubclass(cls, QThread), f"{cls.__name__} ist kein QThread"


class TestModelLoadWorker:
    """ModelLoadWorker gibt korrektes Ergebnis bei nicht erreichbarem Ollama-Server."""

    def test_unreachable_server_emits_empty_list(self, qt_app):
        from src.gui.main_window import ModelLoadWorker

        received = []

        worker = ModelLoadWorker("http://127.0.0.1:19999", "")  # nicht erreichbar
        worker.models_loaded.connect(lambda models, msg: received.append((models, msg)))
        worker.start()
        worker.wait(8000)  # max 8s warten
        qt_app.processEvents()  # Qt-Signals aus Worker-Thread zustellen

        assert len(received) == 1, "models_loaded Signal wurde nicht emittiert"
        models, msg = received[0]
        assert models == [], f"Erwartet: [], erhalten: {models}"
        assert "erreichbar" in msg.lower() or "fehler" in msg.lower(), \
            f"Status-Meldung soll Fehler kommunizieren: '{msg}'"

    def test_provider_exception_does_not_reach_signal_or_log(self, monkeypatch, caplog):
        from src.gui.main_window import ModelLoadWorker
        from src.llm.ollama_client import OllamaClient

        secret = "model-worker-secret"
        userinfo = "user:pass@provider.example"

        def fail_availability(_client):
            raise ValueError(f"https://{userinfo}/api/tags Bearer {secret}")

        monkeypatch.setattr(OllamaClient, "_check_availability", fail_availability)
        worker = ModelLoadWorker(f"https://{userinfo}/api", secret)
        received = []
        worker.models_loaded.connect(lambda models, message: received.append((models, message)))

        with caplog.at_level("ERROR"):
            worker.run()

        assert len(received) == 1
        assert received[0][0] == []
        assert "ValueError" in received[0][1]
        assert secret not in received[0][1]
        assert userinfo not in received[0][1]
        assert secret not in caplog.text
        assert userinfo not in caplog.text


def test_llm_worker_sanitizes_provider_exception_before_ui_signal(monkeypatch, caplog):
    from src.gui.chat_panel import LLMWorker

    secret = "chat-worker-secret"
    userinfo = "user:pass@provider.example"

    class FailingClient:
        def stream_chat(self, *_args):
            raise RuntimeError(f"https://{userinfo}/chat Bearer {secret}")

    worker = LLMWorker(FailingClient(), "question", "")
    received = []
    worker.error_occurred.connect(received.append)

    with caplog.at_level("ERROR"):
        worker.run()

    assert len(received) == 1
    assert "RuntimeError" in received[0]
    assert secret not in received[0]
    assert userinfo not in received[0]
    assert secret not in caplog.text
    assert userinfo not in caplog.text

    def test_worker_is_not_gui_thread(self, qt_app):
        from src.gui.main_window import ModelLoadWorker

        worker = ModelLoadWorker("http://127.0.0.1:19999", "")
        worker.start()
        worker.wait(8000)
        qt_app.processEvents()

        assert not worker.isRunning(), "Worker soll nach wait() beendet sein"

    def test_double_start_prevention_pattern(self, qt_app):
        """Verifiziert dass das isRunning()-Guard in _refresh_models greift."""
        from src.gui.main_window import ModelLoadWorker

        worker1 = ModelLoadWorker("http://127.0.0.1:19999", "")
        worker1.start()
        assert worker1.isRunning()

        should_start = not worker1.isRunning()
        assert not should_start, "Doppelstart-Guard muss greifen wenn Worker läuft"

        worker1.wait(8000)
        qt_app.processEvents()


class TestExtractionWorker:
    """ExtractionWorker verarbeitet Dokumente korrekt im Hintergrund."""

    def test_empty_doc_list_emits_all_complete(self, qt_app):
        from src.gui.main_window import ExtractionWorker

        mock_extractor = MagicMock()
        complete_called = []

        worker = ExtractionWorker(mock_extractor, [])
        worker.all_complete.connect(lambda: complete_called.append(True))
        worker.start()
        worker.wait(3000)
        qt_app.processEvents()

        assert complete_called, "all_complete Signal bei leerer Liste nicht emittiert"

    def test_extraction_error_emits_error_signal(self, qt_app):
        from src.gui.main_window import ExtractionWorker

        mock_extractor = MagicMock()
        mock_extractor.extract.side_effect = RuntimeError("Test-Fehler")

        results = []
        worker = ExtractionWorker(mock_extractor, [("doc1", "/tmp/test.pdf", "test.pdf")])
        worker.doc_extracted.connect(lambda doc_id, text, err: results.append((doc_id, text, err)))
        worker.start()
        worker.wait(3000)
        qt_app.processEvents()

        assert len(results) == 1
        doc_id, text, err = results[0]
        assert doc_id == "doc1"
        assert text == ""
        assert "Test-Fehler" in err

    def test_extraction_success_emits_text(self, qt_app):
        from src.gui.main_window import ExtractionWorker

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.text = "Extrahierter Text"

        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = mock_result

        results = []
        worker = ExtractionWorker(mock_extractor, [("doc1", "/tmp/test.pdf", "test.pdf")])
        worker.doc_extracted.connect(lambda doc_id, text, err: results.append((doc_id, text, err)))
        worker.start()
        worker.wait(3000)
        qt_app.processEvents()

        assert len(results) == 1
        assert results[0] == ("doc1", "Extrahierter Text", "")


class TestAnalysisWorker:
    """AnalysisWorker führt LLM-Anfragen im Hintergrund aus."""

    def test_analysis_error_emits_error_signal(self, qt_app):
        from src.gui.main_window import AnalysisWorker

        mock_client = MagicMock()
        mock_client.chat.side_effect = ConnectionError("LLM nicht erreichbar")

        results = []
        worker = AnalysisWorker(mock_client, [("q1", "Testfrage?")])
        worker.query_complete.connect(lambda qid, resp, err: results.append((qid, resp, err)))
        worker.start()
        worker.wait(3000)
        qt_app.processEvents()

        assert len(results) == 1
        assert results[0][0] == "q1"
        assert results[0][1] == ""
        assert "ConnectionError" in results[0][2]
        assert "LLM nicht erreichbar" not in results[0][2]

    def test_analysis_success_emits_response(self, qt_app):
        from src.gui.main_window import AnalysisWorker

        mock_client = MagicMock()
        mock_client.chat.return_value = "Analyseergebnis"

        results = []
        complete = []
        worker = AnalysisWorker(mock_client, [("q1", "Frage")])
        worker.query_complete.connect(lambda qid, resp, err: results.append((qid, resp, err)))
        worker.all_complete.connect(lambda: complete.append(True))
        worker.start()
        worker.wait(3000)
        qt_app.processEvents()

        assert results[0] == ("q1", "Analyseergebnis", "")
        assert complete, "all_complete nicht emittiert"
