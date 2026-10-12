#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workspace Exporter — notespacellm-workspace-v1 Format
======================================================

Erstellt ein Workspace-JSON aus dem aktuellen Projekt.
Das Format ist der Austauschvertrag zwischen Desktop-App und Web/PWA/Mobile.

Datenschutzregeln (aus EXPORTFORMAT.md):
- Gespeicherte API-Schlüsselfelder werden nicht exportiert; frei verfasste
  Bericht- und Chattexte können trotzdem Geheimnisse enthalten.
- Vektordatenbanken und Cache-Verzeichnisse werden nie exportiert
- Rohdokumente werden standardmäßig nicht eingebettet
- Auszüge nur wenn bereits für Report/Chat/Review ausgewählt
"""

import json
import ipaddress
import re
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING
from urllib.parse import urlsplit

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
        if include_subquery_excerpts and doc.is_selected:
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
            # Stabile Projekt-ID (optional im Schema): Companion-Notizen werden
            # damit pro Projekt statt pro (nicht eindeutigem) Titel gespeichert.
            "id": str(getattr(project, "id", "") or ""),
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


def workspace_export_confirmation_text(payload: dict) -> str:
    """Describe the exact user content included before the UI writes an export."""
    documents = payload.get("documents", [])
    selected_documents = [doc for doc in documents if doc.get("selected")]
    excerpt_count = sum(len(doc.get("excerpts", [])) for doc in selected_documents)
    chat_messages = payload.get("chat", {}).get("messages", [])
    report_content = payload.get("report", {}).get("content", "")

    report_line = "Bericht: vollständiger Inhalt" if report_content else "Bericht: leer"
    return "\n".join((
        "Die Workspace-Datei enthält:",
        f"• Projektmetadaten und Dateinamen für {len(documents)} Dokument(e)",
        f"• {report_line}",
        f"• vollständigen Chatverlauf mit {len(chat_messages)} Nachrichten",
        (
            f"• {excerpt_count} abgeschlossene Auszüge aus "
            f"{len(selected_documents)} ausgewählten Dokument(en)"
        ),
        "",
        (
            "Der Export wird nicht anonymisiert. Bericht, Chat und Auszüge können "
            "persönliche oder vertrauliche Angaben enthalten. Vollständige "
            "Rohdokumente, gespeicherte API-Schlüsselfelder und lokale "
            "Vektordatenbanken werden nicht aufgenommen. Frei verfasste Inhalte "
            "werden nicht auf Geheimnisse geprüft; prüfe Bericht und Chat vor "
            "dem Weitergeben."
        ),
        "",
        "Möchtest du diese Inhalte in die gewählte Datei schreiben?",
    ))


def export_workspace_if_confirmed(payload: dict, filepath: Path, confirmed: bool) -> bool:
    """Write only after an explicit affirmative decision; return whether written."""
    if not confirmed:
        return False
    export_workspace_to_file(payload, filepath)
    return True


def _build_excerpts(project: "Project", doc_id: str) -> List[dict]:
    """Erzeugt Auszüge aus abgeschlossenen Sub-Queries eines Dokuments."""
    excerpts = []
    try:
        for sq in project.subqueries.queries:
            if sq.document_id != doc_id:
                continue
            from .sub_query import SubQueryStatus
            status_val = sq.status.value if hasattr(sq.status, "value") else str(sq.status)
            if status_val not in (SubQueryStatus.COMPLETED.value, "completed") or not sq.result_text:
                continue
            q_type = sq.query_type.value if hasattr(sq.query_type, "value") else str(sq.query_type or "custom")
            q_text = (sq.query_text or "")[:80]
            excerpts.append({
                "id": sq.id,
                "text": sq.result_text[:2000],  # max 2000 Zeichen pro Auszug
                "source_hint": f"{q_type}: {q_text}",
            })
    except Exception:
        pass
    return excerpts


def _build_provider_info(project: "Project") -> dict:
    """Erzeugt Provider-Infos ohne Secrets."""
    try:
        provider = project.settings.llm_provider or "unknown"
        model = project.settings.llm_model or ""
        if provider == "ollama":
            mode = _classify_ollama_endpoint(
                getattr(project.settings, "ollama_base_url", "")
            )
        elif provider in {"openai", "anthropic", "claude-code"}:
            mode = "remote"
        else:
            mode = "unknown"
        return {
            "mode": mode,
            "name": provider,
            "model_hint": model,
            "secret_exported": False,
        }
    except Exception:
        return {"mode": "unknown", "name": "unknown", "secret_exported": False}


def _classify_ollama_endpoint(value: object) -> str:
    """Classify configured endpoints without DNS or network access.

    Only a valid HTTP(S) URL with an exact localhost hostname or an IP loopback
    address is called local. Invalid or credential-bearing URLs stay unknown.
    """
    if not isinstance(value, str) or not value or any(ch.isspace() for ch in value):
        return "unknown"
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            return "unknown"
        if parsed.username is not None or parsed.password is not None:
            return "unknown"
        hostname = parsed.hostname
        port = parsed.port  # Raises ValueError for malformed/out-of-range values.
    except ValueError:
        return "unknown"

    if not hostname or port == 0:
        return "unknown"

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            ascii_host = hostname.encode("idna").decode("ascii").lower()
        except UnicodeError:
            return "unknown"
        if ascii_host.endswith(".."):
            return "unknown"
        normalized_host = ascii_host.removesuffix(".")
        labels = normalized_host.split(".")
        label_pattern = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")
        if any(
            not label or len(label) > 63 or not label_pattern.fullmatch(label)
            for label in labels
        ):
            return "unknown"
        return "local" if normalized_host == "localhost" else "remote"
    return "local" if address.is_loopback else "remote"
