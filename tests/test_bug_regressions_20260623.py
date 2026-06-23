# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 15/15).

Geprüfte echte Bugs (NoteSpaceLLM Desktop-Erst-Sweep):
  #1 core: nicht-atomare Schreibvorgänge (app_config/document_manager/project/sub_query)
     -> Datenverlust bei Crash/OneDrive-Lock mitten im Write (Config inkl. API-Key).
  #2 translator.t(): fehlender isinstance-Guard -> AttributeError bei korrupter JSON.
  #3 chat_panel RAGWorker: fehlende stop()-Methode -> AttributeError in stop_generation().
  #4 chat_panel _clear_history(): Streaming-Widget-Referenz nicht genullt -> RuntimeError
     (Zugriff auf gelöschtes C++-Objekt), wenn während Streaming gelöscht wird.
"""
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

try:
    from PySide6.QtWidgets import QApplication  # noqa: F401
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


# --- Bug #1: atomares Schreiben -------------------------------------------

def test_atomic_write_text_writes_and_no_tmp(tmp_path):
    from src.core._io import atomic_write_text

    target = tmp_path / "sub" / "config.json"
    atomic_write_text(target, '{"a": 1}')
    assert target.read_text(encoding="utf-8") == '{"a": 1}'
    # Keine .tmp-Reste.
    assert not (target.parent / (target.name + ".tmp")).exists()


def test_atomic_write_preserves_original_on_replace_failure(tmp_path, monkeypatch):
    from src.core import _io

    target = tmp_path / "config.json"
    target.write_text("ALT-INHALT", encoding="utf-8")

    # os.replace schlägt fehl (z.B. Lock) -> Originaldatei muss intakt bleiben.
    def boom(src, dst):
        raise OSError("replace failed")

    monkeypatch.setattr(_io.os, "replace", boom)
    with pytest.raises(OSError):
        _io.atomic_write_text(target, "NEU-INHALT-HALB")
    # Kritisch: Original unverändert (kein leeres/halbes File).
    assert target.read_text(encoding="utf-8") == "ALT-INHALT"


def test_document_manager_save_state_is_atomic_roundtrip(tmp_path):
    from src.core.document_manager import DocumentManager

    mgr = DocumentManager()
    fp = tmp_path / "documents.json"
    mgr.save_state(fp)
    assert fp.exists()
    # Gültiges JSON, keine .tmp-Reste.
    json.loads(fp.read_text(encoding="utf-8"))
    assert not (tmp_path / "documents.json.tmp").exists()


# --- Bug #2: translator isinstance-Guard ----------------------------------

def test_translator_corrupt_entry_no_crash(tmp_path):
    from translator import TranslationSystem

    ts = TranslationSystem(app_dir=tmp_path)
    # Korrupte Struktur: String statt {lang: text}-Dict.
    ts.translations["kaputt"] = "nur ein string"
    # Vor dem Fix: AttributeError ('str' object has no attribute 'get').
    assert ts.t("kaputt") == "kaputt"


# --- Bug #3: RAGWorker.stop() ---------------------------------------------

@pytest.mark.skipif(not PYSIDE_AVAILABLE, reason="PySide6 nicht verfügbar")
def test_ragworker_has_stop_and_no_crash():
    from PySide6.QtWidgets import QApplication
    from src.gui.chat_panel import RAGWorker
    from unittest.mock import MagicMock

    app = QApplication.instance() or QApplication([])  # noqa: F841
    worker = RAGWorker(MagicMock(), "frage", document_ids=None, k=5)
    assert hasattr(worker, "stop")
    # Vor dem Fix: AttributeError, da RAGWorker keine stop()-Methode hatte.
    worker.stop()
    assert worker._stop_requested is True


# --- Bug #4: _clear_history nullt Streaming-Widget ------------------------

def test_clear_history_nulls_streaming_widget_source():
    # ChatPanel headless zu konstruieren ist aufwändig (volle GUI-Abhängigkeiten);
    # daher Quelltext-Assertion, dass _clear_history die Streaming-Referenz nullt.
    src = (ROOT / "src" / "gui" / "chat_panel.py").read_text(encoding="utf-8")
    clear_idx = src.index("def _clear_history")
    next_def = src.index("\n    def ", clear_idx + 1)
    body = src[clear_idx:next_def]
    assert "self._streaming_widget = None" in body
