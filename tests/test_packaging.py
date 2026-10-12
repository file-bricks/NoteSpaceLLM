"""Build-contract tests for the installable src package and source archive."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = (
    "ARCHITECTURE.txt",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "EXPORTFORMAT.md",
    "LICENSE",
    "MANIFEST.in",
    "NOTICE",
    "NoteSpaceLLM.ico",
    "PRIVACY_POLICY.md",
    "README.md",
    "README_de.md",
    "SECURITY.md",
    "STORE_LISTING.md",
    "SUPPORT.md",
    "THIRD_PARTY_LICENSES.md",
    "THIRD_PARTY_LICENSES.txt",
    "WINDOWS_STORE_PREP.md",
    "build_exe.bat",
    "llms.txt",
    "main.py",
    "manage_translations.py",
    "notespacellm_launcher.py",
    "pyproject.toml",
    "requirements.txt",
    "run.bat",
    "setup.py",
    "setup_environment.py",
    "start.bat",
    "store_package.json",
    "translator.py",
)
TREE_DIRS = ("assets", "locales", "scripts", "src", "tests", "web_companion")
IGNORED_NAMES = shutil.ignore_patterns(
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".pytest_temp",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "*.pyc",
    "*.pyo",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.log",
)
LOCAL_ONLY_DIRS = ("data", "output", "profiles", "workflows", "storage", "chroma_db", "releases")


def _copy_build_snapshot(destination: Path) -> Path:
    project = destination / "project"
    project.mkdir(parents=True)

    for name in ROOT_FILES:
        source = ROOT / name
        if source.is_file():
            shutil.copy2(source, project / source.name)

    for name in TREE_DIRS:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, project / name, ignore=IGNORED_NAMES)

    workflow_source = ROOT / ".github" / "workflows"
    if workflow_source.is_dir():
        shutil.copytree(
            workflow_source,
            project / ".github" / "workflows",
            ignore=IGNORED_NAMES,
        )

    return project


def _run(command: list[str], *, cwd: Path, env: dict[str, str], timeout: int = 240):
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def test_environment_bootstrap_stops_when_dependency_install_fails(
    tmp_path: Path, monkeypatch, capsys
):
    import runpy

    bootstrap = tmp_path / "setup_environment.py"
    shutil.copy2(ROOT / "setup_environment.py", bootstrap)
    namespace = runpy.run_path(str(bootstrap), run_name="setup_environment_test")
    calls = []

    def fail_dependency_install(command):
        calls.append(command)
        raise subprocess.CalledProcessError(23, command)

    monkeypatch.setattr(namespace["subprocess"], "check_call", fail_dependency_install)

    assert namespace["main"]() == 1

    assert len(calls) == 1
    assert calls[0][1:4] == ["-m", "pip", "install"]
    assert not any(
        (tmp_path / dirname).exists()
        for dirname in ("data", "workflows", "profiles", "output", "assets")
    )
    output = capsys.readouterr().out
    assert "Dependency installation failed" in output
    assert "Setup complete!" not in output


def test_setup_metadata_command_does_not_run_environment_bootstrap(tmp_path: Path):
    project = _copy_build_snapshot(tmp_path)
    # The bootstrap normally creates this directory, so leave it absent in
    # this metadata-only fixture even though it is a source asset in the repo.
    if (project / "assets").exists():
        shutil.rmtree(project / "assets")
    fake_pip = project / "pip"
    fake_pip.mkdir()
    (fake_pip / "__init__.py").write_text("", encoding="utf-8")
    (fake_pip / "__main__.py").write_text(
        "import os\nfrom pathlib import Path\n"
        "Path(os.environ['NOTESPACELLM_PIP_MARKER']).touch()\n"
        "raise SystemExit(87)\n",
        encoding="utf-8",
    )

    marker = tmp_path / "pip-was-called"
    env = os.environ.copy()
    env["NOTESPACELLM_PIP_MARKER"] = str(marker)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = _run([sys.executable, "setup.py", "--name"], cwd=project, env=env)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "notespacellm" in result.stdout.lower()
    assert not marker.exists(), "metadata inspection must never invoke the bootstrap pip install"
    for name in ("data", "workflows", "profiles", "output", "assets"):
        assert not (project / name).exists(), f"metadata inspection created {name}/"


def test_sdist_wheel_and_installed_src_runtime_contract(tmp_path: Path):
    project = _copy_build_snapshot(tmp_path)
    for dirname in LOCAL_ONLY_DIRS:
        local_dir = project / dirname
        local_dir.mkdir(parents=True, exist_ok=True)
        (local_dir / "synthetic-local-state-sentinel.txt").write_text(
            "synthetic data that must not ship", encoding="utf-8"
        )

    dist = tmp_path / "dist"
    dist.mkdir()
    build_env = os.environ.copy()
    build_env["PYTHONDONTWRITEBYTECODE"] = "1"
    build = _run(
        [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--sdist",
            "--wheel",
            "--outdir",
            str(dist),
        ],
        cwd=project,
        env=build_env,
        timeout=360,
    )
    assert build.returncode == 0, build.stdout + build.stderr

    wheels = list(dist.glob("*.whl"))
    sdists = list(dist.glob("*.tar.gz"))
    assert len(wheels) == 1
    assert len(sdists) == 1

    with zipfile.ZipFile(wheels[0]) as archive:
        wheel_names = set(archive.namelist())
        assert "src/__init__.py" in wheel_names
        assert "src/rag/engine.py" in wheel_names
        assert "src/core/workspace_exporter.py" in wheel_names
        assert any(name.endswith(".dist-info/licenses/LICENSE") for name in wheel_names)
        metadata_path = next(name for name in wheel_names if name.endswith(".dist-info/METADATA"))
        metadata = archive.read(metadata_path).decode("utf-8")
        metadata_lines = metadata.splitlines()
        assert "Version: 1.0.0" in metadata_lines
        assert "License-Expression: AGPL-3.0-only" in metadata_lines
        assert "Requires-Dist: PySide6" in metadata
        assert "Requires-Dist: chromadb" in metadata
        assert "Requires-Dist: keyring" in metadata
        assert not any("synthetic-local-state-sentinel" in name for name in wheel_names)
        assert not any(name.startswith(tuple(f"{d}/" for d in LOCAL_ONLY_DIRS)) for name in wheel_names)

    with tarfile.open(sdists[0], "r:gz") as archive:
        sdist_names = {name.split("/", 1)[1] for name in archive.getnames() if "/" in name}
        for expected in (
            "src/__init__.py",
            "src/rag/engine.py",
            "tests/test_packaging.py",
            "LICENSE",
            "NOTICE",
            "THIRD_PARTY_LICENSES.md",
            "setup_environment.py",
            "MANIFEST.in",
            "web_companion/index.html",
        ):
            assert expected in sdist_names, f"sdist omitted {expected}"
        assert not any("synthetic-local-state-sentinel" in name for name in sdist_names)
        assert not any(name.split("/", 1)[0] in LOCAL_ONLY_DIRS for name in sdist_names)

    target = tmp_path / "installed-target"
    install = _run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--no-index",
            "--target",
            str(target),
            str(wheels[0]),
        ],
        cwd=tmp_path,
        env=build_env,
        timeout=180,
    )
    assert install.returncode == 0, install.stdout + install.stderr

    import_env = build_env.copy()
    import_env.pop("PYTHONPATH", None)
    import_env["PYTHONPATH"] = str(target)
    import_env["HOME"] = str(tmp_path / "isolated-home")
    import_env["USERPROFILE"] = str(tmp_path / "isolated-home")
    import_env["APPDATA"] = str(tmp_path / "isolated-appdata")
    import_smoke = _run(
        [
            sys.executable,
            "-c",
            (
                "import src; import src.core.workspace_exporter; "
                "import src.rag.engine; import src.rag.embeddings; "
                "print(src.__file__)"
            ),
        ],
        cwd=tmp_path,
        env=import_env,
        timeout=120,
    )
    assert import_smoke.returncode == 0, import_smoke.stdout + import_smoke.stderr
    assert str(target) in import_smoke.stdout
