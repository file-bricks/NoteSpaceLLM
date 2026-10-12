# -*- coding: utf-8 -*-
"""Checks NoteSpaceLLM metadata, declared dependency coverage, and CI configuration."""

from pathlib import Path
import re

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python <3.11


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_notice_present_and_well_formed():
    notice_file = ROOT / "NOTICE"
    assert notice_file.is_file(), "Root NOTICE file must exist"
    content = notice_file.read_text(encoding="utf-8")

    assert "NoteSpaceLLM" in content
    assert "Lukas Geiger" in content
    assert "file-bricks" in content
    assert "open-bricks" in content
    assert "AGPL-3.0" in content



def test_declared_dependency_license_references_present():
    notes_file = ROOT / "THIRD_PARTY_LICENSES.md"
    assert notes_file.is_file(), "THIRD_PARTY_LICENSES.md must exist"
    content = notes_file.read_text(encoding="utf-8")

    assert "PySide6" in content
    assert "PyMuPDF" in content
    assert "AGPL-3.0-only" in content

    # Verify requirements coverage
    req_file = ROOT / "requirements.txt"
    for line in req_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pkg = re.split(r"[><=~]", line)[0].strip().lower()
        assert pkg in content.lower(), f"Package {pkg} must appear in the dependency notes"


def test_pep621_pyproject_metadata_and_version_freeze():
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.is_file()

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    assert project.get("license") == "AGPL-3.0-only"
    # The current full-care change preserves the declared application version.
    assert project.get("version") == "1.0.0", "Application version must remain 1.0.0"

    license_files = project.get("license-files", [])
    for expected_file in ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]:
        assert expected_file in license_files, f"{expected_file} must be declared in license-files"

    classifiers = project.get("classifiers", [])
    assert len(classifiers) >= 8, "pyproject.toml must retain its declared platform and topic classifiers"

    urls = project.get("urls", {})
    assert "Homepage" in urls
    assert "Repository" in urls
    assert "Documentation" in urls
    assert "Issues" in urls
    assert "Notice" in urls
    assert "Third-Party Licenses" in urls
    assert "Changelog" in urls

    pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "--basetemp=.pytest_temp" in pytest_opts.get("addopts", "")

    ruff_opts = data.get("tool", {}).get("ruff", {})
    assert ruff_opts.get("line-length") == 100


def test_gitignore_cloud_sync_and_lock_guards():
    gitignore_path = ROOT / ".gitignore"
    assert gitignore_path.is_file()
    content = gitignore_path.read_text(encoding="utf-8")

    # Multi-host sync conflict protection
    assert "*conflicted copy*" in content
    assert "*-WORKSTATION*" in content
    assert "*-ASUS*" in content
    assert "*-LAPTOP*" in content
    assert "*-Mac*" in content

    # System-wide and scoped locks
    assert "LOCK" in content
    assert "LOCK.user.*" in content
    assert "LOCK.until.*" in content
    assert "LOCK.condition.*" in content
    assert ".automation-lock" in content

    # Temporary test caches
    assert ".pytest_temp/" in content
    assert ".ruff_cache/" in content


def test_ci_workflows_have_timeouts_and_read_scope():
    ci_dir = ROOT / ".github" / "workflows"
    tests_file = ci_dir / "tests.yml"
    stale_file = ci_dir / "stale.yml"
    welcome_file = ci_dir / "welcome.yml"

    for wf_path in (tests_file, stale_file, welcome_file):
        assert wf_path.is_file(), f"Workflow {wf_path.name} must exist"
        wf_content = wf_path.read_text(encoding="utf-8")
        assert "timeout-minutes:" in wf_content, f"{wf_path.name} must specify timeout-minutes"

    tests_content = tests_file.read_text(encoding="utf-8")
    assert "cancel-in-progress: true" in tests_content, "tests.yml must specify cancel-in-progress"
    assert "contents: read" in tests_content
    assert "compileall" in tests_content
    assert "pytest" in tests_content
    assert "web-companion-tests" in tests_content


def test_security_reporting_links_are_present():
    security_file = ROOT / "SECURITY.md"
    assert security_file.is_file()
    sec_content = security_file.read_text(encoding="utf-8")

    assert "https://github.com/file-bricks/NoteSpaceLLM/security/advisories" in sec_content
    assert "security@file-bricks.org" in sec_content
    assert "support@lukasgeiger.com" in sec_content


def test_marketing_log_present_and_well_formed():
    mkt_file = ROOT / "MARKETING-LOG.txt"
    assert mkt_file.is_file(), "MARKETING-LOG.txt must exist"
    mkt_content = mkt_file.read_text(encoding="utf-8")

    assert "file-bricks" in mkt_content
    assert "open-bricks" in mkt_content
    assert "2026-09-22" in mkt_content
    assert "Pfad A" in mkt_content
