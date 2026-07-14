import importlib.util
import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent


def _load_module(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _install_embedding_stubs(monkeypatch, fake_cls):
    ollama_mod = types.ModuleType("langchain_ollama")
    ollama_mod.OllamaEmbeddings = fake_cls

    embeddings_mod = types.ModuleType("langchain_core.embeddings")

    class Embeddings:
        pass

    embeddings_mod.Embeddings = Embeddings

    monkeypatch.setitem(sys.modules, "langchain_ollama", ollama_mod)
    monkeypatch.setitem(sys.modules, "langchain_core.embeddings", embeddings_mod)


def test_embeddings_manager_sets_http_timeout_and_headers(monkeypatch):
    calls = []

    class FakeOllamaEmbeddings:
        def __init__(self, **kwargs):
            calls.append(kwargs)

        def embed_query(self, text):
            return [1.0, 2.0]

    _install_embedding_stubs(monkeypatch, FakeOllamaEmbeddings)
    module = _load_module("notespace_embeddings_timeout_test", "src/rag/embeddings.py")

    manager = module.EmbeddingsManager(
        model_name="nomic-embed-text",
        base_url="http://ollama.local:11434",
        headers={"Authorization": "Bearer test"},
        request_timeout=42.0,
    )

    assert manager.embed_query("probe") == [1.0, 2.0]
    assert calls[0]["client_kwargs"]["headers"] == {"Authorization": "Bearer test"}
    assert calls[0]["client_kwargs"]["timeout"] == 42.0


def test_embed_query_rejects_empty_ollama_vector(monkeypatch):
    class FakeOllamaEmbeddings:
        def __init__(self, **kwargs):
            pass

        def embed_query(self, text):
            return []

    _install_embedding_stubs(monkeypatch, FakeOllamaEmbeddings)
    module = _load_module("notespace_embeddings_empty_query_test", "src/rag/embeddings.py")

    with pytest.raises(ValueError, match="leer"):
        module.EmbeddingsManager().embed_query("probe")


def test_embed_documents_rejects_wrong_count_and_empty_vectors(monkeypatch):
    class FakeOllamaEmbeddings:
        def __init__(self, **kwargs):
            pass

        def embed_documents(self, texts):
            return [[]]

    _install_embedding_stubs(monkeypatch, FakeOllamaEmbeddings)
    module = _load_module("notespace_embeddings_docs_test", "src/rag/embeddings.py")

    with pytest.raises(ValueError, match="1 Vektoren für 2 Texte"):
        module.EmbeddingsManager().embed_documents(["eins", "zwei"])

    with pytest.raises(ValueError, match="leer"):
        module.EmbeddingsManager().embed_documents(["eins"])


def _install_splitter_stubs(monkeypatch):
    splitters_mod = types.ModuleType("langchain_text_splitters")

    class RecursiveCharacterTextSplitter:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def split_text(self, text):
            return [text]

    splitters_mod.RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter

    docs_mod = types.ModuleType("langchain_core.documents")

    class Document:
        def __init__(self, page_content, metadata):
            self.page_content = page_content
            self.metadata = metadata

    docs_mod.Document = Document

    monkeypatch.setitem(sys.modules, "langchain_text_splitters", splitters_mod)
    monkeypatch.setitem(sys.modules, "langchain_core.documents", docs_mod)


def test_document_splitter_rejects_invalid_overlap(monkeypatch):
    _install_splitter_stubs(monkeypatch)
    module = _load_module("notespace_splitter_guard_test", "src/rag/splitter.py")

    with pytest.raises(ValueError, match="kleiner als chunk_size"):
        module.DocumentSplitter(chunk_size=100, chunk_overlap=100)

    splitter = module.DocumentSplitter(chunk_size=100, chunk_overlap=10)
    with pytest.raises(ValueError, match="kleiner als chunk_size"):
        splitter.update_config(chunk_size=20, chunk_overlap=20)

    assert splitter.get_config()["chunk_size"] == 100
    assert splitter.get_config()["chunk_overlap"] == 10


def test_rag_engine_uses_validating_embeddings_manager():
    engine_src = (ROOT / "src" / "rag" / "engine.py").read_text(encoding="utf-8")
    assert "embedding_function=self.embeddings_manager," in engine_src
    assert "embedding_function=self.embeddings_manager.embeddings" not in engine_src
