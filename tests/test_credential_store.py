from __future__ import annotations

import pytest

from src.core.credential_store import (
    SERVICE_NAME,
    CredentialConflictError,
    CredentialStore,
    CredentialStoreError,
)


class MemoryBackend:
    priority = 1

    def __init__(self):
        self.passwords = {}
        self.fail_readback = False
        self.delete_calls = []

    def get_password(self, service, username):
        if self.fail_readback and (service, username) in self.passwords:
            return "different value"
        return self.passwords.get((service, username))

    def set_password(self, service, username, password):
        self.passwords[(service, username)] = password

    def delete_password(self, service, username):
        self.delete_calls.append((service, username))
        self.passwords.pop((service, username), None)


def test_constructing_store_does_not_load_or_touch_backend():
    calls = []
    store = CredentialStore(
        platform="linux",
        backend_factories={"linux": (lambda: calls.append("backend"),)},
    )

    assert calls == []
    assert store._platform == "linux"


def test_secret_write_is_verified_and_conflicting_id_is_not_overwritten():
    backend = MemoryBackend()
    store = CredentialStore(
        platform="test", backend_factories={"test": (lambda: backend,)}
    )

    assert store.set_secret_verified("credential-1", "secret") == "native OS credential store"
    assert store.get_secret("credential-1") == "secret"
    with pytest.raises(CredentialConflictError):
        store.set_secret_verified("credential-1", "replacement")
    assert backend.passwords[(SERVICE_NAME, "credential-1")] == "secret"


def test_failed_readback_removes_new_secret():
    backend = MemoryBackend()
    backend.fail_readback = True
    store = CredentialStore(
        platform="test", backend_factories={"test": (lambda: backend,)}
    )

    with pytest.raises(CredentialStoreError, match="save and verify"):
        store.set_secret_verified("new-credential", "secret")
    assert (SERVICE_NAME, "new-credential") not in backend.passwords
    assert backend.delete_calls == [(SERVICE_NAME, "new-credential")]


def test_backend_instance_is_reused_for_write_readback_and_later_reads():
    backend = MemoryBackend()
    factory_calls = []

    def factory():
        factory_calls.append("created")
        return backend

    store = CredentialStore(platform="test", backend_factories={"test": (factory,)})
    store.set_secret_verified("credential-1", "secret")
    assert store.get_secret("credential-1") == "secret"
    assert factory_calls == ["created"]


def test_only_allowlisted_platforms_are_available_without_injected_factories():
    store = CredentialStore(platform="unsupported-os")
    with pytest.raises(CredentialStoreError, match="No supported native"):
        store.get_secret("credential-1")
