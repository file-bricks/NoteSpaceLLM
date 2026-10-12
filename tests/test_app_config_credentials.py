from __future__ import annotations

import json

import pytest

from src.core.app_config import (
    API_KEY_ENV_VAR,
    AppConfig,
    AppConfigConflictError,
    AppConfigError,
    LegacyCredentialMigrationRequired,
)
from src.core.credential_store import CredentialStoreError


class MemoryCredentialStore:
    def __init__(self):
        self.secrets = {}
        self.set_calls = []
        self.delete_calls = []
        self.fail_set = False

    def get_secret(self, credential_id):
        if credential_id not in self.secrets:
            from src.core.credential_store import CredentialNotFoundError
            raise CredentialNotFoundError("missing")
        return self.secrets[credential_id]

    def set_secret_verified(self, credential_id, secret):
        self.set_calls.append((credential_id, secret))
        if self.fail_set:
            raise CredentialStoreError("fake keyring failure")
        if credential_id in self.secrets:
            raise CredentialStoreError("duplicate")
        self.secrets[credential_id] = secret
        if self.secrets[credential_id] != secret:
            raise CredentialStoreError("readback mismatch")
        return "fake native store"

    def delete_secret(self, credential_id):
        self.delete_calls.append(credential_id)
        self.secrets.pop(credential_id, None)


@pytest.fixture
def config_factory(tmp_path, monkeypatch):
    import src.core.app_config as app_config_module

    config_file = tmp_path / "profile" / "config.json"
    monkeypatch.setattr(app_config_module, "CONFIG_FILE", config_file)
    monkeypatch.setattr(app_config_module, "CONFIG_DIR", config_file.parent)
    monkeypatch.delenv(API_KEY_ENV_VAR, raising=False)

    def create(store=None):
        return AppConfig(credential_store=store or MemoryCredentialStore())

    return config_file, create


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_config_construction_does_not_read_keyring(config_factory):
    class NoTouchStore(MemoryCredentialStore):
        def get_secret(self, credential_id):
            raise AssertionError("constructor touched keyring")

    _path, create = config_factory
    cfg = create(NoTouchStore())
    assert cfg.llm_provider == "ollama"


def test_project_settings_load_ignores_legacy_keys_and_existing_credential_ids(
    config_factory, monkeypatch
):
    import src.core.app_config as app_config_module
    from src.core.project import Project, ProjectSettings

    path, create = config_factory
    write_json(
        path,
        {
            "llm_provider": "ollama",
            "ollama_credential_id": "existing-global-id",
            "ollama_api_key": "legacy-global-secret",
            "active_profile": "Migrated",
            "profiles": {
                "Migrated": {
                    "llm_provider": "ollama",
                    "credential_id": "existing-profile-id",
                    "ollama_api_key": "legacy-profile-secret",
                }
            },
        },
    )
    before = path.read_bytes()

    class NoReadStore(MemoryCredentialStore):
        def __init__(self):
            super().__init__()
            self.read_calls = []

        def get_secret(self, credential_id):
            self.read_calls.append(credential_id)
            raise AssertionError("project load must not read the credential store")

    store = NoReadStore()
    cfg = create(store)
    monkeypatch.setattr(app_config_module, "_instance", cfg)

    settings = ProjectSettings.from_dict(
        {"ollama_credential_id": "project-id", "ollama_api_key": "project-legacy"}
    )
    project = Project.from_dict(
        {
            "id": "project-id",
            "name": "Synthetic project",
            "created_at": "2026-01-01T00:00:00",
            "settings": {
                "ollama_credential_id": "project-id",
                "ollama_api_key": "project-legacy",
            },
        }
    )

    assert settings.llm_provider == "ollama"
    assert project.settings.ollama_base_url == cfg.ollama_base_url
    assert not hasattr(settings, "ollama_api_key")
    assert not hasattr(project.settings, "ollama_api_key")
    assert cfg.has_legacy_credentials
    assert store.read_calls == []
    assert path.read_bytes() == before


def test_explicit_key_save_uses_verified_store_and_never_serializes_secret(config_factory):
    path, create = config_factory
    store = MemoryCredentialStore()
    cfg = create(store)
    cfg.ollama_api_key = "test-secret"
    cfg.save()

    saved = json.loads(path.read_text(encoding="utf-8"))
    credential_id = saved["ollama_credential_id"]
    assert store.secrets[credential_id] == "test-secret"
    assert cfg.get_ollama_api_key() == "test-secret"
    assert "test-secret" not in path.read_text(encoding="utf-8")


def test_environment_override_is_never_saved(config_factory, monkeypatch):
    path, create = config_factory
    store = MemoryCredentialStore()
    cfg = create(store)
    cfg.ollama_api_key = "saved-secret"
    cfg.save()
    before = path.read_bytes()

    monkeypatch.setenv(API_KEY_ENV_VAR, "environment-secret")
    assert cfg.get_ollama_api_key() == "environment-secret"
    cfg.ollama_api_key = "environment-secret"
    with pytest.raises(CredentialStoreError, match="cannot be persisted"):
        cfg.save()
    assert path.read_bytes() == before
    assert "environment-secret" not in store.secrets.values()


def test_legacy_plaintext_is_never_returned_until_explicit_migration(config_factory):
    path, create = config_factory
    write_json(path, {"ollama_api_key": "legacy-secret", "profiles": {}})
    store = MemoryCredentialStore()
    cfg = create(store)

    assert cfg.has_legacy_credentials
    assert cfg.credential_status()[0] == "legacy"
    with pytest.raises(LegacyCredentialMigrationRequired):
        cfg.get_ollama_api_key()
    assert store.set_calls == []

    assert cfg.migrate_legacy_credentials() == 1
    assert cfg.get_ollama_api_key() == "legacy-secret"
    saved_text = path.read_text(encoding="utf-8")
    assert "legacy-secret" not in saved_text
    assert not cfg.has_legacy_credentials


def test_migration_with_matching_existing_credential_removes_only_duplicate_plaintext(config_factory):
    path, create = config_factory
    write_json(
        path,
        {
            "ollama_credential_id": "existing-id",
            "ollama_api_key": "same-secret",
            "profiles": {},
        },
    )
    store = MemoryCredentialStore()
    store.secrets["existing-id"] = "same-secret"
    cfg = create(store)

    assert cfg.migrate_legacy_credentials() == 1
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["ollama_credential_id"] == "existing-id"
    assert "ollama_api_key" not in saved
    assert store.set_calls == []
    assert store.secrets == {"existing-id": "same-secret"}


def test_migration_conflict_with_existing_credential_preserves_config_and_secret(config_factory):
    path, create = config_factory
    write_json(
        path,
        {
            "ollama_credential_id": "existing-id",
            "ollama_api_key": "legacy-secret",
            "profiles": {},
        },
    )
    before = path.read_bytes()
    store = MemoryCredentialStore()
    store.secrets["existing-id"] = "different-secret"
    cfg = create(store)

    with pytest.raises(AppConfigError, match="conflicts with an existing"):
        cfg.migrate_legacy_credentials()
    assert path.read_bytes() == before
    assert cfg.has_legacy_credentials
    assert store.secrets == {"existing-id": "different-secret"}
    assert store.set_calls == []
    assert store.delete_calls == []


def test_missing_profile_legacy_key_is_not_written_to_keyring(config_factory):
    path, create = config_factory
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{"profiles":{"Gone":{"ollama_api_key":"stale-secret"}}}',
        encoding="utf-8",
    )
    before = path.read_bytes()
    store = MemoryCredentialStore()
    cfg = create(store)
    # Simulate an in-memory profile removal that left a legacy credential
    # scope behind, as can happen after a damaged/older config transition.
    cfg._data["profiles"].pop("Gone")

    with pytest.raises(AppConfigError, match="missing profile"):
        cfg.migrate_legacy_credentials()
    assert store.set_calls == []
    assert path.read_bytes() == before


def test_migration_keyring_failure_keeps_config_bytes_and_legacy_state(config_factory):
    path, create = config_factory
    write_json(path, {"ollama_api_key": "legacy-secret", "profiles": {}})
    before = path.read_bytes()
    store = MemoryCredentialStore()
    store.fail_set = True
    cfg = create(store)

    with pytest.raises(CredentialStoreError):
        cfg.migrate_legacy_credentials()
    assert path.read_bytes() == before
    assert cfg.has_legacy_credentials


def test_config_replace_failure_removes_new_key_and_keeps_old_file(config_factory, monkeypatch):
    import src.core.app_config as app_config_module

    path, create = config_factory
    write_json(path, {"ollama_api_key": "legacy-secret", "profiles": {}})
    before = path.read_bytes()
    store = MemoryCredentialStore()
    cfg = create(store)

    def fail_replace(*_args, **_kwargs):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(app_config_module.os, "replace", fail_replace)
    with pytest.raises(AppConfigError, match="could not be committed"):
        cfg.migrate_legacy_credentials()
    assert path.read_bytes() == before
    assert cfg.has_legacy_credentials
    assert store.secrets == {}
    assert len(store.delete_calls) == 1


def test_external_config_change_conflict_cleans_new_secret(config_factory):
    path, create = config_factory
    store = MemoryCredentialStore()
    cfg = create(store)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"llm_model":"external"}', encoding="utf-8")
    cfg.ollama_api_key = "candidate-secret"

    with pytest.raises(AppConfigConflictError):
        cfg.save()
    assert path.read_text(encoding="utf-8") == '{"llm_model":"external"}'
    assert store.secrets == {}
    assert len(store.delete_calls) == 1


def test_profile_rename_preserves_stable_credential_id(config_factory):
    _path, create = config_factory
    store = MemoryCredentialStore()
    cfg = create(store)
    cfg.ollama_api_key = "profile-secret"
    cfg.save_profile("Before")
    old_id = cfg.profiles["Before"]["credential_id"]

    assert cfg.rename_profile("Before", "After")
    assert cfg.profiles["After"]["credential_id"] == old_id
    assert cfg.get_ollama_api_key(profile_name="After") == "profile-secret"
