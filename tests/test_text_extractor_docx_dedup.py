# -*- coding: utf-8 -*-
"""Regressionstest fuer TextExtractor._extract_docx() -- Nebenfund aus
T-20260817-825816579, eigenes Ticket T-20260817-422197376.

`row.cells` liefert in python-docx eine ueber mehrere Rasterspalten verbundene
Zelle einmal PRO SPALTE. Ohne Dedup ueber die Identitaet des zugrunde
liegenden <w:tc>-Elements wird der Zellinhalt so oft wiederholt, wie er
Spalten ueberspannt -- formularartige DOCX werden dadurch um ein Vielfaches
aufgeblaeht (in BACH an einer realen Formular-DOCX gemessen: Faktor ~17,8x).
Dieser Test baut eine synthetische DOCX mit einer horizontal verbundenen
Zelle und prueft, dass der extrahierte Text jeden eindeutigen Zellinhalt
genau einmal enthaelt.
"""
from pathlib import Path

import pytest

docx = pytest.importorskip("docx")

from src.core.text_extractor import TextExtractor  # noqa: E402


def _build_docx_with_merged_header(path: Path) -> None:
    """Tabelle mit 4 Spalten; Zeile 1 ist eine ueber alle 4 Spalten verbundene
    Ueberschriftszelle, Zeile 2 hat vier eigenstaendige Zellen -- das
    Formular-Muster aus T-20260817-825816579."""
    doc = docx.Document()
    table = doc.add_table(rows=2, cols=4)
    header_cell = table.cell(0, 0).merge(table.cell(0, 3))
    header_cell.text = "LERNVEREINBARUNG"
    for i, text in enumerate(["Name", "Datum", "Ort", "Unterschrift"]):
        table.cell(1, i).text = text
    doc.save(str(path))


def test_row_cells_repeats_merged_cell_per_column(tmp_path):
    """Gegenprobe: row.cells zaehlt die verbundene Zelle 4x, tc-Identitaet nur 1x."""
    docx_path = tmp_path / "merged.docx"
    _build_docx_with_merged_header(docx_path)

    doc = docx.Document(str(docx_path))
    row0 = doc.tables[0].rows[0]
    assert len(row0.cells) == 4
    assert len({id(c._tc) for c in row0.cells}) == 1


def test_extract_docx_deduplicates_merged_cells(tmp_path):
    docx_path = tmp_path / "merged.docx"
    _build_docx_with_merged_header(docx_path)

    extractor = TextExtractor(enable_ocr=False)
    result = extractor._extract_docx(docx_path)

    assert result.success is True
    lines = [line for line in result.text.split("\n") if line.strip()]

    # Zeile 1: die verbundene Zelle darf nur EIN Segment liefern, nicht 4.
    header_line = next(line for line in lines if "LERNVEREINBARUNG" in line)
    assert header_line.count("LERNVEREINBARUNG") == 1
    assert " | " not in header_line

    # Zeile 2: vier eigenstaendige Zellen bleiben vollstaendig und unverdoppelt.
    data_line = next(line for line in lines if "Name" in line)
    assert data_line == "Name | Datum | Ort | Unterschrift"

    # Kein genereller Textverlust: eindeutige Zellinhalte bleiben vollstaendig.
    assert "Name" in result.text
    assert "Datum" in result.text
    assert "Ort" in result.text
    assert "Unterschrift" in result.text


def test_extract_docx_unmerged_table_unaffected(tmp_path):
    """Gegenprobe: eine Tabelle ganz ohne verbundene Zellen bleibt unveraendert
    (keine Regression fuer den Normalfall)."""
    docx_path = tmp_path / "plain.docx"
    doc = docx.Document()
    table = doc.add_table(rows=2, cols=3)
    for r, row_vals in enumerate([["A", "B", "C"], ["1", "2", "3"]]):
        for c, val in enumerate(row_vals):
            table.cell(r, c).text = val
    doc.save(str(docx_path))

    extractor = TextExtractor(enable_ocr=False)
    result = extractor._extract_docx(docx_path)

    assert result.success is True
    lines = [line for line in result.text.split("\n") if line.strip()]
    assert "A | B | C" in lines
    assert "1 | 2 | 3" in lines
