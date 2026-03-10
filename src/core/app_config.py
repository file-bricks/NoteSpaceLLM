#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Config - Local application-level settings for NoteSpaceLLM
===============================================================

Stores global LLM defaults (provider, model, URL, API key) in a local
config file (~/.notespacellm/config.json). API keys are stored here
instead of in project files to prevent accidental sharing.
"""

import json
from pathlib import Path
from typing import Optional


# Config lives outside OneDrive/synced folders
CONFIG_DIR = Path.home() / ".notespacellm"
CONFIG_FILE = CONFIG_DIR / "config.json"


class AppConfig:
    """Persistent app-level configuration stored locally."""

    DEFAULTS = {
        "llm_provider": "ollama",
        "llm_model": "llama3",
        "ollama_base_url": "http://localhost:11434",
        "ollama_api_key": "",
    }

    def __init__(self):
        self._data: dict = dict(self.DEFAULTS)
        self._load()

    def _load(self):
        """Load config from disk."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                # Merge with defaults (new keys get default values)
                for key, default in self.DEFAULTS.items():
                    self._data[key] = stored.get(key, default)
            except Exception:
                pass  # Keep defaults on error

    def save(self):
        """Write config to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # --- Properties ---

    @property
    def llm_provider(self) -> str:
        return self._data["llm_provider"]

    @llm_provider.setter
    def llm_provider(self, value: str):
        self._data["llm_provider"] = value

    @property
    def llm_model(self) -> str:
        return self._data["llm_model"]

    @llm_model.setter
    def llm_model(self, value: str):
        self._data["llm_model"] = value

    @property
    def ollama_base_url(self) -> str:
        return self._data["ollama_base_url"]

    @ollama_base_url.setter
    def ollama_base_url(self, value: str):
        self._data["ollama_base_url"] = value

    @property
    def ollama_api_key(self) -> str:
        return self._data["ollama_api_key"]

    @ollama_api_key.setter
    def ollama_api_key(self, value: str):
        self._data["ollama_api_key"] = value


# Singleton instance
_instance: Optional[AppConfig] = None


def get_app_config() -> AppConfig:
    """Get the global app config (singleton)."""
    global _instance
    if _instance is None:
        _instance = AppConfig()
    return _instance
