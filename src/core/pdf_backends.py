#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Backends - Austauschbare PDF-Extraktions- und Render-Engines
================================================================

Kapselt die PDF-Verarbeitung hinter einem einheitlichen Interface, damit
NoteSpaceLLM zwischen mehreren Bibliotheken umschalten kann:

- ``pymupdf``   (fitz)      -- beste Qualitaet, kann rendern (OCR). AGPL/Kommerziell.
- ``pypdfium2`` (PDFium)    -- Extraktion + Rendering (OCR). Apache-2.0/BSD-3.
- ``pypdf``                 -- reine Text-Extraktion, KEIN Rendering (kein OCR). BSD-3.

Der Konfig-Schalter ``pdf_backend`` (auto|pymupdf|pypdfium2|pypdf) steuert die
Auswahl. ``auto`` bevorzugt pymupdf (falls installiert), dann pypdfium2, dann
pypdf.
"""

import io
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class PdfBackend(ABC):
    """Einheitliche Schnittstelle fuer eine PDF-Engine."""

    #: Kurzname des Backends (auto-Schalter-Wert)
    name: str = ""

    #: True, wenn das Backend Seiten zu Bildern rendern kann (Voraussetzung fuer OCR)
    can_render: bool = False

    @staticmethod
    @abstractmethod
    def is_available() -> bool:
        """True, wenn die zugrunde liegende Bibliothek importierbar ist."""
        raise NotImplementedError

    @abstractmethod
    def extract_text(self, filepath: Path) -> List[str]:
        """Rohen Text je Seite zurueckgeben (eine Liste, ein Eintrag pro Seite)."""
        raise NotImplementedError

    @abstractmethod
    def page_count(self, filepath: Path) -> int:
        """Anzahl der Seiten im Dokument."""
        raise NotImplementedError

    def render_page_png(self, filepath: Path, page_index: int,
                        scale: float = 2.0) -> Optional[bytes]:
        """
        Eine Seite als PNG-Bytes rendern.

        Args:
            filepath: Pfad zur PDF
            page_index: 0-basierter Seitenindex
            scale: Zoom-Faktor (2.0 = doppelte Aufloesung, gut fuer OCR)

        Returns:
            PNG-Bytes oder ``None``, wenn dieses Backend nicht rendern kann.
        """
        return None


class PyMuPdfBackend(PdfBackend):
    """PyMuPDF (fitz) -- beste Qualitaet, rendert (AGPL/Kommerziell)."""

    name = "pymupdf"
    can_render = True

    @staticmethod
    def is_available() -> bool:
        import importlib.util
        return importlib.util.find_spec("fitz") is not None

    def extract_text(self, filepath: Path) -> List[str]:
        import fitz
        doc = fitz.open(str(filepath))
        try:
            return [page.get_text() for page in doc]
        finally:
            doc.close()

    def page_count(self, filepath: Path) -> int:
        import fitz
        doc = fitz.open(str(filepath))
        try:
            return doc.page_count
        finally:
            doc.close()

    def render_page_png(self, filepath: Path, page_index: int,
                        scale: float = 2.0) -> Optional[bytes]:
        import fitz
        doc = fitz.open(str(filepath))
        try:
            page = doc[page_index]
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat)
            return pix.tobytes("png")
        finally:
            doc.close()


class Pypdfium2Backend(PdfBackend):
    """pypdfium2 (Google PDFium) -- Extraktion + Rendering (Apache-2.0/BSD-3)."""

    name = "pypdfium2"
    can_render = True

    @staticmethod
    def is_available() -> bool:
        import importlib.util
        return importlib.util.find_spec("pypdfium2") is not None

    def extract_text(self, filepath: Path) -> List[str]:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(filepath))
        try:
            texts = []
            for i in range(len(pdf)):
                page = pdf[i]
                textpage = page.get_textpage()
                texts.append(textpage.get_text_range())
                textpage.close()
                page.close()
            return texts
        finally:
            pdf.close()

    def page_count(self, filepath: Path) -> int:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(filepath))
        try:
            return len(pdf)
        finally:
            pdf.close()

    def render_page_png(self, filepath: Path, page_index: int,
                        scale: float = 2.0) -> Optional[bytes]:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(filepath))
        try:
            page = pdf[page_index]
            bitmap = page.render(scale=scale)
            pil_image = bitmap.to_pil()
            buf = io.BytesIO()
            pil_image.save(buf, format="PNG")
            page.close()
            return buf.getvalue()
        finally:
            pdf.close()


class PypdfBackend(PdfBackend):
    """pypdf -- reine Text-Extraktion, KEIN Rendering (BSD-3)."""

    name = "pypdf"
    can_render = False

    @staticmethod
    def is_available() -> bool:
        import importlib.util
        return importlib.util.find_spec("pypdf") is not None

    def extract_text(self, filepath: Path) -> List[str]:
        from pypdf import PdfReader
        reader = PdfReader(str(filepath))
        return [(page.extract_text() or "") for page in reader.pages]

    def page_count(self, filepath: Path) -> int:
        from pypdf import PdfReader
        reader = PdfReader(str(filepath))
        return len(reader.pages)

    # render_page_png bleibt bei der Basisklasse -> None (kein OCR moeglich)


# Reihenfolge der auto-Kaskade: beste Qualitaet zuerst.
_AUTO_ORDER = (PyMuPdfBackend, Pypdfium2Backend, PypdfBackend)
_BY_NAME = {cls.name: cls for cls in _AUTO_ORDER}


def available_backends() -> dict:
    """Verfuegbarkeitsstatus aller bekannten Backends: {name: bool}."""
    return {cls.name: cls.is_available() for cls in _AUTO_ORDER}


def select_backend(preference: str = "auto") -> Optional[PdfBackend]:
    """
    Backend nach Konfig-Schalter auswaehlen.

    Args:
        preference: auto | pymupdf | pypdfium2 | pypdf

    Returns:
        Instanz des gewaehlten Backends, oder ``None`` wenn keine passende
        Bibliothek installiert ist.
    """
    pref = (preference or "auto").strip().lower()

    if pref == "auto":
        for cls in _AUTO_ORDER:
            if cls.is_available():
                return cls()
        return None

    cls = _BY_NAME.get(pref)
    if cls is None:
        # Unbekannter Wert -> wie auto behandeln (robust gegen Config-Tippfehler)
        for fallback in _AUTO_ORDER:
            if fallback.is_available():
                return fallback()
        return None

    if cls.is_available():
        return cls()
    return None
