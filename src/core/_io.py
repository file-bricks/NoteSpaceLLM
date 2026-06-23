#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared low-level IO helpers for the core package."""

from __future__ import annotations

import os
from pathlib import Path


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Schreibt Text atomar (tmp-Datei + os.replace).

    Bugsweep (2026-06-23): Direktes ``write_text``/``open(w)`` auf Projekt-,
    Workspace- und Config-Dateien hinterliess bei einem Absturz oder OneDrive-Lock
    mitten im Schreiben eine leere oder halb geschriebene Datei (Datenverlust; bei
    der App-Config inkl. ``ollama_api_key``). ``os.replace`` ist auf demselben
    Volume atomar, sodass die Zieldatei immer einen vollstaendigen Stand hat.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding=encoding)
    os.replace(tmp, path)
