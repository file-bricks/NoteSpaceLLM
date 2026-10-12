"""Keep tests away from user state, native keyrings, and network services."""

from __future__ import annotations

import os
import socket
import tempfile
import urllib.request
from pathlib import Path

import pytest

# Test modules import app_config during collection, so isolate its Path.home()
# default before those imports can capture the real user's profile path.
_COLLECTION_HOME = Path(tempfile.gettempdir()) / f"notespacellm-pytest-profile-{os.getpid()}"
os.environ["USERPROFILE"] = str(_COLLECTION_HOME)
os.environ["HOME"] = str(_COLLECTION_HOME)
os.environ["QT_QPA_PLATFORM"] = "offscreen"


class _TestCredentialStore:
    """Per-test fake store used by legacy tests that construct AppConfig directly."""

    def __init__(self):
        self.secrets: dict[str, str] = {}

    def get_secret(self, credential_id: str) -> str:
        from src.core.credential_store import CredentialNotFoundError

        try:
            return self.secrets[credential_id]
        except KeyError:
            raise CredentialNotFoundError("No test credential is stored.") from None

    def set_secret_verified(self, credential_id: str, secret: str) -> str:
        if credential_id in self.secrets:
            raise RuntimeError("Duplicate test credential ID.")
        self.secrets[credential_id] = secret
        if self.secrets.get(credential_id) != secret:
            raise RuntimeError("Test credential readback failed.")
        return "isolated test store"

    def delete_secret(self, credential_id: str) -> None:
        self.secrets.pop(credential_id, None)


@pytest.fixture(autouse=True)
def isolate_desktop_state(monkeypatch, tmp_path):
    """Use temporary config/home paths and block any accidental provider request."""
    from src.core import app_config

    isolated_home = tmp_path.parent / f"{tmp_path.name}-isolated-home"
    isolated_home.mkdir()
    config_dir = isolated_home / ".notespacellm"

    monkeypatch.setattr(Path, "home", lambda: isolated_home)
    monkeypatch.setattr(app_config, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(app_config, "CONFIG_FILE", config_dir / "config.json")
    monkeypatch.setattr(app_config, "CredentialStore", _TestCredentialStore)
    monkeypatch.setattr(app_config, "_instance", None)

    for name in (
        app_config.API_KEY_ENV_VAR,
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)

    def block_network(*_args, **_kwargs):
        raise OSError("Network access is disabled in the test suite.")

    monkeypatch.setattr(urllib.request, "urlopen", block_network)
    monkeypatch.setattr(socket.socket, "connect", block_network)
    monkeypatch.setattr(socket.socket, "connect_ex", block_network)
    monkeypatch.setattr(socket, "create_connection", block_network)

    try:
        import src.rag.engine as rag_engine
    except ImportError:
        # Unit tests may isolate provider/vector bindings when this host cannot
        # import the RAG stack. The unmocked installed-package import is checked
        # separately in tests/test_packaging.py and remains a required gate.
        pass
    else:
        isolated_vector_db = tmp_path / "vector-db"
        monkeypatch.setattr(rag_engine.RAGEngine, "DEFAULT_PERSIST_DIR", str(isolated_vector_db))
        defaults = rag_engine.RAGEngine.__init__.__defaults__
        if defaults:
            monkeypatch.setattr(
                rag_engine.RAGEngine.__init__,
                "__defaults__",
                (str(isolated_vector_db), *defaults[1:]),
            )

    yield
    app_config._instance = None
