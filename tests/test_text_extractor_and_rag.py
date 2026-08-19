#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for TextExtractor and DocumentManager RAG metadata integration.
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.core.text_extractor import TextExtractor, ExtractionResult
from src.core.document_manager import DocumentManager, DocumentItem, DocumentStatus


def test_rtf_extraction_umlauts_and_metadata_stripping(tmp_path):
    """Test RTF extraction correctly decodes German umlauts, unicode and strips metadata."""
    rtf_content = (
        r"{\rtf1\ansi\ansicpg1252\deff0\nouicompat\deflang1031{\fonttbl{\f0\fnil\fcharset0 Arial;}}" + "\n"
        r"{\colortbl ;\red0\green0\blue0;}" + "\n"
        r"{\*\generator Riched20 10.0.19041}\viewkind4\uc1 " + "\n"
        r"\pard\sa200\sl276\slmult1\f0\fs22\lang7 Dies ist ein Test f\'fcr deutsche Umlaute: \'e4, \'f6, \'fc, \'df, \'c4, \'d6, \'dc.\par" + "\n"
        r"Zweite Zeile mit \b fetter\b0  Schrift und Unicode: \u8364? 250.\par" + "\n"
        r"}"
    )

    rtf_file = tmp_path / "sample.rtf"
    rtf_file.write_bytes(rtf_content.encode("latin-1"))

    extractor = TextExtractor()
    result = extractor.extract(rtf_file)

    assert result.success is True
    assert "Riched20" not in result.text
    assert "fonttbl" not in result.text
    assert "Arial" not in result.text
    assert "Dies ist ein Test für deutsche Umlaute: ä, ö, ü, ß, Ä, Ö, Ü." in result.text
    assert "Zweite Zeile mit fetter Schrift und Unicode: € 250." in result.text
    assert result.word_count > 0


def test_html_to_text_helper():
    """Test HTML parsing and entity decoding in TextExtractor."""
    html_input = (
        "<html><head><title>Ignored Title</title><style>body { color: red; }</style></head>"
        "<body>"
        "<h1>Projekt &amp; Analyse</h1>"
        "<p>Absatz mit <b>fettem</b> Text und &Uuml;bersicht.</p>"
        "<div>Zweite Zeile mit &quot;Zitaten&quot; &lt;und&gt; Sonderzeichen.</div>"
        "<script>console.log('secret');</script>"
        "</body></html>"
    )

    text = TextExtractor._html_to_text(html_input)

    assert "Projekt & Analyse" in text
    assert "Absatz mit fettem Text und Übersicht." in text
    assert 'Zweite Zeile mit "Zitaten" <und> Sonderzeichen.' in text
    assert "secret" not in text
    assert "color: red" not in text


def test_eml_extraction_html_only(tmp_path):
    """Test EML extraction from multipart email that only contains HTML body."""
    eml_raw = (
        b"From: sender@example.com\r\n"
        b"To: receiver@example.com\r\n"
        b"Subject: Wichtige Mitteilung\r\n"
        b"Date: Mon, 14 Aug 2026 12:00:00 +0200\r\n"
        b"Content-Type: multipart/alternative; boundary=\"bound123\"\r\n\r\n"
        b"--bound123\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n\r\n"
        b"<html><body><p>Sehr geehrte Damen und Herren,<br>der Bericht ist <b>fertig</b>.</p></body></html>\r\n"
        b"--bound123--\r\n"
    )

    eml_file = tmp_path / "message.eml"
    eml_file.write_bytes(eml_raw)

    extractor = TextExtractor()
    result = extractor.extract(eml_file)

    assert result.success is True
    assert "From: sender@example.com" in result.text
    assert "Subject: Wichtige Mitteilung" in result.text
    assert "Sehr geehrte Damen und Herren" in result.text
    assert "der Bericht ist fertig." in result.text


def test_eml_extraction_plain_text(tmp_path):
    """Test EML extraction from plain text email."""
    eml_raw = (
        b"From: alice@example.com\r\n"
        b"To: bob@example.com\r\n"
        b"Subject: Treffen\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
        b"Hallo Bob, treffen wir uns morgen um 10 Uhr?"
    )

    eml_file = tmp_path / "plain.eml"
    eml_file.write_bytes(eml_raw)

    extractor = TextExtractor()
    result = extractor.extract(eml_file)

    assert result.success is True
    assert "From: alice@example.com" in result.text
    assert "Hallo Bob, treffen wir uns morgen um 10 Uhr?" in result.text


def test_document_manager_index_tags_serialization(tmp_path):
    """Test that DocumentManager passes serialized tags to RAGEngine.index_document."""
    mock_rag = MagicMock()
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.chunks_created = 3
    mock_rag.index_document.return_value = mock_result

    dm = DocumentManager(project_path=tmp_path, rag_engine=mock_rag)
    dm.set_auto_index(False)  # Explicit indexing test

    test_file = tmp_path / "test.txt"
    test_file.write_text("Inhalt des Dokuments für die RAG-Suche.", encoding="utf-8")

    doc = dm.add_file(test_file)
    assert doc is not None

    dm.add_tag(doc.id, "finanzen")
    dm.add_tag(doc.id, "analyse")
    dm.update_content(doc.id, "Inhalt des Dokuments für die RAG-Suche.")

    success = dm.index_document(doc.id)
    assert success is True

    # Verify RAGEngine was called with string tags metadata
    mock_rag.index_document.assert_called_once()
    kwargs = mock_rag.index_document.call_args.kwargs
    metadata = kwargs.get("metadata", {})

    assert isinstance(metadata.get("tags"), str)
    assert "finanzen" in metadata["tags"]
    assert "analyse" in metadata["tags"]
