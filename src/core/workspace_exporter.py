#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workspace Exporter — notespacellm-workspace-v1 Format
======================================================

Erzeugt ein datenschutzkonformes Workspace-JSON aus dem aktuellen Projekt.
Das Format ist der Austauschvertrag zwischen Desktop-App und Web/PWA/Mobile.

Datenschutzregeln (aus EXPORTFORMAT.md):
- API-Schlüssel werden nie exportiert
- Vektordatenbanken und Cache-Verzeichnisse werden nie exportiert
- Rohdokumente werden standardmäßig nicht eingebettet
- Auszüge nur wenn bereits für Report/Chat/Review ausgewählt
"""

import json
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .project import Project
    from .document_manager import DocumentItem

APP_VERSION = "1.0.0"
SCHEMA_VERSION = "notespacellm-workspace-v1"


def build_workspace_export_payload(
    project: "Project",
    report_content: str = "",
    chat_history: Optional[List[dict]] = None,
    include_subquery_excerpts: bool = True,
) -> dict:
    """
    Erzeugt das notespacellm-workspace-v1 Export-Payload.

    Args:
        project: Das aktuelle Projekt
        report_content: Aktueller Bericht-Text (Markdown)
        chat_history: Liste von Chat-Nachrichten [{"role": ..., "content": ...}]
        include_subquery_excerpts: Sub-Query-Ergebnisse als Dokument-Auszüge

    Returns:
        Dict mit dem vollständigen Workspace-Schema
    """
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # --- Dokumente ---
    documents = []
    for doc in project.documents.documents:
        if doc.is_directory:
            continue

        excerpts = []
        if include_subquery_excerpts:
            excerpts = _build_excerpts(project, doc.id)

        documents.append({
            "id": doc.id,
            "name": doc.name,
            "path_hint": doc.name,  # Nur Dateiname, kein absoluter Pfad
            "format": doc.extension.lstrip(".").lower() if doc.extension else "unknown",
            "selected": doc.is_selected,
            "content_included": False,  # Rohdaten nie exportieren
            "excerpts": excerpts,
        })

    # --- Report ---
    report = {
        "title": project.name,
        "format": "markdown",
        "content": report_content or "",
    }

    # --- Chat-Verlauf (ohne System-Nachrichten) ---
    safe_chat = []
    if chat_history:
        for msg in chat_history:
            role = msg.get("role", "")
            if role in ("user", "assistant") and msg.get("content"):
                safe_chat.append({"role": role, "content": msg["content"]})

    # --- Provider (ohne Secrets) ---
    provider_info = _build_provider_info(project)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "app": {
            "name": "NoteSpaceLLM",
            "version": APP_VERSION,
            "exported_at": now_iso,
        },
        "workspace": {
            "title": project.name,
            "question": project.main_question or "",
            "workflow_type": project.report_type or "analysis",
            "locale": project.settings.language or "de",
        },
        "documents": documents,
        "report": report,
        "chat": {"messages": safe_chat},
        "provider": provider_info,
    }
    return payload


def export_workspace_to_file(payload: dict, filepath: Path) -> None:
    """
    Schreibt das Workspace-Payload atomar als UTF-8-JSON-Datei.

    Atomic: schreibt zuerst in eine Temp-Datei, dann rename.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=filepath.parent, prefix=".tmp_workspace_", suffix=".json"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, filepath)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _build_excerpts(project: "Project", doc_id: str) -> List[dict]:
    """Erzeugt Auszüge aus abgeschlossenen Sub-Queries eines Dokuments."""
    excerpts = []
    try:
        for sq in project.subqueries.queries:
            if sq.document_id != doc_id:
                continue
            from .sub_query import SubQueryStatus
            if sq.status != SubQueryStatus.COMPLETED or not sq.result_text:
                continue
            excerpts.append({
                "id": sq.id,
                "text": sq.result_text[:2000],  # max 2000 Zeichen pro Auszug
                "source_hint": f"{sq.query_type.value}: {sq.query_text[:80]}",
            })
    except Exception:
        pass
    return excerpts


def _build_provider_info(project: "Project") -> dict:
    """Erzeugt Provider-Infos ohne Secrets."""
    try:
        provider = project.settings.llm_provider or "unknown"
        model = project.settings.llm_model or ""
        return {
            "mode": "local" if provider == "ollama" else "remote",
            "name": provider,
            "model_hint": model,
            "secret_exported": False,
        }
    except Exception:
        return {"mode": "unknown", "name": "unknown", "secret_exported": False}
