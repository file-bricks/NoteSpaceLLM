"""Tests fuer den PDF-Backend-Schalter (Entscheidung E05, 2026-07-04).

Deckt ab:
  - auto-Kaskade der Backend-Auswahl (pymupdf -> pypdfium2 -> pypdf) via Monkeypatch
  - Extraktions-Roundtrip je real installiertem Backend (kleines generiertes Test-PDF)
  - Render-/OCR-Faehigkeit: PNG-Bytes bei pypdfium2/pymupdf, None bei pypdf,
    und saubere OCR-Fehlermeldung, wenn das pypdf-Backend nicht rendern kann.
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core import pdf_backends
from src.core.pdf_backends import (
    PyMuPdfBackend, Pypdfium2Backend, PypdfBackend,
    select_backend, available_backends,
)
from src.core.text_extractor import TextExtractor


TEST_TEXT = "NoteSpaceLLM PDF Backend Test 12345"


def _assemble_pdf(stream: bytes) -> bytes:
    """Baut ein minimales, gueltiges 1-Seiten-PDF mit korrektem xref."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf += str(i).encode() + b" 0 obj\n" + body + b"\nendobj\n"
    xref_pos = len(pdf)
    size = len(objects) + 1
    pdf += b"xref\n0 " + str(size).encode() + b"\n0000000000 65535 f \n"
    for off in offsets:
        pdf += ("%010d 00000 n \n" % off).encode()
    pdf += b"trailer\n<< /Size " + str(size).encode() + b" /Root 1 0 R >>\nstartxref\n"
    pdf += str(xref_pos).encode() + b"\n%%EOF"
    return bytes(pdf)


def make_text_pdf(text: str = TEST_TEXT) -> bytes:
    esc = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = b"BT /F1 24 Tf 72 720 Td (" + esc.encode("latin-1") + b") Tj ET"
    return _assemble_pdf(stream)


def make_blank_pdf() -> bytes:
    """PDF ohne Textinhalt -> loest im Extractor den OCR-Pfad aus."""
    return _assemble_pdf(b"")


def _write_tmp(data: bytes) -> Path:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    with open(fd, "wb") as f:
        f.write(data)
    return Path(path)


class TestBackendSelection(unittest.TestCase):
    """auto-Kaskade und explizite Auswahl per Monkeypatch der Verfuegbarkeit."""

    def _patch(self, pymupdf, pypdfium2, pypdf):
        return (
            mock.patch.object(PyMuPdfBackend, "is_available", staticmethod(lambda: pymupdf)),
            mock.patch.object(Pypdfium2Backend, "is_available", staticmethod(lambda: pypdfium2)),
            mock.patch.object(PypdfBackend, "is_available", staticmethod(lambda: pypdf)),
        )

    def _select(self, pref, pymupdf, pypdfium2, pypdf):
        patches = self._patch(pymupdf, pypdfium2, pypdf)
        for p in patches:
            p.start()
        try:
            return select_backend(pref)
        finally:
            for p in patches:
                p.stop()

    def test_auto_prefers_pymupdf(self):
        b = self._select("auto", True, True, True)
        self.assertEqual(b.name, "pymupdf")

    def test_auto_falls_to_pypdfium2(self):
        b = self._select("auto", False, True, True)
        self.assertEqual(b.name, "pypdfium2")

    def test_auto_falls_to_pypdf(self):
        b = self._select("auto", False, False, True)
        self.assertEqual(b.name, "pypdf")

    def test_auto_none_when_nothing_installed(self):
        b = self._select("auto", False, False, False)
        self.assertIsNone(b)

    def test_explicit_backend_selected(self):
        b = self._select("pypdf", True, True, True)
        self.assertEqual(b.name, "pypdf")

    def test_explicit_unavailable_returns_none(self):
        b = self._select("pymupdf", False, True, True)
        self.assertIsNone(b)

    def test_unknown_pref_falls_back_like_auto(self):
        b = self._select("tippfehler", False, True, True)
        self.assertEqual(b.name, "pypdfium2")


class TestExtractionRoundtrip(unittest.TestCase):
    """Roundtrip je real installiertem Backend."""

    @classmethod
    def setUpClass(cls):
        cls.pdf_path = _write_tmp(make_text_pdf())

    @classmethod
    def tearDownClass(cls):
        cls.pdf_path.unlink(missing_ok=True)

    def _roundtrip(self, backend_name):
        if not available_backends().get(backend_name):
            self.skipTest(f"{backend_name} nicht installiert")
        extractor = TextExtractor(enable_ocr=False, pdf_backend=backend_name)
        self.assertEqual(extractor._pdf_backend.name, backend_name)
        result = extractor.extract(self.pdf_path)
        self.assertTrue(result.success, f"{backend_name}: {result.error}")
        self.assertIn(TEST_TEXT, result.text)
        self.assertEqual(result.method, "native")

    def test_roundtrip_pymupdf(self):
        self._roundtrip("pymupdf")

    def test_roundtrip_pypdfium2(self):
        self._roundtrip("pypdfium2")

    def test_roundtrip_pypdf(self):
        self._roundtrip("pypdf")


class TestRenderAndOcr(unittest.TestCase):
    """Render-Faehigkeit und OCR-Pfad-Routing."""

    @classmethod
    def setUpClass(cls):
        cls.pdf_path = _write_tmp(make_text_pdf())
        cls.blank_path = _write_tmp(make_blank_pdf())

    @classmethod
    def tearDownClass(cls):
        cls.pdf_path.unlink(missing_ok=True)
        cls.blank_path.unlink(missing_ok=True)

    def _assert_renders_png(self, backend_cls):
        if not backend_cls.is_available():
            self.skipTest(f"{backend_cls.name} nicht installiert")
        # render_page_png() der pypdfium2/PyMuPDF-Backends geht ueber Pillow
        # (bitmap.to_pil() bzw. pix.tobytes()). Pillow ist bewusst NICHT Teil
        # von requirements.txt (nur zusammen mit pytesseract als OCR-Extra in
        # requirements-optional.txt) -- der produktive OCR-Pfad prueft das
        # bereits vorab (_deps["pytesseract"] deckt "pytesseract UND PIL
        # importierbar" ab), bevor render_page_png() ueberhaupt aufgerufen
        # wird. Dieser Test ruft render_page_png() direkt auf und muss daher
        # dieselbe Pillow-Verfuegbarkeit selbst pruefen, sonst schlaegt er in
        # einer reinen requirements.txt-Umgebung (= CI) fehl.
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow nicht installiert (nur ueber requirements-optional.txt)")
        png = backend_cls().render_page_png(self.pdf_path, 0, scale=2.0)
        self.assertIsNotNone(png)
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")

    def test_pymupdf_renders_png(self):
        self._assert_renders_png(PyMuPdfBackend)

    def test_pypdfium2_renders_png(self):
        self._assert_renders_png(Pypdfium2Backend)

    def test_pypdf_cannot_render(self):
        if not PypdfBackend.is_available():
            self.skipTest("pypdf nicht installiert")
        backend = PypdfBackend()
        self.assertFalse(backend.can_render)
        self.assertIsNone(backend.render_page_png(self.pdf_path, 0, scale=2.0))

    def test_pypdf_backend_ocr_path_fails_clearly(self):
        """pypdf-Backend + text-loses PDF -> OCR-Pfad -> sauberer Fehler mit OCR-Hinweis."""
        if not PypdfBackend.is_available():
            self.skipTest("pypdf nicht installiert")
        extractor = TextExtractor(enable_ocr=True, pdf_backend="pypdf")
        result = extractor.extract(self.blank_path)
        self.assertFalse(result.success)
        self.assertIn("OCR", result.error)

    def test_no_backend_installed_reports_error(self):
        with mock.patch.object(pdf_backends, "select_backend", return_value=None):
            extractor = TextExtractor(enable_ocr=False, pdf_backend="auto")
        self.assertIsNone(extractor._pdf_backend)
        result = extractor.extract(self.pdf_path)
        self.assertFalse(result.success)
        self.assertIn("Backend", result.error)


if __name__ == "__main__":
    unittest.main()
