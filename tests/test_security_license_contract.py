# -*- coding: utf-8 -*-
"""Security and License Contract Test Suite for NoteSpaceLLM.

Validates dependency vulnerability floors, complete third-party license
inventory, .gitignore sync conflict and lock patterns, absence of hardcoded
developer paths / secrets, offline zero-egress guarantees of core parsers,
and bilingual security policy standards.
"""
from __future__ import annotations

import ast
from pathlib import Path
import re

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dependency_vulnerability_floors() -> None:
    """Ensure declared dependency versions meet security floors."""
    pyproject_text = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pyproject_data = tomllib.loads(pyproject_text)

    deps = pyproject_data.get("project", {}).get("dependencies", [])
    assert any("PySide6>=6.5.0" in d for d in deps), (
        "pyproject.toml dependencies must declare PySide6>=6.5.0"
    )
    assert any("PyMuPDF>=1.24.10" in d for d in deps), (
        "pyproject.toml dependencies must declare PyMuPDF>=1.24.10"
    )
    assert any("openpyxl>=3.1.3" in d for d in deps), (
        "pyproject.toml dependencies must declare openpyxl>=3.1.3 to mitigate CVE-2024-34064"
    )
    assert any("chromadb>=0.5.4" in d for d in deps), (
        "pyproject.toml dependencies must declare chromadb>=0.5.4"
    )
    assert any("python-docx>=1.1.0" in d for d in deps), (
        "pyproject.toml dependencies must declare python-docx>=1.1.0"
    )

    opt_deps = pyproject_data.get("project", {}).get("optional-dependencies", {})
    test_deps = opt_deps.get("test", [])
    dev_deps = opt_deps.get("dev", [])

    all_test_deps = test_deps + dev_deps
    assert any("pytest>=9.1.1" in d for d in all_test_deps), (
        "pytest floor must be >=9.1.1 to protect against CVE-2025-7117 / GHSA-6w46-j5rx-g56g"
    )

    req_text = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "PySide6>=6.5.0" in req_text, "requirements.txt must declare PySide6>=6.5.0"
    assert "PyMuPDF>=1.24.10" in req_text, "requirements.txt must declare PyMuPDF>=1.24.10"
    assert "openpyxl>=3.1.3" in req_text, "requirements.txt must declare openpyxl>=3.1.3"
    assert "chromadb>=0.5.4" in req_text, "requirements.txt must declare chromadb>=0.5.4"


def test_third_party_licenses_inventory_complete() -> None:
    """Ensure THIRD_PARTY_LICENSES.txt comprehensively covers dependencies."""
    tpl_path = PROJECT_ROOT / "THIRD_PARTY_LICENSES.txt"
    assert tpl_path.is_file(), "THIRD_PARTY_LICENSES.txt must exist"
    text = tpl_path.read_text(encoding="utf-8")

    required_packages = [
        "PySide6",
        "shiboken6",
        "PyMuPDF",
        "python-docx",
        "openpyxl",
        "extract-msg",
        "langchain",
        "langchain-core",
        "langchain-community",
        "langchain-ollama",
        "langchain-chroma",
        "chromadb",
        "pytest",
        "ruff",
        "PyInstaller",
    ]
    for pkg in required_packages:
        assert pkg in text, f"Missing {pkg} in THIRD_PARTY_LICENSES.txt"

    assert "License:" in text, "Missing License entries in inventory"
    assert "URL:" in text, "Missing URL entries in inventory"

    # Verify sections exist
    assert "1. Runtime Dependencies" in text
    assert "2. Optional Integrations & Backends" in text
    assert "3. Development, Build & Test Dependencies" in text

    # Verify copyleft & compatibility analysis
    assert "AGPL-3.0" in text
    assert "LGPL-3.0-only" in text
    assert "License Compatibility & Copyleft Analysis" in text


def test_gitignore_security_and_conflict_hardening() -> None:
    """Ensure .gitignore blocks sync conflict copies, lock files, and sensitive data."""
    gi_path = PROJECT_ROOT / ".gitignore"
    assert gi_path.is_file(), ".gitignore must exist"
    text = gi_path.read_text(encoding="utf-8")

    required_patterns = [
        "*-WORKSTATION-LG*",
        "*-ASUS-GEI*",
        "*.conflict",
        "*.sync-conflict-*",
        "LOCK*",
        "LOCK.*",
        "LOCK*.txt",
        ".env",
        "credentials.json",
        "*.pem",
        "*.key",
        "*.pfx",
        ".pytest_cache/",
    ]
    for pattern in required_patterns:
        assert pattern in text, f"Missing pattern '{pattern}' in .gitignore"


def test_no_hardcoded_user_paths_or_dev_secrets() -> None:
    """Ensure Python source and test files contain no private user paths or secrets."""
    forbidden_paths = [
        re.compile(r"C:[\\/]Users[\\/]lukas", re.IGNORECASE),
        re.compile(r"/home/lukas", re.IGNORECASE),
    ]
    secret_patterns = [
        re.compile(r"ghp_[A-Za-z0-9]{36}"),
        re.compile(r"github_pat_[A-Za-z0-9_]{82}"),
        re.compile(r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----"),
    ]

    current_file = Path(__file__).resolve()
    py_files = [
        p for p in (list(PROJECT_ROOT.glob("*.py")) + list((PROJECT_ROOT / "src").rglob("*.py")) + list((PROJECT_ROOT / "tests").rglob("*.py")))
        if p.resolve() != current_file
    ]
    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for pat in forbidden_paths:
            assert not pat.search(content), (
                f"Hardcoded developer path found in {py_file.name}"
            )
        for pat in secret_patterns:
            assert not pat.search(content), (
                f"Plaintext secret pattern found in {py_file.name}"
            )


def test_offline_core_document_parsers_zero_egress() -> None:
    """Verify core document extraction and project modules perform zero network calls."""
    forbidden_modules = {
        "urllib.request",
        "requests",
        "httpx",
        "aiohttp",
        "socket",
        "http.client",
        "ftplib",
        "smtplib",
    }
    core_files = [
        PROJECT_ROOT / "src" / "core" / "text_extractor.py",
        PROJECT_ROOT / "src" / "core" / "document_manager.py",
        PROJECT_ROOT / "src" / "core" / "project.py",
        PROJECT_ROOT / "src" / "core" / "sub_query.py",
        PROJECT_ROOT / "src" / "core" / "workspace_exporter.py",
    ]
    for py_file in core_files:
        if not py_file.is_file():
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in forbidden_modules, (
                        f"Forbidden network module '{alias.name}' in {py_file.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert node.module not in forbidden_modules, (
                        f"Forbidden network module '{node.module}' in {py_file.name}"
                    )


def test_security_policy_bilingual_and_sla() -> None:
    """Verify SECURITY.md contains bilingual policy, contacts, and 48h SLA."""
    sec_path = PROJECT_ROOT / "SECURITY.md"
    assert sec_path.is_file(), "SECURITY.md must exist"
    text = sec_path.read_text(encoding="utf-8")

    assert "## Deutsch" in text
    assert "## English" in text
    assert "48 Stunden" in text
    assert "48 hours" in text
    assert "5 Werktagen" in text
    assert "5 business days" in text
    assert "security@file-bricks.org" in text
    assert "support@lukasgeiger.com" in text
    assert "https://github.com/file-bricks/NoteSpaceLLM/security/advisories" in text
