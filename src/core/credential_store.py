"""Access NoteSpaceLLM credentials through an allowlisted native keyring."""

from __future__ import annotations

import importlib
import sys
import threading
from collections.abc import Callable
from typing import ClassVar

SERVICE_NAME = "NoteSpaceLLM"


class CredentialStoreError(RuntimeError):
    """A native credential store could not safely read or write a secret."""


class CredentialNotFoundError(CredentialStoreError):
    """A config entry points at a credential that is missing from the keyring."""


class CredentialConflictError(CredentialStoreError):
    """A generated credential ID already exists and will not be overwritten."""


class CredentialStore:
    """Lazy, fail-closed wrapper around the OS keyring implementations.

    The library's configurable backend loader is intentionally not used: it can
    load third-party or plaintext backends from user configuration. Only the
    backend classes listed for the current operating system are instantiated.
    Constructing this object performs no keyring access.
    """

    _BACKENDS: ClassVar[dict[str, tuple[tuple[str, str, str], ...]]] = {
        "win32": (
            ("keyring.backends.Windows", "WinVaultKeyring", "Windows Credential Locker"),
        ),
        "darwin": (
            ("keyring.backends.macOS", "Keyring", "macOS Keychain"),
        ),
        "linux": (
            ("keyring.backends.SecretService", "Keyring", "Freedesktop Secret Service"),
            ("keyring.backends.kwallet", "DBusKeyring", "KDE KWallet"),
        ),
    }

    def __init__(
        self,
        platform: str | None = None,
        backend_factories: dict[str, tuple[Callable[[], object], ...]] | None = None,
    ):
        self._platform = platform or sys.platform
        self._backend_factories = backend_factories
        self._resolved_backend = None
        self._backend_lock = threading.Lock()

    def _factories(self):
        if self._backend_factories is not None:
            factories = self._backend_factories.get(self._platform, ())
            return tuple((factory, None) for factory in factories)

        specs = self._BACKENDS.get(self._platform, ())
        resolved = []
        for module_name, class_name, label in specs:
            def factory(module_name=module_name, class_name=class_name):
                module = importlib.import_module(module_name)
                return getattr(module, class_name)()

            resolved.append((factory, label))
        return tuple(resolved)

    def _backend(self):
        if self._platform not in self._BACKENDS and self._backend_factories is None:
            raise CredentialStoreError(
                f"No supported native credential store is configured for {self._platform}."
            )

        if self._resolved_backend is not None:
            return self._resolved_backend

        with self._backend_lock:
            if self._resolved_backend is not None:
                return self._resolved_backend

            failures = []
            for factory, label in self._factories():
                try:
                    backend = factory()
                    priority = getattr(backend, "priority", 1)
                    if priority <= 0:
                        failures.append("native backend is unavailable")
                        continue
                    self._resolved_backend = (backend, label)
                    return self._resolved_backend
                except Exception as exc:  # noqa: BLE001 - sanitize native backend errors
                    # Backend setup details may include system-specific information;
                    # keep the public error useful without exposing that detail.
                    failures.append(type(exc).__name__)

            detail = ", ".join(dict.fromkeys(failures)) or "no allowlisted backend is installed"
            raise CredentialStoreError(
                f"No usable native credential store is available ({detail})."
            )

    def get_secret(self, credential_id: str) -> str:
        if not credential_id:
            return ""
        backend, _ = self._backend()
        try:
            secret = backend.get_password(SERVICE_NAME, credential_id)
        except Exception:  # noqa: BLE001 - backend errors may contain secret-bearing details
            raise CredentialStoreError("The native credential store could not read the key.") from None
        if secret is None:
            raise CredentialNotFoundError(
                "The configured credential is missing from the native credential store."
            )
        if not isinstance(secret, str):
            raise CredentialStoreError("The native credential store returned an invalid value.")
        return secret

    def set_secret_verified(self, credential_id: str, secret: str) -> str:
        if not credential_id or not secret:
            raise ValueError("A credential ID and non-empty secret are required.")
        backend, label = self._backend()
        try:
            existing = backend.get_password(SERVICE_NAME, credential_id)
        except Exception:  # noqa: BLE001 - backend errors may contain secret-bearing details
            raise CredentialStoreError("The native credential store could not check the key.") from None
        if existing is not None:
            raise CredentialConflictError(
                "A credential already exists for this generated ID; it was not overwritten."
            )

        try:
            backend.set_password(SERVICE_NAME, credential_id, secret)
            readback = backend.get_password(SERVICE_NAME, credential_id)
            if readback != secret:
                raise RuntimeError("Credential readback did not match.")
        except Exception:  # noqa: BLE001 - backend errors may contain secret-bearing details
            try:
                backend.delete_password(SERVICE_NAME, credential_id)
            except Exception:  # noqa: BLE001, S110 - cleanup is best effort; keep the primary error
                pass
            raise CredentialStoreError(
                "The native credential store could not save and verify the key."
            ) from None
        return label or "native OS credential store"

    def delete_secret(self, credential_id: str) -> None:
        if not credential_id:
            return
        backend, _ = self._backend()
        try:
            backend.delete_password(SERVICE_NAME, credential_id)
        except Exception:  # noqa: BLE001 - backend errors may contain secret-bearing details
            # Missing entries are harmless during post-commit cleanup. The
            # caller treats all cleanup failures as best-effort and never
            # rolls back a config file after it has committed.
            raise CredentialStoreError("The native credential store could not remove an old key.") from None
