#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Client - Local LLM via Ollama
====================================

Connects to a local Ollama instance for LLM inference.
"""

import json
import time
from typing import Iterator, Optional
import urllib.request
import urllib.error

from .client import LLMClient


class OllamaClient(LLMClient):
    """
    Client for Ollama local LLM server.

    Requires Ollama to be running locally (default: http://localhost:11434)
    """

    DEFAULT_URL = "http://localhost:11434"
    # Nach einer fehlgeschlagenen Prüfung frühestens nach so vielen Sekunden erneut prüfen
    RECHECK_INTERVAL = 5.0

    def __init__(self, model: str = "llama3", base_url: str = DEFAULT_URL,
                 api_key: str = ""):
        """
        Initialize the Ollama client.

        Args:
            model: The model to use (must be pulled in Ollama)
            base_url: Ollama server URL
            api_key: Optional API key for authenticated proxy
        """
        super().__init__(model)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        # Erreichbarkeit wird lazy beim ersten Aufruf geprüft (im Worker-Thread,
        # nicht im GUI-Thread) und nach Fehlschlägen erneut geprüft.
        self._last_check: Optional[float] = None

    def _auth_headers(self) -> dict:
        """Build request headers including auth if configured."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _check_availability(self):
        """Check if Ollama is available."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags",
                                        headers=self._auth_headers())
            with urllib.request.urlopen(req, timeout=5) as response:
                self._is_available = response.status == 200
        except Exception:
            self._is_available = False
        self._last_check = time.monotonic()

    def _ensure_available(self) -> bool:
        """Prüft die Erreichbarkeit erneut, solange der Server als nicht erreichbar gilt.

        Ein einmal fehlgeschlagener Check wird NICHT dauerhaft gecacht: wird
        Ollama nach dem App-Start gestartet, funktioniert der nächste Aufruf.
        """
        if self._is_available:
            return True
        last = getattr(self, "_last_check", None)
        if last is None or time.monotonic() - last >= self.RECHECK_INTERVAL:
            self._check_availability()
        return self._is_available

    def _mark_unavailable_on(self, exc: Exception) -> None:
        """Verbindungsfehler bei echten Requests als 'nicht erreichbar' merken."""
        if isinstance(exc, (urllib.error.URLError, ConnectionError, TimeoutError)) and not (
            isinstance(exc, urllib.error.HTTPError)
        ):
            self._is_available = False
            self._last_check = time.monotonic()

    def chat(self, prompt: str, context: str = "") -> str:
        """Send a chat message and get a response."""
        if not self._ensure_available():
            raise ConnectionError("Ollama is not available")

        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(data).encode("utf-8"),
            headers=self._auth_headers()
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("message", {}).get("content", "")
        except Exception as e:
            self._mark_unavailable_on(e)
            raise

    def stream_chat(self, prompt: str, context: str = "") -> Iterator[str]:
        """Stream a chat response."""
        if not self._ensure_available():
            raise ConnectionError("Ollama is not available")

        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(data).encode("utf-8"),
            headers=self._auth_headers()
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                for line in response:
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            self._mark_unavailable_on(e)
            raise

    def get_models(self) -> list:
        """Get available models from Ollama."""
        if not self._ensure_available():
            return []

        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags",
                                        headers=self._auth_headers())
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama registry.

        Args:
            model: Model name to pull

        Returns:
            True if successful
        """
        try:
            data = {"name": model}
            req = urllib.request.Request(
                f"{self.base_url}/api/pull",
                data=json.dumps(data).encode("utf-8"),
                headers=self._auth_headers()
            )

            with urllib.request.urlopen(req, timeout=600) as response:
                # Stream response until complete
                for line in response:
                    pass
                return True

        except Exception:
            return False

    def generate(self, prompt: str, system: str = "") -> str:
        """
        Simple text generation (non-chat mode).

        Args:
            prompt: The prompt text
            system: Optional system prompt

        Returns:
            Generated text
        """
        if not self._ensure_available():
            raise ConnectionError("Ollama is not available")

        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        if system:
            data["system"] = system

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(data).encode("utf-8"),
            headers=self._auth_headers()
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "")
        except Exception as e:
            self._mark_unavailable_on(e)
            raise
