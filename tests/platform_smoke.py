#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kleiner Source-Smoke für Desktop-Plattformen.

Prüft ohne echten LLM-/Ollama-Server:
- QApplication + MainWindow starten offscreen
- temporäres Dokument in ein Projekt laden
- einfachen Bericht lokal exportieren
- notespacellm-workspace-v1.json exportieren
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def run_platform_smoke(project_name: str = "Desktop Smoke") -> str:
    """Führt einen kleinen Offscreen-Smoke durch und gibt eine Kurzinfo zurück."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtWidgets import QApplication
    from src.core.project import Project
    from src.core.workspace_exporter import (
        build_workspace_export_payload,
        export_workspace_to_file,
    )
    from src.gui.main_window import MainWindow
    from src.reports.exporter import ReportExporter

    with tempfile.TemporaryDirectory(prefix="notespacellm-smoke-") as tmp_dir:
        tmp_home = Path(tmp_dir)
        sample_file = tmp_home / "quelle.txt"
        export_file = tmp_home / "workspace.json"
        reports_dir = tmp_home / "reports"
        sample_text = "Äpfel, Öl und Übersicht für den Plattform-Smoke."
        sample_file.write_text(sample_text, encoding="utf-8")

        app = QApplication.instance() or QApplication([])

        with patch("pathlib.Path.home", return_value=tmp_home):
            with patch.object(MainWindow, "_init_rag_engine", lambda self: None):
                window = MainWindow()
                window.show()
                app.processEvents()

                project = Project.create(
                    name=project_name,
                    main_question="Welche Kernpunkte enthält das Testdokument?",
                    report_type="analysis",
                )
                document = project.documents.add_file(sample_file)
                if document is None:
                    raise AssertionError("Dokument konnte im Smoke nicht importiert werden.")
                project.documents.update_content(document.id, sample_text)

                window._current_project = project
                window.output_panel.set_content("# Smoke-Bericht\n\nExportbereit.")
                app.processEvents()

                exporter = ReportExporter(reports_dir)
                report_results = exporter.export(
                    content=window.output_panel.get_content(),
                    base_name="platform_smoke_bericht",
                    formats=["md", "txt"],
                    title="Smoke-Bericht",
                )
                if not all(result.success for result in report_results):
                    raise AssertionError("Berichtsexport schlug im Plattform-Smoke fehl.")
                report_files = {result.format: result.filepath for result in report_results}
                if not report_files["md"].exists() or not report_files["txt"].exists():
                    raise AssertionError("Erwartete Report-Dateien fehlen im Plattform-Smoke.")
                if "Smoke-Bericht" not in report_files["md"].read_text(encoding="utf-8"):
                    raise AssertionError("Markdown-Export enthält den Smoke-Bericht nicht.")
                if "Exportbereit." not in report_files["txt"].read_text(encoding="utf-8"):
                    raise AssertionError("TXT-Export enthält den Smoke-Bericht nicht.")

                payload = build_workspace_export_payload(
                    project=project,
                    report_content=window.output_panel.get_content(),
                    chat_history=[
                        {"role": "user", "content": "Kurzer Test"},
                        {"role": "assistant", "content": "Smoke erfolgreich."},
                    ],
                )
                export_workspace_to_file(payload, export_file)

                exported = json.loads(export_file.read_text(encoding="utf-8"))
                if exported["schema_version"] != "notespacellm-workspace-v1":
                    raise AssertionError("Workspace-Schema im Smoke unerwartet.")
                if exported["documents"][0]["name"] != "quelle.txt":
                    raise AssertionError("Importiertes Dokument fehlt im Smoke-Export.")
                if "Äpfel" not in sample_file.read_text(encoding="utf-8"):
                    raise AssertionError("UTF-8-Smoke fehlgeschlagen.")

                window.close()
                app.processEvents()

                return (
                    f"{export_file.name} + {report_files['md'].name}"
                    f" ({len(exported['documents'])} Dokument)"
                )


def main() -> int:
    summary = run_platform_smoke()
    print(f"Platform smoke OK: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
