#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Config - Local application-level settings for NoteSpaceLLM.

Provider settings and profile metadata remain app-global. API keys live in the
native credential store; legacy plaintext fields are only retained for an
explicit user-requested migration and are never returned to a provider.
"""

from __future__ import annotations

import copy
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List

from .credential_store import (
    CredentialNotFoundError,
    CredentialStore,
    CredentialStoreError,
)


CONFIG_DIR = Path.home() / ".notespacellm"
CONFIG_FILE = CONFIG_DIR / "config.json"
API_KEY_ENV_VAR = "NOTESPACELLM_OLLAMA_API_KEY"
_UNSET = object()


class AppConfigError(RuntimeError):
    """App configuration could not be safely loaded or committed."""


class AppConfigConflictError(AppConfigError):
    """The config changed on disk since this instance loaded it."""


class LegacyCredentialMigrationRequired(AppConfigError):
    """A legacy key exists but must not be used before explicit migration."""


class AppConfig:
    """Persistent app-level configuration stored locally."""

    DEFAULTS = {
        "llm_provider": "ollama",
        "llm_model": "llama3",
        "ollama_base_url": "http://localhost:11434",
        "ollama_credential_id": "",
        "embedding_model": "nomic-embed-text",
        "claude_code_mode": "api",
        "active_profile": "",
        "profiles": {},
    }

    BUILTIN_PROFILES = {
        "Lokal (Standard)": {
            "llm_provider": "ollama",
            "llm_model": "llama3",
            "ollama_base_url": "http://localhost:11434",
            "embedding_model": "nomic-embed-text",
        },
    }

    def __init__(self, credential_store: CredentialStore | None = None):
        self._data: dict = copy.deepcopy(self.DEFAULTS)
        self._credential_store = credential_store or CredentialStore()
        self._legacy_credentials: dict[str, str] = {}
        self._loaded_config_bytes: bytes | None = None
        self._load_failed = False
        self._pending_api_key = _UNSET
        self.last_cleanup_error = ""
        self._load()

    def _load(self) -> None:
        """Read settings without touching the OS keyring or migrating secrets."""
        config_path = Path(CONFIG_FILE)
        try:
            raw = config_path.read_bytes()
        except FileNotFoundError:
            return
        except OSError:
            self._load_failed = True
            return

        self._loaded_config_bytes = raw
        try:
            stored = json.loads(raw.decode("utf-8"))
            if not isinstance(stored, dict):
                raise TypeError("configuration root must be an object")
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
            self._load_failed = True
            return

        self._data = copy.deepcopy(stored)
        for key, default in self.DEFAULTS.items():
            self._data.setdefault(key, copy.deepcopy(default))

        global_secret = self._data.pop("ollama_api_key", "")
        if isinstance(global_secret, str) and global_secret:
            self._legacy_credentials["global"] = global_secret

        profiles = self._data.get("profiles")
        if not isinstance(profiles, dict):
            profiles = {}
            self._data["profiles"] = profiles

        for name, profile in list(profiles.items()):
            if not isinstance(profile, dict):
                profiles[name] = {}
                continue
            profile = copy.deepcopy(profile)
            legacy_secret = profile.pop("ollama_api_key", "")
            if isinstance(legacy_secret, str) and legacy_secret:
                self._legacy_credentials[f"profile:{name}"] = legacy_secret
            profiles[name] = profile

    def _serialized_config(self, candidate: dict, legacy: dict[str, str]) -> bytes:
        stored = copy.deepcopy(candidate)
        stored.pop("ollama_api_key", None)
        profiles = stored.setdefault("profiles", {})
        for profile in profiles.values():
            if isinstance(profile, dict):
                profile.pop("ollama_api_key", None)

        if legacy.get("global"):
            stored["ollama_api_key"] = legacy["global"]
        for scope, secret in legacy.items():
            if not scope.startswith("profile:") or not secret:
                continue
            name = scope.partition(":")[2]
            profile = profiles.get(name)
            if isinstance(profile, dict):
                profile["ollama_api_key"] = secret

        return json.dumps(stored, indent=2, ensure_ascii=False).encode("utf-8")

    def _write_candidate(self, candidate: dict, legacy: dict[str, str]) -> bytes:
        if self._load_failed:
            raise AppConfigError(
                "The existing config could not be read; it was left unchanged."
            )

        config_path = Path(CONFIG_FILE)
        try:
            current_bytes = config_path.read_bytes()
        except FileNotFoundError:
            current_bytes = None
        except OSError as exc:
            raise AppConfigError("The existing config could not be checked.") from exc

        if current_bytes != self._loaded_config_bytes:
            raise AppConfigConflictError(
                "The config changed on disk. Reload it before saving to avoid overwriting changes."
            )

        encoded = self._serialized_config(candidate, legacy)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=config_path.parent,
                prefix=".config-",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temp_path = Path(stream.name)
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())

            readback = temp_path.read_bytes()
            if readback != encoded:
                raise AppConfigError("The temporary config failed its readback check.")
            json.loads(readback.decode("utf-8"))
            os.replace(temp_path, config_path)
            temp_path = None
            return encoded
        except Exception as exc:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass
            if isinstance(exc, AppConfigError):
                raise
            raise AppConfigError("The config could not be committed; the previous file was retained.") from exc

    def _commit(self, candidate: dict, legacy: dict[str, str]) -> None:
        encoded = self._write_candidate(candidate, legacy)
        self._data = copy.deepcopy(candidate)
        self._legacy_credentials = copy.deepcopy(legacy)
        self._loaded_config_bytes = encoded
        self._load_failed = False

    @staticmethod
    def _credential_ids(data: dict) -> set[str]:
        ids = set()
        global_id = data.get("ollama_credential_id")
        if isinstance(global_id, str) and global_id:
            ids.add(global_id)
        profiles = data.get("profiles", {})
        if isinstance(profiles, dict):
            for profile in profiles.values():
                if isinstance(profile, dict):
                    credential_id = profile.get("credential_id")
                    if isinstance(credential_id, str) and credential_id:
                        ids.add(credential_id)
        return ids

    def _cleanup_unreferenced(self, old_ids: set[str], candidate: dict) -> None:
        self.last_cleanup_error = ""
        for credential_id in old_ids - self._credential_ids(candidate):
            try:
                self._credential_store.delete_secret(credential_id)
            except CredentialStoreError as exc:
                self.last_cleanup_error = str(exc)

    def _discard_new_secret(self, credential_id: str | None) -> None:
        if not credential_id:
            return
        try:
            self._credential_store.delete_secret(credential_id)
        except CredentialStoreError:
            pass

    @property
    def llm_provider(self) -> str:
        return self._data["llm_provider"]

    @llm_provider.setter
    def llm_provider(self, value: str) -> None:
        self._data["llm_provider"] = value

    @property
    def llm_model(self) -> str:
        return self._data["llm_model"]

    @llm_model.setter
    def llm_model(self, value: str) -> None:
        self._data["llm_model"] = value

    @property
    def ollama_base_url(self) -> str:
        return self._data["ollama_base_url"]

    @ollama_base_url.setter
    def ollama_base_url(self, value: str) -> None:
        self._data["ollama_base_url"] = value

    @property
    def ollama_api_key(self) -> str:
        """Resolve a key only on explicit access; never read legacy plaintext."""
        return self.get_ollama_api_key()

    @ollama_api_key.setter
    def ollama_api_key(self, value: str) -> None:
        self._pending_api_key = value or ""

    @property
    def embedding_model(self) -> str:
        return self._data.get("embedding_model", "nomic-embed-text")

    @embedding_model.setter
    def embedding_model(self, value: str) -> None:
        self._data["embedding_model"] = value

    @property
    def claude_code_mode(self) -> str:
        return self._data.get("claude_code_mode", "api")

    @claude_code_mode.setter
    def claude_code_mode(self, value: str) -> None:
        self._data["claude_code_mode"] = value

    @property
    def profiles(self) -> Dict[str, dict]:
        """All saved profiles, with legacy plaintext keys removed."""
        all_profiles = copy.deepcopy(self.BUILTIN_PROFILES)
        all_profiles.update(copy.deepcopy(self._data.get("profiles", {})))
        return all_profiles

    @property
    def active_profile(self) -> str:
        return self._data.get("active_profile", "")

    @active_profile.setter
    def active_profile(self, value: str) -> None:
        self._data["active_profile"] = value

    @property
    def has_legacy_credentials(self) -> bool:
        return bool(self._legacy_credentials)

    @property
    def legacy_credential_count(self) -> int:
        return len(self._legacy_credentials)

    def _current_legacy_scope(self) -> str:
        active = self.active_profile
        if active and active in self._data.get("profiles", {}):
            return f"profile:{active}"
        return "global"

    def _current_credential_id(self) -> str:
        credential_id = self._data.get("ollama_credential_id", "")
        if credential_id:
            return credential_id
        active = self.active_profile
        if active:
            profile = self._data.get("profiles", {}).get(active, {})
            return profile.get("credential_id", "") if isinstance(profile, dict) else ""
        return ""

    def get_ollama_api_key(
        self,
        profile_name: str | None = None,
        explicit_key: str | None = None,
    ) -> str:
        """Resolve a request key with env override, profile, and keyring precedence."""
        env_key = os.environ.get(API_KEY_ENV_VAR, "")
        if env_key:
            return env_key
        if explicit_key:
            return explicit_key

        if profile_name is not None:
            profile = self._data.get("profiles", {}).get(profile_name)
            if not isinstance(profile, dict):
                raise AppConfigError(f"Unknown connection profile: {profile_name}")
            credential_id = profile.get("credential_id", "")
            legacy_scope = f"profile:{profile_name}"
        else:
            credential_id = self._current_credential_id()
            legacy_scope = self._current_legacy_scope()

        if credential_id:
            return self._credential_store.get_secret(credential_id)
        if self._legacy_credentials.get(legacy_scope):
            raise LegacyCredentialMigrationRequired(
                "A legacy API key is still stored in config and will not be sent. "
                "Use the explicit key migration action or replace/remove that key."
            )
        return ""

    def credential_status(self, profile_name: str | None = None) -> tuple[str, str]:
        """Return a secret-free status for the settings UI."""
        if os.environ.get(API_KEY_ENV_VAR, ""):
            return "environment", "Environment override active; it is never saved by the app."

        if profile_name is not None:
            profile = self._data.get("profiles", {}).get(profile_name)
            if not isinstance(profile, dict):
                return "missing", "No saved API key for this profile."
            credential_id = profile.get("credential_id", "")
            legacy_scope = f"profile:{profile_name}"
        else:
            credential_id = self._current_credential_id()
            legacy_scope = self._current_legacy_scope()

        if credential_id:
            try:
                self._credential_store.get_secret(credential_id)
                return "stored", "API key is available in the native OS credential store."
            except CredentialNotFoundError as exc:
                return "missing", str(exc)
            except CredentialStoreError as exc:
                return "unavailable", str(exc)
        if self._legacy_credentials.get(legacy_scope):
            return (
                "legacy",
                "A plaintext legacy key is present in config but will not be sent until migrated.",
            )
        return "missing", "No API key is stored; local Ollama can run without one."

    def save(self) -> None:
        """Save settings, writing a new credential only after explicit key input."""
        candidate = copy.deepcopy(self._data)
        legacy = copy.deepcopy(self._legacy_credentials)
        old_ids = self._credential_ids(self._data)
        pending = self._pending_api_key
        new_id = None

        if pending is _UNSET:
            self._commit(candidate, legacy)
            return
        if os.environ.get(API_KEY_ENV_VAR, "") and pending:
            raise CredentialStoreError(
                f"{API_KEY_ENV_VAR} is active; the environment key cannot be persisted."
            )

        try:
            if pending:
                new_id = str(uuid.uuid4())
                self._credential_store.set_secret_verified(new_id, pending)
                candidate["ollama_credential_id"] = new_id
                legacy.pop("global", None)
            else:
                candidate["ollama_credential_id"] = ""
                legacy.pop("global", None)
                active = candidate.get("active_profile", "")
                if active and isinstance(candidate.get("profiles", {}).get(active), dict):
                    candidate["profiles"][active].pop("credential_id", None)
                    legacy.pop(f"profile:{active}", None)

            self._commit(candidate, legacy)
        except Exception:
            self._discard_new_secret(new_id)
            raise

        self._pending_api_key = _UNSET
        self._cleanup_unreferenced(old_ids, candidate)

    def save_profile(self, name: str) -> None:
        """Save current app settings as a profile without storing a plaintext key."""
        if not name:
            raise ValueError("A profile name is required.")
        if os.environ.get(API_KEY_ENV_VAR, "") and self._pending_api_key:
            raise CredentialStoreError(
                f"{API_KEY_ENV_VAR} is active; its value cannot be saved into a profile."
            )

        candidate = copy.deepcopy(self._data)
        legacy = copy.deepcopy(self._legacy_credentials)
        old_ids = self._credential_ids(self._data)
        profiles = candidate.setdefault("profiles", {})
        existing = profiles.get(name, {})
        profile = {
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "ollama_base_url": self.ollama_base_url,
            "embedding_model": self.embedding_model,
        }
        pending = self._pending_api_key
        new_id = None

        try:
            if pending is not _UNSET:
                if pending:
                    new_id = str(uuid.uuid4())
                    self._credential_store.set_secret_verified(new_id, pending)
                    candidate["ollama_credential_id"] = new_id
                    profile["credential_id"] = new_id
                else:
                    candidate["ollama_credential_id"] = ""
                    legacy.pop("global", None)
                    legacy.pop(f"profile:{name}", None)
            else:
                credential_id = candidate.get("ollama_credential_id", "")
                if not credential_id and isinstance(existing, dict):
                    credential_id = existing.get("credential_id", "")
                if credential_id:
                    profile["credential_id"] = credential_id
                elif legacy.get("global") or legacy.get(f"profile:{name}"):
                    raise LegacyCredentialMigrationRequired(
                        "Migrate the legacy key or enter a replacement before saving this profile."
                    )

            if pending is not _UNSET:
                legacy.pop("global", None)
                legacy.pop(f"profile:{name}", None)
            profiles[name] = profile
            candidate["active_profile"] = name
            self._commit(candidate, legacy)
        except Exception:
            self._discard_new_secret(new_id)
            raise

        self._pending_api_key = _UNSET
        self._cleanup_unreferenced(old_ids, candidate)

    def load_profile(self, name: str) -> bool:
        """Activate a profile without reading or writing its keyring secret."""
        all_profiles = self.profiles
        if name not in all_profiles:
            return False

        profile = all_profiles[name]
        candidate = copy.deepcopy(self._data)
        for key in ("llm_provider", "llm_model", "ollama_base_url", "embedding_model"):
            candidate[key] = profile.get(key, self.DEFAULTS[key])
        candidate["ollama_credential_id"] = profile.get("credential_id", "")
        candidate["active_profile"] = name
        self._commit(candidate, copy.deepcopy(self._legacy_credentials))
        return True

    def set_active_profile(self, name: str) -> bool:
        """Select a profile in memory for a settings dialog that has not committed yet."""
        if not name:
            self._data["active_profile"] = ""
            return True
        profile = self._data.get("profiles", {}).get(name)
        if not isinstance(profile, dict):
            if name in self.BUILTIN_PROFILES:
                profile = self.BUILTIN_PROFILES[name]
            else:
                return False
        self._data["active_profile"] = name
        self._data["ollama_credential_id"] = profile.get("credential_id", "")
        return True

    def delete_profile(self, name: str) -> bool:
        if name in self.BUILTIN_PROFILES:
            return False
        profiles = self._data.get("profiles", {})
        if name not in profiles:
            return False

        candidate = copy.deepcopy(self._data)
        old_ids = self._credential_ids(self._data)
        removed = candidate["profiles"].pop(name)
        legacy = copy.deepcopy(self._legacy_credentials)
        legacy.pop(f"profile:{name}", None)
        if candidate.get("active_profile") == name:
            candidate["active_profile"] = ""

        self._commit(candidate, legacy)
        removed_id = removed.get("credential_id") if isinstance(removed, dict) else None
        self._cleanup_unreferenced(old_ids | ({removed_id} if removed_id else set()), candidate)
        return True

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        if old_name in self.BUILTIN_PROFILES or not new_name or new_name == old_name:
            return False
        profiles = self._data.get("profiles", {})
        if old_name not in profiles or new_name in self.BUILTIN_PROFILES or new_name in profiles:
            return False

        candidate = copy.deepcopy(self._data)
        candidate["profiles"][new_name] = candidate["profiles"].pop(old_name)
        if candidate.get("active_profile") == old_name:
            candidate["active_profile"] = new_name
        legacy = copy.deepcopy(self._legacy_credentials)
        legacy_scope = f"profile:{old_name}"
        if legacy_scope in legacy:
            legacy[f"profile:{new_name}"] = legacy.pop(legacy_scope)
        self._commit(candidate, legacy)
        return True

    def migrate_legacy_credentials(self) -> int:
        """Explicitly move legacy config keys to verified native keyring entries."""
        if not self._legacy_credentials:
            return 0
        if self._pending_api_key is not _UNSET:
            raise AppConfigError("Save or discard the current key edit before migration.")

        candidate = copy.deepcopy(self._data)
        old_ids = self._credential_ids(self._data)
        created_ids: list[str] = []
        migrated = 0

        # Validate all scopes before writing any keyring entries. This makes a
        # stale/corrupt profile reference a visible, non-destructive error.
        for scope in self._legacy_credentials:
            if scope == "global":
                continue
            if not scope.startswith("profile:"):
                raise AppConfigError("An unsupported legacy credential scope needs manual review.")
            profile_name = scope.partition(":")[2]
            profile = candidate.get("profiles", {}).get(profile_name)
            if not isinstance(profile, dict):
                raise AppConfigError(
                    "A legacy key refers to a missing profile; config was left unchanged."
                )

        try:
            for scope, secret in self._legacy_credentials.items():
                if not secret:
                    continue
                profile_name = None
                current_id = candidate.get("ollama_credential_id", "")
                if scope.startswith("profile:"):
                    profile_name = scope.partition(":")[2]
                    profile = candidate.get("profiles", {}).get(profile_name)
                    current_id = profile.get("credential_id", "")

                if current_id:
                    try:
                        current_secret = self._credential_store.get_secret(current_id)
                    except CredentialNotFoundError:
                        current_secret = None
                    if current_secret is not None:
                        if current_secret != secret:
                            raise AppConfigError(
                                "A legacy key conflicts with an existing stored key; "
                                "config was left unchanged."
                            )
                        # The same key is already stored. The explicit migration
                        # can remove the duplicate plaintext without replacing it.
                        migrated += 1
                        continue

                credential_id = str(uuid.uuid4())
                self._credential_store.set_secret_verified(credential_id, secret)
                created_ids.append(credential_id)
                if scope == "global":
                    candidate["ollama_credential_id"] = credential_id
                elif profile_name is not None:
                    profile["credential_id"] = credential_id
                migrated += 1

            if not migrated:
                return 0
            self._commit(candidate, {})
        except Exception:
            for credential_id in created_ids:
                self._discard_new_secret(credential_id)
            raise

        self._cleanup_unreferenced(old_ids, candidate)
        return migrated

    def list_profile_names(self) -> List[str]:
        return list(self.profiles.keys())


_instance: AppConfig | None = None


def get_app_config() -> AppConfig:
    """Get the global app config singleton."""
    global _instance
    if _instance is None:
        _instance = AppConfig()
    return _instance
